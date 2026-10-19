"""Multi-exchange market data ETL: extract -> bronze -> silver -> gold.

Exit code is 0 only when every stage finished and, if uploads were requested,
every S3 upload succeeded. Run ``python run_pipeline.py --help`` for options.
"""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from src.config import Settings, load_config
from src.extract import fetch_ohlcv, get_nifty50_tickers, get_sp500_tickers
from src.load import save_local, upload_bronze, upload_gold, upload_metrics, upload_silver
from src.transform import (
    clean_data,
    engineer_features,
    flatten_and_merge,
    validate_analytics,
    validate_raw,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("market_pipeline")

EXCHANGES = ("SP500", "NIFTY50", "ALL")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Exchange ETL Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run every stage but never touch S3")
    parser.add_argument("--exchange", choices=EXCHANGES, default="ALL", help="Target exchange (default: ALL)")
    parser.add_argument("--period", default="1y", help="yfinance period to download (default: 1y)")
    parser.add_argument(
        "--require-s3",
        action="store_true",
        help="Fail if S3 settings are missing instead of falling back to local files (use in CI)",
    )
    return parser.parse_args(argv)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tickers(exchange: str) -> pd.DataFrame:
    frames = []
    if exchange in ("NIFTY50", "ALL"):
        logger.info("Extracting Nifty 50 tickers...")
        frames.append(get_nifty50_tickers())
    if exchange in ("SP500", "ALL"):
        logger.info("Extracting S&P 500 tickers...")
        frames.append(get_sp500_tickers())
    return pd.concat(frames, ignore_index=True)


def run(args: argparse.Namespace, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Execute the pipeline and return its metrics (``status`` is SUCCESS or FAILURE)."""
    settings = settings or load_config()
    start = time.time()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    metrics: Dict[str, Any] = {
        "run_id": run_id,
        "status": "IN_PROGRESS",
        "exchange": args.exchange,
        "dry_run": bool(args.dry_run),
        "uploaded": False,
        "start_time": _now(),
        "end_time": None,
        "duration_seconds": None,
        "records_extracted": 0,
        "records_bronze": 0,
        "records_silver": 0,
        "records_gold": 0,
        "failed_tickers": [],
        "upload_failures": [],
        "errors": [],
    }

    upload = settings.can_upload and not args.dry_run
    if not args.dry_run and not settings.can_upload:
        msg = "S3 is not configured (need S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
        if args.require_s3:
            metrics.update(status="FAILURE", end_time=_now(), duration_seconds=time.time() - start)
            metrics["errors"].append(msg)
            logger.error(msg)
            return metrics
        logger.warning("%s. Writing local files only.", msg)
    metrics["uploaded"] = upload

    def _upload(stage: str, ok: bool) -> None:
        if not ok:
            metrics["upload_failures"].append(stage)
            logger.error("S3 upload failed for the %s layer", stage)

    try:
        logger.info("--- PHASE 1: EXTRACT ---")
        tickers_df = _tickers(args.exchange)
        if tickers_df.empty:
            raise ValueError("No tickers extracted.")
        raw_ohlcv = fetch_ohlcv(tickers_df["Symbol"].tolist(), period=args.period)
        metrics["records_extracted"] = len(raw_ohlcv)
        if raw_ohlcv.empty:
            raise ValueError("No OHLCV data extracted.")
        raw_merged = flatten_and_merge(raw_ohlcv, tickers_df[["Symbol", "GICS Sector", "Security", "Exchange"]])

        logger.info("--- PHASE 2: BRONZE ---")
        bronze_df, failed = validate_raw(raw_merged)
        metrics["failed_tickers"] = failed
        metrics["records_bronze"] = len(bronze_df)
        if upload:
            _upload("bronze", upload_bronze(bronze_df, settings.bucket, run_id))
        else:
            save_local(bronze_df, "raw", run_id)

        logger.info("--- PHASE 3: SILVER ---")
        silver_df = clean_data(bronze_df)
        metrics["records_silver"] = len(silver_df)
        if upload:
            _upload("silver", upload_silver(silver_df, settings.bucket, run_id))
        else:
            save_local(silver_df, "processed", run_id)

        logger.info("--- PHASE 4: GOLD ---")
        gold_df = validate_analytics(engineer_features(silver_df))
        metrics["records_gold"] = len(gold_df)
        if upload:
            _upload("gold", upload_gold(gold_df, settings.bucket, run_id))
        else:
            save_local(gold_df, "analytics", run_id, csv=True)
        # Latest copy read by the dashboard
        os.makedirs("data", exist_ok=True)
        gold_df.to_parquet("data/sector_growth_data.parquet", engine="pyarrow", index=False)
        gold_df.to_csv("data/sector_growth_data.csv", index=False)

        if metrics["upload_failures"]:
            raise RuntimeError("S3 upload failed for: " + ", ".join(metrics["upload_failures"]))
        metrics["status"] = "SUCCESS"
        logger.info("Pipeline execution completed successfully.")
    except Exception as exc:  # noqa: BLE001 - recorded in metrics and reflected in the exit code
        metrics["status"] = "FAILURE"
        metrics["errors"].append(str(exc))
        logger.error("Pipeline failed: %s", exc)
    finally:
        metrics["duration_seconds"] = time.time() - start
        metrics["end_time"] = _now()
        os.makedirs("logs", exist_ok=True)
        with open(f"logs/metrics_{run_id}.json", "w") as fh:
            json.dump(metrics, fh, indent=4)
        if upload:
            if not upload_metrics(metrics, settings.bucket, run_id):
                logger.error("Could not upload metrics.json to S3")
    return metrics


def main(argv: Optional[List[str]] = None) -> int:
    metrics = run(parse_args(argv))
    return 0 if metrics["status"] == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())

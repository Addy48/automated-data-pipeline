import os
import time
import logging
from datetime import datetime
from typing import Dict, Any

from src.config import S3_PATHS
from src.extract import get_nifty50_tickers, get_sp500_tickers, fetch_ohlcv
from src.transform import validate_raw, clean_data, engineer_features, validate_analytics, flatten_and_merge
from src.load import upload_bronze, upload_silver, upload_gold, upload_metrics

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("market_pipeline")

def main():
    logger.info("=" * 50)
    logger.info("Starting Automated Data Pipeline...")
    logger.info("=" * 50)
    
    start_time = time.time()
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize metrics
    metrics: Dict[str, Any] = {
        "run_id": run_id,
        "status": "IN_PROGRESS",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "records_extracted": 0,
        "records_bronze": 0,
        "records_silver": 0,
        "records_gold": 0,
        "failed_tickers": [],
        "errors": []
    }
    
    # Check if we should attempt AWS upload
    aws_bucket = os.getenv("AWS_BUCKET_NAME", "your-bucket-name-here")
    has_aws_creds = bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
    if not has_aws_creds:
        logger.warning("AWS Credentials not found in environment. Will save locally and simulate S3 upload.")
    
    try:
        # 1. EXTRACT
        logger.info("\n--- PHASE 1: EXTRACT ---")
        import pandas as pd
        
        logger.info("Extracting Nifty 50 tickers...")
        nifty_df = get_nifty50_tickers()
        logger.info("Extracting S&P 500 tickers...")
        sp500_df = get_sp500_tickers()
        
        tickers_df = pd.concat([nifty_df, sp500_df], ignore_index=True)
        
        if tickers_df.empty:
            raise ValueError("Failed to extract tickers from both sources.")
            
        tickers_list = tickers_df['Symbol'].tolist()
        logger.info(f"Extracting OHLCV for {len(tickers_list)} combined tickers...")
        
        # In a real run, this fetches all. We take top combined for speed if not production
        raw_ohlcv = fetch_ohlcv(tickers_list, period='1mo')
        metrics["records_extracted"] = len(raw_ohlcv)
        
        if raw_ohlcv.empty:
            raise ValueError("No OHLCV data extracted.")
            
        # Join with metadata (Sector and Exchange)
        raw_merged = flatten_and_merge(raw_ohlcv, tickers_df[['Symbol', 'GICS Sector', 'Exchange']])
        
        # 2. BRONZE GATE & LOAD
        logger.info("\n--- PHASE 2: BRONZE GATE ---")
        bronze_df, failed_tickers = validate_raw(raw_merged)
        metrics["failed_tickers"] = failed_tickers
        metrics["records_bronze"] = len(bronze_df)
        
        logger.info("Loading to Bronze Layer...")
        if has_aws_creds:
            upload_bronze(bronze_df, aws_bucket, run_id)
        else:
            logger.info("Mocking Bronze S3 upload. Data saved locally in data/ folder.")
            
        # 3. SILVER (CLEANING) & LOAD
        logger.info("\n--- PHASE 3: SILVER (CLEAN & TRANSFORM) ---")
        silver_df = clean_data(bronze_df)
        metrics["records_silver"] = len(silver_df)
        
        logger.info("Loading to Silver Layer...")
        if has_aws_creds:
            upload_silver(silver_df, aws_bucket, run_id)
        else:
            logger.info("Mocking Silver S3 upload.")
            
        # 4. GOLD (FEATURE ENGINEERING) & GATE & LOAD
        logger.info("\n--- PHASE 4: GOLD (ANALYTICS) ---")
        gold_df = engineer_features(silver_df)
        
        logger.info("Validating Gold Schema...")
        gold_df = validate_analytics(gold_df)
        metrics["records_gold"] = len(gold_df)
        
        logger.info("Loading to Gold Layer...")
        if has_aws_creds:
            upload_gold(gold_df, aws_bucket, run_id)
        else:
            logger.info("Mocking Gold S3 upload.")
        
        metrics["status"] = "SUCCESS"
        logger.info("=" * 50)
        logger.info("Pipeline execution completed successfully.")
        logger.info("=" * 50)
        
    except Exception as e:
        metrics["status"] = "FAILURE"
        metrics["errors"].append(str(e))
        logger.error(f"Pipeline failed: {e}")
        
    finally:
        elapsed_time = time.time() - start_time
        metrics["duration_seconds"] = elapsed_time
        metrics["end_time"] = datetime.utcnow().isoformat()
        
        logger.info(f"Uploading metrics.json for run_id {run_id}...")
        if has_aws_creds:
            upload_metrics(metrics, aws_bucket, run_id)
        else:
            # save locally to logs/
            import json
            os.makedirs("logs", exist_ok=True)
            with open(f"logs/metrics_{run_id}.json", "w") as f:
                json.dump(metrics, f, indent=4)
            logger.info("Mocking metrics S3 upload.")

if __name__ == "__main__":
    main()

import json
from pathlib import Path

import pandas as pd
import pytest

import run_pipeline
from src.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def stubbed(monkeypatch, tmp_path):
    """Run in a temp dir with extraction replaced by fixtures (no network)."""
    sp500 = pd.read_csv(FIXTURES / "mock_sp500.csv")
    sp500["Exchange"] = "S&P 500"
    nifty = pd.read_csv(FIXTURES / "mock_nifty50.csv")
    nifty["Exchange"] = "Nifty 50"
    ohlcv = pd.read_parquet(FIXTURES / "mock_ohlcv.parquet")
    ohlcv["Date"] = pd.to_datetime(ohlcv["Date"])
    calls = {"nifty": 0, "sp500": 0, "uploads": []}

    def fake_sp500():
        calls["sp500"] += 1
        return sp500

    def fake_nifty():
        calls["nifty"] += 1
        return nifty

    monkeypatch.setattr(run_pipeline, "get_sp500_tickers", fake_sp500)
    monkeypatch.setattr(run_pipeline, "get_nifty50_tickers", fake_nifty)
    monkeypatch.setattr(run_pipeline, "fetch_ohlcv", lambda tickers, period="1mo": ohlcv)
    monkeypatch.chdir(tmp_path)
    return calls


def _settings(upload=True):
    return Settings(bucket="test-bucket" if upload else None, region="us-east-1", has_credentials=upload)


def _metrics_file(tmp_path):
    (path,) = list((tmp_path / "logs").glob("metrics_*.json"))
    return json.loads(path.read_text())


def test_dry_run_writes_local_files_and_never_uploads(stubbed, monkeypatch, tmp_path):
    for name in ("upload_bronze", "upload_silver", "upload_gold", "upload_metrics"):
        monkeypatch.setattr(run_pipeline, name, lambda *a, **k: pytest.fail("S3 must not be touched in a dry run"))
    metrics = run_pipeline.run(run_pipeline.parse_args(["--dry-run", "--exchange", "SP500"]), _settings())
    assert metrics["status"] == "SUCCESS"
    assert metrics["uploaded"] is False
    assert (tmp_path / "data" / "sector_growth_data.parquet").exists()
    assert _metrics_file(tmp_path)["status"] == "SUCCESS"


def test_exchange_flag_selects_sources(stubbed):
    run_pipeline.run(run_pipeline.parse_args(["--dry-run", "--exchange", "NIFTY50"]), _settings(upload=False))
    assert stubbed["nifty"] == 1 and stubbed["sp500"] == 0


def test_failed_upload_fails_the_run(stubbed, monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "upload_bronze", lambda *a, **k: True)
    monkeypatch.setattr(run_pipeline, "upload_silver", lambda *a, **k: False)
    monkeypatch.setattr(run_pipeline, "upload_gold", lambda *a, **k: True)
    monkeypatch.setattr(run_pipeline, "upload_metrics", lambda *a, **k: True)
    metrics = run_pipeline.run(run_pipeline.parse_args(["--exchange", "SP500"]), _settings())
    assert metrics["status"] == "FAILURE"
    assert metrics["upload_failures"] == ["silver"]
    assert _metrics_file(tmp_path)["status"] == "FAILURE"


def test_successful_upload_path(stubbed, monkeypatch):
    seen = []
    for name in ("upload_bronze", "upload_silver", "upload_gold", "upload_metrics"):
        monkeypatch.setattr(run_pipeline, name, lambda df, bucket, run_id, _n=name: seen.append((_n, bucket)) or True)
    metrics = run_pipeline.run(run_pipeline.parse_args(["--exchange", "SP500"]), _settings())
    assert metrics["status"] == "SUCCESS" and metrics["uploaded"] is True
    assert [n for n, _ in seen] == ["upload_bronze", "upload_silver", "upload_gold", "upload_metrics"]
    assert {b for _, b in seen} == {"test-bucket"}


def test_require_s3_fails_without_configuration(stubbed):
    metrics = run_pipeline.run(run_pipeline.parse_args(["--require-s3"]), _settings(upload=False))
    assert metrics["status"] == "FAILURE"
    assert "S3 is not configured" in metrics["errors"][0]


def test_local_mode_without_configuration_still_succeeds(stubbed):
    metrics = run_pipeline.run(run_pipeline.parse_args(["--exchange", "SP500"]), _settings(upload=False))
    assert metrics["status"] == "SUCCESS" and metrics["uploaded"] is False


def test_main_returns_exit_code(stubbed, monkeypatch):
    monkeypatch.setattr(run_pipeline, "load_config", lambda: _settings(upload=False))
    assert run_pipeline.main(["--exchange", "SP500"]) == 0
    assert run_pipeline.main(["--exchange", "SP500", "--require-s3"]) == 1


def test_bronze_gate_sees_a_complete_schema(stubbed, caplog):
    """The merged frame must carry every column the Bronze schema requires (it used to miss Security)."""
    with caplog.at_level("WARNING"):
        run_pipeline.run(run_pipeline.parse_args(["--dry-run", "--exchange", "SP500"]), _settings(upload=False))
    assert "schema errors" not in caplog.text

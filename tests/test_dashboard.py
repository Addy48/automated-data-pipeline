"""Smoke test: the Streamlit dashboard imports and renders from a gold-layer parquet."""

import sys
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.transform import clean_data, engineer_features, flatten_and_merge  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
DATA = ROOT / "data" / "sector_growth_data.parquet"


@pytest.fixture
def gold_parquet():
    sp500 = pd.read_csv(FIXTURES / "mock_sp500.csv")
    sp500["Exchange"] = "S&P 500"
    ohlcv = pd.read_parquet(FIXTURES / "mock_ohlcv.parquet")
    ohlcv["Date"] = pd.to_datetime(ohlcv["Date"])
    merged = flatten_and_merge(
        ohlcv, sp500[["Symbol", "GICS Sector", "Security", "Exchange"]]
    )
    gold = engineer_features(clean_data(merged))
    existed = DATA.exists()
    backup = DATA.read_bytes() if existed else None
    DATA.parent.mkdir(exist_ok=True)
    gold.to_parquet(DATA, index=False)
    try:
        yield gold
    finally:
        if existed:
            DATA.write_bytes(backup)
        else:
            DATA.unlink(missing_ok=True)


def test_dashboard_renders_without_exceptions(gold_parquet, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "dashboard"))
    monkeypatch.syspath_prepend(str(ROOT))
    for name in [
        m for m in sys.modules if m == "components" or m.startswith("components.")
    ]:
        del sys.modules[name]
    at = AppTest.from_file(str(ROOT / "dashboard" / "app.py"), default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]

import pytest
import pandas as pd
from src.extract import get_sp500_tickers, fetch_ohlcv
import yfinance as yf
from unittest.mock import patch


def test_get_sp500_tickers_wikipedia_success():
    # Mocking requests.get to simulate successful Wikipedia scrape
    class MockResponse:
        def __init__(self):
            self.text = (
                "<html><body><table>"
                "<thead><tr><th>Symbol</th><th>Security</th><th>GICS Sector</th></tr></thead>"
                "<tbody>"
                "<tr><td>AAPL</td><td>Apple Inc.</td><td>Information Technology</td></tr>"
                "<tr><td>BRK.B</td><td>Berkshire</td><td>Financials</td></tr>"
                "</tbody></table></body></html>"
            )
            self.status_code = 200

        def raise_for_status(self):
            pass

    with patch("requests.get", return_value=MockResponse()):
        df = get_sp500_tickers(fallback_path="nonexistent.csv")
        assert not df.empty
        assert "Symbol" in df.columns
        assert "GICS Sector" in df.columns
        assert len(df) == 2
        # Check hyphen replacement
        assert "BRK-B" in df["Symbol"].values


def test_get_sp500_tickers_fallback_success():
    # Simulate network failure to force fallback
    with patch("requests.get", side_effect=Exception("Network Error")):
        df = get_sp500_tickers(fallback_path="tests/fixtures/mock_sp500.csv")
        assert not df.empty
        assert "Symbol" in df.columns
        assert len(df) == 10


def test_fetch_ohlcv_success():
    # Mock yfinance download
    mock_data = pd.DataFrame(
        {
            ("Adj Close", "AAPL"): [150.0, 151.0],
            ("Close", "AAPL"): [150.0, 151.0],
            ("High", "AAPL"): [152.0, 153.0],
            ("Low", "AAPL"): [149.0, 150.0],
            ("Open", "AAPL"): [149.5, 150.5],
        }
    )
    mock_data.index = pd.to_datetime(["2023-01-01", "2023-01-02"])
    mock_data.index.name = "Date"

    mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)

    with patch("yfinance.download", return_value=mock_data):
        df = fetch_ohlcv(["AAPL"], period="1mo")
        assert not df.empty
        assert "Symbol" in df.columns
        assert "Date" in df.columns
        assert "Close" in df.columns
        assert df["Symbol"].iloc[0] == "AAPL"
        assert len(df) == 2


def test_fetch_ohlcv_empty():
    with patch("yfinance.download", return_value=pd.DataFrame()):
        df = fetch_ohlcv(["INVALID"], period="1mo")
        assert df.empty


def test_fetch_ohlcv_exception():
    with patch("yfinance.download", side_effect=Exception("API limit")):
        with pytest.raises(Exception) as excinfo:
            fetch_ohlcv(["AAPL"])
        assert "API limit" in str(excinfo.value)

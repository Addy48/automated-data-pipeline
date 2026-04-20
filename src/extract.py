import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger("sp500_pipeline")


def get_sp500_tickers(
    fallback_path: str = "tests/fixtures/mock_sp500.csv",
) -> pd.DataFrame:
    """
    Scrape the S&P 500 constituency list from Wikipedia.

    Args:
        fallback_path (str): Path to local CSV if Wikipedia is unreachable.

    Returns:
        pd.DataFrame: DataFrame containing 'Symbol' and 'GICS Sector' columns.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DataPipeline/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Read the first table on the page
        tables = pd.read_html(response.text)
        df = tables[0]

        # Wikipedia sometimes uses dots instead of hyphens for class shares (e.g. BRK.B instead of BRK-B)
        # yfinance expects hyphens
        df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
        logger.info(f"Successfully scraped {len(df)} tickers from Wikipedia.")
        return df[["Symbol", "GICS Sector", "Security"]]

    except Exception as e:
        logger.error(
            f"Failed to scrape Wikipedia: {e}. Falling back to {fallback_path}."
        )
        try:
            df = pd.read_csv(fallback_path)
            df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
            logger.info(f"Successfully loaded {len(df)} tickers from fallback CSV.")
            return df[["Symbol", "GICS Sector", "Security"]]
        except Exception as fallback_err:
            logger.critical(f"Fallback also failed: {fallback_err}")
            raise


def fetch_ohlcv(tickers: List[str], period: str = "1mo") -> pd.DataFrame:
    """
    Download OHLCV data for a list of tickers using yfinance.

    Args:
        tickers (List[str]): List of stock ticker symbols.
        period (str): The time period to download (default: 1mo).

    Returns:
        pd.DataFrame: Flattened DataFrame containing OHLCV data.
    """
    logger.info(f"Downloading OHLCV data for {len(tickers)} tickers. Period: {period}")

    # Bulk download is faster but returns a MultiIndex columns dataframe
    try:
        data = yf.download(
            tickers,
            period=period,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False,
        )
    except Exception as e:
        logger.error(f"yfinance download failed: {e}")
        raise

    if data.empty:
        logger.warning("Downloaded data is empty.")
        return pd.DataFrame()

    # Flatten the MultiIndex DataFrame
    frames = []

    # If there's only one ticker, yf doesn't use MultiIndex columns for tickers
    if len(tickers) == 1:
        ticker = tickers[0]
        df = data.copy()
        df["Symbol"] = ticker
        df = df.reset_index()
        frames.append(df)
    else:
        for ticker in tickers:
            if ticker in data.columns.levels[0]:
                df = data[ticker].copy()
                df = df.dropna(
                    how="all"
                )  # Drop days with no data for this specific ticker
                if not df.empty:
                    df["Symbol"] = ticker
                    df = df.reset_index()
                    frames.append(df)
            else:
                logger.warning(f"No data found for ticker {ticker}")

    if not frames:
        logger.warning("No valid data frames extracted from download.")
        return pd.DataFrame()

    flat_df = pd.concat(frames, ignore_index=True)

    # Ensure standard column names and Date format
    if "Date" in flat_df.columns:
        flat_df["Date"] = pd.to_datetime(flat_df["Date"]).dt.date
    elif "Datetime" in flat_df.columns:
        flat_df = flat_df.rename(columns={"Datetime": "Date"})
        flat_df["Date"] = pd.to_datetime(flat_df["Date"]).dt.date

    logger.info(f"Successfully flattened OHLCV data. Total rows: {len(flat_df)}")
    return flat_df

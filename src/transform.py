import logging
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Tuple, List

logger = logging.getLogger("sp500_pipeline")

# ---------------------------------------------------------
# Bronze Gate: Lazy Validation Schema
# ---------------------------------------------------------
class RawDataSchema(pa.DataFrameModel):
    Symbol: Series[str] = pa.Field(nullable=False)
    Date: Series[pd.Timestamp] = pa.Field(nullable=False)
    Open: Series[float] = pa.Field(nullable=True)
    High: Series[float] = pa.Field(nullable=True)
    Low: Series[float] = pa.Field(nullable=True)
    Close: Series[float] = pa.Field(nullable=True)
    Volume: Series[float] = pa.Field(nullable=True)
    GICS_Sector: Series[str] = pa.Field(nullable=True)
    Security: Series[str] = pa.Field(nullable=True)

    class Config:
        coerce = True
        strict = False  # Allow extra columns


# ---------------------------------------------------------
# Gold Gate: Eager Validation Schema
# ---------------------------------------------------------
class AnalyticsDataSchema(pa.DataFrameModel):
    Symbol: Series[str] = pa.Field(nullable=False)
    Date: Series[pd.Timestamp] = pa.Field(nullable=False)
    Close: Series[float] = pa.Field(gt=0, nullable=False)
    Volume: Series[float] = pa.Field(ge=0, nullable=False)
    GICS_Sector: Series[str] = pa.Field(nullable=False)
    Daily_Return: Series[float] = pa.Field(nullable=True)
    MA_20: Series[float] = pa.Field(nullable=True)
    MA_50: Series[float] = pa.Field(nullable=True)
    Cumulative_Return: Series[float] = pa.Field(nullable=True)
    Volatility_30D: Series[float] = pa.Field(nullable=True)
    Max_Drawdown: Series[float] = pa.Field(nullable=True)

    class Config:
        coerce = True
        strict = False


def flatten_and_merge(ohlcv_df: pd.DataFrame, sp500_df: pd.DataFrame) -> pd.DataFrame:
    """Merge OHLCV data with S&P 500 sector metadata."""
    if ohlcv_df.empty or sp500_df.empty:
        logger.warning("Empty dataframe passed to flatten_and_merge.")
        return pd.DataFrame()
        
    merged_df = ohlcv_df.merge(sp500_df, on='Symbol', how='left')
    merged_df = merged_df.rename(columns={'GICS Sector': 'GICS_Sector'})
    logger.info(f"Merged OHLCV with S&P 500 metadata. Shape: {merged_df.shape}")
    return merged_df


def validate_raw(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Lazy validation for Bronze Gate. Drops invalid rows and reports failures."""
    if df.empty:
        return df, []
        
    try:
        validated_df = RawDataSchema.validate(df, lazy=True)
        return validated_df, []
    except pa.errors.SchemaErrors as err:
        logger.warning(f"Bronze validation caught {len(err.failure_cases)} schema errors.")
        
        # We can extract failed indices and drop them
        failed_indices = err.failure_cases['index'].dropna().unique()
        valid_df = df.drop(index=failed_indices).reset_index(drop=True)
        
        failed_symbols = []
        if 'Symbol' in df.columns:
            failed_symbols = df.loc[failed_indices, 'Symbol'].dropna().unique().tolist()
            
        logger.info(f"Dropped {len(failed_indices)} invalid rows. {len(valid_df)} rows remaining.")
        return valid_df, failed_symbols


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data: handle nulls and drop impossible values."""
    if df.empty:
        return df
        
    df = df.copy()
    
    # Drop rows where critical price data is missing
    df = df.dropna(subset=['Close', 'Volume', 'GICS_Sector'])
    
    # Assert physical reality
    df = df[df['Close'] > 0]
    df = df[df['Volume'] >= 0]
    
    # Forward fill Open/High/Low if they are NaN but Close exists
    df['Open'] = df['Open'].fillna(df['Close'])
    df['High'] = df['High'].fillna(df['Close'])
    df['Low'] = df['Low'].fillna(df['Close'])
    
    logger.info(f"Data cleaned. Shape after cleaning: {df.shape}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized feature engineering for analytical insights."""
    if df.empty:
        return df
        
    df = df.copy()
    
    # Sort values to ensure correct rolling window calculations
    df = df.sort_values(['Symbol', 'Date']).reset_index(drop=True)
    
    # Group by Symbol for sequential calculations
    grouped = df.groupby('Symbol')
    
    # Daily Returns
    df['Daily_Return'] = grouped['Close'].pct_change()
    
    # Moving Averages
    df['MA_20'] = grouped['Close'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
    df['MA_50'] = grouped['Close'].transform(lambda x: x.rolling(window=50, min_periods=1).mean())
    
    # Cumulative Returns
    df['Cumulative_Return'] = grouped['Daily_Return'].transform(lambda x: (1 + x.fillna(0)).cumprod() - 1)
    
    # 30-Day Volatility (Annualized)
    # Approx 252 trading days in a year -> sqrt(252)
    df['Volatility_30D'] = grouped['Daily_Return'].transform(lambda x: x.rolling(window=30, min_periods=1).std() * (252 ** 0.5))
    
    # Max Drawdown
    cumulative_max = grouped['Close'].cummax()
    drawdown = (df['Close'] - cumulative_max) / cumulative_max
    df['Max_Drawdown'] = df.groupby('Symbol')['Close'].transform(lambda x: ((x - x.cummax()) / x.cummax()).rolling(window=252, min_periods=1).min())
    
    logger.info(f"Feature engineering complete. Added analytical columns.")
    return df


def validate_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """Eager validation for Gold Gate. Fatal if failed."""
    if df.empty:
        return df
        
    try:
        validated_df = AnalyticsDataSchema.validate(df)
        logger.info("Gold validation passed successfully.")
        return validated_df
    except pa.errors.SchemaError as err:
        logger.critical(f"Gold validation FAILED: {err}")
        raise

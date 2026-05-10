import pytest
import pandas as pd
import numpy as np
from src.transform import flatten_and_merge, clean_data, engineer_features

@pytest.fixture
def sample_ohlcv():
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=5),
        'Symbol': ['AAPL']*5,
        'Open': [100, 101, 102, np.nan, 104],
        'High': [105, 106, 107, np.nan, 109],
        'Low': [95, 96, 97, np.nan, 99],
        'Close': [102, 103, 104, 105, 106],
        'Volume': [1000, 1100, 1200, 1300, 1400]
    })

@pytest.fixture
def sample_sp500():
    return pd.DataFrame({
        'Symbol': ['AAPL', 'MSFT'],
        'Security': ['Apple Inc.', 'Microsoft Corp.'],
        'GICS Sector': ['Information Technology', 'Information Technology']
    })

def test_flatten_and_merge(sample_ohlcv, sample_sp500):
    merged = flatten_and_merge(sample_ohlcv, sample_sp500)
    assert not merged.empty
    assert 'GICS_Sector' in merged.columns
    assert 'Security' in merged.columns
    assert merged['GICS_Sector'].iloc[0] == 'Information Technology'

def test_flatten_and_merge_empty():
    empty_df = pd.DataFrame()
    assert flatten_and_merge(empty_df, empty_df).empty

def test_clean_data(sample_ohlcv, sample_sp500):
    merged = flatten_and_merge(sample_ohlcv, sample_sp500)
    
    # Introduce bad data
    merged.loc[0, 'Close'] = -5  # Impossible
    merged.loc[1, 'Volume'] = -100 # Impossible
    merged.loc[2, 'GICS_Sector'] = np.nan # Missing sector
    
    cleaned = clean_data(merged)
    
    assert len(cleaned) == 2 # Only rows 3 and 4 survive
    # Check forward fill for row 3 (which had NaN Open/High/Low)
    assert cleaned.iloc[0]['Open'] == cleaned.iloc[0]['Close']

def test_engineer_features(sample_ohlcv, sample_sp500):
    merged = flatten_and_merge(sample_ohlcv, sample_sp500)
    cleaned = clean_data(merged)
    
    featured = engineer_features(cleaned)
    
    assert 'Daily_Return' in featured.columns
    assert 'MA_20' in featured.columns
    assert 'MA_50' in featured.columns
    assert 'Cumulative_Return' in featured.columns
    assert 'Volatility_30D' in featured.columns
    assert 'Max_Drawdown' in featured.columns
    
    # Daily return for the second day should be (103-102)/102
    assert pytest.approx(featured['Daily_Return'].iloc[1]) == (103-102)/102

def test_engineer_features_empty():
    assert engineer_features(pd.DataFrame()).empty

import pytest
import pandas as pd
from src.transform import RawDataSchema, AnalyticsDataSchema, validate_raw, validate_analytics
import pandera as pa

@pytest.fixture
def valid_raw_data():
    return pd.DataFrame({
        'Symbol': ['AAPL'],
        'Date': [pd.Timestamp('2023-01-01')],
        'Open': [100.0],
        'High': [105.0],
        'Low': [95.0],
        'Close': [102.0],
        'Volume': [1000.0],
        'GICS_Sector': ['Information Technology'],
        'Security': ['Apple Inc.']
    })

@pytest.fixture
def valid_analytics_data(valid_raw_data):
    df = valid_raw_data.copy()
    df['Daily_Return'] = 0.01
    df['MA_20'] = 100.0
    df['MA_50'] = 98.0
    df['Cumulative_Return'] = 0.05
    df['Volatility_30D'] = 0.2
    df['Max_Drawdown'] = -0.1
    return df

def test_raw_schema_valid(valid_raw_data):
    validated, failed = validate_raw(valid_raw_data)
    assert len(failed) == 0
    assert len(validated) == 1

def test_raw_schema_invalid():
    invalid_data = pd.DataFrame({
        'Symbol': [None, 'AAPL'], # Null symbol should fail
        'Date': [pd.Timestamp('2023-01-01'), 'not-a-date'], # Bad date type
    })
    validated, failed = validate_raw(invalid_data)
    assert len(validated) == 0
    assert len(failed) >= 1

def test_analytics_schema_valid(valid_analytics_data):
    validated = validate_analytics(valid_analytics_data)
    assert len(validated) == 1

def test_analytics_schema_invalid_fatal(valid_analytics_data):
    invalid_data = valid_analytics_data.copy()
    invalid_data.loc[0, 'Close'] = -10.0 # Negative close is invalid in Gold Gate
    
    with pytest.raises(pa.errors.SchemaError):
        validate_analytics(invalid_data)

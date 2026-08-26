# Medallion Architecture Specification

## Overview
This automated data pipeline processes market OHLCV and constituent data across S&P 500 and NIFTY 50 exchanges through a 3-tier S3 Lakehouse architecture.

```
[ Wikipedia + Yahoo Finance ]
              |
              v (Raw Parquet / JSON)
        [ BRONZE TIER ]
   s3://lake-bucket/raw/
              |
              v (Pandera Schema Validation & Cleaning)
        [ SILVER TIER ]
   s3://lake-bucket/curated/
              |
              v (Moving Averages, RSI, Volatility Feature Engineering)
        [ GOLD TIER ]
   s3://lake-bucket/analytics/
              |
              +---> [ Athena Serverless SQL ]
              +---> [ Streamlit Arena Dashboard ]
```

## Data Quality Guarantees
- **Bronze Gate**: Lazy validation allows non-fatal schema anomalies to be quarantined.
- **Silver Gate**: Type coercion, timestamp normalization, null value handling.
- **Gold Gate**: Eager validation with fatal abort on critical invariant violations.

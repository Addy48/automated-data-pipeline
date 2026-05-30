# Medallion architecture

Nightly ETL for S&P 500 constituents. Wikipedia supplies the ticker list. Yahoo Finance supplies twelve months of OHLCV. Data lands in Amazon S3 as three layers, then Athena and Streamlit read Gold.

```
Wikipedia  +  yfinance
        \    /
         EXTRACT
            |
            v
     Bronze  s3://bucket/raw/year=YYYY/month=MM/
            |  Pandera RawDataSchema
            v
     Silver  s3://bucket/processed/year=YYYY/month=MM/
            |  clean, coerce, drop bad Close
            v
     Gold    s3://bucket/analytics/year=YYYY/month=MM/
            |  Daily_Return, MA_20, MA_50,
            |  Cumulative_Return, Volatility_30D, Max_Drawdown
            |  Pandera AnalyticsDataSchema (strict)
            v
     Glue catalog  ->  Athena  ->  Streamlit
     observability JSON under s3://bucket/observability/
```

GitHub Actions runs `python run_pipeline.py` on a nightly cron. Terraform owns the bucket, Glue database, crawler, Athena workgroup, and IAM.

Local files under `data/` are kept if an S3 upload fails.

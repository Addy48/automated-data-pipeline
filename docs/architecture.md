# Medallion architecture

ETL for the S&P 500 and Nifty 50. Wikipedia supplies the ticker lists, Yahoo Finance supplies daily OHLCV (one year by default). Data lands in Amazon S3 as three layers; Glue and Athena serve SQL over Gold, and the Streamlit dashboard reads the latest Gold file written locally by the pipeline.

```
Wikipedia  +  yfinance
        \    /
         EXTRACT   (fallback ticker CSVs if Wikipedia is unreachable)
            |
            v
     Bronze  s3://bucket/raw/run_id=<run>/data.parquet
            |  Pandera RawDataSchema (lazy: bad rows dropped and reported)
            v
     Silver  s3://bucket/processed/run_id=<run>/data.parquet
            |  drop nulls and impossible prices, fill Open/High/Low
            v
     Gold    s3://bucket/analytics/run_id=<run>/data.{parquet,csv}
            |  Daily_Return, MA_20, MA_50, EMA_12, EMA_26, RSI_14,
            |  Cumulative_Return, Volatility_30D, Max_Drawdown
            |  Pandera AnalyticsDataSchema (eager: fatal if it fails)
            v
     Glue catalog  ->  Athena          (ad-hoc SQL)
     data/sector_growth_data.parquet   ->  Streamlit dashboard
     run metrics    s3://bucket/observability/run_id=<run>/metrics.json
```

GitHub Actions runs `python run_pipeline.py --require-s3` twice a day. Terraform owns the bucket, Glue database, crawler, Athena workgroup, and IAM.

## Failure handling

- The process exits non-zero if any stage fails or any S3 upload fails, so a red workflow run means data did not land.
- `--require-s3` (used in CI) fails the run when `S3_BUCKET_NAME` or the AWS keys are missing, instead of silently writing local files.
- `--dry-run` runs every stage without touching S3.
- Every run writes `logs/metrics_<run>.json` (status, row counts per layer, failed tickers, upload failures, errors) and uploads it to `observability/` when S3 is configured. The CI job also keeps it as a run artifact.
- Local copies under `data/` are kept when an upload fails.

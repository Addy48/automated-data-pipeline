# Automated Market Data ETL Pipeline & Analytics Dashboard

![Pipeline Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20Glue%20%7C%20Athena-orange)

An automated, serverless ETL pipeline that extracts financial market data, enforces strict data quality contracts using Pandera, and stages it in an AWS S3 Medallion Data Lake. The data is ultimately visualized via a high-performance Streamlit dashboard powered by AWS Athena.

## Architecture

1. **Extract**: Scrapes S&P 500 constituents from Wikipedia and fetches OHLCV data via `yfinance`.
2. **Transform**: Merges sector metadata, handles missing values, and engineers financial features (Volatility, Max Drawdown). Guarded by lazy (Bronze) and eager (Gold) Pandera validation schemas.
3. **Load**: Stores data in S3 using a Medallion architecture (`raw/`, `processed/`, `analytics/`).
4. **Serve**: AWS Athena queries the Gold layer via `awswrangler`, caching results in a Streamlit dashboard.

## Setup Instructions

Please see `docs/architecture.md` for detailed infrastructure setup.

### Prerequisites
- Python 3.11+
- AWS Account & configured IAM credentials
- Terraform installed

### Local Development
1. Clone the repository
2. Run `pip install -r requirements-dev.txt`
3. Setup pre-commit: `pre-commit install`
4. Copy `.env.example` to `.env` and configure your AWS credentials
5. Run the pipeline: `python run_pipeline.py`
6. Start the dashboard: `streamlit run dashboard/app.py`

# Automated Market Data ETL Pipeline & Analytics Dashboard

Welcome to the **Automated Market Data ETL Pipeline & Analytics Dashboard**. This is a complete, production-grade automated platform designed to extract, transform, and load (ETL) global market data—simultaneously tracking the **S&P 500 (US Market)** and the **Nifty 50 (Indian Market)**—into an AWS S3 Medallion Data Lake, query it via AWS Athena, and visualize it through a premium, custom-styled Streamlit Analytics Dashboard.

## 🌟 Project Master Overview

This repository houses the entire end-to-end infrastructure and code for the automated data pipeline.

### Core Capabilities
1. **Automated Multi-Exchange Extraction**: Scrapes the constituency lists for both the **S&P 500** and **Nifty 50** from Wikipedia, fetching corresponding daily OHLCV market data via `yfinance`.
2. **Medallion Data Architecture**: Data is rigorously validated, cleaned, and partitioned, flowing through `Bronze` (Raw), `Silver` (Cleaned), and `Gold` (Aggregated) layers in AWS S3 with explicit tracking of the exchange dimension.
3. **Infrastructure as Code (IaC)**: The entire AWS backend (S3 Bucket, Glue Catalog, IAM Roles, Athena Workgroup) is fully automated and provisioned via Terraform.
4. **CI/CD & Automation**: GitHub Actions runs a dual-cron trigger (12:30 UTC for the Indian market close, and 21:30 UTC for the US close) to capture same-day market closings.
5. **Premium Interactive Analytics**: A custom-styled Streamlit dashboard ("The Arena") that connects securely to AWS Athena to deliver high-performance visual insights on sector growth, KPI metrics, and top-performing stocks.

---

## 🏗️ Architecture Blueprint

```mermaid
graph TD
    A[Data Sources: Wikipedia & yfinance] -->|Extract| B(GitHub Actions Python Script)
    B -->|Transform & Validate| C{Pandera & PyArrow}
    C -->|Load Parquet| D[(AWS S3 Data Lake)]
    D -->|Bronze: Raw| D1[s3://bucket/bronze/]
    D -->|Silver: Cleaned| D2[s3://bucket/silver/]
    D -->|Gold: Aggregated| D3[s3://bucket/gold/]
    D -->|Catalog| E[AWS Glue Data Catalog]
    E --> F[AWS Athena Serverless Query]
    F -->|Boto3 / PyAthena| G[Streamlit Analytics Dashboard]
```

---

## 📁 Repository Structure

```text
.
├── .github/                  # GitHub Actions CI/CD workflows, issue/PR templates
│   └── workflows/
│       ├── etl_cron.yml      # The automation engine running twice daily (12:30 & 21:30 UTC)
│       └── ci.yml            # Continuous integration (Linting & Testing)
├── dashboard/                # Analytics Dashboard App
│   ├── app.py                # Main Streamlit application ("The Arena" UI)
│   └── components/           # Reusable UI components (KPI cards, charts)
├── src/                      # Core Pipeline Source Code
│   ├── extract.py            # Dual Wikipedia & yfinance extraction logic
│   ├── transform.py          # Data cleaning & schema validation (Pandera)
│   ├── load.py               # AWS S3 Parquet uploading and partitioning
│   └── config.py             # Logging and configuration utils
├── terraform/                # Infrastructure as Code (AWS Provisioning)
│   ├── main.tf               # S3, Glue, Athena, IAM resource definitions
│   └── variables.tf          # Configurable AWS variables
├── tests/                    # Pytest suite for the pipeline
├── requirements.txt          # Production Python dependencies
└── USER_MANUAL.md            # Comprehensive user guide on how to operate the project
```

---

## 🚀 How It Works (The Automation Engine)

This project requires **zero daily manual intervention**.
1. Twice a day, **GitHub Actions** triggers the `ETL Pipeline`:
   - At **12:30 UTC** (6:00 PM IST) to capture the closing of the Indian Stock Exchange.
   - At **21:30 UTC** (5:00 PM EST) to capture the closing of the US Stock Exchanges.
2. A cloud runner spins up, installs Python dependencies, and runs the extraction suite.
3. Data is fetched, validated against strict `Pandera` schemas (enforcing the exchange and sector partitions), converted into compressed columnar `Parquet` format, and partitioned by date.
4. The runner securely authenticates with AWS using GitHub Secrets and uploads the Parquet files to the **S3 Data Lake**.
5. **AWS Glue** catalogs the new partitions, making them queryable by **AWS Athena**.
6. When a user opens the **Streamlit Dashboard**, it sends optimized SQL queries directly to Athena, crunching millions of rows in seconds, and visualizes the results.

---

## 📚 Documentation

For a full guide on where to see the project running, how to access the AWS resources, and how to launch your dashboard, please read the [USER MANUAL](USER_MANUAL.md).

---

## 🛠️ Technology Stack

- **Cloud & Big Data**: AWS S3, AWS Glue, AWS Athena, Boto3
- **Infrastructure as Code**: Terraform
- **Data Engineering**: Pandas, PyArrow, Fastparquet, Pandera
- **Automation & CI/CD**: GitHub Actions
- **Dashboard & UI**: Streamlit, Plotly
- **Language**: Python 3.9+

---

## 📝 License & Contributing

This project is open-source and available under the MIT License. Please review `CONTRIBUTING.md` and `SECURITY.md` for guidelines on submitting pull requests.

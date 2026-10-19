# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-19

### Fixed
- The pipeline read the bucket from `AWS_BUCKET_NAME` while the workflow and `.env.example` set `S3_BUCKET_NAME`, so every scheduled run tried to upload to the placeholder `your-bucket-name-here` and got `AccessDenied`. It now reads `S3_BUCKET_NAME`.
- Failed S3 uploads were logged but the run still reported success and exited 0. A failed stage or upload now sets `status: FAILURE` and a non-zero exit code.
- The Bronze merge dropped the `Security` column the schema requires, so every run logged a schema error.
- Nifty 50 scraping turned blank rows into a `nan.NS` ticker and called `pd.read_html` on a raw string (removed in pandas 3).
- The dashboard crashed on import (`plotly.graph_objects` was never imported), and the pipeline monitor crashed on metrics files without `start_time`.
- `--dry-run` and `--exchange` were parsed but never used; they now work.
- The S&P fixture CSV had an unquoted comma that shifted its columns, and the Nifty fallback fixture did not exist.

### Changed
- Dependencies updated together (boto3/botocore/awswrangler as one set, pandas 3, plotly 7, pytest 9); Dependabot now groups related updates.
- Workflow: runs local-only until the repository variable `ETL_S3=true` is set, then `--require-s3`; 30-minute timeout, no overlapping runs, read-only token, metrics uploaded as an artifact, manual run can pick the exchange.
- Default download period is one year, matching the dashboard and docs.
- The dashboard shows the RSI chart that was already implemented but never rendered.

### Added
- Tests for configuration, the pipeline run (dry run, upload success and failure, exit codes), Nifty extraction and a dashboard smoke test.

## [1.0.0] - 2026-05-25

### Added
- Complete Automated Data Pipeline architecture
- S3 Medallion Lake configuration via Terraform
- Pandera validation schemas (Bronze and Gold gates)
- Robust ETL extraction with yfinance and Wikipedia fallbacks
- Streamlit dashboard with KPI cards, heatmap, and sector comparisons
- GitHub Actions integration and dependency scanning

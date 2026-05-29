# 📖 Master User Manual & Operations Guide

This document is your definitive guide on **how and where to see the project**, **how to use it**, and **how to manage it**.

---

## 1. Where Is Everything Located?

The project spans across three major platforms: **GitHub**, **AWS**, and your **Local Machine**.

### A. GitHub (The Control Center & Automation Engine)
Your entire codebase lives at: `https://github.com/Addy48/automated-data-pipeline`
- **What happens here?** GitHub stores the code and runs the automation.
- **Where to look:** Click on the **"Actions"** tab at the top of your GitHub repository. Here you will see the **"Nightly ETL Pipeline"**. This is the heart of the project. It automatically triggers twice daily (at 12:30 UTC and 21:30 UTC), processes the market data for both S&P 500 and Nifty 50, and uploads it to AWS.

### B. AWS Cloud (The Storage & Compute Engine)
Go to [aws.amazon.com](https://aws.amazon.com) and log into your console. Search for the following services:
- **Amazon S3**: Search for "S3". You will see a bucket named `sp500-pipeline-aaditya-2026-xyz` (or your customized bucket name). Click it. Inside, you will see folders for `raw/` (Bronze), `processed/` (Silver), and `analytics/` (Gold). This is where your actual Parquet files are securely saved after each run.
- **Amazon Athena**: Search for "Athena". This is the query engine. In the Query Editor, select the database `sp500_analytics`, where you can query the unified gold layer containing both US and Indian stock metrics.

### C. Your Local Machine (The Visualization Engine)
Your Mac terminal is where you launch the beautiful, interactive Analytics Dashboard ("The Arena"). The dashboard connects to AWS, pulls the insights, and displays them in your web browser.

---

## 2. How To Use It

### Scenario 1: I want to view the Dashboard and analyze the market.
You don't need to touch AWS or GitHub for this.
1. Open your Mac Terminal.
2. Navigate to the project folder:
   ```bash
   cd /Users/aaditya/.gemini/antigravity/automated-data-pipeline
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Run the Streamlit Dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```
5. Your browser will automatically open a beautiful webpage styled like **The Arena**. 
   - **Toggling Markets:** Use the horizontal selection pills at the top (`🌐 All Markets`, `🇮🇳 Nifty 50`, `🇺🇸 S&P 500`) to filter between US and Indian equities.
   - **Filtering Sectors:** Use the GICS Sector dropdown inline in the main body to filter industry segments and view top performer cards dynamically.

### Scenario 2: I want to manually sync / trigger a data extraction right now.
Although the pipeline runs automatically twice a day, you can trigger it manually:
- **Directly from the Dashboard:** Click the **"🔄 Sync Markets"** button on the top right of the dashboard. It will spin up the ETL pipeline in a background process, re-extract Wikipedia and yfinance data, validate schemas, rewrite local Parquet files, and refresh the UI in-place!
- **From GitHub Actions:** 
  1. Go to your repository on GitHub (`Addy48/automated-data-pipeline`).
  2. Click the **"Actions"** tab.
  3. On the left sidebar, click **"Nightly ETL Pipeline"**.
  4. Click the green **"Run workflow"** button on the right.

---

## 3. Operations & Maintenance

### What if I want to change the schedule?
If you want the pipeline to run at a different time:
1. Open the file `.github/workflows/etl_cron.yml`.
2. Look for the lines under `schedule:`:
   ```yaml
   - cron: '30 12,21 * * *'
   ```
3. Modify the cron expression to your desired UTC times and push to GitHub.

### What if AWS charges me money?
The infrastructure is designed using serverless components (S3, Athena, Glue).
- **S3** costs pennies per gigabyte. The stock data is compressed into Parquet, taking up very little space.
- **Athena** charges $5 per Terabyte queried. Since the dashboard queries only megabytes, execution costs fall entirely within the **AWS Free Tier** (or will cost less than $0.10 a month).

---

## 4. Troubleshooting

- **Dashboard is failing to load data**: Ensure you have executed `python run_pipeline.py` or clicked **"🔄 Sync Markets"** to generate the initial local parquet data files inside the `data/` folder.
- **KeyError: 'Exchange' or Column Errors**: Ensure all your local files match the latest repository code. Run `git pull origin main` to synchronize.
- **Yahoo Finance rate-limiting**: The extraction engine is resilient and retries downloads. If a download fails, check the `logs/` directory for detailed exception metrics.

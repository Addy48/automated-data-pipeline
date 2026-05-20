# 📖 Master User Manual & Operations Guide

This document is your definitive guide on **how and where to see the project**, **how to use it**, and **how to manage it**.

---

## 1. Where Is Everything Located?

The project spans across three major platforms: **GitHub**, **AWS**, and your **Local Machine**.

### A. GitHub (The Control Center & Automation Engine)
Your entire codebase lives at: `https://github.com/Addy48/automated-data-pipeline`
- **What happens here?** GitHub stores the code and runs the automation.
- **Where to look:** Click on the **"Actions"** tab at the top of your GitHub repository. Here you will see the **"Nightly ETL Pipeline"**. This is the heart of the project. It automatically turns on every day, processes the market data, and sends it to AWS.

### B. AWS Cloud (The Storage & Compute Engine)
Go to [aws.amazon.com](https://aws.amazon.com) and log into your console. Search for the following services:
- **Amazon S3**: Search for "S3". You will see a bucket named `sp500-pipeline-aaditya-2026-xyz`. Click it. Inside, you will see folders for `bronze`, `silver`, and `gold`. This is where your actual Parquet data files are being saved every night.
- **Amazon Athena**: Search for "Athena". This is the query engine. If you go to the Query Editor, select the database `sp500_analytics`, you can literally type `SELECT * FROM gold_layer LIMIT 10;` and instantly see your pipeline's data.

### C. Your Local Machine (The Visualization Engine)
Your Mac terminal is where you launch the beautiful, interactive Analytics Dashboard. The dashboard connects to AWS, pulls the insights, and displays them in your web browser.

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
5. Your browser will automatically open a beautiful webpage. Use the sidebar on the left to filter by sectors, view the KPI cards, and interact with the charts!

### Scenario 2: I want to manually trigger a data extraction right now.
The pipeline runs automatically at 02:00 UTC. However, if you want to pull data *right now*:
1. Go to your repository on GitHub (`Addy48/automated-data-pipeline`).
2. Click the **"Actions"** tab.
3. On the left sidebar, click **"Nightly ETL Pipeline"**.
4. On the right side of the screen, click the **"Run workflow"** dropdown button, and click the green **"Run workflow"** button.
5. Wait about 1-2 minutes. The pipeline will spin up, extract today's stock data, and upload it to AWS!

---

## 3. Operations & Maintenance

### What if I want to change the schedule?
If you want the pipeline to run at a different time:
1. Open the file `.github/workflows/etl_cron.yml`.
2. Look for the line: `- cron: '0 2 * * *'`
3. This is standard Cron syntax. Change it to your desired time and push the code to GitHub.

### What if AWS charges me money?
The infrastructure is designed using serverless components (S3, Athena, Glue).
- **S3** costs pennies per gigabyte. The stock data is compressed into Parquet, meaning it takes up mere kilobytes.
- **Athena** charges $5 per Terabyte queried. You are querying megabytes.
- Overall, this architecture falls entirely within the **AWS Free Tier** or will cost less than $0.10 a month.

### Adding New Developers to the Project
If someone else joins your team:
1. Have them clone the repo from GitHub.
2. Have them create their own `.env` file using `.env.example` as a template.
3. Give them AWS IAM Read-Only credentials so they can run the dashboard locally.

---

## 4. Troubleshooting

- **Dashboard is failing to load data**: Ensure your `.env` file exists locally and has your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- **GitHub Actions is failing**: Check the logs in the GitHub Actions tab. It is usually caused by Wikipedia changing its table structure or Yahoo Finance rate-limiting the IP. The code has robust error handling, but APIs can change!
- **Terraform says state is locked**: If you ever run Terraform manually and it locks, simply go to your AWS console, or ensure no other terminal is currently running an apply. (You shouldn't need to run Terraform again, it is already deployed!)

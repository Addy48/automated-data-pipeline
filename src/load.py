import logging
import pandas as pd
import json
import boto3
import botocore
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import os

logger = logging.getLogger("sp500_pipeline")

def _get_boto3_client():
    """Internal factory to get boto3 S3 client."""
    return boto3.client('s3')

def _upload_to_s3(local_path: str, bucket: str, s3_key: str) -> bool:
    """Helper to upload a file to S3."""
    client = _get_boto3_client()
    try:
        client.upload_file(local_path, bucket, s3_key)
        logger.info(f"Successfully uploaded {local_path} to s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"S3 Upload failed for {local_path}: {e}")
        return False
    except Exception as e:
        logger.critical(f"Unexpected error during S3 upload of {local_path}: {e}")
        return False

def upload_bronze(df: pd.DataFrame, bucket: str, run_id: str) -> bool:
    """Save raw data to local parquet and upload to Bronze S3 layer."""
    if df.empty:
        logger.warning("Empty DataFrame passed to upload_bronze.")
        return False
        
    local_path = f"data/raw_{run_id}.parquet"
    s3_key = f"raw/run_id={run_id}/data.parquet"
    
    try:
        df.to_parquet(local_path, engine="pyarrow", index=False)
        return _upload_to_s3(local_path, bucket, s3_key)
    except Exception as e:
        logger.error(f"Failed to write bronze parquet: {e}")
        return False

def upload_silver(df: pd.DataFrame, bucket: str, run_id: str) -> bool:
    """Save cleaned/transformed data to local parquet and upload to Silver S3 layer."""
    if df.empty:
        logger.warning("Empty DataFrame passed to upload_silver.")
        return False
        
    local_path = f"data/processed_{run_id}.parquet"
    s3_key = f"processed/run_id={run_id}/data.parquet"
    
    try:
        df.to_parquet(local_path, engine="pyarrow", index=False)
        return _upload_to_s3(local_path, bucket, s3_key)
    except Exception as e:
        logger.error(f"Failed to write silver parquet: {e}")
        return False

def upload_gold(df: pd.DataFrame, bucket: str, run_id: str) -> bool:
    """Save analytics-ready data to local parquet & CSV, and upload to Gold S3 layer."""
    if df.empty:
        logger.warning("Empty DataFrame passed to upload_gold.")
        return False
        
    local_pq_path = f"data/analytics_{run_id}.parquet"
    local_csv_path = f"data/analytics_{run_id}.csv"
    s3_pq_key = f"analytics/run_id={run_id}/data.parquet"
    s3_csv_key = f"analytics/run_id={run_id}/data.csv"
    
    try:
        df.to_parquet(local_pq_path, engine="pyarrow", index=False)
        df.to_csv(local_csv_path, index=False)
        
        pq_success = _upload_to_s3(local_pq_path, bucket, s3_pq_key)
        csv_success = _upload_to_s3(local_csv_path, bucket, s3_csv_key)
        return pq_success and csv_success
    except Exception as e:
        logger.error(f"Failed to write gold datasets: {e}")
        return False

def upload_metrics(metrics: Dict[str, Any], bucket: str, run_id: str) -> bool:
    """Save pipeline execution metrics to local JSON and upload to Observability S3 layer."""
    if not metrics:
        return False
        
    local_path = f"logs/metrics_{run_id}.json"
    s3_key = f"observability/run_id={run_id}/metrics.json"
    
    try:
        with open(local_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        return _upload_to_s3(local_path, bucket, s3_key)
    except Exception as e:
        logger.error(f"Failed to write metrics json: {e}")
        return False

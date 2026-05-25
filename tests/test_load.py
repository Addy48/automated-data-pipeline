import pytest
import pandas as pd
import json
import os
import boto3
from moto import mock_aws
from botocore.exceptions import ClientError
from src.load import upload_bronze, upload_silver, upload_gold, upload_metrics, _get_boto3_client

@pytest.fixture
def dummy_df():
    return pd.DataFrame({"A": [1, 2], "B": [3, 4]})

@pytest.fixture
def mock_s3():
    with mock_aws():
        client = boto3.client('s3', region_name='us-east-1')
        client.create_bucket(Bucket='test-bucket')
        yield client

def test_upload_bronze_success(dummy_df, mock_s3):
    success = upload_bronze(dummy_df, 'test-bucket', 'test_run')
    assert success
    
    # Verify file is in S3
    response = mock_s3.list_objects_v2(Bucket='test-bucket', Prefix='raw/run_id=test_run/')
    assert 'Contents' in response
    assert len(response['Contents']) == 1
    assert response['Contents'][0]['Key'] == 'raw/run_id=test_run/data.parquet'

def test_upload_silver_success(dummy_df, mock_s3):
    success = upload_silver(dummy_df, 'test-bucket', 'test_run')
    assert success
    
    response = mock_s3.list_objects_v2(Bucket='test-bucket', Prefix='processed/run_id=test_run/')
    assert 'Contents' in response
    assert len(response['Contents']) == 1

def test_upload_gold_success(dummy_df, mock_s3):
    success = upload_gold(dummy_df, 'test-bucket', 'test_run')
    assert success
    
    response = mock_s3.list_objects_v2(Bucket='test-bucket', Prefix='analytics/run_id=test_run/')
    assert 'Contents' in response
    assert len(response['Contents']) == 2 # parquet and csv

def test_upload_metrics_success(mock_s3):
    metrics = {"status": "SUCCESS", "rows": 100}
    success = upload_metrics(metrics, 'test-bucket', 'test_run')
    assert success
    
    response = mock_s3.list_objects_v2(Bucket='test-bucket', Prefix='observability/run_id=test_run/')
    assert 'Contents' in response
    assert len(response['Contents']) == 1

def test_upload_empty_df_returns_false():
    empty_df = pd.DataFrame()
    assert not upload_bronze(empty_df, 'test-bucket', 'run1')
    assert not upload_silver(empty_df, 'test-bucket', 'run1')
    assert not upload_gold(empty_df, 'test-bucket', 'run1')

def test_upload_failure_handling(dummy_df, mock_s3):
    # Try to upload to a non-existent bucket
    success = upload_bronze(dummy_df, 'nonexistent-bucket', 'test_run')
    assert not success

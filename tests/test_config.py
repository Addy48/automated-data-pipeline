from src.config import load_config


def test_bucket_read_from_s3_bucket_name():
    cfg = load_config({"S3_BUCKET_NAME": "my-lake", "AWS_ACCESS_KEY_ID": "a", "AWS_SECRET_ACCESS_KEY": "b"})
    assert cfg.bucket == "my-lake"
    assert cfg.can_upload


def test_legacy_alias_still_accepted():
    assert load_config({"AWS_BUCKET_NAME": "old-name"}).bucket == "old-name"


def test_placeholder_bucket_counts_as_unset():
    cfg = load_config({"S3_BUCKET_NAME": "your-bucket-name-here", "AWS_ACCESS_KEY_ID": "a", "AWS_SECRET_ACCESS_KEY": "b"})
    assert cfg.bucket is None
    assert not cfg.can_upload


def test_upload_needs_bucket_and_both_keys():
    assert not load_config({"S3_BUCKET_NAME": "b", "AWS_ACCESS_KEY_ID": "a"}).can_upload
    assert load_config({}).region == "us-east-1"

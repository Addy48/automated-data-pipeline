import logging
import os
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass
class S3Paths:
    raw: str = "raw/"
    processed: str = "processed/"
    analytics: str = "analytics/"
    observability: str = "observability/"


@dataclass(frozen=True)
class Settings:
    """Runtime settings read from the environment."""

    bucket: Optional[str]
    region: str
    has_credentials: bool

    @property
    def can_upload(self) -> bool:
        return bool(self.bucket and self.has_credentials)


def _is_placeholder(value: Optional[str]) -> bool:
    return not value or value.startswith("your-")


def load_config(env: Optional[Mapping[str, str]] = None) -> Settings:
    """Read settings from environment variables.

    The bucket comes from ``S3_BUCKET_NAME`` (the name used in ``.env.example``, the
    workflow and the Terraform outputs). ``AWS_BUCKET_NAME`` is still accepted as an
    older alias. A placeholder such as ``your-bucket-name-here`` counts as unset.
    """
    env = os.environ if env is None else env
    bucket = env.get("S3_BUCKET_NAME") or env.get("AWS_BUCKET_NAME")
    return Settings(
        bucket=None if _is_placeholder(bucket) else bucket,
        region=env.get("AWS_REGION") or "us-east-1",
        has_credentials=bool(
            env.get("AWS_ACCESS_KEY_ID") and env.get("AWS_SECRET_ACCESS_KEY")
        ),
    )


def setup_logging(level=logging.INFO):
    """Setup structured logging for the pipeline."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("sp500_pipeline")


S3_PATHS = S3Paths()

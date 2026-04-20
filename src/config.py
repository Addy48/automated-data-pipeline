import os
import logging
from dataclasses import dataclass


@dataclass
class S3Paths:
    raw: str = "raw/"
    processed: str = "processed/"
    analytics: str = "analytics/"
    observability: str = "observability/"


def load_config():
    """Load configuration from environment variables."""
    # Ensure critical variables exist, though we might not fail immediately if running locally
    pass


def setup_logging(level=logging.INFO):
    """Setup structured logging for the pipeline."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("sp500_pipeline")


S3_PATHS = S3Paths()

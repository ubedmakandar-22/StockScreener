"""
Configuration module for Stock Scanner application.
Handles environment-based settings and application constants.
"""

import os
from datetime import timedelta
from typing import Literal


class Config:
    """Base configuration class."""

    # Flask settings
    DEBUG = False
    TESTING = False
    ENV = "production"

    # NSE API Configuration
    NSE_BASE_URL = "https://www.nseindia.com"
    NSE_API_BASE_URL = "https://www.nseindia.com/api"
    NSE_TIMEOUT = 30
    NSE_MAX_RETRIES = 3
    NSE_RETRY_DELAY = 2  # seconds

    # Headers to mimic browser requests
    NSE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # Cache configuration
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 minutes in seconds
    CACHE_BACKEND = "memory"  # memory, redis (future)

    # Scanner configuration
    SCANNER_TIMEOUT = 30  # seconds per stock
    SCANNER_MAX_WORKERS = 10  # ThreadPoolExecutor workers
    SCANNER_BATCH_SIZE = 50  # Process stocks in batches

    # Indicator parameters
    EMA_FAST = 10
    EMA_SHORT = 20
    EMA_MEDIUM = 50
    EMA_LONG = 200
    RSI_PERIOD = 14
    VOLUME_AVG_PERIOD = 20

    # Scanner thresholds
    DAILY_RSI_MIN = 60
    DAILY_VOLUME_RATIO_MIN = 1.5
    DAILY_PRICE_FROM_52W_HIGH_MAX = 5.0  # percentage

    WEEKLY_RSI_MIN = 55
    WEEKLY_SWING_COUNT = 3  # Check last 3 swings

    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/stock_scanner.log"
    LOG_MAX_BYTES = 10485760  # 10 MB
    LOG_BACKUP_COUNT = 5

    # API Response configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    ENV = "development"
    NSE_MAX_RETRIES = 2
    SCANNER_MAX_WORKERS = 5  # Fewer workers in dev


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    ENV = "testing"
    CACHE_ENABLED = False
    NSE_MAX_RETRIES = 1
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "production"
    NSE_MAX_RETRIES = 3
    SCANNER_MAX_WORKERS = 15


def get_config(env: Literal["development", "testing", "production"] | None = None) -> Config:
    """
    Get configuration based on environment.

    Args:
        env: Environment name. If None, reads from FLASK_ENV or defaults to production.

    Returns:
        Configuration object.
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "production")

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    return config_map.get(env, ProductionConfig)()

"""Test fixtures and configuration."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from config import TestingConfig
from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(env="testing")
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_stock_data():
    """
    Create sample stock OHLCV data.

    Returns:
        DataFrame with sample data.
    """
    dates = pd.date_range(end=datetime.now(), periods=365, freq="D")
    np.random.seed(42)

    data = {
        "timestamp": dates,
        "open": np.random.uniform(100, 200, 365),
        "high": np.random.uniform(110, 210, 365),
        "low": np.random.uniform(90, 190, 365),
        "close": np.random.uniform(100, 200, 365),
        "volume": np.random.uniform(1000000, 5000000, 365).astype(int),
        "symbol": "TRENT",
    }

    df = pd.DataFrame(data)
    # Ensure high > low and high >= close, low <= close
    df["high"] = df[["open", "close"]].max(axis=1) + np.random.uniform(1, 10, 365)
    df["low"] = df[["open", "close"]].min(axis=1) - np.random.uniform(1, 10, 365)
    return df


@pytest.fixture
def bullish_stock_data():
    """
    Create bullish trending stock data.

    Returns:
        DataFrame with uptrending data.
    """
    dates = pd.date_range(end=datetime.now(), periods=365, freq="D")
    closes = np.linspace(100, 200, 365)  # Strong uptrend
    volumes = np.linspace(1000000, 3000000, 365)

    data = {
        "timestamp": dates,
        "open": closes - 2,
        "close": closes,
        "high": closes + 5,
        "low": closes - 5,
        "volume": volumes.astype(int),
        "symbol": "BULLISH",
    }

    return pd.DataFrame(data)

"""Tests for services."""

import pytest
import pandas as pd
from services.cache import CacheManager
from services.market_data import MarketDataService


class TestCacheManager:
    """Test cache manager."""

    def test_cache_set_get(self):
        """Test cache set and get."""
        cache = CacheManager(ttl=3600)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        """Test cache miss."""
        cache = CacheManager(ttl=3600)

        assert cache.get("nonexistent") is None

    def test_cache_delete(self):
        """Test cache delete."""
        cache = CacheManager(ttl=3600)

        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_cache_clear(self):
        """Test cache clear."""
        cache = CacheManager(ttl=3600)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.size() == 0

    def test_cache_size(self):
        """Test cache size."""
        cache = CacheManager(ttl=3600)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size() == 2


class TestMarketDataService:
    """Test market data service."""

    def test_resample_weekly(self, sample_stock_data):
        """Test weekly resampling."""
        weekly = MarketDataService.resample_weekly(sample_stock_data)

        assert len(weekly) <= len(sample_stock_data) / 5  # Roughly 52 weeks
        assert "open" in weekly.columns
        assert "close" in weekly.columns

    def test_resample_monthly(self, sample_stock_data):
        """Test monthly resampling."""
        monthly = MarketDataService.resample_monthly(sample_stock_data)

        assert len(monthly) <= 12  # Roughly 12 months
        assert "open" in monthly.columns
        assert "close" in monthly.columns

    def test_is_bullish_candle(self):
        """Test bullish candle detection."""
        assert MarketDataService.is_bullish_candle(100, 110) is True
        assert MarketDataService.is_bullish_candle(110, 100) is False
        assert MarketDataService.is_bullish_candle(100, 100) is False

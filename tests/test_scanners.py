"""Tests for scanner modules."""

import pytest
import pandas as pd
from config import TestingConfig
from scanner.daily import DailyScanner
from scanner.weekly import WeeklyScanner
from scanner.monthly import MonthlyScanner


class TestDailyScanner:
    """Test daily scanner."""

    def test_daily_scan_with_sample_data(self, sample_stock_data):
        """Test daily scanner with sample data."""
        config = TestingConfig()
        scanner = DailyScanner(config)

        result = scanner.scan(sample_stock_data, "TEST")

        assert result.symbol == "TEST"
        assert result.price >= 0
        assert isinstance(result.daily, bool)

    def test_daily_scan_with_bullish_data(self, bullish_stock_data):
        """Test daily scanner with bullish data."""
        config = TestingConfig()
        scanner = DailyScanner(config)

        result = scanner.scan(bullish_stock_data, "BULLISH")

        assert result.symbol == "BULLISH"
        assert result.indicators is not None
        assert result.indicators.rsi > 0

    def test_daily_scan_with_empty_data(self):
        """Test daily scanner with empty data."""
        config = TestingConfig()
        scanner = DailyScanner(config)

        result = scanner.scan(pd.DataFrame(), "EMPTY")

        assert result.daily is False

    def test_daily_scan_with_insufficient_data(self):
        """Test daily scanner with insufficient data."""
        config = TestingConfig()
        scanner = DailyScanner(config)

        small_df = pd.DataFrame({
            "close": [1, 2, 3],
            "volume": [1000, 1000, 1000],
            "high": [2, 3, 4],
            "low": [0, 1, 2],
        })

        result = scanner.scan(small_df, "SMALL")
        assert result.daily is False


class TestWeeklyScanner:
    """Test weekly scanner."""

    def test_weekly_scan_with_sample_data(self, sample_stock_data):
        """Test weekly scanner with sample data."""
        config = TestingConfig()
        scanner = WeeklyScanner(config)

        result = scanner.scan(sample_stock_data, "TEST")

        assert result.symbol == "TEST"
        assert isinstance(result.weekly, bool)

    def test_weekly_scan_with_bullish_data(self, bullish_stock_data):
        """Test weekly scanner with bullish data."""
        config = TestingConfig()
        scanner = WeeklyScanner(config)

        result = scanner.scan(bullish_stock_data, "BULLISH")

        assert result.symbol == "BULLISH"


class TestMonthlyScanner:
    """Test monthly scanner."""

    def test_monthly_scan_with_sample_data(self, sample_stock_data):
        """Test monthly scanner with sample data."""
        config = TestingConfig()
        scanner = MonthlyScanner(config)

        result = scanner.scan(sample_stock_data, "TEST")

        assert result.symbol == "TEST"
        assert isinstance(result.monthly, bool)

    def test_monthly_scan_with_bullish_data(self, bullish_stock_data):
        """Test monthly scanner with bullish data."""
        config = TestingConfig()
        scanner = MonthlyScanner(config)

        result = scanner.scan(bullish_stock_data, "BULLISH")

        assert result.symbol == "BULLISH"

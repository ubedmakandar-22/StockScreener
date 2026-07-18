"""Tests for indicator calculations."""

import pytest
import pandas as pd
import numpy as np
from scanner.indicators import Indicators


class TestEMA:
    """Test EMA calculation."""

    def test_ema_basic(self):
        """Test basic EMA calculation."""
        data = pd.Series([1, 2, 3, 4, 5])
        ema = Indicators.ema(data, period=2)

        assert len(ema) == len(data)
        assert ema.iloc[-1] > data.iloc[0]

    def test_ema_insufficient_data(self):
        """Test EMA with insufficient data."""
        data = pd.Series([1, 2])
        ema = Indicators.ema(data, period=10)

        assert len(ema) == len(data)
        assert pd.isna(ema.iloc[0])

    def test_ema_with_sample_data(self, sample_stock_data):
        """Test EMA with sample stock data."""
        df = sample_stock_data
        ema20 = Indicators.ema(df["close"], period=20)
        ema50 = Indicators.ema(df["close"], period=50)

        assert len(ema20) == len(df)
        assert len(ema50) == len(df)
        assert not np.isnan(ema20.iloc[-1])
        assert not np.isnan(ema50.iloc[-1])


class TestRSI:
    """Test RSI calculation."""

    def test_rsi_range(self, sample_stock_data):
        """Test RSI is between 0 and 100."""
        df = sample_stock_data
        rsi = Indicators.rsi(df["close"], period=14)

        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        data = pd.Series([1, 2, 3])
        rsi = Indicators.rsi(data, period=14)

        assert len(rsi) == len(data)

    def test_rsi_uptrend(self, bullish_stock_data):
        """Test RSI in uptrend should be higher."""
        df = bullish_stock_data
        rsi = Indicators.rsi(df["close"], period=14)

        # In strong uptrend, RSI should be > 50 on average
        avg_rsi = rsi.dropna().tail(50).mean()
        assert avg_rsi > 50


class TestAverageVolume:
    """Test average volume calculation."""

    def test_avg_volume_calculation(self, sample_stock_data):
        """Test average volume calculation."""
        df = sample_stock_data
        avg_vol = Indicators.average_volume(df["volume"], period=20)

        assert len(avg_vol) == len(df)
        assert not np.isnan(avg_vol.iloc[-1])

    def test_avg_volume_vs_manual(self):
        """Test average volume against manual calculation."""
        volumes = pd.Series([1000, 2000, 3000, 4000, 5000])
        avg_vol = Indicators.average_volume(volumes, period=3)

        # Check last value
        expected = (3000 + 4000 + 5000) / 3
        assert abs(avg_vol.iloc[-1] - expected) < 0.01


class TestVolumeRatio:
    """Test volume ratio calculation."""

    def test_volume_ratio_basic(self):
        """Test volume ratio calculation."""
        ratio = Indicators.volume_ratio(3000, 1000)
        assert ratio == 3.0

    def test_volume_ratio_zero_avg(self):
        """Test volume ratio with zero average."""
        ratio = Indicators.volume_ratio(1000, 0)
        assert ratio is None

    def test_volume_ratio_half(self):
        """Test volume ratio less than 1."""
        ratio = Indicators.volume_ratio(500, 1000)
        assert ratio == 0.5


class TestDistanceFrom52wHigh:
    """Test distance from 52w high calculation."""

    def test_distance_at_high(self):
        """Test when price equals 52w high."""
        distance = Indicators.distance_from_52w_high(100, 100)
        assert distance == 0.0

    def test_distance_below_high(self):
        """Test when price is below 52w high."""
        distance = Indicators.distance_from_52w_high(90, 100)
        assert distance == 10.0

    def test_distance_zero_high(self):
        """Test with zero high."""
        distance = Indicators.distance_from_52w_high(50, 0)
        assert distance is None


class TestHigherHighsLows:
    """Test higher highs and lows detection."""

    def test_higher_highs_true(self):
        """Test detection of higher highs."""
        df = pd.DataFrame({
            "high": [100, 110, 120, 130],
            "low": [90, 100, 110, 120],
        })
        assert Indicators.higher_highs(df, count=3) is True

    def test_higher_highs_false(self):
        """Test when highs not increasing."""
        df = pd.DataFrame({
            "high": [100, 120, 110, 130],
            "low": [90, 100, 110, 120],
        })
        assert Indicators.higher_highs(df, count=3) is False

    def test_higher_lows_true(self):
        """Test detection of higher lows."""
        df = pd.DataFrame({
            "high": [100, 110, 120, 130],
            "low": [90, 100, 110, 120],
        })
        assert Indicators.higher_lows(df, count=3) is True

    def test_higher_lows_false(self):
        """Test when lows not increasing."""
        df = pd.DataFrame({
            "high": [100, 110, 120, 130],
            "low": [90, 100, 95, 120],
        })
        assert Indicators.higher_lows(df, count=3) is False

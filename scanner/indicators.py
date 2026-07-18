"""Indicator calculations for stock analysis."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class Indicators:
    """Calculate technical indicators."""

    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Args:
            series: Price series.
            period: EMA period.

        Returns:
            EMA series.
        """
        if series is None or len(series) < period:
            return pd.Series([np.nan] * len(series))

        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            series: Price series.
            period: RSI period.

        Returns:
            RSI series.
        """
        if series is None or len(series) < period + 1:
            return pd.Series([np.nan] * len(series))

        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def average_volume(series: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Average Volume.

        Args:
            series: Volume series.
            period: Average period.

        Returns:
            Average volume series.
        """
        if series is None or len(series) < period:
            return pd.Series([np.nan] * len(series))

        return series.rolling(window=period).mean()

    @staticmethod
    def volume_ratio(current_volume: float, avg_volume: float) -> Optional[float]:
        """
        Calculate volume ratio.

        Args:
            current_volume: Current volume.
            avg_volume: Average volume.

        Returns:
            Volume ratio or None if avg_volume is 0.
        """
        if avg_volume == 0:
            return None
        return current_volume / avg_volume

    @staticmethod
    def distance_from_52w_high(current_price: float, high_52w: float) -> Optional[float]:
        """
        Calculate distance from 52-week high in percentage.

        Args:
            current_price: Current price.
            high_52w: 52-week high price.

        Returns:
            Distance percentage or None.
        """
        if high_52w == 0:
            return None
        return ((high_52w - current_price) / high_52w) * 100

    @staticmethod
    def higher_highs(df: pd.DataFrame, count: int = 3) -> bool:
        """
        Check if last N swing highs are increasing.

        Args:
            df: OHLCV DataFrame.
            count: Number of swings to check.

        Returns:
            True if higher highs detected.
        """
        if df is None or len(df) < count + 1:
            return False

        highs = df["high"].tail(count + 1).values
        return all(highs[i] < highs[i + 1] for i in range(len(highs) - 1))

    @staticmethod
    def higher_lows(df: pd.DataFrame, count: int = 3) -> bool:
        """
        Check if last N swing lows are increasing.

        Args:
            df: OHLCV DataFrame.
            count: Number of swings to check.

        Returns:
            True if higher lows detected.
        """
        if df is None or len(df) < count + 1:
            return False

        lows = df["low"].tail(count + 1).values
        return all(lows[i] < lows[i + 1] for i in range(len(lows) - 1))

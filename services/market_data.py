"""Market data service."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service to process and manage market data."""

    @staticmethod
    def resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
        """
        Resample daily data to weekly OHLCV.

        Args:
            df: Daily OHLCV DataFrame.

        Returns:
            Weekly OHLCV DataFrame.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        df_copy = df.copy()
        df_copy["timestamp"] = pd.to_datetime(df_copy["timestamp"])
        df_copy.set_index("timestamp", inplace=True)

        weekly = df_copy.resample("W").agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )

        weekly.reset_index(inplace=True)
        if "symbol" in df_copy.columns:
            weekly["symbol"] = df_copy["symbol"].iloc[0]

        return weekly

    @staticmethod
    def resample_monthly(df: pd.DataFrame) -> pd.DataFrame:
        """
        Resample daily data to monthly OHLCV.

        Args:
            df: Daily OHLCV DataFrame.

        Returns:
            Monthly OHLCV DataFrame.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        df_copy = df.copy()
        df_copy["timestamp"] = pd.to_datetime(df_copy["timestamp"])
        df_copy.set_index("timestamp", inplace=True)

        monthly = df_copy.resample("M").agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )

        monthly.reset_index(inplace=True)
        if "symbol" in df_copy.columns:
            monthly["symbol"] = df_copy["symbol"].iloc[0]

        return monthly

    @staticmethod
    def is_bullish_candle(open_price: float, close_price: float) -> bool:
        """
        Check if candle is bullish.

        Args:
            open_price: Opening price.
            close_price: Closing price.

        Returns:
            True if bullish, False otherwise.
        """
        return close_price > open_price

"""Daily momentum scanner."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from scanner.indicators import Indicators
from config import Config
from models.stock import Indicators as IndicatorsModel, ScannerResult

logger = logging.getLogger(__name__)


class DailyScanner:
    """Daily momentum scanner."""

    def __init__(self, config: Config):
        """Initialize daily scanner."""
        self.config = config

    def scan(self, df: pd.DataFrame, symbol: str) -> ScannerResult:
        """
        Scan stock for daily momentum conditions.

        Args:
            df: Daily OHLCV DataFrame.
            symbol: Stock symbol.

        Returns:
            ScannerResult with conditions met.
        """
        result = ScannerResult(symbol=symbol, price=0.0, daily=False)

        try:
            if df is None or len(df) < 200:
                logger.warning(f"Insufficient data for {symbol}")
                return result

            # Get latest values
            current_close = df["close"].iloc[-1]
            current_volume = df["volume"].iloc[-1]

            # Calculate indicators
            ema10 = Indicators.ema(df["close"], self.config.EMA_FAST).iloc[-1]
            ema20 = Indicators.ema(df["close"], self.config.EMA_SHORT).iloc[-1]
            ema50 = Indicators.ema(df["close"], self.config.EMA_MEDIUM).iloc[-1]
            ema200 = Indicators.ema(df["close"], self.config.EMA_LONG).iloc[-1]
            rsi = Indicators.rsi(df["close"], self.config.RSI_PERIOD).iloc[-1]
            avg_volume = Indicators.average_volume(
                df["volume"], self.config.VOLUME_AVG_PERIOD
            ).iloc[-1]
            high_52w = df["high"].tail(252).max()  # 252 trading days ~= 1 year

            volume_ratio = Indicators.volume_ratio(current_volume, avg_volume)
            distance_from_high = Indicators.distance_from_52w_high(
                current_close, high_52w
            )

            # Check conditions
            condition1 = current_close > ema20
            condition2 = ema20 > ema50
            condition3 = ema50 > ema200
            condition4 = volume_ratio > self.config.DAILY_VOLUME_RATIO_MIN
            condition5 = rsi > self.config.DAILY_RSI_MIN
            condition6 = distance_from_high < self.config.DAILY_PRICE_FROM_52W_HIGH_MAX

            all_conditions_met = all(
                [condition1, condition2, condition3, condition4, condition5, condition6]
            )

            indicators = IndicatorsModel(
                symbol=symbol,
                ema10=float(ema10),
                ema20=float(ema20),
                ema50=float(ema50),
                ema200=float(ema200),
                rsi=float(rsi),
                average_volume=float(avg_volume),
                volume_ratio=float(volume_ratio) if volume_ratio else None,
                high_52w=float(high_52w),
                distance_from_52w_high=float(distance_from_high)
                if distance_from_high
                else None,
            )

            result = ScannerResult(
                symbol=symbol,
                price=float(current_close),
                daily=all_conditions_met,
                indicators=indicators,
            )

            logger.info(f"{symbol} Daily: {all_conditions_met}")
            return result

        except Exception as e:
            logger.error(f"Error scanning {symbol} daily: {e}", exc_info=True)
            result.error = str(e)
            return result

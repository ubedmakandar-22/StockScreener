"""Monthly trend scanner."""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from scanner.indicators import Indicators
from services.market_data import MarketDataService
from config import Config
from models.stock import Indicators as IndicatorsModel, ScannerResult

logger = logging.getLogger(__name__)


class MonthlyScanner:
    """Monthly trend scanner."""

    def __init__(self, config: Config):
        """Initialize monthly scanner."""
        self.config = config
        self.market_data = MarketDataService()

    def scan(self, df: pd.DataFrame, symbol: str) -> ScannerResult:
        """
        Scan stock for monthly trend conditions.

        Args:
            df: Daily OHLCV DataFrame.
            symbol: Stock symbol.

        Returns:
            ScannerResult with conditions met.
        """
        result = ScannerResult(symbol=symbol, price=0.0, monthly=False)

        try:
            if df is None or len(df) < 100:
                logger.warning(f"Insufficient data for {symbol} monthly")
                return result

            # Resample to monthly
            monthly_df = MarketDataService.resample_monthly(df)

            if len(monthly_df) < 12:
                logger.warning(f"Insufficient monthly data for {symbol}")
                return result

            # Get latest values
            current_close = monthly_df["close"].iloc[-1]
            current_open = monthly_df["open"].iloc[-1]
            current_volume = monthly_df["volume"].iloc[-1]

            # Calculate indicators
            ema10 = Indicators.ema(monthly_df["close"], self.config.EMA_FAST).iloc[-1]
            rsi = Indicators.rsi(monthly_df["close"], self.config.RSI_PERIOD).iloc[-1]
            avg_volume = Indicators.average_volume(
                monthly_df["volume"], self.config.VOLUME_AVG_PERIOD
            ).iloc[-1]

            # Check conditions
            condition1 = current_close > ema10
            condition2 = MarketDataService.is_bullish_candle(current_open, current_close)
            condition3 = Indicators.higher_highs(
                monthly_df, self.config.WEEKLY_SWING_COUNT
            )

            all_conditions_met = all([condition1, condition2, condition3])

            volume_ratio = Indicators.volume_ratio(current_volume, avg_volume)
            high_52w = df["high"].tail(252).max()
            distance_from_high = Indicators.distance_from_52w_high(
                current_close, high_52w
            )

            indicators = IndicatorsModel(
                symbol=symbol,
                ema10=float(ema10),
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
                monthly=all_conditions_met,
                indicators=indicators,
            )

            logger.info(f"{symbol} Monthly: {all_conditions_met}")
            return result

        except Exception as e:
            logger.error(f"Error scanning {symbol} monthly: {e}", exc_info=True)
            result.error = str(e)
            return result

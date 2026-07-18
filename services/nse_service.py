"""NSE India data service."""

import logging
from typing import Optional
import requests
import pandas as pd
from datetime import datetime, timedelta

from config import Config
from utils.helpers import retry

logger = logging.getLogger(__name__)


class NSEService:
    """Service to fetch data from NSE India."""

    def __init__(self, config: Config):
        """Initialize NSE service."""
        self.config = config
        self.base_url = config.NSE_BASE_URL
        self.api_url = config.NSE_API_BASE_URL
        self.timeout = config.NSE_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update(config.NSE_HEADERS)

    @retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
    def get_nse_index_symbols(self) -> list[str]:
        """
        Fetch all NSE stock symbols.

        Returns:
            List of stock symbols.

        Raises:
            requests.RequestException: If API call fails.
        """
        try:
            url = f"{self.api_url}/allStocks"
            logger.info(f"Fetching NSE symbols from {url}")

            # First, get the index page to establish session
            self.session.get(self.base_url, timeout=self.timeout)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            symbols = []

            if "records" in data and "data" in data["records"]:
                for stock in data["records"]["data"]:
                    if "symbol" in stock:
                        symbols.append(stock["symbol"])

            logger.info(f"Fetched {len(symbols)} NSE symbols")
            return symbols

        except requests.RequestException as e:
            logger.error(f"Failed to fetch NSE symbols: {e}")
            raise

    @retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
    def get_stock_data(
        self, symbol: str, period: str = "1y"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data for a symbol.

        Args:
            symbol: Stock symbol.
            period: Period for data ('1d', '1mo', '1y').

        Returns:
            DataFrame with OHLCV data or None if failed.
        """
        try:
            url = f"{self.api_url}/chart-data"
            params = {
                "symbol": symbol,
                "resolution": "D",
                "from": int((datetime.now() - timedelta(days=365)).timestamp()),
                "to": int(datetime.now().timestamp()),
            }

            logger.debug(f"Fetching data for {symbol}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if "candles" in data:
                df = pd.DataFrame(
                    data["candles"],
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
                )
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                df["symbol"] = symbol
                return df

            logger.warning(f"No candle data for {symbol}")
            return None

        except requests.RequestException as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return None

    def get_52w_high(self, df: pd.DataFrame) -> Optional[float]:
        """
        Get 52-week high from dataframe.

        Args:
            df: DataFrame with stock data.

        Returns:
            52-week high price or None.
        """
        if df is None or df.empty:
            return None

        # Get data for last 52 weeks
        cutoff_date = datetime.now() - timedelta(weeks=52)
        recent_data = df[df["timestamp"] >= cutoff_date]

        if recent_data.empty:
            return None

        return float(recent_data["high"].max())

    def get_current_price(self, df: pd.DataFrame) -> Optional[float]:
        """
        Get current price from latest candle.

        Args:
            df: DataFrame with stock data.

        Returns:
            Current close price or None.
        """
        if df is None or df.empty:
            return None

        return float(df.iloc[-1]["close"])

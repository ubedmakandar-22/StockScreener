"""Data models for stock scanner."""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class StockData:
    """Stock OHLCV data point."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Indicators:
    """Calculated indicators for a stock."""

    symbol: str
    ema10: Optional[float] = None
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    rsi: Optional[float] = None
    average_volume: Optional[float] = None
    volume_ratio: Optional[float] = None
    high_52w: Optional[float] = None
    distance_from_52w_high: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ScannerResult:
    """Result of scanner condition check."""

    symbol: str
    price: float
    daily: bool = False
    weekly: bool = False
    monthly: bool = False
    indicators: Optional[Indicators] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.indicators:
            data["indicators"] = self.indicators.to_dict()
        return data


@dataclass
class APIResponse:
    """Standard API response."""

    status: str
    data: Optional[list[dict]] = None
    error: Optional[str] = None
    count: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

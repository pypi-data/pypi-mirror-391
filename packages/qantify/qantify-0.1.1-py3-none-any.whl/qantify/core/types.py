"""Core type declarations used across qantify."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True, slots=True)
class Symbol:
    """Represents a tradable symbol.

    Attributes:
        value: Canonical symbol string, e.g. ``"BTC/USDT"``.
        exchange: Optional exchange or venue identifier, e.g. ``"binance"``.
    """

    value: str
    exchange: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Symbol value must be a non-empty string.")

    def __str__(self) -> str:
        if self.exchange:
            return f"{self.exchange}:{self.value}"
        return self.value


@dataclass(frozen=True, slots=True)
class TimeFrame:
    """Represents a normalized timeframe/frequency descriptor."""

    name: str
    pandas_value: str
    seconds: int

    def __post_init__(self) -> None:
        if self.seconds <= 0:
            raise ValueError("TimeFrame seconds must be positive.")
        if not self.name:
            raise ValueError("TimeFrame name must be provided.")
        if not self.pandas_value:
            raise ValueError("TimeFrame pandas_value must be provided.")

    def __str__(self) -> str:
        return self.name


@dataclass(slots=True)
class Bar:
    """Represents an OHLCV bar in a time series."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    symbol: Symbol = field(default_factory=lambda: Symbol("UNKNOWN"))
    timeframe: Optional[TimeFrame] = None

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise ValueError("High price cannot be lower than low price.")
        if not self.high >= self.open >= self.low:
            raise ValueError("Open price must lie within high/low range.")
        if not self.high >= self.close >= self.low:
            raise ValueError("Close price must lie within high/low range.")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative.")

        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))

    @property
    def midpoint(self) -> float:
        """Return the average of high and low."""

        return (self.high + self.low) * 0.5

    def to_tuple(self) -> tuple:
        """Return a tuple representation suitable for vectorized ingestion."""

        return (
            self.timestamp,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            str(self.symbol),
            self.timeframe.name if self.timeframe else None,
        )

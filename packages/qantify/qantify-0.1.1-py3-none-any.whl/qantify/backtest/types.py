"""Shared type declarations for backtesting engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from uuid import uuid4


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    BRACKET = "bracket"
    OCO = "oco"
    ALGOLIKE = "algo"


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"


class TimeInForce(str, Enum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


@dataclass(slots=True)
class Order:
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: float
    type: OrderType = OrderType.MARKET
    price: Optional[float] = None
    stop_price: Optional[float] = None
    tag: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    time_in_force: TimeInForce = TimeInForce.GTC
    trail_amount: Optional[float] = None
    trail_percent: Optional[float] = None
    meta: dict = field(default_factory=dict)
    parent_id: Optional[str] = None
    display_quantity: Optional[float] = None
    children: tuple[str, ...] = field(default_factory=tuple)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive.")
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

    @property
    def remaining(self) -> float:
        return max(0.0, self.quantity - self.filled_quantity)

    def mark_filled(self) -> None:
        self.filled_quantity = self.quantity
        self.status = OrderStatus.FILLED

    def mark_cancelled(self) -> None:
        self.status = OrderStatus.CANCELLED

    def mark_partial(self, fill_qty: float) -> None:
        self.filled_quantity += fill_qty
        if self.remaining <= 1e-9:
            self.mark_filled()
        else:
            self.status = OrderStatus.PARTIALLY_FILLED


@dataclass(slots=True)
class Fill:
    timestamp: datetime
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    commission: float = 0.0
    slippage: float = 0.0
    order: Optional[Order] = None

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("Fill price must be positive.")
        if self.quantity <= 0:
            raise ValueError("Fill quantity must be positive.")
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)


@dataclass(slots=True)
class Position:
    symbol: str
    side: PositionSide
    quantity: float
    avg_price: float
    unrealized_pnl: float = 0.0
    currency: Optional[str] = None

    @property
    def signed_quantity(self) -> float:
        return self.quantity if self.side == PositionSide.LONG else -self.quantity

    @property
    def symbol_currency(self) -> Optional[str]:
        return self.currency

    @symbol_currency.setter
    def symbol_currency(self, value: Optional[str]) -> None:
        self.currency = value


@dataclass(slots=True)
class PortfolioSnapshot:
    timestamp: datetime
    equity: float
    cash: float
    positions: tuple[Position, ...] = field(default_factory=tuple)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    gross_exposure: float = 0.0


@dataclass(slots=True)
class Trade:
    entry: Fill
    exit: Optional[Fill]
    quantity: float
    pnl: float
    return_pct: float
    max_drawdown: float
    direction: OrderSide

    def is_closed(self) -> bool:
        return self.exit is not None

    @property
    def duration(self) -> Optional[int]:
        if not self.entry or not self.exit:
            return None
        return int((self.exit.timestamp - self.entry.timestamp).total_seconds())


__all__ = [
    "Order",
    "Fill",
    "Trade",
    "PortfolioSnapshot",
    "Position",
    "PositionSide",
    "OrderStatus",
    "TimeInForce",
    "OrderType",
    "OrderSide",
]

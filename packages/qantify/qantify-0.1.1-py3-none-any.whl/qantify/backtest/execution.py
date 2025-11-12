"""Advanced execution and slippage modeling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

from qantify.backtest.types import Fill, Order, OrderSide
from qantify.core.utils import ensure_datetime

if TYPE_CHECKING:  # pragma: no cover - type hint only
    from qantify.backtest.market_microstructure import MarketMicrostructureSimulator


@dataclass(slots=True)
class OrderBookSnapshot:
    timestamp: datetime
    bids: List[tuple[float, float]]  # price, size
    asks: List[tuple[float, float]]


@dataclass(slots=True)
class LatencyModel:
    mean_ms: float = 10.0
    jitter_ms: float = 5.0

    def sample(self, rng: np.random.Generator) -> timedelta:
        delay = max(0.0, rng.normal(self.mean_ms, self.jitter_ms)) / 1000.0
        return timedelta(seconds=delay)


class SlippageModel:
    def apply(self, order: Order, base_price: float, quantity: float, book: Optional[OrderBookSnapshot] = None) -> float:
        return base_price


class OrderBookSlippage(SlippageModel):
    def __init__(self, *, depth: int = 5) -> None:
        self.depth = depth

    def apply(self, order: Order, base_price: float, quantity: float, book: Optional[OrderBookSnapshot] = None) -> float:
        if book is None:
            return base_price
        remaining = quantity
        if order.side == OrderSide.BUY:
            levels = book.asks[: self.depth]
        else:
            levels = book.bids[: self.depth]
        if not levels:
            return base_price
        cost = 0.0
        total = 0.0
        for price, size in levels:
            trade = min(size, remaining)
            if trade <= 0:
                break
            cost += price * trade
            total += trade
            remaining -= trade
        if total <= 0:
            return base_price
        return cost / total


class VolumeParticipationSlippage(SlippageModel):
    def __init__(self, *, participation_rate: float = 0.1, impact_factor: float = 0.05) -> None:
        self.participation_rate = participation_rate
        self.impact_factor = impact_factor

    def apply(self, order: Order, base_price: float, quantity: float, book: Optional[OrderBookSnapshot] = None) -> float:
        if book is None:
            return base_price
        avg_size = np.mean([size for _, size in (book.asks + book.bids)]) if (book.asks or book.bids) else quantity
        ratio = (quantity / max(self.participation_rate * avg_size, 1e-9))
        impact = self.impact_factor * np.log1p(ratio)
        if order.side == OrderSide.BUY:
            return base_price * (1 + impact)
        return base_price * (1 - impact)


class TWAPSlippage(SlippageModel):
    """Approximate the execution cost of spreading fills across equal slices."""

    def __init__(self, *, slices: int = 8, impact: float = 0.005) -> None:
        self.slices = max(1, slices)
        self.impact = impact

    def apply(self, order: Order, base_price: float, quantity: float, book: Optional[OrderBookSnapshot] = None) -> float:
        progress = order.meta.setdefault("twap_progress", 0)
        fraction = min(progress / self.slices, 1.0)
        adjustment = self.impact * (fraction - 0.5)
        order.meta["twap_progress"] = progress + 1
        if order.side == OrderSide.BUY:
            return base_price * (1 + adjustment)
        return base_price * (1 - adjustment)


class VWAPSlippage(SlippageModel):
    """Adjust fill price relative to observed VWAP drift."""

    def __init__(self, *, lookback: int = 20, sensitivity: float = 0.01) -> None:
        self.lookback = max(2, lookback)
        self.sensitivity = sensitivity
        self._history: List[float] = []

    def apply(self, order: Order, base_price: float, quantity: float, book: Optional[OrderBookSnapshot] = None) -> float:
        if book is None:
            return base_price
        best = book.asks[0][0] if order.side == OrderSide.BUY else book.bids[0][0]
        self._history.append(best)
        if len(self._history) > self.lookback:
            self._history.pop(0)
        avg = sum(self._history) / len(self._history)
        drift = (best - avg) / max(avg, 1e-9)
        adjust = 1 + self.sensitivity * drift
        return base_price * adjust


@dataclass(slots=True)
class QueueModel:
    """Simple queue depth model to throttle expected fills."""

    depth_decay: float = 0.2
    min_fill: float = 0.1

    def estimate(self, order: Order, quantity: float, book: Optional[OrderBookSnapshot]) -> float:
        if book is None or quantity <= 0:
            return quantity
        levels = book.asks if order.side == OrderSide.BUY else book.bids
        depth = sum(level[1] for level in levels) or quantity
        ratio = quantity / max(depth, 1e-9)
        fill_fraction = max(self.min_fill, 1 - self.depth_decay * ratio)
        return quantity * fill_fraction


class ExecutionEngine:
    def __init__(
        self,
        *,
        latency_model: Optional[LatencyModel] = None,
        slippage_models: Optional[Iterable[SlippageModel]] = None,
        rng: Optional[np.random.Generator] = None,
        microstructure: "MarketMicrostructureSimulator | None" = None,
        queue_model: Optional[QueueModel] = None,
    ) -> None:
        self.latency_model = latency_model or LatencyModel()
        self.slippage_models = list(slippage_models or [SlippageModel()])
        self.rng = rng or np.random.default_rng()
        self.microstructure = microstructure
        self.queue_model = queue_model

    def execute(
        self,
        order: Order,
        *,
        base_price: float,
        book: Optional[OrderBookSnapshot] = None,
        timestamp: Optional[datetime] = None,
    ) -> Fill:
        delay = self.latency_model.sample(self.rng)
        fill_time = ensure_datetime(timestamp or order.timestamp) + delay

        adjusted_price = base_price
        for model in self.slippage_models:
            adjusted_price = model.apply(order, adjusted_price, order.remaining or order.quantity, book)

        fill_quantity = float(order.remaining or order.quantity)
        if self.queue_model is not None:
            fill_quantity = float(self.queue_model.estimate(order, fill_quantity, book))
        if self.microstructure is not None:
            adjusted_price, meta = self.microstructure.simulate_order(order, adjusted_price, fill_quantity, book)
            expected = meta.get("expected_fill") if meta else None
            if isinstance(expected, (int, float)) and expected > 0:
                fill_quantity = float(min(fill_quantity, expected))
            if meta:
                micro_meta = order.meta.setdefault("microstructure", {})
                micro_meta.update(meta)
        if fill_quantity <= 0:
            fill_quantity = float(order.remaining or order.quantity)

        return Fill(
            timestamp=fill_time,
            symbol=order.symbol,
            side=order.side,
            price=float(adjusted_price),
            quantity=fill_quantity,
            order=order,
        )


class VWAPParticipationModel:
    """Generate target price/size based on VWAP and participation rates."""

    def __init__(self, *, interval: int = 60, participation: float = 0.1) -> None:
        self.interval = interval
        self.participation = participation

    def target_quantity(self, historical_volume: float) -> float:
        return historical_volume * self.participation

    def target_price(self, bars: pd.DataFrame) -> float:
        vwap = (bars["close"] * bars["volume"]).sum() / max(bars["volume"].sum(), 1e-9)
        return float(vwap)


__all__ = [
    "OrderBookSnapshot",
    "LatencyModel",
    "SlippageModel",
    "OrderBookSlippage",
    "VolumeParticipationSlippage",
    "TWAPSlippage",
    "VWAPSlippage",
    "ExecutionEngine",
    "VWAPParticipationModel",
    "QueueModel",
]

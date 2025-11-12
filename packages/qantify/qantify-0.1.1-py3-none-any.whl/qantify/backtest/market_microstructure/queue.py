from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

from qantify.backtest.execution import OrderBookSnapshot
from qantify.backtest.types import OrderSide


@dataclass(slots=True)
class QueueEstimate:
    adjusted_price: float
    expected_fill: float
    queue_position: float
    walked_levels: int
    remaining: float
    price_used: float


class QueueDynamicsSimulator:
    """Simplified queue model that approximates standing size and fill probability."""

    def __init__(self, *, queue_penalty: float = 0.25) -> None:
        self.queue_penalty = max(0.0, min(queue_penalty, 1.0))
        self._resting_depth: Dict[str, Dict[float, float]] = {"bid": {}, "ask": {}}
        self._last_snapshot: Optional[OrderBookSnapshot] = None

    def update(self, snapshot: OrderBookSnapshot) -> None:
        """Register the latest book snapshot for queue estimates."""
        self._last_snapshot = snapshot
        self._resting_depth["bid"] = {price: size for price, size in snapshot.bids}
        self._resting_depth["ask"] = {price: size for price, size in snapshot.asks}

    def estimate_fill(
        self,
        side: OrderSide,
        limit_price: float,
        quantity: float,
        snapshot: OrderBookSnapshot,
        base_price: float,
    ) -> QueueEstimate:
        """Estimate effective fill price accounting for resting queue depth."""
        if quantity <= 0:
            raise ValueError("quantity must be positive.")

        levels: Sequence[Tuple[float, float]]
        depth_key: str
        price_cmp: callable

        if side == OrderSide.BUY:
            levels = snapshot.asks
            depth_key = "ask"
            price_cmp = lambda level_price: level_price <= limit_price
        else:
            levels = snapshot.bids
            depth_key = "bid"
            price_cmp = lambda level_price: level_price >= limit_price

        if not levels:
            return QueueEstimate(
                adjusted_price=base_price,
                expected_fill=0.0,
                queue_position=0.0,
                walked_levels=0,
                remaining=quantity,
                price_used=base_price,
            )

        remaining = quantity
        spent = 0.0
        total_taken = 0.0
        queue_position = 0.0
        walked_levels = 0
        price_used = base_price

        for price, size in levels:
            if not price_cmp(price):
                break
            walked_levels += 1
            standing = self._resting_depth[depth_key].get(price, size)
            queue_position = max(queue_position, max(0.0, standing - size))
            available = max(0.0, size - queue_position * self.queue_penalty)
            if available <= 0:
                continue
            take = min(remaining, available)
            spent += take * price
            total_taken += take
            remaining -= take
            price_used = price
            if remaining <= 1e-12:
                break

        if total_taken <= 0:
            adjusted = base_price
        else:
            adjusted = spent / total_taken

        return QueueEstimate(
            adjusted_price=float(adjusted),
            expected_fill=float(total_taken),
            queue_position=float(queue_position),
            walked_levels=walked_levels,
            remaining=float(max(0.0, remaining)),
            price_used=float(price_used),
        )

    def register_execution(self, side: OrderSide, price: float, quantity: float) -> None:
        """Update internal queue depth after an execution."""
        depth_key = "bid" if side == OrderSide.SELL else "ask"
        current = self._resting_depth.get(depth_key, {})
        prev = current.get(price, 0.0)
        current[price] = max(0.0, prev - quantity)
        self._resting_depth[depth_key] = current


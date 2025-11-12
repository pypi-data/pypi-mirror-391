from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from statistics import pstdev
from typing import Deque, Dict, Tuple

from qantify.backtest.types import OrderSide


@dataclass(slots=True)
class IcebergSignal:
    side: OrderSide
    price: float
    total_executed: float
    hits: int


class IcebergDetector:
    """Heuristic iceberg detector based on repeated prints at the same price."""

    def __init__(
        self,
        *,
        window: int = 12,
        min_hits: int = 4,
        size_threshold: float = 1.0,
        std_threshold: float = 0.05,
    ) -> None:
        self.window = max(2, window)
        self.min_hits = max(2, min_hits)
        self.size_threshold = max(0.0, size_threshold)
        self.std_threshold = max(0.0, std_threshold)
        self._fills: Dict[Tuple[OrderSide, float], Deque[float]] = defaultdict(lambda: deque(maxlen=self.window))

    def observe_fill(self, price: float, quantity: float, side: OrderSide) -> None:
        key = (side, round(price, 6))
        bucket = self._fills[key]
        bucket.append(max(0.0, quantity))

    def check_iceberg(self, price: float, side: OrderSide) -> IcebergSignal | None:
        key = (side, round(price, 6))
        bucket = self._fills.get(key)
        if not bucket or len(bucket) < self.min_hits:
            return None
        total = sum(bucket)
        if total < self.size_threshold:
            return None
        dispersion = pstdev(bucket) if len(bucket) > 1 else 0.0
        if dispersion <= self.std_threshold:
            return IcebergSignal(side=side, price=price, total_executed=total, hits=len(bucket))
        return None

    def reset(self) -> None:
        self._fills.clear()


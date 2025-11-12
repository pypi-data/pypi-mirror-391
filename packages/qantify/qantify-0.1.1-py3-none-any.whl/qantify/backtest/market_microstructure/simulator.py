from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from qantify.backtest.execution import OrderBookSnapshot
from qantify.backtest.market_microstructure.detection import IcebergDetector
from qantify.backtest.market_microstructure.queue import QueueDynamicsSimulator, QueueEstimate
from qantify.backtest.types import Order, OrderSide


class MarketMicrostructureSimulator:
    """Combines order book replay, queue dynamics, and iceberg detection for execution adjustments."""

    def __init__(
        self,
        *,
        queue_penalty: float = 0.25,
        detection_threshold: float = 1.0,
    ) -> None:
        self.queue = QueueDynamicsSimulator(queue_penalty=queue_penalty)
        self.iceberg = IcebergDetector(size_threshold=detection_threshold)
        self._last_snapshot: Optional[OrderBookSnapshot] = None

    def update_snapshot(self, snapshot: OrderBookSnapshot) -> None:
        self._last_snapshot = snapshot
        self.queue.update(snapshot)

    def simulate_order(
        self,
        order: Order,
        base_price: float,
        quantity: float,
        book: Optional[OrderBookSnapshot],
    ) -> Tuple[float, Dict[str, Any]]:
        snapshot = book or self._last_snapshot
        if snapshot is None:
            return base_price, {}

        estimate = self.queue.estimate_fill(
            order.side,
            order.price if order.price is not None else base_price,
            quantity,
            snapshot,
            base_price,
        )

        adjusted_price = estimate.adjusted_price if estimate.expected_fill > 0 else base_price
        meta: Dict[str, Any] = {
            "queue_position": estimate.queue_position,
            "expected_fill": estimate.expected_fill,
            "walked_levels": estimate.walked_levels,
            "remaining_after_sim": estimate.remaining,
        }

        if estimate.expected_fill > 0:
            self.queue.register_execution(order.side, estimate.price_used, estimate.expected_fill)
            self.iceberg.observe_fill(estimate.price_used, estimate.expected_fill, order.side)
            signal = self.iceberg.check_iceberg(estimate.price_used, order.side)
            if signal:
                meta["iceberg_detected"] = {
                    "total_executed": signal.total_executed,
                    "hits": signal.hits,
                    "price": signal.price,
                    "side": signal.side.value,
                }

        return adjusted_price, meta


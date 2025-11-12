"""Advanced order orchestration utilities for the backtest engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from uuid import uuid4

from .types import Order, OrderSide, OrderType, TimeInForce


@dataclass(slots=True)
class IcebergSpec:
    """State container for iceberg-style execution."""

    total_quantity: float
    display_quantity: float
    refill: bool = True
    min_display: float = 1e-6
    executed: float = 0.0

    def next_slice(self) -> float:
        remaining = self.total_quantity - self.executed
        if remaining <= self.min_display:
            return max(remaining, 0.0)
        return min(self.display_quantity, remaining)

    def record_fill(self, quantity: float) -> None:
        self.executed += quantity

    @property
    def done(self) -> bool:
        return self.executed >= self.total_quantity - self.min_display


@dataclass(slots=True)
class AlgoSchedule:
    """Algorithmic schedule metadata (TWAP, VWAP, POV)."""

    label: str
    parameters: Dict[str, float]
    generator: Callable[[Order, float], float]

    def target_quantity(self, order: Order, market_volume: float) -> float:
        return float(self.generator(order, market_volume))


@dataclass(slots=True)
class BracketOrder:
    """Container modelling parent + take-profit + stop-loss."""

    parent: Order
    take_profit: Optional[Order] = None
    stop_loss: Optional[Order] = None
    id: str = field(default_factory=lambda: f"bracket-{uuid4().hex}")


@dataclass(slots=True)
class OCOGroup:
    """One-cancels-other order grouping."""

    primary: Order
    secondary: Order
    id: str = field(default_factory=lambda: f"oco-{uuid4().hex}")


def create_bracket_order(
    *,
    base_order: Order,
    take_profit_price: Optional[float],
    stop_loss_price: Optional[float],
    quantity: Optional[float] = None,
    time_in_force: TimeInForce = TimeInForce.GTC,
) -> BracketOrder:
    """Generate linked orders to emulate broker bracket behaviour."""

    qty = quantity or base_order.quantity
    tp: Optional[Order] = None
    sl: Optional[Order] = None

    if take_profit_price is not None:
        tp = Order(
            timestamp=base_order.timestamp,
            symbol=base_order.symbol,
            side=OrderSide.SELL if base_order.side == OrderSide.BUY else OrderSide.BUY,
            quantity=qty,
            type=OrderType.LIMIT,
            price=take_profit_price,
            time_in_force=time_in_force,
        )
        tp.parent_id = base_order.id
    if stop_loss_price is not None:
        sl = Order(
            timestamp=base_order.timestamp,
            symbol=base_order.symbol,
            side=OrderSide.SELL if base_order.side == OrderSide.BUY else OrderSide.BUY,
            quantity=qty,
            type=OrderType.STOP,
            stop_price=stop_loss_price,
            time_in_force=time_in_force,
        )
        sl.parent_id = base_order.id

    child_ids: List[str] = []
    if tp is not None:
        child_ids.append(tp.id)
        tp.meta["compound_parent"] = base_order.id
    if sl is not None:
        child_ids.append(sl.id)
        sl.meta["compound_parent"] = base_order.id
    base_order.children = tuple(child_ids)
    base_order.meta["compound"] = "bracket"

    return BracketOrder(parent=base_order, take_profit=tp, stop_loss=sl)


def create_oco_group(order_a: Order, order_b: Order) -> OCOGroup:
    """Associate two orders so that one cancels the other when filled."""

    group = OCOGroup(primary=order_a, secondary=order_b)
    order_a.parent_id = group.id
    order_b.parent_id = group.id
    order_a.children = (order_b.id,)
    order_b.children = (order_a.id,)
    order_a.meta["oco_group"] = group.id
    order_b.meta["oco_group"] = group.id
    return group


def create_iceberg_order(
    base_order: Order,
    *,
    display_quantity: float,
    refill: bool = True,
    min_display: float = 1e-6,
) -> Tuple[Order, IcebergSpec]:
    """Convert an order into iceberg style with metadata."""

    spec = IcebergSpec(
        total_quantity=base_order.quantity,
        display_quantity=display_quantity,
        refill=refill,
        min_display=min_display,
    )
    base_order.display_quantity = float(display_quantity)
    base_order.meta.setdefault("iceberg", {"display_quantity": display_quantity, "refill": refill, "executed": 0.0})
    return base_order, spec


__all__ = [
    "IcebergSpec",
    "AlgoSchedule",
    "BracketOrder",
    "OCOGroup",
    "create_bracket_order",
    "create_oco_group",
    "create_iceberg_order",
]


"""Event-driven backtesting engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Tuple
from uuid import uuid4

import pandas as pd

from qantify.core.utils import validate_ohlcv_frame

from .compliance import ComplianceCheck, ComplianceContext, ComplianceEngine
from .costs import CommissionModel, NoCommission, NoSlippage, SlippageModel
from .errors import ConfigurationError, ExecutionError
from .orders import (
    AlgoSchedule,
    BracketOrder,
    IcebergSpec,
    OCOGroup,
    create_bracket_order,
    create_iceberg_order,
    create_oco_group,
)
from .portfolio import Portfolio
from .risk import RiskContext, RiskManager, RiskRule
from .types import (
    Fill,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    PortfolioSnapshot,
    TimeInForce,
    Trade,
)
from .execution import ExecutionEngine, OrderBookSnapshot

try:  # Optional to avoid circular import issues during initialization
    from qantify.strategy.base import Strategy as BaseStrategy
except Exception:  # pragma: no cover - optional dependency
    BaseStrategy = None


class StrategyProtocol(Protocol):
    """Minimal protocol expected from strategy implementations."""

    def on_start(self, context: "EventContext") -> None:  # pragma: no cover - protocol definition
        ...

    def on_bar(self, context: "EventContext") -> None:  # pragma: no cover - protocol definition
        ...

    def on_finish(self, context: "EventContext") -> None:  # pragma: no cover - protocol definition
        ...


@dataclass(slots=True)
class EventContext:
    data: pd.DataFrame
    timestamp: pd.Timestamp
    row: pd.Series
    index: int
    broker: "Broker"
    portfolio: Portfolio


@dataclass(slots=True)
class Broker:
    symbol: str
    commission_model: CommissionModel
    slippage_model: SlippageModel
    portfolio: Portfolio
    record_callback: Callable[[Order, Fill], None]
    cancel_callback: Optional[Callable[[Order], None]] = None
    risk_manager: Optional[RiskManager] = None
    execution_engine: Optional[ExecutionEngine] = None
    compliance_engine: Optional[ComplianceEngine] = None
    pending_orders: List[Order] = field(default_factory=list)
    orders: dict[str, Order] = field(default_factory=dict)
    trailing_meta: Dict[str, Dict[str, float]] = field(default_factory=dict)
    bracket_registry: Dict[str, BracketOrder] = field(default_factory=dict)
    bracket_waiting: Dict[str, BracketOrder] = field(default_factory=dict)
    oco_registry: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    iceberg_specs: Dict[str, IcebergSpec] = field(default_factory=dict)
    iceberg_parents: Dict[str, str] = field(default_factory=dict)
    algo_registry: Dict[str, AlgoSchedule] = field(default_factory=dict)

    _current_timestamp: Optional[pd.Timestamp] = None
    _current_price: Optional[float] = None
    _current_row: Optional[pd.Series] = None
    _current_snapshot: Optional[PortfolioSnapshot] = None
    _current_book: Optional[OrderBookSnapshot] = None

    def _risk_check(self, order: Order) -> bool:
        if self.risk_manager is None:
            return True
        if not self.risk_manager.approve(order):
            order.mark_cancelled()
            if order in self.pending_orders:
                self.pending_orders.remove(order)
            if self.cancel_callback is not None:
                self.cancel_callback(order)
            return False
        return True

    def _compliance_check(self, order: Order) -> bool:
        if self.compliance_engine is None:
            return True
        if self.compliance_engine.approve(order):
            return True
        order.mark_cancelled()
        if order in self.pending_orders:
            self.pending_orders.remove(order)
        if self.cancel_callback is not None:
            self.cancel_callback(order)
        return False

    def set_market_state(self, timestamp: pd.Timestamp, row: pd.Series) -> None:
        self._current_timestamp = timestamp
        self._current_row = row
        self._current_price = float(row.get("close", row.iloc[-1] if len(row) else 0.0))
        self._current_snapshot = self.portfolio.snapshot(timestamp.to_pydatetime(), {self.symbol: self._current_price})

        book = None
        if {"bid", "ask"}.issubset(row.index):
            bid_size = float(row.get("bid_size", row.get("bid_volume", row.get("bid_qty", 0.0)) or 0.0)) or 0.0
            ask_size = float(row.get("ask_size", row.get("ask_volume", row.get("ask_qty", 0.0)) or 0.0)) or 0.0
            if bid_size <= 0:
                bid_size = 1.0
            if ask_size <= 0:
                ask_size = 1.0
            book = OrderBookSnapshot(
                timestamp=timestamp.to_pydatetime(),
                bids=[(float(row["bid"]), bid_size)],
                asks=[(float(row["ask"]), ask_size)],
            )
        self._current_book = book

        if self.execution_engine and getattr(self.execution_engine, "microstructure", None) and book is not None:
            self.execution_engine.microstructure.update_snapshot(book)

        if self.risk_manager is not None:
            context = RiskContext(
                symbol=self.symbol,
                price=self._current_price,
                snapshot=self._current_snapshot,
                timestamp=timestamp,
            )
            self.risk_manager.update_context(context)

        if self.compliance_engine is not None and self._current_snapshot is not None:
            comp_context = ComplianceContext(
                symbol=self.symbol,
                price=self._current_price,
                snapshot=self._current_snapshot,
                timestamp=timestamp,
            )
            self.compliance_engine.update_context(comp_context)

        self._update_trailing_orders()
        self._process_pending_orders()

    def buy(self, quantity: float) -> Fill:
        return self._submit(OrderSide.BUY, quantity, order_type=OrderType.MARKET)

    def sell(self, quantity: float) -> Fill:
        return self._submit(OrderSide.SELL, quantity, order_type=OrderType.MARKET)

    def limit(
        self,
        side: OrderSide,
        price: float,
        quantity: float,
        *,
        time_in_force: TimeInForce = TimeInForce.GTC,
        fill_ratio: float = 1.0,
    ) -> Fill | Order:
        return self._submit(
            side,
            quantity,
            order_type=OrderType.LIMIT,
            price=price,
            time_in_force=time_in_force,
            fill_ratio=fill_ratio,
        )

    def stop(
        self,
        side: OrderSide,
        price: float,
        quantity: float,
        *,
        time_in_force: TimeInForce = TimeInForce.GTC,
        fill_ratio: float = 1.0,
    ) -> Fill | Order:
        return self._submit(
            side,
            quantity,
            order_type=OrderType.STOP,
            stop_price=price,
            time_in_force=time_in_force,
            fill_ratio=fill_ratio,
        )

    def stop_limit(
        self,
        side: OrderSide,
        stop_price: float,
        limit_price: float,
        quantity: float,
        *,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Fill | Order:
        return self._submit(
            side,
            quantity,
            order_type=OrderType.STOP_LIMIT,
            stop_price=stop_price,
            price=limit_price,
            time_in_force=time_in_force,
        )

    def trailing_stop(
        self,
        side: OrderSide,
        quantity: float,
        *,
        trail_amount: Optional[float] = None,
        trail_percent: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Fill | Order:
        if trail_amount is None and trail_percent is None:
            raise ExecutionError("Trailing stop requires trail_amount or trail_percent.")
        return self._submit(
            side,
            quantity,
            order_type=OrderType.TRAILING_STOP,
            time_in_force=time_in_force,
            trail_amount=trail_amount,
            trail_percent=trail_percent,
        )

    def bracket(
        self,
        side: OrderSide,
        quantity: float,
        *,
        entry_type: OrderType = OrderType.MARKET,
        entry_price: Optional[float] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Tuple[Fill | Order, Optional[Order], Optional[Order]]:
        if entry_type == OrderType.LIMIT and entry_price is None:
            raise ExecutionError("Bracket limit order requires entry_price.")
        if entry_type not in {OrderType.MARKET, OrderType.LIMIT}:
            raise ExecutionError("Bracket orders currently support market or limit entries.")

        entry_kwargs: Dict[str, Any] = {"order_type": entry_type, "time_in_force": time_in_force}
        if entry_type == OrderType.LIMIT:
            entry_kwargs["price"] = entry_price

        entry_result = self._submit(side, quantity, **entry_kwargs)
        entry_order = entry_result.order if isinstance(entry_result, Fill) else entry_result

        bracket = create_bracket_order(
            base_order=entry_order,
            take_profit_price=take_profit,
            stop_loss_price=stop_loss,
            quantity=quantity,
            time_in_force=time_in_force,
        )
        self.bracket_registry[entry_order.id] = bracket

        if isinstance(entry_result, Fill):
            self._activate_bracket(bracket)
        else:
            self.bracket_waiting[entry_order.id] = bracket

        return entry_result, bracket.take_profit, bracket.stop_loss

    def oco(
        self,
        *,
        primary_side: OrderSide,
        secondary_side: OrderSide,
        quantity: float,
        primary_type: OrderType = OrderType.LIMIT,
        secondary_type: OrderType = OrderType.STOP,
        primary_price: Optional[float] = None,
        secondary_price: Optional[float] = None,
        primary_stop: Optional[float] = None,
        secondary_stop: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> Tuple[Fill | Order, Fill | Order]:
        primary_kwargs: Dict[str, Any] = {"order_type": primary_type, "time_in_force": time_in_force}
        secondary_kwargs: Dict[str, Any] = {"order_type": secondary_type, "time_in_force": time_in_force}

        if primary_type == OrderType.LIMIT:
            if primary_price is None:
                raise ExecutionError("Primary limit order requires primary_price.")
            primary_kwargs["price"] = primary_price
        elif primary_type == OrderType.STOP:
            if primary_stop is None:
                raise ExecutionError("Primary stop order requires primary_stop.")
            primary_kwargs["stop_price"] = primary_stop

        if secondary_type == OrderType.LIMIT:
            if secondary_price is None:
                raise ExecutionError("Secondary limit order requires secondary_price.")
            secondary_kwargs["price"] = secondary_price
        elif secondary_type == OrderType.STOP:
            if secondary_stop is None:
                raise ExecutionError("Secondary stop order requires secondary_stop.")
            secondary_kwargs["stop_price"] = secondary_stop

        primary_result = self._submit(primary_side, quantity, **primary_kwargs)
        secondary_result = self._submit(secondary_side, quantity, **secondary_kwargs)

        primary_order = primary_result.order if isinstance(primary_result, Fill) else primary_result
        secondary_order = secondary_result.order if isinstance(secondary_result, Fill) else secondary_result

        group = create_oco_group(primary_order, secondary_order)
        self.oco_registry[group.id] = (primary_order.id, secondary_order.id)

        if isinstance(primary_result, Fill):
            self._handle_post_fill(primary_order, primary_result)
        if isinstance(secondary_result, Fill):
            self._handle_post_fill(secondary_order, secondary_result)

        return primary_result, secondary_result

    def iceberg(
        self,
        side: OrderSide,
        total_quantity: float,
        *,
        display_quantity: float,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
        refill: bool = True,
        min_display: float = 1e-6,
    ) -> Optional[Fill | Order]:
        if display_quantity <= 0:
            raise ExecutionError("Iceberg order requires positive display_quantity.")
        spec_id = f"iceberg-{uuid4().hex}"
        spec = IcebergSpec(
            total_quantity=total_quantity,
            display_quantity=display_quantity,
            refill=refill,
            min_display=min_display,
        )
        self.iceberg_specs[spec_id] = spec
        return self._submit_iceberg_slice(
            spec_id=spec_id,
            side=side,
            order_type=order_type,
            price=price,
            time_in_force=time_in_force,
        )

    def cancel_all(self) -> int:
        cancelled = 0
        for order in list(self.pending_orders):
            if self.cancel(order.id):
                cancelled += 1
        return cancelled

    def _submit(
        self,
        side: OrderSide,
        quantity: float,
        *,
        order_type: OrderType,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
        fill_ratio: float = 1.0,
        trail_amount: Optional[float] = None,
        trail_percent: Optional[float] = None,
    ) -> Fill | Order:
        if self._current_timestamp is None or self._current_price is None or self._current_row is None:
            raise ExecutionError("Market state not initialized before order submission.")
        if quantity <= 0:
            raise ExecutionError("Order quantity must be positive.")
        if fill_ratio <= 0 or fill_ratio > 1:
            raise ExecutionError("fill_ratio must be within (0, 1].")
        if order_type == OrderType.TRAILING_STOP and trail_amount is None and trail_percent is None:
            raise ExecutionError("Trailing stop requires trail parameters.")
        if order_type == OrderType.STOP_LIMIT and (price is None or stop_price is None):
            raise ExecutionError("Stop-limit order requires stop and limit prices.")
        if order_type == OrderType.STOP and stop_price is None:
            raise ExecutionError("Stop order requires stop_price.")
        if order_type == OrderType.LIMIT and price is None:
            raise ExecutionError("Limit order requires price.")
        if time_in_force == TimeInForce.FOK and fill_ratio < 0.999:
            raise ExecutionError("Fill-or-kill orders must request full quantity.")

        order = Order(
            timestamp=self._current_timestamp.to_pydatetime(),
            symbol=self.symbol,
            side=side,
            quantity=quantity,
            type=order_type,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )
        order.meta["fill_ratio"] = fill_ratio
        if trail_amount is not None:
            order.trail_amount = trail_amount
        if trail_percent is not None:
            order.trail_percent = trail_percent

        if not self._risk_check(order):
            return order
        if not self._compliance_check(order):
            return order
        self.orders[order.id] = order

        if order_type == OrderType.MARKET:
            return self._execute_fill(order, float(self._current_price))

        self.pending_orders.append(order)
        fill = self._evaluate_order(order)
        if fill is not None:
            return fill
        return order

    def cancel(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if order is None or order.status in {OrderStatus.CANCELLED, OrderStatus.FILLED}:
            return False

        if order in self.pending_orders:
            self.pending_orders.remove(order)
        order.mark_cancelled()
        if self.cancel_callback is not None:
            self.cancel_callback(order)
        return True

    def _process_pending_orders(self) -> None:
        if not self.pending_orders:
            return
        pending_snapshot = list(self.pending_orders)
        for order in pending_snapshot:
            fill = self._evaluate_order(order)
            if fill is not None and order in self.pending_orders:
                self.pending_orders.remove(order)

    def _evaluate_order(self, order: Order) -> Optional[Fill]:
        if self._current_row is None or self._current_timestamp is None:
            return None

        open_price = float(self._current_row.get("open", self._current_price))
        high = float(self._current_row.get("high", self._current_price))
        low = float(self._current_row.get("low", self._current_price))
        close = float(self._current_row.get("close", self._current_price))

        execution_price: Optional[float] = None

        if order.type == OrderType.LIMIT:
            if order.price is None:
                raise ExecutionError("Limit order must specify a price.")
            if order.side == OrderSide.BUY and low <= order.price:
                execution_price = min(order.price, open_price)
            elif order.side == OrderSide.SELL and high >= order.price:
                execution_price = max(order.price, open_price)
        elif order.type == OrderType.STOP:
            if order.stop_price is None:
                raise ExecutionError("Stop order must specify a stop price.")
            if order.side == OrderSide.BUY and high >= order.stop_price:
                execution_price = max(order.stop_price, open_price)
            elif order.side == OrderSide.SELL and low <= order.stop_price:
                execution_price = min(order.stop_price, open_price)
        elif order.type == OrderType.STOP_LIMIT:
            if order.stop_price is None or order.price is None:
                raise ExecutionError("Stop-limit order requires stop and limit prices.")
            if not order.meta.get("triggered", False):
                if order.side == OrderSide.BUY and high >= order.stop_price:
                    order.meta["triggered"] = True
                elif order.side == OrderSide.SELL and low <= order.stop_price:
                    order.meta["triggered"] = True
            if order.meta.get("triggered"):
                if order.side == OrderSide.BUY and low <= order.price:
                    execution_price = max(order.price, open_price)
                elif order.side == OrderSide.SELL and high >= order.price:
                    execution_price = min(order.price, open_price)
        elif order.type == OrderType.TRAILING_STOP:
            stop_price = order.stop_price
            if stop_price is None:
                return None
            if order.side == OrderSide.SELL and low <= stop_price:
                execution_price = min(stop_price, open_price)
            elif order.side == OrderSide.BUY and high >= stop_price:
                execution_price = max(stop_price, open_price)

        if execution_price is None:
            return None

        fill_ratio = order.meta.get("fill_ratio", 1.0)
        remaining = order.remaining
        fill_qty = min(remaining, order.quantity * fill_ratio)
        if fill_qty <= 0:
            return None

        if order in self.pending_orders:
            self.pending_orders.remove(order)

        fill = self._execute_fill(order, execution_price, quantity=fill_qty)

        if order.status not in {OrderStatus.FILLED, OrderStatus.CANCELLED} and order.time_in_force == TimeInForce.IOC:
            self.cancel(order.id)

        return fill

    def _update_trailing_orders(self) -> None:
        if not self.pending_orders:
            return
        if self._current_row is None or self._current_price is None:
            return
        high = float(self._current_row.get("high", self._current_price))
        low = float(self._current_row.get("low", self._current_price))

        for order in self.pending_orders:
            if order.type != OrderType.TRAILING_STOP:
                continue
            meta = self.trailing_meta.setdefault(order.id, {"benchmark": self._current_price})
            if order.side == OrderSide.SELL:
                meta["benchmark"] = max(meta.get("benchmark", high), high)
                reference = meta["benchmark"]
                if order.trail_amount is not None:
                    order.stop_price = reference - order.trail_amount
                elif order.trail_percent is not None:
                    order.stop_price = reference * (1 - order.trail_percent)
            else:
                meta["benchmark"] = min(meta.get("benchmark", low), low)
                reference = meta["benchmark"]
                if order.trail_amount is not None:
                    order.stop_price = reference + order.trail_amount
                elif order.trail_percent is not None:
                    order.stop_price = reference * (1 + order.trail_percent)

    def _execute_fill(self, order: Order, base_price: float, *, quantity: Optional[float] = None) -> Fill:
        fill_qty = quantity if quantity is not None else order.remaining or order.quantity
        if fill_qty <= 0:
            raise ExecutionError("Cannot execute fill with non-positive quantity.")

        book = None
        if self._current_book is not None:
            book = self._current_book
        elif self._current_row is not None and {"bid", "ask"}.issubset(self._current_row.index):
            bid_size = float(self._current_row.get("bid_size", self._current_row.get("bid_volume", self._current_row.get("bid_qty", fill_qty)) or fill_qty))
            ask_size = float(self._current_row.get("ask_size", self._current_row.get("ask_volume", self._current_row.get("ask_qty", fill_qty)) or fill_qty))
            book = OrderBookSnapshot(
                timestamp=self._current_timestamp.to_pydatetime(),
                bids=[(float(self._current_row["bid"]), bid_size or fill_qty)],
                asks=[(float(self._current_row["ask"]), ask_size or fill_qty)],
            )
            self._current_book = book
            if self.execution_engine and getattr(self.execution_engine, "microstructure", None):
                self.execution_engine.microstructure.update_snapshot(book)

        if self.execution_engine:
            fill = self.execution_engine.execute(
                order,
                base_price=base_price,
                book=book,
                timestamp=self._current_timestamp.to_pydatetime(),
            )
            fill_qty = fill.quantity
        else:
            slippage_model = self.slippage_model
            try:
                adjusted_price = slippage_model.apply(order, base_price, fill_qty, book)  # type: ignore[arg-type]
            except TypeError:
                adjusted_price = slippage_model.apply(order, base_price, fill_qty)
            fill = Fill(
                timestamp=self._current_timestamp.to_pydatetime(),
                symbol=self.symbol,
                side=order.side,
                price=adjusted_price,
                quantity=fill_qty,
                order=order,
            )

        commission = self.commission_model.compute(order, fill.price, fill.quantity)
        fill.commission = commission
        fill.slippage = fill.price - base_price

        self.portfolio.apply_fill(fill)
        order.mark_partial(fill_qty)
        if order.remaining <= 1e-9:
            order.mark_filled()
        elif order.time_in_force == TimeInForce.FOK:
            raise ExecutionError("Fill-or-kill order failed to fill completely.")

        self.record_callback(order, fill)
        if self.risk_manager is not None:
            self.risk_manager.on_fill(order)
        if self.compliance_engine is not None:
            self.compliance_engine.on_fill(order, fill)
        if order.status == OrderStatus.PARTIALLY_FILLED and order not in self.pending_orders:
            self.pending_orders.append(order)
        self._handle_post_fill(order, fill)
        return fill

    def _activate_bracket(self, bracket: BracketOrder) -> None:
        self.bracket_registry[bracket.parent.id] = bracket
        for child in (bracket.take_profit, bracket.stop_loss):
            if child is None:
                continue
            if not self._risk_check(child):
                continue
            self.orders[child.id] = child
            if child not in self.pending_orders:
                self.pending_orders.append(child)
        self._process_pending_orders()

    def _submit_iceberg_slice(
        self,
        *,
        spec_id: str,
        side: OrderSide,
        order_type: OrderType,
        price: Optional[float],
        time_in_force: TimeInForce,
    ) -> Optional[Fill | Order]:
        spec = self.iceberg_specs.get(spec_id)
        if spec is None:
            return None
        slice_quantity = spec.next_slice()
        if slice_quantity <= spec.min_display:
            if spec.done:
                self.iceberg_specs.pop(spec_id, None)
            return None

        submit_kwargs: Dict[str, Any] = {"order_type": order_type, "time_in_force": time_in_force}
        if order_type == OrderType.LIMIT:
            submit_kwargs["price"] = price
        elif order_type == OrderType.STOP:
            submit_kwargs["stop_price"] = price

        result = self._submit(side, slice_quantity, **submit_kwargs)
        order = result.order if isinstance(result, Fill) else result
        order.parent_id = spec_id
        iceberg_meta = order.meta.setdefault("iceberg", {})
        iceberg_meta.update(
            {
                "spec_id": spec_id,
                "total_quantity": spec.total_quantity,
                "display_quantity": spec.display_quantity,
                "refill": spec.refill,
                "base_type": order_type.value,
            }
        )
        if price is not None:
            iceberg_meta["base_price"] = price
        self.iceberg_parents[order.id] = spec_id

        return result

    def _handle_post_fill(self, order: Order, fill: Fill) -> None:
        # Activate bracket children when parent fills
        if order.id in self.bracket_waiting:
            bracket = self.bracket_waiting.pop(order.id)
            self._activate_bracket(bracket)

        parent_id = order.parent_id

        if parent_id and parent_id in self.bracket_registry:
            bracket = self.bracket_registry[parent_id]
            for sibling in (bracket.take_profit, bracket.stop_loss):
                if sibling is None or sibling.id == order.id:
                    continue
                self.cancel(sibling.id)
            siblings = [bracket.take_profit, bracket.stop_loss]
            if all(s is None or s.status in {OrderStatus.CANCELLED, OrderStatus.FILLED} for s in siblings):
                self.bracket_registry.pop(parent_id, None)

        if parent_id and parent_id in self.oco_registry:
            for sibling_id in self.oco_registry.pop(parent_id):
                if sibling_id != order.id:
                    self.cancel(sibling_id)

        if parent_id and parent_id in self.iceberg_specs:
            spec = self.iceberg_specs[parent_id]
            iceberg_meta = order.meta.setdefault("iceberg", {})
            iceberg_meta["executed"] = spec.executed
            base_type_value = iceberg_meta.get("base_type", OrderType.MARKET.value)
            try:
                base_type = OrderType(base_type_value)
            except ValueError:
                base_type = OrderType.MARKET
            base_price = iceberg_meta.get("base_price")

            self.iceberg_parents.pop(order.id, None)

            if spec.done or not spec.refill:
                self.iceberg_specs.pop(parent_id, None)
            else:
                self._submit_iceberg_slice(
                    spec_id=parent_id,
                    side=order.side,
                    order_type=base_type,
                    price=base_price,
                    time_in_force=order.time_in_force,
                )


@dataclass(slots=True)
class EventBacktestResult:
    equity_curve: pd.Series
    orders: List[Order]
    fills: List[Fill]
    snapshots: List[PortfolioSnapshot]
    trades: List[Trade] = field(default_factory=list)
    cancelled_orders: List[Order] = field(default_factory=list)
    risk_events: pd.DataFrame | None = None
    compliance_events: pd.DataFrame | None = None


@dataclass(slots=True)
class _OpenPosition:
    fill: Fill
    quantity: float
    total_quantity: float


class EventBacktester:
    def __init__(
        self,
        data: pd.DataFrame,
        *,
        symbol: str,
        strategy: StrategyProtocol,
        initial_cash: float = 100_000.0,
        commission_model: CommissionModel | None = None,
        slippage_model: SlippageModel | None = None,
        price_column: str = "close",
        execution_engine: Optional[ExecutionEngine] = None,
        risk_rules: Optional[Iterable[RiskRule]] = None,
        compliance_checks: Optional[Iterable[ComplianceCheck]] = None,
    ) -> None:
        validate_ohlcv_frame(data)
        if price_column not in data.columns:
            raise ConfigurationError(f"Price column '{price_column}' missing from data.")

        self.data = data
        self.symbol = symbol
        self.strategy = strategy
        self.price_column = price_column

        self.commission_model = commission_model or NoCommission()
        self.slippage_model = slippage_model or NoSlippage()

        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.orders: List[Order] = []
        self.fills: List[Fill] = []
        self.snapshots: List[PortfolioSnapshot] = []
        self.cancelled_orders: List[Order] = []
        self.trades: List[Trade] = []
        self._open_positions: Dict[tuple[str, OrderSide], List[_OpenPosition]] = {}
        self.risk_manager = RiskManager(list(risk_rules) if risk_rules else [])
        self.compliance_engine = ComplianceEngine(list(compliance_checks) if compliance_checks else [])
        if not compliance_checks:
            self.compliance_engine = None

        self.broker = Broker(
            symbol=symbol,
            commission_model=self.commission_model,
            slippage_model=self.slippage_model,
            portfolio=self.portfolio,
            record_callback=self._record_fill,
            cancel_callback=self._record_cancel,
            risk_manager=self.risk_manager if self.risk_manager.rules else None,
            execution_engine=execution_engine,
            compliance_engine=self.compliance_engine if self.compliance_engine and self.compliance_engine.checks else None,
        )

        if BaseStrategy is not None and isinstance(self.strategy, BaseStrategy):
            self.strategy._bind(
                data=self.data,
                symbol=self.symbol,
                broker=self.broker,
                portfolio=self.portfolio,
                price_column=self.price_column,
            )

    def _record_fill(self, order: Order, fill: Fill) -> None:
        self.orders.append(order)
        self.fills.append(fill)
        if hasattr(self.strategy, "on_fill"):
            self.strategy.on_fill(fill)
        self._update_trade_state(fill)

    def _record_cancel(self, order: Order) -> None:
        self.cancelled_orders.append(order)
        if hasattr(self.strategy, "on_cancel"):
            self.strategy.on_cancel(order)

    def run(self) -> EventBacktestResult:
        if self.data.empty:
            raise ConfigurationError("Cannot run event-driven backtest on empty dataset.")

        if self.risk_manager.rules:
            self.risk_manager.reset()
        if self.compliance_engine is not None:
            self.compliance_engine.reset()

        first_index = 0
        first_timestamp = self.data.index[first_index]
        first_row = self.data.iloc[first_index]

        self.broker.set_market_state(first_timestamp, first_row)

        context = EventContext(
            data=self.data,
            timestamp=first_timestamp,
            row=first_row,
            index=first_index,
            broker=self.broker,
            portfolio=self.portfolio,
        )

        if hasattr(self.strategy, "on_start"):
            self.strategy.on_start(context)

        for idx, (timestamp, row) in enumerate(self.data.iterrows()):
            self.broker.set_market_state(timestamp, row)

            context = EventContext(
                data=self.data,
                timestamp=timestamp,
                row=row,
                index=idx,
                broker=self.broker,
                portfolio=self.portfolio,
            )

            self.strategy.on_bar(context)

            price = float(row[self.price_column])
            snapshot = self.portfolio.snapshot(timestamp.to_pydatetime(), {self.symbol: price})
            self.snapshots.append(snapshot)

        if hasattr(self.strategy, "on_finish"):
            context = EventContext(
                data=self.data,
                timestamp=self.data.index[-1],
                row=self.data.iloc[-1],
                index=len(self.data) - 1,
                broker=self.broker,
                portfolio=self.portfolio,
            )
            self.strategy.on_finish(context)

        equity_curve = pd.Series(
            data=[snapshot.equity for snapshot in self.snapshots],
            index=self.data.index[: len(self.snapshots)],
            name="equity",
        )

        return EventBacktestResult(
            equity_curve=equity_curve,
            orders=self.orders,
            fills=self.fills,
            snapshots=self.snapshots,
            cancelled_orders=self.cancelled_orders,
            trades=self.trades,
            risk_events=self.risk_manager.summary() if self.risk_manager.rules else None,
             compliance_events=self.compliance_engine.summary() if self.compliance_engine is not None else None,
        )

    def _update_trade_state(self, fill: Fill) -> None:
        key_long = (fill.symbol, OrderSide.BUY)
        key_short = (fill.symbol, OrderSide.SELL)
        quantity_remaining = fill.quantity

        if fill.side == OrderSide.BUY:
            # Close short positions first
            quantity_remaining = self._close_positions(key_short, fill, quantity_remaining)
            if quantity_remaining > 1e-9:
                self._open_positions.setdefault(key_long, []).append(
                    _OpenPosition(fill=fill, quantity=quantity_remaining, total_quantity=quantity_remaining)
                )
        else:
            quantity_remaining = self._close_positions(key_long, fill, quantity_remaining)
            if quantity_remaining > 1e-9:
                self._open_positions.setdefault(key_short, []).append(
                    _OpenPosition(fill=fill, quantity=quantity_remaining, total_quantity=quantity_remaining)
                )

    def _close_positions(self, key: tuple[str, OrderSide], fill: Fill, quantity: float) -> float:
        if quantity <= 1e-9:
            return 0.0
        open_list = self._open_positions.get(key)
        if not open_list:
            return quantity

        while quantity > 1e-9 and open_list:
            open_position = open_list[0]
            qty = min(open_position.quantity, quantity)
            entry_fill = open_position.fill
            entry_ratio = qty / open_position.total_quantity if open_position.total_quantity > 0 else 1.0
            exit_ratio = qty / fill.quantity if fill.quantity > 0 else 1.0

            entry_commission = entry_fill.commission * entry_ratio
            exit_commission = fill.commission * exit_ratio

            entry_copy = Fill(
                timestamp=entry_fill.timestamp,
                symbol=entry_fill.symbol,
                side=entry_fill.side,
                price=entry_fill.price,
                quantity=qty,
                commission=entry_commission,
                slippage=entry_fill.slippage,
                order=entry_fill.order,
            )

            exit_copy = Fill(
                timestamp=fill.timestamp,
                symbol=fill.symbol,
                side=fill.side,
                price=fill.price,
                quantity=qty,
                commission=exit_commission,
                slippage=fill.slippage,
                order=fill.order,
            )

            if key[1] == OrderSide.BUY:
                gross = (exit_copy.price - entry_copy.price) * qty
                direction = OrderSide.BUY
            else:
                gross = (entry_copy.price - exit_copy.price) * qty
                direction = OrderSide.SELL

            pnl = gross - entry_commission - exit_commission
            notional = entry_copy.price * qty if entry_copy.price else 1.0
            return_pct = pnl / notional if notional else 0.0

            trade = Trade(
                entry=entry_copy,
                exit=exit_copy,
                quantity=qty,
                pnl=pnl,
                return_pct=return_pct,
                max_drawdown=0.0,
                direction=direction,
            )
            self.trades.append(trade)

            if qty >= open_position.quantity - 1e-9:
                open_list.pop(0)
            else:
                open_position.quantity -= qty

            quantity -= qty

        if not open_list:
            self._open_positions.pop(key, None)

        return quantity

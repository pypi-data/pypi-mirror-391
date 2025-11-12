"""Advanced order types and execution algorithms for sophisticated trading."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, Protocol
from datetime import datetime, timedelta
from enum import Enum
import uuid

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from qantify.backtest.types import OrderSide
from qantify.backtest.event import EventBacktestResult

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Advanced order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    BRACKET = "bracket"
    OCO = "oco"  # One-Cancels-Other
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    ICEBERG = "iceberg"
    SCALE = "scale"
    CONDITIONAL = "conditional"


class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"


class ExecutionAlgorithm(Enum):
    """Execution algorithms for order fulfillment."""

    IMMEDIATE = "immediate"  # Fill immediately at market
    MARKET_MAKER = "market_maker"  # Simulate market maker behavior
    PARTICIPATION = "participation"  # Volume participation
    POV = "pov"  # Percent of Volume
    IS = "is"  # Implementation Shortfall
    CUSTOM = "custom"


@dataclass(slots=True)
class AdvancedOrder:
    """Base class for advanced orders."""

    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    order_type: OrderType = OrderType.MARKET
    quantity: float = 0.0
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    execution_algorithm: ExecutionAlgorithm = ExecutionAlgorithm.IMMEDIATE

    # Common parameters
    time_in_force: str = "GTC"  # Good Till Cancelled
    expiry: Optional[datetime] = None

    # Execution tracking
    fills: List[Dict[str, Any]] = field(default_factory=list)
    average_fill_price: float = 0.0

    def __post_init__(self):
        self.remaining_quantity = self.quantity

    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status."""
        self.status = new_status

    def add_fill(self, price: float, quantity: float, timestamp: datetime) -> None:
        """Add a fill to the order."""
        fill = {
            'price': price,
            'quantity': quantity,
            'timestamp': timestamp,
            'value': price * quantity
        }
        self.fills.append(fill)
        self.filled_quantity += quantity
        self.remaining_quantity = max(0, self.remaining_quantity - quantity)

        # Update average fill price
        total_value = sum(f['value'] for f in self.fills)
        self.average_fill_price = total_value / self.filled_quantity if self.filled_quantity > 0 else 0

        # Update status
        if self.remaining_quantity == 0:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIAL

    def cancel(self) -> None:
        """Cancel the order."""
        if self.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            self.status = OrderStatus.CANCELLED

    def is_expired(self) -> bool:
        """Check if order is expired."""
        if self.expiry and datetime.now() > self.expiry:
            self.status = OrderStatus.EXPIRED
            return True
        return False


@dataclass(slots=True)
class BracketOrder(AdvancedOrder):
    """Bracket order with entry, stop loss, and profit target."""

    entry_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    profit_target_price: Optional[float] = None
    trailing_stop: bool = False
    trailing_percentage: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.BRACKET

    def update_trailing_stop(self, current_price: float) -> None:
        """Update trailing stop price."""
        if not self.trailing_stop or not self.stop_loss_price:
            return

        if self.side == OrderSide.BUY:
            # For long positions, trailing stop moves up with price
            new_stop = current_price * (1 - self.trailing_percentage)
            if new_stop > self.stop_loss_price:
                self.stop_loss_price = new_stop
        else:
            # For short positions, trailing stop moves down with price
            new_stop = current_price * (1 + self.trailing_percentage)
            if new_stop < self.stop_loss_price:
                self.stop_loss_price = new_stop


@dataclass(slots=True)
class OCOOrder(AdvancedOrder):
    """One-Cancels-Other order pair."""

    linked_order_id: Optional[str] = None
    oco_group_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.OCO


@dataclass(slots=True)
class TWAPOrder(AdvancedOrder):
    """Time-Weighted Average Price order."""

    duration_minutes: int = 60
    interval_seconds: int = 30
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.TWAP
        if not self.start_time:
            self.start_time = datetime.now()
        if not self.end_time:
            self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)


@dataclass(slots=True)
class VWAPOrder(AdvancedOrder):
    """Volume-Weighted Average Price order."""

    target_percentage: float = 0.1  # Percentage of daily volume
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    volume_profile: Optional[pd.Series] = None

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.VWAP


@dataclass(slots=True)
class IcebergOrder(AdvancedOrder):
    """Iceberg order that hides large quantity."""

    visible_quantity: float = 0.0
    peak_quantity: float = 0.0  # Maximum visible quantity per slice
    refresh_delay_seconds: int = 30

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.ICEBERG
        if not self.visible_quantity:
            self.visible_quantity = min(self.peak_quantity, self.remaining_quantity)


@dataclass(slots=True)
class ScaleOrder(AdvancedOrder):
    """Scale order for gradual position building/exiting."""

    scale_levels: List[Tuple[float, float]] = field(default_factory=list)  # (price, quantity) pairs
    current_level: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.SCALE


@dataclass(slots=True)
class ConditionalOrder(AdvancedOrder):
    """Conditional order with complex trigger conditions."""

    conditions: List[Dict[str, Any]] = field(default_factory=list)  # List of trigger conditions
    logical_operator: str = "AND"  # AND, OR, NOT

    def __post_init__(self):
        super().__post_init__()
        self.order_type = OrderType.CONDITIONAL

    def evaluate_conditions(self, market_data: Dict[str, Any]) -> bool:
        """Evaluate if all conditions are met."""
        results = []

        for condition in self.conditions:
            condition_type = condition.get('type')
            if condition_type == 'price_above':
                results.append(market_data.get('price', 0) > condition['value'])
            elif condition_type == 'price_below':
                results.append(market_data.get('price', 0) < condition['value'])
            elif condition_type == 'volume_above':
                results.append(market_data.get('volume', 0) > condition['value'])
            elif condition_type == 'indicator_above':
                indicator_value = market_data.get(condition.get('indicator', ''), 0)
                results.append(indicator_value > condition['value'])
            elif condition_type == 'time_after':
                current_time = datetime.now().time()
                condition_time = condition['value']
                results.append(current_time > condition_time)

        if self.logical_operator == "AND":
            return all(results)
        elif self.logical_operator == "OR":
            return any(results)
        elif self.logical_operator == "NOT":
            return not all(results)

        return False


class OrderExecutionEngine:
    """Advanced order execution engine with multiple algorithms."""

    def __init__(self, slippage_model: Optional[Callable] = None):
        self.slippage_model = slippage_model or self._default_slippage
        self.active_orders: Dict[str, AdvancedOrder] = {}
        self.completed_orders: Dict[str, AdvancedOrder] = {}

    def submit_order(self, order: AdvancedOrder) -> str:
        """Submit an order for execution."""
        self.active_orders[order.order_id] = order
        logger.info(f"Submitted {order.order_type.value} order {order.order_id} for {order.symbol}")
        return order.order_id

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an active order."""
        if order_id in self.active_orders:
            self.active_orders[order_id].cancel()
            logger.info(f"Cancelled order {order_id}")
            return True
        return False

    def process_market_data(self, symbol: str, data: pd.Series, timestamp: datetime) -> List[Dict[str, Any]]:
        """Process market data and execute orders."""
        fills = []

        # Get current price and volume
        current_price = data['close']
        current_volume = data.get('volume', 0)

        # Process active orders for this symbol
        orders_to_remove = []

        for order_id, order in self.active_orders.items():
            if order.symbol != symbol:
                continue

            # Check if order is expired
            if order.is_expired():
                orders_to_remove.append(order_id)
                continue

            # Execute based on order type
            order_fills = self._execute_order(order, current_price, current_volume, data, timestamp)
            fills.extend(order_fills)

            # Check if order is complete
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.EXPIRED]:
                orders_to_remove.append(order_id)

        # Move completed orders
        for order_id in orders_to_remove:
            if order_id in self.active_orders:
                order = self.active_orders.pop(order_id)
                self.completed_orders[order_id] = order

        return fills

    def _execute_order(
        self,
        order: AdvancedOrder,
        current_price: float,
        current_volume: float,
        market_data: pd.Series,
        timestamp: datetime
    ) -> List[Dict[str, Any]]:
        """Execute a specific order type."""
        fills = []

        if order.order_type == OrderType.MARKET:
            fills.extend(self._execute_market_order(order, current_price, timestamp))
        elif order.order_type == OrderType.LIMIT:
            fills.extend(self._execute_limit_order(order, current_price, timestamp))
        elif order.order_type == OrderType.STOP:
            fills.extend(self._execute_stop_order(order, current_price, timestamp))
        elif order.order_type == OrderType.BRACKET:
            fills.extend(self._execute_bracket_order(order, current_price, timestamp))
        elif order.order_type == OrderType.OCO:
            fills.extend(self._execute_oco_order(order, current_price, timestamp))
        elif order.order_type == OrderType.TWAP:
            fills.extend(self._execute_twap_order(order, current_price, current_volume, timestamp))
        elif order.order_type == OrderType.VWAP:
            fills.extend(self._execute_vwap_order(order, current_price, current_volume, market_data, timestamp))
        elif order.order_type == OrderType.ICEBERG:
            fills.extend(self._execute_iceberg_order(order, current_price, timestamp))
        elif order.order_type == OrderType.SCALE:
            fills.extend(self._execute_scale_order(order, current_price, timestamp))
        elif order.order_type == OrderType.CONDITIONAL:
            fills.extend(self._execute_conditional_order(order, market_data, timestamp))

        return fills

    def _execute_market_order(self, order: AdvancedOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute market order."""
        if order.status != OrderStatus.PENDING:
            return []

        # Apply slippage
        execution_price = self.slippage_model(price, order.quantity, order.side, "market")

        # Fill the order
        fill_quantity = order.remaining_quantity
        order.add_fill(execution_price, fill_quantity, timestamp)

        return [{
            'order_id': order.order_id,
            'symbol': order.symbol,
            'side': order.side.value,
            'price': execution_price,
            'quantity': fill_quantity,
            'timestamp': timestamp,
            'order_type': order.order_type.value
        }]

    def _execute_limit_order(self, order: AdvancedOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute limit order."""
        if not order.price or order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return []

        # Check if limit price is reached
        if (order.side == OrderSide.BUY and price <= order.price) or \
           (order.side == OrderSide.SELL and price >= order.price):

            execution_price = order.price  # Fill at limit price
            fill_quantity = order.remaining_quantity
            order.add_fill(execution_price, fill_quantity, timestamp)

            return [{
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side.value,
                'price': execution_price,
                'quantity': fill_quantity,
                'timestamp': timestamp,
                'order_type': order.order_type.value
            }]

        return []

    def _execute_stop_order(self, order: AdvancedOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute stop order."""
        if not order.price or order.status != OrderStatus.PENDING:
            return []

        # Check if stop price is triggered
        triggered = False
        if order.side == OrderSide.BUY and price >= order.price:
            triggered = True
        elif order.side == OrderSide.SELL and price <= order.price:
            triggered = True

        if triggered:
            # Convert to market order
            execution_price = self.slippage_model(price, order.remaining_quantity, order.side, "stop")
            fill_quantity = order.remaining_quantity
            order.add_fill(execution_price, fill_quantity, timestamp)

            return [{
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side.value,
                'price': execution_price,
                'quantity': fill_quantity,
                'timestamp': timestamp,
                'order_type': order.order_type.value
            }]

        return []

    def _execute_bracket_order(self, order: BracketOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute bracket order."""
        fills = []

        # Update trailing stop if applicable
        if order.trailing_stop:
            order.update_trailing_stop(price)

        # Check stop loss
        if order.stop_loss_price:
            stop_triggered = False
            if order.side == OrderSide.BUY and price <= order.stop_loss_price:
                stop_triggered = True
            elif order.side == OrderSide.SELL and price >= order.stop_loss_price:
                stop_triggered = True

            if stop_triggered and order.filled_quantity > 0:
                # Close position at stop loss
                execution_price = order.stop_loss_price
                order.add_fill(execution_price, -order.filled_quantity, timestamp)
                fills.append({
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'price': execution_price,
                    'quantity': -order.filled_quantity,
                    'timestamp': timestamp,
                    'order_type': 'bracket_stop'
                })

        # Check profit target
        if order.profit_target_price:
            target_triggered = False
            if order.side == OrderSide.BUY and price >= order.profit_target_price:
                target_triggered = True
            elif order.side == OrderSide.SELL and price <= order.profit_target_price:
                target_triggered = True

            if target_triggered and order.filled_quantity > 0:
                # Close position at profit target
                execution_price = order.profit_target_price
                order.add_fill(execution_price, -order.filled_quantity, timestamp)
                fills.append({
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'price': execution_price,
                    'quantity': -order.filled_quantity,
                    'timestamp': timestamp,
                    'order_type': 'bracket_target'
                })

        return fills

    def _execute_oco_order(self, order: OCOOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute OCO order."""
        # OCO logic would require coordination with linked orders
        # This is a simplified implementation
        fills = []

        # For now, treat as regular order
        if order.status == OrderStatus.PENDING:
            fills.extend(self._execute_market_order(order, price, timestamp))

        return fills

    def _execute_twap_order(self, order: TWAPOrder, price: float, volume: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute TWAP order."""
        fills = []

        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return fills

        # Check if within execution window
        if timestamp < order.start_time or timestamp > order.end_time:
            return fills

        # Calculate time-based execution
        total_duration = (order.end_time - order.start_time).total_seconds()
        elapsed = (timestamp - order.start_time).total_seconds()
        progress = elapsed / total_duration

        target_executed = order.quantity * progress
        remaining_to_execute = target_executed - order.filled_quantity

        if remaining_to_execute > 0.001:  # Minimum execution threshold
            execution_price = self.slippage_model(price, remaining_to_execute, order.side, "twap")
            order.add_fill(execution_price, remaining_to_execute, timestamp)

            fills.append({
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side.value,
                'price': execution_price,
                'quantity': remaining_to_execute,
                'timestamp': timestamp,
                'order_type': order.order_type.value
            })

        return fills

    def _execute_vwap_order(self, order: VWAPOrder, price: float, volume: float, market_data: pd.Series, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute VWAP order."""
        fills = []

        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return fills

        # Simplified VWAP execution - in practice would track volume profile
        if volume > 0:
            participation_rate = min(order.target_percentage, 0.05)  # Max 5% participation
            execution_quantity = volume * participation_rate

            if execution_quantity > 0 and order.remaining_quantity > 0:
                actual_quantity = min(execution_quantity, order.remaining_quantity)
                execution_price = self.slippage_model(price, actual_quantity, order.side, "vwap")

                order.add_fill(execution_price, actual_quantity, timestamp)

                fills.append({
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'price': execution_price,
                    'quantity': actual_quantity,
                    'timestamp': timestamp,
                    'order_type': order.order_type.value
                })

        return fills

    def _execute_iceberg_order(self, order: IcebergOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute iceberg order."""
        fills = []

        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return fills

        # Show only visible quantity
        if order.remaining_quantity > order.visible_quantity:
            visible_qty = order.visible_quantity
        else:
            visible_qty = order.remaining_quantity

        if visible_qty > 0:
            execution_price = self.slippage_model(price, visible_qty, order.side, "iceberg")
            order.add_fill(execution_price, visible_qty, timestamp)

            fills.append({
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side.value,
                'price': execution_price,
                'quantity': visible_qty,
                'timestamp': timestamp,
                'order_type': order.order_type.value
            })

            # Refresh visible quantity
            order.visible_quantity = min(order.peak_quantity, order.remaining_quantity)

        return fills

    def _execute_scale_order(self, order: ScaleOrder, price: float, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute scale order."""
        fills = []

        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL] or not order.scale_levels:
            return fills

        # Execute next scale level
        if order.current_level < len(order.scale_levels):
            level_price, level_quantity = order.scale_levels[order.current_level]

            # Check if price condition is met
            price_met = False
            if order.side == OrderSide.BUY and price <= level_price:
                price_met = True
            elif order.side == OrderSide.SELL and price >= level_price:
                price_met = True

            if price_met:
                execution_price = self.slippage_model(price, level_quantity, order.side, "scale")
                order.add_fill(execution_price, level_quantity, timestamp)
                order.current_level += 1

                fills.append({
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'price': execution_price,
                    'quantity': level_quantity,
                    'timestamp': timestamp,
                    'order_type': f'{order.order_type.value}_level_{order.current_level}'
                })

        return fills

    def _execute_conditional_order(self, order: ConditionalOrder, market_data: pd.Series, timestamp: datetime) -> List[Dict[str, Any]]:
        """Execute conditional order."""
        fills = []

        if order.status != OrderStatus.PENDING:
            return fills

        # Convert market data to dict for condition evaluation
        market_dict = {
            'price': market_data.get('close', 0),
            'volume': market_data.get('volume', 0),
            'high': market_data.get('high', 0),
            'low': market_data.get('low', 0),
            'open': market_data.get('open', 0),
        }

        # Evaluate conditions
        if order.evaluate_conditions(market_dict):
            # Execute as market order
            fills.extend(self._execute_market_order(order, market_dict['price'], timestamp))

        return fills

    def _default_slippage(self, price: float, quantity: float, side: OrderSide, order_type: str) -> float:
        """Default slippage model."""
        # Simple slippage based on order type and quantity
        base_slippage = 0.0001  # 0.01%

        if order_type in ['market', 'stop']:
            base_slippage *= 2  # Higher slippage for market orders
        elif order_type in ['twap', 'vwap']:
            base_slippage *= 0.5  # Lower slippage for algorithmic orders

        # Quantity impact
        quantity_impact = min(quantity / 1000000, 0.001)  # Max 0.1% for large orders

        slippage_factor = 1 + base_slippage + quantity_impact

        if side == OrderSide.BUY:
            return price * slippage_factor
        else:
            return price * (1 / slippage_factor)


class OrderAnalytics:
    """Analytics for order execution performance."""

    @staticmethod
    def analyze_order_performance(orders: List[AdvancedOrder]) -> Dict[str, Any]:
        """Analyze performance of executed orders."""

        if not orders:
            return {}

        completed_orders = [o for o in orders if o.status == OrderStatus.FILLED]

        if not completed_orders:
            return {}

        # Basic statistics
        total_orders = len(completed_orders)
        avg_fill_price = np.mean([o.average_fill_price for o in completed_orders])
        total_volume = sum(o.filled_quantity for o in completed_orders)

        # Slippage analysis
        slippage_by_type = {}
        for order in completed_orders:
            if order.fills:
                order_type = order.order_type.value
                if order_type not in slippage_by_type:
                    slippage_by_type[order_type] = []

                # Calculate slippage for each fill
                for fill in order.fills:
                    # This would require knowing the "fair" price
                    slippage_by_type[order_type].append(0)  # Placeholder

        # Execution time analysis
        execution_times = []
        for order in completed_orders:
            if order.fills:
                first_fill = min(f['timestamp'] for f in order.fills)
                last_fill = max(f['timestamp'] for f in order.fills)
                execution_times.append((last_fill - first_fill).total_seconds())

        return {
            'total_orders': total_orders,
            'avg_fill_price': avg_fill_price,
            'total_volume': total_volume,
            'avg_execution_time_seconds': np.mean(execution_times) if execution_times else 0,
            'order_type_breakdown': {ot: len([o for o in completed_orders if o.order_type.value == ot])
                                   for ot in set(o.order_type.value for o in completed_orders)}
        }


# Convenience functions
def create_bracket_order(
    symbol: str,
    side: OrderSide,
    quantity: float,
    entry_price: Optional[float] = None,
    stop_loss_price: Optional[float] = None,
    profit_target_price: Optional[float] = None,
    trailing_stop: bool = False,
    trailing_percentage: float = 0.05
) -> BracketOrder:
    """Create a bracket order."""
    return BracketOrder(
        symbol=symbol,
        side=side,
        quantity=quantity,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        profit_target_price=profit_target_price,
        trailing_stop=trailing_stop,
        trailing_percentage=trailing_percentage
    )


def create_twap_order(
    symbol: str,
    side: OrderSide,
    quantity: float,
    duration_minutes: int = 60,
    interval_seconds: int = 30
) -> TWAPOrder:
    """Create a TWAP order."""
    return TWAPOrder(
        symbol=symbol,
        side=side,
        quantity=quantity,
        duration_minutes=duration_minutes,
        interval_seconds=interval_seconds
    )


def create_iceberg_order(
    symbol: str,
    side: OrderSide,
    quantity: float,
    peak_quantity: float,
    refresh_delay_seconds: int = 30
) -> IcebergOrder:
    """Create an iceberg order."""
    return IcebergOrder(
        symbol=symbol,
        side=side,
        quantity=quantity,
        peak_quantity=peak_quantity,
        refresh_delay_seconds=refresh_delay_seconds
    )


__all__ = [
    "OrderType",
    "OrderStatus",
    "ExecutionAlgorithm",
    "AdvancedOrder",
    "BracketOrder",
    "OCOOrder",
    "TWAPOrder",
    "VWAPOrder",
    "IcebergOrder",
    "ScaleOrder",
    "ConditionalOrder",
    "OrderExecutionEngine",
    "OrderAnalytics",
    "create_bracket_order",
    "create_twap_order",
    "create_iceberg_order",
]

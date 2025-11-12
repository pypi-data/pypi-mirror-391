"""Advanced order management system for institutional-grade live trading."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Union

from qantify.live.adapters import RestExchangeAdapter, ExecutionReport


logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    """Comprehensive order status tracking."""
    PENDING = "pending"
    OPEN = "open"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class OrderPriority(Enum):
    """Order execution priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(slots=True)
class OrderExecutionMetrics:
    """Detailed order execution metrics."""
    order_id: str
    submitted_at: datetime
    first_fill_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    slippage_bps: float = 0.0
    market_impact_bps: float = 0.0
    execution_time_ms: float = 0.0
    fill_rate: float = 0.0
    total_filled_qty: float = 0.0
    remaining_qty: float = 0.0
    avg_fill_price: Optional[float] = None
    best_fill_price: Optional[float] = None
    worst_fill_price: Optional[float] = None
    fill_prices: List[float] = field(default_factory=list)
    fill_sizes: List[float] = field(default_factory=list)
    fill_timestamps: List[datetime] = field(default_factory=list)


@dataclass(slots=True)
class OrderInfo:
    """Enhanced order information with comprehensive tracking."""
    order: LiveOrder
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: float = 0.0
    remaining_qty: float = 0.0
    avg_fill_price: Optional[float] = None
    last_fill_price: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    priority: OrderPriority = OrderPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_metrics: OrderExecutionMetrics = None

    def __post_init__(self):
        if self.execution_metrics is None:
            self.execution_metrics = OrderExecutionMetrics(
                order_id=self.order.payload.get("order_id", f"order_{int(time.time())}"),
                submitted_at=self.created_at
            )
        self.remaining_qty = float(self.order.payload.get("quantity", 0.0))


@dataclass(slots=True)
class OrderQueue:
    """Priority-based order queue for execution management."""
    orders: Dict[OrderPriority, deque[str]] = field(default_factory=lambda: {
        priority: deque() for priority in OrderPriority
    })
    order_info: Dict[str, OrderInfo] = field(default_factory=dict)

    def add_order(self, order_id: str, priority: OrderPriority = OrderPriority.NORMAL) -> None:
        """Add order to execution queue."""
        self.orders[priority].append(order_id)

    def get_next_order(self) -> Optional[str]:
        """Get next order to execute based on priority."""
        for priority in reversed(OrderPriority):  # Highest priority first
            if self.orders[priority]:
                return self.orders[priority].popleft()
        return None

    def remove_order(self, order_id: str) -> None:
        """Remove order from queue."""
        for priority_queue in self.orders.values():
            try:
                priority_queue.remove(order_id)
            except ValueError:
                continue
        self.order_info.pop(order_id, None)

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "total_queued": sum(len(queue) for queue in self.orders.values()),
            "by_priority": {
                priority.name: len(queue) for priority, queue in self.orders.items()
            },
            "oldest_order": min(
                (info.created_at for info in self.order_info.values()),
                default=None
            )
        }


class LiveOrderManager:
    """Advanced order management system with institutional capabilities."""

    def __init__(
        self,
        adapter: RestExchangeAdapter,
        *,
        reconcile_interval: int = 30,
        max_concurrent_orders: int = 100,
        order_timeout: int = 300,  # 5 minutes
        enable_auto_cancel: bool = True,
        risk_check_interval: int = 10,
        performance_monitoring: bool = True
    ) -> None:
        self.adapter = adapter
        self.reconcile_interval = reconcile_interval
        self.max_concurrent_orders = max_concurrent_orders
        self.order_timeout = order_timeout
        self.enable_auto_cancel = enable_auto_cancel
        self.risk_check_interval = risk_check_interval
        self.performance_monitoring = performance_monitoring

        # Core data structures
        self.orders: Dict[str, OrderInfo] = {}
        self.order_queue = OrderQueue()
        self.active_orders: Set[str] = set()
        self.completed_orders: Dict[str, OrderInfo] = {}

        # Order relationships
        self.parent_child_orders: Dict[str, Set[str]] = defaultdict(set)  # parent -> children
        self.child_parent_orders: Dict[str, str] = {}  # child -> parent
        self.bracket_orders: Dict[str, Dict[str, str]] = defaultdict(dict)  # parent -> {'take_profit': id, 'stop_loss': id}
        self.oco_orders: Dict[str, str] = {}  # order_id -> paired_order_id

        # Execution tracking
        self.execution_history: deque[OrderExecutionMetrics] = deque(maxlen=10000)
        self.failed_orders: Dict[str, Dict[str, Any]] = {}

        # Performance metrics
        self.order_latency: deque[float] = deque(maxlen=1000)
        self.fill_rates: deque[float] = deque(maxlen=1000)
        self.slippage_history: deque[float] = deque(maxlen=1000)

        # Background tasks
        self._reconcile_task: Optional[asyncio.Task] = None
        self._timeout_task: Optional[asyncio.Task] = None
        self._risk_monitor_task: Optional[asyncio.Task] = None
        self._performance_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the order management system."""
        if self._running:
            return

        self._running = True
        logger.info("Starting advanced order management system")

        # Start background tasks
        self._reconcile_task = asyncio.create_task(self._reconcile_loop())
        self._timeout_task = asyncio.create_task(self._timeout_monitor_loop())
        self._risk_monitor_task = asyncio.create_task(self._risk_monitor_loop())

        if self.performance_monitoring:
            self._performance_task = asyncio.create_task(self._performance_monitor_loop())

    async def stop(self) -> None:
        """Stop the order management system."""
        self._running = False

        # Cancel all background tasks
        tasks = [self._reconcile_task, self._timeout_task,
                self._risk_monitor_task, self._performance_task]
        for task in tasks:
            if task:
                task.cancel()

        # Wait for completion
        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)

        # Cancel all active orders
        await self._cancel_all_active_orders()

        logger.info("Order management system stopped")

    def register_order(
        self,
        order_id: str,
        live_order: LiveOrder,
        status: OrderStatus = OrderStatus.PENDING,
        filled_qty: float = 0.0,
        priority: OrderPriority = OrderPriority.NORMAL
    ) -> None:
        """Register a new order with enhanced tracking."""
        order_info = OrderInfo(
            order=live_order,
            status=status,
            filled_qty=filled_qty,
            priority=priority
        )

        self.orders[order_id] = order_info

        # Add to appropriate queue
        if status in [OrderStatus.PENDING, OrderStatus.OPEN]:
            self.order_queue.add_order(order_id, priority)
            self.active_orders.add(order_id)
        else:
            self.completed_orders[order_id] = order_info

        # Track order relationships
        self._track_order_relationships(order_id, live_order)

        logger.info(f"Registered order {order_id} with status {status.value}")

    def _track_order_relationships(self, order_id: str, live_order: LiveOrder) -> None:
        """Track complex order relationships."""
        # Parent-child relationships
        if hasattr(live_order, 'parent_order_id') and live_order.parent_order_id:
            self.parent_child_orders[live_order.parent_order_id].add(order_id)
            self.child_parent_orders[order_id] = live_order.parent_order_id

        # Bracket order relationships
        if live_order.order_type == OrderType.BRACKET:
            # This would be set up when bracket orders are created
            pass

        # OCO relationships
        if hasattr(live_order, 'oco_linked_order') and live_order.oco_linked_order:
            self.oco_orders[order_id] = live_order.oco_linked_order

    def update_order_status(
        self,
        order_id: str,
        new_status: OrderStatus,
        filled_qty: Optional[float] = None,
        fill_price: Optional[float] = None,
        fill_timestamp: Optional[datetime] = None
    ) -> None:
        """Update order status with execution tracking."""
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found for status update")
            return

        order_info = self.orders[order_id]
        old_status = order_info.status

        # Update basic info
        order_info.status = new_status
        order_info.updated_at = datetime.utcnow()

        # Update fill information
        if filled_qty is not None:
            order_info.filled_qty = filled_qty
            order_info.remaining_qty = max(0, order_info.remaining_qty - filled_qty)

            # Update average fill price
            if fill_price is not None:
                if order_info.avg_fill_price is None:
                    order_info.avg_fill_price = fill_price
                else:
                    total_value = order_info.avg_fill_price * (order_info.filled_qty - filled_qty) + fill_price * filled_qty
                    order_info.avg_fill_price = total_value / order_info.filled_qty

                order_info.last_fill_price = fill_price

                # Track fill metrics
                order_info.execution_metrics.fill_prices.append(fill_price)
                order_info.execution_metrics.fill_sizes.append(filled_qty)
                if fill_timestamp:
                    order_info.execution_metrics.fill_timestamps.append(fill_timestamp)

                # Update execution metrics
                if not order_info.execution_metrics.first_fill_at:
                    order_info.execution_metrics.first_fill_at = fill_timestamp or datetime.utcnow()

        # Handle status transitions
        if new_status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
            # Move to completed orders
            self.active_orders.discard(order_id)
            self.completed_orders[order_id] = order_info
            self.order_queue.remove_order(order_id)

            # Finalize execution metrics
            order_info.execution_metrics.completed_at = datetime.utcnow()
            order_info.execution_metrics.total_filled_qty = order_info.filled_qty
            order_info.execution_metrics.remaining_qty = order_info.remaining_qty
            order_info.execution_metrics.fill_rate = order_info.filled_qty / float(order_info.order.payload.get("quantity", 1))

            if order_info.execution_metrics.fill_prices:
                order_info.execution_metrics.best_fill_price = min(order_info.execution_metrics.fill_prices)
                order_info.execution_metrics.worst_fill_price = max(order_info.execution_metrics.fill_prices)

            # Calculate execution time
            if order_info.execution_metrics.first_fill_at and order_info.execution_metrics.completed_at:
                execution_time = (order_info.execution_metrics.completed_at - order_info.execution_metrics.submitted_at).total_seconds() * 1000
                order_info.execution_metrics.execution_time_ms = execution_time
                self.order_latency.append(execution_time)

            # Move to execution history
            self.execution_history.append(order_info.execution_metrics)

            # Handle related orders
            self._handle_related_orders(order_id, new_status)

        elif new_status == OrderStatus.PARTIAL_FILL:
            # Update fill rate tracking
            total_qty = float(order_info.order.payload.get("quantity", 1))
            if total_qty > 0:
                fill_rate = order_info.filled_qty / total_qty
                self.fill_rates.append(fill_rate)

        logger.info(f"Order {order_id} status: {old_status.value} -> {new_status.value}")

    def _handle_related_orders(self, order_id: str, status: OrderStatus) -> None:
        """Handle related order management (OCO, bracket, etc.)."""
        # OCO order handling
        if order_id in self.oco_orders and status == OrderStatus.FILLED:
            paired_order = self.oco_orders[order_id]
            # Cancel the paired order
            asyncio.create_task(self._cancel_order_async(paired_order))

        # Bracket order handling
        for parent_id, bracket_orders in self.bracket_orders.items():
            if order_id in bracket_orders.values():
                # One leg of bracket filled, manage other legs
                if status == OrderStatus.FILLED:
                    # This is simplified - real bracket logic would be more complex
                    pass
                break

    async def _cancel_order_async(self, order_id: str) -> None:
        """Cancel an order asynchronously."""
        try:
            if order_id in self.orders:
                await self.adapter.cancel_order(order_id)
                self.update_order_status(order_id, OrderStatus.CANCELLED)
        except Exception as e:
            logger.error(f"Failed to cancel related order {order_id}: {e}")

    def remove_order(self, order_id: str) -> None:
        """Remove an order from tracking."""
        self.orders.pop(order_id, None)
        self.active_orders.discard(order_id)
        self.completed_orders.pop(order_id, None)
        self.order_queue.remove_order(order_id)

        # Clean up relationships
        self.parent_child_orders.pop(order_id, None)
        self.child_parent_orders.pop(order_id, None)
        self.oco_orders.pop(order_id, None)

        # Remove from bracket orders
        for bracket_set in self.bracket_orders.values():
            for key, oid in list(bracket_set.items()):
                if oid == order_id:
                    del bracket_set[key]

    async def reconcile_order(self, order_id: str) -> None:
        """Reconcile order status with broker."""
        try:
            if order_id not in self.orders:
                return

            response = await self.adapter.fetch_order(order_id)
            status_str = response.get("status", "").upper()
            filled_qty = float(response.get("filled", 0))

            # Map broker status to internal status
            status_mapping = {
                "NEW": OrderStatus.OPEN,
                "PARTIALLY_FILLED": OrderStatus.PARTIAL_FILL,
                "FILLED": OrderStatus.FILLED,
                "CANCELLED": OrderStatus.CANCELLED,
                "REJECTED": OrderStatus.REJECTED,
                "EXPIRED": OrderStatus.EXPIRED
            }

            status = status_mapping.get(status_str, OrderStatus.OPEN)
            self.update_order_status(order_id, status, filled_qty=filled_qty)

        except Exception as e:
            logger.error(f"Order reconciliation failed for {order_id}: {e}")

    async def _reconcile_loop(self) -> None:
        """Periodic order reconciliation."""
        while self._running:
            try:
                await asyncio.sleep(self.reconcile_interval)

                # Reconcile active orders
                active_order_ids = list(self.active_orders)
                for order_id in active_order_ids[:50]:  # Limit concurrent reconciliations
                    await self.reconcile_order(order_id)

            except Exception as e:
                logger.error(f"Reconciliation loop error: {e}")

    async def _timeout_monitor_loop(self) -> None:
        """Monitor for order timeouts."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                if not self.enable_auto_cancel:
                    continue

                cutoff_time = datetime.utcnow() - timedelta(seconds=self.order_timeout)
                timeout_orders = []

                for order_id, order_info in self.orders.items():
                    if (order_info.status in [OrderStatus.PENDING, OrderStatus.OPEN] and
                        order_info.created_at < cutoff_time):
                        timeout_orders.append(order_id)

                # Cancel timed out orders
                for order_id in timeout_orders:
                    try:
                        await self.adapter.cancel_order(order_id)
                        self.update_order_status(order_id, OrderStatus.EXPIRED)
                        logger.warning(f"Order {order_id} timed out and cancelled")
                    except Exception as e:
                        logger.error(f"Failed to cancel timed out order {order_id}: {e}")

            except Exception as e:
                logger.error(f"Timeout monitor error: {e}")

    async def _risk_monitor_loop(self) -> None:
        """Monitor orders for risk violations."""
        while self._running:
            try:
                await asyncio.sleep(self.risk_check_interval)

                # Check for risk violations
                # This would integrate with risk management system
                # For now, it's a placeholder
                pass

            except Exception as e:
                logger.error(f"Risk monitor error: {e}")

    async def _performance_monitor_loop(self) -> None:
        """Monitor order execution performance."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                if not self.performance_monitoring:
                    continue

                # Calculate performance metrics
                if self.order_latency:
                    avg_latency = sum(self.order_latency) / len(self.order_latency)
                    p95_latency = sorted(self.order_latency)[int(len(self.order_latency) * 0.95)]

                    logger.info(f"Order Performance - Avg Latency: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms")

                if self.fill_rates:
                    avg_fill_rate = sum(self.fill_rates) / len(self.fill_rates)
                    logger.info(f"Order Performance - Avg Fill Rate: {avg_fill_rate:.3f}")

                if self.slippage_history:
                    avg_slippage = sum(self.slippage_history) / len(self.slippage_history)
                    logger.info(f"Order Performance - Avg Slippage: {avg_slippage:.4f} bps")

            except Exception as e:
                logger.error(f"Performance monitor error: {e}")

    async def _cancel_all_active_orders(self) -> None:
        """Cancel all active orders during shutdown."""
        active_order_ids = list(self.active_orders)
        for order_id in active_order_ids:
            try:
                await self.adapter.cancel_order(order_id)
                self.update_order_status(order_id, OrderStatus.CANCELLED)
            except Exception as e:
                logger.error(f"Failed to cancel order {order_id} during shutdown: {e}")

    # Public interface methods
    def get_order_info(self, order_id: str) -> Optional[OrderInfo]:
        """Get detailed order information."""
        return self.orders.get(order_id)

    def get_active_orders(self) -> List[OrderInfo]:
        """Get all active orders."""
        return [info for oid, info in self.orders.items() if oid in self.active_orders]

    def get_completed_orders(self, limit: int = 100) -> List[OrderInfo]:
        """Get recently completed orders."""
        return list(self.completed_orders.values())[-limit:]

    def get_order_execution_metrics(self, order_id: str) -> Optional[OrderExecutionMetrics]:
        """Get execution metrics for an order."""
        order_info = self.orders.get(order_id)
        return order_info.execution_metrics if order_info else None

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get order queue statistics."""
        return self.order_queue.get_queue_stats()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        total_orders = len(self.orders)
        completed_orders = len(self.completed_orders)
        active_orders = len(self.active_orders)

        fill_rate = sum(self.fill_rates) / len(self.fill_rates) if self.fill_rates else 0
        avg_latency = sum(self.order_latency) / len(self.order_latency) if self.order_latency else 0
        avg_slippage = sum(self.slippage_history) / len(self.slippage_history) if self.slippage_history else 0

        return {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "completion_rate": completed_orders / total_orders if total_orders > 0 else 0,
            "avg_fill_rate": fill_rate,
            "avg_execution_latency_ms": avg_latency,
            "avg_slippage_bps": avg_slippage,
            "queue_stats": self.get_queue_stats(),
            "recent_failures": len(self.failed_orders)
        }

    def get_orders_by_symbol(self, symbol: str) -> List[OrderInfo]:
        """Get all orders for a specific symbol."""
        return [
            info for info in self.orders.values()
            if info.order.payload.get("symbol", "").upper() == symbol.upper()
        ]

    def get_orders_by_status(self, status: OrderStatus) -> List[OrderInfo]:
        """Get orders by status."""
        return [info for info in self.orders.values() if info.status == status]

    def get_orders_by_type(self, order_type: OrderType) -> List[OrderInfo]:
        """Get orders by type."""
        return [info for info in self.orders.values() if info.order.order_type == order_type]

    def get_related_orders(self, order_id: str) -> Dict[str, List[str]]:
        """Get related orders (parent/child, bracket, OCO)."""
        related = {
            "parent": [],
            "children": [],
            "bracket": [],
            "oco": []
        }

        # Parent relationship
        if order_id in self.child_parent_orders:
            related["parent"].append(self.child_parent_orders[order_id])

        # Child relationships
        if order_id in self.parent_child_orders:
            related["children"] = list(self.parent_child_orders[order_id])

        # Bracket relationships
        for parent_id, bracket_orders in self.bracket_orders.items():
            if order_id == parent_id or order_id in bracket_orders.values():
                related["bracket"] = list(bracket_orders.values())

        # OCO relationships
        if order_id in self.oco_orders:
            related["oco"].append(self.oco_orders[order_id])

        return related

    def add_order_tag(self, order_id: str, tag: str) -> None:
        """Add a tag to an order."""
        if order_id in self.orders:
            self.orders[order_id].tags.add(tag)

    def remove_order_tag(self, order_id: str, tag: str) -> None:
        """Remove a tag from an order."""
        if order_id in self.orders:
            self.orders[order_id].tags.discard(tag)

    def get_orders_by_tag(self, tag: str) -> List[OrderInfo]:
        """Get orders by tag."""
        return [info for info in self.orders.values() if tag in info.tags]

    def set_order_metadata(self, order_id: str, key: str, value: Any) -> None:
        """Set metadata for an order."""
        if order_id in self.orders:
            self.orders[order_id].metadata[key] = value

    def get_order_metadata(self, order_id: str, key: str) -> Any:
        """Get metadata from an order."""
        if order_id in self.orders:
            return self.orders[order_id].metadata.get(key)
        return None

    # Advanced order management
    async def bulk_cancel_orders(self, order_ids: List[str]) -> Dict[str, bool]:
        """Cancel multiple orders."""
        results = {}
        for order_id in order_ids:
            try:
                await self.adapter.cancel_order(order_id)
                self.update_order_status(order_id, OrderStatus.CANCELLED)
                results[order_id] = True
            except Exception as e:
                logger.error(f"Failed to cancel order {order_id}: {e}")
                results[order_id] = False
        return results

    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order."""
        try:
            # This depends on broker API capabilities
            # Implementation would vary by broker
            response = await self.adapter._request_context(
                "patch",
                f"{self.adapter.base_url}/orders/{order_id}",
                json=modifications
            )
            # Update local tracking
            return True
        except Exception as e:
            logger.error(f"Order modification failed for {order_id}: {e}")
            return False

    def get_order_book_impact(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Estimate order book impact (placeholder for advanced analysis)."""
        # This would integrate with market data to estimate slippage
        return {
            "estimated_slippage_bps": 5.0,  # Placeholder
            "market_depth_analysis": "insufficient_depth",  # Placeholder
            "recommended_split_orders": 3  # Placeholder
        }

    async def retry_failed_order(self, order_id: str) -> bool:
        """Retry a failed order."""
        if order_id not in self.failed_orders:
            return False

        order_info = self.orders.get(order_id)
        if not order_info or order_info.retry_count >= order_info.max_retries:
            return False

        try:
            # Resubmit the order
            report = await self.adapter.submit_order(order_info.order.payload)
            order_info.retry_count += 1

            # Update with new order ID
            new_order_id = report.order_id
            self.orders[new_order_id] = order_info
            self.register_order(new_order_id, order_info.order, OrderStatus.OPEN)

            # Remove old failed order
            self.failed_orders.pop(order_id, None)

            return True

        except Exception as e:
            logger.error(f"Order retry failed for {order_id}: {e}")
            order_info.retry_count += 1
            return False

    def export_order_history(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Export order history for analysis."""
        history = []
        for order_info in self.completed_orders.values():
            if start_date <= order_info.created_at <= end_date:
                history.append({
                    "order_id": list(self.completed_orders.keys())[list(self.completed_orders.values()).index(order_info)],
                    "symbol": order_info.order.payload.get("symbol"),
                    "side": order_info.order.payload.get("side"),
                    "quantity": order_info.order.payload.get("quantity"),
                    "filled_qty": order_info.filled_qty,
                    "avg_fill_price": order_info.avg_fill_price,
                    "status": order_info.status.value,
                    "created_at": order_info.created_at.isoformat(),
                    "execution_metrics": {
                        "execution_time_ms": order_info.execution_metrics.execution_time_ms,
                        "fill_rate": order_info.execution_metrics.fill_rate,
                        "slippage_bps": order_info.execution_metrics.slippage_bps
                    }
                })
        return history


__all__ = [
    "OrderStatus",
    "OrderPriority",
    "OrderExecutionMetrics",
    "OrderInfo",
    "OrderQueue",
    "LiveOrderManager"
]

"""Advanced live trading engine with institutional-grade capabilities."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics

from qantify.backtest.portfolio import Portfolio
from qantify.backtest.types import OrderSide
from qantify.data.streaming import EventQueue, StreamEvent
from qantify.live.adapters import ExecutionReport, RestExchangeAdapter
from qantify.strategy import Strategy
from qantify.live.risk import RiskConfig, RiskGuardrails
from qantify.live.order_manager import LiveOrderManager
from qantify.live.adapters import WebsocketExchangeAdapter
# from qantify.math.timeseries import exponential_moving_average, bollinger_bands  # Not available
# from qantify.signals.indicators import rsi, macd, bollinger_bands_signals  # Not available


logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Advanced order types for institutional trading."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    BRACKET = "bracket"
    OCO = "oco"  # One-Cancels-Other
    ICEBERG = "iceberg"
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    PEGGED = "pegged"


class ExecutionAlgorithm(Enum):
    """Execution algorithms for optimal order placement."""
    IMMEDIATE = "immediate"
    PARTICIPATE = "participate"
    PROVIDE = "provide"
    ADAPTIVE = "adaptive"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"


class MarketRegime(Enum):
    """Market regime detection for dynamic execution."""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass(slots=True)
class ExecutionMetrics:
    """Real-time execution performance metrics."""
    slippage_bps: float = 0.0
    market_impact_bps: float = 0.0
    execution_time_ms: float = 0.0
    fill_rate: float = 0.0
    adverse_selection_cost: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class OrderSlice:
    """Iceberg order slice for large orders."""
    quantity: float
    price: Optional[float] = None
    executed: bool = False
    execution_time: Optional[datetime] = None


@dataclass(slots=True)
class LiveOrder:
    """Enhanced live order with advanced features."""
    payload: Dict[str, Any]
    strategy_symbol: str
    order_type: OrderType = OrderType.MARKET
    execution_algo: ExecutionAlgorithm = ExecutionAlgorithm.IMMEDIATE
    slices: List[OrderSlice] = field(default_factory=list)
    parent_order_id: Optional[str] = None
    child_orders: List[str] = field(default_factory=list)
    time_in_force: str = "GTC"  # Good Till Cancelled
    iceberg_quantity: Optional[float] = None
    trailing_stop_distance: Optional[float] = None
    trailing_stop_trigger: Optional[float] = None
    bracket_take_profit: Optional[float] = None
    bracket_stop_loss: Optional[float] = None
    oco_linked_order: Optional[str] = None
    twap_duration: Optional[int] = None  # seconds
    vwap_start_time: Optional[datetime] = None
    peg_offset: Optional[float] = None
    adaptive_params: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metrics: List[ExecutionMetrics] = field(default_factory=list)


class LiveEngine:
    """Advanced live trading engine with institutional capabilities."""

    def __init__(
        self,
        strategy: Strategy,
        adapter: RestExchangeAdapter,
        *,
        portfolio: Portfolio,
        event_queue: Optional[EventQueue] = None,
        risk_config: Optional[RiskConfig] = None,
        execution_ws: Optional[WebsocketExchangeAdapter] = None,
        market_data_ws: Optional[WebsocketExchangeAdapter] = None,
        enable_market_regime_detection: bool = True,
        enable_adaptive_execution: bool = True,
        max_concurrent_orders: int = 50,
        order_queue_size: int = 1000,
        performance_monitoring: bool = True,
    ) -> None:
        # Core components
        self.strategy = strategy
        self.adapter = adapter
        self.portfolio = portfolio
        self.event_queue = event_queue or EventQueue()
        self.guardrails = RiskGuardrails(risk_config or RiskConfig())

        # WebSocket connections
        self.execution_ws = execution_ws
        self.market_data_ws = market_data_ws

        # Order management
        self.order_manager = LiveOrderManager(adapter)
        self._open_orders: Dict[str, LiveOrder] = {}
        self._order_queue: asyncio.Queue[LiveOrder] = asyncio.Queue(maxsize=order_queue_size)
        self._pending_orders: Dict[str, LiveOrder] = {}
        self.max_concurrent_orders = max_concurrent_orders

        # Execution state
        self._running = False
        self._shutdown = False
        self.execution_tasks: List[asyncio.Task] = []

        # Market regime detection
        self.enable_market_regime_detection = enable_market_regime_detection
        self.market_regime = MarketRegime.SIDEWAYS
        self.regime_history: deque[Tuple[datetime, MarketRegime]] = deque(maxlen=1000)
        self.price_history: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=100))
        self.volume_history: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=100))

        # Adaptive execution
        self.enable_adaptive_execution = enable_adaptive_execution
        self.execution_performance: Dict[str, List[ExecutionMetrics]] = defaultdict(list)
        self.symbol_volatility: Dict[str, float] = {}
        self.symbol_spread: Dict[str, float] = {}

        # Performance monitoring
        self.performance_monitoring = performance_monitoring
        self.execution_times: deque[float] = deque(maxlen=1000)
        self.slippage_history: deque[float] = deque(maxlen=1000)
        self.fill_rates: deque[float] = deque(maxlen=1000)

        # Advanced order tracking
        self.trailing_stops: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.bracket_orders: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.oco_orders: Dict[str, str] = {}
        self.iceberg_slices: Dict[str, List[OrderSlice]] = defaultdict(list)
        self.twap_orders: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.vwap_orders: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Background tasks
        self._market_regime_task: Optional[asyncio.Task] = None
        self._execution_processor_task: Optional[asyncio.Task] = None
        self._performance_monitor_task: Optional[asyncio.Task] = None
        self._risk_monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the live trading engine with all background services."""
        logger.info("Starting live trading engine...")

        # Start core services
        await self.event_queue.start()
        await self.order_manager.start()

        # Start WebSocket connections
        if self.execution_ws:
            await self.execution_ws.__aenter__()
        if self.market_data_ws:
            await self.market_data_ws.__aenter__()

        # Start background tasks
        self._running = True
        self._shutdown = False

        # Execution feed listener
        if self.execution_ws:
            asyncio.create_task(self._listen_execution_feed())

        # Market data listener
        if self.market_data_ws:
            asyncio.create_task(self._listen_market_data_feed())

        # Background services
        self._execution_processor_task = asyncio.create_task(self._process_order_queue())
        self._performance_monitor_task = asyncio.create_task(self._monitor_performance())
        self._risk_monitor_task = asyncio.create_task(self._monitor_risk())

        if self.enable_market_regime_detection:
            self._market_regime_task = asyncio.create_task(self._detect_market_regime())

        logger.info("Live trading engine started successfully")

    async def stop(self) -> None:
        """Gracefully stop the live trading engine."""
        logger.info("Stopping live trading engine...")

        self._shutdown = True
        self._running = False

        # Cancel all background tasks
        tasks_to_cancel = [
            self._execution_processor_task,
            self._performance_monitor_task,
            self._risk_monitor_task,
            self._market_regime_task,
        ]

        for task in tasks_to_cancel:
            if task:
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*[t for t in tasks_to_cancel if t], return_exceptions=True)

        # Cancel all active orders
        await self._cancel_all_orders()

        # Stop services
        await self.event_queue.stop()
        await self.order_manager.stop()

        # Close WebSocket connections
        if self.execution_ws:
            await self.execution_ws.__aexit__(None, None, None)
        if self.market_data_ws:
            await self.market_data_ws.__aexit__(None, None, None)

        logger.info("Live trading engine stopped")

    async def submit_order(self, order: LiveOrder) -> Union[ExecutionReport, List[ExecutionReport]]:
        """Submit advanced order with execution algorithms."""
        start_time = time.time()

        try:
            # Extract order parameters
            symbol = order.payload.get("symbol", order.strategy_symbol)
            side = OrderSide.BUY if order.payload.get("side", "BUY").upper() == "BUY" else OrderSide.SELL
            quantity = float(order.payload.get("quantity", 0.0))
            price = order.payload.get("price")

            # Risk check
            if not await self._check_order_risk(order, symbol, side, quantity, price):
                raise RuntimeError("Risk guardrails rejected order submission.")

            # Check concurrent order limits
            if len(self._open_orders) >= self.max_concurrent_orders:
                await self._order_queue.put(order)
                logger.info(f"Order queued due to concurrent limit: {len(self._open_orders)}/{self.max_concurrent_orders}")
                return ExecutionReport(
                    order_id=f"queued_{order.created_at.timestamp()}",
                    status="QUEUED",
                    filled_qty=0.0,
                    price=0.0,
                    raw={"message": "Order queued for processing"}
                )

            # Process based on order type
            if order.order_type == OrderType.ICEBERG:
                reports = await self._submit_iceberg_order(order)
            elif order.order_type == OrderType.BRACKET:
                reports = await self._submit_bracket_order(order)
            elif order.order_type == OrderType.OCO:
                reports = await self._submit_oco_order(order)
            elif order.order_type == OrderType.TWAP:
                reports = await self._submit_twap_order(order)
            elif order.order_type == OrderType.VWAP:
                reports = await self._submit_vwap_order(order)
            elif order.order_type == OrderType.TRAILING_STOP:
                reports = await self._submit_trailing_stop_order(order)
            else:
                # Standard order with execution algorithm
                reports = [await self._execute_with_algorithm(order)]

            # Track execution metrics
            execution_time = (time.time() - start_time) * 1000
            self.execution_times.append(execution_time)

            # Register orders
            if isinstance(reports, list):
                for report in reports:
                    if report.order_id not in self._open_orders:
                        self._open_orders[report.order_id] = order
                        self.order_manager.register(report.order_id, order, status=report.status, filled_qty=report.filled_qty)

                        # Track order relationships
                        if hasattr(order, 'parent_order_id') and order.parent_order_id:
                            if order.parent_order_id not in self._open_orders:
                                continue
                            parent_order = self._open_orders[order.parent_order_id]
                            parent_order.child_orders.append(report.order_id)
            else:
                self._open_orders[reports.order_id] = order
                self.order_manager.register(reports.order_id, order, status=reports.status, filled_qty=reports.filled_qty)

            # Update monitoring
            self.strategy.monitor.log_event("order_submitted", tags={
                "symbol": symbol,
                "side": side.value,
                "order_type": order.order_type.value,
                "execution_algo": order.execution_algo.value
            })
            self.strategy.monitor.record_metric("live_open_orders", len(self._open_orders))

            return reports

        except Exception as e:
            logger.error(f"Order submission failed: {e}")
            raise

    async def _check_order_risk(self, order: LiveOrder, symbol: str, side: OrderSide,
                               quantity: float, price: Optional[float]) -> bool:
        """Enhanced risk checking with market conditions."""
        timestamp = datetime.utcnow()

        # Basic risk guardrails
        if not self.guardrails.check_order(
            self.portfolio,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price or 0.0,
            timestamp=timestamp,
        ):
            return False

        # Market regime based risk adjustment
        if self.market_regime == MarketRegime.HIGH_VOLATILITY:
            # Increase risk limits during high volatility
            volatility_multiplier = 1.5
        elif self.market_regime == MarketRegime.LOW_VOLATILITY:
            # Tighten limits during low volatility
            volatility_multiplier = 0.8
        else:
            volatility_multiplier = 1.0

        # Symbol-specific risk adjustment
        symbol_volatility = self.symbol_volatility.get(symbol, 0.02)  # Default 2%
        if symbol_volatility > 0.05:  # High volatility symbol
            volatility_multiplier *= 1.2

        # Apply volatility adjustment to position limits
        if hasattr(self.guardrails.config, 'max_position_size') and self.guardrails.config.max_position_size:
            adjusted_limit = self.guardrails.config.max_position_size * volatility_multiplier
            position = self.portfolio.state.positions.get(symbol)
            current_qty = position.quantity if position else 0.0
            projected = current_qty + quantity if side == OrderSide.BUY else current_qty - quantity

            if abs(projected) > adjusted_limit:
                logger.warning(f"Volatility-adjusted position limit exceeded: {abs(projected)} > {adjusted_limit}")
                return False

        return True

    async def _execute_with_algorithm(self, order: LiveOrder) -> ExecutionReport:
        """Execute order using specified algorithm."""
        symbol = order.payload.get("symbol", order.strategy_symbol)
        side = order.payload.get("side", "BUY").upper()
        quantity = float(order.payload.get("quantity", 0.0))

        # Get current market data for algorithm decisions
        market_data = await self._get_market_data(symbol)

        if order.execution_algo == ExecutionAlgorithm.IMMEDIATE:
            return await self.adapter.submit_order(order.payload)

        elif order.execution_algo == ExecutionAlgorithm.PARTICIPATE:
            # Participate in current market volume
            return await self._execute_participate(order, market_data)

        elif order.execution_algo == ExecutionAlgorithm.PROVIDE:
            # Provide liquidity
            return await self._execute_provide(order, market_data)

        elif order.execution_algo == ExecutionAlgorithm.ADAPTIVE:
            # Adaptive based on market conditions
            return await self._execute_adaptive(order, market_data)

        elif order.execution_algo == ExecutionAlgorithm.STEALTH:
            # Stealth execution to minimize market impact
            return await self._execute_stealth(order, market_data)

        elif order.execution_algo == ExecutionAlgorithm.AGGRESSIVE:
            # Aggressive execution for fast fills
            return await self._execute_aggressive(order, market_data)

        else:
            # Default to immediate
            return await self.adapter.submit_order(order.payload)

    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for execution decisions."""
        try:
            # Try to get from live feed first
            if self.market_data_ws:
                # This would need implementation in the websocket adapter
                pass

            # Fallback to REST API
            ticker = await self.adapter.get(f"/market/ticker/{symbol}")
            orderbook = await self.adapter.get(f"/market/orderbook/{symbol}")

            return {
                'ticker': ticker,
                'orderbook': orderbook,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.warning(f"Failed to get market data for {symbol}: {e}")
            return {}

    # Execution Algorithms Implementation
    async def _execute_participate(self, order: LiveOrder, market_data: Dict[str, Any]) -> ExecutionReport:
        """Participate in current market volume without dominating."""
        symbol = order.payload.get("symbol", order.strategy_symbol)
        quantity = float(order.payload.get("quantity", 0.0))

        # Get orderbook data
        orderbook = market_data.get('orderbook', {})
        best_bid = orderbook.get('best_bid', 0.0)
        best_ask = orderbook.get('best_ask', 0.0)
        bid_volume = orderbook.get('bid_volume', 0.0)
        ask_volume = orderbook.get('ask_volume', 0.0)

        side = order.payload.get("side", "BUY").upper()

        if side == "BUY":
            # Participate at bid without taking all volume
            participation_rate = min(0.1, quantity / max(bid_volume, 1))  # Max 10% participation
            order.payload["price"] = best_bid
            order.payload["quantity"] = quantity * participation_rate
        else:
            # Participate at ask
            participation_rate = min(0.1, quantity / max(ask_volume, 1))
            order.payload["price"] = best_ask
            order.payload["quantity"] = quantity * participation_rate

        return await self.adapter.submit_order(order.payload)

    async def _execute_provide(self, order: LiveOrder, market_data: Dict[str, Any]) -> ExecutionReport:
        """Provide liquidity by placing limit orders."""
        symbol = order.payload.get("symbol", order.strategy_symbol)
        quantity = float(order.payload.get("quantity", 0.0))

        orderbook = market_data.get('orderbook', {})
        best_bid = orderbook.get('best_bid', 0.0)
        best_ask = orderbook.get('best_ask', 0.0)
        spread = best_ask - best_bid

        side = order.payload.get("side", "BUY").upper()

        if side == "BUY":
            # Place limit order slightly below best bid to provide liquidity
            price_offset = spread * 0.1  # 10% inside the spread
            order.payload["price"] = best_bid - price_offset
            order.payload["type"] = "limit"
        else:
            # Place limit order slightly above best ask
            price_offset = spread * 0.1
            order.payload["price"] = best_ask + price_offset
            order.payload["type"] = "limit"

        return await self.adapter.submit_order(order.payload)

    async def _execute_adaptive(self, order: LiveOrder, market_data: Dict[str, Any]) -> ExecutionReport:
        """Adapt execution based on current market conditions."""
        symbol = order.payload.get("symbol", order.strategy_symbol)

        # Use market regime to determine execution style
        if self.market_regime == MarketRegime.HIGH_VOLATILITY:
            # Use stealth execution in high volatility
            return await self._execute_stealth(order, market_data)
        elif self.market_regime == MarketRegime.LOW_VOLATILITY:
            # Use aggressive execution in low volatility
            return await self._execute_aggressive(order, market_data)
        elif self.market_regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
            # Participate in trends
            return await self._execute_participate(order, market_data)
        else:
            # Provide liquidity in sideways markets
            return await self._execute_provide(order, market_data)

    async def _execute_stealth(self, order: LiveOrder, market_data: Dict[str, Any]) -> ExecutionReport:
        """Execute with minimal market impact using iceberg orders."""
        # Convert to iceberg order
        order.order_type = OrderType.ICEBERG
        order.iceberg_quantity = float(order.payload.get("quantity", 0.0)) / 10  # 10 slices
        return (await self._submit_iceberg_order(order))[0]

    async def _execute_aggressive(self, order: LiveOrder, market_data: Dict[str, Any]) -> ExecutionReport:
        """Execute aggressively for fast fills."""
        # Use immediate execution with slight price improvement
        orderbook = market_data.get('orderbook', {})
        best_bid = orderbook.get('best_bid', 0.0)
        best_ask = orderbook.get('best_ask', 0.0)

        side = order.payload.get("side", "BUY").upper()

        if side == "BUY":
            # Bid slightly above best bid for aggressive buy
            order.payload["price"] = best_bid * 1.0001  # 1 bp improvement
        else:
            # Ask slightly below best ask for aggressive sell
            order.payload["price"] = best_ask * 0.9999  # 1 bp improvement

        return await self.adapter.submit_order(order.payload)

    # Advanced Order Types Implementation
    async def _submit_iceberg_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit iceberg order with hidden quantity."""
        reports = []
        total_quantity = float(order.payload.get("quantity", 0.0))
        visible_quantity = order.iceberg_quantity or (total_quantity / 10)
        symbol = order.payload.get("symbol", order.strategy_symbol)

        # Create slices
        num_slices = int(total_quantity / visible_quantity)
        remaining_quantity = total_quantity

        for i in range(num_slices):
            slice_quantity = min(visible_quantity, remaining_quantity)
            slice_order = LiveOrder(
                payload={
                    **order.payload,
                    "quantity": slice_quantity,
                    "iceberg": True,
                    "iceberg_total": total_quantity,
                    "iceberg_slice": i + 1,
                    "iceberg_total_slices": num_slices
                },
                strategy_symbol=symbol,
                order_type=OrderType.LIMIT,
                parent_order_id=f"iceberg_{order.created_at.timestamp()}"
            )

            slice_order.slices.append(OrderSlice(quantity=slice_quantity))

            # Submit slice
            report = await self.adapter.submit_order(slice_order.payload)
            reports.append(report)

            # Wait before next slice to avoid detection
            if i < num_slices - 1:
                await asyncio.sleep(1.0)  # 1 second delay

            remaining_quantity -= slice_quantity
            if remaining_quantity <= 0:
                break

        # Track iceberg slices
        self.iceberg_slices[order.payload.get("symbol", order.strategy_symbol)] = [
            OrderSlice(quantity=slice_quantity) for _ in range(num_slices)
        ]

        return reports

    async def _submit_bracket_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit bracket order with take profit and stop loss."""
        reports = []
        symbol = order.payload.get("symbol", order.strategy_symbol)
        parent_id = f"bracket_{order.created_at.timestamp()}"

        # Submit main order
        main_order = LiveOrder(
            payload={**order.payload},
            strategy_symbol=symbol,
            parent_order_id=parent_id
        )
        main_report = await self.adapter.submit_order(main_order.payload)
        reports.append(main_report)

        # Submit take profit order
        if order.bracket_take_profit:
            tp_order = LiveOrder(
                payload={
                    "symbol": symbol,
                    "side": "SELL" if order.payload.get("side") == "BUY" else "BUY",
                    "quantity": float(order.payload.get("quantity", 0.0)),
                    "price": order.bracket_take_profit,
                    "type": "limit"
                },
                strategy_symbol=symbol,
                order_type=OrderType.LIMIT,
                parent_order_id=parent_id
            )
            tp_report = await self.adapter.submit_order(tp_order.payload)
            reports.append(tp_report)

        # Submit stop loss order
        if order.bracket_stop_loss:
            sl_order = LiveOrder(
                payload={
                    "symbol": symbol,
                    "side": "SELL" if order.payload.get("side") == "BUY" else "BUY",
                    "quantity": float(order.payload.get("quantity", 0.0)),
                    "price": order.bracket_stop_loss,
                    "type": "stop"
                },
                strategy_symbol=symbol,
                order_type=OrderType.STOP,
                parent_order_id=parent_id
            )
            sl_report = await self.adapter.submit_order(sl_order.payload)
            reports.append(sl_report)

        # Track bracket relationships
        self.bracket_orders[symbol][parent_id] = {
            "main": main_report.order_id,
            "take_profit": tp_report.order_id if order.bracket_take_profit else None,
            "stop_loss": sl_report.order_id if order.bracket_stop_loss else None
        }

        return reports

    async def _submit_oco_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit One-Cancels-Other order."""
        reports = []
        symbol = order.payload.get("symbol", order.strategy_symbol)
        oco_group_id = f"oco_{order.created_at.timestamp()}"

        # Submit first leg
        leg1_order = LiveOrder(
            payload={**order.payload, "oco_group": oco_group_id, "oco_leg": 1},
            strategy_symbol=symbol,
            oco_linked_order=oco_group_id
        )
        leg1_report = await self.adapter.submit_order(leg1_order.payload)
        reports.append(leg1_report)

        # Submit second leg (OCO partner)
        if order.oco_linked_order:
            leg2_payload = order.oco_linked_order
            leg2_order = LiveOrder(
                payload={**leg2_payload, "oco_group": oco_group_id, "oco_leg": 2},
                strategy_symbol=symbol,
                oco_linked_order=oco_group_id
            )
            leg2_report = await self.adapter.submit_order(leg2_order.payload)
            reports.append(leg2_report)

        # Track OCO relationship
        self.oco_orders[leg1_report.order_id] = leg2_report.order_id
        self.oco_orders[leg2_report.order_id] = leg1_report.order_id

        return reports

    async def _submit_twap_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit Time-Weighted Average Price order."""
        reports = []
        symbol = order.payload.get("symbol", order.strategy_symbol)
        total_quantity = float(order.payload.get("quantity", 0.0))
        duration = order.twap_duration or 300  # 5 minutes default
        num_slices = max(5, duration // 30)  # Slice every 30 seconds
        slice_quantity = total_quantity / num_slices
        twap_id = f"twap_{order.created_at.timestamp()}"

        # Track TWAP order
        self.twap_orders[symbol][twap_id] = {
            "total_quantity": total_quantity,
            "remaining_quantity": total_quantity,
            "duration": duration,
            "num_slices": num_slices,
            "slice_quantity": slice_quantity,
            "start_time": datetime.utcnow(),
            "executed_slices": 0
        }

        # Submit first slice
        slice_order = LiveOrder(
            payload={
                **order.payload,
                "quantity": slice_quantity,
                "twap_id": twap_id
            },
            strategy_symbol=symbol,
            order_type=OrderType.MARKET,
            parent_order_id=twap_id
        )
        first_report = await self.adapter.submit_order(slice_order.payload)
        reports.append(first_report)

        # Schedule remaining slices
        asyncio.create_task(self._execute_twap_slices(symbol, twap_id))

        return reports

    async def _submit_vwap_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit Volume-Weighted Average Price order."""
        reports = []
        symbol = order.payload.get("symbol", order.strategy_symbol)
        total_quantity = float(order.payload.get("quantity", 0.0))
        vwap_id = f"vwap_{order.created_at.timestamp()}"

        # Track VWAP order
        self.vwap_orders[symbol][vwap_id] = {
            "total_quantity": total_quantity,
            "remaining_quantity": total_quantity,
            "start_time": order.vwap_start_time or datetime.utcnow(),
            "executed_quantity": 0.0,
            "vwap_price": 0.0
        }

        # Start VWAP execution
        asyncio.create_task(self._execute_vwap_order(symbol, vwap_id, order))

        return reports

    async def _submit_trailing_stop_order(self, order: LiveOrder) -> List[ExecutionReport]:
        """Submit trailing stop order."""
        symbol = order.payload.get("symbol", order.strategy_symbol)
        side = order.payload.get("side", "BUY").upper()

        # Initialize trailing stop tracking
        if side == "BUY":
            # For long positions, trail below the highest price
            self.trailing_stops[symbol][order.created_at.timestamp()] = {
                "type": "long",
                "trail_distance": order.trailing_stop_distance or 0.02,  # 2% default
                "highest_price": float(order.payload.get("price", 0.0)),
                "trigger_price": None
            }
        else:
            # For short positions, trail above the lowest price
            self.trailing_stops[symbol][order.created_at.timestamp()] = {
                "type": "short",
                "trail_distance": order.trailing_stop_distance or 0.02,
                "lowest_price": float(order.payload.get("price", 0.0)),
                "trigger_price": None
            }

        # Submit as regular stop order initially
        stop_payload = {
            **order.payload,
            "type": "stop",
            "stop_price": order.trailing_stop_trigger
        }

        report = await self.adapter.submit_order(stop_payload)
        return [report]

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order and handle complex order relationships."""
        response = await self.adapter.cancel_order(order_id)

        # Handle complex order cancellations
        if order_id in self.oco_orders:
            # Cancel OCO partner
            partner_id = self.oco_orders[order_id]
            try:
                await self.adapter.cancel_order(partner_id)
                self._open_orders.pop(partner_id, None)
                self.order_manager.remove(partner_id)
            except Exception as e:
                logger.warning(f"Failed to cancel OCO partner {partner_id}: {e}")

        # Handle bracket order cancellations
        for symbol, brackets in self.bracket_orders.items():
            for parent_id, orders in brackets.items():
                if order_id in [orders.get("main"), orders.get("take_profit"), orders.get("stop_loss")]:
                    # Cancel all related orders
                    for related_order_id in [orders.get("main"), orders.get("take_profit"), orders.get("stop_loss")]:
                        if related_order_id and related_order_id != order_id:
                            try:
                                await self.adapter.cancel_order(related_order_id)
                                self._open_orders.pop(related_order_id, None)
                                self.order_manager.remove(related_order_id)
                            except Exception as e:
                                logger.warning(f"Failed to cancel bracket order {related_order_id}: {e}")
                    break

        # Handle iceberg slice cancellations
        for symbol, slices in self.iceberg_slices.items():
            # Cancel remaining slices if parent is cancelled
            pass  # Implementation for iceberg cancellation

        # Clean up tracking
        self._open_orders.pop(order_id, None)
        self.order_manager.remove(order_id)
        self.oco_orders.pop(order_id, None)

        self.strategy.monitor.log_event("order_cancelled", tags={"order_id": order_id})
        self.strategy.monitor.record_metric("live_open_orders", len(self._open_orders))
        return response

    # Background Tasks Implementation
    async def _process_order_queue(self) -> None:
        """Process queued orders when capacity allows."""
        while not self._shutdown:
            try:
                # Wait for order or shutdown signal
                order = await asyncio.wait_for(self._order_queue.get(), timeout=1.0)
                if self._shutdown:
                    break

                # Check if we can now process the order
                if len(self._open_orders) < self.max_concurrent_orders:
                    try:
                        await self.submit_order(order)
                        logger.info(f"Processed queued order for {order.strategy_symbol}")
                    except Exception as e:
                        logger.error(f"Failed to process queued order: {e}")
                else:
                    # Put back in queue
                    await self._order_queue.put(order)
                    await asyncio.sleep(0.1)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Order queue processing error: {e}")

    async def _monitor_performance(self) -> None:
        """Monitor live trading performance metrics."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Update every minute

                if not self.performance_monitoring:
                    continue

                # Calculate performance metrics
                if self.execution_times:
                    avg_execution_time = statistics.mean(self.execution_times)
                    p95_execution_time = statistics.quantiles(self.execution_times, n=20)[18]  # 95th percentile
                    self.strategy.monitor.record_metric("avg_execution_time_ms", avg_execution_time)
                    self.strategy.monitor.record_metric("p95_execution_time_ms", p95_execution_time)

                if self.slippage_history:
                    avg_slippage = statistics.mean(self.slippage_history)
                    max_slippage = max(self.slippage_history)
                    self.strategy.monitor.record_metric("avg_slippage_bps", avg_slippage)
                    self.strategy.monitor.record_metric("max_slippage_bps", max_slippage)

                if self.fill_rates:
                    avg_fill_rate = statistics.mean(self.fill_rates)
                    self.strategy.monitor.record_metric("avg_fill_rate", avg_fill_rate)

                # System health metrics
                self.strategy.monitor.record_metric("open_orders_count", len(self._open_orders))
                self.strategy.monitor.record_metric("queued_orders_count", self._order_queue.qsize())
                self.strategy.monitor.record_metric("active_strategies", 1)  # For now

                # Memory usage (approximate)
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.strategy.monitor.record_metric("memory_usage_mb", memory_mb)

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")

    async def _monitor_risk(self) -> None:
        """Continuous risk monitoring and alerts."""
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Portfolio risk checks
                equity = self.portfolio.snapshot(datetime.utcnow(), {}).equity

                # Drawdown check
                if not self.guardrails.check_drawdown(equity):
                    self.strategy.monitor.log_event("risk_alert", tags={
                        "type": "drawdown",
                        "severity": "critical",
                        "equity": equity
                    })

                # Daily loss check
                if not self.guardrails.check_daily_loss(equity, datetime.utcnow()):
                    self.strategy.monitor.log_event("risk_alert", tags={
                        "type": "daily_loss",
                        "severity": "warning",
                        "equity": equity
                    })

                # Position concentration check
                total_exposure = sum(abs(pos.quantity * pos.avg_price) for pos in self.portfolio.state.positions.values())
                max_position = max((abs(pos.quantity * pos.avg_price) for pos in self.portfolio.state.positions.values()), default=0)
                concentration_ratio = max_position / max(total_exposure, 1) if total_exposure > 0 else 0

                if concentration_ratio > 0.3:  # 30% concentration
                    self.strategy.monitor.log_event("risk_alert", tags={
                        "type": "concentration",
                        "severity": "warning",
                        "ratio": concentration_ratio
                    })

                # Volatility-adjusted position sizing
                for symbol, volatility in self.symbol_volatility.items():
                    if volatility > 0.05:  # High volatility
                        position = self.portfolio.state.positions.get(symbol)
                        if position and abs(position.quantity) > 1000:  # Arbitrary threshold
                            self.strategy.monitor.log_event("risk_alert", tags={
                                "type": "volatility",
                                "symbol": symbol,
                                "volatility": volatility,
                                "position_size": position.quantity
                            })

            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")

    async def _detect_market_regime(self) -> None:
        """Detect and adapt to market regime changes."""
        while not self._shutdown:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                if not self.enable_market_regime_detection:
                    continue

                # Analyze price action across all symbols
                regime_signals = []

                for symbol, prices in self.price_history.items():
                    if len(prices) < 50:  # Need enough data
                        continue

                    # Calculate technical indicators for regime detection
                    price_array = list(prices)

                    # RSI for momentum
                    rsi_values = []
                    for i in range(14, len(price_array)):
                        gains = sum(max(0, price_array[j] - price_array[j-1]) for j in range(i-14, i))
                        losses = sum(max(0, price_array[j-1] - price_array[j]) for j in range(i-14, i))
                        if losses == 0:
                            rsi = 100
                        else:
                            rs = gains / losses
                            rsi = 100 - (100 / (1 + rs))
                        rsi_values.append(rsi)

                    if rsi_values:
                        current_rsi = rsi_values[-1]

                        # Volatility using standard deviation
                        volatility = statistics.stdev(price_array[-20:]) / statistics.mean(price_array[-20:])

                        # Trend detection using linear regression
                        x = list(range(len(price_array[-20:])))
                        y = price_array[-20:]
                        slope = statistics.linear_regression(x, y).slope
                        trend_strength = abs(slope) / statistics.mean(y)

                        # Classify regime
                        if volatility > 0.03:  # 3% daily volatility threshold
                            regime = MarketRegime.HIGH_VOLATILITY
                        elif volatility < 0.01:  # 1% daily volatility threshold
                            regime = MarketRegime.LOW_VOLATILITY
                        elif trend_strength > 0.005 and slope > 0:  # Strong uptrend
                            regime = MarketRegime.TRENDING_UP
                        elif trend_strength > 0.005 and slope < 0:  # Strong downtrend
                            regime = MarketRegime.TRENDING_DOWN
                        else:
                            regime = MarketRegime.SIDEWAYS

                        regime_signals.append(regime)

                        # Update symbol-specific volatility
                        self.symbol_volatility[symbol] = volatility

                # Determine overall market regime
                if regime_signals:
                    # Use majority vote for overall regime
                    regime_counts = {}
                    for regime in regime_signals:
                        regime_counts[regime] = regime_counts.get(regime, 0) + 1

                    current_regime = max(regime_counts, key=regime_counts.get)

                    # Update regime if changed
                    if current_regime != self.market_regime:
                        logger.info(f"Market regime changed: {self.market_regime.value} -> {current_regime.value}")
                        self.market_regime = current_regime

                        # Log regime change
                        self.strategy.monitor.log_event("regime_change", tags={
                            "from_regime": self.market_regime.value,
                            "to_regime": current_regime.value
                        })

                    # Record regime history
                    self.regime_history.append((datetime.utcnow(), current_regime))

            except Exception as e:
                logger.error(f"Market regime detection error: {e}")

    # TWAP and VWAP Execution
    async def _execute_twap_slices(self, symbol: str, twap_id: str) -> None:
        """Execute remaining TWAP slices over time."""
        twap_data = self.twap_orders[symbol].get(twap_id)
        if not twap_data:
            return

        slice_interval = twap_data["duration"] / twap_data["num_slices"]
        executed_slices = 1  # First slice already executed

        while executed_slices < twap_data["num_slices"] and not self._shutdown:
            await asyncio.sleep(slice_interval)

            remaining_quantity = twap_data["remaining_quantity"] - twap_data["slice_quantity"]
            if remaining_quantity <= 0:
                break

            # Submit next slice
            slice_payload = {
                "symbol": symbol,
                "side": "BUY",  # Should be determined from original order
                "quantity": min(twap_data["slice_quantity"], remaining_quantity),
                "type": "market",
                "twap_id": twap_id
            }

            try:
                report = await self.adapter.submit_order(slice_payload)
                executed_slices += 1
                twap_data["executed_slices"] = executed_slices
                twap_data["remaining_quantity"] = remaining_quantity

                logger.info(f"TWAP slice {executed_slices}/{twap_data['num_slices']} executed for {symbol}")

            except Exception as e:
                logger.error(f"TWAP slice execution failed: {e}")

    async def _execute_vwap_order(self, symbol: str, vwap_id: str, original_order: LiveOrder) -> None:
        """Execute VWAP order based on volume profile."""
        vwap_data = self.vwap_orders[symbol].get(vwap_id)
        if not vwap_data:
            return

        # VWAP calculation requires intraday volume data
        # This is a simplified implementation

        while vwap_data["remaining_quantity"] > 0 and not self._shutdown:
            try:
                # Get current market data
                market_data = await self._get_market_data(symbol)
                ticker = market_data.get("ticker", {})

                current_price = ticker.get("price", 0.0)
                current_volume = ticker.get("volume", 0.0)

                if current_price > 0 and current_volume > 0:
                    # Simple VWAP approximation
                    vwap_data["vwap_price"] = (
                        (vwap_data["vwap_price"] * vwap_data["executed_quantity"]) +
                        (current_price * current_volume)
                    ) / (vwap_data["executed_quantity"] + current_volume)

                    # Execute portion based on volume
                    execution_size = min(
                        vwap_data["remaining_quantity"] * 0.1,  # Execute 10% at a time
                        vwap_data["remaining_quantity"]
                    )

                    if execution_size > 0:
                        slice_payload = {
                            "symbol": symbol,
                            "side": original_order.payload.get("side", "BUY"),
                            "quantity": execution_size,
                            "type": "market",
                            "vwap_id": vwap_id
                        }

                        report = await self.adapter.submit_order(slice_payload)
                        vwap_data["executed_quantity"] += execution_size
                        vwap_data["remaining_quantity"] -= execution_size

                        logger.info(f"VWAP execution: {execution_size} @ {current_price} for {symbol}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"VWAP execution error: {e}")
                await asyncio.sleep(60)

    # Market Data Feed Handlers
    async def _listen_execution_feed(self) -> None:
        """Listen to execution reports via websocket."""
        assert self.execution_ws is not None
        try:
            async for message in self.execution_ws.listen():
                try:
                    order_id = message.get("orderId") or message.get("order_id")
                    if order_id:
                        report = ExecutionReport(
                            order_id=order_id,
                            status=message.get("status", "UNKNOWN"),
                            filled_qty=float(message.get("filled", 0.0)),
                            price=float(message.get("price", 0.0)),
                            raw=message
                        )
                        self.handle_execution_report(report)
                except Exception as e:
                    logger.error(f"Execution feed processing error: {e}")
        except Exception as e:
            logger.error(f"Execution feed connection error: {e}")

    async def _listen_market_data_feed(self) -> None:
        """Listen to market data updates."""
        assert self.market_data_ws is not None
        try:
            async for message in self.market_data_ws.listen():
                try:
                    symbol = message.get("symbol")
                    if symbol and "price" in message:
                        price = float(message.get("price", 0.0))
                        volume = float(message.get("volume", 0.0))

                        # Update price history for regime detection
                        self.price_history[symbol].append(price)
                        self.volume_history[symbol].append(volume)

                        # Update trailing stops
                        await self._update_trailing_stops(symbol, price)

                        # Emit market data event
                        await self.event_queue.publish(
                            StreamEvent(symbol=symbol, payload=message)
                        )

                except Exception as e:
                    logger.error(f"Market data feed processing error: {e}")
        except Exception as e:
            logger.error(f"Market data feed connection error: {e}")

    async def _update_trailing_stops(self, symbol: str, current_price: float) -> None:
        """Update trailing stop orders based on price movement."""
        for order_id, stop_data in self.trailing_stops[symbol].items():
            if stop_data["type"] == "long":
                # Update highest price for long positions
                if current_price > stop_data["highest_price"]:
                    stop_data["highest_price"] = current_price
                    stop_data["trigger_price"] = current_price * (1 - stop_data["trail_distance"])

            elif stop_data["type"] == "short":
                # Update lowest price for short positions
                if current_price < stop_data["lowest_price"]:
                    stop_data["lowest_price"] = current_price
                    stop_data["trigger_price"] = current_price * (1 + stop_data["trail_distance"])

            # Check if stop should be triggered
            if stop_data["trigger_price"]:
                if (stop_data["type"] == "long" and current_price <= stop_data["trigger_price"]) or \
                   (stop_data["type"] == "short" and current_price >= stop_data["trigger_price"]):
                    # Trigger stop loss
                    try:
                        stop_payload = {
                            "symbol": symbol,
                            "side": "SELL" if stop_data["type"] == "long" else "BUY",
                            "quantity": 1000,  # Should be from original position
                            "type": "market",
                            "triggered_by": "trailing_stop"
                        }
                        await self.adapter.submit_order(stop_payload)
                        logger.info(f"Trailing stop triggered for {symbol} at {current_price}")
                    except Exception as e:
                        logger.error(f"Trailing stop execution failed: {e}")

    async def _cancel_all_orders(self) -> None:
        """Cancel all open orders during shutdown."""
        order_ids = list(self._open_orders.keys())
        for order_id in order_ids:
            try:
                await self.cancel_order(order_id)
            except Exception as e:
                logger.error(f"Failed to cancel order {order_id} during shutdown: {e}")

    # Utility Methods
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            "execution_times": {
                "avg": statistics.mean(self.execution_times) if self.execution_times else 0,
                "p95": statistics.quantiles(self.execution_times, n=20)[18] if len(self.execution_times) >= 20 else 0,
                "count": len(self.execution_times)
            },
            "slippage": {
                "avg_bps": statistics.mean(self.slippage_history) if self.slippage_history else 0,
                "max_bps": max(self.slippage_history) if self.slippage_history else 0,
                "count": len(self.slippage_history)
            },
            "fill_rates": {
                "avg": statistics.mean(self.fill_rates) if self.fill_rates else 0,
                "count": len(self.fill_rates)
            },
            "orders": {
                "open": len(self._open_orders),
                "queued": self._order_queue.qsize()
            },
            "market_regime": self.market_regime.value,
            "regime_history": [(ts.isoformat(), regime.value) for ts, regime in list(self.regime_history)[-10:]]
        }

        return stats

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed order status."""
        order = self._open_orders.get(order_id)
        if not order:
            return None

        return {
            "order_id": order_id,
            "symbol": order.strategy_symbol,
            "type": order.order_type.value,
            "algo": order.execution_algo.value,
            "created_at": order.created_at.isoformat(),
            "payload": order.payload,
            "metrics": [m.__dict__ for m in order.metrics[-5:]]  # Last 5 metrics
        }

    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing order."""
        if order_id not in self._open_orders:
            raise ValueError(f"Order {order_id} not found")

        # Implementation depends on broker API capabilities
        # This is a placeholder
        return {"status": "not_implemented", "order_id": order_id}

    async def get_market_data_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data snapshot."""
        return await self._get_market_data(symbol)

    # Health Check and Diagnostics
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check."""
        return {
            "status": "healthy" if self._running else "stopped",
            "websocket_execution": self.execution_ws is not None,
            "websocket_market_data": self.market_data_ws is not None,
            "open_orders": len(self._open_orders),
            "queued_orders": self._order_queue.qsize(),
            "market_regime": self.market_regime.value,
            "performance_monitoring": self.performance_monitoring,
            "background_tasks": {
                "execution_processor": self._execution_processor_task is not None,
                "performance_monitor": self._performance_monitor_task is not None,
                "risk_monitor": self._risk_monitor_task is not None,
                "market_regime": self._market_regime_task is not None
            }
        }

    async def run_forever(self) -> None:
        """Run the engine indefinitely."""
        while not self._shutdown:
            await asyncio.sleep(1)

    async def _handle_event(self, event: StreamEvent) -> None:
        """Handle streaming events."""
        # Enhanced event handling with indicators and signals
        self.strategy.monitor.record_metric("live_events_total", 1.0, tags={"symbol": event.symbol})

        # Update portfolio snapshot
        price = event.payload.get("price", 0.0)
        self.guardrails.record_portfolio(datetime.utcnow(), self.portfolio.snapshot(datetime.utcnow(), {event.symbol: price}).equity)

        equity = self.guardrails.current_equity()

        # Risk checks
        if not self.guardrails.check_drawdown(equity):
            self.strategy.health_check("critical", message="Drawdown limit exceeded")
        if not self.guardrails.check_daily_loss(equity, datetime.utcnow()):
            self.strategy.health_check("warning", message="Daily loss limit exceeded")

        # Adaptive risk adjustments based on market regime
        if self.market_regime == MarketRegime.HIGH_VOLATILITY:
            # Increase risk thresholds during high volatility
            pass  # Implementation for dynamic risk adjustment

    @property
    def open_orders(self) -> Dict[str, LiveOrder]:
        """Get all open orders."""
        return dict(self._open_orders)


__all__ = [
    "LiveEngine",
    "LiveOrder",
    "OrderType",
    "ExecutionAlgorithm",
    "MarketRegime",
    "ExecutionMetrics",
    "OrderSlice"
]

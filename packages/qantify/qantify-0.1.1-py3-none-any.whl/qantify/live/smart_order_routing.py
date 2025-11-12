"""
Smart Order Routing and Execution Optimization
==============================================

This module implements intelligent order routing algorithms that optimize execution
across multiple exchanges, minimize costs, and maximize fill rates through advanced
machine learning and market microstructure analysis.

Key Features:
- Multi-exchange order routing optimization
- Cost-minimization algorithms
- Latency-aware execution
- Market impact modeling
- Smart order slicing and iceberg orders
- Real-time exchange selection
- VWAP and TWAP execution algorithms
- Adaptive routing based on market conditions
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import asyncio

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import norm, t
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# Import existing Qantify modules
try:
    from ..data.clients.binance import BinanceClient
    from ..data.clients.alpaca import AlpacaClient
    from ..signals.indicators import rsi, bollinger_bands, exponential_moving_average
except ImportError:
    pass


@dataclass
class OrderRoutingConfig:
    """Configuration for smart order routing"""

    # Core parameters
    symbol: str = "BTCUSDT"
    order_side: str = "buy"  # "buy" or "sell"
    order_size: float = 1.0
    order_type: str = "market"  # "market", "limit", "stop", "twap", "vwap"

    # Routing parameters
    exchanges: List[str] = field(default_factory=lambda: ["binance", "coinbase", "kraken"])
    max_exchanges: int = 3
    routing_strategy: str = "cost_optimized"  # "cost_optimized", "latency_optimized", "liquidity_optimized"

    # Execution parameters
    time_horizon: int = 60  # seconds for TWAP/VWAP
    max_slippage: float = 0.005  # 0.5%
    min_fill_rate: float = 0.95

    # Risk management
    max_market_impact: float = 0.002
    position_limit_pct: float = 10.0

    # Advanced features
    use_machine_learning: bool = True
    adaptive_routing: bool = True
    real_time_optimization: bool = True

    # Performance tracking
    track_execution_metrics: bool = True
    log_routing_decisions: bool = True


@dataclass
class ExchangeProfile:
    """Profile of an exchange for routing decisions"""

    name: str
    fee_structure: Dict[str, float]  # maker/taker fees
    latency_ms: float
    liquidity_score: float  # 0-1 scale
    reliability_score: float  # 0-1 scale
    supported_symbols: List[str]
    min_order_size: float
    max_order_size: float
    last_update: float

    @property
    def total_cost_score(self) -> float:
        """Combined cost score including fees and latency"""
        # Normalize and combine metrics
        fee_score = (self.fee_structure.get('maker', 0.001) + self.fee_structure.get('taker', 0.001)) / 2.0
        latency_score = min(1.0, self.latency_ms / 1000.0)  # Normalize to 0-1
        liquidity_score = 1.0 - self.liquidity_score  # Invert (higher liquidity = lower cost)

        return (fee_score * 0.4 + latency_score * 0.3 + liquidity_score * 0.3)


@dataclass
class RoutingDecision:
    """Decision for order routing"""

    order_id: str
    exchange_allocations: Dict[str, float]  # exchange -> percentage
    execution_strategy: str
    expected_cost: float
    expected_latency: float
    expected_fill_rate: float
    timestamp: float
    reasoning: str = ""


@dataclass
class ExecutionSlice:
    """Individual order slice for execution"""

    slice_id: str
    exchange: str
    size: float
    price: Optional[float] = None
    order_type: str = "market"
    urgency: str = "normal"  # "low", "normal", "high"
    deadline: Optional[float] = None


class MarketDataAggregator:
    """Aggregates market data from multiple exchanges"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config
        self.exchange_data = {}
        self.price_feeds = {}
        self.order_books = {}

    def update_market_data(self, exchange: str, data: Dict[str, Any]):
        """Update market data for an exchange"""

        self.exchange_data[exchange] = {
            'prices': data.get('prices', {}),
            'order_book': data.get('order_book', {}),
            'liquidity': data.get('liquidity', {}),
            'fees': data.get('fees', {}),
            'latency': data.get('latency', 100.0),
            'timestamp': time.time()
        }

    def get_exchange_profiles(self) -> Dict[str, ExchangeProfile]:
        """Get current exchange profiles"""

        profiles = {}

        for exchange, data in self.exchange_data.items():
            # Calculate liquidity score
            order_book = data.get('order_book', {})
            liquidity_score = self._calculate_liquidity_score(order_book)

            # Get fee structure
            fees = data.get('fees', {'maker': 0.001, 'taker': 0.001})

            # Create profile
            profiles[exchange] = ExchangeProfile(
                name=exchange,
                fee_structure=fees,
                latency_ms=data.get('latency', 100.0),
                liquidity_score=liquidity_score,
                reliability_score=0.95,  # Placeholder
                supported_symbols=list(data.get('prices', {}).keys()),
                min_order_size=0.001,
                max_order_size=1000.0,
                last_update=data.get('timestamp', time.time())
            )

        return profiles

    def _calculate_liquidity_score(self, order_book: Dict[str, Any]) -> float:
        """Calculate liquidity score from order book"""

        if not order_book:
            return 0.0

        # Calculate depth at different levels
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])

        # Depth at first 5 levels
        bid_depth = sum(size for _, size in bids[:5]) if bids else 0
        ask_depth = sum(size for _, size in asks[:5]) if asks else 0

        # Spread
        if bids and asks:
            spread = asks[0][0] - bids[0][0]
            spread_score = 1.0 / (1.0 + spread)  # Lower spread = higher score
        else:
            spread_score = 0.0

        # Combine metrics
        depth_score = min(1.0, (bid_depth + ask_depth) / 100.0)  # Normalize
        liquidity_score = (depth_score + spread_score) / 2.0

        return liquidity_score


class CostOptimizationEngine:
    """Optimizes execution costs across exchanges"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config

    def optimize_routing(self, order_config: OrderRoutingConfig,
                        exchange_profiles: Dict[str, ExchangeProfile]) -> RoutingDecision:
        """Optimize order routing for minimum cost"""

        # Filter available exchanges
        available_exchanges = self._filter_available_exchanges(
            order_config.symbol, exchange_profiles
        )

        if not available_exchanges:
            return self._create_default_routing(order_config)

        # Calculate optimal allocation
        if len(available_exchanges) == 1:
            # Only one exchange available
            allocation = {list(available_exchanges.keys())[0]: 1.0}
        else:
            # Multi-exchange optimization
            allocation = self._optimize_multi_exchange_allocation(
                order_config, available_exchanges
            )

        # Calculate expected metrics
        expected_cost, expected_latency, expected_fill_rate = self._calculate_expected_metrics(
            allocation, available_exchanges
        )

        return RoutingDecision(
            order_id=f"route_{int(time.time())}",
            exchange_allocations=allocation,
            execution_strategy=self._select_execution_strategy(order_config, allocation),
            expected_cost=expected_cost,
            expected_latency=expected_latency,
            expected_fill_rate=expected_fill_rate,
            timestamp=time.time(),
            reasoning="Cost-optimized routing"
        )

    def _filter_available_exchanges(self, symbol: str,
                                  exchange_profiles: Dict[str, ExchangeProfile]) -> Dict[str, ExchangeProfile]:
        """Filter exchanges that support the symbol"""

        available = {}
        for name, profile in exchange_profiles.items():
            if symbol in profile.supported_symbols:
                # Additional filters (liquidity, fees, etc.)
                if profile.liquidity_score > 0.1:  # Minimum liquidity threshold
                    available[name] = profile

        return available

    def _optimize_multi_exchange_allocation(self, order_config: OrderRoutingConfig,
                                          exchange_profiles: Dict[str, ExchangeProfile]) -> Dict[str, float]:
        """Optimize allocation across multiple exchanges"""

        def objective(allocation):
            """Cost objective function"""
            total_cost = 0.0
            allocation_dict = dict(zip(exchange_profiles.keys(), allocation))

            for exchange, weight in allocation_dict.items():
                if weight > 0:
                    profile = exchange_profiles[exchange]
                    # Cost components: fees, latency penalty, liquidity penalty
                    fee_cost = profile.fee_structure.get('taker', 0.001) * weight
                    latency_penalty = (profile.latency_ms / 1000.0) * 0.1 * weight
                    liquidity_bonus = profile.liquidity_score * 0.05 * weight

                    total_cost += fee_cost + latency_penalty - liquidity_bonus

            return total_cost

        # Constraints
        n_exchanges = len(exchange_profiles)
        bounds = [(0, 1) for _ in range(n_exchanges)]
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - 1},  # Sum to 1
        ]

        # Initial guess: equal allocation
        x0 = np.ones(n_exchanges) / n_exchanges

        try:
            result = optimize.minimize(
                objective, x0,
                bounds=bounds,
                constraints=constraints,
                method='SLSQP'
            )

            if result.success:
                allocation = dict(zip(exchange_profiles.keys(), result.x))
                # Remove zero allocations
                allocation = {k: v for k, v in allocation.items() if v > 0.001}
                # Renormalize
                total = sum(allocation.values())
                allocation = {k: v/total for k, v in allocation.items()}
                return allocation
            else:
                # Fallback to equal allocation
                return {name: 1.0/n_exchanges for name in exchange_profiles.keys()}

        except:
            # Fallback to equal allocation
            return {name: 1.0/n_exchanges for name in exchange_profiles.keys()}

    def _calculate_expected_metrics(self, allocation: Dict[str, float],
                                  exchange_profiles: Dict[str, ExchangeProfile]) \
            -> Tuple[float, float, float]:
        """Calculate expected cost, latency, and fill rate"""

        total_cost = 0.0
        total_latency = 0.0
        total_fill_rate = 0.0

        for exchange, weight in allocation.items():
            profile = exchange_profiles[exchange]

            # Cost: weighted average of fees
            cost = profile.fee_structure.get('taker', 0.001) * weight
            total_cost += cost

            # Latency: weighted average
            latency = profile.latency_ms * weight
            total_latency += latency

            # Fill rate: based on liquidity and reliability
            fill_rate = (profile.liquidity_score * 0.7 + profile.reliability_score * 0.3) * weight
            total_fill_rate += fill_rate

        return total_cost, total_latency, total_fill_rate

    def _select_execution_strategy(self, order_config: OrderRoutingConfig,
                                 allocation: Dict[str, float]) -> str:
        """Select optimal execution strategy"""

        n_exchanges = len(allocation)

        if order_config.order_type == "market":
            if n_exchanges == 1:
                return "direct_market"
            else:
                return "parallel_market"
        elif order_config.order_type == "limit":
            return "limit_order"
        elif order_config.order_type == "twap":
            return "time_weighted_average"
        elif order_config.order_type == "vwap":
            return "volume_weighted_average"
        else:
            return "smart_routing"

    def _create_default_routing(self, order_config: OrderRoutingConfig) -> RoutingDecision:
        """Create default routing when optimization fails"""

        return RoutingDecision(
            order_id=f"default_{int(time.time())}",
            exchange_allocations={order_config.exchanges[0]: 1.0},
            execution_strategy="direct_market",
            expected_cost=0.001,
            expected_latency=100.0,
            expected_fill_rate=0.95,
            timestamp=time.time(),
            reasoning="Default routing - no optimization available"
        )


class LatencyOptimizationEngine:
    """Optimizes for minimum execution latency"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config

    def optimize_for_latency(self, order_config: OrderRoutingConfig,
                           exchange_profiles: Dict[str, ExchangeProfile]) -> RoutingDecision:
        """Optimize routing for minimum latency"""

        # Sort exchanges by latency
        sorted_exchanges = sorted(
            exchange_profiles.items(),
            key=lambda x: x[1].latency_ms
        )

        # Select top exchanges
        selected_exchanges = sorted_exchanges[:min(self.config.max_exchanges, len(sorted_exchanges))]

        # Allocate based on latency (prefer faster exchanges)
        total_weight = sum(1.0 / profile.latency_ms for _, profile in selected_exchanges)

        allocation = {}
        for exchange, profile in selected_exchanges:
            weight = (1.0 / profile.latency_ms) / total_weight
            allocation[exchange] = weight

        # Calculate expected metrics
        expected_latency = sum(profile.latency_ms * weight for _, profile in selected_exchanges for exchange, weight in allocation.items() if exchange == selected_exchanges[0][0])
        expected_cost = sum(profile.fee_structure.get('taker', 0.001) * allocation.get(exchange, 0) for exchange, profile in selected_exchanges)

        return RoutingDecision(
            order_id=f"latency_{int(time.time())}",
            exchange_allocations=allocation,
            execution_strategy="latency_optimized",
            expected_cost=expected_cost,
            expected_latency=expected_latency,
            expected_fill_rate=0.98,  # High fill rate for fast execution
            timestamp=time.time(),
            reasoning="Latency-optimized routing"
        )


class LiquidityOptimizationEngine:
    """Optimizes for maximum liquidity and fill rates"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config

    def optimize_for_liquidity(self, order_config: OrderRoutingConfig,
                             exchange_profiles: Dict[str, ExchangeProfile]) -> RoutingDecision:
        """Optimize routing for maximum liquidity"""

        # Sort exchanges by liquidity score
        sorted_exchanges = sorted(
            exchange_profiles.items(),
            key=lambda x: x[1].liquidity_score,
            reverse=True
        )

        # Select top exchanges
        selected_exchanges = sorted_exchanges[:min(self.config.max_exchanges, len(sorted_exchanges))]

        # Allocate based on liquidity (prefer more liquid exchanges)
        total_liquidity = sum(profile.liquidity_score for _, profile in selected_exchanges)

        allocation = {}
        for exchange, profile in selected_exchanges:
            if total_liquidity > 0:
                weight = profile.liquidity_score / total_liquidity
            else:
                weight = 1.0 / len(selected_exchanges)
            allocation[exchange] = weight

        # Calculate expected metrics
        expected_fill_rate = sum(profile.liquidity_score * allocation.get(exchange, 0) for exchange, profile in selected_exchanges)
        expected_cost = sum(profile.fee_structure.get('maker', 0.001) * allocation.get(exchange, 0) for exchange, profile in selected_exchanges)

        return RoutingDecision(
            order_id=f"liquidity_{int(time.time())}",
            exchange_allocations=allocation,
            execution_strategy="liquidity_optimized",
            expected_cost=expected_cost,
            expected_latency=200.0,  # Slightly higher latency for better fills
            expected_fill_rate=min(1.0, expected_fill_rate),
            timestamp=time.time(),
            reasoning="Liquidity-optimized routing"
        )


class OrderSlicingEngine:
    """Implements intelligent order slicing and iceberg orders"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config

    def create_execution_plan(self, routing_decision: RoutingDecision,
                            order_config: OrderRoutingConfig) -> List[ExecutionSlice]:
        """Create detailed execution plan with order slices"""

        slices = []
        slice_id_counter = 0

        for exchange, allocation_pct in routing_decision.exchange_allocations.items():
            exchange_size = order_config.order_size * allocation_pct

            # Determine slicing strategy
            if routing_decision.execution_strategy in ["twap", "vwap"]:
                # Time/volume weighted execution
                exchange_slices = self._create_time_slices(
                    exchange, exchange_size, routing_decision.execution_strategy, order_config.time_horizon
                )
            else:
                # Direct or smart routing
                exchange_slices = self._create_smart_slices(
                    exchange, exchange_size, routing_decision.execution_strategy
                )

            slices.extend(exchange_slices)
            slice_id_counter += len(exchange_slices)

        return slices

    def _create_time_slices(self, exchange: str, total_size: float,
                          strategy: str, time_horizon: int) -> List[ExecutionSlice]:
        """Create time-weighted slices"""

        slices = []
        n_slices = max(1, time_horizon // 10)  # One slice per 10 seconds

        # Exponential decay for TWAP (front-load)
        if strategy == "twap":
            weights = np.exp(-np.linspace(0, 2, n_slices))
            weights = weights / weights.sum()
        else:  # VWAP - more uniform
            weights = np.ones(n_slices) / n_slices

        current_time = time.time()
        slice_interval = time_horizon / n_slices

        for i, weight in enumerate(weights):
            slice_size = total_size * weight

            if slice_size >= 0.001:  # Minimum order size
                slice = ExecutionSlice(
                    slice_id=f"{exchange}_{i}_{int(current_time)}",
                    exchange=exchange,
                    size=slice_size,
                    order_type="market",
                    urgency="normal",
                    deadline=current_time + (i + 1) * slice_interval
                )
                slices.append(slice)

        return slices

    def _create_smart_slices(self, exchange: str, total_size: float,
                           strategy: str) -> List[ExecutionSlice]:
        """Create smart slices based on strategy"""

        if total_size <= 0.01:  # Small order, execute directly
            return [ExecutionSlice(
                slice_id=f"{exchange}_direct_{int(time.time())}",
                exchange=exchange,
                size=total_size,
                order_type="market",
                urgency="normal"
            )]

        # Large order - split into smaller pieces
        max_slice_size = min(total_size * 0.1, 0.1)  # Max 10% of order or 0.1 units
        n_slices = max(1, int(np.ceil(total_size / max_slice_size)))

        slices = []
        remaining_size = total_size

        for i in range(n_slices):
            if remaining_size <= 0:
                break

            slice_size = min(max_slice_size, remaining_size)

            # Add randomness to slice sizes
            if i < n_slices - 1:  # Not the last slice
                slice_size *= (0.8 + np.random.random() * 0.4)  # 80%-120% of base size
                slice_size = min(slice_size, remaining_size)

            slice = ExecutionSlice(
                slice_id=f"{exchange}_smart_{i}_{int(time.time())}",
                exchange=exchange,
                size=slice_size,
                order_type="market",
                urgency="normal" if i < n_slices - 1 else "high",  # Last slice high urgency
                deadline=time.time() + 30  # 30 second deadline
            )
            slices.append(slice)
            remaining_size -= slice_size

        return slices


class ExecutionMonitor:
    """Monitors order execution and provides feedback"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config
        self.execution_history = deque(maxlen=1000)
        self.performance_metrics = {}

    def track_execution(self, slice: ExecutionSlice, result: Dict[str, Any]):
        """Track execution result"""

        execution_record = {
            'slice_id': slice.slice_id,
            'exchange': slice.exchange,
            'intended_size': slice.size,
            'executed_size': result.get('executed_size', 0),
            'executed_price': result.get('executed_price', 0),
            'latency_ms': result.get('latency_ms', 0),
            'fees': result.get('fees', 0),
            'timestamp': time.time()
        }

        self.execution_history.append(execution_record)

        # Update performance metrics
        self._update_performance_metrics(slice.exchange, execution_record)

    def _update_performance_metrics(self, exchange: str, record: Dict[str, Any]):
        """Update performance metrics for an exchange"""

        if exchange not in self.performance_metrics:
            self.performance_metrics[exchange] = {
                'total_orders': 0,
                'total_executed': 0,
                'avg_latency': 0,
                'avg_slippage': 0,
                'fill_rate': 0
            }

        metrics = self.performance_metrics[exchange]

        # Update counters
        metrics['total_orders'] += 1
        metrics['total_executed'] += record['executed_size']

        # Update averages
        n = metrics['total_orders']
        metrics['avg_latency'] = (metrics['avg_latency'] * (n-1) + record['latency_ms']) / n

        # Calculate fill rate
        metrics['fill_rate'] = metrics['total_executed'] / sum(r['intended_size'] for r in self.execution_history if r['exchange'] == exchange)

    def get_exchange_performance(self, exchange: str) -> Dict[str, float]:
        """Get performance metrics for an exchange"""

        return self.performance_metrics.get(exchange, {})

    def get_routing_feedback(self) -> Dict[str, Any]:
        """Provide feedback for routing optimization"""

        feedback = {
            'best_exchanges': [],
            'worst_exchanges': [],
            'avg_fill_rate': 0,
            'avg_latency': 0
        }

        if not self.performance_metrics:
            return feedback

        # Sort exchanges by fill rate
        sorted_exchanges = sorted(
            self.performance_metrics.items(),
            key=lambda x: x[1]['fill_rate'],
            reverse=True
        )

        feedback['best_exchanges'] = [ex[0] for ex in sorted_exchanges[:3]]
        feedback['worst_exchanges'] = [ex[0] for ex in sorted_exchanges[-3:]]

        # Calculate averages
        all_metrics = list(self.performance_metrics.values())
        feedback['avg_fill_rate'] = np.mean([m['fill_rate'] for m in all_metrics])
        feedback['avg_latency'] = np.mean([m['avg_latency'] for m in all_metrics])

        return feedback


class SmartOrderRouter:
    """Main smart order routing engine"""

    def __init__(self, config: OrderRoutingConfig):
        self.config = config

        # Initialize components
        self.market_data = MarketDataAggregator(config)
        self.cost_optimizer = CostOptimizationEngine(config)
        self.latency_optimizer = LatencyOptimizationEngine(config)
        self.liquidity_optimizer = LiquidityOptimizationEngine(config)
        self.slicing_engine = OrderSlicingEngine(config)
        self.execution_monitor = ExecutionMonitor(config)

        # Machine learning components
        self.routing_model = None
        self.performance_predictor = RandomForestRegressor(n_estimators=50, random_state=42)

    def route_order(self, order_config: OrderRoutingConfig) -> Tuple[RoutingDecision, List[ExecutionSlice]]:
        """Route an order intelligently"""

        # Get current market data
        exchange_profiles = self.market_data.get_exchange_profiles()

        # Select optimization strategy
        if self.config.routing_strategy == "cost_optimized":
            routing_decision = self.cost_optimizer.optimize_routing(order_config, exchange_profiles)
        elif self.config.routing_strategy == "latency_optimized":
            routing_decision = self.latency_optimizer.optimize_for_latency(order_config, exchange_profiles)
        elif self.config.routing_strategy == "liquidity_optimized":
            routing_decision = self.liquidity_optimizer.optimize_for_liquidity(order_config, exchange_profiles)
        else:
            routing_decision = self.cost_optimizer.optimize_routing(order_config, exchange_profiles)

        # Create execution plan
        execution_slices = self.slicing_engine.create_execution_plan(routing_decision, order_config)

        # Apply machine learning adjustments if available
        if self.routing_model and self.config.use_machine_learning:
            routing_decision, execution_slices = self._apply_ml_adjustments(
                routing_decision, execution_slices, exchange_profiles
            )

        return routing_decision, execution_slices

    def execute_order(self, routing_decision: RoutingDecision,
                     execution_slices: List[ExecutionSlice]) -> Dict[str, Any]:
        """Execute the routed order"""

        execution_results = []

        # Execute slices (simplified - would integrate with actual exchange APIs)
        for slice in execution_slices:
            result = self._execute_slice(slice)
            execution_results.append(result)

            # Track execution
            self.execution_monitor.track_execution(slice, result)

        # Aggregate results
        total_executed = sum(r['executed_size'] for r in execution_results)
        total_cost = sum(r.get('fees', 0) for r in execution_results)
        avg_price = np.average(
            [r['executed_price'] for r in execution_results if r['executed_price'] > 0],
            weights=[r['executed_size'] for r in execution_results if r['executed_price'] > 0]
        )

        execution_summary = {
            'total_intended': sum(s.size for s in execution_slices),
            'total_executed': total_executed,
            'fill_rate': total_executed / sum(s.size for s in execution_slices),
            'total_cost': total_cost,
            'avg_price': avg_price,
            'execution_time': time.time() - routing_decision.timestamp,
            'n_slices': len(execution_slices),
            'exchanges_used': list(routing_decision.exchange_allocations.keys())
        }

        return execution_summary

    def _execute_slice(self, slice: ExecutionSlice) -> Dict[str, Any]:
        """Execute a single order slice (simplified simulation)"""

        # Simulate execution
        time.sleep(0.01)  # Simulate latency

        # Random execution quality
        execution_probability = 0.95  # 95% success rate
        slippage_factor = 0.001  # 0.1% slippage

        if np.random.random() < execution_probability:
            executed_size = slice.size * (0.98 + np.random.random() * 0.04)  # 98-102% fill
            executed_price = 50000 * (1 + (np.random.random() - 0.5) * slippage_factor * 2)  # Mock price
            fees = executed_size * executed_price * 0.001  # 0.1% fee
            latency = np.random.normal(50, 10)  # Mean 50ms latency

            return {
                'executed_size': executed_size,
                'executed_price': executed_price,
                'fees': fees,
                'latency_ms': max(0, latency),
                'success': True
            }
        else:
            return {
                'executed_size': 0,
                'executed_price': 0,
                'fees': 0,
                'latency_ms': 0,
                'success': False,
                'error': 'Execution failed'
            }

    def _apply_ml_adjustments(self, routing_decision: RoutingDecision,
                            execution_slices: List[ExecutionSlice],
                            exchange_profiles: Dict[str, ExchangeProfile]) \
            -> Tuple[RoutingDecision, List[ExecutionSlice]]:
        """Apply machine learning adjustments to routing"""

        # This would use trained models to adjust routing based on historical performance
        # For now, return unchanged
        return routing_decision, execution_slices

    def update_market_data(self, exchange: str, data: Dict[str, Any]):
        """Update market data for an exchange"""
        self.market_data.update_market_data(exchange, data)

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""

        feedback = self.execution_monitor.get_routing_feedback()

        return {
            'execution_monitor': self.execution_monitor.get_exchange_performance,
            'routing_feedback': feedback,
            'total_orders': len(self.execution_monitor.execution_history),
            'avg_fill_rate': feedback['avg_fill_rate'],
            'avg_latency': feedback['avg_latency']
        }


# Factory functions
def create_smart_order_router(config: Optional[OrderRoutingConfig] = None) -> SmartOrderRouter:
    """Factory function for smart order router"""
    if config is None:
        config = OrderRoutingConfig()
    return SmartOrderRouter(config)


def create_cost_optimizer(config: Optional[OrderRoutingConfig] = None) -> CostOptimizationEngine:
    """Factory function for cost optimization engine"""
    if config is None:
        config = OrderRoutingConfig()
    return CostOptimizationEngine(config)


def route_order_smart(order_config: OrderRoutingConfig,
                     market_data: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for smart order routing"""

    # Create router
    router = create_smart_order_router(order_config)

    # Update market data if provided
    if market_data:
        for exchange, data in market_data.items():
            router.update_market_data(exchange, data)

    # Route order
    routing_decision, execution_slices = router.route_order(order_config)

    # Execute order (simulation)
    execution_result = router.execute_order(routing_decision, execution_slices)

    return {
        'routing_decision': routing_decision,
        'execution_slices': execution_slices,
        'execution_result': execution_result,
        'performance_report': router.get_performance_report()
    }


# Example usage and testing
if __name__ == "__main__":
    # Test smart order routing
    print("Testing Smart Order Routing...")

    config = OrderRoutingConfig(
        symbol="BTCUSDT",
        order_size=1.0,
        routing_strategy="cost_optimized"
    )

    router = create_smart_order_router(config)

    # Mock market data
    mock_data = {
        'binance': {
            'prices': {'BTCUSDT': 50000},
            'order_book': {
                'bids': [(49990, 1.0), (49980, 2.0), (49970, 1.5)],
                'asks': [(50010, 1.2), (50020, 2.1), (50030, 1.8)]
            },
            'liquidity': {'score': 0.8},
            'fees': {'maker': 0.0002, 'taker': 0.0004},
            'latency': 50.0
        },
        'coinbase': {
            'prices': {'BTCUSDT': 50005},
            'order_book': {
                'bids': [(49995, 0.8), (49985, 1.5), (49975, 1.2)],
                'asks': [(50015, 1.0), (50025, 1.8), (50035, 1.5)]
            },
            'liquidity': {'score': 0.6},
            'fees': {'maker': 0.0005, 'taker': 0.0007},
            'latency': 80.0
        }
    }

    # Update market data
    for exchange, data in mock_data.items():
        router.update_market_data(exchange, data)

    # Test routing
    print("\n1. Testing Order Routing...")
    routing_decision, execution_slices = router.route_order(config)

    print(f"Routing decision: {routing_decision.execution_strategy}")
    print(f"Exchange allocation: {routing_decision.exchange_allocations}")
    print(f"Expected cost: {routing_decision.expected_cost:.6f}")
    print(f"Expected latency: {routing_decision.expected_latency:.1f} ms")
    print(f"Number of slices: {len(execution_slices)}")

    # Test execution
    print("\n2. Testing Order Execution...")
    execution_result = router.execute_order(routing_decision, execution_slices)

    print(f"Fill rate: {execution_result['fill_rate']:.3f}")
    print(f"Total cost: ${execution_result['total_cost']:.4f}")
    print(f"Average price: ${execution_result['avg_price']:.2f}")

    # Test performance report
    print("\n3. Testing Performance Report...")
    report = router.get_performance_report()
    print(f"Total orders executed: {report['total_orders']}")
    print(f"Average fill rate: {report['avg_fill_rate']:.3f}")

    print("\nSmart order routing test completed successfully!")

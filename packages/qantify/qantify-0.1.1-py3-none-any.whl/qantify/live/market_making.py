"""
Advanced Market Making Algorithms for High-Frequency Trading
===========================================================

This module implements sophisticated market making strategies for automated liquidity provision.
Includes inventory management, risk controls, price discovery, and adaptive spread management.

Key Features:
- Dynamic inventory management with risk limits
- Adaptive spread calculation based on market conditions
- Price discovery algorithms using order book analysis
- Risk-adjusted quoting strategies
- Market microstructure awareness
- High-frequency trading capabilities
- Real-time performance monitoring
- Circuit breakers and safety mechanisms
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
from sklearn.ensemble import RandomForestRegressor

# Import existing Qantify modules
try:
    from ..math.stochastic import BrownianMotion, GeometricBrownianMotion
    from ..math.volatility import SABRCalibrator
    from ..risk_models import LedoitWolfShrinkage
    from ..signals.indicators import rsi, bollinger_bands, exponential_moving_average
except ImportError:
    pass


@dataclass
class MarketMakingConfig:
    """Configuration for market making strategies"""

    # Core parameters
    symbol: str = "BTCUSDT"
    base_currency: str = "BTC"
    quote_currency: str = "USDT"

    # Inventory management
    max_inventory: float = 100.0  # Maximum position size
    target_inventory: float = 0.0  # Target neutral position
    inventory_rebalance_threshold: float = 10.0

    # Spread management
    base_spread_bps: float = 2.0  # Base spread in basis points
    min_spread_bps: float = 0.5
    max_spread_bps: float = 10.0
    spread_adjustment_factor: float = 0.1

    # Risk management
    max_drawdown_pct: float = 5.0
    position_limit_pct: float = 10.0
    volatility_multiplier: float = 2.0

    # Order management
    max_orders_per_side: int = 5
    order_refresh_interval: float = 1.0  # seconds
    order_lifetime: float = 30.0  # seconds

    # Market microstructure
    order_book_depth: int = 10
    min_order_size: float = 0.001
    max_order_size: float = 10.0

    # Performance tracking
    pnl_tracking: bool = True
    inventory_tracking: bool = True
    spread_tracking: bool = True

    # Safety mechanisms
    circuit_breaker_enabled: bool = True
    max_gap_pct: float = 2.0  # Maximum allowed price gap
    emergency_stop_loss: float = 0.05


@dataclass
class InventoryPosition:
    """Current inventory position and P&L"""

    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    timestamp: float = 0.0

    @property
    def total_pnl(self) -> float:
        """Total P&L including unrealized"""
        return self.realized_pnl + self.unrealized_pnl

    def update_unrealized_pnl(self, current_price: float):
        """Update unrealized P&L based on current price"""
        if self.quantity != 0:
            self.unrealized_pnl = self.quantity * (current_price - self.avg_price)
        else:
            self.unrealized_pnl = 0.0


@dataclass
class OrderBookSnapshot:
    """Snapshot of order book for analysis"""

    timestamp: float
    bids: List[Tuple[float, float]]  # (price, size) tuples
    asks: List[Tuple[float, float]]  # (price, size) tuples

    @property
    def best_bid(self) -> float:
        """Best bid price"""
        return self.bids[0][0] if self.bids else 0.0

    @property
    def best_ask(self) -> float:
        """Best ask price"""
        return self.asks[0][0] if self.asks else float('inf')

    @property
    def mid_price(self) -> float:
        """Mid price"""
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return (self.best_bid + self.best_ask) / 2.0
        return 0.0

    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return self.best_ask - self.best_bid
        return 0.0

    @property
    def spread_bps(self) -> float:
        """Spread in basis points"""
        if self.mid_price > 0:
            return (self.spread / self.mid_price) * 10000
        return 0.0


@dataclass
class MarketMakingSignal:
    """Signal for market making actions"""

    timestamp: float
    action: str  # "quote", "cancel", "adjust", "pause"
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    reason: str = ""
    confidence: float = 0.0


class InventoryManager:
    """Advanced inventory management for market making"""

    def __init__(self, config: MarketMakingConfig):
        self.config = config
        self.position = InventoryPosition(config.symbol)
        self.trade_history = deque(maxlen=1000)
        self.inventory_history = deque(maxlen=1000)

    def update_position(self, trade_quantity: float, trade_price: float, timestamp: float):
        """Update position after a trade"""

        # Record trade
        self.trade_history.append({
            'quantity': trade_quantity,
            'price': trade_price,
            'timestamp': timestamp
        })

        # Update position
        if self.position.quantity == 0:
            # New position
            self.position.quantity = trade_quantity
            self.position.avg_price = trade_price
        else:
            # Average price update
            total_quantity = self.position.quantity + trade_quantity
            if total_quantity != 0:
                self.position.avg_price = (
                    (self.position.quantity * self.position.avg_price) +
                    (trade_quantity * trade_price)
                ) / total_quantity

            self.position.quantity = total_quantity

        self.position.timestamp = timestamp
        self.inventory_history.append({
            'quantity': self.position.quantity,
            'avg_price': self.position.avg_price,
            'timestamp': timestamp
        })

    def get_inventory_score(self) -> float:
        """Calculate inventory deviation score (-1 to 1)"""
        if self.config.max_inventory == 0:
            return 0.0

        deviation = self.position.quantity - self.config.target_inventory
        max_deviation = self.config.max_inventory

        return max(-1.0, min(1.0, deviation / max_deviation))

    def should_rebalance(self) -> bool:
        """Check if inventory rebalancing is needed"""
        inventory_score = abs(self.get_inventory_score())
        return inventory_score > (self.config.inventory_rebalance_threshold / self.config.max_inventory)

    def get_rebalance_signal(self) -> Tuple[str, float]:
        """Get rebalancing signal"""
        inventory_score = self.get_inventory_score()

        if inventory_score > 0.5:
            # Overbought - sell
            return "sell", abs(inventory_score)
        elif inventory_score < -0.5:
            # Oversold - buy
            return "buy", abs(inventory_score)
        else:
            return "hold", 0.0

    def get_inventory_adjustment_factor(self) -> float:
        """Get adjustment factor based on inventory"""
        inventory_score = abs(self.get_inventory_score())
        return 1.0 + (inventory_score * 0.5)  # Increase spread when inventory is high


class SpreadCalculator:
    """Dynamic spread calculation based on market conditions"""

    def __init__(self, config: MarketMakingConfig):
        self.config = config
        self.price_history = deque(maxlen=100)
        self.spread_history = deque(maxlen=100)
        self.volatility_estimator = None

    def calculate_optimal_spread(self, order_book: OrderBookSnapshot,
                               inventory_score: float, market_volatility: float) -> float:
        """Calculate optimal bid-ask spread"""

        # Base spread
        spread_bps = self.config.base_spread_bps

        # Inventory adjustment
        inventory_factor = 1.0 + abs(inventory_score) * self.config.spread_adjustment_factor
        spread_bps *= inventory_factor

        # Volatility adjustment
        volatility_factor = 1.0 + market_volatility * self.config.volatility_multiplier
        spread_bps *= volatility_factor

        # Order book imbalance adjustment
        imbalance_factor = self._calculate_order_book_imbalance(order_book)
        spread_bps *= (1.0 + imbalance_factor * 0.2)

        # Market microstructure adjustment
        microstructure_factor = self._calculate_microstructure_factor(order_book)
        spread_bps *= microstructure_factor

        # Constrain spread
        spread_bps = max(self.config.min_spread_bps, min(self.config.max_spread_bps, spread_bps))

        return spread_bps / 10000.0  # Convert to decimal

    def _calculate_order_book_imbalance(self, order_book: OrderBookSnapshot) -> float:
        """Calculate order book imbalance"""
        total_bid_volume = sum(size for _, size in order_book.bids[:5])
        total_ask_volume = sum(size for _, size in order_book.asks[:5])

        if total_bid_volume + total_ask_volume > 0:
            imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
            return imbalance
        return 0.0

    def _calculate_microstructure_factor(self, order_book: OrderBookSnapshot) -> float:
        """Calculate market microstructure factor"""

        # Spread factor
        spread_factor = order_book.spread_bps / self.config.base_spread_bps

        # Depth factor
        bid_depth = sum(size for _, size in order_book.bids[:3])
        ask_depth = sum(size for _, size in order_book.asks[:3])
        avg_depth = (bid_depth + ask_depth) / 2.0

        # Assume minimum depth of 1 for calculation
        depth_factor = 1.0 / max(1.0, avg_depth / 10.0)

        return (spread_factor + depth_factor) / 2.0


class PriceDiscoveryEngine:
    """Price discovery using order book analysis and ML"""

    def __init__(self, config: MarketMakingConfig):
        self.config = config
        self.order_book_history = deque(maxlen=100)
        self.price_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False

    def analyze_order_book(self, order_book: OrderBookSnapshot) -> Dict[str, float]:
        """Analyze order book for price discovery signals"""

        # Store order book
        self.order_book_history.append(order_book)

        # Calculate order book features
        features = self._extract_order_book_features(order_book)

        # Price direction prediction
        price_direction = self._predict_price_direction(features)

        # Fair value estimation
        fair_value = self._estimate_fair_value(order_book)

        # Confidence calculation
        confidence = self._calculate_confidence(order_book)

        return {
            'fair_value': fair_value,
            'price_direction': price_direction,
            'confidence': confidence,
            'features': features
        }

    def _extract_order_book_features(self, order_book: OrderBookSnapshot) -> Dict[str, float]:
        """Extract features from order book"""

        features = {}

        # Basic statistics
        features['spread_bps'] = order_book.spread_bps
        features['mid_price'] = order_book.mid_price

        # Volume-weighted average prices
        bid_vwap = self._calculate_vwap(order_book.bids[:5])
        ask_vwap = self._calculate_vwap(order_book.asks[:5])

        features['bid_vwap'] = bid_vwap
        features['ask_vwap'] = ask_vwap

        # Order book slope (price vs cumulative volume)
        bid_slope = self._calculate_order_book_slope(order_book.bids[:5])
        ask_slope = self._calculate_order_book_slope(order_book.asks[:5])

        features['bid_slope'] = bid_slope
        features['ask_slope'] = ask_slope

        # Depth ratios
        bid_depth_5 = sum(size for _, size in order_book.bids[:5])
        ask_depth_5 = sum(size for _, size in order_book.asks[:5])

        features['depth_ratio'] = bid_depth_5 / max(ask_depth_5, 0.001)

        return features

    def _calculate_vwap(self, orders: List[Tuple[float, float]]) -> float:
        """Calculate volume-weighted average price"""
        if not orders:
            return 0.0

        total_volume = sum(size for _, size in orders)
        if total_volume == 0:
            return 0.0

        weighted_sum = sum(price * size for price, size in orders)
        return weighted_sum / total_volume

    def _calculate_order_book_slope(self, orders: List[Tuple[float, float]]) -> float:
        """Calculate order book slope using linear regression"""
        if len(orders) < 2:
            return 0.0

        # Cumulative volume vs price
        prices = [price for price, _ in orders]
        volumes = [size for _, size in orders]
        cum_volume = np.cumsum(volumes)

        # Linear regression
        try:
            slope, _ = np.polyfit(cum_volume, prices, 1)
            return slope
        except:
            return 0.0

    def _predict_price_direction(self, features: Dict[str, float]) -> float:
        """Predict short-term price direction (-1 to 1)"""

        # Simple rule-based prediction
        spread_change = features.get('spread_bps', 0) / self.config.base_spread_bps
        depth_ratio = features.get('depth_ratio', 1.0)

        # High spread + imbalanced depth suggests price movement
        direction_signal = 0.0

        if spread_change > 1.5:  # Wide spread
            if depth_ratio > 1.5:  # More bids than asks
                direction_signal = -0.3  # Expect price down
            elif depth_ratio < 0.67:  # More asks than bids
                direction_signal = 0.3   # Expect price up

        # Slope-based signal
        slope_diff = features.get('ask_slope', 0) - features.get('bid_slope', 0)
        slope_signal = np.tanh(slope_diff * 1000)  # Normalize

        return (direction_signal + slope_signal) / 2.0

    def _estimate_fair_value(self, order_book: OrderBookSnapshot) -> float:
        """Estimate fair value using order book analysis"""

        # Volume-weighted mid price
        bid_vwap = self._calculate_vwap(order_book.bids[:10])
        ask_vwap = self._calculate_vwap(order_book.asks[:10])

        if bid_vwap > 0 and ask_vwap > 0:
            return (bid_vwap + ask_vwap) / 2.0
        else:
            return order_book.mid_price

    def _calculate_confidence(self, order_book: OrderBookSnapshot) -> float:
        """Calculate confidence in price discovery"""

        # Based on order book depth and spread
        depth_score = min(1.0, (len(order_book.bids) + len(order_book.asks)) / 20.0)
        spread_score = max(0.0, 1.0 - (order_book.spread_bps / self.config.max_spread_bps))

        return (depth_score + spread_score) / 2.0


class MarketMakingStrategy:
    """Core market making strategy implementation"""

    def __init__(self, config: MarketMakingConfig):
        self.config = config

        # Initialize components
        self.inventory_manager = InventoryManager(config)
        self.spread_calculator = SpreadCalculator(config)
        self.price_discovery = PriceDiscoveryEngine(config)

        # State tracking
        self.current_orders = {'bids': [], 'asks': []}
        self.last_quote_time = 0.0
        self.is_active = True

        # Performance tracking
        self.performance_history = deque(maxlen=1000)

    def generate_signal(self, order_book: OrderBookSnapshot,
                       market_data: Dict[str, Any]) -> MarketMakingSignal:
        """Generate market making signal"""

        timestamp = time.time()

        # Check emergency conditions
        if self._check_emergency_conditions(order_book, market_data):
            return MarketMakingSignal(
                timestamp=timestamp,
                action="pause",
                reason="Emergency conditions detected"
            )

        # Check if we need to refresh quotes
        if timestamp - self.last_quote_time < self.config.order_refresh_interval:
            return MarketMakingSignal(
                timestamp=timestamp,
                action="hold",
                reason="Waiting for refresh interval"
            )

        # Update inventory
        self._update_inventory_from_market_data(market_data)

        # Check inventory rebalancing
        if self.inventory_manager.should_rebalance():
            rebalance_action, intensity = self.inventory_manager.get_rebalance_signal()
            return MarketMakingSignal(
                timestamp=timestamp,
                action="rebalance",
                reason=f"Inventory rebalancing: {rebalance_action}",
                confidence=intensity
            )

        # Analyze market conditions
        inventory_score = self.inventory_manager.get_inventory_score()
        market_volatility = market_data.get('volatility', 0.02)

        # Calculate optimal spread
        optimal_spread = self.spread_calculator.calculate_optimal_spread(
            order_book, inventory_score, market_volatility
        )

        # Price discovery
        price_analysis = self.price_discovery.analyze_order_book(order_book)

        # Calculate quote prices
        mid_price = price_analysis['fair_value']
        if mid_price <= 0:
            mid_price = order_book.mid_price

        half_spread = optimal_spread / 2.0
        bid_price = mid_price * (1.0 - half_spread)
        ask_price = mid_price * (1.0 + half_spread)

        # Adjust for price direction
        price_adjustment = price_analysis['price_direction'] * (optimal_spread * 0.1)
        bid_price -= price_adjustment * mid_price
        ask_price -= price_adjustment * mid_price

        # Calculate order sizes
        base_size = self._calculate_order_size(order_book, inventory_score)
        bid_size = ask_size = base_size

        # Adjust sizes based on inventory
        if inventory_score > 0:
            # Too much inventory, reduce bid size, increase ask size
            bid_size *= (1.0 - inventory_score * 0.5)
            ask_size *= (1.0 + inventory_score * 0.5)
        elif inventory_score < 0:
            # Too little inventory, increase bid size, reduce ask size
            bid_size *= (1.0 + abs(inventory_score) * 0.5)
            ask_size *= (1.0 - abs(inventory_score) * 0.5)

        # Constrain order sizes
        bid_size = max(self.config.min_order_size, min(self.config.max_order_size, bid_size))
        ask_size = max(self.config.min_order_size, min(self.config.max_order_size, ask_size))

        self.last_quote_time = timestamp

        return MarketMakingSignal(
            timestamp=timestamp,
            action="quote",
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=bid_size,
            ask_size=ask_size,
            reason="Regular market making",
            confidence=price_analysis['confidence']
        )

    def _check_emergency_conditions(self, order_book: OrderBookSnapshot,
                                  market_data: Dict[str, Any]) -> bool:
        """Check for emergency conditions that require pausing"""

        if not self.config.circuit_breaker_enabled:
            return False

        # Check price gap
        if order_book.spread_bps > self.config.max_gap_pct * 100:
            return True

        # Check volatility
        volatility = market_data.get('volatility', 0.0)
        if volatility > self.config.emergency_stop_loss:
            return True

        # Check drawdown
        current_pnl = self.inventory_manager.position.total_pnl
        if current_pnl < -self.config.max_drawdown_pct:
            return True

        return False

    def _update_inventory_from_market_data(self, market_data: Dict[str, Any]):
        """Update inventory from market data"""
        # This would be implemented to track actual trades
        # For now, placeholder
        pass

    def _calculate_order_size(self, order_book: OrderBookSnapshot, inventory_score: float) -> float:
        """Calculate optimal order size"""

        # Base size based on order book depth
        avg_depth = (sum(size for _, size in order_book.bids[:3]) +
                    sum(size for _, size in order_book.asks[:3])) / 6.0

        base_size = min(avg_depth * 0.1, self.config.max_order_size)

        # Adjust based on inventory
        inventory_factor = 1.0 - abs(inventory_score) * 0.3
        base_size *= inventory_factor

        return max(self.config.min_order_size, base_size)

    def update_performance(self, pnl: float, timestamp: float):
        """Update performance tracking"""

        self.performance_history.append({
            'pnl': pnl,
            'inventory': self.inventory_manager.position.quantity,
            'timestamp': timestamp
        })

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""

        if not self.performance_history:
            return {}

        pnl_values = [entry['pnl'] for entry in self.performance_history]
        inventory_values = [entry['inventory'] for entry in self.performance_history]

        return {
            'total_pnl': pnl_values[-1] if pnl_values else 0.0,
            'avg_inventory': np.mean(inventory_values),
            'inventory_volatility': np.std(inventory_values),
            'sharpe_ratio': self._calculate_sharpe_ratio(pnl_values),
            'max_drawdown': self._calculate_max_drawdown(pnl_values)
        }

    def _calculate_sharpe_ratio(self, pnl_values: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if len(pnl_values) < 2:
            return 0.0

        returns = np.diff(pnl_values)
        if len(returns) == 0:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        return np.sqrt(252) * mean_return / std_return

    def _calculate_max_drawdown(self, pnl_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not pnl_values:
            return 0.0

        cumulative = np.maximum.accumulate(pnl_values)
        drawdown = (cumulative - pnl_values) / np.maximum(cumulative, 1e-10)
        return np.max(drawdown)


class AdaptiveMarketMaker:
    """Adaptive market maker with learning capabilities"""

    def __init__(self, config: MarketMakingConfig):
        self.config = config
        self.strategy = MarketMakingStrategy(config)

        # Learning components
        self.performance_model = RandomForestRegressor(n_estimators=20, random_state=42)
        self.parameter_optimizer = None

        # Adaptation history
        self.parameter_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=100)

    def run_market_making_cycle(self, order_book: OrderBookSnapshot,
                               market_data: Dict[str, Any]) -> MarketMakingSignal:
        """Run one market making cycle"""

        # Generate signal
        signal = self.strategy.generate_signal(order_book, market_data)

        # Adapt parameters if needed
        if len(self.performance_history) > 10:
            self._adapt_parameters()

        return signal

    def _adapt_parameters(self):
        """Adapt strategy parameters based on performance"""

        # Simple parameter adaptation
        recent_performance = list(self.performance_history)[-10:]
        avg_performance = np.mean(recent_performance)

        # Adjust spread based on performance
        if avg_performance > 0:
            # Good performance, can tighten spread
            self.config.base_spread_bps *= 0.99
        else:
            # Poor performance, widen spread
            self.config.base_spread_bps *= 1.01

        # Constrain spread
        self.config.base_spread_bps = max(
            self.config.min_spread_bps,
            min(self.config.max_spread_bps, self.config.base_spread_bps)
        )

    def update_learning(self, signal: MarketMakingSignal, outcome: Dict[str, Any]):
        """Update learning from signal outcomes"""

        # Record parameter state
        self.parameter_history.append({
            'spread_bps': self.config.base_spread_bps,
            'timestamp': signal.timestamp
        })

        # Record performance outcome
        performance = outcome.get('realized_pnl', 0.0)
        self.performance_history.append(performance)


# Factory functions
def create_market_making_strategy(config: Optional[MarketMakingConfig] = None) -> MarketMakingStrategy:
    """Factory function for market making strategy"""
    if config is None:
        config = MarketMakingConfig()
    return MarketMakingStrategy(config)


def create_adaptive_market_maker(config: Optional[MarketMakingConfig] = None) -> AdaptiveMarketMaker:
    """Factory function for adaptive market maker"""
    if config is None:
        config = MarketMakingConfig()
    return AdaptiveMarketMaker(config)


def create_inventory_manager(config: Optional[MarketMakingConfig] = None) -> InventoryManager:
    """Factory function for inventory manager"""
    if config is None:
        config = MarketMakingConfig()
    return InventoryManager(config)


# Example usage and testing
if __name__ == "__main__":
    # Test market making components
    print("Testing Market Making Components...")

    config = MarketMakingConfig()

    # Test inventory manager
    print("\n1. Testing Inventory Manager...")
    inventory_mgr = create_inventory_manager(config)
    inventory_mgr.update_position(10.0, 50000.0, time.time())
    inventory_mgr.update_position(-5.0, 51000.0, time.time())

    print(f"Current position: {inventory_mgr.position.quantity}")
    print(f"Inventory score: {inventory_mgr.get_inventory_score()}")
    print(f"Should rebalance: {inventory_mgr.should_rebalance()}")

    # Test spread calculator
    print("\n2. Testing Spread Calculator...")
    spread_calc = SpreadCalculator(config)

    # Create mock order book
    order_book = OrderBookSnapshot(
        timestamp=time.time(),
        bids=[(49990, 1.0), (49980, 2.0), (49970, 1.5)],
        asks=[(50010, 1.2), (50020, 2.1), (50030, 1.8)]
    )

    optimal_spread = spread_calc.calculate_optimal_spread(order_book, 0.0, 0.02)
    print(f"Optimal spread: {optimal_spread:.6f}")
    print(f"Order book spread: {order_book.spread_bps:.2f} bps")

    # Test price discovery
    print("\n3. Testing Price Discovery...")
    price_engine = PriceDiscoveryEngine(config)
    analysis = price_engine.analyze_order_book(order_book)

    print(f"Fair value estimate: ${analysis['fair_value']:.2f}")
    print(f"Price direction: {analysis['price_direction']:.3f}")
    print(f"Confidence: {analysis['confidence']:.3f}")

    # Test market making strategy
    print("\n4. Testing Market Making Strategy...")
    strategy = create_market_making_strategy(config)
    market_data = {'volatility': 0.02}

    signal = strategy.generate_signal(order_book, market_data)
    print(f"Signal action: {signal.action}")
    if signal.action == "quote":
        print(f"Bid: ${signal.bid_price:.2f} ({signal.bid_size:.3f})")
        print(f"Ask: ${signal.ask_price:.2f} ({signal.ask_size:.3f})")

    print("\nMarket making components test completed successfully!")

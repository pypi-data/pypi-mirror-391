"""Order book analytics and limit order book modeling."""

from __future__ import annotations

import warnings
import json
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    sm = None

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    RandomForestRegressor = None
    GradientBoostingClassifier = None
    StandardScaler = None
    TimeSeriesSplit = None


@dataclass
class OrderBookSnapshot:
    """Snapshot of the limit order book at a point in time"""

    timestamp: float
    symbol: str

    # Bid side (price, quantity pairs)
    bids: List[Tuple[float, int]] = field(default_factory=list)

    # Ask side (price, quantity pairs)
    asks: List[Tuple[float, int]] = field(default_factory=list)

    # Market statistics
    spread: float = 0.0
    mid_price: float = 0.0
    bid_depth: int = 0
    ask_depth: int = 0

    # Imbalance metrics
    order_imbalance: float = 0.0
    volume_imbalance: float = 0.0

    @property
    def best_bid(self) -> Optional[float]:
        """Get best bid price"""
        return self.bids[0][0] if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        """Get best ask price"""
        return self.asks[0][0] if self.asks else None

    @property
    def spread_bps(self) -> float:
        """Get spread in basis points"""
        if self.best_bid and self.best_ask and self.mid_price > 0:
            return ((self.best_ask - self.best_bid) / self.mid_price) * 10000
        return 0.0

    @property
    def market_depth(self) -> Dict[str, int]:
        """Get market depth statistics"""
        return {
            'bid_orders': len(self.bids),
            'ask_orders': len(self.asks),
            'total_orders': len(self.bids) + len(self.asks),
            'bid_volume': sum(qty for _, qty in self.bids),
            'ask_volume': sum(qty for _, qty in self.asks)
        }


@dataclass
class OrderFlowEvent:
    """An order flow event (market or limit order)"""

    timestamp: float
    symbol: str
    order_type: str  # "market_buy", "market_sell", "limit_buy", "limit_sell"

    # Order details
    price: float
    quantity: int
    order_id: str = ""

    # Execution details
    executed_quantity: int = 0
    remaining_quantity: int = 0

    # Market context
    best_bid_before: Optional[float] = None
    best_ask_before: Optional[float] = None
    spread_before: float = 0.0

    @property
    def is_market_order(self) -> bool:
        """Check if this is a market order"""
        return "market" in self.order_type

    @property
    def is_buy_order(self) -> bool:
        """Check if this is a buy order"""
        return "buy" in self.order_type

    @property
    def price_impact(self) -> float:
        """Calculate price impact if applicable"""
        if self.best_bid_before and self.best_ask_before and self.price > 0:
            mid_before = (self.best_bid_before + self.best_ask_before) / 2
            return (self.price - mid_before) / mid_before
        return 0.0


@dataclass
class LOBModelConfig:
    """Configuration for limit order book modeling"""

    # Model parameters
    model_type: str = "queue_aware"  # "queue_aware", "zero_intelligence", "sequential"

    # Queue modeling
    queue_decay_factor: float = 0.95
    max_queue_length: int = 10

    # Price modeling
    tick_size: float = 0.01
    price_levels: int = 5

    # Time modeling
    time_horizon: float = 1.0  # seconds
    temporal_decay: float = 0.9

    # Risk modeling
    volatility_estimation_window: int = 100
    jump_probability: float = 0.01


class LimitOrderBook:
    """Limit Order Book implementation with advanced analytics"""

    def __init__(self, symbol: str, max_levels: int = 10):
        self.symbol = symbol
        self.max_levels = max_levels

        # Order book state
        self.bids = []  # List of (price, quantity) tuples, sorted descending
        self.asks = []  # List of (price, quantity) tuples, sorted ascending

        # Historical data
        self.snapshots = deque(maxlen=1000)
        self.order_flow = deque(maxlen=10000)

        # Analytics
        self.spread_history = deque(maxlen=1000)
        self.mid_price_history = deque(maxlen=1000)
        self.imbalance_history = deque(maxlen=1000)

    def update_order_book(self, bids: List[Tuple[float, int]],
                         asks: List[Tuple[float, int]], timestamp: float):
        """Update the order book with new bid/ask data"""

        self.bids = sorted(bids, key=lambda x: -x[0])[:self.max_levels]  # Highest first
        self.asks = sorted(asks, key=lambda x: x[0])[:self.max_levels]   # Lowest first

        # Create snapshot
        snapshot = OrderBookSnapshot(
            timestamp=timestamp,
            symbol=self.symbol,
            bids=self.bids.copy(),
            asks=self.asks.copy()
        )

        # Calculate market statistics
        snapshot.mid_price = self._calculate_mid_price()
        snapshot.spread = self._calculate_spread()
        snapshot.bid_depth = sum(qty for _, qty in self.bids)
        snapshot.ask_depth = sum(qty for _, qty in self.asks)

        # Calculate imbalances
        snapshot.order_imbalance = self._calculate_order_imbalance()
        snapshot.volume_imbalance = self._calculate_volume_imbalance()

        # Store snapshot
        self.snapshots.append(snapshot)

        # Update history
        self.spread_history.append(snapshot.spread)
        self.mid_price_history.append(snapshot.mid_price)
        self.imbalance_history.append(snapshot.order_imbalance)

    def add_order_flow(self, event: OrderFlowEvent):
        """Add an order flow event"""

        self.order_flow.append(event)

        # Update order book based on execution
        if event.is_market_order:
            self._process_market_order(event)

    def get_current_snapshot(self) -> Optional[OrderBookSnapshot]:
        """Get the current order book snapshot"""
        return self.snapshots[-1] if self.snapshots else None

    def get_order_book_depth(self, levels: int = 5) -> Dict[str, List[Tuple[float, int]]]:
        """Get order book depth for specified number of levels"""

        return {
            'bids': self.bids[:levels],
            'asks': self.asks[:levels]
        }

    def calculate_liquidity_metrics(self) -> Dict[str, float]:
        """Calculate liquidity metrics"""

        if not self.snapshots:
            return {}

        current = self.snapshots[-1]

        # Depth metrics
        bid_depth = sum(qty for _, qty in self.bids)
        ask_depth = sum(qty for _, qty in self.asks)

        # Spread metrics
        avg_spread = np.mean(list(self.spread_history))
        spread_volatility = np.std(list(self.spread_history))

        # Imbalance metrics
        avg_imbalance = np.mean(list(self.imbalance_history))

        # Market quality metrics
        market_quality = self._calculate_market_quality()

        return {
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'total_depth': bid_depth + ask_depth,
            'depth_imbalance': (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0,
            'average_spread': avg_spread,
            'spread_volatility': spread_volatility,
            'average_imbalance': avg_imbalance,
            'market_quality_score': market_quality
        }

    def analyze_order_flow(self, window: int = 100) -> Dict[str, Any]:
        """Analyze recent order flow"""

        if len(self.order_flow) < window:
            return {}

        recent_orders = list(self.order_flow)[-window:]

        # Classify orders
        market_buy_orders = [o for o in recent_orders if o.order_type == "market_buy"]
        market_sell_orders = [o for o in recent_orders if o.order_type == "market_sell"]
        limit_buy_orders = [o for o in recent_orders if o.order_type == "limit_buy"]
        limit_sell_orders = [o for o in recent_orders if o.order_type == "limit_sell"]

        # Volume analysis
        total_market_volume = sum(o.quantity for o in market_buy_orders + market_sell_orders)
        total_limit_volume = sum(o.quantity for o in limit_buy_orders + limit_sell_orders)

        # Order imbalance
        market_buy_volume = sum(o.quantity for o in market_buy_orders)
        market_sell_volume = sum(o.quantity for o in market_sell_orders)
        market_imbalance = (market_buy_volume - market_sell_volume) / (market_buy_volume + market_sell_volume) if (market_buy_volume + market_sell_volume) > 0 else 0

        # Execution analysis
        avg_execution_time = np.mean([o.executed_quantity / max(o.quantity, 1) for o in recent_orders if o.quantity > 0])

        return {
            'total_orders': len(recent_orders),
            'market_orders': len(market_buy_orders) + len(market_sell_orders),
            'limit_orders': len(limit_buy_orders) + len(limit_sell_orders),
            'market_buy_volume': market_buy_volume,
            'market_sell_volume': market_sell_volume,
            'limit_buy_volume': sum(o.quantity for o in limit_buy_orders),
            'limit_sell_volume': sum(o.quantity for o in limit_sell_orders),
            'market_imbalance': market_imbalance,
            'avg_execution_ratio': avg_execution_time,
            'order_intensity': len(recent_orders) / window
        }

    def predict_price_movement(self, horizon: int = 10) -> Dict[str, float]:
        """Predict short-term price movement based on order book"""

        if len(self.snapshots) < 30:
            return {}

        # Features from order book
        features = []

        for snapshot in list(self.snapshots)[-20:]:
            features.append([
                snapshot.spread,
                snapshot.order_imbalance,
                snapshot.volume_imbalance,
                snapshot.bid_depth,
                snapshot.ask_depth,
                snapshot.spread_bps
            ])

        features = np.array(features)

        # Simple momentum-based prediction
        # In practice, this would use a trained ML model
        recent_imbalances = [f[1] for f in features[-5:]]
        imbalance_trend = np.polyfit(range(len(recent_imbalances)), recent_imbalances, 1)[0]

        # Predict price movement direction
        if imbalance_trend > 0.1:
            direction_prob = 0.7  # Likely upward
        elif imbalance_trend < -0.1:
            direction_prob = 0.3  # Likely downward
        else:
            direction_prob = 0.5  # Neutral

        # Estimate magnitude
        spread_volatility = np.std([s.spread for s in list(self.snapshots)[-20:]])
        expected_move = spread_volatility * np.sqrt(horizon / 252)  # Annualized

        return {
            'predicted_direction': 'up' if direction_prob > 0.5 else 'down',
            'direction_probability': direction_prob,
            'expected_move_bps': expected_move * 10000,
            'confidence_interval': (expected_move * 0.5, expected_move * 1.5)
        }

    def _calculate_mid_price(self) -> float:
        """Calculate mid price"""
        if self.bids and self.asks:
            return (self.bids[0][0] + self.asks[0][0]) / 2
        return 0.0

    def _calculate_spread(self) -> float:
        """Calculate bid-ask spread"""
        if self.bids and self.asks:
            return self.asks[0][0] - self.bids[0][0]
        return 0.0

    def _calculate_order_imbalance(self) -> float:
        """Calculate order imbalance"""
        bid_orders = len(self.bids)
        ask_orders = len(self.asks)
        total_orders = bid_orders + ask_orders

        if total_orders > 0:
            return (bid_orders - ask_orders) / total_orders
        return 0.0

    def _calculate_volume_imbalance(self) -> float:
        """Calculate volume imbalance"""
        bid_volume = sum(qty for _, qty in self.bids)
        ask_volume = sum(qty for _, qty in self.asks)
        total_volume = bid_volume + ask_volume

        if total_volume > 0:
            return (bid_volume - ask_volume) / total_volume
        return 0.0

    def _calculate_market_quality(self) -> float:
        """Calculate market quality score (0-1)"""

        if not self.snapshots:
            return 0.0

        # Factors contributing to market quality
        factors = []

        # 1. Spread tightness (lower spread = higher quality)
        avg_spread = np.mean(list(self.spread_history))
        spread_score = max(0, 1 - avg_spread / 0.02)  # Assume 2% max spread
        factors.append(spread_score)

        # 2. Depth adequacy
        avg_bid_depth = np.mean([sum(qty for _, qty in s.bids) for s in self.snapshots])
        avg_ask_depth = np.mean([sum(qty for _, qty in s.asks) for s in self.snapshots])
        depth_score = min(1.0, (avg_bid_depth + avg_ask_depth) / 2000)  # Assume 2000 shares adequate
        factors.append(depth_score)

        # 3. Imbalance stability
        imbalance_volatility = np.std(list(self.imbalance_history))
        imbalance_score = max(0, 1 - imbalance_volatility)
        factors.append(imbalance_score)

        # 4. Order flow consistency
        if len(self.order_flow) > 50:
            recent_flow = list(self.order_flow)[-50:]
            flow_volatility = np.std([o.quantity for o in recent_flow])
            avg_flow = np.mean([o.quantity for o in recent_flow])
            flow_score = max(0, 1 - flow_volatility / (2 * avg_flow)) if avg_flow > 0 else 0
            factors.append(flow_score)

        return np.mean(factors) if factors else 0.0

    def _process_market_order(self, event: OrderFlowEvent):
        """Process a market order and update order book"""

        remaining_qty = event.quantity

        if event.is_buy_order:
            # Market buy order - consume ask side
            for i, (price, qty) in enumerate(self.asks):
                if remaining_qty <= 0:
                    break

                executed_qty = min(remaining_qty, qty)
                self.asks[i] = (price, qty - executed_qty)
                remaining_qty -= executed_qty

            # Remove empty levels
            self.asks = [(p, q) for p, q in self.asks if q > 0]

        else:
            # Market sell order - consume bid side
            for i, (price, qty) in enumerate(self.bids):
                if remaining_qty <= 0:
                    break

                executed_qty = min(remaining_qty, qty)
                self.bids[i] = (price, qty - executed_qty)
                remaining_qty -= executed_qty

            # Remove empty levels
            self.bids = [(p, q) for p, q in self.bids if q > 0]


class LOBDynamicsModel:
    """Limit Order Book Dynamics Model"""

    def __init__(self, config: LOBModelConfig):
        self.config = config

        # Model components
        self.price_model = None
        self.queue_model = None
        self.execution_model = None

        # Training data
        self.historical_snapshots = []
        self.order_flow_history = []

    def train(self, snapshots: List[OrderBookSnapshot],
              order_flow: List[OrderFlowEvent]):
        """Train the LOB dynamics model"""

        self.historical_snapshots = snapshots
        self.order_flow_history = order_flow

        # Train price dynamics model
        self._train_price_model()

        # Train queue position model
        self._train_queue_model()

        # Train execution model
        self._train_execution_model()

    def simulate_order_book_evolution(self, initial_snapshot: OrderBookSnapshot,
                                    time_horizon: float, n_steps: int) -> List[OrderBookSnapshot]:
        """Simulate order book evolution over time"""

        snapshots = [initial_snapshot]
        current_snapshot = initial_snapshot

        dt = time_horizon / n_steps

        for step in range(n_steps):
            # Simulate order arrivals and executions
            new_events = self._simulate_order_events(current_snapshot, dt)

            # Update order book
            updated_snapshot = self._apply_events_to_snapshot(current_snapshot, new_events)

            snapshots.append(updated_snapshot)
            current_snapshot = updated_snapshot

        return snapshots

    def estimate_queue_position_probability(self, target_price: float,
                                         current_book: OrderBookSnapshot) -> float:
        """Estimate probability of executing at target price"""

        if not self.queue_model:
            return 0.0

        # Extract features
        features = self._extract_queue_features(target_price, current_book)

        # Predict execution probability
        if hasattr(self.queue_model, 'predict_proba'):
            prob = self.queue_model.predict_proba([features])[0][1]
        else:
            prob = self.queue_model.predict([features])[0]

        return prob

    def estimate_price_impact(self, order_size: int,
                            current_book: OrderBookSnapshot,
                            execution_time: float) -> Dict[str, float]:
        """Estimate price impact of a market order"""

        # Simple square-root market impact model
        market_depth = current_book.market_depth['total_orders']
        spread = current_book.spread

        if market_depth == 0:
            return {'immediate_impact': 0.0, 'temporary_impact': 0.0, 'permanent_impact': 0.0}

        # Kyle's lambda (market impact coefficient)
        kyle_lambda = spread / (2 * market_depth)

        # Price impact components
        immediate_impact = kyle_lambda * order_size
        temporary_impact = immediate_impact * 0.5  # Decay over time
        permanent_impact = immediate_impact * 0.2   # Information effect

        return {
            'immediate_impact': immediate_impact,
            'temporary_impact': temporary_impact,
            'permanent_impact': permanent_impact,
            'total_impact': immediate_impact + temporary_impact + permanent_impact
        }

    def _train_price_model(self):
        """Train price dynamics model"""

        if len(self.historical_snapshots) < 50:
            return

        # Extract price time series
        prices = [s.mid_price for s in self.historical_snapshots]
        returns = np.diff(np.log(prices))

        # Fit ARIMA model for price dynamics
        try:
            model = sm.tsa.ARIMA(returns, order=(1, 0, 1))
            self.price_model = model.fit()
        except:
            # Fallback: simple random walk
            self.price_model = None

    def _train_queue_model(self):
        """Train queue position model"""

        if len(self.historical_snapshots) < 50 or len(self.order_flow_history) < 50:
            return

        # Create training data
        X = []
        y = []

        for i, event in enumerate(self.order_flow_history):
            if i >= len(self.historical_snapshots) - 1:
                break

            snapshot = self.historical_snapshots[i]

            # Features: distance from best bid/ask, order book imbalance, etc.
            features = self._extract_queue_features(event.price, snapshot)
            X.append(features)

            # Target: whether order was executed
            executed = event.executed_quantity > 0
            y.append(int(executed))

        if len(X) >= 50:
            # Train random forest classifier
            self.queue_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.queue_model.fit(X, y)

    def _train_execution_model(self):
        """Train order execution model"""

        if len(self.order_flow_history) < 50:
            return

        # Create training data for execution time prediction
        X = []
        y = []

        for event in self.order_flow_history:
            if event.executed_quantity > 0 and event.remaining_quantity == 0:
                # Fully executed orders
                features = [
                    event.quantity,
                    event.price,
                    1 if event.is_buy_order else 0,
                    1 if event.is_market_order else 0
                ]
                X.append(features)
                y.append(event.executed_quantity / event.quantity)  # Execution ratio

        if len(X) >= 20:
            self.execution_model = GradientBoostingClassifier(n_estimators=50, random_state=42)
            self.execution_model.fit(X, y)

    def _simulate_order_events(self, snapshot: OrderBookSnapshot, dt: float) -> List[OrderFlowEvent]:
        """Simulate order arrivals and executions"""

        events = []

        # Parameters from historical data
        avg_order_size = 100  # Placeholder
        order_arrival_rate = 10  # Orders per second

        # Simulate Poisson arrivals
        n_orders = np.random.poisson(order_arrival_rate * dt)

        for _ in range(n_orders):
            # Random order type
            order_types = ["market_buy", "market_sell", "limit_buy", "limit_sell"]
            weights = [0.2, 0.2, 0.3, 0.3]  # Market orders less frequent
            order_type = np.random.choice(order_types, p=weights)

            # Random price (around mid price)
            mid_price = snapshot.mid_price
            price_std = snapshot.spread * 2
            price = np.random.normal(mid_price, price_std)

            # Random quantity
            quantity = int(np.random.exponential(avg_order_size))

            event = OrderFlowEvent(
                timestamp=snapshot.timestamp + dt,
                symbol=snapshot.symbol,
                order_type=order_type,
                price=max(0.01, price),  # Ensure positive price
                quantity=quantity
            )

            events.append(event)

        return events

    def _apply_events_to_snapshot(self, snapshot: OrderBookSnapshot,
                                events: List[OrderFlowEvent]) -> OrderBookSnapshot:
        """Apply order events to create new snapshot"""

        new_bids = snapshot.bids.copy()
        new_asks = snapshot.asks.copy()

        for event in events:
            if event.order_type == "limit_buy":
                # Add to bid side
                self._add_limit_order(new_bids, event.price, event.quantity, is_bid=True)
            elif event.order_type == "limit_sell":
                # Add to ask side
                self._add_limit_order(new_asks, event.price, event.quantity, is_bid=False)
            elif event.is_market_order:
                # Process market order
                if event.is_buy_order:
                    # Consume ask side
                    remaining_qty = event.quantity
                    new_asks_copy = new_asks.copy()
                    for i, (price, qty) in enumerate(new_asks_copy):
                        if remaining_qty <= 0:
                            break
                        executed_qty = min(remaining_qty, qty)
                        new_asks[i] = (price, qty - executed_qty)
                        remaining_qty -= executed_qty
                    new_asks[:] = [(p, q) for p, q in new_asks if q > 0]
                else:
                    # Consume bid side
                    remaining_qty = event.quantity
                    new_bids_copy = new_bids.copy()
                    for i, (price, qty) in enumerate(new_bids_copy):
                        if remaining_qty <= 0:
                            break
                        executed_qty = min(remaining_qty, qty)
                        new_bids[i] = (price, qty - executed_qty)
                        remaining_qty -= executed_qty
                    new_bids[:] = [(p, q) for p, q in new_bids if q > 0]

        # Create new snapshot
        new_snapshot = OrderBookSnapshot(
            timestamp=snapshot.timestamp + 0.1,  # Small time increment
            symbol=snapshot.symbol,
            bids=new_bids,
            asks=new_asks
        )

        # Recalculate metrics
        new_snapshot.mid_price = (new_snapshot.best_bid + new_snapshot.best_ask) / 2 if (new_snapshot.best_bid and new_snapshot.best_ask) else snapshot.mid_price
        new_snapshot.spread = new_snapshot.best_ask - new_snapshot.best_bid if (new_snapshot.best_bid and new_snapshot.best_ask) else snapshot.spread

        return new_snapshot

    def _add_limit_order(self, order_list: List[Tuple[float, int]], price: float,
                        quantity: int, is_bid: bool):
        """Add a limit order to the order list"""

        # Insert in correct position
        if is_bid:
            # Bids: descending order (highest first)
            for i, (p, q) in enumerate(order_list):
                if price > p:
                    order_list.insert(i, (price, quantity))
                    return
            order_list.append((price, quantity))
        else:
            # Asks: ascending order (lowest first)
            for i, (p, q) in enumerate(order_list):
                if price < p:
                    order_list.insert(i, (price, quantity))
                    return
            order_list.append((price, quantity))

    def _extract_queue_features(self, target_price: float,
                               snapshot: OrderBookSnapshot) -> List[float]:
        """Extract features for queue position modeling"""

        features = []

        # Distance from best prices
        if snapshot.best_bid:
            distance_from_bid = (target_price - snapshot.best_bid) / snapshot.best_bid
        else:
            distance_from_bid = 0.0

        if snapshot.best_ask:
            distance_from_ask = (target_price - snapshot.best_ask) / snapshot.best_ask
        else:
            distance_from_ask = 0.0

        features.extend([distance_from_bid, distance_from_ask])

        # Order book imbalance
        features.append(snapshot.order_imbalance)

        # Spread
        features.append(snapshot.spread)

        # Queue depth
        features.extend([snapshot.bid_depth, snapshot.ask_depth])

        # Market quality
        features.append(snapshot.spread_bps)

        return features


class OrderBookAnalyzer:
    """Advanced order book analysis tools"""

    def __init__(self):
        self.lob_model = None
        self.liquidity_metrics = {}

    def analyze_order_book_resilience(self, order_book: LimitOrderBook) -> Dict[str, float]:
        """Analyze order book resilience to large orders"""

        if not order_book.snapshots:
            return {}

        current_snapshot = order_book.get_current_snapshot()

        # Test different order sizes
        test_sizes = [100, 500, 1000, 5000, 10000]
        resilience_scores = {}

        for size in test_sizes:
            # Estimate price impact
            if self.lob_model:
                impact = self.lob_model.estimate_price_impact(size, current_snapshot, 1.0)
                resilience_scores[f'size_{size}'] = 1.0 / (1.0 + impact['total_impact'])
            else:
                # Simple heuristic
                market_depth = current_snapshot.market_depth['total_orders']
                resilience_scores[f'size_{size}'] = min(1.0, market_depth / (market_depth + size))

        # Overall resilience score
        avg_resilience = np.mean(list(resilience_scores.values()))

        return {
            'resilience_scores': resilience_scores,
            'average_resilience': avg_resilience,
            'resilience_volatility': np.std(list(resilience_scores.values())),
            'max_impact_order_size': max(test_sizes)
        }

    def detect_order_book_manipulation(self, order_book: LimitOrderBook) -> Dict[str, Any]:
        """Detect potential order book manipulation patterns"""

        if len(order_book.order_flow) < 100:
            return {'manipulation_detected': False, 'confidence': 0.0}

        # Analyze order flow patterns
        recent_orders = list(order_book.order_flow)[-100:]

        # Check for spoofing patterns (large orders quickly cancelled)
        spoofing_indicators = []

        # 1. Large orders followed by quick cancellation
        large_orders = [o for o in recent_orders if o.quantity > np.percentile([o.quantity for o in recent_orders], 95)]

        for order in large_orders:
            # Check if order was cancelled quickly (placeholder logic)
            cancellation_time = 0.1  # Placeholder
            if cancellation_time < 1.0:  # Cancelled within 1 second
                spoofing_indicators.append(order)

        # 2. Layering patterns (multiple orders at same price)
        price_counts = defaultdict(int)
        for order in recent_orders:
            price_counts[order.price] += 1

        layering_score = sum(count for count in price_counts.values() if count > 5) / len(recent_orders)

        # 3. Momentum ignition (orders designed to trigger other orders)
        momentum_indicators = []

        # Overall manipulation score
        spoofing_score = len(spoofing_indicators) / max(len(large_orders), 1)
        layering_score = min(layering_score, 1.0)

        total_score = (spoofing_score + layering_score) / 2

        return {
            'manipulation_detected': total_score > 0.3,
            'manipulation_score': total_score,
            'spoofing_indicators': len(spoofing_indicators),
            'layering_score': layering_score,
            'confidence': min(total_score * 2, 1.0)
        }

    def calculate_optimal_execution_strategy(self, order_size: int,
                                           order_book: LimitOrderBook,
                                           time_horizon: float) -> Dict[str, Any]:
        """Calculate optimal execution strategy"""

        if not order_book.snapshots:
            return {}

        current_snapshot = order_book.get_current_snapshot()

        # VWAP strategy
        vwap_schedule = self._calculate_vwap_schedule(order_size, time_horizon)

        # POV (Percentage of Volume) strategy
        pov_schedule = self._calculate_pov_schedule(order_size, time_horizon, order_book)

        # Implementation shortfall
        is_schedule = self._calculate_implementation_shortfall_schedule(order_size, time_horizon, order_book)

        # TWAP (Time Weighted Average Price)
        twap_schedule = self._calculate_twap_schedule(order_size, time_horizon)

        strategies = {
            'vwap': vwap_schedule,
            'pov': pov_schedule,
            'implementation_shortfall': is_schedule,
            'twap': twap_schedule
        }

        # Evaluate strategies
        evaluation = {}
        for name, schedule in strategies.items():
            evaluation[name] = self._evaluate_execution_schedule(schedule, order_book)

        # Find best strategy
        best_strategy = max(evaluation, key=lambda x: evaluation[x]['expected_return'])

        return {
            'strategies': strategies,
            'evaluation': evaluation,
            'recommended_strategy': best_strategy,
            'expected_improvement': evaluation[best_strategy]['expected_return']
        }

    def _calculate_vwap_schedule(self, order_size: int, time_horizon: float) -> List[Tuple[float, int]]:
        """Calculate VWAP execution schedule"""

        # Simple equal-sized chunks over time
        n_periods = max(1, int(time_horizon / 60))  # 1-minute intervals
        chunk_size = order_size // n_periods
        remainder = order_size % n_periods

        schedule = []
        for i in range(n_periods):
            qty = chunk_size + (1 if i < remainder else 0)
            schedule.append((i * 60, qty))  # (time_offset, quantity)

        return schedule

    def _calculate_pov_schedule(self, order_size: int, time_horizon: float,
                               order_book: LimitOrderBook) -> List[Tuple[float, int]]:
        """Calculate POV execution schedule"""

        # Target percentage of volume
        target_pov = 0.1  # 10% of volume

        # Estimate market volume from order book
        if order_book.snapshots:
            avg_volume = np.mean([s.market_depth['total_orders'] for s in order_book.snapshots])
            target_volume_per_period = avg_volume * target_pov

            # Schedule based on estimated volume
            schedule = []
            remaining_qty = order_size
            time_step = time_horizon / 10  # 10 periods

            for i in range(10):
                if remaining_qty <= 0:
                    break

                qty = min(remaining_qty, int(target_volume_per_period))
                schedule.append((i * time_step, qty))
                remaining_qty -= qty

            return schedule

        return self._calculate_twap_schedule(order_size, time_horizon)

    def _calculate_implementation_shortfall_schedule(self, order_size: int, time_horizon: float,
                                                   order_book: LimitOrderBook) -> List[Tuple[float, int]]:
        """Calculate Implementation Shortfall schedule"""

        # Front-load execution to minimize price impact
        total_time = time_horizon

        # Execute 50% immediately, then remaining over time
        immediate_qty = order_size // 2
        remaining_qty = order_size - immediate_qty

        schedule = [(0, immediate_qty)]

        # Spread remaining over time
        n_periods = max(1, int(total_time / 60))
        chunk_size = remaining_qty // n_periods

        for i in range(1, n_periods + 1):
            if remaining_qty <= 0:
                break

            qty = min(chunk_size, remaining_qty)
            schedule.append((i * 60, qty))
            remaining_qty -= qty

        return schedule

    def _calculate_twap_schedule(self, order_size: int, time_horizon: float) -> List[Tuple[float, int]]:
        """Calculate TWAP execution schedule"""

        n_periods = max(1, int(time_horizon / 60))
        chunk_size = order_size // n_periods
        remainder = order_size % n_periods

        schedule = []
        for i in range(n_periods):
            qty = chunk_size + (1 if i < remainder else 0)
            schedule.append((i * 60, qty))

        return schedule

    def _evaluate_execution_schedule(self, schedule: List[Tuple[float, int]],
                                   order_book: LimitOrderBook) -> Dict[str, float]:
        """Evaluate execution schedule performance"""

        if not schedule or not order_book.snapshots:
            return {'expected_return': 0.0, 'execution_cost': 0.0}

        current_snapshot = order_book.get_current_snapshot()
        mid_price = current_snapshot.mid_price

        total_cost = 0.0
        total_quantity = 0

        for time_offset, qty in schedule:
            # Estimate execution price with some slippage
            slippage = current_snapshot.spread * 0.1  # 10% of spread
            execution_price = mid_price + slippage if qty > 0 else mid_price

            total_cost += execution_price * qty
            total_quantity += qty

        avg_execution_price = total_cost / total_quantity if total_quantity > 0 else mid_price

        # Calculate implementation shortfall
        expected_return = (mid_price - avg_execution_price) / mid_price

        # Estimate transaction costs
        execution_cost = abs(expected_return) * 0.001  # 10 bps cost

        return {
            'expected_return': expected_return,
            'execution_cost': execution_cost,
            'avg_execution_price': avg_execution_price,
            'total_quantity': total_quantity
        }


# Factory functions
def create_limit_order_book(symbol: str, max_levels: int = 10) -> LimitOrderBook:
    """Factory function for limit order book"""
    return LimitOrderBook(symbol, max_levels)


def create_lob_dynamics_model(config: LOBModelConfig = None) -> LOBDynamicsModel:
    """Factory function for LOB dynamics model"""
    return LOBDynamicsModel(config or LOBModelConfig())


def create_order_book_analyzer() -> OrderBookAnalyzer:
    """Factory function for order book analyzer"""
    return OrderBookAnalyzer()


# Example usage and testing
if __name__ == "__main__":
    # Test order book analytics
    print("Testing Order Book Analytics...")

    # Create order book
    lob = create_limit_order_book("AAPL", max_levels=5)

    # Simulate order book data
    np.random.seed(42)

    for i in range(100):
        # Generate synthetic bid/ask data
        mid_price = 150 + np.random.normal(0, 0.5)
        spread = np.random.uniform(0.01, 0.05)

        bids = []
        asks = []

        # Generate bid levels
        for j in range(5):
            price = mid_price - spread/2 - j * 0.01
            qty = int(np.random.uniform(50, 200))
            bids.append((price, qty))

        # Generate ask levels
        for j in range(5):
            price = mid_price + spread/2 + j * 0.01
            qty = int(np.random.uniform(50, 200))
            asks.append((price, qty))

        timestamp = time.time() + i
        lob.update_order_book(bids, asks, timestamp)

        # Add some order flow
        if np.random.random() < 0.3:  # 30% chance of order
            order_types = ["market_buy", "market_sell", "limit_buy", "limit_sell"]
            order_type = np.random.choice(order_types)
            price = mid_price + np.random.normal(0, spread)
            qty = int(np.random.exponential(100))

            event = OrderFlowEvent(
                timestamp=timestamp,
                symbol="AAPL",
                order_type=order_type,
                price=max(0.01, price),
                quantity=qty
            )
            lob.add_order_flow(event)

    print(f"Processed {len(lob.snapshots)} order book snapshots")

    # Analyze liquidity
    liquidity = lob.calculate_liquidity_metrics()
    print("Liquidity Metrics:")
    for key, value in liquidity.items():
        print(".4f")

    # Analyze order flow
    flow_analysis = lob.analyze_order_flow(window=50)
    print("\nOrder Flow Analysis:")
    for key, value in flow_analysis.items():
        print(f"  {key}: {value}")

    # Predict price movement
    prediction = lob.predict_price_movement(horizon=10)
    print("\nPrice Movement Prediction:")
    for key, value in prediction.items():
        print(f"  {key}: {value}")

    print("\nOrder book analytics test completed successfully!")

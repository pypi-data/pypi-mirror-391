"""High-frequency trading models and latency analysis."""

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
from scipy import stats, optimize
from scipy.spatial.distance import pdist, squareform

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    RandomForestClassifier = None
    GradientBoostingRegressor = None
    StandardScaler = None
    TimeSeriesSplit = None

try:
    from statsmodels.tsa.stattools import grangercausalitytests
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    grangercausalitytests = None

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None

# Import existing modules
try:
    from .order_book_analytics import OrderBookSnapshot, OrderFlowEvent, LimitOrderBook
except ImportError:
    OrderBookSnapshot = None
    OrderFlowEvent = None
    LimitOrderBook = None


@dataclass
class LatencyMetrics:
    """Latency measurement and analysis"""

    order_to_execution_latency: float = 0.0  # microseconds
    market_data_latency: float = 0.0  # microseconds
    network_round_trip: float = 0.0  # microseconds
    processing_latency: float = 0.0  # microseconds

    # Latency distribution
    latency_percentiles: Dict[str, float] = field(default_factory=dict)

    # Jitter and stability
    latency_jitter: float = 0.0
    latency_stability_score: float = 0.0

    @property
    def total_latency(self) -> float:
        """Total round-trip latency"""
        return (self.order_to_execution_latency +
                self.market_data_latency +
                self.network_round_trip +
                self.processing_latency)


@dataclass
class HFTStrategyConfig:
    """Configuration for HFT strategies"""

    # Execution parameters
    max_position_size: int = 1000
    max_orders_per_second: int = 100
    min_profit_threshold: float = 0.001  # $0.001 per share

    # Risk limits
    max_inventory_risk: float = 0.02  # 2% of portfolio
    max_adverse_selection_risk: float = 0.01
    stop_loss_threshold: float = 0.05

    # Latency thresholds
    max_execution_latency: float = 100  # microseconds
    max_market_data_delay: float = 10   # microseconds

    # Strategy parameters
    momentum_window: int = 10
    mean_reversion_threshold: float = 0.001
    order_book_depth: int = 5

    # Market regime detection
    regime_detection_window: int = 100
    volatility_threshold: float = 0.02


@dataclass
class ExecutionSignal:
    """HFT execution signal"""

    timestamp: float
    symbol: str
    signal_type: str  # "buy", "sell", "cancel", "modify"
    price: float
    quantity: int
    urgency: str = "normal"  # "high", "normal", "low"

    # Signal metadata
    confidence_score: float = 0.0
    expected_profit: float = 0.0
    risk_score: float = 0.0

    # Execution constraints
    max_latency: float = 100.0  # microseconds
    time_to_live: float = 1.0   # seconds

    @property
    def is_expired(self) -> bool:
        """Check if signal has expired"""
        return time.time() - self.timestamp > self.time_to_live


class LatencyArbitrageStrategy:
    """Latency arbitrage between different market venues"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Venue latency tracking
        self.venue_latencies = {}  # venue -> LatencyMetrics
        self.price_discrepancies = deque(maxlen=1000)

        # Position tracking
        self.positions = {}  # symbol -> position
        self.pending_orders = {}  # order_id -> order_details

    def detect_arbitrage_opportunity(self, venue_prices: Dict[str, Dict[str, float]],
                                    venue_latencies: Dict[str, LatencyMetrics]) -> Optional[ExecutionSignal]:
        """Detect latency arbitrage opportunities across venues"""

        if len(venue_prices) < 2:
            return None

        # Find best bid and ask across all venues
        best_bid = -float('inf')
        best_bid_venue = None
        best_ask = float('inf')
        best_ask_venue = None

        for venue, prices in venue_prices.items():
            if 'bid' in prices and prices['bid'] > best_bid:
                best_bid = prices['bid']
                best_bid_venue = venue

            if 'ask' in prices and prices['ask'] < best_ask:
                best_ask = prices['ask']
                best_ask_venue = venue

        # Check for profitable arbitrage
        if best_bid > best_ask and best_bid_venue != best_ask_venue:
            # Calculate profit after latency costs
            gross_profit = best_bid - best_ask

            # Account for latency costs
            bid_latency = venue_latencies[best_bid_venue].total_latency / 1e6  # Convert to seconds
            ask_latency = venue_latencies[best_ask_venue].total_latency / 1e6

            # Assume price movement during latency
            expected_price_move = 0.0001  # 1 bp per second (conservative)
            latency_cost = expected_price_move * (bid_latency + ask_latency)

            net_profit = gross_profit - latency_cost

            if net_profit > self.config.min_profit_threshold:
                # Generate arbitrage signal
                signal = ExecutionSignal(
                    timestamp=time.time(),
                    symbol=list(venue_prices.keys())[0],  # Assume same symbol
                    signal_type="arbitrage",
                    price=best_ask,
                    quantity=min(100, self.config.max_position_size // 2),  # Conservative size
                    urgency="high",
                    confidence_score=min(1.0, net_profit / 0.01),  # Confidence based on profit
                    expected_profit=net_profit,
                    risk_score=latency_cost / gross_profit
                )

                return signal

        return None

    def execute_arbitrage_trade(self, signal: ExecutionSignal,
                               venue_connections: Dict[str, Any]) -> bool:
        """Execute arbitrage trade across venues"""

        try:
            # This would implement actual order routing to different venues
            # For now, simulate execution

            # Update position
            if signal.symbol not in self.positions:
                self.positions[signal.symbol] = 0

            self.positions[signal.symbol] += signal.quantity

            # Check position limits
            if abs(self.positions[signal.symbol]) > self.config.max_position_size:
                # Generate offsetting trade
                offset_signal = ExecutionSignal(
                    timestamp=time.time(),
                    symbol=signal.symbol,
                    signal_type="sell" if signal.signal_type == "buy" else "buy",
                    price=signal.price + 0.01,  # Slight slippage
                    quantity=abs(self.positions[signal.symbol]) - self.config.max_position_size,
                    urgency="high"
                )
                self._execute_offset_trade(offset_signal)

            return True

        except Exception as e:
            print(f"Arbitrage execution failed: {e}")
            return False

    def _execute_offset_trade(self, signal: ExecutionSignal):
        """Execute offsetting trade to manage position"""
        # Implementation would route to appropriate venue
        pass


class OrderFlowPredictionModel:
    """Machine learning model for order flow prediction"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Model components
        self.feature_extractor = None
        self.prediction_model = None
        self.scaler = StandardScaler()

        # Training data
        self.historical_features = []
        self.historical_targets = []

    def train(self, order_book: LimitOrderBook, order_flow: List[OrderFlowEvent]):
        """Train the order flow prediction model"""

        # Extract features from historical data
        features = []
        targets = []

        for i in range(self.config.momentum_window, len(order_flow)):
            # Extract features from order book state
            snapshot = order_book.snapshots[i - self.config.momentum_window]
            feature_vector = self._extract_features(snapshot, order_flow[i-self.config.momentum_window:i])

            features.append(feature_vector)

            # Target: next order direction (1 for buy, -1 for sell)
            next_order = order_flow[i]
            target = 1 if next_order.is_buy_order else -1
            targets.append(target)

        if len(features) >= 100:
            # Scale features
            features_scaled = self.scaler.fit_transform(features)

            # Train model
            self.prediction_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.prediction_model.fit(features_scaled, targets)

    def predict_next_order_direction(self, current_snapshot: OrderBookSnapshot,
                                   recent_orders: List[OrderFlowEvent]) -> Tuple[int, float]:
        """Predict the direction of the next order"""

        if not self.prediction_model:
            return 0, 0.0

        # Extract features
        features = self._extract_features(current_snapshot, recent_orders)
        features_scaled = self.scaler.transform([features])

        # Predict
        prediction = self.prediction_model.predict(features_scaled)[0]
        probabilities = self.prediction_model.predict_proba(features_scaled)[0]

        confidence = max(probabilities)

        return prediction, confidence

    def generate_trading_signal(self, current_snapshot: OrderBookSnapshot,
                              recent_orders: List[OrderFlowEvent]) -> Optional[ExecutionSignal]:
        """Generate trading signal based on order flow prediction"""

        direction, confidence = self.predict_next_order_direction(current_snapshot, recent_orders)

        if confidence < 0.6:  # Minimum confidence threshold
            return None

        # Determine trade parameters
        if direction == 1:  # Expected buy order
            signal_type = "sell"
            price = current_snapshot.best_ask
        else:  # Expected sell order
            signal_type = "buy"
            price = current_snapshot.best_bid

        signal = ExecutionSignal(
            timestamp=time.time(),
            symbol=current_snapshot.symbol,
            signal_type=signal_type,
            price=price,
            quantity=min(50, self.config.max_position_size // 10),  # Small size for HFT
            urgency="normal",
            confidence_score=confidence,
            expected_profit=self.config.min_profit_threshold,
            risk_score=0.1
        )

        return signal

    def _extract_features(self, snapshot: OrderBookSnapshot,
                         recent_orders: List[OrderFlowEvent]) -> List[float]:
        """Extract features for prediction model"""

        features = []

        # Order book features
        features.extend([
            snapshot.spread,
            snapshot.order_imbalance,
            snapshot.volume_imbalance,
            snapshot.bid_depth,
            snapshot.ask_depth,
            snapshot.spread_bps
        ])

        # Order flow features (last N orders)
        n_recent = min(len(recent_orders), 10)

        buy_volume = sum(o.quantity for o in recent_orders[-n_recent:] if o.is_buy_order)
        sell_volume = sum(o.quantity for o in recent_orders[-n_recent:] if not o.is_buy_order)
        total_volume = buy_volume + sell_volume

        order_imbalance = (buy_volume - sell_volume) / total_volume if total_volume > 0 else 0
        order_intensity = len(recent_orders[-n_recent:]) / n_recent if n_recent > 0 else 0

        features.extend([
            order_imbalance,
            order_intensity,
            buy_volume,
            sell_volume
        ])

        # Momentum features
        if len(recent_orders) >= 5:
            recent_prices = [o.price for o in recent_orders[-5:]]
            price_momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] != 0 else 0
            features.append(price_momentum)

        # Queue position features
        if snapshot.bids and snapshot.asks:
            queue_ratio = len(snapshot.bids) / (len(snapshot.bids) + len(snapshot.asks))
            features.append(queue_ratio)

        return features


class QueuePositionOptimizer:
    """Optimize queue position in limit order book"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Queue position model
        self.execution_probability_model = None
        self.price_impact_model = None

    def find_optimal_queue_position(self, order_book: LimitOrderBook,
                                  target_price: float, side: str) -> Tuple[float, float]:
        """Find optimal price level for queue positioning"""

        # Get relevant price levels
        if side == "buy":
            price_levels = [price for price, _ in order_book.bids[:self.config.order_book_depth]]
        else:
            price_levels = [price for price, _ in order_book.asks[:self.config.order_book_depth]]

        if not price_levels:
            return target_price, 0.0

        best_price = target_price
        best_expected_profit = -float('inf')

        # Evaluate each price level
        for price in price_levels:
            # Estimate execution probability
            execution_prob = self._estimate_execution_probability(price, order_book, side)

            # Estimate queue position cost
            queue_cost = abs(price - target_price)

            # Calculate expected profit
            expected_profit = execution_prob * self.config.min_profit_threshold - queue_cost

            if expected_profit > best_expected_profit:
                best_expected_profit = expected_profit
                best_price = price

        return best_price, best_expected_profit

    def optimize_limit_order_placement(self, order_book: LimitOrderBook,
                                     target_quantity: int, side: str,
                                     time_horizon: float) -> List[Tuple[float, int]]:
        """Optimize limit order placement across multiple price levels"""

        # Split order across optimal price levels
        total_placed = 0
        order_schedule = []

        while total_placed < target_quantity:
            # Find optimal price for remaining quantity
            remaining_qty = target_quantity - total_placed
            optimal_price, _ = self.find_optimal_queue_position(
                order_book, order_book.get_current_snapshot().mid_price, side
            )

            # Place portion of order
            place_qty = min(remaining_qty, 100)  # Max 100 shares per level

            order_schedule.append((optimal_price, place_qty))
            total_placed += place_qty

            # Update order book simulation (simplified)
            # In practice, this would simulate the impact of our own orders

        return order_schedule

    def _estimate_execution_probability(self, price: float,
                                      order_book: LimitOrderBook,
                                      side: str) -> float:
        """Estimate probability of order execution at given price"""

        current_snapshot = order_book.get_current_snapshot()

        if side == "buy":
            # For buy orders, execution depends on ask side
            if price >= current_snapshot.best_ask:
                # Market order - immediate execution
                return 1.0
            else:
                # Limit order - depends on queue position
                queue_position = 0
                cumulative_volume = 0

                for ask_price, ask_qty in current_snapshot.asks:
                    if price >= ask_price:
                        cumulative_volume += ask_qty
                        if cumulative_volume >= 50:  # Assume we can walk through 50 shares
                            return min(1.0, cumulative_volume / 200)  # Conservative estimate
                    queue_position += 1

                return 0.0  # No execution expected

        else:  # sell orders
            if price <= current_snapshot.best_bid:
                return 1.0
            else:
                queue_position = 0
                cumulative_volume = 0

                for bid_price, bid_qty in current_snapshot.bids:
                    if price <= bid_price:
                        cumulative_volume += bid_qty
                        if cumulative_volume >= 50:
                            return min(1.0, cumulative_volume / 200)
                    queue_position += 1

                return 0.0


class MomentumIgnitionStrategy:
    """Momentum ignition and order flow manipulation strategies"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Strategy state
        self.active_positions = {}
        self.ignition_orders = deque(maxlen=100)

    def detect_momentum_opportunity(self, order_book: LimitOrderBook) -> Optional[ExecutionSignal]:
        """Detect momentum ignition opportunities"""

        if len(order_book.snapshots) < self.config.momentum_window:
            return None

        # Analyze recent price momentum
        recent_snapshots = list(order_book.snapshots)[-self.config.momentum_window:]
        prices = [s.mid_price for s in recent_snapshots]

        # Calculate momentum
        price_change = prices[-1] - prices[0]
        momentum = price_change / prices[0] if prices[0] != 0 else 0

        # Detect strong momentum
        if abs(momentum) > 0.001:  # 0.1% price move
            direction = "buy" if momentum > 0 else "sell"

            # Check order book imbalance
            current_snapshot = order_book.get_current_snapshot()
            imbalance_threshold = 0.2

            if ((direction == "buy" and current_snapshot.order_imbalance > imbalance_threshold) or
                (direction == "sell" and current_snapshot.order_imbalance < -imbalance_threshold)):

                signal = ExecutionSignal(
                    timestamp=time.time(),
                    symbol=current_snapshot.symbol,
                    signal_type=direction,
                    price=current_snapshot.best_bid if direction == "buy" else current_snapshot.best_ask,
                    quantity=min(200, self.config.max_position_size // 5),
                    urgency="high",
                    confidence_score=min(1.0, abs(momentum) / 0.005),  # Confidence based on momentum strength
                    expected_profit=abs(momentum) * 0.5,  # Expect to capture half the move
                    risk_score=0.3
                )

                return signal

        return None

    def execute_momentum_trade(self, signal: ExecutionSignal) -> bool:
        """Execute momentum ignition trade"""

        try:
            # Place aggressive order to ignite momentum
            # In practice, this would route to exchange

            # Track position
            if signal.symbol not in self.active_positions:
                self.active_positions[signal.symbol] = 0

            if signal.signal_type == "buy":
                self.active_positions[signal.symbol] += signal.quantity
            else:
                self.active_positions[signal.symbol] -= signal.quantity

            # Set up exit strategy
            self._schedule_exit_trade(signal)

            return True

        except Exception as e:
            print(f"Momentum trade execution failed: {e}")
            return False

    def _schedule_exit_trade(self, entry_signal: ExecutionSignal):
        """Schedule exit trade for momentum strategy"""

        # Simple time-based exit (in practice, would use profit targets/stops)
        exit_time = time.time() + 30  # 30 seconds

        exit_signal = ExecutionSignal(
            timestamp=exit_time,
            symbol=entry_signal.symbol,
            signal_type="sell" if entry_signal.signal_type == "buy" else "buy",
            price=entry_signal.price * 1.002 if entry_signal.signal_type == "buy" else entry_signal.price * 0.998,
            quantity=entry_signal.quantity,
            urgency="normal"
        )

        self.ignition_orders.append(exit_signal)


class FlashCrashDetector:
    """Detect and respond to flash crash events"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Crash detection parameters
        self.price_velocity_threshold = 0.05  # 5% per second
        self.volume_spike_threshold = 3.0     # 3x normal volume
        self.recovery_time_threshold = 30     # 30 seconds

        # State tracking
        self.crash_detected = False
        self.crash_start_time = None
        self.pre_crash_prices = deque(maxlen=10)

    def detect_flash_crash(self, order_book: LimitOrderBook) -> bool:
        """Detect flash crash conditions"""

        if len(order_book.snapshots) < 10:
            return False

        recent_snapshots = list(order_book.snapshots)[-10:]

        # Calculate price velocity
        prices = [s.mid_price for s in recent_snapshots]
        time_diffs = np.diff([s.timestamp for s in recent_snapshots])

        if len(time_diffs) > 0 and time_diffs[0] > 0:
            price_velocity = (prices[-1] - prices[0]) / time_diffs[0]
            price_velocity_pct = price_velocity / prices[0]

            # Check for extreme negative velocity
            if price_velocity_pct < -self.price_velocity_threshold:
                if not self.crash_detected:
                    self.crash_detected = True
                    self.crash_start_time = time.time()
                    print(f"Flash crash detected! Price velocity: {price_velocity_pct:.2%}")

                return True

        # Check for recovery
        if self.crash_detected and self.crash_start_time:
            recovery_time = time.time() - self.crash_start_time

            if recovery_time > self.recovery_time_threshold:
                # Check if prices have recovered
                current_price = recent_snapshots[-1].mid_price
                avg_pre_crash = np.mean(list(self.pre_crash_prices)) if self.pre_crash_prices else current_price

                if abs(current_price - avg_pre_crash) / avg_pre_crash < 0.02:  # Within 2% of pre-crash
                    self.crash_detected = False
                    self.crash_start_time = None
                    print("Flash crash recovery detected")

        # Update pre-crash prices
        if not self.crash_detected:
            self.pre_crash_prices.append(recent_snapshots[-1].mid_price)

        return self.crash_detected

    def generate_crash_response_signal(self, order_book: LimitOrderBook) -> Optional[ExecutionSignal]:
        """Generate trading signal in response to flash crash"""

        if not self.crash_detected:
            return None

        current_snapshot = order_book.get_current_snapshot()

        # During crash: Buy oversold assets
        # After crash: Sell overbought assets

        if self.crash_start_time and (time.time() - self.crash_start_time) < 10:
            # Early crash phase - buy dip
            signal_type = "buy"
            price = current_snapshot.best_bid
            confidence = 0.6
        else:
            # Recovery phase - sell rally
            signal_type = "sell"
            price = current_snapshot.best_ask
            confidence = 0.4

        signal = ExecutionSignal(
            timestamp=time.time(),
            symbol=current_snapshot.symbol,
            signal_type=signal_type,
            price=price,
            quantity=min(100, self.config.max_position_size // 10),
            urgency="low",  # Conservative during uncertainty
            confidence_score=confidence,
            risk_score=0.8  # High risk during flash crashes
        )

        return signal


class StatisticalMicroArbitrage:
    """Statistical arbitrage at microsecond scale"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Cointegration and correlation tracking
        self.asset_pairs = {}  # pair -> cointegration_params
        self.spread_history = defaultdict(deque)

    def find_micro_arbitrage_opportunities(self, asset_prices: Dict[str, float],
                                         order_books: Dict[str, LimitOrderBook]) -> List[ExecutionSignal]:
        """Find statistical arbitrage opportunities"""

        signals = []

        # Check each asset pair
        for pair, params in self.asset_pairs.items():
            asset1, asset2 = pair.split('_')

            if asset1 not in asset_prices or asset2 not in asset_prices:
                continue

            price1 = asset_prices[asset1]
            price2 = asset_prices[asset2]

            # Calculate spread
            spread = price1 - params['hedge_ratio'] * price2

            # Store spread history
            self.spread_history[pair].append(spread)

            if len(self.spread_history[pair]) >= 100:
                # Calculate z-score
                spread_mean = np.mean(list(self.spread_history[pair]))
                spread_std = np.std(list(self.spread_history[pair]))

                if spread_std > 0:
                    z_score = (spread - spread_mean) / spread_std

                    # Generate signals for extreme deviations
                    if abs(z_score) > 2.0:  # 2 standard deviations
                        direction = -1 if z_score > 0 else 1  # Mean reversion

                        # Create signal for asset1
                        signal1 = ExecutionSignal(
                            timestamp=time.time(),
                            symbol=asset1,
                            signal_type="buy" if direction == 1 else "sell",
                            price=order_books[asset1].get_current_snapshot().best_bid if direction == 1
                                 else order_books[asset1].get_current_snapshot().best_ask,
                            quantity=min(50, self.config.max_position_size // 20),
                            urgency="normal",
                            confidence_score=min(1.0, abs(z_score) / 4.0),
                            expected_profit=abs(z_score) * spread_std * 0.1,  # Expected convergence
                            risk_score=abs(z_score) / 10.0
                        )

                        # Create offsetting signal for asset2
                        signal2 = ExecutionSignal(
                            timestamp=time.time(),
                            symbol=asset2,
                            signal_type="sell" if direction == 1 else "buy",
                            price=order_books[asset2].get_current_snapshot().best_bid if direction == -1
                                 else order_books[asset2].get_current_snapshot().best_ask,
                            quantity=int(signal1.quantity * params['hedge_ratio']),
                            urgency="normal",
                            confidence_score=signal1.confidence_score
                        )

                        signals.extend([signal1, signal2])

        return signals

    def update_cointegration_params(self, price_data: pd.DataFrame):
        """Update cointegration parameters for asset pairs"""

        assets = price_data.columns.tolist()

        for i in range(len(assets)):
            for j in range(i+1, len(assets)):
                asset1, asset2 = assets[i], assets[j]

                # Test for cointegration
                try:
                    result = self._test_cointegration(price_data[asset1], price_data[asset2])

                    if result['is_cointegrated']:
                        pair_name = f"{asset1}_{asset2}"
                        self.asset_pairs[pair_name] = {
                            'hedge_ratio': result['hedge_ratio'],
                            'half_life': result['half_life'],
                            'adf_statistic': result['adf_statistic']
                        }

                except Exception as e:
                    continue

    def _test_cointegration(self, price1: pd.Series, price2: pd.Series) -> Dict[str, Any]:
        """Test for cointegration between two price series"""

        # Simple Engle-Granger test simulation
        # In practice, would use statsmodels coint function

        # Calculate hedge ratio
        covariance = np.cov(price1, price2)[0, 1]
        variance = np.var(price2)
        hedge_ratio = covariance / variance if variance > 0 else 1.0

        # Create spread
        spread = price1 - hedge_ratio * price2

        # Simple stationarity test (ADF-like)
        from statsmodels.tsa.stattools import adfuller

        try:
            adf_result = adfuller(spread, maxlag=1)
            adf_statistic = adf_result[0]
            p_value = adf_result[1]

            # Estimate half-life
            spread_lag = spread.shift(1).dropna()
            spread_diff = spread.diff().dropna()
            spread_lag = spread_lag.iloc[:len(spread_diff)]

            # Simple OLS for half-life
            beta = np.cov(spread_diff, spread_lag)[0, 1] / np.var(spread_lag)
            half_life = -np.log(2) / beta if beta < 0 else float('inf')

            return {
                'is_cointegrated': p_value < 0.05,
                'hedge_ratio': hedge_ratio,
                'half_life': half_life,
                'adf_statistic': adf_statistic,
                'p_value': p_value
            }

        except:
            return {
                'is_cointegrated': False,
                'hedge_ratio': 1.0,
                'half_life': float('inf'),
                'adf_statistic': 0.0,
                'p_value': 1.0
            }


class HFTRiskManager:
    """Risk management for high-frequency trading"""

    def __init__(self, config: HFTStrategyConfig):
        self.config = config

        # Risk tracking
        self.position_sizes = {}
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_pnl = 0.0

        # Circuit breakers
        self.consecutive_losses = 0
        self.last_trade_time = time.time()

    def check_position_limits(self, symbol: str, proposed_quantity: int) -> bool:
        """Check if proposed position exceeds limits"""

        current_position = self.position_sizes.get(symbol, 0)
        new_position = current_position + proposed_quantity

        # Check absolute position limit
        if abs(new_position) > self.config.max_position_size:
            return False

        # Check inventory risk limit
        portfolio_value = 100000  # Assume $100K portfolio
        position_value = abs(new_position) * 100  # Assume $100 per share

        if position_value / portfolio_value > self.config.max_inventory_risk:
            return False

        return True

    def check_adverse_selection_risk(self, signal: ExecutionSignal,
                                   order_book: LimitOrderBook) -> bool:
        """Check adverse selection risk"""

        # Estimate probability of adverse price movement
        current_snapshot = order_book.get_current_snapshot()

        # Simple adverse selection measure: spread width and order imbalance
        spread_risk = current_snapshot.spread / current_snapshot.mid_price
        imbalance_risk = abs(current_snapshot.order_imbalance)

        total_risk = spread_risk + imbalance_risk

        return total_risk < self.config.max_adverse_selection_risk

    def update_pnl_tracking(self, trade_pnl: float):
        """Update P&L tracking and drawdown calculation"""

        self.daily_pnl += trade_pnl

        # Update drawdown
        if self.daily_pnl > self.peak_pnl:
            self.peak_pnl = self.daily_pnl
            self.max_drawdown = 0.0
        else:
            current_drawdown = self.peak_pnl - self.daily_pnl
            self.max_drawdown = max(self.max_drawdown, current_drawdown)

        # Check stop-loss
        if self.max_drawdown > self.config.stop_loss_threshold:
            print(f"Stop-loss triggered. Drawdown: {self.max_drawdown:.2%}")
            return False

        return True

    def should_pause_trading(self) -> bool:
        """Check if trading should be paused due to risk limits"""

        # Check consecutive losses
        if self.consecutive_losses >= 5:
            return True

        # Check trading frequency
        time_since_last_trade = time.time() - self.last_trade_time
        if time_since_last_trade < 1.0 / self.config.max_orders_per_second:
            return True

        return False


# Factory functions
def create_latency_arbitrage_strategy(config: HFTStrategyConfig = None) -> LatencyArbitrageStrategy:
    """Factory function for latency arbitrage strategy"""
    return LatencyArbitrageStrategy(config or HFTStrategyConfig())


def create_order_flow_prediction_model(config: HFTStrategyConfig = None) -> OrderFlowPredictionModel:
    """Factory function for order flow prediction model"""
    return OrderFlowPredictionModel(config or HFTStrategyConfig())


def create_queue_position_optimizer(config: HFTStrategyConfig = None) -> QueuePositionOptimizer:
    """Factory function for queue position optimizer"""
    return QueuePositionOptimizer(config or HFTStrategyConfig())


def create_flash_crash_detector(config: HFTStrategyConfig = None) -> FlashCrashDetector:
    """Factory function for flash crash detector"""
    return FlashCrashDetector(config or HFTStrategyConfig())


def create_hft_risk_manager(config: HFTStrategyConfig = None) -> HFTRiskManager:
    """Factory function for HFT risk manager"""
    return HFTRiskManager(config or HFTStrategyConfig())


# Example usage and testing
if __name__ == "__main__":
    # Test HFT modeling
    print("Testing High-Frequency Trading Modeling...")

    # Create components
    config = HFTStrategyConfig(max_position_size=1000)
    risk_manager = create_hft_risk_manager(config)
    flash_detector = create_flash_crash_detector(config)

    # Create mock order book
    from .order_book_analytics import create_limit_order_book
    order_book = create_limit_order_book("AAPL")

    # Simulate order book updates
    np.random.seed(42)

    for i in range(200):
        # Generate synthetic order book
        mid_price = 150 + np.sin(i / 10) * 2  # Some trend
        spread = 0.02 + np.random.uniform(-0.01, 0.01)

        bids = []
        asks = []

        for j in range(5):
            bid_price = mid_price - spread/2 - j * 0.005
            ask_price = mid_price + spread/2 + j * 0.005
            bid_qty = int(np.random.uniform(20, 100))
            ask_qty = int(np.random.uniform(20, 100))

            bids.append((bid_price, bid_qty))
            asks.append((ask_price, ask_qty))

        timestamp = time.time() + i * 0.1
        order_book.update_order_book(bids, asks, timestamp)

        # Check for flash crash
        if flash_detector.detect_flash_crash(order_book):
            signal = flash_detector.generate_crash_response_signal(order_book)
            if signal:
                print(f"Flash crash signal generated: {signal.signal_type} {signal.quantity} shares")

        # Simulate some trades
        if np.random.random() < 0.05:  # 5% chance of trade
            pnl = np.random.normal(0, 0.01)  # Small P&L per trade
            risk_manager.update_pnl_tracking(pnl)

    # Test risk limits
    test_signal = ExecutionSignal(
        timestamp=time.time(),
        symbol="AAPL",
        signal_type="buy",
        price=150.0,
        quantity=100
    )

    position_ok = risk_manager.check_position_limits("AAPL", 100)
    adverse_ok = risk_manager.check_adverse_selection_risk(test_signal, order_book)

    print("Risk Management Tests:")
    print(f"Position limit check: {'✓' if position_ok else '✗'}")
    print(f"Adverse selection check: {'✓' if adverse_ok else '✗'}")

    # Test order flow prediction
    prediction_model = create_order_flow_prediction_model(config)

    if len(order_book.order_flow) >= config.momentum_window:
        direction, confidence = prediction_model.predict_next_order_direction(
            order_book.get_current_snapshot(),
            list(order_book.order_flow)[-10:]
        )

        print("Order Flow Prediction:")
        print(f"Predicted direction: {'Buy' if direction == 1 else 'Sell' if direction == -1 else 'Neutral'}")
        print(f"Confidence: {confidence:.2%}")

    print("\nHigh-frequency trading modeling test completed successfully!")

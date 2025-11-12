"""Liquidity modeling and risk assessment."""

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
from scipy.optimize import minimize_scalar
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.stattools import grangercausalitytests, coint
from statsmodels.tsa.api import VAR
import networkx as nx

# Import existing modules
try:
    from .order_book_analytics import OrderBookSnapshot, OrderFlowEvent, LimitOrderBook
    from .hft_modeling import ExecutionSignal, HFTStrategyConfig
    from .market_impact import TransactionCosts, ExecutionTrajectory
except ImportError:
    OrderBookSnapshot = None
    OrderFlowEvent = None
    LimitOrderBook = None
    ExecutionSignal = None
    HFTStrategyConfig = None
    TransactionCosts = None
    ExecutionTrajectory = None


@dataclass
class LiquidityMetrics:
    """Comprehensive liquidity metrics"""

    # Depth metrics
    bid_depth: float = 0.0
    ask_depth: float = 0.0
    total_depth: float = 0.0
    depth_imbalance: float = 0.0

    # Spread metrics
    quoted_spread: float = 0.0
    effective_spread: float = 0.0
    realized_spread: float = 0.0

    # Volume metrics
    trading_volume: float = 0.0
    order_flow_volume: float = 0.0
    cancellation_volume: float = 0.0

    # Resilience metrics
    price_impact: float = 0.0
    resilience_time: float = 0.0
    absorption_capacity: float = 0.0

    # Risk metrics
    liquidity_risk_score: float = 0.0
    dry_up_probability: float = 0.0

    # Market quality
    turnover_ratio: float = 0.0
    participation_rate: float = 0.0

    @property
    def market_quality_index(self) -> float:
        """Calculate overall market quality index (0-1)"""
        # Normalize and combine metrics
        spread_score = max(0, 1 - self.quoted_spread / 0.05)  # Lower spread = higher quality
        depth_score = min(1.0, self.total_depth / 10000)     # Higher depth = higher quality
        volume_score = min(1.0, self.trading_volume / 100000) # Higher volume = higher quality
        risk_score = 1 - self.liquidity_risk_score            # Lower risk = higher quality

        return np.mean([spread_score, depth_score, volume_score, risk_score])


@dataclass
class LiquidityModelConfig:
    """Configuration for liquidity modeling"""

    # Model parameters
    model_type: str = "high_frequency"  # "high_frequency", "daily", "intraday"

    # Time windows
    short_window: int = 5     # 5-minute window
    medium_window: int = 60   # 1-hour window
    long_window: int = 1440   # 1-day window (in minutes)

    # Liquidity thresholds
    min_depth_threshold: float = 1000
    max_spread_threshold: float = 0.05
    min_volume_threshold: float = 10000

    # Risk parameters
    liquidity_var_confidence: float = 0.99
    stress_test_scenarios: int = 1000

    # Market parameters
    tick_size: float = 0.01
    lot_size: int = 100


@dataclass
class LiquidityStressTestResult:
    """Results from liquidity stress testing"""

    scenario_name: str = ""
    liquidity_dry_up_time: float = 0.0  # minutes
    max_spread_expansion: float = 0.0
    volume_decline_percentage: float = 0.0
    price_impact_increase: float = 0.0
    recovery_time: float = 0.0

    # Risk measures
    var_liquidity_shortfall: float = 0.0
    expected_shortfall_liquidity: float = 0.0

    # Scenario details
    shock_magnitude: float = 0.0
    shock_duration: float = 0.0


class LiquidityRiskModel:
    """Advanced liquidity risk modeling"""

    def __init__(self, config: LiquidityModelConfig):
        self.config = config

        # Historical data
        self.liquidity_history = deque(maxlen=10000)
        self.spread_history = deque(maxlen=5000)
        self.depth_history = deque(maxlen=5000)

        # Risk models
        self.liquidity_var_model = None
        self.spread_volatility_model = None

    def calculate_liquidity_metrics(self, order_book: LimitOrderBook,
                                  time_window: int = 60) -> LiquidityMetrics:
        """Calculate comprehensive liquidity metrics"""

        if len(order_book.snapshots) < time_window:
            return LiquidityMetrics()

        # Get recent snapshots
        recent_snapshots = list(order_book.snapshots)[-time_window:]

        # Depth metrics
        bid_depths = [s.market_depth['bid_volume'] for s in recent_snapshots]
        ask_depths = [s.market_depth['ask_volume'] for s in recent_snapshots]

        metrics = LiquidityMetrics()
        metrics.bid_depth = np.mean(bid_depths)
        metrics.ask_depth = np.mean(ask_depths)
        metrics.total_depth = metrics.bid_depth + metrics.ask_depth
        metrics.depth_imbalance = (metrics.bid_depth - metrics.ask_depth) / metrics.total_depth if metrics.total_depth > 0 else 0

        # Spread metrics
        spreads = [s.spread for s in recent_snapshots]
        metrics.quoted_spread = np.mean(spreads)

        # Effective spread (simplified - would need trade data)
        metrics.effective_spread = metrics.quoted_spread * 1.2

        # Realized spread (simplified)
        metrics.realized_spread = metrics.quoted_spread * 0.8

        # Volume metrics
        if hasattr(order_book, 'order_flow') and order_book.order_flow:
            recent_orders = list(order_book.order_flow)[-time_window * 10:]  # Assume 10 orders per minute
            metrics.trading_volume = sum(o.quantity for o in recent_orders if o.is_market_order)
            metrics.order_flow_volume = sum(o.quantity for o in recent_orders)

        # Resilience metrics
        metrics.price_impact = self._calculate_price_impact_resilience(recent_snapshots)
        metrics.resilience_time = self._calculate_resilience_time(recent_snapshots)
        metrics.absorption_capacity = self._calculate_absorption_capacity(recent_snapshots)

        # Risk metrics
        metrics.liquidity_risk_score = self._calculate_liquidity_risk_score(metrics)
        metrics.dry_up_probability = self._calculate_dry_up_probability(recent_snapshots)

        # Market quality metrics
        metrics.turnover_ratio = metrics.trading_volume / metrics.total_depth if metrics.total_depth > 0 else 0
        metrics.participation_rate = metrics.order_flow_volume / (metrics.order_flow_volume + metrics.total_depth) if (metrics.order_flow_volume + metrics.total_depth) > 0 else 0

        return metrics

    def estimate_liquidity_var(self, confidence_level: float = 0.99,
                             time_horizon: int = 1) -> Dict[str, float]:
        """Estimate Value-at-Risk for liquidity"""

        if len(self.liquidity_history) < 100:
            return {'liquidity_var': 0.0, 'expected_shortfall': 0.0}

        # Calculate liquidity shortfall distribution
        liquidity_shortfalls = []

        for i in range(len(self.liquidity_history) - time_horizon):
            current_liquidity = self.liquidity_history[i]
            future_liquidity = np.mean(list(self.liquidity_history)[i+1:i+1+time_horizon])

            shortfall = current_liquidity - future_liquidity
            liquidity_shortfalls.append(shortfall)

        if not liquidity_shortfalls:
            return {'liquidity_var': 0.0, 'expected_shortfall': 0.0}

        # Calculate VaR and ES
        shortfalls_sorted = np.sort(liquidity_shortfalls)
        var_index = int((1 - confidence_level) * len(shortfalls_sorted))

        liquidity_var = shortfalls_sorted[var_index]
        expected_shortfall = np.mean(shortfalls_sorted[:var_index])

        return {
            'liquidity_var': liquidity_var,
            'expected_shortfall': expected_shortfall,
            'confidence_level': confidence_level,
            'time_horizon': time_horizon
        }

    def model_liquidity_commonality(self, asset_liquidity_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Model liquidity commonality across assets"""

        if len(asset_liquidity_data) < 2:
            return {}

        # Prepare data for analysis
        asset_names = list(asset_liquidity_data.keys())
        liquidity_series = [pd.Series(data) for data in asset_liquidity_data.values()]

        # Align time series
        min_length = min(len(series) for series in liquidity_series)
        aligned_series = [series.tail(min_length).values for series in liquidity_series]

        # Calculate correlations
        correlation_matrix = np.corrcoef(aligned_series)

        # Principal component analysis for commonality
        from sklearn.decomposition import PCA
        pca = PCA(n_components=min(5, len(asset_names)))
        pca.fit(np.column_stack(aligned_series))

        # Commonality explained by first component
        commonality_ratio = pca.explained_variance_ratio_[0]

        # Network analysis of liquidity connections
        liquidity_network = self._build_liquidity_network(correlation_matrix, asset_names)

        return {
            'correlation_matrix': correlation_matrix,
            'commonality_ratio': commonality_ratio,
            'explained_variance_ratios': pca.explained_variance_ratio_,
            'liquidity_network': liquidity_network,
            'most_connected_asset': max(liquidity_network.degree(), key=lambda x: x[1])[0] if liquidity_network else None
        }

    def stress_test_liquidity(self, baseline_liquidity: LiquidityMetrics,
                            scenarios: List[Dict[str, float]]) -> List[LiquidityStressTestResult]:
        """Perform liquidity stress testing"""

        results = []

        for scenario in scenarios:
            shock_magnitude = scenario.get('shock_magnitude', 0.0)
            shock_duration = scenario.get('shock_duration', 1.0)
            shock_type = scenario.get('shock_type', 'volume_decline')

            # Simulate stressed liquidity
            stressed_metrics = self._simulate_liquidity_stress(
                baseline_liquidity, shock_magnitude, shock_duration, shock_type
            )

            result = LiquidityStressTestResult(
                scenario_name=f"{shock_type}_{shock_magnitude:.1%}_{shock_duration:.1f}h",
                liquidity_dry_up_time=self._calculate_dry_up_time(stressed_metrics),
                max_spread_expansion=stressed_metrics.quoted_spread / baseline_liquidity.quoted_spread - 1,
                volume_decline_percentage=(baseline_liquidity.trading_volume - stressed_metrics.trading_volume) / baseline_liquidity.trading_volume if baseline_liquidity.trading_volume > 0 else 0,
                price_impact_increase=stressed_metrics.price_impact / baseline_liquidity.price_impact - 1 if baseline_liquidity.price_impact > 0 else 0,
                recovery_time=self._estimate_recovery_time(stressed_metrics, baseline_liquidity),
                shock_magnitude=shock_magnitude,
                shock_duration=shock_duration
            )

            # Calculate risk measures
            risk_metrics = self._calculate_stress_risk_measures(stressed_metrics, baseline_liquidity)
            result.var_liquidity_shortfall = risk_metrics.get('var_shortfall', 0.0)
            result.expected_shortfall_liquidity = risk_metrics.get('es_shortfall', 0.0)

            results.append(result)

        return results

    def _calculate_price_impact_resilience(self, snapshots: List[OrderBookSnapshot]) -> float:
        """Calculate price impact resilience"""

        if len(snapshots) < 10:
            return 0.0

        # Simulate small market orders and measure price impact
        impacts = []

        for snapshot in snapshots[-10:]:
            # Simulate 100-share market order
            test_order_size = 100

            if snapshot.asks:
                # Buy order impact
                best_ask = snapshot.asks[0][0]
                available_qty = sum(qty for _, qty in snapshot.asks[:5])  # Top 5 levels

                if available_qty >= test_order_size:
                    # Would execute at best ask
                    impact = 0.0
                else:
                    # Would walk the book
                    remaining_qty = test_order_size - available_qty
                    avg_price = (sum(p * min(qty, remaining_qty) for p, qty in snapshot.asks[:5]) +
                               snapshot.asks[-1][0] * max(0, remaining_qty - sum(qty for _, qty in snapshot.asks[:5]))) / test_order_size
                    impact = avg_price - best_ask

                impacts.append(impact)

        return np.mean(impacts) if impacts else 0.0

    def _calculate_resilience_time(self, snapshots: List[OrderBookSnapshot]) -> float:
        """Calculate liquidity resilience time (minutes)"""

        if len(snapshots) < 30:
            return float('inf')

        # Look for large price moves and recovery time
        prices = [s.mid_price for s in snapshots]
        price_changes = np.diff(prices)

        # Find significant price shocks
        threshold = np.std(price_changes) * 2
        shock_indices = np.where(np.abs(price_changes) > threshold)[0]

        if len(shock_indices) == 0:
            return float('inf')

        # Calculate average recovery time
        recovery_times = []

        for shock_idx in shock_indices:
            if shock_idx + 10 >= len(prices):
                continue

            shock_price = prices[shock_idx]
            post_shock_prices = prices[shock_idx+1:shock_idx+11]

            # Find when price recovers to within 50% of shock
            recovery_threshold = shock_price + 0.5 * price_changes[shock_idx]

            for i, price in enumerate(post_shock_prices):
                if abs(price - shock_price) <= abs(recovery_threshold - shock_price):
                    recovery_times.append(i + 1)  # +1 because we start from shock_idx+1
                    break

        return np.mean(recovery_times) if recovery_times else float('inf')

    def _calculate_absorption_capacity(self, snapshots: List[OrderBookSnapshot]) -> float:
        """Calculate market's absorption capacity"""

        if len(snapshots) < 10:
            return 0.0

        # Measure how much volume the order book can absorb
        absorption_capacities = []

        for snapshot in snapshots:
            # Calculate total depth at different spread levels
            spreads = [0.01, 0.02, 0.05, 0.10]  # Different spread thresholds

            for spread_threshold in spreads:
                bid_absorption = sum(qty for price, qty in snapshot.bids
                                   if snapshot.best_bid and (snapshot.best_bid - price) <= spread_threshold)

                ask_absorption = sum(qty for price, qty in snapshot.asks
                                   if snapshot.best_ask and (price - snapshot.best_ask) <= spread_threshold)

                total_absorption = bid_absorption + ask_absorption
                absorption_capacities.append(total_absorption)

        return np.mean(absorption_capacities) if absorption_capacities else 0.0

    def _calculate_liquidity_risk_score(self, metrics: LiquidityMetrics) -> float:
        """Calculate overall liquidity risk score (0-1, higher = more risk)"""

        # Normalize individual risk factors
        spread_risk = min(1.0, metrics.quoted_spread / self.config.max_spread_threshold)
        depth_risk = max(0, 1 - metrics.total_depth / self.config.min_depth_threshold)
        volume_risk = max(0, 1 - metrics.trading_volume / self.config.min_volume_threshold)

        imbalance_risk = abs(metrics.depth_imbalance)
        impact_risk = min(1.0, metrics.price_impact / 0.01)  # Assume 1% max impact

        # Weighted average
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Spread, depth, volume, imbalance, impact
        risk_factors = [spread_risk, depth_risk, volume_risk, imbalance_risk, impact_risk]

        return np.average(risk_factors, weights=weights)

    def _calculate_dry_up_probability(self, snapshots: List[OrderBookSnapshot]) -> float:
        """Calculate probability of liquidity dry-up"""

        if len(snapshots) < 50:
            return 0.0

        # Look for periods of low liquidity
        depths = [s.market_depth['total_orders'] for s in snapshots]
        spreads = [s.spread for s in snapshots]

        # Define dry-up conditions
        low_depth_threshold = np.percentile(depths, 10)  # Bottom 10%
        high_spread_threshold = np.percentile(spreads, 90)  # Top 10%

        dry_up_periods = 0
        total_periods = len(snapshots)

        for depth, spread in zip(depths, spreads):
            if depth <= low_depth_threshold and spread >= high_spread_threshold:
                dry_up_periods += 1

        return dry_up_periods / total_periods if total_periods > 0 else 0.0

    def _build_liquidity_network(self, correlation_matrix: np.ndarray,
                               asset_names: List[str]) -> nx.Graph:
        """Build network of liquidity connections"""

        G = nx.Graph()

        # Add nodes
        for name in asset_names:
            G.add_node(name)

        # Add edges based on correlation strength
        n = len(asset_names)
        for i in range(n):
            for j in range(i+1, n):
                correlation = correlation_matrix[i, j]
                if abs(correlation) > 0.3:  # Significant correlation threshold
                    G.add_edge(asset_names[i], asset_names[j], weight=correlation)

        return G

    def _simulate_liquidity_stress(self, baseline: LiquidityMetrics,
                                 shock_magnitude: float, shock_duration: float,
                                 shock_type: str) -> LiquidityMetrics:
        """Simulate liquidity under stress"""

        stressed = LiquidityMetrics()

        # Apply different shock types
        if shock_type == 'volume_decline':
            stressed.trading_volume = baseline.trading_volume * (1 - shock_magnitude)
            stressed.quoted_spread = baseline.quoted_spread * (1 + shock_magnitude)
            stressed.total_depth = baseline.total_depth * (1 - shock_magnitude * 0.5)

        elif shock_type == 'spread_expansion':
            stressed.quoted_spread = baseline.quoted_spread * (1 + shock_magnitude)
            stressed.trading_volume = baseline.trading_volume * (1 - shock_magnitude * 0.3)
            stressed.total_depth = baseline.total_depth

        elif shock_type == 'depth_reduction':
            stressed.total_depth = baseline.total_depth * (1 - shock_magnitude)
            stressed.quoted_spread = baseline.quoted_spread * (1 + shock_magnitude * 0.5)
            stressed.trading_volume = baseline.trading_volume

        else:  # General shock
            stressed.trading_volume = baseline.trading_volume * (1 - shock_magnitude)
            stressed.quoted_spread = baseline.quoted_spread * (1 + shock_magnitude)
            stressed.total_depth = baseline.total_depth * (1 - shock_magnitude)

        # Copy other metrics (simplified)
        stressed.bid_depth = stressed.total_depth * (1 + baseline.depth_imbalance) / 2
        stressed.ask_depth = stressed.total_depth * (1 - baseline.depth_imbalance) / 2
        stressed.depth_imbalance = baseline.depth_imbalance

        return stressed

    def _calculate_dry_up_time(self, stressed_metrics: LiquidityMetrics) -> float:
        """Calculate time to liquidity dry-up under stress"""

        # Simplified model: time proportional to remaining liquidity
        if stressed_metrics.total_depth <= 0:
            return 0.0

        # Assume consumption rate based on current volume
        consumption_rate = stressed_metrics.trading_volume / 60  # Per minute

        if consumption_rate <= 0:
            return float('inf')

        return stressed_metrics.total_depth / consumption_rate

    def _estimate_recovery_time(self, stressed: LiquidityMetrics,
                              baseline: LiquidityMetrics) -> float:
        """Estimate time for liquidity recovery"""

        # Simplified exponential recovery model
        recovery_rate = 0.1  # 10% recovery per hour

        spread_ratio = stressed.quoted_spread / baseline.quoted_spread
        depth_ratio = stressed.total_depth / baseline.total_depth

        # Time to recover 80% of normal conditions
        recovery_target = 0.2  # 80% recovered

        if spread_ratio <= 1.0 and depth_ratio >= 1.0:
            return 0.0  # Already recovered

        # Estimate recovery time
        max_ratio = max(spread_ratio - 1, 1 - depth_ratio)
        if max_ratio <= 0:
            return 0.0

        return -np.log(recovery_target) / recovery_rate

    def _calculate_stress_risk_measures(self, stressed: LiquidityMetrics,
                                      baseline: LiquidityMetrics) -> Dict[str, float]:
        """Calculate risk measures under stress"""

        # Liquidity shortfall
        depth_shortfall = baseline.total_depth - stressed.total_depth
        spread_shortfall = stressed.quoted_spread - baseline.quoted_spread

        # VaR-style measures (simplified)
        var_shortfall = depth_shortfall * 1.96  # 95% confidence
        es_shortfall = depth_shortfall * 2.33  # Expected shortfall

        return {
            'var_shortfall': var_shortfall,
            'es_shortfall': es_shortfall,
            'depth_shortfall': depth_shortfall,
            'spread_shortfall': spread_shortfall
        }


class MarketMakerLiquidityModel:
    """Market maker inventory and liquidity provision modeling"""

    def __init__(self, config: LiquidityModelConfig):
        self.config = config

        # Inventory management
        self.current_inventory = 0
        self.target_inventory = 0
        self.inventory_limits = (-5000, 5000)  # Min/max inventory

        # Quote management
        self.current_quotes = {'bid': None, 'ask': None}
        self.quote_sizes = {'bid': 100, 'ask': 100}

        # Risk management
        self.inventory_risk_aversion = 0.001  # Price adjustment per unit inventory

    def optimize_inventory_management(self, market_signals: Dict[str, Any],
                                    current_inventory: int) -> Dict[str, Any]:
        """Optimize market maker inventory management"""

        self.current_inventory = current_inventory

        # Calculate optimal quotes
        optimal_bid, optimal_ask = self._calculate_optimal_quotes(market_signals)

        # Calculate optimal quote sizes
        bid_size, ask_size = self._calculate_optimal_sizes(market_signals)

        # Check inventory limits
        inventory_adjustment = self._check_inventory_limits()

        return {
            'optimal_bid': optimal_bid,
            'optimal_ask': optimal_ask,
            'bid_size': bid_size,
            'ask_size': ask_size,
            'inventory_adjustment': inventory_adjustment,
            'current_inventory': self.current_inventory,
            'inventory_target': self.target_inventory
        }

    def model_liquidity_provision_strategy(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Model liquidity provision strategy"""

        # Assess market conditions
        volatility = market_conditions.get('volatility', 0.02)
        spread = market_conditions.get('spread', 0.02)
        depth = market_conditions.get('depth', 5000)

        # Adjust strategy based on conditions
        if volatility > 0.05:  # High volatility
            strategy = 'conservative'
            quote_frequency = 0.5  # 50% of time
            quote_size_multiplier = 0.7

        elif spread > 0.05:  # Wide spreads
            strategy = 'aggressive'
            quote_frequency = 0.9  # 90% of time
            quote_size_multiplier = 1.2

        elif depth < 2000:  # Low depth
            strategy = 'supportive'
            quote_frequency = 0.8  # 80% of time
            quote_size_multiplier = 1.1

        else:  # Normal conditions
            strategy = 'balanced'
            quote_frequency = 0.7  # 70% of time
            quote_size_multiplier = 1.0

        return {
            'strategy': strategy,
            'quote_frequency': quote_frequency,
            'quote_size_multiplier': quote_size_multiplier,
            'risk_adjustment': volatility * 0.1,
            'spread_target': spread * 1.1  # Slightly wider than market
        }

    def calculate_inventory_hedging(self, inventory_size: int,
                                  hedging_instruments: List[str]) -> Dict[str, float]:
        """Calculate optimal inventory hedging"""

        # Simple delta-hedging approach
        hedge_ratios = {}

        for instrument in hedging_instruments:
            # Assume some correlation/covariance
            correlation = np.random.uniform(0.5, 0.9)  # Placeholder
            volatility = np.random.uniform(0.01, 0.03)  # Placeholder

            # Optimal hedge ratio
            hedge_ratio = correlation * (volatility / 0.02)  # Normalize by market volatility

            hedge_ratios[instrument] = hedge_ratio * inventory_size

        return hedge_ratios

    def _calculate_optimal_quotes(self, market_signals: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate optimal bid/ask quotes"""

        # Get market mid price
        mid_price = market_signals.get('mid_price', 100.0)
        market_spread = market_signals.get('spread', 0.02)

        # Inventory adjustment
        inventory_adjustment = self.inventory_risk_aversion * self.current_inventory

        # Calculate quotes
        half_spread = market_spread / 2
        optimal_bid = mid_price - half_spread - inventory_adjustment
        optimal_ask = mid_price + half_spread - inventory_adjustment

        # Ensure bid < ask
        if optimal_bid >= optimal_ask:
            midpoint = (optimal_bid + optimal_ask) / 2
            optimal_bid = midpoint - half_spread
            optimal_ask = midpoint + half_spread

        return optimal_bid, optimal_ask

    def _calculate_optimal_sizes(self, market_signals: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate optimal quote sizes"""

        base_size = self.quote_sizes['bid']  # Symmetric for simplicity

        # Adjust based on market conditions
        volatility = market_signals.get('volatility', 0.02)
        depth = market_signals.get('depth', 5000)

        # Higher volatility -> smaller sizes
        volatility_adjustment = max(0.5, 1 - volatility / 0.05)

        # Lower depth -> larger sizes (provide more liquidity)
        depth_adjustment = min(2.0, 5000 / max(depth, 1000))

        adjusted_size = int(base_size * volatility_adjustment * depth_adjustment)

        return adjusted_size, adjusted_size

    def _check_inventory_limits(self) -> Optional[Dict[str, Any]]:
        """Check inventory limits and suggest adjustment"""

        min_inv, max_inv = self.inventory_limits

        if self.current_inventory < min_inv:
            # Need to buy back
            adjustment = {
                'action': 'buy',
                'quantity': min_inv - self.current_inventory,
                'reason': 'inventory_below_minimum'
            }
            return adjustment

        elif self.current_inventory > max_inv:
            # Need to sell
            adjustment = {
                'action': 'sell',
                'quantity': self.current_inventory - max_inv,
                'reason': 'inventory_above_maximum'
            }
            return adjustment

        return None


class LiquidityContagionModel:
    """Model liquidity contagion across markets"""

    def __init__(self, config: LiquidityModelConfig):
        self.config = config

        # Network of market connections
        self.market_network = nx.Graph()

        # Contagion parameters
        self.contagion_strength = 0.1
        self.recovery_rate = 0.05

    def build_market_liquidity_network(self, market_data: Dict[str, pd.DataFrame]) -> nx.Graph:
        """Build network of liquidity connections between markets"""

        markets = list(market_data.keys())

        # Add nodes
        for market in markets:
            self.market_network.add_node(market)

        # Calculate liquidity correlations
        for i, market1 in enumerate(markets):
            for j, market2 in enumerate(markets):
                if i >= j:
                    continue

                # Calculate correlation of liquidity measures
                liquidity1 = market_data[market1]['liquidity'].values
                liquidity2 = market_data[market2]['liquidity'].values

                min_len = min(len(liquidity1), len(liquidity2))
                corr = np.corrcoef(liquidity1[-min_len:], liquidity2[-min_len:])[0, 1]

                if abs(corr) > 0.3:  # Significant connection
                    self.market_network.add_edge(market1, market2, weight=abs(corr))

        return self.market_network

    def simulate_liquidity_shock_propagation(self, initial_shock_market: str,
                                           shock_magnitude: float,
                                           time_horizon: int = 60) -> Dict[str, List[float]]:
        """Simulate how liquidity shock propagates through market network"""

        # Initialize liquidity levels
        market_liquidity = {node: 1.0 for node in self.market_network.nodes()}

        # Apply initial shock
        market_liquidity[initial_shock_market] = 1.0 - shock_magnitude

        # Track liquidity over time
        liquidity_history = {market: [liquidity] for market, liquidity in market_liquidity.items()}

        # Simulate propagation
        for t in range(time_horizon):
            new_liquidity = market_liquidity.copy()

            for market in self.market_network.nodes():
                # Contagion from neighbors
                neighbors = list(self.market_network.neighbors(market))
                if neighbors:
                    neighbor_avg_liquidity = np.mean([market_liquidity[n] for n in neighbors])
                    contagion_effect = (neighbor_avg_liquidity - market_liquidity[market]) * self.contagion_strength
                else:
                    contagion_effect = 0

                # Recovery towards equilibrium
                recovery_effect = (1.0 - market_liquidity[market]) * self.recovery_rate

                # Update liquidity
                new_liquidity[market] += contagion_effect + recovery_effect

                # Bound between 0 and 1
                new_liquidity[market] = np.clip(new_liquidity[market], 0.0, 1.0)

            market_liquidity = new_liquidity

            # Record history
            for market, liquidity in market_liquidity.items():
                liquidity_history[market].append(liquidity)

        return liquidity_history

    def calculate_systemic_liquidity_risk(self) -> Dict[str, float]:
        """Calculate systemic liquidity risk measures"""

        if not self.market_network:
            return {}

        # Network centrality measures
        degree_centrality = nx.degree_centrality(self.market_network)
        betweenness_centrality = nx.betweenness_centrality(self.market_network)
        eigenvector_centrality = nx.eigenvector_centrality(self.market_network, max_iter=1000)

        # Systemic risk metrics
        most_central_market = max(degree_centrality, key=degree_centrality.get)
        network_density = nx.density(self.market_network)
        average_clustering = nx.average_clustering(self.market_network)

        return {
            'most_central_market': most_central_market,
            'network_density': network_density,
            'average_clustering': average_clustering,
            'systemic_risk_score': network_density * average_clustering,
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality,
            'eigenvector_centrality': eigenvector_centrality
        }


# Factory functions
def create_liquidity_risk_model(config: LiquidityModelConfig = None) -> LiquidityRiskModel:
    """Factory function for liquidity risk model"""
    return LiquidityRiskModel(config or LiquidityModelConfig())


def create_market_maker_model(config: LiquidityModelConfig = None) -> MarketMakerLiquidityModel:
    """Factory function for market maker liquidity model"""
    return MarketMakerLiquidityModel(config or LiquidityModelConfig())


def create_liquidity_contagion_model(config: LiquidityModelConfig = None) -> LiquidityContagionModel:
    """Factory function for liquidity contagion model"""
    return LiquidityContagionModel(config or LiquidityModelConfig())


# Example usage and testing
if __name__ == "__main__":
    # Test liquidity modeling
    print("Testing Liquidity Modeling...")

    # Create components
    config = LiquidityModelConfig()
    risk_model = create_liquidity_risk_model(config)
    mm_model = create_market_maker_model(config)
    contagion_model = create_liquidity_contagion_model(config)

    # Create mock order book
    from .order_book_analytics import create_limit_order_book
    order_book = create_limit_order_book("AAPL")

    # Simulate order book data
    np.random.seed(42)

    for i in range(500):
        # Generate synthetic order book
        mid_price = 150 + np.sin(i / 50) * 2
        spread = 0.02 + np.random.uniform(-0.01, 0.01)

        bids = []
        asks = []

        for j in range(5):
            bid_price = mid_price - spread/2 - j * 0.005
            ask_price = mid_price + spread/2 + j * 0.005
            bid_qty = int(np.random.uniform(50, 200))
            ask_qty = int(np.random.uniform(50, 200))

            bids.append((bid_price, bid_qty))
            asks.append((ask_price, ask_qty))

        timestamp = time.time() + i * 0.1
        order_book.update_order_book(bids, asks, timestamp)

        # Store liquidity history
        current_snapshot = order_book.get_current_snapshot()
        if current_snapshot:
            risk_model.liquidity_history.append(current_snapshot.market_depth['total_orders'])

    # Calculate liquidity metrics
    liquidity_metrics = risk_model.calculate_liquidity_metrics(order_book, time_window=60)
    print("Liquidity Metrics:")
    print(f"Bid depth: {liquidity_metrics.bid_depth:.0f}")
    print(f"Ask depth: {liquidity_metrics.ask_depth:.0f}")
    print(f"Spread: {liquidity_metrics.spread:.4f}")
    print(f"Spread bps: {liquidity_metrics.spread_bps:.2%}")
    print(f"Mid price: {liquidity_metrics.mid_price:.4f}")
    print(f"Imbalance: {liquidity_metrics.imbalance:.2%}")

    # Estimate liquidity VaR
    liquidity_var = risk_model.estimate_liquidity_var(confidence_level=0.99, time_horizon=5)
    print(f"Liquidity VaR (99% confidence, 5-minute horizon): {liquidity_var:.0f}")

    # Test market maker optimization
    market_signals = {
        'mid_price': 150.0,
        'spread': 0.02,
        'volatility': 0.02,
        'depth': 5000
    }

    mm_optimization = mm_model.optimize_inventory_management(market_signals, current_inventory=1000)
    print(f"Market Maker Optimization: {mm_optimization.get('optimal_spread', 0):.4f}")
    print(f"Inventory: {mm_optimization.get('current_inventory', 0):.4f}")

    # Test liquidity provision strategy
    provision_strategy = mm_model.model_liquidity_provision_strategy(market_signals)
    print("Liquidity Provision Strategy:")
    print(f"Strategy: {provision_strategy.get('strategy', 'N/A')}")
    print(f"Expected return: {provision_strategy.get('expected_return', 0):.1%}")

    # Test stress testing
    baseline_metrics = risk_model.calculate_liquidity_metrics(order_book, time_window=30)

    stress_scenarios = [
        {'shock_magnitude': 0.3, 'shock_duration': 1.0, 'shock_type': 'volume_decline'},
        {'shock_magnitude': 0.5, 'shock_duration': 2.0, 'shock_type': 'spread_expansion'},
        {'shock_magnitude': 0.2, 'shock_duration': 0.5, 'shock_type': 'depth_reduction'}
    ]

    stress_results = risk_model.stress_test_liquidity(baseline_metrics, stress_scenarios)

    print("Liquidity Stress Test Results:")
    for result in stress_results:
        print(f"{result.scenario_name}:")
        print(f"Impact: {result.impact:.1f}")
        print(f"Severity: {result.severity:.1%}")

    print("\nLiquidity modeling test completed successfully!")

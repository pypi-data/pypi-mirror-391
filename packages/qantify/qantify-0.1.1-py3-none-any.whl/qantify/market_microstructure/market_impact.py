"""Market impact analysis and optimal execution models."""

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

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    RandomForestRegressor = None
    GradientBoostingRegressor = None
    StandardScaler = None
    TimeSeriesSplit = None

try:
    from statsmodels.regression.linear_model import OLS
    from statsmodels.tsa.stattools import acf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    OLS = None
    acf = None

# Import existing modules
try:
    from .order_book_analytics import OrderBookSnapshot, OrderFlowEvent, LimitOrderBook
    from .hft_modeling import ExecutionSignal, HFTStrategyConfig
except ImportError:
    OrderBookSnapshot = None
    OrderFlowEvent = None
    LimitOrderBook = None
    ExecutionSignal = None
    HFTStrategyConfig = None


@dataclass
class MarketImpactModelConfig:
    """Configuration for market impact modeling"""

    # Model parameters
    model_type: str = "almgren_chriss"  # "kyle_lambda", "almgren_chriss", "square_root", "adaptive"

    # Time parameters
    trading_horizon: float = 1.0  # hours
    time_steps: int = 100

    # Impact parameters
    permanent_impact_factor: float = 0.1
    temporary_impact_factor: float = 0.5
    impact_decay_half_life: float = 0.5  # hours

    # Market parameters
    daily_volume: int = 1000000  # shares
    average_spread: float = 0.02  # dollars
    volatility: float = 0.02      # daily volatility

    # Risk parameters
    risk_aversion: float = 1.0
    participation_rate_limit: float = 0.1  # Max 10% of volume


@dataclass
class TransactionCosts:
    """Transaction cost breakdown"""

    # Explicit costs
    commission: float = 0.0
    fees: float = 0.0
    taxes: float = 0.0

    # Implicit costs
    spread_cost: float = 0.0
    market_impact: float = 0.0
    opportunity_cost: float = 0.0
    timing_risk: float = 0.0

    # Total costs
    total_explicit: float = 0.0
    total_implicit: float = 0.0
    total_cost: float = 0.0

    @property
    def explicit_cost_ratio(self) -> float:
        """Ratio of explicit to total costs"""
        return self.total_explicit / self.total_cost if self.total_cost > 0 else 0.0

    @property
    def implicit_cost_ratio(self) -> float:
        """Ratio of implicit to total costs"""
        return self.total_implicit / self.total_cost if self.total_cost > 0 else 0.0

    def update_totals(self):
        """Update total cost calculations"""
        self.total_explicit = self.commission + self.fees + self.taxes
        self.total_implicit = self.spread_cost + self.market_impact + self.opportunity_cost + self.timing_risk
        self.total_cost = self.total_explicit + self.total_implicit


@dataclass
class ExecutionTrajectory:
    """Trajectory of an execution schedule"""

    timestamps: List[float] = field(default_factory=list)
    prices: List[float] = field(default_factory=list)
    quantities: List[float] = field(default_factory=list)
    cumulative_quantity: List[float] = field(default_factory=list)

    # Cost tracking
    transaction_costs: List[TransactionCosts] = field(default_factory=list)

    # Performance metrics
    implementation_shortfall: float = 0.0
    vwap_benchmark: float = 0.0
    arrival_price: float = 0.0

    def add_execution_point(self, timestamp: float, price: float, quantity: float,
                          costs: TransactionCosts = None):
        """Add an execution point to the trajectory"""

        self.timestamps.append(timestamp)
        self.prices.append(price)
        self.quantities.append(quantity)

        cum_qty = self.cumulative_quantity[-1] if self.cumulative_quantity else 0
        self.cumulative_quantity.append(cum_qty + quantity)

        if costs:
            self.transaction_costs.append(costs)

    @property
    def total_quantity(self) -> float:
        """Total executed quantity"""
        return self.cumulative_quantity[-1] if self.cumulative_quantity else 0.0

    @property
    def average_price(self) -> float:
        """Volume-weighted average price"""
        if not self.quantities or not self.prices:
            return 0.0

        total_volume = sum(self.quantities)
        if total_volume == 0:
            return 0.0

        return sum(p * q for p, q in zip(self.prices, self.quantities)) / total_volume

    @property
    def total_costs(self) -> TransactionCosts:
        """Aggregate transaction costs"""
        if not self.transaction_costs:
            return TransactionCosts()

        total_costs = TransactionCosts()
        for cost in self.transaction_costs:
            total_costs.commission += cost.commission
            total_costs.fees += cost.fees
            total_costs.taxes += cost.taxes
            total_costs.spread_cost += cost.spread_cost
            total_costs.market_impact += cost.market_impact
            total_costs.opportunity_cost += cost.opportunity_cost
            total_costs.timing_risk += cost.timing_risk

        total_costs.update_totals()
        return total_costs


class KyleLambdaModel:
    """Kyle's Lambda Market Impact Model"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # Model parameters
        self.lambda_estimate = None
        self.impact_history = deque(maxlen=1000)

    def estimate_lambda(self, trade_data: pd.DataFrame) -> float:
        """Estimate Kyle's lambda from trade data"""

        if 'signed_volume' not in trade_data.columns or 'price_change' not in trade_data.columns:
            raise ValueError("Trade data must contain 'signed_volume' and 'price_change' columns")

        # Kyle's model: ΔP = λ * S
        # where ΔP is price change, S is signed order flow

        # Simple OLS estimation
        try:
            X = trade_data['signed_volume'].values.reshape(-1, 1)
            y = trade_data['price_change'].values

            # Add intercept
            X = np.column_stack([np.ones(len(X)), X])

            model = OLS(y, X).fit()
            self.lambda_estimate = model.params[1]  # Slope coefficient

            return self.lambda_estimate

        except Exception as e:
            print(f"Lambda estimation failed: {e}")
            self.lambda_estimate = 0.001  # Default value
            return self.lambda_estimate

    def calculate_market_impact(self, order_size: int, is_buy: bool) -> Dict[str, float]:
        """Calculate market impact using Kyle's model"""

        if self.lambda_estimate is None:
            return {'immediate_impact': 0.0, 'total_impact': 0.0}

        signed_volume = order_size if is_buy else -order_size

        # Kyle's lambda gives the price impact per unit of signed volume
        price_impact = self.lambda_estimate * signed_volume

        return {
            'immediate_impact': price_impact,
            'total_impact': price_impact,  # In Kyle's model, impact is permanent
            'lambda_used': self.lambda_estimate
        }

    def predict_price_impact_decay(self, initial_impact: float,
                                 time_horizon: float) -> np.ndarray:
        """Predict how market impact decays over time"""

        # In Kyle's model, impact is permanent, but we can model decay
        decay_rate = np.log(2) / self.config.impact_decay_half_life

        times = np.linspace(0, time_horizon, 100)
        decayed_impact = initial_impact * np.exp(-decay_rate * times)

        return decayed_impact


class AlmgrenChrissModel:
    """Almgren-Chriss Optimal Execution Model"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # Model parameters (to be estimated)
        self.sigma = config.volatility  # Volatility
        self.eta = None  # Temporary impact parameter
        self.gamma = config.risk_aversion  # Risk aversion
        self.kappa = config.permanent_impact_factor  # Permanent impact parameter

    def estimate_parameters(self, trade_data: pd.DataFrame):
        """Estimate model parameters from historical data"""

        # Estimate volatility (sigma)
        if 'returns' in trade_data.columns:
            self.sigma = trade_data['returns'].std() * np.sqrt(252)  # Annualized

        # Estimate temporary impact parameter (eta)
        # This is a simplified estimation
        self.eta = self.config.temporary_impact_factor

        # Estimate permanent impact parameter (kappa)
        self.kappa = self.config.permanent_impact_factor

    def calculate_optimal_schedule(self, total_quantity: int, time_horizon: float,
                                 arrival_price: float) -> ExecutionTrajectory:
        """Calculate optimal execution schedule using Almgren-Chriss model"""

        # Discretize time
        dt = time_horizon / self.config.time_steps
        times = np.linspace(0, time_horizon, self.config.time_steps + 1)

        # Optimal trading rate (simplified closed-form solution)
        tau = time_horizon
        Q = total_quantity

        # Risk term
        risk_term = self.gamma * self.sigma**2 * Q**2 / tau

        # Impact term
        impact_term = self.eta * Q**2 / tau

        # Optimal trading speed
        v_opt = Q / tau * (1 - np.sqrt(risk_term / (risk_term + impact_term)))

        # Create execution trajectory
        trajectory = ExecutionTrajectory()
        trajectory.arrival_price = arrival_price
        trajectory.vwap_benchmark = arrival_price  # Simplified

        cumulative_qty = 0

        for i, t in enumerate(times[:-1]):
            # Execute at optimal rate
            qty_to_execute = min(v_opt * dt, total_quantity - cumulative_qty)

            if qty_to_execute <= 0:
                break

            # Price with market impact
            temporary_impact = self.eta * qty_to_execute
            permanent_impact = self.kappa * cumulative_qty

            execution_price = arrival_price + temporary_impact + permanent_impact

            # Add execution point
            timestamp = time.time() + t * 3600  # Convert to seconds
            costs = TransactionCosts(
                market_impact=temporary_impact + permanent_impact,
                timing_risk=self.sigma * np.sqrt(dt) * execution_price
            )
            costs.update_totals()

            trajectory.add_execution_point(timestamp, execution_price, qty_to_execute, costs)
            cumulative_qty += qty_to_execute

        # Calculate implementation shortfall
        avg_price = trajectory.average_price
        trajectory.implementation_shortfall = (avg_price - arrival_price) / arrival_price

        return trajectory

    def calculate_liquidation_value(self, trajectory: ExecutionTrajectory,
                                  current_time: float) -> float:
        """Calculate remaining liquidation value"""

        if not trajectory.timestamps:
            return 0.0

        # Find remaining quantity
        executed_qty = trajectory.total_quantity
        remaining_qty = trajectory.total_quantity - executed_qty  # This should be passed as parameter

        # Estimate remaining market impact
        remaining_impact = self.kappa * remaining_qty

        # Estimate current market price (simplified)
        last_price = trajectory.prices[-1] if trajectory.prices else trajectory.arrival_price

        return (last_price + remaining_impact) * remaining_qty


class SquareRootMarketImpact:
    """Square Root Market Impact Model"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # Model parameters
        self.impact_coefficient = None  # To be estimated

    def estimate_impact_coefficient(self, trade_data: pd.DataFrame) -> float:
        """Estimate square root impact coefficient"""

        if 'order_size' not in trade_data.columns or 'price_impact' not in trade_data.columns:
            raise ValueError("Trade data must contain 'order_size' and 'price_impact' columns")

        # Square root model: Impact = β * sqrt(Size / Volume)
        try:
            # Normalize by daily volume
            normalized_size = trade_data['order_size'] / self.config.daily_volume
            sqrt_size = np.sqrt(normalized_size)

            # Estimate coefficient
            slope, intercept = np.polyfit(sqrt_size, trade_data['price_impact'], 1)
            self.impact_coefficient = slope

            return self.impact_coefficient

        except Exception as e:
            print(f"Impact coefficient estimation failed: {e}")
            self.impact_coefficient = 0.01  # Default value
            return self.impact_coefficient

    def calculate_market_impact(self, order_size: int, daily_volume: int = None) -> Dict[str, float]:
        """Calculate market impact using square root model"""

        if self.impact_coefficient is None:
            return {'impact': 0.0}

        volume = daily_volume or self.config.daily_volume
        normalized_size = order_size / volume

        impact = self.impact_coefficient * np.sqrt(normalized_size)

        return {
            'impact': impact,
            'normalized_size': normalized_size,
            'coefficient': self.impact_coefficient
        }


class AdaptiveMarketImpactModel:
    """Adaptive market impact model using machine learning"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # ML models
        self.impact_predictor = None
        self.feature_scaler = StandardScaler()

        # Training data
        self.historical_impacts = []
        self.feature_history = []

    def train_model(self, trade_data: pd.DataFrame):
        """Train adaptive impact model"""

        # Extract features
        features = []
        targets = []

        for _, row in trade_data.iterrows():
            if all(col in row.index for col in ['order_size', 'time_to_execute', 'spread', 'volatility', 'price_impact']):
                feature_vector = [
                    row['order_size'],
                    row['time_to_execute'],
                    row['spread'],
                    row['volatility'],
                    np.log(row['order_size'] + 1),  # Log size
                    row['order_size'] / self.config.daily_volume,  # Size ratio
                ]

                features.append(feature_vector)
                targets.append(row['price_impact'])

        if len(features) >= 50:
            # Scale features
            features_scaled = self.feature_scaler.fit_transform(features)

            # Train model
            self.impact_predictor = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            self.impact_predictor.fit(features_scaled, targets)

    def predict_market_impact(self, order_size: int, time_to_execute: float,
                            current_spread: float, current_volatility: float) -> float:
        """Predict market impact using ML model"""

        if self.impact_predictor is None:
            # Fallback to square root model
            sqrt_model = SquareRootMarketImpact(self.config)
            return sqrt_model.calculate_market_impact(order_size)['impact']

        # Create feature vector
        features = [
            order_size,
            time_to_execute,
            current_spread,
            current_volatility,
            np.log(order_size + 1),
            order_size / self.config.daily_volume
        ]

        # Scale features
        features_scaled = self.feature_scaler.transform([features])

        # Predict
        predicted_impact = self.impact_predictor.predict(features_scaled)[0]

        return max(0, predicted_impact)  # Ensure non-negative


class OptimalExecutionEngine:
    """Engine for calculating optimal execution strategies"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # Available models
        self.kyle_model = KyleLambdaModel(config)
        self.almgren_model = AlmgrenChrissModel(config)
        self.sqrt_model = SquareRootMarketImpact(config)
        self.adaptive_model = AdaptiveMarketImpactModel(config)

        # Current market conditions
        self.current_market_data = {}

    def calculate_optimal_strategy(self, order_size: int, time_horizon: float,
                                 strategy_type: str = "almgren_chriss") -> ExecutionTrajectory:
        """Calculate optimal execution strategy"""

        if strategy_type == "almgren_chriss":
            return self.almgren_model.calculate_optimal_schedule(
                order_size, time_horizon,
                self.current_market_data.get('arrival_price', 100.0)
            )
        elif strategy_type == "vwap":
            return self._calculate_vwap_schedule(order_size, time_horizon)
        elif strategy_type == "pov":
            return self._calculate_pov_schedule(order_size, time_horizon)
        elif strategy_type == "implementation_shortfall":
            return self._calculate_is_schedule(order_size, time_horizon)
        else:
            # Default to Almgren-Chriss
            return self.almgren_model.calculate_optimal_schedule(
                order_size, time_horizon,
                self.current_market_data.get('arrival_price', 100.0)
            )

    def compare_strategies(self, order_size: int, time_horizon: float) -> Dict[str, ExecutionTrajectory]:
        """Compare different execution strategies"""

        strategies = {}

        # Almgren-Chriss optimal
        strategies['almgren_chriss'] = self.calculate_optimal_strategy(
            order_size, time_horizon, "almgren_chriss"
        )

        # VWAP
        strategies['vwap'] = self._calculate_vwap_schedule(order_size, time_horizon)

        # POV
        strategies['pov'] = self._calculate_pov_schedule(order_size, time_horizon)

        # Implementation Shortfall
        strategies['implementation_shortfall'] = self._calculate_is_schedule(order_size, time_horizon)

        return strategies

    def estimate_transaction_costs(self, trajectory: ExecutionTrajectory) -> TransactionCosts:
        """Estimate transaction costs for a trajectory"""

        costs = TransactionCosts()

        # Commission (simplified)
        costs.commission = len(trajectory.quantities) * 0.005  # $0.005 per trade

        # Market impact (already in trajectory)
        total_impact = sum(cost.market_impact for cost in trajectory.transaction_costs)
        costs.market_impact = total_impact

        # Spread cost
        avg_spread = self.current_market_data.get('average_spread', 0.02)
        total_volume = sum(trajectory.quantities)
        costs.spread_cost = avg_spread * total_volume * 0.5  # Half spread on average

        # Timing risk
        volatility = self.current_market_data.get('volatility', 0.02)
        time_horizon = trajectory.timestamps[-1] - trajectory.timestamps[0] if trajectory.timestamps else time_horizon
        costs.timing_risk = volatility * trajectory.average_price * np.sqrt(time_horizon / (365 * 24 * 3600))

        costs.update_totals()
        return costs

    def _calculate_vwap_schedule(self, order_size: int, time_horizon: float) -> ExecutionTrajectory:
        """Calculate VWAP execution schedule"""

        trajectory = ExecutionTrajectory()

        # Assume uniform volume throughout day
        total_seconds = time_horizon * 3600
        n_intervals = max(1, int(total_seconds / 60))  # 1-minute intervals

        qty_per_interval = order_size / n_intervals

        current_time = time.time()
        arrival_price = self.current_market_data.get('arrival_price', 100.0)

        for i in range(n_intervals):
            timestamp = current_time + i * 60

            # Add some price movement (simplified)
            price_noise = np.random.normal(0, 0.001)
            price = arrival_price * (1 + price_noise)

            costs = TransactionCosts(
                market_impact=0.0001 * qty_per_interval,  # Small impact
                commission=0.005
            )
            costs.update_totals()

            trajectory.add_execution_point(timestamp, price, qty_per_interval, costs)

        trajectory.arrival_price = arrival_price
        trajectory.vwap_benchmark = trajectory.average_price

        return trajectory

    def _calculate_pov_schedule(self, order_size: int, time_horizon: float) -> ExecutionTrajectory:
        """Calculate Percentage of Volume (POV) execution schedule"""

        trajectory = ExecutionTrajectory()

        # Target POV rate
        target_pov = 0.05  # 5% of volume

        daily_volume = self.current_market_data.get('daily_volume', self.config.daily_volume)
        hourly_volume = daily_volume / 24
        target_hourly_volume = hourly_volume * target_pov

        # Calculate execution rate
        hours = time_horizon
        target_qty_per_hour = target_hourly_volume * hours
        actual_qty_per_hour = min(target_qty_per_hour, order_size / hours)

        n_intervals = max(1, int(hours * 60))  # 1-minute intervals
        qty_per_interval = actual_qty_per_hour / 60

        current_time = time.time()
        arrival_price = self.current_market_data.get('arrival_price', 100.0)
        cumulative_qty = 0

        for i in range(n_intervals):
            if cumulative_qty >= order_size:
                break

            timestamp = current_time + i * 60
            remaining_qty = order_size - cumulative_qty
            execute_qty = min(qty_per_interval, remaining_qty)

            # Price with small impact
            impact = 0.00005 * execute_qty
            price = arrival_price * (1 + np.random.normal(0, 0.001)) + impact

            costs = TransactionCosts(
                market_impact=impact,
                commission=0.005
            )
            costs.update_totals()

            trajectory.add_execution_point(timestamp, price, execute_qty, costs)
            cumulative_qty += execute_qty

        trajectory.arrival_price = arrival_price
        return trajectory

    def _calculate_is_schedule(self, order_size: int, time_horizon: float) -> ExecutionTrajectory:
        """Calculate Implementation Shortfall schedule"""

        trajectory = ExecutionTrajectory()

        # Front-load execution to minimize opportunity cost
        immediate_qty = order_size * 0.4  # 40% immediately
        remaining_qty = order_size * 0.6

        current_time = time.time()
        arrival_price = self.current_market_data.get('arrival_price', 100.0)

        # Immediate execution
        impact = self.adaptive_model.predict_market_impact(
            immediate_qty, 0.001,  # Very short time
            self.current_market_data.get('spread', 0.02),
            self.current_market_data.get('volatility', 0.02)
        )
        price = arrival_price + impact

        costs = TransactionCosts(
            market_impact=impact,
            commission=0.005
        )
        costs.update_totals()

        trajectory.add_execution_point(current_time, price, immediate_qty, costs)

        # Spread remaining over time
        remaining_time = time_horizon * 3600
        n_intervals = max(1, int(remaining_time / 60))
        qty_per_interval = remaining_qty / n_intervals

        for i in range(1, n_intervals + 1):
            timestamp = current_time + i * 60

            # Gradual execution with decaying impact
            time_factor = i / n_intervals
            impact = self.adaptive_model.predict_market_impact(
                qty_per_interval, time_factor * time_horizon,
                self.current_market_data.get('spread', 0.02),
                self.current_market_data.get('volatility', 0.02)
            ) * (1 - time_factor)  # Impact decreases over time

            price = arrival_price + impact + np.random.normal(0, 0.001) * arrival_price

            costs = TransactionCosts(
                market_impact=impact,
                commission=0.005
            )
            costs.update_totals()

            trajectory.add_execution_point(timestamp, price, qty_per_interval, costs)

        trajectory.arrival_price = arrival_price
        trajectory.implementation_shortfall = (trajectory.average_price - arrival_price) / arrival_price

        return trajectory


class TransactionCostAnalyzer:
    """Advanced transaction cost analysis"""

    def __init__(self, config: MarketImpactModelConfig):
        self.config = config

        # Cost tracking
        self.cost_history = deque(maxlen=1000)
        self.benchmark_costs = {}

    def analyze_execution_quality(self, trajectory: ExecutionTrajectory,
                                benchmark_price: float = None) -> Dict[str, float]:
        """Analyze execution quality metrics"""

        if not trajectory.prices:
            return {}

        # Use arrival price as benchmark if not provided
        benchmark = benchmark_price or trajectory.arrival_price

        # Implementation shortfall
        avg_price = trajectory.average_price
        shortfall = (avg_price - benchmark) / benchmark

        # VWAP comparison
        vwap_diff = (avg_price - trajectory.vwap_benchmark) / trajectory.vwap_benchmark if trajectory.vwap_benchmark > 0 else 0

        # Cost breakdown
        total_costs = trajectory.total_costs
        cost_ratio = total_costs.total_cost / (avg_price * trajectory.total_quantity)

        # Timing analysis
        if len(trajectory.timestamps) > 1:
            execution_duration = trajectory.timestamps[-1] - trajectory.timestamps[0]
            avg_time_between_trades = execution_duration / len(trajectory.quantities)
        else:
            avg_time_between_trades = 0

        # Market impact analysis
        total_impact = total_costs.market_impact
        avg_impact_per_share = total_impact / trajectory.total_quantity

        return {
            'implementation_shortfall': shortfall,
            'vwap_difference': vwap_diff,
            'total_cost_ratio': cost_ratio,
            'explicit_cost_ratio': total_costs.explicit_cost_ratio,
            'implicit_cost_ratio': total_costs.implicit_cost_ratio,
            'market_impact_per_share': avg_impact_per_share,
            'execution_duration': execution_duration if 'execution_duration' in locals() else 0,
            'avg_time_between_trades': avg_time_between_trades,
            'trade_count': len(trajectory.quantities)
        }

    def calculate_cost_attribution(self, trajectory: ExecutionTrajectory) -> Dict[str, float]:
        """Attribute costs to different sources"""

        total_costs = trajectory.total_costs

        # Cost attribution percentages
        total = total_costs.total_cost

        if total == 0:
            return {'market_impact': 0, 'spread_cost': 0, 'commission': 0, 'timing_risk': 0, 'opportunity_cost': 0}

        return {
            'market_impact': total_costs.market_impact / total,
            'spread_cost': total_costs.spread_cost / total,
            'commission': total_costs.commission / total,
            'timing_risk': total_costs.timing_risk / total,
            'opportunity_cost': total_costs.opportunity_cost / total
        }

    def estimate_optimal_trading_horizon(self, order_size: int,
                                       arrival_price: float) -> float:
        """Estimate optimal trading horizon to minimize costs"""

        def cost_function(horizon):
            # Simulate trajectory for different horizons
            trajectory = self._simulate_trajectory_for_horizon(order_size, horizon, arrival_price)
            quality_metrics = self.analyze_execution_quality(trajectory)

            # Cost = implementation shortfall + timing risk
            return abs(quality_metrics.get('implementation_shortfall', 0)) + quality_metrics.get('total_cost_ratio', 0)

        # Optimize horizon
        result = minimize_scalar(cost_function, bounds=(0.1, 24), method='bounded')

        return result.x if result.success else 1.0

    def _simulate_trajectory_for_horizon(self, order_size: int, horizon: float,
                                       arrival_price: float) -> ExecutionTrajectory:
        """Simulate execution trajectory for cost optimization"""

        trajectory = ExecutionTrajectory()
        trajectory.arrival_price = arrival_price

        # Simple uniform execution
        n_steps = max(1, int(horizon * 60))  # 1-minute steps
        qty_per_step = order_size / n_steps

        for i in range(n_steps):
            timestamp = time.time() + i * 60

            # Price with some impact
            impact = 0.0001 * qty_per_step * np.sqrt(i + 1)  # Increasing impact
            price = arrival_price + impact + np.random.normal(0, 0.001) * arrival_price

            costs = TransactionCosts(
                market_impact=impact,
                commission=0.005
            )
            costs.update_totals()

            trajectory.add_execution_point(timestamp, price, qty_per_step, costs)

        return trajectory


# Factory functions
def create_market_impact_model(config: MarketImpactModelConfig = None) -> AdaptiveMarketImpactModel:
    """Factory function for market impact model"""
    return AdaptiveMarketImpactModel(config or MarketImpactModelConfig())


def create_optimal_execution_engine(config: MarketImpactModelConfig = None) -> OptimalExecutionEngine:
    """Factory function for optimal execution engine"""
    return OptimalExecutionEngine(config or MarketImpactModelConfig())


def create_transaction_cost_analyzer(config: MarketImpactModelConfig = None) -> TransactionCostAnalyzer:
    """Factory function for transaction cost analyzer"""
    return TransactionCostAnalyzer(config or MarketImpactModelConfig())


# Example usage and testing
if __name__ == "__main__":
    # Test market impact analysis
    print("Testing Market Impact Analysis...")

    # Create components
    config = MarketImpactModelConfig()
    impact_model = create_market_impact_model(config)
    execution_engine = create_optimal_execution_engine(config)
    cost_analyzer = create_transaction_cost_analyzer(config)

    # Simulate market data
    execution_engine.current_market_data = {
        'arrival_price': 100.0,
        'average_spread': 0.02,
        'volatility': 0.02,
        'daily_volume': 1000000
    }

    # Test different execution strategies
    order_size = 10000
    time_horizon = 2.0  # 2 hours

    strategies = execution_engine.compare_strategies(order_size, time_horizon)

    print(f"Comparing execution strategies for {order_size} shares over {time_horizon} hours:")

    for strategy_name, trajectory in strategies.items():
        # Analyze execution quality
        quality = cost_analyzer.analyze_execution_quality(trajectory)

        # Cost attribution
        attribution = cost_analyzer.calculate_cost_attribution(trajectory)

        print(f"\n{strategy_name.upper()}:")
        print(".4f")
        print(".2%")
        print(".4f")
        print(f"  Market Impact: {attribution.get('market_impact', 0):.2%}")
        print(f"  Spread Cost: {attribution.get('spread_cost', 0):.2%}")
        print(f"  Commission: {attribution.get('commission', 0):.2%}")

    # Test market impact prediction
    impact = impact_model.predict_market_impact(
        order_size=5000,
        time_to_execute=1.0,
        current_spread=0.02,
        current_volatility=0.02
    )

    print(f"Market impact: {impact:.6f}")
    # Test Kyle's lambda model
    kyle_model = KyleLambdaModel(config)

    # Simulate trade data
    np.random.seed(42)
    trade_data = pd.DataFrame({
        'signed_volume': np.random.normal(0, 1000, 500),
        'price_change': np.random.normal(0, 0.01, 500)
    })

    lambda_est = kyle_model.estimate_lambda(trade_data)
    print(f"Kyle's lambda estimate: {lambda_est:.6f}")
    # Test Almgren-Chriss model
    almgren_model = AlmgrenChrissModel(config)
    almgren_model.estimate_parameters(trade_data)

    optimal_trajectory = almgren_model.calculate_optimal_schedule(order_size, time_horizon, 100.0)
    print(f"Optimal trajectory cost: {optimal_trajectory.total_cost:.4f}")

    print("\nMarket impact analysis test completed successfully!")

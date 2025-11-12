"""Advanced stress and gap scenario simulation utilities with regime detection and multi-asset testing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional, List, Union, Any
from abc import ABC, abstractmethod
import numpy as np
from enum import Enum

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats


@dataclass(slots=True)
class StressScenario:
    name: str
    shock_map: Dict[str, float]
    description: str = ""

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        for column, pct in self.shock_map.items():
            if column in frame.columns:
                frame[column] = frame[column] * (1 + pct)
        return frame


@dataclass(slots=True)
class GapScenario:
    """Apply an overnight gap followed by recovery/decay."""

    gap_pct: float
    recovery_steps: int = 1
    column: str = "close"

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            return data
        frame = data.copy()
        gap_index = frame.index[0]
        frame.at[gap_index, self.column] = frame.iloc[0][self.column] * (1 + self.gap_pct)
        if self.recovery_steps > 0:
            step = -self.gap_pct / self.recovery_steps
            for i in range(1, min(self.recovery_steps + 1, len(frame))):
                frame.iat[i, frame.columns.get_loc(self.column)] *= 1 + step
        return frame


class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"


class RegimeBasedScenario:
    """Scenario that adapts based on detected market regime."""

    def __init__(self, regime: MarketRegime, shock_multipliers: Dict[str, float],
                 volatility_multiplier: float = 1.0):
        self.regime = regime
        self.shock_multipliers = shock_multipliers
        self.volatility_multiplier = volatility_multiplier

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()

        # Apply regime-specific shocks
        for column, multiplier in self.shock_multipliers.items():
            if column in frame.columns:
                if self.regime == MarketRegime.BULL:
                    # Bull market: positive shocks, lower volatility
                    frame[column] = frame[column] * (1 + multiplier * 0.5)
                elif self.regime == MarketRegime.BEAR:
                    # Bear market: negative shocks, higher volatility
                    frame[column] = frame[column] * (1 - multiplier)
                elif self.regime == MarketRegime.SIDEWAYS:
                    # Sideways: minimal directional movement, low volatility
                    frame[column] = frame[column] * (1 + multiplier * 0.1)
                elif self.regime == MarketRegime.HIGH_VOLATILITY:
                    # High volatility: amplified moves in both directions
                    frame[column] = frame[column] * (1 + multiplier * np.random.choice([-1, 1]))

        # Apply volatility adjustment
        if 'close' in frame.columns:
            returns = frame['close'].pct_change().fillna(0)
            frame['close'] = frame['close'].iloc[0] * (1 + returns * self.volatility_multiplier).cumprod()

        return frame


class MultiAssetStressScenario:
    """Stress scenario for multiple correlated assets."""

    def __init__(self, name: str, asset_shocks: Dict[str, Dict[str, float]],
                 correlation_matrix: Optional[pd.DataFrame] = None):
        self.name = name
        self.asset_shocks = asset_shocks  # {asset: {column: shock_pct}}
        self.correlation_matrix = correlation_matrix

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()

        # Apply shocks to each asset
        for asset, shocks in self.asset_shocks.items():
            asset_columns = [col for col in frame.columns if col.startswith(f"{asset}_")]
            if not asset_columns:
                # Assume single asset data
                for column, shock_pct in shocks.items():
                    if column in frame.columns:
                        frame[column] = frame[column] * (1 + shock_pct)

        # Apply correlation effects if matrix provided
        if self.correlation_matrix is not None:
            self._apply_correlation_effects(frame)

        return frame

    def _apply_correlation_effects(self, data: pd.DataFrame) -> None:
        """Apply correlation-based contagion effects."""
        assets = list(self.correlation_matrix.columns)

        for i, asset_i in enumerate(assets):
            shock_i = self.asset_shocks.get(asset_i, {}).get('close', 0)

            for j, asset_j in enumerate(assets):
                if i != j:
                    correlation = self.correlation_matrix.loc[asset_i, asset_j]
                    contagion_shock = shock_i * correlation * 0.5  # Dampened contagion

                    asset_columns = [col for col in data.columns if col.startswith(f"{asset_j}_")]
                    if asset_columns:
                        for col in asset_columns:
                            if 'close' in col:
                                data[col] = data[col] * (1 + contagion_shock)


class CircuitBreakerScenario:
    """Scenario simulating market circuit breakers and trading halts."""

    def __init__(self, trigger_threshold: float = 0.1, halt_duration: int = 5,
                 breaker_levels: List[float] = None):
        self.trigger_threshold = trigger_threshold
        self.halt_duration = halt_duration
        self.breaker_levels = breaker_levels or [0.07, 0.13, 0.20]

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        if 'close' not in frame.columns:
            return frame

        prices = frame['close'].values
        halted_periods = []

        for i in range(1, len(prices)):
            daily_return = (prices[i] - prices[i-1]) / prices[i-1]

            if abs(daily_return) >= self.trigger_threshold:
                # Trigger circuit breaker
                level = min(self.breaker_levels, key=lambda x: abs(abs(daily_return) - x))
                halt_start = i
                halt_end = min(i + self.halt_duration, len(prices))

                # Price freezes during halt
                for j in range(halt_start, halt_end):
                    prices[j] = prices[halt_start-1]

                halted_periods.append((halt_start, halt_end))

        frame['close'] = prices
        return frame


class LiquidityCrunchScenario:
    """Scenario simulating liquidity dry-up and widening spreads."""

    def __init__(self, spread_multiplier: float = 5.0, volume_drop: float = 0.8,
                 duration: int = 10):
        self.spread_multiplier = spread_multiplier
        self.volume_drop = volume_drop
        self.duration = duration

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()

        # Simulate liquidity crunch in the middle of the period
        mid_point = len(frame) // 2
        start_idx = max(0, mid_point - self.duration // 2)
        end_idx = min(len(frame), mid_point + self.duration // 2)

        # Widen spreads (if spread columns exist)
        spread_cols = [col for col in frame.columns if 'spread' in col.lower()]
        for col in spread_cols:
            frame.loc[start_idx:end_idx, col] *= self.spread_multiplier

        # Reduce volume
        volume_cols = [col for col in frame.columns if 'volume' in col.lower()]
        for col in volume_cols:
            frame.loc[start_idx:end_idx, col] *= (1 - self.volume_drop)

        # Add slippage to price movements
        if 'close' in frame.columns:
            price_changes = frame['close'].pct_change().fillna(0)
            # During crunch, add random slippage
            slippage = np.random.normal(0, 0.001, len(frame))  # 0.1% average slippage
            slippage[start_idx:end_idx] *= self.spread_multiplier
            frame['close'] *= (1 + slippage)

        return frame


class BlackSwanScenario:
    """Extreme tail risk event simulation."""

    def __init__(self, probability: float = 0.001, magnitude: float = 0.15,
                 recovery_periods: int = 20):
        self.probability = probability
        self.magnitude = magnitude
        self.recovery_periods = recovery_periods

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        if 'close' not in frame.columns:
            return frame

        # Randomly trigger black swan event
        if np.random.random() < self.probability:
            event_idx = np.random.randint(len(frame) // 4, 3 * len(frame) // 4)  # Middle 50%

            # Apply shock
            shock = np.random.choice([-1, 1]) * self.magnitude
            frame.loc[event_idx:, 'close'] *= (1 + shock)

            # Gradual recovery
            if self.recovery_periods > 0:
                recovery_indices = range(event_idx, min(event_idx + self.recovery_periods, len(frame)))
                recovery_factors = np.linspace(1 + shock, 1, len(recovery_indices))

                for i, idx in enumerate(recovery_indices):
                    frame.loc[idx, 'close'] = frame.loc[event_idx-1, 'close'] * recovery_factors[i]

        return frame


class RegimeDetectionEngine:
    """Machine learning-based market regime detection."""

    def __init__(self, n_regimes: int = 4, lookback_window: int = 252):
        self.n_regimes = n_regimes
        self.lookback_window = lookback_window
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_regimes, random_state=42)
        self.is_fitted = False

    def fit(self, data: pd.DataFrame) -> None:
        """Fit regime detection model on historical data."""
        if 'close' not in data.columns:
            return

        # Create features for regime detection
        returns = data['close'].pct_change().fillna(0)
        volatility = returns.rolling(self.lookback_window).std().fillna(0)
        trend = data['close'].rolling(self.lookback_window).mean().pct_change().fillna(0)
        volume = data.get('volume', pd.Series(1, index=data.index))

        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'trend': trend,
            'volume': volume
        }).fillna(0)

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        # Fit clustering model
        self.kmeans.fit(scaled_features)
        self.is_fitted = True

    def detect_regime(self, data: pd.DataFrame) -> MarketRegime:
        """Detect current market regime."""
        if not self.is_fitted:
            return MarketRegime.SIDEWAYS

        # Get latest features
        latest_returns = data['close'].pct_change().iloc[-1] if len(data) > 1 else 0
        latest_volatility = data['close'].pct_change().rolling(20).std().iloc[-1] if len(data) > 20 else 0.02
        latest_trend = data['close'].rolling(20).mean().pct_change().iloc[-1] if len(data) > 20 else 0
        latest_volume = data.get('volume', pd.Series(1, index=data.index)).iloc[-1] if len(data) > 0 else 1

        features = np.array([[latest_returns, latest_volatility, latest_trend, latest_volume]])
        scaled_features = self.scaler.transform(features)

        regime_cluster = self.kmeans.predict(scaled_features)[0]

        # Map clusters to regimes (simplified mapping)
        if regime_cluster == 0:
            return MarketRegime.BULL
        elif regime_cluster == 1:
            return MarketRegime.BEAR
        elif regime_cluster == 2:
            return MarketRegime.HIGH_VOLATILITY
        else:
            return MarketRegime.SIDEWAYS


class ScenarioGenerator:
    """Automated scenario generation engine."""

    def __init__(self, base_data: pd.DataFrame):
        self.base_data = base_data
        self.regime_detector = RegimeDetectionEngine()
        self.regime_detector.fit(base_data)

    def generate_stress_scenarios(self, n_scenarios: int = 10) -> List[StressScenario]:
        """Generate diverse stress scenarios based on historical patterns."""
        scenarios = []

        # Historical scenarios
        returns = self.base_data['close'].pct_change().dropna()

        for i in range(n_scenarios):
            # Sample from historical distribution
            shock_pct = np.random.choice(returns, size=1)[0] * np.random.uniform(2, 5)
            shock_pct = np.clip(shock_pct, -0.5, 0.5)  # Reasonable bounds

            scenario = StressScenario(
                name=f"Historical_Stress_{i+1}",
                shock_map={"close": shock_pct},
                description=f"Historical pattern stress test {i+1}"
            )
            scenarios.append(scenario)

        return scenarios

    def generate_regime_scenarios(self) -> List[RegimeBasedScenario]:
        """Generate regime-aware scenarios."""
        scenarios = []

        for regime in MarketRegime:
            shock_multipliers = {
                "close": 0.05,  # Base shock
                "high": 0.03,
                "low": -0.03,
                "volume": 0.5
            }

            scenario = RegimeBasedScenario(
                regime=regime,
                shock_multipliers=shock_multipliers,
                volatility_multiplier=1.5 if regime == MarketRegime.HIGH_VOLATILITY else 1.0
            )
            scenarios.append(scenario)

        return scenarios


def run_scenarios(
    data: pd.DataFrame,
    scenarios: Iterable[Union[StressScenario, RegimeBasedScenario, MultiAssetStressScenario, Any]],
    runner: Callable[[pd.DataFrame], float],
) -> pd.DataFrame:
    """Evaluate multiple scenarios returning the metric produced by runner."""

    results = []
    for scenario in scenarios:
        shocked = scenario.apply(data)
        metric = runner(shocked)

        # Extract scenario info
        name = getattr(scenario, 'name', str(type(scenario).__name__))
        description = getattr(scenario, 'description', '')

        results.append({
            "scenario": name,
            "metric": metric,
            "description": description,
            "scenario_type": type(scenario).__name__
        })
    return pd.DataFrame(results)


def run_multi_asset_scenarios(
    data: pd.DataFrame,
    scenarios: Iterable[MultiAssetStressScenario],
    runner: Callable[[pd.DataFrame], Dict[str, float]],
) -> pd.DataFrame:
    """Run multi-asset scenarios and aggregate results."""

    all_results = []
    for scenario in scenarios:
        shocked = scenario.apply(data)
        metrics = runner(shocked)

        for asset, metric in metrics.items():
            all_results.append({
                "scenario": scenario.name,
                "asset": asset,
                "metric": metric,
                "description": getattr(scenario, 'description', '')
            })

    return pd.DataFrame(all_results)


def create_extreme_scenarios(data: pd.DataFrame, n_scenarios: int = 5) -> List[StressScenario]:
    """Create extreme but plausible scenarios based on historical data."""

    returns = data['close'].pct_change().dropna()
    scenarios = []

    # Statistical extremes
    confidence_levels = [0.99, 0.995, 0.999]

    for i, conf_level in enumerate(confidence_levels[:n_scenarios]):
        # Calculate VaR at different confidence levels
        var = np.percentile(returns, (1 - conf_level) * 100)
        shock_pct = abs(var) * np.random.uniform(1.5, 3.0)  # Amplify the shock

        scenario = StressScenario(
            name=f"Extreme_VaR_{int(conf_level*100)}%",
            shock_map={"close": shock_pct},
            description=f"Extreme scenario based on {int(conf_level*100)}% VaR"
        )
        scenarios.append(scenario)

    return scenarios


def create_correlation_break_scenarios(
    data: pd.DataFrame,
    assets: List[str],
    base_correlations: pd.DataFrame
) -> List[MultiAssetStressScenario]:
    """Create scenarios where correlations break down."""

    scenarios = []

    # Correlation breakdown scenario
    shock_map = {}
    for asset in assets:
        # Random shock for each asset
        shock_map[asset] = {"close": np.random.uniform(-0.1, 0.1)}

    # Use identity matrix for zero correlation
    zero_corr = pd.DataFrame(np.eye(len(assets)), index=assets, columns=assets)

    scenario = MultiAssetStressScenario(
        name="Correlation_Breakdown",
        asset_shocks=shock_map,
        correlation_matrix=zero_corr
    )
    scenarios.append(scenario)

    # High correlation contagion scenario
    high_corr = base_correlations * 1.5  # Amplify correlations
    np.fill_diagonal(high_corr.values, 1.0)  # Keep diagonal as 1

    scenario = MultiAssetStressScenario(
        name="High_Correlation_Contagion",
        asset_shocks=shock_map,
        correlation_matrix=high_corr
    )
    scenarios.append(scenario)

    return scenarios


def benchmark_scenario_performance(
    data: pd.DataFrame,
    scenarios: List[Any],
    runner: Callable[[pd.DataFrame], float],
    baseline_metric: float
) -> pd.DataFrame:
    """Benchmark scenario performance against baseline."""

    results = run_scenarios(data, scenarios, runner)

    # Add baseline comparison
    results['baseline_metric'] = baseline_metric
    results['performance_vs_baseline'] = results['metric'] - baseline_metric
    results['performance_pct'] = (results['metric'] / baseline_metric - 1) * 100

    # Sort by performance impact
    results = results.sort_values('performance_vs_baseline', ascending=True)

    return results


__all__ = [
    "StressScenario",
    "GapScenario",
    "MarketRegime",
    "RegimeBasedScenario",
    "MultiAssetStressScenario",
    "CircuitBreakerScenario",
    "LiquidityCrunchScenario",
    "BlackSwanScenario",
    "RegimeDetectionEngine",
    "ScenarioGenerator",
    "run_scenarios",
    "run_multi_asset_scenarios",
    "create_extreme_scenarios",
    "create_correlation_break_scenarios",
    "benchmark_scenario_performance",
]


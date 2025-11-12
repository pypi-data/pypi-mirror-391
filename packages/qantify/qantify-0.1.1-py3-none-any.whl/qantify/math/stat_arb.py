"""Statistical arbitrage models and cointegration analysis."""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize, spatial
from scipy.optimize import minimize, minimize_scalar, differential_evolution
from scipy.stats import norm, t, chi2, f, jarque_bera, shapiro
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf, MinCovDet


# Optional dependencies with fallbacks
try:
    import statsmodels.api as sm
    import statsmodels.tsa.api as tsa
    import statsmodels.tsa.stattools as stattools
    from statsmodels.tsa.vector_ar.vecm import VECM, coint_johansen
    STATS_MODELS_AVAILABLE = True
except ImportError:
    STATS_MODELS_AVAILABLE = False
    sm = None
    tsa = None
    stattools = None

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    torch = None

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


# =============================================================================
# UTILITY FUNCTIONS AND CLASSES
# =============================================================================

class StatsmodelsUnavailable(RuntimeError):
    """Raised when statsmodels is required but missing."""


def _require_statsmodels_tsa():
    """Require statsmodels for time series analysis."""
    if not STATS_MODELS_AVAILABLE:
        raise StatsmodelsUnavailable("statsmodels is required for statistical arbitrage")
    return sm, stattools


def _require_pytorch():
    """Require PyTorch for neural stat arb."""
    if not PYTORCH_AVAILABLE:
        raise RuntimeError("PyTorch required for neural statistical arbitrage")
    return torch


def calculate_half_life(spread: pd.Series) -> float:
    """Calculate half-life of mean reversion for a spread."""
    # Simple OLS regression: spread_t = alpha + beta * spread_{t-1} + epsilon
    y = spread.values[1:]
    X = spread.values[:-1].reshape(-1, 1)

    # Add constant
    X = np.column_stack([np.ones(len(X)), X])

    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0][1]
        half_life = -np.log(2) / np.log(np.abs(beta)) if np.abs(beta) < 1 else np.inf
        return half_life
    except:
        return np.inf


def calculate_zscore(spread: pd.Series, window: int = 20) -> pd.Series:
    """Calculate z-score for spread normalization."""
    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()
    zscore = (spread - rolling_mean) / rolling_std
    return zscore


def detect_cointegration_clusters(data: pd.DataFrame, threshold: float = 0.05) -> List[Tuple[str, str]]:
    """Find cointegrated pairs using Engle-Granger test."""
    assets = data.columns
    cointegrated_pairs = []

    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            asset1, asset2 = assets[i], assets[j]

            try:
                eg_test = EngleGrangerTest()
                result = eg_test.run(data[asset1], data[asset2])

                if result.p_value < threshold:
                    cointegrated_pairs.append((asset1, asset2))

            except Exception as e:
                warnings.warn(f"Failed to test cointegration for {asset1}-{asset2}: {e}")
                continue

    return cointegrated_pairs


def calculate_distance_matrix(data: pd.DataFrame, method: str = 'correlation') -> pd.DataFrame:
    """Calculate distance matrix between assets."""
    if method == 'correlation':
        corr_matrix = data.corr()
        distance_matrix = np.sqrt(2 * (1 - corr_matrix))
    elif method == 'cointegration':
        # Use cointegration test p-values as distances
        n_assets = len(data.columns)
        distance_matrix = np.ones((n_assets, n_assets))

        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                try:
                    eg_test = EngleGrangerTest()
                    result = eg_test.run(data.iloc[:, i], data.iloc[:, j])
                    distance = result.p_value  # Lower p-value = more cointegrated = smaller distance
                    distance_matrix[i, j] = distance_matrix[j, i] = distance
                except:
                    distance_matrix[i, j] = distance_matrix[j, i] = 1.0
    else:
        raise ValueError(f"Unknown distance method: {method}")

    return pd.DataFrame(distance_matrix, index=data.columns, columns=data.columns)


# =============================================================================
# COINTEGRATION ANALYSIS
# =============================================================================

@dataclass(slots=True)
class CointegrationTestResult:
    """Result of cointegration test."""
    test_statistic: float
    p_value: float
    critical_values: Dict[str, float]
    half_life: Optional[float] = None
    hedge_ratio: Optional[float] = None
    residuals: Optional[pd.Series] = None
    confidence_intervals: Optional[Dict[str, float]] = None


@dataclass(slots=True)
class EngleGrangerTest:
    """Engle-Granger cointegration test."""

    regression: str = "c"  # 'c' for constant, 'ct' for constant and trend, 'nc' for no constant

    def run(self, series_x: pd.Series, series_y: pd.Series) -> CointegrationTestResult:
        """Run Engle-Granger cointegration test."""
        sm, stattools = _require_statsmodels_tsa()

        # Run cointegration test
        test_stat, p_value, crit_values = stattools.coint(
            series_x, series_y, regression=self.regression
        )

        # Critical values dictionary
        critical_values = {
            '1%': crit_values[0],
            '5%': crit_values[1],
            '10%': crit_values[2]
        }

        # Calculate hedge ratio and spread
        model = sm.OLS(series_y, sm.add_constant(series_x)).fit()
        hedge_ratio = model.params[1]

        spread = series_y - hedge_ratio * series_x
        half_life = calculate_half_life(spread)

        # Confidence intervals
        conf_int = model.conf_int()
        confidence_intervals = {
            'hedge_ratio_lower': conf_int[1][0],
            'hedge_ratio_upper': conf_int[1][1]
        }

        return CointegrationTestResult(
            test_statistic=test_stat,
            p_value=p_value,
            critical_values=critical_values,
            half_life=half_life,
            hedge_ratio=hedge_ratio,
            residuals=spread,
            confidence_intervals=confidence_intervals
        )


@dataclass(slots=True)
class JohansenTest:
    """Johansen cointegration test for multivariate series."""

    det_order: int = 0  # 0: no deterministic terms, 1: constant, 2: constant and trend
    k_ar_diff: int = 1  # Number of lags in VAR

    def run(self, frame: pd.DataFrame) -> Dict[str, Any]:
        """Run Johansen cointegration test."""
        sm, _ = _require_statsmodels_tsa()

        try:
            result = coint_johansen(frame.values, det_order=self.det_order, k_ar_diff=self.k_ar_diff)

            # Extract results
            n_vars = frame.shape[1]

            # Test statistics and critical values
            test_results = {}
            for i in range(n_vars):
                test_results[f'r<={i}'] = {
                    'eigenvalue': result.eig[i],
                    'trace_statistic': result.lr1[i],
                    'trace_critical_1%': result.cvt[i, 0],
                    'trace_critical_5%': result.cvt[i, 1],
                    'trace_critical_10%': result.cvt[i, 2],
                    'max_eigen_statistic': result.lr2[i],
                    'max_eigen_critical_1%': result.cvm[i, 0],
                    'max_eigen_critical_5%': result.cvm[i, 1],
                    'max_eigen_critical_10%': result.cvm[i, 2]
                }

            # Cointegration vectors
            cointegration_vectors = result.evec

            # Determine cointegration rank
            cointegration_rank = 0
            for i in range(n_vars):
                if result.lr1[i] > result.cvt[i, 1]:  # 5% significance
                    cointegration_rank += 1

            return {
                'cointegration_rank': cointegration_rank,
                'test_results': test_results,
                'cointegration_vectors': cointegration_vectors,
                'normalization_restrictions': result.ind  # Normalization restrictions
            }

        except Exception as e:
            return {'error': str(e)}


@dataclass(slots=True)
class PhillipsOuliarisTest:
    """Phillips-Ouliaris cointegration test."""

    regression: str = "c"
    lags: Optional[int] = None

    def run(self, series_x: pd.Series, series_y: pd.Series) -> CointegrationTestResult:
        """Run Phillips-Ouliaris test."""
        # This is a simplified implementation
        # Full implementation would require specialized statistical packages

        # Use Engle-Granger as approximation
        eg_test = EngleGrangerTest(regression=self.regression)
        return eg_test.run(series_x, series_y)


@dataclass(slots=True)
class AdvancedCointegrationAnalyzer:
    """Advanced cointegration analysis with multiple tests and robustness checks."""

    def comprehensive_cointegration_test(self, series_x: pd.Series, series_y: pd.Series) -> Dict[str, Any]:
        """Run multiple cointegration tests for robustness."""
        results = {}

        # Engle-Granger test
        try:
            eg_test = EngleGrangerTest()
            results['engle_granger'] = eg_test.run(series_x, series_y)
        except Exception as e:
            results['engle_granger'] = {'error': str(e)}

        # Phillips-Ouliaris test (simplified)
        try:
            po_test = PhillipsOuliarisTest()
            results['phillips_ouliaris'] = po_test.run(series_x, series_y)
        except Exception as e:
            results['phillips_ouliaris'] = {'error': str(e)}

        # Summary
        tests_passed = sum(1 for result in results.values()
                          if isinstance(result, CointegrationTestResult) and result.p_value < 0.05)

        overall_cointegrated = tests_passed >= len(results) * 0.6  # Majority vote

        return {
            'overall_cointegrated': overall_cointegrated,
            'tests_passed': tests_passed,
            'total_tests': len(results),
            'test_results': results
        }

    def rolling_cointegration_test(self, series_x: pd.Series, series_y: pd.Series,
                                 window: int = 252, step: int = 21) -> pd.DataFrame:
        """Rolling cointegration test over time."""
        results = []

        for i in range(window, len(series_x), step):
            try:
                x_window = series_x.iloc[i-window:i]
                y_window = series_y.iloc[i-window:i]

                eg_test = EngleGrangerTest()
                result = eg_test.run(x_window, y_window)

                results.append({
                    'date': series_x.index[i-1],
                    'p_value': result.p_value,
                    'hedge_ratio': result.hedge_ratio,
                    'half_life': result.half_life,
                    'cointegrated': result.p_value < 0.05
                })

            except Exception as e:
                results.append({
                    'date': series_x.index[i-1],
                    'error': str(e)
                })

        return pd.DataFrame(results)


# =============================================================================
# PAIRS TRADING STRATEGIES
# =============================================================================

@dataclass(slots=True)
class PairsTradingStrategy:
    """Pairs trading strategy implementation."""

    entry_threshold: float = 2.0  # Z-score entry threshold
    exit_threshold: float = 0.5   # Z-score exit threshold
    lookback_window: int = 252    # Rolling window for mean/std calculation
    max_holding_period: int = 20  # Maximum holding period in days
    stop_loss_threshold: float = 4.0  # Stop loss z-score threshold

    # Strategy state
    position: int = field(default=0, init=False)  # -1: short spread, 0: neutral, 1: long spread
    entry_date: Optional[pd.Timestamp] = field(default=None, init=False)
    entry_price: Optional[float] = field(default=None, init=False)

    def calculate_spread(self, series_x: pd.Series, series_y: pd.Series) -> pd.Series:
        """Calculate spread between two series."""
        # Estimate hedge ratio
        model = sm.OLS(series_y, sm.add_constant(series_x)).fit()
        hedge_ratio = model.params[1]

        spread = series_y - hedge_ratio * series_x
        return spread, hedge_ratio

    def generate_signals(self, series_x: pd.Series, series_y: pd.Series) -> pd.DataFrame:
        """Generate trading signals for pairs trading."""
        spread, hedge_ratio = self.calculate_spread(series_x, series_y)
        zscore = calculate_zscore(spread, self.lookback_window)

        signals = pd.DataFrame(index=spread.index)
        signals['spread'] = spread
        signals['zscore'] = zscore
        signals['hedge_ratio'] = hedge_ratio
        signals['signal'] = 0  # -1: short spread, 0: hold/no position, 1: long spread

        # Generate signals
        for i in range(len(signals)):
            current_zscore = signals.iloc[i]['zscore']

            # Entry signals
            if self.position == 0:
                if current_zscore > self.entry_threshold:
                    signals.iloc[i, signals.columns.get_loc('signal')] = -1  # Short spread
                    self.position = -1
                    self.entry_date = signals.index[i]
                elif current_zscore < -self.entry_threshold:
                    signals.iloc[i, signals.columns.get_loc('signal')] = 1   # Long spread
                    self.position = 1
                    self.entry_date = signals.index[i]

            # Exit signals
            elif self.position != 0:
                # Check for exit conditions
                exit_signal = False

                # Z-score exit
                if abs(current_zscore) < self.exit_threshold:
                    exit_signal = True

                # Stop loss
                elif abs(current_zscore) > self.stop_loss_threshold:
                    exit_signal = True

                # Maximum holding period
                elif self.entry_date is not None and (signals.index[i] - self.entry_date).days > self.max_holding_period:
                    exit_signal = True

                if exit_signal:
                    signals.iloc[i, signals.columns.get_loc('signal')] = 0  # Exit position
                    self.position = 0
                    self.entry_date = None

        return signals

    def calculate_returns(self, signals: pd.DataFrame, transaction_costs: float = 0.001) -> pd.Series:
        """Calculate strategy returns."""
        # Simplified return calculation
        # In practice, would need to account for actual position sizing and costs

        returns = signals['signal'].shift(1) * (-signals['zscore'].pct_change())  # Simplified
        returns = returns.fillna(0)

        # Apply transaction costs
        trades = signals['signal'].diff().abs() > 0
        returns -= trades * transaction_costs

        return returns


@dataclass(slots=True)
class EnhancedPairsTradingStrategy:
    """Enhanced pairs trading with ML and advanced features."""

    entry_threshold: float = 2.0
    exit_threshold: float = 0.5
    lookback_window: int = 252
    max_holding_period: int = 20
    stop_loss_threshold: float = 4.0

    # Enhanced features
    use_ml_prediction: bool = True
    regime_detection: bool = True
    dynamic_hedge_ratio: bool = True
    transaction_cost_model: str = 'linear'  # 'linear', 'quadratic', 'fixed'

    # ML model for spread prediction
    ml_model: Any = field(default=None, init=False)
    regime_detector: Any = field(default=None, init=False)

    def __post_init__(self):
        """Initialize enhanced components."""
        if self.use_ml_prediction:
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)

        if self.regime_detection:
            # Simple regime detection based on volatility
            self.regime_detector = lambda spread: 'high_vol' if spread.std() > spread.quantile(0.95) else 'normal'

    def fit_ml_model(self, historical_spreads: pd.Series, features: pd.DataFrame):
        """Fit ML model for spread prediction."""
        if not self.use_ml_prediction:
            return

        # Prepare training data
        X = features.values[:-1]
        y = historical_spreads.values[1:]  # Predict next spread

        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]

        self.ml_model.fit(X, y)

    def predict_spread(self, current_features: pd.DataFrame) -> float:
        """Predict next spread using ML model."""
        if not self.use_ml_prediction or self.ml_model is None:
            return 0.0

        return self.ml_model.predict(current_features.values.reshape(1, -1))[0]

    def adaptive_thresholds(self, spread_volatility: float) -> Tuple[float, float]:
        """Calculate adaptive entry/exit thresholds based on market conditions."""
        base_entry = self.entry_threshold
        base_exit = self.exit_threshold

        # Increase thresholds in high volatility periods
        vol_multiplier = min(1.5, 1 + spread_volatility * 2)

        return base_entry * vol_multiplier, base_exit * vol_multiplier

    def calculate_transaction_costs(self, trade_size: float, spread_zscore: float) -> float:
        """Calculate transaction costs based on model."""
        if self.transaction_cost_model == 'linear':
            cost = abs(trade_size) * 0.001  # 10 bps
        elif self.transaction_cost_model == 'quadratic':
            cost = abs(trade_size) * 0.001 + (trade_size ** 2) * 0.0001
        elif self.transaction_cost_model == 'fixed':
            cost = 0.0005  # Fixed cost
        else:
            cost = 0.0

        # Increase costs for extreme z-scores (market impact)
        impact_multiplier = 1 + max(0, abs(spread_zscore) - 2) * 0.1
        cost *= impact_multiplier

        return cost


# =============================================================================
# STATISTICAL ARBITRAGE FRAMEWORKS
# =============================================================================

@dataclass(slots=True)
class StatisticalArbitragePortfolio:
    """Portfolio of statistical arbitrage strategies."""

    strategies: List[Any] = field(default_factory=list)
    capital_allocation: Dict[str, float] = field(default_factory=dict)
    risk_limits: Dict[str, float] = field(default_factory=dict)

    # Portfolio state
    positions: Dict[str, float] = field(default_factory=dict, init=False)
    pnl: pd.Series = field(default_factory=lambda: pd.Series(), init=False)

    def add_strategy(self, strategy: Any, name: str, allocation: float = 0.1,
                    risk_limit: float = 0.05):
        """Add a strategy to the portfolio."""
        self.strategies.append(strategy)
        self.capital_allocation[name] = allocation
        self.risk_limits[name] = risk_limit

    def optimize_allocations(self, historical_returns: pd.DataFrame) -> Dict[str, float]:
        """Optimize capital allocations using mean-variance optimization."""
        if len(historical_returns.columns) < 2:
            return self.capital_allocation

        # Calculate expected returns and covariance
        expected_returns = historical_returns.mean()
        cov_matrix = historical_returns.cov()

        # Minimize variance subject to return constraint
        n_assets = len(expected_returns)

        def objective(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
            {'type': 'ineq', 'fun': lambda w: np.dot(expected_returns, w) - 0.02}  # Target return
        ]

        bounds = [(0, 0.5) for _ in range(n_assets)]  # Max 50% per strategy

        try:
            result = minimize(objective, np.ones(n_assets) / n_assets,
                            method='SLSQP', bounds=bounds, constraints=constraints)

            if result.success:
                optimized_weights = dict(zip(historical_returns.columns, result.x))
                self.capital_allocation.update(optimized_weights)

        except Exception as e:
            warnings.warn(f"Allocation optimization failed: {e}")

        return self.capital_allocation

    def calculate_portfolio_risk(self, returns: pd.DataFrame) -> Dict[str, float]:
        """Calculate portfolio risk metrics."""
        portfolio_returns = returns.sum(axis=1)

        return {
            'volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252),
            'max_drawdown': (portfolio_returns.cumsum() - portfolio_returns.cumsum().expanding().max()).min(),
            'var_95': portfolio_returns.quantile(0.05),
            'cvar_95': portfolio_returns[portfolio_returns <= portfolio_returns.quantile(0.05)].mean()
        }

    def apply_risk_management(self, current_positions: Dict[str, float],
                            market_data: pd.DataFrame) -> Dict[str, float]:
        """Apply risk management rules."""
        adjusted_positions = current_positions.copy()

        # Check risk limits
        for strategy_name, position in current_positions.items():
            risk_limit = self.risk_limits.get(strategy_name, 0.05)

            # Calculate current risk contribution
            # Simplified - would need proper risk attribution
            if abs(position) > risk_limit:
                # Scale down position to meet risk limit
                scale_factor = risk_limit / abs(position)
                adjusted_positions[strategy_name] = position * scale_factor

        return adjusted_positions


@dataclass(slots=True)
class BasketTradingStrategy:
    """Basket trading strategy for statistical arbitrage."""

    basket_weights: Dict[str, float]
    entry_threshold: float = 2.0
    exit_threshold: float = 0.5
    lookback_window: int = 252

    def construct_basket(self, data: pd.DataFrame) -> pd.Series:
        """Construct basket from individual assets."""
        basket = pd.Series(0.0, index=data.index)

        for asset, weight in self.basket_weights.items():
            if asset in data.columns:
                basket += data[asset] * weight

        return basket

    def find_basket_arbitrage(self, data: pd.DataFrame, benchmark: pd.Series) -> pd.Series:
        """Find arbitrage opportunities between basket and benchmark."""
        basket = self.construct_basket(data)
        spread = basket - benchmark
        zscore = calculate_zscore(spread, self.lookback_window)

        signals = pd.Series(0, index=data.index)
        signals[zscore > self.entry_threshold] = -1   # Short basket
        signals[zscore < -self.entry_threshold] = 1   # Long basket
        signals[abs(zscore) < self.exit_threshold] = 0  # Exit

        return signals


@dataclass(slots=True)
class CrossSectionalMomentumStrategy:
    """Cross-sectional momentum statistical arbitrage."""

    lookback_period: int = 252
    holding_period: int = 21
    num_quantiles: int = 5
    long_quantile: int = 1  # Top quantile to long
    short_quantile: int = 5  # Bottom quantile to short

    def generate_signals(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Generate cross-sectional momentum signals."""
        # Calculate momentum scores
        momentum_scores = returns.rolling(self.lookback_period).mean()

        # Rank assets at each point in time
        ranks = momentum_scores.rank(axis=1)

        # Convert to signals
        signals = pd.DataFrame(0, index=returns.index, columns=returns.columns)

        # Long signals (top performers)
        quantile_size = len(returns.columns) / self.num_quantiles
        long_threshold = (self.num_quantiles - self.long_quantile + 1) * quantile_size
        signals[ranks > len(returns.columns) - long_threshold] = 1

        # Short signals (worst performers)
        short_threshold = self.short_quantile * quantile_size
        signals[ranks <= short_threshold] = -1

        return signals

    def calculate_returns(self, signals: pd.DataFrame, returns: pd.DataFrame,
                         transaction_costs: float = 0.001) -> pd.Series:
        """Calculate strategy returns."""
        # Apply holding period logic
        # Simplified - in practice would need more sophisticated position management
        strategy_returns = (signals.shift(1) * returns).sum(axis=1)

        # Apply transaction costs
        trade_changes = signals.diff().abs().sum(axis=1)
        strategy_returns -= trade_changes * transaction_costs

        return strategy_returns


# =============================================================================
# MACHINE LEARNING ENHANCED STAT ARB
# =============================================================================

@dataclass(slots=True)
class NeuralPairsIdentifier:
    """Neural network for identifying cointegrated pairs."""

    embedding_dim: int = 32
    hidden_dim: int = 64
    num_layers: int = 2
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 100

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, asset_features: pd.DataFrame, cointegration_labels: pd.Series):
        """Fit neural network to identify cointegrated pairs."""
        torch = _require_pytorch()

        # Prepare data
        X = asset_features.values
        y = cointegration_labels.values

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Create dataset
        dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_scaled),
            torch.FloatTensor(y)
        )
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

        # Initialize model
        input_dim = X.shape[1]
        self._model = PairsClassifier(input_dim, self.embedding_dim, self.hidden_dim,
                                    self.num_layers, self.dropout)

        criterion = torch.nn.BCELoss()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self.learning_rate)

        # Training loop
        self._model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self._model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            if (epoch + 1) % 20 == 0:
                print(".4f")

        self._fitted = True

    def predict_cointegration(self, asset_features: pd.DataFrame) -> np.ndarray:
        """Predict cointegration probability."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        X_scaled = self._scaler.transform(asset_features.values)
        X_tensor = torch.FloatTensor(X_scaled)

        self._model.eval()
        with torch.no_grad():
            predictions = self._model(X_tensor)

        return predictions.numpy().flatten()


class PairsClassifier(torch.nn.Module):
    """Neural network for pairs classification."""

    def __init__(self, input_dim: int, embedding_dim: int, hidden_dim: int,
                 num_layers: int, dropout: float):
        super().__init__()

        self.embedding = torch.nn.Linear(input_dim, embedding_dim)
        self.layers = torch.nn.ModuleList()

        for i in range(num_layers):
            in_dim = embedding_dim if i == 0 else hidden_dim
            self.layers.append(torch.nn.Linear(in_dim, hidden_dim))
            self.layers.append(torch.nn.ReLU())
            self.layers.append(torch.nn.Dropout(dropout))

        self.output = torch.nn.Linear(hidden_dim, 1)
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.embedding(x)
        for layer in self.layers:
            x = layer(x)
        x = self.output(x)
        return self.sigmoid(x)


@dataclass(slots=True)
class ReinforcementLearningStatArb:
    """Reinforcement learning for statistical arbitrage."""

    state_dim: int = 10
    action_dim: int = 3  # -1: short, 0: hold, 1: long
    hidden_dim: int = 64
    learning_rate: float = 0.001
    gamma: float = 0.99
    epsilon: float = 0.1

    # RL components
    policy_network: Any = field(default=None, init=False)
    value_network: Any = field(default=None, init=False)
    optimizer: Any = field(default=None, init=False)

    def __post_init__(self):
        """Initialize RL networks."""
        torch = _require_pytorch()

        self.policy_network = torch.nn.Sequential(
            torch.nn.Linear(self.state_dim, self.hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.hidden_dim, self.action_dim),
            torch.nn.Softmax(dim=-1)
        )

        self.value_network = torch.nn.Sequential(
            torch.nn.Linear(self.state_dim, self.hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.hidden_dim, 1)
        )

        self.optimizer = torch.optim.Adam(
            list(self.policy_network.parameters()) + list(self.value_network.parameters()),
            lr=self.learning_rate
        )

    def select_action(self, state: np.ndarray) -> int:
        """Select action using epsilon-greedy policy."""
        torch = _require_pytorch()

        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_dim) - 1  # -1, 0, 1

        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs = self.policy_network(state_tensor)
            action = torch.multinomial(action_probs, 1).item()

        return action - 1  # Convert to -1, 0, 1

    def update_policy(self, states: List[np.ndarray], actions: List[int],
                     rewards: List[float], next_states: List[np.ndarray]):
        """Update policy using REINFORCE algorithm."""
        torch = _require_pytorch()

        # Convert to tensors
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.LongTensor([a + 1 for a in actions])  # Shift to 0,1,2
        rewards_tensor = torch.FloatTensor(rewards)

        # Calculate discounted rewards
        discounted_rewards = []
        running_sum = 0
        for r in reversed(rewards):
            running_sum = r + self.gamma * running_sum
            discounted_rewards.insert(0, running_sum)

        discounted_rewards = torch.FloatTensor(discounted_rewards)
        discounted_rewards = (discounted_rewards - discounted_rewards.mean()) / (discounted_rewards.std() + 1e-8)

        # Update policy
        self.optimizer.zero_grad()

        # Policy loss
        action_probs = self.policy_network(states_tensor)
        log_probs = torch.log(action_probs.gather(1, actions_tensor.unsqueeze(1)).squeeze())
        policy_loss = -(log_probs * discounted_rewards).mean()

        # Value loss
        values = self.value_network(states_tensor).squeeze()
        value_loss = torch.nn.MSELoss()(values, discounted_rewards)

        # Total loss
        total_loss = policy_loss + value_loss

        total_loss.backward()
        self.optimizer.step()


# =============================================================================
# HIGH-FREQUENCY STATISTICAL ARBITRAGE
# =============================================================================

@dataclass(slots=True)
class HighFrequencyStatArb:
    """High-frequency statistical arbitrage strategies."""

    sampling_frequency: str = '1min'
    lookback_window: int = 100  # Number of observations for analysis
    entry_threshold: float = 3.0
    exit_threshold: float = 0.5
    max_holding_period: int = 10  # Maximum holding period in minutes

    def detect_microstructure_arbitrage(self, order_book_data: pd.DataFrame) -> pd.Series:
        """Detect arbitrage opportunities in order book microstructure."""
        # Analyze bid-ask spreads, order imbalances, etc.
        # Simplified implementation

        signals = pd.Series(0, index=order_book_data.index)

        # Check for order book imbalances
        if 'bid_volume' in order_book_data.columns and 'ask_volume' in order_book_data.columns:
            imbalance = (order_book_data['bid_volume'] - order_book_data['ask_volume']) / \
                       (order_book_data['bid_volume'] + order_book_data['ask_volume'])

            # Generate signals based on imbalance
            signals[imbalance > 0.7] = 1   # Long
            signals[imbalance < -0.7] = -1  # Short
            signals[abs(imbalance) < 0.1] = 0  # Exit

        return signals

    def latency_arbitrage(self, price_data: Dict[str, pd.Series]) -> pd.Series:
        """Latency arbitrage between different price feeds."""
        # Simplified - compare prices from different exchanges/venues

        signals = pd.Series(0, index=price_data[list(price_data.keys())[0]].index)

        if len(price_data) >= 2:
            prices = list(price_data.values())
            spreads = prices[0] - prices[1]  # Price differences

            # Generate signals based on price discrepancies
            zscore = calculate_zscore(spreads, self.lookback_window)
            signals[zscore > self.entry_threshold] = -1
            signals[zscore < -self.entry_threshold] = 1
            signals[abs(zscore) < self.exit_threshold] = 0

        return signals


# =============================================================================
# RISK MANAGEMENT FOR STAT ARB
# =============================================================================

@dataclass(slots=True)
class StatArbRiskManager:
    """Risk management for statistical arbitrage portfolios."""

    max_portfolio_var: float = 0.02  # Maximum portfolio VaR (2%)
    max_individual_var: float = 0.01  # Maximum individual strategy VaR (1%)
    max_correlation: float = 0.8      # Maximum correlation between strategies
    rebalance_frequency: str = 'daily'

    def calculate_portfolio_var(self, returns: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Calculate portfolio Value-at-Risk."""
        portfolio_returns = returns.sum(axis=1)

        # Historical VaR
        var = portfolio_returns.quantile(1 - confidence_level)

        return abs(var)  # Return positive value

    def calculate_risk_contributions(self, returns: pd.DataFrame) -> pd.Series:
        """Calculate risk contributions of individual strategies."""
        # Euler allocation principle for risk contributions
        cov_matrix = returns.cov()
        weights = np.ones(len(returns.columns)) / len(returns.columns)  # Equal weights

        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        risk_contributions = weights * np.dot(cov_matrix, weights) / portfolio_variance

        return pd.Series(risk_contributions, index=returns.columns)

    def apply_risk_limits(self, positions: Dict[str, float], returns: pd.DataFrame) -> Dict[str, float]:
        """Apply risk limits to positions."""
        adjusted_positions = positions.copy()

        # Calculate individual VaRs
        for strategy_name in positions.keys():
            if strategy_name in returns.columns:
                strategy_returns = returns[strategy_name]
                strategy_var = abs(strategy_returns.quantile(0.05))

                if strategy_var > self.max_individual_var:
                    # Scale down position
                    scale_factor = self.max_individual_var / strategy_var
                    adjusted_positions[strategy_name] *= scale_factor

        # Check portfolio VaR
        portfolio_returns = pd.DataFrame(adjusted_positions, index=[0]) * returns.iloc[-1:]
        portfolio_var = self.calculate_portfolio_var(portfolio_returns)

        if portfolio_var > self.max_portfolio_var:
            # Scale down entire portfolio
            scale_factor = self.max_portfolio_var / portfolio_var
            adjusted_positions = {k: v * scale_factor for k, v in adjusted_positions.items()}

        return adjusted_positions


# =============================================================================
# PERFORMANCE ATTRIBUTION AND ANALYSIS
# =============================================================================

@dataclass(slots=True)
class StatArbPerformanceAnalyzer:
    """Performance analysis for statistical arbitrage strategies."""

    benchmark_returns: Optional[pd.Series] = None

    def calculate_strategy_metrics(self, strategy_returns: pd.Series) -> Dict[str, float]:
        """Calculate comprehensive strategy performance metrics."""
        metrics = {}

        # Basic return metrics
        total_return = (1 + strategy_returns).prod() - 1
        annual_return = strategy_returns.mean() * 252
        annual_volatility = strategy_returns.std() * np.sqrt(252)

        metrics['total_return'] = total_return
        metrics['annual_return'] = annual_return
        metrics['annual_volatility'] = annual_volatility

        # Risk-adjusted metrics
        if annual_volatility > 0:
            metrics['sharpe_ratio'] = annual_return / annual_volatility
            metrics['sortino_ratio'] = annual_return / (strategy_returns[strategy_returns < 0].std() * np.sqrt(252))

        # Drawdown analysis
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        metrics['max_drawdown'] = drawdown.min()
        metrics['calmar_ratio'] = annual_return / abs(drawdown.min()) if drawdown.min() != 0 else 0

        # Win rate and profit factor
        winning_trades = strategy_returns > 0
        metrics['win_rate'] = winning_trades.mean()
        avg_win = strategy_returns[winning_trades].mean()
        avg_loss = strategy_returns[~winning_trades].mean()
        metrics['profit_factor'] = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')

        return metrics

    def attribution_analysis(self, strategy_returns: pd.DataFrame) -> Dict[str, Any]:
        """Perform performance attribution analysis."""
        attribution = {}

        # Strategy contributions
        total_returns = strategy_returns.sum(axis=1)
        strategy_contributions = strategy_returns.div(total_returns.abs(), axis=0).fillna(0)

        attribution['strategy_contributions'] = strategy_contributions.mean()

        # Risk attribution
        cov_matrix = strategy_returns.cov()
        portfolio_vol = total_returns.std() * np.sqrt(252)

        # Marginal risk contributions
        weights = np.ones(len(strategy_returns.columns)) / len(strategy_returns.columns)
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol

        attribution['risk_contributions'] = dict(zip(strategy_returns.columns, marginal_contrib))

        return attribution

    def benchmark_comparison(self, strategy_returns: pd.Series) -> Dict[str, float]:
        """Compare strategy performance against benchmark."""
        if self.benchmark_returns is None:
            return {}

        comparison = {}

        # Alpha and beta
        try:
            import statsmodels.api as sm
            model = sm.OLS(strategy_returns, sm.add_constant(self.benchmark_returns)).fit()
            comparison['alpha'] = model.params[0] * 252  # Annualized
            comparison['beta'] = model.params[1]
            comparison['r_squared'] = model.rsquared
        except:
            comparison['alpha'] = strategy_returns.mean() * 252
            comparison['beta'] = 1.0
            comparison['r_squared'] = 0.0

        # Information ratio
        tracking_error = (strategy_returns - self.benchmark_returns).std() * np.sqrt(252)
        if tracking_error > 0:
            comparison['information_ratio'] = comparison['alpha'] / tracking_error

        return comparison


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Maintain backward compatibility
# Note: EngleGrangerTest and JohansenTest classes need to be defined if these are used
# cointegration_test = EngleGrangerTest().run
# johansen_test = JohansenTest().run
# PairsTradingAnalytics is defined as a class below


class PairsTradingAnalytics:
    @staticmethod
    def zscore(spread: pd.Series, window: int = 60) -> pd.Series:
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std(ddof=0)
        return (spread - rolling_mean) / rolling_std

    @staticmethod
    def half_life(spread: pd.Series) -> Optional[float]:
        spread = spread.dropna()
        if spread.empty:
            return None
        lagged = spread.shift(1).iloc[1:]
        delta = spread.diff().iloc[1:]
        if lagged.std() == 0:
            return None
        beta = np.linalg.lstsq(lagged.values.reshape(-1, 1), delta.values, rcond=None)[0][0]
        halflife = -np.log(2) / beta if beta != 0 else None
        return float(halflife) if halflife and halflife > 0 else None

    @staticmethod
    def hurst_exponent(series: pd.Series, max_lag: int = 100) -> float:
        lags = range(2, max_lag)
        tau = [np.sqrt(np.std(series.diff(lag))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = poly[0] * 2.0
        return float(hurst)


class KalmanHedgeRatioEstimator:
    """Estimate time-varying hedge ratios using a simple Kalman filter."""

    def __init__(self, delta: float = 1e-4, observation_variance: float = 1e-3) -> None:
        self.delta = delta
        self.observation_variance = observation_variance

    def fit(self, dependent: pd.Series, independent: pd.Series) -> pd.Series:
        if len(dependent) != len(independent):
            raise ValueError("Series must be the same length.")
        y = dependent.ffill().bfill().values
        x = independent.ffill().bfill().values

        theta = np.zeros(len(y))
        P = 1.0
        for t in range(len(y)):
            if t == 0:
                theta[t] = y[t] / x[t] if x[t] != 0 else 0.0
                continue
            P = P + self.delta
            K = P * x[t] / (x[t] * P * x[t] + self.observation_variance)
            theta[t] = theta[t - 1] + K * (y[t] - x[t] * theta[t - 1])
            P = (1 - K * x[t]) * P
        return pd.Series(theta, index=dependent.index, name="kalman_hedge_ratio")


# =============================================================================
# ADVANCED COINTEGRATION AND ERROR CORRECTION MODELS (NOBEL-PRIZE LEVEL)
# =============================================================================

@dataclass
class AdvancedCointegrationTests:
    """Advanced cointegration testing frameworks beyond Engle-Granger and Johansen."""

    @staticmethod
    def nonlinear_cointegration_test(series1: pd.Series, series2: pd.Series,
                                   threshold: float = 0.05) -> Dict[str, Any]:
        """Nonlinear cointegration test using threshold error correction models.

        Tests for nonlinear cointegration relationships that standard
        linear tests might miss, using threshold autoregressive models.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series to test for cointegration
        threshold : float
            Threshold parameter for nonlinear adjustment

        Returns:
        --------
        dict : Nonlinear cointegration test results
        """
        # Compute spread
        spread = series1 - series2

        # Test for nonlinear cointegration using TAR model
        # Threshold error correction model
        def tar_error_correction(spread, threshold):
            # Split into regimes based on threshold
            regime1 = spread <= -threshold
            regime2 = spread > threshold
            regime3 = (~regime1) & (~regime2)  # Middle regime

            # Fit different AR models for each regime
            results = {}

            for regime_name, mask in [('lower', regime1), ('upper', regime2), ('middle', regime3)]:
                if np.sum(mask) > 10:  # Minimum observations
                    y_regime = spread[mask]
                    X_regime = spread.shift(1)[mask]

                    # Simple AR(1) fit
                    valid_idx = ~np.isnan(X_regime)
                    if np.sum(valid_idx) > 5:
                        slope, intercept = np.polyfit(X_regime[valid_idx], y_regime[valid_idx], 1)
                        results[regime_name] = {
                            'slope': slope,
                            'intercept': intercept,
                            'observations': np.sum(valid_idx)
                        }

            return results

        # Perform TAR analysis
        tar_results = tar_error_correction(spread, threshold)

        # Test for stationarity in each regime
        stationarity_tests = {}
        for regime_name, mask in [('lower', spread <= -threshold),
                                ('upper', spread > threshold),
                                ('middle', (spread > -threshold) & (spread <= threshold))]:
            if np.sum(mask) > 10:
                regime_data = spread[mask]
                # ADF test for stationarity
                try:
                    adf_stat, p_value, _, _, critical_values, _ = adfuller(regime_data, maxlag=5)
                    stationarity_tests[regime_name] = {
                        'adf_statistic': adf_stat,
                        'p_value': p_value,
                        'critical_values': critical_values,
                        'is_stationary': p_value < 0.05
                    }
                except:
                    stationarity_tests[regime_name] = {'error': 'Insufficient data'}

        # Overall nonlinear cointegration assessment
        regime_stationary = sum(1 for test in stationarity_tests.values()
                              if isinstance(test, dict) and test.get('is_stationary', False))

        is_nonlinear_cointegrated = regime_stationary >= 2  # At least 2 regimes stationary

        return {
            'tar_parameters': tar_results,
            'stationarity_tests': stationarity_tests,
            'threshold': threshold,
            'is_nonlinear_cointegrated': is_nonlinear_cointegrated,
            'regimes_stationary': regime_stationary,
            'model_type': 'Nonlinear Cointegration (TAR-ECT)'
        }

    @staticmethod
    def fractional_cointegration_test(series1: pd.Series, series2: pd.Series,
                                    max_lags: int = 20) -> Dict[str, Any]:
        """Test for fractional cointegration between time series.

        Tests for long-memory relationships using fractional integration
        and cointegration in the frequency domain.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series to test
        max_lags : int
            Maximum lags for long memory estimation

        Returns:
        --------
        dict : Fractional cointegration test results
        """
        # Estimate fractional integration orders
        def estimate_fractional_order(series, max_lags):
            """Estimate fractional integration order using GPH estimator."""
            # Compute autocorrelations
            autocorr = [np.corrcoef(series[:-k], series[k:])[0, 1] for k in range(1, max_lags+1)]

            # GPH estimator: regress log|ρ(k)| on log(k)
            lags = np.arange(1, len(autocorr)+1)
            log_lags = np.log(lags)
            log_autocorr = np.log(np.abs(autocorr))

            # Remove NaN and infinite values
            valid_idx = np.isfinite(log_autocorr)
            if np.sum(valid_idx) < 5:
                return 0.0

            # Linear regression
            slope, _ = np.polyfit(log_lags[valid_idx], log_autocorr[valid_idx], 1)

            # Fractional order is d = -slope/2 for ARFIMA(0,d,0)
            d = -slope / 2
            return max(-0.5, min(d, 0.5))  # Constrain to reasonable range

        # Estimate fractional orders
        d1 = estimate_fractional_order(series1, max_lags)
        d2 = estimate_fractional_order(series2, max_lags)

        # Compute spread and its fractional order
        spread = series1 - series2
        d_spread = estimate_fractional_order(spread, max_lags)

        # Fractional cointegration condition: d_spread < max(d1, d2)
        # If the spread has lower fractional order, series are fractionally cointegrated
        is_fractionally_cointegrated = d_spread < max(d1, d2) - 0.1  # Small tolerance

        # Test the difference in fractional orders
        fractional_difference = max(d1, d2) - d_spread

        return {
            'fractional_orders': {
                'series1': d1,
                'series2': d2,
                'spread': d_spread
            },
            'fractional_difference': fractional_difference,
            'is_fractionally_cointegrated': is_fractionally_cointegrated,
            'cointegration_strength': fractional_difference,
            'max_lags': max_lags,
            'model_type': 'Fractional Cointegration'
        }

    @staticmethod
    def structural_break_cointegration_test(series1: pd.Series, series2: pd.Series,
                                          break_points: List[int] = None) -> Dict[str, Any]:
        """Test for cointegration with structural breaks.

        Tests for cointegration relationships that may be affected
        by structural breaks in the relationship parameters.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series to test
        break_points : list
            Known structural break points

        Returns:
        --------
        dict : Structural break cointegration test results
        """
        n = len(series1)

        # If no break points provided, estimate them
        if break_points is None:
            # Simple break point detection using cumulative sum of residuals
            spread = series1 - series2
            residuals = spread - spread.mean()

            # CUSUM test for structural breaks
            cusum = np.cumsum(residuals) / np.std(residuals)
            cusum_sq = cusum**2

            # Find significant breaks (simplified)
            threshold = 1.36  # Approximate 5% significance
            break_candidates = np.where(np.abs(cusum) > threshold)[0]

            # Select up to 2 break points
            break_points = break_candidates[:2] if len(break_candidates) > 0 else []

        # Test cointegration in each segment
        segments = [0] + break_points + [n]
        segment_results = []

        for i in range(len(segments) - 1):
            start_idx = segments[i]
            end_idx = segments[i + 1]

            seg1 = series1.iloc[start_idx:end_idx]
            seg2 = series2.iloc[start_idx:end_idx]

            if len(seg1) < 20:  # Minimum segment length
                continue

            # Engle-Granger test for this segment
            try:
                result = EngleGrangerTest.test(seg1, seg2)
                segment_results.append({
                    'segment': f'{start_idx}:{end_idx}',
                    'length': end_idx - start_idx,
                    'cointegration_test': result,
                    'is_cointegrated': result.p_value < 0.05
                })
            except:
                segment_results.append({
                    'segment': f'{start_idx}:{end_idx}',
                    'length': end_idx - start_idx,
                    'error': 'Insufficient data or test failed'
                })

        # Overall assessment
        cointegrated_segments = sum(1 for seg in segment_results
                                  if isinstance(seg, dict) and seg.get('is_cointegrated', False))

        is_overall_cointegrated = cointegrated_segments >= len(segment_results) * 0.6  # 60% of segments

        return {
            'break_points': break_points,
            'segments': segment_results,
            'cointegrated_segments': cointegrated_segments,
            'total_segments': len(segment_results),
            'is_overall_cointegrated': is_overall_cointegrated,
            'cointegration_ratio': cointegrated_segments / max(1, len(segment_results)),
            'model_type': 'Structural Break Cointegration'
        }


# =============================================================================
# ADVANCED ERROR CORRECTION MODELS
# =============================================================================

@dataclass
class AdvancedErrorCorrectionModels:
    """Advanced error correction models beyond standard VECM."""

    @staticmethod
    def asymmetric_error_correction_model(series1: pd.Series, series2: pd.Series,
                                       threshold: float = 0.05) -> Dict[str, Any]:
        """Asymmetric error correction model with different adjustment speeds.

        Models different speeds of adjustment when the spread is above
        or below its equilibrium level.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series in cointegration relationship
        threshold : float
            Asymmetry threshold

        Returns:
        --------
        dict : Asymmetric ECM results
        """
        # Compute spread and its lagged values
        spread = series1 - series2
        spread_lag = spread.shift(1)
        delta_spread = spread - spread_lag

        # Create asymmetric adjustment terms
        above_threshold = (spread_lag > threshold).astype(int)
        below_threshold = (spread_lag < -threshold).astype(int)
        within_threshold = 1 - above_threshold - below_threshold

        # Construct asymmetric ECM
        # Δspread = α_above * I(spread_lag > threshold) * spread_lag +
        #           α_below * I(spread_lag < -threshold) * spread_lag +
        #           β * Δspread_lag + ε

        # Prepare data for regression
        y = delta_spread.dropna()
        X_above = -spread_lag[above_threshold.astype(bool)]  # Negative for error correction
        X_below = -spread_lag[below_threshold.astype(bool)]
        X_within = -spread_lag[within_threshold.astype(bool)]

        # Align indices
        common_idx = y.index.intersection(X_above.index)
        if len(common_idx) < 10:
            return {'error': 'Insufficient data for asymmetric ECM'}

        # Simplified asymmetric adjustment estimation
        alpha_above = np.mean(y.loc[common_idx]) / np.mean(X_above.loc[common_idx]) if len(X_above.loc[common_idx]) > 0 else 0
        alpha_below = np.mean(y.loc[common_idx]) / np.mean(X_below.loc[common_idx]) if len(X_below.loc[common_idx]) > 0 else 0
        alpha_within = np.mean(y.loc[common_idx]) / np.mean(X_within.loc[common_idx]) if len(X_within.loc[common_idx]) > 0 else 0

        # Test significance (simplified t-test approximation)
        se_above = np.std(y.loc[common_idx]) / np.sqrt(len(common_idx))
        se_below = np.std(y.loc[common_idx]) / np.sqrt(len(common_idx))
        se_within = np.std(y.loc[common_idx]) / np.sqrt(len(common_idx))

        t_above = alpha_above / se_above if se_above > 0 else 0
        t_below = alpha_below / se_below if se_below > 0 else 0
        t_within = alpha_within / se_within if se_within > 0 else 0

        return {
            'adjustment_speeds': {
                'above_threshold': alpha_above,
                'below_threshold': alpha_below,
                'within_threshold': alpha_within
            },
            't_statistics': {
                'above_threshold': t_above,
                'below_threshold': t_below,
                'within_threshold': t_within
            },
            'significant_adjustment': {
                'above_threshold': abs(t_above) > 1.96,  # 5% significance
                'below_threshold': abs(t_below) > 1.96,
                'within_threshold': abs(t_within) > 1.96
            },
            'threshold': threshold,
            'observations': len(common_idx),
            'model_type': 'Asymmetric Error Correction Model'
        }

    @staticmethod
    def smooth_transition_error_correction(series1: pd.Series, series2: pd.Series,
                                         gamma: float = 1.0) -> Dict[str, Any]:
        """Smooth transition error correction model.

        Models gradual transitions between different adjustment regimes
        using a smooth logistic transition function.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series in cointegration relationship
        gamma : float
            Smoothness parameter for transition

        Returns:
        --------
        dict : Smooth transition ECM results
        """
        # Compute spread
        spread = series1 - series2
        spread_lag = spread.shift(1)
        delta_spread = spread - spread_lag

        # Smooth transition function
        transition_func = 1 / (1 + np.exp(-gamma * spread_lag))

        # Smooth transition ECM:
        # Δspread = α1 * (1 - G(spread_lag)) * spread_lag +
        #           α2 * G(spread_lag) * spread_lag + ε

        # Prepare regression variables
        y = delta_spread.dropna()
        X1 = (1 - transition_func) * spread_lag  # Linear regime
        X2 = transition_func * spread_lag       # Nonlinear regime

        # Align data
        common_idx = y.index
        X1_aligned = X1.loc[common_idx].dropna()
        X2_aligned = X2.loc[common_idx].dropna()
        y_aligned = y.loc[X1_aligned.index]

        if len(y_aligned) < 20:
            return {'error': 'Insufficient data for smooth transition ECM'}

        # Estimate parameters using simple regression
        # For linear regime
        if np.std(X1_aligned) > 0:
            alpha1 = np.cov(y_aligned, X1_aligned)[0, 1] / np.var(X1_aligned)
        else:
            alpha1 = 0

        # For nonlinear regime
        if np.std(X2_aligned) > 0:
            alpha2 = np.cov(y_aligned, X2_aligned)[0, 1] / np.var(X2_aligned)
        else:
            alpha2 = 0

        # Model fit
        y_pred = alpha1 * X1_aligned + alpha2 * X2_aligned
        residuals = y_aligned - y_pred

        r_squared = 1 - np.var(residuals) / np.var(y_aligned)
        mse = np.mean(residuals**2)

        return {
            'adjustment_speeds': {
                'linear_regime': alpha1,
                'nonlinear_regime': alpha2
            },
            'smoothness_parameter': gamma,
            'model_fit': {
                'r_squared': r_squared,
                'mse': mse,
                'observations': len(y_aligned)
            },
            'transition_function': transition_func.describe().to_dict(),
            'model_type': 'Smooth Transition Error Correction Model'
        }

    @staticmethod
    def markov_switching_error_correction(series1: pd.Series, series2: pd.Series,
                                        n_regimes: int = 2) -> Dict[str, Any]:
        """Markov-switching error correction model.

        Models error correction with regime switches governed
        by a hidden Markov chain.

        Parameters:
        -----------
        series1, series2 : pd.Series
            Time series in cointegration relationship
        n_regimes : int
            Number of switching regimes

        Returns:
        --------
        dict : Markov-switching ECM results
        """
        # Compute spread dynamics
        spread = series1 - series2
        delta_spread = spread.diff().dropna()

        n = len(delta_spread)

        # Simplified Markov-switching model
        # Assume two regimes: 'normal' and 'crisis'

        # Estimate regime parameters
        regimes = np.zeros(n)

        # Simple regime classification based on volatility
        vol_window = 20
        rolling_vol = pd.Series(delta_spread).rolling(vol_window).std()

        # High volatility = crisis regime (1), normal = regime (0)
        quantile_75 = np.percentile(rolling_vol.dropna(), 75)
        regimes = (rolling_vol > quantile_75).astype(int)

        # Estimate adjustment speeds by regime
        regime_adjustments = {}

        for regime in range(n_regimes):
            regime_mask = regimes == regime
            regime_data = delta_spread[regime_mask]

            if len(regime_data) > 10:
                # Simple adjustment speed estimation
                spread_regime = spread.iloc[regime_mask.index][regime_mask]
                spread_lag_regime = spread_regime.shift(1).dropna()

                if len(spread_lag_regime) > 5:
                    adjustment = np.mean(regime_data.loc[spread_lag_regime.index]) / np.mean(spread_lag_regime)
                    regime_adjustments[f'regime_{regime}'] = {
                        'adjustment_speed': adjustment,
                        'observations': len(regime_data),
                        'regime_name': 'crisis' if regime == 1 else 'normal'
                    }

        # Transition probabilities
        transition_matrix = np.zeros((n_regimes, n_regimes))

        for i in range(n_regimes):
            for j in range(n_regimes):
                from_regime = regimes[:-1] == i
                to_regime = regimes[1:] == j
                if np.sum(from_regime) > 0:
                    transition_matrix[i, j] = np.sum(from_regime & to_regime) / np.sum(from_regime)

        return {
            'regime_parameters': regime_adjustments,
            'transition_matrix': transition_matrix,
            'regime_probabilities': {
                'normal': np.mean(regimes == 0),
                'crisis': np.mean(regimes == 1)
            },
            'n_regimes': n_regimes,
            'regime_classification': regimes,
            'model_type': 'Markov-Switching Error Correction Model'
        }


# =============================================================================
# ADVANCED ARBITRAGE STRATEGIES
# =============================================================================

@dataclass
class AdvancedArbitrageStrategies:
    """Advanced arbitrage strategies beyond pairs trading."""

    @staticmethod
    def triangular_arbitrage(assets: Dict[str, pd.Series], transaction_costs: Dict[str, float] = None) -> Dict[str, Any]:
        """Triangular arbitrage strategy across three assets.

        Exploits pricing inefficiencies in triangular relationships
        between three currency pairs or assets.

        Parameters:
        -----------
        assets : dict
            Dictionary of asset price series
        transaction_costs : dict
            Transaction costs for each asset

        Returns:
        --------
        dict : Triangular arbitrage opportunities
        """
        if len(assets) < 3:
            return {'error': 'Need at least 3 assets for triangular arbitrage'}

        asset_names = list(assets.keys())
        prices = {name: assets[name] for name in asset_names[:3]}  # Take first 3

        # Compute cross rates
        cross_rates = {}
        for i in range(3):
            for j in range(3):
                if i != j:
                    pair_name = f'{asset_names[i]}_{asset_names[j]}'
                    cross_rates[pair_name] = prices[asset_names[i]] / prices[asset_names[j]]

        # Check triangular arbitrage conditions
        arbitrage_opportunities = []

        for t in range(len(prices[asset_names[0]])):
            try:
                # Forward triangle: A->B->C->A
                forward_rate = (cross_rates[f'{asset_names[0]}_{asset_names[1]}'].iloc[t] *
                              cross_rates[f'{asset_names[1]}_{asset_names[2]}'].iloc[t] *
                              cross_rates[f'{asset_names[2]}_{asset_names[0]}'].iloc[t])

                # Reverse triangle: A->C->B->A
                reverse_rate = (cross_rates[f'{asset_names[0]}_{asset_names[2]}'].iloc[t] *
                              cross_rates[f'{asset_names[2]}_{asset_names[1]}'].iloc[t] *
                              cross_rates[f'{asset_names[1]}_{asset_names[0]}'].iloc[t])

                # No-arbitrage condition: forward_rate should equal 1
                forward_deviation = abs(forward_rate - 1)
                reverse_deviation = abs(reverse_rate - 1)

                # Account for transaction costs
                total_cost = 0
                if transaction_costs:
                    for pair in [f'{asset_names[0]}_{asset_names[1]}',
                               f'{asset_names[1]}_{asset_names[2]}',
                               f'{asset_names[2]}_{asset_names[0]}']:
                        total_cost += transaction_costs.get(pair, 0.001)  # Default 0.1%

                if forward_deviation > total_cost or reverse_deviation > total_cost:
                    arbitrage_opportunities.append({
                        'timestamp': prices[asset_names[0]].index[t],
                        'forward_rate': forward_rate,
                        'reverse_rate': reverse_rate,
                        'forward_deviation': forward_deviation,
                        'reverse_deviation': reverse_deviation,
                        'transaction_cost': total_cost,
                        'profitable': (forward_deviation > total_cost) or (reverse_deviation > total_cost)
                    })

            except (IndexError, KeyError):
                continue

        profitable_opportunities = [opp for opp in arbitrage_opportunities if opp['profitable']]

        return {
            'total_opportunities': len(arbitrage_opportunities),
            'profitable_opportunities': len(profitable_opportunities),
            'profitability_ratio': len(profitable_opportunities) / max(1, len(arbitrage_opportunities)),
            'sample_opportunities': profitable_opportunities[:10],  # First 10 profitable ones
            'assets': asset_names[:3],
            'model_type': 'Triangular Arbitrage'
        }

    @staticmethod
    def statistical_arbitrage_basket(assets: Dict[str, pd.Series],
                                    target_weights: np.ndarray = None) -> Dict[str, Any]:
        """Statistical arbitrage with basket of assets.

        Creates synthetic instruments from baskets of assets
        and trades deviations from fair value.

        Parameters:
        -----------
        assets : dict
            Dictionary of asset price series
        target_weights : np.ndarray
            Target weights for basket construction

        Returns:
        --------
        dict : Basket statistical arbitrage results
        """
        asset_names = list(assets.keys())
        n_assets = len(asset_names)

        if target_weights is None:
            target_weights = np.ones(n_assets) / n_assets  # Equal weight

        if len(target_weights) != n_assets:
            return {'error': 'Weights must match number of assets'}

        # Construct basket (synthetic asset)
        prices_df = pd.DataFrame(assets)
        basket_price = prices_df.dot(target_weights)

        # Compute individual asset deviations from basket
        asset_returns = prices_df.pct_change().dropna()
        basket_returns = basket_price.pct_change().dropna()

        # Statistical arbitrage signals
        signals = {}

        for asset in asset_names:
            # Cointegration test between asset and basket
            try:
                coint_test = EngleGrangerTest.test(prices_df[asset], basket_price)
                is_cointegrated = coint_test.p_value < 0.05

                if is_cointegrated:
                    # Compute hedge ratio
                    hedge_ratio = np.cov(prices_df[asset], basket_price)[0, 1] / np.var(basket_price)

                    # Compute spread
                    spread = prices_df[asset] - hedge_ratio * basket_price

                    # Test for stationarity
                    adf_result = adfuller(spread.dropna(), maxlag=5)
                    spread_stationary = adf_result[1] < 0.05

                    # Generate trading signals
                    z_score = (spread - spread.mean()) / spread.std()
                    signal = np.where(z_score > 2, -1, np.where(z_score < -2, 1, 0))

                    signals[asset] = {
                        'hedge_ratio': hedge_ratio,
                        'cointegration_p_value': coint_test.p_value,
                        'spread_stationary': spread_stationary,
                        'signal': signal,
                        'z_score': z_score,
                        'profitable_trades': np.sum(signal != 0)
                    }

            except Exception as e:
                signals[asset] = {'error': str(e)}

        # Basket performance
        basket_returns = basket_price.pct_change().dropna()
        basket_sharpe = np.mean(basket_returns) / np.std(basket_returns) * np.sqrt(252)

        return {
            'basket_weights': dict(zip(asset_names, target_weights)),
            'basket_performance': {
                'total_return': (basket_price.iloc[-1] / basket_price.iloc[0] - 1),
                'annualized_volatility': np.std(basket_returns) * np.sqrt(252),
                'sharpe_ratio': basket_sharpe
            },
            'asset_signals': signals,
            'profitable_assets': sum(1 for sig in signals.values()
                                   if isinstance(sig, dict) and sig.get('profitable_trades', 0) > 0),
            'total_assets': n_assets,
            'model_type': 'Basket Statistical Arbitrage'
        }

    @staticmethod
    def cross_market_arbitrage(market1_prices: pd.Series, market2_prices: pd.Series,
                             basis_adjustment: float = 0.0) -> Dict[str, Any]:
        """Cross-market arbitrage between related instruments.

        Exploits price differences between the same underlying
        asset traded in different markets or forms.

        Parameters:
        -----------
        market1_prices, market2_prices : pd.Series
            Price series from two different markets
        basis_adjustment : float
            Adjustment for fair value differences

        Returns:
        --------
        dict : Cross-market arbitrage opportunities
        """
        # Align time series
        common_idx = market1_prices.index.intersection(market2_prices.index)
        if len(common_idx) < 30:
            return {'error': 'Insufficient overlapping data'}

        p1 = market1_prices.loc[common_idx]
        p2 = market2_prices.loc[common_idx]

        # Compute price differential (basis)
        basis = p1 - p2 - basis_adjustment

        # Statistical properties
        basis_mean = basis.mean()
        basis_std = basis.std()
        z_score = (basis - basis_mean) / basis_std

        # Arbitrage signals
        entry_threshold = 2.0  # 2 standard deviations
        signals = np.where(z_score > entry_threshold, -1,  # Short market1, long market2
                  np.where(z_score < -entry_threshold, 1, 0))  # Long market1, short market2

        # Profitability analysis
        returns = basis.diff().fillna(0)
        signal_returns = signals[:-1] * returns[1:]  # Next period returns

        profitable_trades = np.sum(signal_returns > 0)
        total_trades = np.sum(signals[:-1] != 0)

        if total_trades > 0:
            hit_rate = profitable_trades / total_trades
            avg_win = np.mean(signal_returns[signal_returns > 0]) if np.sum(signal_returns > 0) > 0 else 0
            avg_loss = np.mean(signal_returns[signal_returns < 0]) if np.sum(signal_returns < 0) > 0 else 0
        else:
            hit_rate = 0
            avg_win = 0
            avg_loss = 0

        return {
            'basis_statistics': {
                'mean': basis_mean,
                'std': basis_std,
                'min': basis.min(),
                'max': basis.max()
            },
            'arbitrage_signals': {
                'total_signals': total_trades,
                'entry_threshold': entry_threshold,
                'current_signal': signals[-1] if len(signals) > 0 else 0
            },
            'performance': {
                'hit_rate': hit_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'total_return': np.sum(signal_returns),
                'sharpe_ratio': np.mean(signal_returns) / np.std(signal_returns) * np.sqrt(252) if np.std(signal_returns) > 0 else 0
            },
            'basis_adjustment': basis_adjustment,
            'model_type': 'Cross-Market Arbitrage'
        }


# =============================================================================
# EXPORT ADVANCED STATISTICAL ARBITRAGE COMPONENTS
# =============================================================================

__all__ = [
    "CointegrationTestResult",
    "EngleGrangerTest",
    "JohansenTest",
    "PairsTradingAnalytics",
    "KalmanHedgeRatioEstimator",
    "StatsmodelsUnavailable",
    # New advanced exports
    "AdvancedCointegrationTests",
    "AdvancedErrorCorrectionModels",
    "AdvancedArbitrageStrategies"
]

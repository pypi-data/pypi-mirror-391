"""Walk-forward analysis and time-series cross-validation system."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Protocol
from datetime import datetime, timedelta
from enum import Enum
import itertools

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from scipy.optimize import minimize, differential_evolution
from scipy import stats

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.types import OrderSide
from qantify.strategy import Strategy

logger = logging.getLogger(__name__)


class WalkForwardMethod(Enum):
    """Methods for walk-forward analysis."""

    ROLLING = "rolling"  # Rolling window
    ANCHORED = "anchored"  # Anchored window
    EXPANDING = "expanding"  # Expanding window
    SLIDING = "sliding"  # Sliding window with gaps


class ValidationMethod(Enum):
    """Methods for validation in walk-forward analysis."""

    SIMPLE = "simple"  # Single train/test split
    MULTI_SPLIT = "multi_split"  # Multiple train/test splits
    ROLLING_ORIGIN = "rolling_origin"  # Rolling origin cross-validation
    BLOCKED = "blocked"  # Blocked cross-validation


class OptimizationMethod(Enum):
    """Methods for parameter optimization."""

    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    DIFFERENTIAL_EVOLUTION = "differential_evolution"
    NELDER_MEAD = "nelder_mead"


@dataclass(slots=True)
class WalkForwardWindow:
    """Represents a single walk-forward window."""

    window_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_data: pd.DataFrame
    test_data: pd.DataFrame
    parameters: Dict[str, Any]
    train_result: Optional[EventBacktestResult] = None
    test_result: Optional[EventBacktestResult] = None
    optimization_score: float = 0.0


@dataclass(slots=True)
class ParameterSpace:
    """Parameter space definition for optimization."""

    name: str
    type: str  # 'int', 'float', 'categorical'
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    values: Optional[List[Any]] = None
    step: Optional[float] = None

    def generate_values(self, n_samples: int = 10) -> List[Any]:
        """Generate parameter values for optimization."""
        if self.type == 'categorical':
            return self.values or []
        elif self.type == 'int':
            if self.values:
                return self.values
            else:
                return list(range(int(self.min_value), int(self.max_value) + 1, int(self.step or 1)))
        elif self.type == 'float':
            if self.values:
                return self.values
            else:
                return np.linspace(self.min_value, self.max_value, n_samples).tolist()
        else:
            raise ValueError(f"Unknown parameter type: {self.type}")


@dataclass(slots=True)
class OptimizationResult:
    """Result of parameter optimization."""

    best_parameters: Dict[str, Any]
    best_score: float
    optimization_history: List[Dict[str, Any]]
    convergence_info: Dict[str, Any]
    computation_time: float


@dataclass(slots=True)
class WalkForwardResult:
    """Complete walk-forward analysis result."""

    method: WalkForwardMethod
    validation_method: ValidationMethod
    windows: List[WalkForwardWindow]
    overall_train_performance: Dict[str, float]
    overall_test_performance: Dict[str, float]
    overfitting_metrics: Dict[str, Any]
    stability_metrics: Dict[str, Any]
    performance_decay: Dict[str, Any]
    optimization_results: Optional[OptimizationResult] = None


@dataclass(slots=True)
class CrossValidationResult:
    """Time-series cross-validation results."""

    cv_method: ValidationMethod
    folds: List[Dict[str, Any]]
    mean_train_score: float
    mean_test_score: float
    std_train_score: float
    std_test_score: float
    overfitting_risk: float
    stability_score: float


class WalkForwardEngine:
    """Walk-forward analysis engine with time-series cross-validation."""

    def __init__(
        self,
        method: WalkForwardMethod = WalkForwardMethod.ROLLING,
        train_window: int = 252,  # Trading days
        test_window: int = 63,    # Trading days
        step_size: int = 21,      # Trading days
        min_train_size: int = 126
    ):
        self.method = method
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size
        self.min_train_size = min_train_size

    def create_windows(
        self,
        data: pd.DataFrame,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WalkForwardWindow]:
        """Create walk-forward windows from data."""

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have DatetimeIndex")

        # Filter date range
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]

        if len(data) < self.min_train_size + self.test_window:
            raise ValueError("Insufficient data for walk-forward analysis")

        windows = []
        current_end = self.min_train_size

        window_id = 0

        while current_end + self.test_window <= len(data):

            if self.method == WalkForwardMethod.ROLLING:
                train_start_idx = current_end - self.train_window
                train_end_idx = current_end
            elif self.method == WalkForwardMethod.ANCHORED:
                train_start_idx = 0
                train_end_idx = current_end
            elif self.method == WalkForwardMethod.EXPANDING:
                train_start_idx = 0
                train_end_idx = current_end
            elif self.method == WalkForwardMethod.SLIDING:
                train_start_idx = current_end - self.train_window
                train_end_idx = current_end

            test_start_idx = current_end
            test_end_idx = current_end + self.test_window

            # Ensure we don't go beyond data bounds
            train_start_idx = max(0, train_start_idx)
            test_end_idx = min(len(data), test_end_idx)

            if test_end_idx - test_start_idx < self.test_window // 2:
                break  # Insufficient test data

            train_data = data.iloc[train_start_idx:train_end_idx]
            test_data = data.iloc[test_start_idx:test_end_idx]

            window = WalkForwardWindow(
                window_id=window_id,
                train_start=train_data.index[0].to_pydatetime(),
                train_end=train_data.index[-1].to_pydatetime(),
                test_start=test_data.index[0].to_pydatetime(),
                test_end=test_data.index[-1].to_pydatetime(),
                train_data=train_data,
                test_data=test_data,
                parameters={}
            )

            windows.append(window)
            window_id += 1

            if self.method == WalkForwardMethod.ROLLING:
                current_end += self.step_size
            else:
                current_end += self.test_window

        logger.info(f"Created {len(windows)} walk-forward windows")
        return windows

    def run_walk_forward_analysis(
        self,
        strategy_cls: type,
        data: pd.DataFrame,
        parameter_spaces: Optional[List[ParameterSpace]] = None,
        optimization_method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
        metric_function: Optional[Callable[[EventBacktestResult], float]] = None,
        **backtest_kwargs
    ) -> WalkForwardResult:
        """Run complete walk-forward analysis."""

        if metric_function is None:
            metric_function = lambda result: result.sharpe_ratio

        # Create windows
        windows = self.create_windows(data)

        if not windows:
            raise ValueError("No valid walk-forward windows could be created")

        # Run analysis for each window
        for window in windows:
            if parameter_spaces:
                # Optimize parameters on training data
                best_params = self.optimize_parameters(
                    strategy_cls,
                    window.train_data,
                    parameter_spaces,
                    optimization_method,
                    metric_function,
                    **backtest_kwargs
                )
                window.parameters = best_params

                # Run optimized strategy on training data
                window.train_result = self._run_strategy(
                    strategy_cls, window.train_data, best_params, **backtest_kwargs
                )

                # Run optimized strategy on test data
                window.test_result = self._run_strategy(
                    strategy_cls, window.test_data, best_params, **backtest_kwargs
                )
            else:
                # No optimization, use default parameters
                default_params = {}
                window.parameters = default_params

                window.train_result = self._run_strategy(
                    strategy_cls, window.train_data, default_params, **backtest_kwargs
                )
                window.test_result = self._run_strategy(
                    strategy_cls, window.test_data, default_params, **backtest_kwargs
                )

        # Calculate overall metrics
        overall_train_performance = self._calculate_overall_performance(
            [w.train_result for w in windows if w.train_result is not None]
        )

        overall_test_performance = self._calculate_overall_performance(
            [w.test_result for w in windows if w.test_result is not None]
        )

        # Calculate overfitting and stability metrics
        overfitting_metrics = self._calculate_overfitting_metrics(windows)
        stability_metrics = self._calculate_stability_metrics(windows)
        performance_decay = self._calculate_performance_decay(windows)

        result = WalkForwardResult(
            method=self.method,
            validation_method=ValidationMethod.SIMPLE,
            windows=windows,
            overall_train_performance=overall_train_performance,
            overall_test_performance=overall_test_performance,
            overfitting_metrics=overfitting_metrics,
            stability_metrics=stability_metrics,
            performance_decay=performance_decay
        )

        logger.info(f"Walk-forward analysis completed with {len(windows)} windows")
        return result

    def optimize_parameters(
        self,
        strategy_cls: type,
        data: pd.DataFrame,
        parameter_spaces: List[ParameterSpace],
        method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
        metric_function: Optional[Callable[[EventBacktestResult], float]] = None,
        **backtest_kwargs
    ) -> Dict[str, Any]:
        """Optimize strategy parameters using specified method."""

        if metric_function is None:
            metric_function = lambda result: result.sharpe_ratio

        def objective_function(params_dict: Dict[str, Any]) -> float:
            """Objective function to minimize (negative of metric)."""
            try:
                result = self._run_strategy(strategy_cls, data, params_dict, **backtest_kwargs)
                return -metric_function(result)  # Minimize negative metric = maximize metric
            except Exception as e:
                logger.warning(f"Parameter evaluation failed: {e}")
                return float('inf')

        if method == OptimizationMethod.GRID_SEARCH:
            return self._grid_search(parameter_spaces, objective_function)
        elif method == OptimizationMethod.RANDOM_SEARCH:
            return self._random_search(parameter_spaces, objective_function, n_samples=50)
        elif method == OptimizationMethod.DIFFERENTIAL_EVOLUTION:
            return self._differential_evolution(parameter_spaces, objective_function)
        elif method == OptimizationMethod.NELDER_MEAD:
            return self._nelder_mead(parameter_spaces, objective_function)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")

    def _grid_search(
        self,
        parameter_spaces: List[ParameterSpace],
        objective_function: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        """Perform grid search optimization."""

        # Generate all parameter combinations
        param_values = [space.generate_values() for space in parameter_spaces]
        param_names = [space.name for space in parameter_spaces]

        best_params = {}
        best_score = float('inf')

        for param_combo in itertools.product(*param_values):
            params_dict = dict(zip(param_names, param_combo))
            score = objective_function(params_dict)

            if score < best_score:
                best_score = score
                best_params = params_dict

        return best_params

    def _random_search(
        self,
        parameter_spaces: List[ParameterSpace],
        objective_function: Callable[[Dict[str, Any]], float],
        n_samples: int = 50
    ) -> Dict[str, Any]:
        """Perform random search optimization."""

        param_names = [space.name for space in parameter_spaces]

        best_params = {}
        best_score = float('inf')

        for _ in range(n_samples):
            params_dict = {}
            for space in parameter_spaces:
                values = space.generate_values(n_samples=100)
                params_dict[space.name] = np.random.choice(values)

            score = objective_function(params_dict)

            if score < best_score:
                best_score = score
                best_params = params_dict

        return best_params

    def _differential_evolution(
        self,
        parameter_spaces: List[ParameterSpace],
        objective_function: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        """Perform differential evolution optimization."""

        # Create bounds for continuous parameters
        bounds = []
        param_names = []

        for space in parameter_spaces:
            if space.type in ['int', 'float']:
                bounds.append((space.min_value, space.max_value))
                param_names.append(space.name)
            elif space.type == 'categorical':
                # For categorical, we'll use indices
                bounds.append((0, len(space.values) - 1))
                param_names.append(space.name)

        def de_objective(x):
            params_dict = {}
            for i, name in enumerate(param_names):
                space = next(s for s in parameter_spaces if s.name == name)
                if space.type == 'categorical':
                    params_dict[name] = space.values[int(x[i])]
                elif space.type == 'int':
                    params_dict[name] = int(x[i])
                else:
                    params_dict[name] = x[i]

            return objective_function(params_dict)

        result = differential_evolution(de_objective, bounds, maxiter=50, popsize=15)

        # Convert back to parameter dictionary
        best_params = {}
        for i, name in enumerate(param_names):
            space = next(s for s in parameter_spaces if s.name == name)
            if space.type == 'categorical':
                best_params[name] = space.values[int(result.x[i])]
            elif space.type == 'int':
                best_params[name] = int(result.x[i])
            else:
                best_params[name] = result.x[i]

        return best_params

    def _nelder_mead(
        self,
        parameter_spaces: List[ParameterSpace],
        objective_function: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        """Perform Nelder-Mead optimization."""

        # Use first set of values as starting point
        x0 = []
        param_names = []

        for space in parameter_spaces:
            if space.type in ['int', 'float']:
                x0.append((space.min_value + space.max_value) / 2)
                param_names.append(space.name)
            elif space.type == 'categorical':
                x0.append(0)  # Start with first category
                param_names.append(space.name)

        def nm_objective(x):
            params_dict = {}
            for i, name in enumerate(param_names):
                space = next(s for s in parameter_spaces if s.name == name)
                if space.type == 'categorical':
                    params_dict[name] = space.values[int(x[i])]
                elif space.type == 'int':
                    params_dict[name] = int(x[i])
                else:
                    params_dict[name] = x[i]

            return objective_function(params_dict)

        bounds = [(space.min_value, space.max_value) if space.type in ['int', 'float']
                 else (0, len(space.values) - 1) if space.type == 'categorical'
                 else (0, 1) for space in parameter_spaces]

        result = minimize(nm_objective, x0, method='Nelder-Mead', bounds=bounds)

        # Convert back to parameter dictionary
        best_params = {}
        for i, name in enumerate(param_names):
            space = next(s for s in parameter_spaces if s.name == name)
            if space.type == 'categorical':
                best_params[name] = space.values[int(result.x[i])]
            elif space.type == 'int':
                best_params[name] = int(result.x[i])
            else:
                best_params[name] = result.x[i]

        return best_params

    def _run_strategy(
        self,
        strategy_cls: type,
        data: pd.DataFrame,
        params: Dict[str, Any],
        **backtest_kwargs
    ) -> EventBacktestResult:
        """Run a strategy with given parameters."""

        strategy = strategy_cls(**params)
        engine = EventBacktester(data, symbol="WALK_FORWARD", strategy=strategy, **backtest_kwargs)
        return engine.run()

    def _calculate_overall_performance(self, results: List[EventBacktestResult]) -> Dict[str, float]:
        """Calculate overall performance metrics across all results."""

        if not results:
            return {}

        total_return = np.mean([(result.equity_curve.iloc[-1] / result.equity_curve.iloc[0] - 1)
                               for result in results])
        annualized_return = np.mean([((result.equity_curve.iloc[-1] / result.equity_curve.iloc[0]) **
                                     (252 / len(result.equity_curve)) - 1) for result in results])
        volatility = np.mean([result.equity_curve.pct_change().std() * np.sqrt(252) for result in results])
        sharpe_ratio = np.mean([result.sharpe_ratio for result in results])
        max_drawdown = np.mean([result.max_drawdown for result in results])
        win_rate = np.mean([result.win_rate for result in results])

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }

    def _calculate_overfitting_metrics(self, windows: List[WalkForwardWindow]) -> Dict[str, Any]:
        """Calculate overfitting metrics."""

        train_scores = [w.optimization_score for w in windows if w.train_result is not None]
        test_scores = [-w.test_result.sharpe_ratio if w.test_result else 0 for w in windows]

        if not train_scores or not test_scores:
            return {'insufficient_data': True}

        overfitting_ratio = np.mean(train_scores) / np.mean(test_scores) if np.mean(test_scores) != 0 else float('inf')

        # Performance decay
        score_decay = np.corrcoef(range(len(test_scores)), test_scores)[0, 1] if len(test_scores) > 1 else 0

        # Stability of performance
        test_std = np.std(test_scores)
        test_mean = np.mean(test_scores)
        stability_ratio = test_std / abs(test_mean) if test_mean != 0 else float('inf')

        return {
            'overfitting_ratio': overfitting_ratio,
            'score_decay': score_decay,
            'stability_ratio': stability_ratio,
            'train_test_correlation': np.corrcoef(train_scores, test_scores)[0, 1] if len(train_scores) == len(test_scores) else 0,
            'performance_consistency': 1 - stability_ratio if stability_ratio < 1 else 0
        }

    def _calculate_stability_metrics(self, windows: List[WalkForwardWindow]) -> Dict[str, Any]:
        """Calculate stability metrics across windows."""

        test_returns = [w.test_result.sharpe_ratio if w.test_result else 0 for w in windows]

        if len(test_returns) < 2:
            return {'insufficient_data': True}

        # Trend stability
        trend_stability = abs(np.corrcoef(range(len(test_returns)), test_returns)[0, 1])

        # Variance stability
        rolling_var = pd.Series(test_returns).rolling(3).var().mean()
        variance_stability = 1 / (1 + rolling_var) if rolling_var > 0 else 1

        # Mean reversion
        mean_reversion = 1 - abs(pd.Series(test_returns).autocorr(1))

        return {
            'trend_stability': trend_stability,
            'variance_stability': variance_stability,
            'mean_reversion': mean_reversion,
            'overall_stability': (trend_stability + variance_stability + mean_reversion) / 3
        }

    def _calculate_performance_decay(self, windows: List[WalkForwardWindow]) -> Dict[str, Any]:
        """Calculate performance decay metrics."""

        test_scores = [w.test_result.sharpe_ratio if w.test_result else 0 for w in windows]

        if len(test_scores) < 3:
            return {'insufficient_data': True}

        # Linear trend
        x = np.arange(len(test_scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, test_scores)

        # Exponential decay
        try:
            from scipy.optimize import curve_fit

            def exp_decay(x, a, b, c):
                return a * np.exp(-b * x) + c

            params, covariance = curve_fit(exp_decay, x, test_scores, p0=[test_scores[0], 0.1, test_scores[-1]])
            decay_rate = params[1]
        except:
            decay_rate = 0

        return {
            'linear_trend_slope': slope,
            'linear_trend_r_squared': r_value ** 2,
            'exponential_decay_rate': decay_rate,
            'performance_decay_risk': 'High' if slope < -0.01 else 'Medium' if slope < 0 else 'Low',
            'half_life': np.log(2) / decay_rate if decay_rate > 0 else float('inf')
        }


class TimeSeriesCrossValidator:
    """Time-series cross-validation engine."""

    def __init__(self, cv_method: ValidationMethod = ValidationMethod.ROLLING_ORIGIN):
        self.cv_method = cv_method

    def cross_validate(
        self,
        strategy_cls: type,
        data: pd.DataFrame,
        n_splits: int = 5,
        metric_function: Optional[Callable[[EventBacktestResult], float]] = None,
        **backtest_kwargs
    ) -> CrossValidationResult:
        """Perform time-series cross-validation."""

        if metric_function is None:
            metric_function = lambda result: result.sharpe_ratio

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have DatetimeIndex")

        if self.cv_method == ValidationMethod.ROLLING_ORIGIN:
            cv = TimeSeriesSplit(n_splits=n_splits, test_size=len(data) // (n_splits + 1))
        else:
            # Simple split for other methods
            cv = TimeSeriesSplit(n_splits=n_splits)

        folds = []
        train_scores = []
        test_scores = []

        for fold_idx, (train_idx, test_idx) in enumerate(cv.split(data)):
            train_data = data.iloc[train_idx]
            test_data = data.iloc[test_idx]

            # Train on training data
            strategy = strategy_cls()  # Use default parameters
            train_engine = EventBacktester(train_data, symbol="CV_TRAIN", strategy=strategy, **backtest_kwargs)
            train_result = train_engine.run()
            train_score = metric_function(train_result)

            # Test on test data
            test_engine = EventBacktester(test_data, symbol="CV_TEST", strategy=strategy, **backtest_kwargs)
            test_result = test_engine.run()
            test_score = metric_function(test_result)

            fold_info = {
                'fold': fold_idx,
                'train_period': (train_data.index[0], train_data.index[-1]),
                'test_period': (test_data.index[0], test_data.index[-1]),
                'train_score': train_score,
                'test_score': test_score,
                'overfitting': train_score - test_score
            }

            folds.append(fold_info)
            train_scores.append(train_score)
            test_scores.append(test_score)

        # Calculate summary statistics
        mean_train_score = np.mean(train_scores)
        mean_test_score = np.mean(test_scores)
        std_train_score = np.std(train_scores)
        std_test_score = np.std(test_scores)

        # Overfitting risk
        overfitting_risk = mean_train_score / mean_test_score if mean_test_score != 0 else float('inf')

        # Stability score (inverse of coefficient of variation)
        stability_score = mean_test_score / std_test_score if std_test_score > 0 else float('inf')

        result = CrossValidationResult(
            cv_method=self.cv_method,
            folds=folds,
            mean_train_score=mean_train_score,
            mean_test_score=mean_test_score,
            std_train_score=std_train_score,
            std_test_score=std_test_score,
            overfitting_risk=overfitting_risk,
            stability_score=stability_score
        )

        logger.info(f"Cross-validation completed with {n_splits} folds")
        return result


# Convenience functions
def run_walk_forward_optimization(
    strategy_cls: type,
    data: pd.DataFrame,
    parameter_spaces: List[ParameterSpace],
    train_window: int = 252,
    test_window: int = 63,
    method: WalkForwardMethod = WalkForwardMethod.ROLLING,
    optimization_method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
    **backtest_kwargs
) -> WalkForwardResult:
    """Convenience function for walk-forward optimization."""

    engine = WalkForwardEngine(
        method=method,
        train_window=train_window,
        test_window=test_window
    )

    return engine.run_walk_forward_analysis(
        strategy_cls=strategy_cls,
        data=data,
        parameter_spaces=parameter_spaces,
        optimization_method=optimization_method,
        **backtest_kwargs
    )


def run_time_series_cv(
    strategy_cls: type,
    data: pd.DataFrame,
    n_splits: int = 5,
    cv_method: ValidationMethod = ValidationMethod.ROLLING_ORIGIN,
    **backtest_kwargs
) -> CrossValidationResult:
    """Convenience function for time-series cross-validation."""

    validator = TimeSeriesCrossValidator(cv_method)
    return validator.cross_validate(strategy_cls, data, n_splits, **backtest_kwargs)


__all__ = [
    "WalkForwardEngine",
    "TimeSeriesCrossValidator",
    "WalkForwardMethod",
    "ValidationMethod",
    "OptimizationMethod",
    "WalkForwardWindow",
    "ParameterSpace",
    "OptimizationResult",
    "WalkForwardResult",
    "CrossValidationResult",
    "run_walk_forward_optimization",
    "run_time_series_cv",
]

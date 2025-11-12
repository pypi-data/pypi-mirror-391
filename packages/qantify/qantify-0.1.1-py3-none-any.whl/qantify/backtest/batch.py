"""Advanced batch and parallel backtesting with distributed computing and hyperparameter optimization."""

from __future__ import annotations

import multiprocessing as mp
from functools import partial
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple, Type, Optional, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import itertools
import json
import os
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm
from sklearn.model_selection import ParameterGrid, cross_val_score
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.vectorized import VectorizedBacktestResult

if TYPE_CHECKING:
    from qantify.strategy import Strategy as StrategyType
else:  # pragma: no cover - runtime hint only
    StrategyType = Any


def _run_event_backtest(
    strategy_cls: Type[StrategyType],
    params: Dict[str, Any],
    data: pd.DataFrame,
    symbol: str,
    backtest_kwargs: Dict[str, Any],
) -> Tuple[Dict[str, Any], EventBacktestResult]:
    strategy = strategy_cls(**params)
    engine = EventBacktester(data, symbol=symbol, strategy=strategy, **backtest_kwargs)
    result = engine.run()
    return params, result


class OptimizationObjective(ABC):
    """Abstract base class for optimization objectives."""

    @abstractmethod
    def evaluate(self, result: Union[EventBacktestResult, VectorizedBacktestResult]) -> float:
        """Evaluate the objective function for a backtest result."""
        pass

    @abstractmethod
    def is_maximize(self) -> bool:
        """Return True if we should maximize this objective, False for minimize."""
        pass


class SharpeRatioObjective(OptimizationObjective):
    """Maximize Sharpe ratio."""

    def evaluate(self, result: Union[EventBacktestResult, VectorizedBacktestResult]) -> float:
        if hasattr(result, 'sharpe_ratio'):
            return result.sharpe_ratio
        # Fallback calculation
        returns = result.returns.dropna()
        if len(returns) == 0:
            return 0.0
        return (returns.mean() * 252) / (returns.std() * np.sqrt(252))

    def is_maximize(self) -> bool:
        return True


class MaxDrawdownObjective(OptimizationObjective):
    """Minimize maximum drawdown."""

    def evaluate(self, result: Union[EventBacktestResult, VectorizedBacktestResult]) -> float:
        if hasattr(result, 'max_drawdown'):
            return result.max_drawdown
        # Fallback calculation
        if hasattr(result, 'calculate_metrics'):
            result.calculate_metrics()
            return result.max_drawdown
        # Simple fallback
        equity = result.equity_curve
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        return abs(drawdown.min())

    def is_maximize(self) -> bool:
        return False


class CalmarRatioObjective(OptimizationObjective):
    """Maximize Calmar ratio."""

    def evaluate(self, result: Union[EventBacktestResult, VectorizedBacktestResult]) -> float:
        if hasattr(result, 'calmar_ratio'):
            return result.calmar_ratio
        # Calculate Calmar ratio
        returns = result.returns.dropna()
        max_dd = MaxDrawdownObjective().evaluate(result)

        if max_dd == 0:
            return 0.0

        ann_return = (1 + returns.mean()) ** 252 - 1
        return ann_return / max_dd

    def is_maximize(self) -> bool:
        return True


class ProfitFactorObjective(OptimizationObjective):
    """Maximize profit factor."""

    def evaluate(self, result: Union[EventBacktestResult, VectorizedBacktestResult]) -> float:
        if hasattr(result, 'profit_factor'):
            return result.profit_factor
        # Calculate profit factor
        if not result.trades:
            return 1.0

        gross_profit = sum(trade.pnl for trade in result.trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in result.trades if trade.pnl < 0))

        return gross_profit / gross_loss if gross_loss > 0 else float('inf')

    def is_maximize(self) -> bool:
        return True


@dataclass
class HyperparameterOptimizationResult:
    """Results from hyperparameter optimization."""

    best_params: Dict[str, Any]
    best_score: float
    all_results: List[Tuple[Dict[str, Any], float]]
    optimization_path: List[Dict[str, Any]] = field(default_factory=list)
    convergence_info: Dict[str, Any] = field(default_factory=dict)


class HyperparameterOptimizer(ABC):
    """Abstract base class for hyperparameter optimization algorithms."""

    def __init__(self, objective: OptimizationObjective):
        self.objective = objective

    @abstractmethod
    def optimize(self, param_space: Dict[str, List[Any]], max_evaluations: int = 50) -> HyperparameterOptimizationResult:
        """Run optimization and return results."""
        pass


class GridSearchOptimizer(HyperparameterOptimizer):
    """Traditional grid search optimization."""

    def optimize(self, param_space: Dict[str, List[Any]], max_evaluations: int = 50) -> HyperparameterOptimizationResult:
        grid = ParameterGrid(param_space)
        param_list = list(grid)[:max_evaluations]  # Limit evaluations

        # This would need to be implemented with actual backtesting
        # For now, return placeholder
        best_params = param_list[0] if param_list else {}
        best_score = 0.0

        return HyperparameterOptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=[(params, 0.0) for params in param_list]
        )


class BayesianOptimizer(HyperparameterOptimizer):
    """Bayesian optimization using Gaussian processes."""

    def __init__(self, objective: OptimizationObjective, acquisition_func: str = "ei"):
        super().__init__(objective)
        self.acquisition_func = acquisition_func
        self.gp = GaussianProcessRegressor(
            kernel=Matern(nu=2.5),
            alpha=1e-6,
            normalize_y=True,
            n_restarts_optimizer=5
        )
        self.X_observed = []
        self.y_observed = []

    def optimize(self, param_space: Dict[str, List[Any]], max_evaluations: int = 50) -> HyperparameterOptimizationResult:
        # Convert parameter space to bounds for continuous optimization
        param_names = list(param_space.keys())
        bounds = []

        for name, values in param_space.items():
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                # For categorical, we'll use integer encoding
                bounds.append((0, len(values) - 1))

        optimization_path = []

        for i in range(max_evaluations):
            if i < 5:  # Initial random samples
                x_next = np.array([np.random.uniform(low, high) for low, high in bounds])
            else:
                # Use GP to suggest next point
                x_next = self._suggest_next_point(bounds)

            # Evaluate objective (placeholder - would need actual backtesting)
            score = np.random.random()  # Placeholder

            self.X_observed.append(x_next)
            self.y_observed.append(score)

            # Update GP model
            if len(self.X_observed) >= 5:
                X = np.array(self.X_observed)
                y = np.array(self.y_observed)
                self.gp.fit(X, y)

            optimization_path.append({
                "iteration": i,
                "params": dict(zip(param_names, x_next)),
                "score": score
            })

        # Find best result
        best_idx = np.argmax(self.y_observed) if self.objective.is_maximize() else np.argmin(self.y_observed)
        best_params = dict(zip(param_names, self.X_observed[best_idx]))
        best_score = self.y_observed[best_idx]

        return HyperparameterOptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=list(zip([dict(zip(param_names, x)) for x in self.X_observed], self.y_observed)),
            optimization_path=optimization_path
        )

    def _suggest_next_point(self, bounds):
        """Suggest next point using expected improvement."""
        def ei(x):
            x = x.reshape(1, -1)
            mu, sigma = self.gp.predict(x, return_std=True)

            if sigma == 0:
                return 0

            if self.objective.is_maximize():
                best_y = max(self.y_observed)
                z = (mu - best_y) / sigma
            else:
                best_y = min(self.y_observed)
                z = (best_y - mu) / sigma

            ei_value = (best_y - mu) * norm.cdf(z) + sigma * norm.pdf(z)
            return -ei_value  # Minimize negative EI

        # Optimize acquisition function
        x0 = np.array([np.random.uniform(low, high) for low, high in bounds])

        try:
            result = minimize_scalar(lambda x: ei(np.array([x])), bounds=bounds[0], method='bounded')
            if result.success:
                return np.array([result.x])
        except:
            pass

        return x0


class BatchBacktestResult:
    """Aggregated results from batch backtesting."""

    def __init__(self, results: List[Tuple[Dict[str, Any], Union[EventBacktestResult, VectorizedBacktestResult]]]):
        self.results = results
        self._summary_df = None

    @property
    def summary(self) -> pd.DataFrame:
        """Get summary DataFrame of all results."""
        if self._summary_df is None:
            summary_data = []

            for params, result in self.results:
                row = dict(params)  # Copy parameters

                # Add key metrics
                if hasattr(result, 'sharpe_ratio'):
                    row['sharpe_ratio'] = result.sharpe_ratio
                if hasattr(result, 'max_drawdown'):
                    row['max_drawdown'] = result.max_drawdown
                if hasattr(result, 'win_rate'):
                    row['win_rate'] = result.win_rate
                if hasattr(result, 'profit_factor'):
                    row['profit_factor'] = result.profit_factor
                if hasattr(result, 'calmar_ratio'):
                    row['calmar_ratio'] = result.calmar_ratio

                # Basic metrics
                final_equity = result.equity_curve.iloc[-1]
                total_return = (final_equity - result.equity_curve.iloc[0]) / result.equity_curve.iloc[0]
                row['total_return'] = total_return
                row['final_equity'] = final_equity
                row['num_trades'] = len(result.trades)

                summary_data.append(row)

            self._summary_df = pd.DataFrame(summary_data)

        return self._summary_df

    def get_best_result(self, metric: str = 'sharpe_ratio', maximize: bool = True) -> Tuple[Dict[str, Any], Any]:
        """Get the best result by specified metric."""
        if self._summary_df is None:
            self.summary

        if maximize:
            best_idx = self._summary_df[metric].idxmax()
        else:
            best_idx = self._summary_df[metric].idxmin()

        best_params = self.results[best_idx][0]
        best_result = self.results[best_idx][1]

        return best_params, best_result

    def plot_parameter_heatmap(self, param1: str, param2: str, metric: str = 'sharpe_ratio'):
        """Create heatmap of parameter combinations vs metric."""
        pivot_table = self.summary.pivot_table(
            values=metric, index=param1, columns=param2, aggfunc='mean'
        )
        return pivot_table

    def get_parameter_importance(self) -> Dict[str, float]:
        """Calculate parameter importance using correlation."""
        numeric_cols = self.summary.select_dtypes(include=[np.number]).columns
        correlations = {}

        for col in numeric_cols:
            if col not in ['sharpe_ratio', 'max_drawdown', 'total_return', 'final_equity']:
                continue

            param_cols = [c for c in self.summary.columns if c not in numeric_cols]
            for param in param_cols:
                if self.summary[param].dtype in ['int64', 'float64']:
                    corr = abs(self.summary[param].corr(self.summary[col]))
                    if not np.isnan(corr):
                        key = f"{param}_vs_{col}"
                        correlations[key] = corr

        return dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))


def run_parallel_event_backtests(
    strategy_cls: Type[StrategyType],
    param_list: Sequence[Dict[str, Any]],
    data: pd.DataFrame,
    *,
    symbol: str,
    backtest_kwargs: Dict[str, Any] | None = None,
    processes: int | None = None,
) -> List[Tuple[Dict[str, Any], EventBacktestResult]]:
    worker = partial(
        _run_event_backtest,
        strategy_cls,
        data=data,
        symbol=symbol,
        backtest_kwargs=backtest_kwargs or {},
    )

    with mp.Pool(processes=processes) as pool:
        results = pool.map(worker, param_list)
    return results


def run_hyperparameter_optimization(
    strategy_cls: Type[StrategyType],
    param_space: Dict[str, List[Any]],
    data: pd.DataFrame,
    *,
    symbol: str,
    optimizer: HyperparameterOptimizer,
    max_evaluations: int = 50,
    backtest_kwargs: Dict[str, Any] | None = None,
    processes: int | None = None,
) -> HyperparameterOptimizationResult:
    """Run hyperparameter optimization for strategy parameters."""

    def evaluate_params(params: Dict[str, Any]) -> float:
        """Evaluate a single parameter set."""
        try:
            result = _run_event_backtest(
                strategy_cls, params, data, symbol, backtest_kwargs or {}
            )[1]
            return optimizer.objective.evaluate(result)
        except Exception as e:
            warnings.warn(f"Error evaluating parameters {params}: {e}")
            return 0.0 if optimizer.objective.is_maximize() else float('inf')

    # Generate parameter combinations
    if isinstance(optimizer, GridSearchOptimizer):
        param_grid = ParameterGrid(param_space)
        param_list = list(param_grid)[:max_evaluations]
    else:
        # For Bayesian optimization, start with random samples
        param_list = []
        for _ in range(max_evaluations):
            params = {}
            for param_name, values in param_space.items():
                params[param_name] = np.random.choice(values)
            param_list.append(params)

    # Evaluate parameters (could be parallelized)
    scores = []
    for params in param_list:
        score = evaluate_params(params)
        scores.append(score)

    # Find best result
    if optimizer.objective.is_maximize():
        best_idx = np.argmax(scores)
    else:
        best_idx = np.argmin(scores)

    best_params = param_list[best_idx]
    best_score = scores[best_idx]

    return HyperparameterOptimizationResult(
        best_params=best_params,
        best_score=best_score,
        all_results=list(zip(param_list, scores))
    )


def run_walk_forward_optimization(
    strategy_cls: Type[StrategyType],
    param_space: Dict[str, List[Any]],
    data: pd.DataFrame,
    *,
    symbol: str,
    train_window: int = 252,
    test_window: int = 63,
    step_size: int = 21,
    objective: OptimizationObjective,
    backtest_kwargs: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Run walk-forward optimization with rolling parameter selection."""

    results = []
    n_periods = len(data)

    for start_idx in range(0, n_periods - train_window - test_window, step_size):
        train_end = start_idx + train_window
        test_end = train_end + test_window

        if test_end > n_periods:
            break

        # Training data
        train_data = data.iloc[start_idx:train_end]

        # Optimize parameters on training data
        optimizer = GridSearchOptimizer(objective)
        opt_result = run_hyperparameter_optimization(
            strategy_cls, param_space, train_data, symbol=symbol,
            optimizer=optimizer, max_evaluations=20, backtest_kwargs=backtest_kwargs
        )

        # Test optimized parameters
        test_data = data.iloc[train_end:test_end]
        test_result = _run_event_backtest(
            strategy_cls, opt_result.best_params, test_data, symbol, backtest_kwargs or {}
        )[1]

        test_score = objective.evaluate(test_result)

        results.append({
            "train_start": data.index[start_idx],
            "train_end": data.index[train_end-1],
            "test_start": data.index[train_end],
            "test_end": data.index[test_end-1],
            "best_params": opt_result.best_params,
            "train_score": opt_result.best_score,
            "test_score": test_score,
            "out_of_sample_performance": test_score - opt_result.best_score
        })

    return results


class DistributedBacktestManager:
    """Manager for distributed backtesting across multiple machines/nodes."""

    def __init__(self, result_dir: str = "./backtest_results"):
        self.result_dir = Path(result_dir)
        self.result_dir.mkdir(exist_ok=True)

    def save_checkpoint(self, results: List[Tuple[Dict[str, Any], Any]], checkpoint_name: str):
        """Save intermediate results to disk."""
        checkpoint_path = self.result_dir / f"{checkpoint_name}.json"

        # Convert results to serializable format
        serializable_results = []
        for params, result in results:
            # Extract key metrics from result
            result_data = {
                "equity_curve": result.equity_curve.tolist() if hasattr(result.equity_curve, 'tolist') else [],
                "sharpe_ratio": getattr(result, 'sharpe_ratio', 0.0),
                "max_drawdown": getattr(result, 'max_drawdown', 0.0),
                "total_return": (result.equity_curve.iloc[-1] - result.equity_curve.iloc[0]) / result.equity_curve.iloc[0],
                "num_trades": len(result.trades)
            }
            serializable_results.append({"params": params, "result": result_data})

        with open(checkpoint_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)

    def load_checkpoint(self, checkpoint_name: str) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Load results from checkpoint."""
        checkpoint_path = self.result_dir / f"{checkpoint_name}.json"

        if not checkpoint_path.exists():
            return []

        with open(checkpoint_path, 'r') as f:
            data = json.load(f)

        return [(item["params"], item["result"]) for item in data]

    def merge_results(self, result_batches: List[List[Tuple[Dict[str, Any], Any]]]) -> BatchBacktestResult:
        """Merge results from multiple batches."""
        all_results = []
        for batch in result_batches:
            all_results.extend(batch)

        return BatchBacktestResult(all_results)


__all__ = [
    "run_parallel_event_backtests",
    "run_hyperparameter_optimization",
    "run_walk_forward_optimization",
    "BatchBacktestResult",
    "OptimizationObjective",
    "SharpeRatioObjective",
    "MaxDrawdownObjective",
    "CalmarRatioObjective",
    "ProfitFactorObjective",
    "HyperparameterOptimizer",
    "GridSearchOptimizer",
    "BayesianOptimizer",
    "HyperparameterOptimizationResult",
    "DistributedBacktestManager",
]

"""Portfolio optimization integration for backtesting."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

from qantify.math.optimization import (
    mean_variance_optimize,
    risk_parity_optimize,
    minimum_variance_optimize,
    maximum_sharpe_optimize,
    black_litterman_optimize
)

logger = logging.getLogger(__name__)


class OptimizationMethod(Enum):
    """Portfolio optimization methods."""

    MEAN_VARIANCE = "mean_variance"
    RISK_PARITY = "risk_parity"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_SHARPE = "maximum_sharpe"
    BLACK_LITTERMAN = "black_litterman"
    EQUAL_WEIGHT = "equal_weight"


@dataclass(slots=True)
class PortfolioConstraint:
    """Portfolio optimization constraint."""

    constraint_type: str  # 'weight', 'exposure', 'turnover', 'tracking_error'
    asset: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    target_value: Optional[float] = None


@dataclass(slots=True)
class OptimizationConfig:
    """Configuration for portfolio optimization."""

    method: OptimizationMethod
    rebalance_frequency: str = "monthly"  # 'daily', 'weekly', 'monthly', 'quarterly'
    risk_free_rate: float = 0.02
    constraints: List[PortfolioConstraint] = field(default_factory=list)
    lambda_risk: float = 2.0  # Risk aversion parameter
    max_weight: float = 0.2  # Maximum weight per asset
    min_weight: float = 0.0  # Minimum weight per asset


@dataclass(slots=True)
class OptimizedPortfolio:
    """Results from portfolio optimization."""

    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: OptimizationMethod
    constraints_satisfied: bool
    optimization_date: pd.Timestamp


class PortfolioOptimizer:
    """Portfolio optimization engine for backtesting."""

    def __init__(self, config: OptimizationConfig):
        self.config = config

    def optimize_portfolio(
        self,
        returns: pd.DataFrame,
        current_weights: Optional[Dict[str, float]] = None,
        market_caps: Optional[Dict[str, float]] = None,
        views: Optional[Dict[str, float]] = None
    ) -> OptimizedPortfolio:
        """Optimize portfolio weights."""

        assets = returns.columns.tolist()
        n_assets = len(assets)

        # Calculate expected returns and covariance
        expected_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252  # Annualized

        # Use shrinkage estimator for better covariance matrix
        try:
            lw = LedoitWolf().fit(returns.values)
            cov_matrix = pd.DataFrame(lw.covariance_, index=assets, columns=assets)
        except:
            pass  # Fall back to sample covariance

        # Apply optimization method
        if self.config.method == OptimizationMethod.MEAN_VARIANCE:
            weights = self._mean_variance_optimization(expected_returns, cov_matrix)
        elif self.config.method == OptimizationMethod.RISK_PARITY:
            weights = self._risk_parity_optimization(cov_matrix)
        elif self.config.method == OptimizationMethod.MINIMUM_VARIANCE:
            weights = self._minimum_variance_optimization(cov_matrix)
        elif self.config.method == OptimizationMethod.MAXIMUM_SHARPE:
            weights = self._maximum_sharpe_optimization(expected_returns, cov_matrix)
        elif self.config.method == OptimizationMethod.BLACK_LITTERMAN:
            weights = self._black_litterman_optimization(
                expected_returns, cov_matrix, market_caps, views
            )
        elif self.config.method == OptimizationMethod.EQUAL_WEIGHT:
            weights = {asset: 1.0 / n_assets for asset in assets}
        else:
            raise ValueError(f"Unsupported optimization method: {self.config.method}")

        # Apply constraints
        weights = self._apply_constraints(weights, current_weights)

        # Calculate portfolio metrics
        port_return = np.sum(weights * expected_returns)
        port_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        sharpe_ratio = (port_return - self.config.risk_free_rate) / port_volatility if port_volatility > 0 else 0

        return OptimizedPortfolio(
            weights=weights,
            expected_return=port_return,
            expected_volatility=port_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method=self.config.method,
            constraints_satisfied=self._check_constraints(weights, current_weights),
            optimization_date=pd.Timestamp.now()
        )

    def _mean_variance_optimization(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Mean-variance optimization."""
        assets = expected_returns.index.tolist()
        n_assets = len(assets)

        def objective(weights):
            port_return = np.sum(weights * expected_returns)
            port_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            return -(port_return - self.config.lambda_risk * port_volatility)  # Maximize return - risk

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
        ]

        bounds = [(self.config.min_weight, self.config.max_weight) for _ in range(n_assets)]

        # Add custom constraints
        for constraint in self.config.constraints:
            if constraint.constraint_type == 'weight' and constraint.asset:
                idx = assets.index(constraint.asset)
                if constraint.min_value is not None:
                    bounds[idx] = (max(bounds[idx][0], constraint.min_value), bounds[idx][1])
                if constraint.max_value is not None:
                    bounds[idx] = (bounds[idx][0], min(bounds[idx][1], constraint.max_value))

        result = minimize(
            objective,
            x0=np.array([1.0 / n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return dict(zip(assets, result.x))

    def _risk_parity_optimization(self, cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Risk parity optimization."""
        assets = cov_matrix.columns.tolist()
        n_assets = len(assets)

        def objective(weights):
            port_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_risk = np.dot(cov_matrix, weights) / port_volatility
            risk_contributions = weights * marginal_risk
            return np.var(risk_contributions)  # Minimize variance of risk contributions

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        ]

        bounds = [(self.config.min_weight, self.config.max_weight) for _ in range(n_assets)]

        result = minimize(
            objective,
            x0=np.array([1.0 / n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return dict(zip(assets, result.x))

    def _minimum_variance_optimization(self, cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Minimum variance optimization."""
        assets = cov_matrix.columns.tolist()
        n_assets = len(assets)

        def objective(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        ]

        bounds = [(self.config.min_weight, self.config.max_weight) for _ in range(n_assets)]

        result = minimize(
            objective,
            x0=np.array([1.0 / n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return dict(zip(assets, result.x))

    def _maximum_sharpe_optimization(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Maximum Sharpe ratio optimization."""
        assets = expected_returns.index.tolist()
        n_assets = len(assets)

        def objective(weights):
            port_return = np.sum(weights * expected_returns)
            port_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            return -(port_return - self.config.risk_free_rate) / port_volatility

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        ]

        bounds = [(self.config.min_weight, self.config.max_weight) for _ in range(n_assets)]

        result = minimize(
            objective,
            x0=np.array([1.0 / n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return dict(zip(assets, result.x))

    def _black_litterman_optimization(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        market_caps: Optional[Dict[str, float]] = None,
        views: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Black-Litterman optimization."""
        assets = expected_returns.index.tolist()

        # Simplified Black-Litterman implementation
        # In practice, this would be more sophisticated

        # Use market cap weights as prior if available
        if market_caps:
            total_cap = sum(market_caps.values())
            prior_weights = {asset: market_caps.get(asset, 0) / total_cap for asset in assets}
        else:
            prior_weights = {asset: 1.0 / len(assets) for asset in assets}

        # Adjust for views (simplified)
        if views:
            adjusted_weights = prior_weights.copy()
            for asset, view in views.items():
                if asset in adjusted_weights:
                    # Simple adjustment based on view
                    adjustment = view * 0.1  # 10% adjustment
                    adjusted_weights[asset] += adjustment
            # Renormalize
            total_weight = sum(adjusted_weights.values())
            adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
            return adjusted_weights

        return prior_weights

    def _apply_constraints(self, weights: Dict[str, float], current_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Apply portfolio constraints."""
        constrained_weights = weights.copy()

        # Turnover constraints
        if current_weights:
            for constraint in self.config.constraints:
                if constraint.constraint_type == 'turnover':
                    turnover = sum(abs(weights.get(asset, 0) - current_weights.get(asset, 0)) for asset in weights.keys())
                    if constraint.max_value and turnover > constraint.max_value:
                        # Scale down changes to meet turnover limit
                        scale_factor = constraint.max_value / turnover
                        for asset in weights.keys():
                            target_weight = current_weights.get(asset, 0) + (weights[asset] - current_weights.get(asset, 0)) * scale_factor
                            constrained_weights[asset] = target_weight

        # Renormalize
        total_weight = sum(constrained_weights.values())
        if total_weight > 0:
            constrained_weights = {k: v / total_weight for k, v in constrained_weights.items()}

        return constrained_weights

    def _check_constraints(self, weights: Dict[str, float], current_weights: Optional[Dict[str, float]] = None) -> bool:
        """Check if constraints are satisfied."""
        # Basic checks
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            return False

        # Individual weight limits
        for asset, weight in weights.items():
            if weight < self.config.min_weight or weight > self.config.max_weight:
                return False

        # Custom constraints
        for constraint in self.config.constraints:
            if constraint.constraint_type == 'weight' and constraint.asset:
                weight = weights.get(constraint.asset, 0)
                if constraint.min_value and weight < constraint.min_value:
                    return False
                if constraint.max_value and weight > constraint.max_value:
                    return False

        return True


class BacktestPortfolioOptimization:
    """Integrate portfolio optimization into backtesting."""

    def __init__(self, optimizer: PortfolioOptimizer):
        self.optimizer = optimizer
        self.optimization_history: List[OptimizedPortfolio] = []

    def run_optimized_backtest(
        self,
        asset_returns: pd.DataFrame,
        rebalance_dates: pd.DatetimeIndex,
        initial_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[pd.Series, List[OptimizedPortfolio]]:
        """Run backtest with periodic portfolio optimization."""

        assets = asset_returns.columns.tolist()
        current_weights = initial_weights or {asset: 1.0 / len(assets) for asset in assets}

        portfolio_values = []
        current_value = 1.0  # Start with $1

        optimization_dates = []
        all_optimized_portfolios = []

        for i, date in enumerate(asset_returns.index):
            # Check if rebalancing is needed
            if date in rebalance_dates or i == 0:
                # Get historical data up to current date for optimization
                historical_data = asset_returns.loc[:date]

                if len(historical_data) >= 30:  # Minimum data requirement
                    try:
                        optimized_portfolio = self.optimizer.optimize_portfolio(
                            historical_data, current_weights
                        )

                        current_weights = optimized_portfolio.weights
                        optimization_dates.append(date)
                        all_optimized_portfolios.append(optimized_portfolio)

                        logger.info(f"Portfolio rebalanced on {date.strftime('%Y-%m-%d')}")
                        logger.info(f"  New weights: {optimized_portfolio.weights}")

                    except Exception as e:
                        logger.warning(f"Optimization failed on {date}: {e}")

            # Calculate daily portfolio return
            daily_returns = asset_returns.loc[date]
            portfolio_return = sum(current_weights.get(asset, 0) * daily_returns[asset] for asset in assets)
            current_value *= (1 + portfolio_return)
            portfolio_values.append(current_value)

        portfolio_series = pd.Series(portfolio_values, index=asset_returns.index)

        return portfolio_series, all_optimized_portfolios

    def analyze_optimization_stability(self) -> Dict[str, float]:
        """Analyze stability of optimization results."""

        if not self.optimization_history:
            return {}

        # Calculate weight changes between rebalances
        weight_changes = []
        for i in range(1, len(self.optimization_history)):
            prev_weights = self.optimization_history[i-1].weights
            curr_weights = self.optimization_history[i].weights

            # Calculate turnover
            assets = set(prev_weights.keys()) | set(curr_weights.keys())
            turnover = sum(abs(curr_weights.get(asset, 0) - prev_weights.get(asset, 0)) for asset in assets)
            weight_changes.append(turnover)

        return {
            'average_turnover': np.mean(weight_changes) if weight_changes else 0,
            'max_turnover': max(weight_changes) if weight_changes else 0,
            'turnover_volatility': np.std(weight_changes) if weight_changes else 0,
            'optimization_frequency': len(self.optimization_history)
        }


# Convenience functions
def create_optimized_portfolio_config(
    method: OptimizationMethod = OptimizationMethod.RISK_PARITY,
    max_weight: float = 0.25,
    rebalance_frequency: str = "monthly"
) -> OptimizationConfig:
    """Create a standard optimized portfolio configuration."""

    constraints = [
        PortfolioConstraint(
            constraint_type="weight",
            max_value=max_weight
        )
    ]

    return OptimizationConfig(
        method=method,
        rebalance_frequency=rebalance_frequency,
        constraints=constraints,
        max_weight=max_weight,
        min_weight=0.0
    )


def optimize_and_backtest(
    asset_returns: pd.DataFrame,
    config: OptimizationConfig,
    rebalance_dates: Optional[pd.DatetimeIndex] = None
) -> Tuple[pd.Series, List[OptimizedPortfolio]]:
    """Convenience function for optimization and backtesting."""

    optimizer = PortfolioOptimizer(config)
    backtest_optimizer = BacktestPortfolioOptimization(optimizer)

    if rebalance_dates is None:
        # Default monthly rebalancing
        rebalance_dates = pd.date_range(
            start=asset_returns.index[0],
            end=asset_returns.index[-1],
            freq='M'
        )

    return backtest_optimizer.run_optimized_backtest(asset_returns, rebalance_dates)


__all__ = [
    "OptimizationMethod",
    "PortfolioConstraint",
    "OptimizationConfig",
    "OptimizedPortfolio",
    "PortfolioOptimizer",
    "BacktestPortfolioOptimization",
    "create_optimized_portfolio_config",
    "optimize_and_backtest",
]

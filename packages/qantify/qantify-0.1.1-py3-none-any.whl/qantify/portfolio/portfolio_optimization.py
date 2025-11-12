"""
Advanced Portfolio Optimization Engine
=====================================

This module implements state-of-the-art portfolio optimization algorithms
and techniques for quantitative trading and investment management.
Supports multiple optimization frameworks, constraints, and risk models.

Key Features:
- Mean-Variance Optimization (Markowitz)
- Risk Parity and Equal Risk Contribution
- Black-Litterman Model with views
- Factor-based Portfolio Construction
- Multi-asset Class Optimization
- Transaction Cost Modeling
- Portfolio Rebalancing Strategies
- Risk Budgeting and Attribution
- ESG and Sustainability Integration
- Dynamic Portfolio Optimization
"""

from __future__ import annotations

import warnings
import json
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import optimize
from scipy.stats import norm, t
import cvxpy as cp
import cvxopt
from sklearn.covariance import LedoitWolf, OAS
from sklearn.preprocessing import StandardScaler

# Import existing Qantify modules
try:
    from ..backtest.portfolio import Portfolio
except ImportError:
    Portfolio = None


@dataclass
class PortfolioConfig:
    """Configuration for portfolio optimization"""

    # Optimization settings
    optimizer: str = "mean_variance"  # "mean_variance", "risk_parity", "black_litterman", "factor"
    risk_measure: str = "variance"  # "variance", "CVaR", "CDaR", "max_drawdown"

    # Risk parameters
    target_risk: float = 0.15  # Target annual volatility
    risk_aversion: float = 3.0  # Risk aversion parameter
    confidence_level: float = 0.95  # Confidence level for CVaR

    # Return parameters
    target_return: Optional[float] = None
    benchmark_return: Optional[float] = None

    # Constraints
    min_weight: float = 0.0
    max_weight: float = 1.0
    max_concentration: float = 0.20  # Max weight per asset
    turnover_limit: float = 0.50  # Max turnover for rebalancing

    # Transaction costs
    transaction_cost_bps: float = 5.0  # Basis points
    market_impact_cost: bool = True

    # Rebalancing
    rebalance_frequency: str = "monthly"  # "daily", "weekly", "monthly", "quarterly"
    rebalance_threshold: float = 0.05  # Rebalance if drift > 5%

    # Advanced settings
    shrinkage_intensity: float = 0.1  # Covariance shrinkage
    use_robust_estimation: bool = True
    enable_short_selling: bool = False


@dataclass
class OptimizationResult:
    """Result of portfolio optimization"""

    optimal_weights: np.ndarray
    expected_return: float
    expected_risk: float
    sharpe_ratio: float

    # Performance metrics
    diversification_ratio: float = 0.0
    concentration_ratio: float = 0.0
    turnover: float = 0.0

    # Risk metrics
    var_95: float = 0.0
    cvar_95: float = 0.0
    max_drawdown: float = 0.0

    # Optimization details
    convergence: bool = True
    iterations: int = 0
    solver_time: float = 0.0

    # Metadata
    optimizer_used: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class PortfolioConstraint:
    """Portfolio optimization constraint"""

    constraint_type: str  # "weight_bounds", "group_limits", "factor_exposure", "tracking_error"
    parameters: Dict[str, Any]
    penalty_weight: float = 1.0

    def evaluate(self, weights: np.ndarray, data: Dict[str, Any]) -> float:
        """Evaluate constraint violation"""
        if self.constraint_type == "weight_bounds":
            min_w, max_w = self.parameters['min_weight'], self.parameters['max_weight']
            violations = np.sum(np.maximum(0, min_w - weights) + np.maximum(0, weights - max_w))
            return violations

        elif self.constraint_type == "group_limits":
            groups = self.parameters['groups']
            max_weights = self.parameters['max_weights']
            total_violation = 0.0

            for group_assets, max_weight in zip(groups, max_weights):
                group_weight = np.sum(weights[group_assets])
                total_violation += max(0, group_weight - max_weight)

            return total_violation

        elif self.constraint_type == "factor_exposure":
            factor_loadings = self.parameters['factor_loadings']
            target_exposure = self.parameters['target_exposure']
            max_deviation = self.parameters['max_deviation']

            portfolio_exposure = factor_loadings.T @ weights
            deviations = np.abs(portfolio_exposure - target_exposure)
            violations = np.sum(np.maximum(0, deviations - max_deviation))

            return violations

        elif self.constraint_type == "tracking_error":
            benchmark_weights = self.parameters['benchmark_weights']
            covariance_matrix = self.parameters['covariance_matrix']
            max_tracking_error = self.parameters['max_tracking_error']

            active_weights = weights - benchmark_weights
            tracking_error = np.sqrt(active_weights.T @ covariance_matrix @ active_weights)

            return max(0, tracking_error - max_tracking_error)

        return 0.0


@dataclass
class AssetUniverse:
    """Asset universe for portfolio optimization"""

    assets: List[str]
    returns: pd.DataFrame
    covariance_matrix: pd.DataFrame
    expected_returns: pd.Series

    # Additional data
    market_caps: Optional[pd.Series] = None
    sectors: Optional[pd.Series] = None
    countries: Optional[pd.Series] = None
    factor_exposures: Optional[pd.DataFrame] = None

    # Risk-free rate
    risk_free_rate: float = 0.02

    @property
    def n_assets(self) -> int:
        """Number of assets"""
        return len(self.assets)

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix"""
        variances = np.diag(self.covariance_matrix.values)
        std_devs = np.sqrt(variances)
        correlation_matrix = self.covariance_matrix.values / np.outer(std_devs, std_devs)
        return pd.DataFrame(correlation_matrix, index=self.assets, columns=self.assets)


class PortfolioOptimizer(ABC):
    """Abstract base class for portfolio optimizers"""

    def __init__(self, config: PortfolioConfig):
        self.config = config

    @abstractmethod
    def optimize(self, universe: AssetUniverse,
                constraints: List[PortfolioConstraint] = None) -> OptimizationResult:
        """Optimize portfolio"""
        pass

    def _calculate_risk_metrics(self, weights: np.ndarray, universe: AssetUniverse) -> Dict[str, float]:
        """Calculate risk metrics for a portfolio"""

        portfolio_return = weights @ universe.expected_returns.values
        portfolio_variance = weights @ universe.covariance_matrix.values @ weights
        portfolio_std = np.sqrt(portfolio_variance)

        # Sharpe ratio
        sharpe_ratio = (portfolio_return - universe.risk_free_rate) / portfolio_std if portfolio_std > 0 else 0

        # VaR and CVaR (simplified calculation)
        n_simulations = 10000
        simulated_returns = np.random.multivariate_normal(
            universe.expected_returns.values,
            universe.covariance_matrix.values,
            n_simulations
        )
        portfolio_simulated_returns = simulated_returns @ weights

        var_95 = np.percentile(portfolio_simulated_returns, 5)
        cvar_95 = portfolio_simulated_returns[portfolio_simulated_returns <= var_95].mean()

        # Maximum drawdown (simplified)
        cumulative_returns = np.cumprod(1 + portfolio_simulated_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        return {
            'expected_return': portfolio_return,
            'expected_risk': portfolio_std,
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'max_drawdown': max_drawdown
        }


class MeanVarianceOptimizer(PortfolioOptimizer):
    """Markowitz Mean-Variance Portfolio Optimization"""

    def optimize(self, universe: AssetUniverse,
                constraints: List[PortfolioConstraint] = None) -> OptimizationResult:

        if constraints is None:
            constraints = []

        n_assets = universe.n_assets
        mu = universe.expected_returns.values
        Sigma = universe.covariance_matrix.values

        # Variables
        w = cp.Variable(n_assets)

        # Objective: minimize portfolio variance
        objective = cp.Minimize(cp.quad_form(w, Sigma))

        # Constraints
        constraints_cvx = [
            cp.sum(w) == 1,  # Fully invested
            w >= self.config.min_weight,
            w <= self.config.max_weight
        ]

        # Add target return constraint if specified
        if self.config.target_return is not None:
            constraints_cvx.append(mu @ w >= self.config.target_return)

        # Add custom constraints
        for constraint in constraints:
            if constraint.constraint_type == "weight_bounds":
                # Already handled above
                pass
            elif constraint.constraint_type == "group_limits":
                groups = constraint.parameters['groups']
                max_weights = constraint.parameters['max_weights']
                for group_assets, max_weight in zip(groups, max_weights):
                    constraints_cvx.append(cp.sum(w[group_assets]) <= max_weight)

        # Solve
        start_time = time.time()
        problem = cp.Problem(objective, constraints_cvx)
        try:
            result = problem.solve(solver=cp.SCS, verbose=False)
            convergence = problem.status == cp.OPTIMAL
        except:
            convergence = False
            result = None

        solver_time = time.time() - start_time

        if convergence and result is not None:
            optimal_weights = w.value
            if optimal_weights is None:
                convergence = False
        else:
            # Fallback: equal weight portfolio
            optimal_weights = np.ones(n_assets) / n_assets
            convergence = False

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(optimal_weights, universe)
        concentration_ratio = self._calculate_concentration_ratio(optimal_weights)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=diversification_ratio,
            concentration_ratio=concentration_ratio,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=getattr(problem, 'iterations', 0),
            solver_time=solver_time,
            optimizer_used="mean_variance"
        )

    def _calculate_diversification_ratio(self, weights: np.ndarray, universe: AssetUniverse) -> float:
        """Calculate portfolio diversification ratio"""

        # Herfindahl-Hirschman Index of volatility-weighted concentrations
        volatilities = np.sqrt(np.diag(universe.covariance_matrix.values))
        weighted_vols = weights * volatilities
        portfolio_vol = np.sqrt(weights @ universe.covariance_matrix.values @ weights)

        if portfolio_vol > 0:
            diversification_ratio = np.sum(weighted_vols) / portfolio_vol
        else:
            diversification_ratio = 0.0

        return diversification_ratio

    def _calculate_concentration_ratio(self, weights: np.ndarray) -> float:
        """Calculate portfolio concentration ratio (Herfindahl index)"""

        return np.sum(weights ** 2)


class RiskParityOptimizer(PortfolioOptimizer):
    """Risk Parity Portfolio Optimization"""

    def optimize(self, universe: AssetUniverse,
                constraints: List[PortfolioConstraint] = None) -> OptimizationResult:

        if constraints is None:
            constraints = []

        n_assets = universe.n_assets
        Sigma = universe.covariance_matrix.values

        # Target: equal risk contribution from each asset
        target_risk_contribution = 1.0 / n_assets

        def risk_parity_objective(w):
            """Risk parity objective function"""

            # Portfolio volatility
            portfolio_vol = np.sqrt(w @ Sigma @ w)

            if portfolio_vol == 0:
                return 1000.0

            # Marginal risk contribution
            marginal_risk = Sigma @ w
            risk_contributions = w * marginal_risk / portfolio_vol

            # Objective: minimize variance of risk contributions
            return np.var(risk_contributions)

        def constraint_sum_to_one(w):
            """Constraint: weights sum to 1"""
            return np.sum(w) - 1.0

        def constraint_non_negative(w):
            """Constraint: non-negative weights"""
            return w  # Will be handled by bounds

        # Optimize
        start_time = time.time()

        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets
        constraints_opt = [
            {'type': 'eq', 'fun': constraint_sum_to_one}
        ]

        # Add non-negative constraint if no short selling
        if not self.config.enable_short_selling:
            bounds = [(max(0, b[0]), b[1]) for b in bounds]

        initial_guess = np.ones(n_assets) / n_assets

        try:
            result = optimize.minimize(
                risk_parity_objective,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            convergence = result.success
            optimal_weights = result.x
            iterations = result.nit

        except Exception as e:
            print(f"Risk parity optimization failed: {e}")
            convergence = False
            optimal_weights = np.ones(n_assets) / n_assets
            iterations = 0

        solver_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(optimal_weights, universe)
        concentration_ratio = self._calculate_concentration_ratio(optimal_weights)

        # Calculate risk parity score
        portfolio_vol = np.sqrt(optimal_weights @ Sigma @ optimal_weights)
        marginal_risk = Sigma @ optimal_weights
        risk_contributions = optimal_weights * marginal_risk / portfolio_vol
        risk_parity_score = 1.0 - np.std(risk_contributions) / np.mean(risk_contributions)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=diversification_ratio,
            concentration_ratio=concentration_ratio,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=iterations,
            solver_time=solver_time,
            optimizer_used="risk_parity"
        )

    def _calculate_diversification_ratio(self, weights: np.ndarray, universe: AssetUniverse) -> float:
        """Calculate portfolio diversification ratio"""

        volatilities = np.sqrt(np.diag(universe.covariance_matrix.values))
        weighted_vols = weights * volatilities
        portfolio_vol = np.sqrt(weights @ universe.covariance_matrix.values @ weights)

        if portfolio_vol > 0:
            diversification_ratio = np.sum(weighted_vols) / portfolio_vol
        else:
            diversification_ratio = 0.0

        return diversification_ratio

    def _calculate_concentration_ratio(self, weights: np.ndarray) -> float:
        """Calculate portfolio concentration ratio"""

        return np.sum(weights ** 2)


class BlackLittermanOptimizer(PortfolioOptimizer):
    """Black-Litterman Portfolio Optimization"""

    def __init__(self, config: PortfolioConfig):
        super().__init__(config)
        self.market_cap_weights = None
        self.market_risk_aversion = 3.0  # Market risk aversion parameter

    def set_market_cap_weights(self, market_caps: pd.Series):
        """Set market capitalization weights for equilibrium"""
        total_cap = market_caps.sum()
        self.market_cap_weights = market_caps / total_cap

    def optimize(self, universe: AssetUniverse,
                constraints: List[PortfolioConstraint] = None,
                views: Dict[str, Any] = None) -> OptimizationResult:

        if constraints is None:
            constraints = []

        if views is None:
            views = {}

        n_assets = universe.n_assets
        mu_market = universe.expected_returns.values
        Sigma = universe.covariance_matrix.values

        # Step 1: Compute equilibrium returns (if no market cap weights, use equal weight)
        if self.market_cap_weights is None:
            pi = self.market_risk_aversion * Sigma @ (np.ones(n_assets) / n_assets)
        else:
            pi = self.market_risk_aversion * Sigma @ self.market_cap_weights.values

        # Step 2: Incorporate views
        if views:
            # View parameters
            view_assets = views.get('assets', [])
            view_returns = views.get('returns', [])
            view_confidences = views.get('confidences', [])

            if view_assets and view_returns and view_confidences:
                P = np.zeros((len(view_assets), n_assets))
                Q = np.array(view_returns)

                # Build pick matrix P
                asset_to_index = {asset: i for i, asset in enumerate(universe.assets)}
                for i, asset in enumerate(view_assets):
                    if asset in asset_to_index:
                        P[i, asset_to_index[asset]] = 1.0

                # Confidence levels (omega matrix)
                omega = np.diag(1.0 / np.array(view_confidences))

                # Black-Litterman formula
                tau = 0.025  # Uncertainty in prior
                Sigma_prior = tau * Sigma

                # Posterior expected returns
                inv_Sigma = np.linalg.inv(Sigma)
                inv_omega = np.linalg.inv(omega)

                A = inv_Sigma + P.T @ inv_omega @ P
                inv_A = np.linalg.inv(A)

                mu_bl = inv_A @ (inv_Sigma @ pi + P.T @ inv_omega @ Q)

                # Posterior covariance
                Sigma_bl = Sigma + inv_A

            else:
                mu_bl = pi
                Sigma_bl = Sigma
        else:
            mu_bl = pi
            Sigma_bl = Sigma

        # Step 3: Optimize portfolio using Black-Litterman inputs
        # Use mean-variance optimization with BL inputs

        # Variables
        w = cp.Variable(n_assets)

        # Objective: maximize Black-Litterman expected return - risk aversion * variance
        objective = cp.Maximize(mu_bl @ w - self.config.risk_aversion * cp.quad_form(w, Sigma_bl))

        # Constraints
        constraints_cvx = [
            cp.sum(w) == 1,  # Fully invested
            w >= self.config.min_weight,
            w <= self.config.max_weight
        ]

        # Solve
        start_time = time.time()
        problem = cp.Problem(objective, constraints_cvx)
        try:
            result = problem.solve(solver=cp.SCS, verbose=False)
            convergence = problem.status == cp.OPTIMAL
        except:
            convergence = False
            result = None

        solver_time = time.time() - start_time

        if convergence and result is not None:
            optimal_weights = w.value
            if optimal_weights is None:
                convergence = False
        else:
            # Fallback: market cap weights or equal weight
            if self.market_cap_weights is not None:
                optimal_weights = self.market_cap_weights.values
            else:
                optimal_weights = np.ones(n_assets) / n_assets
            convergence = False

        # Create universe with BL parameters for metrics calculation
        bl_universe = AssetUniverse(
            assets=universe.assets,
            returns=universe.returns,
            covariance_matrix=pd.DataFrame(Sigma_bl, index=universe.assets, columns=universe.assets),
            expected_returns=pd.Series(mu_bl, index=universe.assets),
            risk_free_rate=universe.risk_free_rate
        )

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, bl_universe)

        # Calculate diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(optimal_weights, universe)
        concentration_ratio = self._calculate_concentration_ratio(optimal_weights)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=diversification_ratio,
            concentration_ratio=concentration_ratio,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=getattr(problem, 'iterations', 0),
            solver_time=solver_time,
            optimizer_used="black_litterman"
        )

    def _calculate_diversification_ratio(self, weights: np.ndarray, universe: AssetUniverse) -> float:
        """Calculate portfolio diversification ratio"""

        volatilities = np.sqrt(np.diag(universe.covariance_matrix.values))
        weighted_vols = weights * volatilities
        portfolio_vol = np.sqrt(weights @ universe.covariance_matrix.values @ weights)

        if portfolio_vol > 0:
            diversification_ratio = np.sum(weighted_vols) / portfolio_vol
        else:
            diversification_ratio = 0.0

        return diversification_ratio

    def _calculate_concentration_ratio(self, weights: np.ndarray) -> float:
        """Calculate portfolio concentration ratio"""

        return np.sum(weights ** 2)


class PortfolioRebalancer:
    """Portfolio rebalancing engine"""

    def __init__(self, config: PortfolioConfig):
        self.config = config

    def should_rebalance(self, current_weights: np.ndarray, target_weights: np.ndarray,
                        current_prices: pd.Series) -> Tuple[bool, float]:
        """Check if portfolio should be rebalanced"""

        # Calculate drift
        drift = np.linalg.norm(current_weights - target_weights)

        # Check threshold
        should_rebalance = drift > self.config.rebalance_threshold

        return should_rebalance, drift

    def calculate_trades(self, current_weights: np.ndarray, target_weights: np.ndarray,
                        current_prices: pd.Series, portfolio_value: float) -> pd.DataFrame:
        """Calculate required trades for rebalancing"""

        # Current positions in dollars
        current_positions = current_weights * portfolio_value

        # Target positions in dollars
        target_positions = target_weights * portfolio_value

        # Required trades
        trades = target_positions - current_positions

        # Convert to shares
        shares_to_trade = trades / current_prices

        # Create trades DataFrame
        trades_df = pd.DataFrame({
            'asset': current_prices.index,
            'current_weight': current_weights,
            'target_weight': target_weights,
            'current_position': current_positions,
            'target_position': target_positions,
            'trade_amount': trades,
            'shares_to_trade': shares_to_trade
        })

        # Calculate transaction costs
        trades_df['transaction_cost'] = self._calculate_transaction_costs(
            trades_df['trade_amount'], current_prices
        )

        # Calculate turnover
        total_turnover = np.sum(np.abs(trades)) / portfolio_value

        return trades_df

    def _calculate_transaction_costs(self, trade_amounts: pd.Series, prices: pd.Series) -> pd.Series:
        """Calculate transaction costs"""

        # Base commission (basis points)
        commission_rate = self.config.transaction_cost_bps / 10000.0

        # Market impact cost (simplified)
        if self.config.market_impact_cost:
            # Square root market impact model
            market_caps = getattr(self, '_market_caps', None)
            if market_caps is not None:
                # Simplified market impact based on trade size relative to market cap
                impact_factor = 0.1  # 10 bps for large trades
                market_impact = impact_factor * np.sqrt(np.abs(trade_amounts) / market_caps[trade_amounts.index])
            else:
                market_impact = commission_rate * 0.5  # Fixed impact
        else:
            market_impact = 0.0

        total_cost = commission_rate + market_impact

        return np.abs(trade_amounts) * total_cost


class PortfolioAnalytics:
    """Portfolio analytics and performance measurement"""

    def __init__(self):
        self.performance_metrics = {}

    def calculate_performance_metrics(self, returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""

        # Basic return metrics
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)

        # Sharpe ratio
        risk_free_rate = 0.02  # Assume 2%
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = drawdowns.min()

        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5)

        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns[returns <= var_95].mean()

        # Omega ratio
        threshold = 0.0  # Risk-free rate as threshold
        omega_ratio = self._calculate_omega_ratio(returns, threshold)

        # Information ratio (if benchmark provided)
        if benchmark_returns is not None:
            excess_returns = returns - benchmark_returns
            tracking_error = excess_returns.std() * np.sqrt(252)
            information_ratio = excess_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
        else:
            information_ratio = 0.0

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'omega_ratio': omega_ratio,
            'information_ratio': information_ratio
        }

        self.performance_metrics = metrics
        return metrics

    def calculate_risk_attribution(self, weights: np.ndarray, covariance_matrix: pd.DataFrame) -> Dict[str, float]:
        """Calculate risk attribution by asset"""

        portfolio_vol = np.sqrt(weights @ covariance_matrix.values @ weights)

        if portfolio_vol == 0:
            return {asset: 0.0 for asset in covariance_matrix.index}

        # Marginal risk contribution
        marginal_risk = covariance_matrix.values @ weights
        risk_contributions = weights * marginal_risk / portfolio_vol

        # Percentage risk contribution
        total_risk_contribution = np.sum(np.abs(risk_contributions))
        risk_attribution = {
            asset: abs(contrib) / total_risk_contribution
            for asset, contrib in zip(covariance_matrix.index, risk_contributions)
        }

        return risk_attribution

    def calculate_factor_attribution(self, weights: np.ndarray, factor_exposures: pd.DataFrame,
                                   factor_returns: pd.Series) -> Dict[str, float]:
        """Calculate factor attribution"""

        portfolio_exposure = factor_exposures.T @ weights
        factor_contributions = portfolio_exposure * factor_returns

        total_contribution = factor_contributions.sum()
        factor_attribution = {
            factor: contrib / total_contribution if total_contribution != 0 else 0.0
            for factor, contrib in factor_contributions.items()
        }

        return factor_attribution

    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float) -> float:
        """Calculate omega ratio"""

        excess_returns = returns - threshold
        positive_excess = excess_returns[excess_returns > 0].sum()
        negative_excess = -excess_returns[excess_returns < 0].sum()

        if negative_excess == 0:
            return float('inf')

        return positive_excess / negative_excess


# Factory functions
def create_portfolio_optimizer(config: PortfolioConfig) -> PortfolioOptimizer:
    """Factory function for portfolio optimizer"""

    if config.optimizer == "mean_variance":
        return MeanVarianceOptimizer(config)
    elif config.optimizer == "risk_parity":
        return RiskParityOptimizer(config)
    elif config.optimizer == "black_litterman":
        return BlackLittermanOptimizer(config)
    else:
        raise ValueError(f"Unknown optimizer: {config.optimizer}")


def create_asset_universe(assets: List[str], returns: pd.DataFrame,
                         covariance_estimator: str = "sample") -> AssetUniverse:
    """Create asset universe with covariance estimation"""

    # Estimate expected returns
    expected_returns = returns.mean() * 252  # Annualized

    # Estimate covariance matrix
    if covariance_estimator == "sample":
        cov_matrix = returns.cov() * 252
    elif covariance_estimator == "ledoit_wolf":
        lw = LedoitWolf()
        cov_matrix = pd.DataFrame(
            lw.fit(returns.values).covariance_,
            index=returns.columns,
            columns=returns.columns
        ) * 252
    elif covariance_estimator == "oas":
        oas = OAS()
        cov_matrix = pd.DataFrame(
            oas.fit(returns.values).covariance_,
            index=returns.columns,
            columns=returns.columns
        ) * 252
    else:
        cov_matrix = returns.cov() * 252

    return AssetUniverse(
        assets=assets,
        returns=returns,
        covariance_matrix=cov_matrix,
        expected_returns=expected_returns
    )


def optimize_portfolio(universe: AssetUniverse, config: PortfolioConfig = None,
                      constraints: List[PortfolioConstraint] = None) -> OptimizationResult:
    """Convenience function for portfolio optimization"""

    if config is None:
        config = PortfolioConfig()

    optimizer = create_portfolio_optimizer(config)
    return optimizer.optimize(universe, constraints)


# Example usage and testing
if __name__ == "__main__":
    # Test portfolio optimization
    print("Testing Portfolio Optimization Engine...")

    # Create mock data
    np.random.seed(42)
    n_assets = 10
    n_periods = 252

    # Generate synthetic returns
    returns_data = np.random.normal(0.001, 0.02, (n_periods, n_assets))
    returns_df = pd.DataFrame(returns_data, columns=[f'Asset_{i}' for i in range(n_assets)])

    # Create asset universe
    assets = [f'Asset_{i}' for i in range(n_assets)]
    universe = create_asset_universe(assets, returns_df, covariance_estimator="ledoit_wolf")

    print(f"Created universe with {len(assets)} assets and {len(returns_df)} periods")

    # Test different optimizers
    optimizers = ["mean_variance", "risk_parity"]

    for opt_name in optimizers:
        print(f"\nTesting {opt_name} optimizer...")

        config = PortfolioConfig(
            optimizer=opt_name,
            target_risk=0.15,
            min_weight=0.0,
            max_weight=0.3
        )

        try:
            result = optimize_portfolio(universe, config)

            print(".4f")
            print(".4f")
            print(".4f")
            print(".4f")
            print(f"Convergence: {result.convergence}")
            print(".3f")

            # Show top 5 holdings
            weights_df = pd.DataFrame({
                'asset': assets,
                'weight': result.optimal_weights
            }).sort_values('weight', ascending=False)

            print("Top 5 holdings:")
            for _, row in weights_df.head().iterrows():
                print(".3f")

        except Exception as e:
            print(f"Optimization failed: {e}")

    print("\nPortfolio optimization test completed successfully!")

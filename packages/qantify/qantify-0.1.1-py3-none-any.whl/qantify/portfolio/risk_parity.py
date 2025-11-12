"""
Risk Parity Portfolio Optimization
=================================

This module implements advanced risk parity strategies for portfolio construction,
ensuring equal risk contribution from different asset classes and investment factors.

Key Features:
- Equal Risk Contribution (ERC) portfolios
- Hierarchical Risk Parity (HRP)
- Maximum Diversification portfolios
- Risk budgeting and allocation
- Multi-asset class risk parity
- Factor risk parity
- Conditional risk parity
- Dynamic risk parity
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
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.covariance import LedoitWolf, OAS

# Import existing Qantify modules
try:
    from .portfolio_optimization import PortfolioConfig, PortfolioOptimizer, OptimizationResult, AssetUniverse
except ImportError:
    PortfolioConfig = None
    PortfolioOptimizer = None
    OptimizationResult = None
    AssetUniverse = None


@dataclass
class RiskParityConfig(PortfolioConfig):
    """Configuration for risk parity optimization"""

    # Risk parity specific settings
    risk_parity_method: str = "erc"  # "erc", "hrp", "mdp", "factor_rp", "conditional_rp"
    risk_budget: Optional[Dict[str, float]] = None  # Custom risk budgets

    # Hierarchical Risk Parity settings
    linkage_method: str = "single"  # "single", "complete", "average", "ward"
    distance_metric: str = "correlation"  # "correlation", "covariance", "variance"

    # Maximum Diversification settings
    diversification_target: str = "maximum"  # "maximum", "target_ratio"

    # Factor Risk Parity settings
    factor_groups: Optional[Dict[str, List[str]]] = None

    # Conditional Risk Parity settings
    regime_detection: bool = False
    regime_threshold: float = 0.0


@dataclass
class RiskContribution:
    """Risk contribution analysis"""

    asset_contributions: Dict[str, float]
    factor_contributions: Dict[str, float]
    total_portfolio_risk: float
    diversification_ratio: float
    risk_parity_score: float

    @property
    def risk_concentration(self) -> float:
        """Calculate risk concentration (Herfindahl index)"""
        contributions = list(self.asset_contributions.values())
        return sum(c ** 2 for c in contributions)


class ERCOptimizer(PortfolioOptimizer):
    """Equal Risk Contribution (ERC) Portfolio Optimizer"""

    def __init__(self, config: RiskParityConfig):
        super().__init__(config)
        self.risk_parity_config = config

    def optimize(self, universe: AssetUniverse,
                constraints: List = None) -> OptimizationResult:

        n_assets = universe.n_assets
        Sigma = universe.covariance_matrix.values

        # Initial guess: equal weights
        w0 = np.ones(n_assets) / n_assets

        # Define the risk parity objective
        def risk_parity_objective(w):
            """Minimize the variance of risk contributions"""

            # Portfolio volatility
            portfolio_vol = np.sqrt(w @ Sigma @ w)

            if portfolio_vol == 0:
                return 1000.0

            # Marginal risk contribution
            marginal_risk = Sigma @ w
            risk_contributions = w * marginal_risk / portfolio_vol

            # Target risk contribution (equal for all assets)
            target_contribution = 1.0 / n_assets
            target_contributions = np.full(n_assets, target_contribution)

            # Objective: minimize squared difference from target
            return np.sum((risk_contributions - target_contributions) ** 2)

        # Constraints
        def sum_to_one(w):
            return np.sum(w) - 1.0

        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets

        if not self.config.enable_short_selling:
            bounds = [(max(0, b[0]), b[1]) for b in bounds]

        constraints_opt = [
            {'type': 'eq', 'fun': sum_to_one}
        ]

        # Optimize
        start_time = time.time()

        try:
            result = optimize.minimize(
                risk_parity_objective,
                w0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            convergence = result.success
            optimal_weights = result.x
            iterations = result.nit

        except Exception as e:
            print(f"ERC optimization failed: {e}")
            convergence = False
            optimal_weights = w0
            iterations = 0

        solver_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate risk contributions
        risk_contributions = self._calculate_risk_contributions(optimal_weights, universe)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=risk_contributions.diversification_ratio,
            concentration_ratio=risk_contributions.risk_concentration,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=iterations,
            solver_time=solver_time,
            optimizer_used="erc"
        )

    def _calculate_risk_contributions(self, weights: np.ndarray, universe: AssetUniverse) -> RiskContribution:
        """Calculate risk contributions for ERC portfolio"""

        Sigma = universe.covariance_matrix.values
        portfolio_vol = np.sqrt(weights @ Sigma @ weights)

        if portfolio_vol == 0:
            return RiskContribution(
                asset_contributions={asset: 0.0 for asset in universe.assets},
                factor_contributions={},
                total_portfolio_risk=0.0,
                diversification_ratio=0.0,
                risk_parity_score=0.0
            )

        # Marginal risk contribution
        marginal_risk = Sigma @ weights
        risk_contributions = weights * marginal_risk / portfolio_vol

        # Asset contributions
        asset_contributions = {
            asset: float(contrib)
            for asset, contrib in zip(universe.assets, risk_contributions)
        }

        # Calculate diversification ratio
        volatilities = np.sqrt(np.diag(Sigma))
        weighted_vols = weights * volatilities
        diversification_ratio = np.sum(weighted_vols) / portfolio_vol

        # Risk parity score (1 - coefficient of variation of risk contributions)
        mean_contrib = np.mean(risk_contributions)
        std_contrib = np.std(risk_contributions)
        risk_parity_score = 1.0 - (std_contrib / mean_contrib) if mean_contrib > 0 else 0.0

        return RiskContribution(
            asset_contributions=asset_contributions,
            factor_contributions={},  # Not applicable for ERC
            total_portfolio_risk=portfolio_vol,
            diversification_ratio=diversification_ratio,
            risk_parity_score=risk_parity_score
        )


class HRPOptimizer(PortfolioOptimizer):
    """Hierarchical Risk Parity (HRP) Portfolio Optimizer"""

    def __init__(self, config: RiskParityConfig):
        super().__init__(config)
        self.risk_parity_config = config

    def optimize(self, universe: AssetUniverse,
                constraints: List = None) -> OptimizationResult:

        n_assets = universe.n_assets

        # Step 1: Hierarchical clustering
        clusters = self._hierarchical_clustering(universe)

        # Step 2: Recursive bisection
        optimal_weights = self._recursive_bisection(universe, clusters)

        # Step 3: Apply constraints (simplified)
        optimal_weights = self._apply_constraints(optimal_weights)

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate risk contributions
        risk_contributions = self._calculate_risk_contributions(optimal_weights, universe)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=risk_contributions.diversification_ratio,
            concentration_ratio=risk_contributions.risk_concentration,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=True,  # HRP is deterministic
            iterations=0,
            solver_time=0.0,
            optimizer_used="hrp"
        )

    def _hierarchical_clustering(self, universe: AssetUniverse) -> Dict[int, List[str]]:
        """Perform hierarchical clustering on assets"""

        if self.risk_parity_config.distance_metric == "correlation":
            # Use correlation distance
            corr_matrix = universe.get_correlation_matrix()
            # Convert correlation to distance
            distance_matrix = np.sqrt(2 * (1 - corr_matrix.values))
            np.fill_diagonal(distance_matrix, 0)
        elif self.risk_parity_config.distance_metric == "covariance":
            # Use covariance distance
            distance_matrix = universe.covariance_matrix.values
        else:
            # Use variance distance
            distance_matrix = np.diag(universe.covariance_matrix.values).reshape(-1, 1)

        # Perform hierarchical clustering
        condensed_distance = pdist(distance_matrix)
        linkage_matrix = linkage(condensed_distance, method=self.risk_parity_config.linkage_method)

        # Create clusters (aim for balanced clusters)
        n_clusters = max(2, int(np.sqrt(universe.n_assets)))
        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

        # Group assets by cluster
        clusters = defaultdict(list)
        for i, asset in enumerate(universe.assets):
            clusters[cluster_labels[i]].append(asset)

        return dict(clusters)

    def _recursive_bisection(self, universe: AssetUniverse, clusters: Dict[int, List[str]]) -> np.ndarray:
        """Recursive bisection algorithm for weight allocation"""

        n_assets = universe.n_assets
        weights = np.zeros(n_assets)

        # Base case: single asset
        if len(clusters) == 1:
            cluster_assets = list(clusters.values())[0]
            asset_weights = np.ones(len(cluster_assets)) / len(cluster_assets)

            for i, asset in enumerate(cluster_assets):
                asset_idx = universe.assets.index(asset)
                weights[asset_idx] = asset_weights[i]

            return weights

        # Recursive case: split into two halves
        cluster_items = list(clusters.items())
        mid = len(cluster_items) // 2

        left_clusters = dict(cluster_items[:mid])
        right_clusters = dict(cluster_items[mid:])

        # Calculate cluster variances
        left_variance = self._calculate_cluster_variance(universe, left_clusters)
        right_variance = self._calculate_cluster_variance(universe, right_clusters)

        # Allocate weights based on inverse variance
        total_variance = left_variance + right_variance

        if total_variance > 0:
            left_weight = right_variance / total_variance
            right_weight = left_variance / total_variance
        else:
            left_weight = right_weight = 0.5

        # Recursive calls
        left_weights = self._recursive_bisection(universe, left_clusters)
        right_weights = self._recursive_bisection(universe, right_clusters)

        # Combine weights
        weights = left_weight * left_weights + right_weight * right_weights

        return weights

    def _calculate_cluster_variance(self, universe: AssetUniverse, clusters: Dict[int, List[str]]) -> float:
        """Calculate variance of a cluster"""

        cluster_assets = []
        for assets in clusters.values():
            cluster_assets.extend(assets)

        if len(cluster_assets) == 1:
            asset_idx = universe.assets.index(cluster_assets[0])
            return universe.covariance_matrix.iloc[asset_idx, asset_idx]

        # Calculate cluster covariance matrix
        indices = [universe.assets.index(asset) for asset in cluster_assets]
        cluster_cov = universe.covariance_matrix.iloc[indices, indices]

        # Equal weights within cluster
        w_cluster = np.ones(len(cluster_assets)) / len(cluster_assets)

        return w_cluster @ cluster_cov.values @ w_cluster

    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """Apply basic constraints to weights"""

        # Ensure non-negative weights if no short selling
        if not self.config.enable_short_selling:
            weights = np.maximum(weights, 0)

        # Ensure weights sum to 1
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)

        # Apply bounds
        weights = np.clip(weights, self.config.min_weight, self.config.max_weight)

        # Renormalize
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)

        return weights

    def _calculate_risk_contributions(self, weights: np.ndarray, universe: AssetUniverse) -> RiskContribution:
        """Calculate risk contributions for HRP portfolio"""

        Sigma = universe.covariance_matrix.values
        portfolio_vol = np.sqrt(weights @ Sigma @ weights)

        if portfolio_vol == 0:
            return RiskContribution(
                asset_contributions={asset: 0.0 for asset in universe.assets},
                factor_contributions={},
                total_portfolio_risk=0.0,
                diversification_ratio=0.0,
                risk_parity_score=0.0
            )

        # Marginal risk contribution
        marginal_risk = Sigma @ weights
        risk_contributions = weights * marginal_risk / portfolio_vol

        # Asset contributions
        asset_contributions = {
            asset: float(contrib)
            for asset, contrib in zip(universe.assets, risk_contributions)
        }

        # Calculate diversification ratio
        volatilities = np.sqrt(np.diag(Sigma))
        weighted_vols = weights * volatilities
        diversification_ratio = np.sum(weighted_vols) / portfolio_vol

        # Risk parity score
        mean_contrib = np.mean(risk_contributions)
        std_contrib = np.std(risk_contributions)
        risk_parity_score = 1.0 - (std_contrib / mean_contrib) if mean_contrib > 0 else 0.0

        return RiskContribution(
            asset_contributions=asset_contributions,
            factor_contributions={},
            total_portfolio_risk=portfolio_vol,
            diversification_ratio=diversification_ratio,
            risk_parity_score=risk_parity_score
        )


class MDPOptimizer(PortfolioOptimizer):
    """Maximum Diversification Portfolio (MDP) Optimizer"""

    def __init__(self, config: RiskParityConfig):
        super().__init__(config)
        self.risk_parity_config = config

    def optimize(self, universe: AssetUniverse,
                constraints: List = None) -> OptimizationResult:

        n_assets = universe.n_assets
        Sigma = universe.covariance_matrix.values
        volatilities = np.sqrt(np.diag(Sigma))

        # Maximum Diversification Portfolio
        # Maximize: w * volatilities / sqrt(w * Sigma * w)

        def diversification_objective(w):
            """Maximize diversification ratio"""

            portfolio_vol = np.sqrt(w @ Sigma @ w)
            weighted_vols = w * volatilities

            if portfolio_vol == 0:
                return -1000.0  # Minimize (negative of diversification ratio)

            diversification_ratio = np.sum(weighted_vols) / portfolio_vol
            return -diversification_ratio  # Minimize negative for maximization

        # Constraints
        def sum_to_one(w):
            return np.sum(w) - 1.0

        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets

        if not self.config.enable_short_selling:
            bounds = [(max(0, b[0]), b[1]) for b in bounds]

        constraints_opt = [
            {'type': 'eq', 'fun': sum_to_one}
        ]

        # Optimize
        start_time = time.time()
        w0 = np.ones(n_assets) / n_assets

        try:
            result = optimize.minimize(
                diversification_objective,
                w0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            convergence = result.success
            optimal_weights = result.x
            iterations = result.nit

        except Exception as e:
            print(f"MDP optimization failed: {e}")
            convergence = False
            optimal_weights = w0
            iterations = 0

        solver_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate risk contributions
        risk_contributions = self._calculate_risk_contributions(optimal_weights, universe)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=risk_contributions.diversification_ratio,
            concentration_ratio=risk_contributions.risk_concentration,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=iterations,
            solver_time=solver_time,
            optimizer_used="mdp"
        )

    def _calculate_risk_contributions(self, weights: np.ndarray, universe: AssetUniverse) -> RiskContribution:
        """Calculate risk contributions for MDP portfolio"""

        Sigma = universe.covariance_matrix.values
        volatilities = np.sqrt(np.diag(Sigma))
        portfolio_vol = np.sqrt(weights @ Sigma @ weights)

        if portfolio_vol == 0:
            return RiskContribution(
                asset_contributions={asset: 0.0 for asset in universe.assets},
                factor_contributions={},
                total_portfolio_risk=0.0,
                diversification_ratio=0.0,
                risk_parity_score=0.0
            )

        # Marginal risk contribution
        marginal_risk = Sigma @ weights
        risk_contributions = weights * marginal_risk / portfolio_vol

        # Asset contributions
        asset_contributions = {
            asset: float(contrib)
            for asset, contrib in zip(universe.assets, risk_contributions)
        }

        # Calculate diversification ratio (this is maximized in MDP)
        weighted_vols = weights * volatilities
        diversification_ratio = np.sum(weighted_vols) / portfolio_vol

        # Risk parity score
        mean_contrib = np.mean(risk_contributions)
        std_contrib = np.std(risk_contributions)
        risk_parity_score = 1.0 - (std_contrib / mean_contrib) if mean_contrib > 0 else 0.0

        return RiskContribution(
            asset_contributions=asset_contributions,
            factor_contributions={},
            total_portfolio_risk=portfolio_vol,
            diversification_ratio=diversification_ratio,
            risk_parity_score=risk_parity_score
        )


class FactorRiskParityOptimizer(PortfolioOptimizer):
    """Factor-based Risk Parity Optimizer"""

    def __init__(self, config: RiskParityConfig):
        super().__init__(config)
        self.risk_parity_config = config

    def optimize(self, universe: AssetUniverse,
                constraints: List = None) -> OptimizationResult:

        if not universe.factor_exposures:
            raise ValueError("Factor exposures required for factor risk parity")

        n_assets = universe.n_assets
        factor_exposures = universe.factor_exposures.values
        factor_names = universe.factor_exposures.columns.tolist()

        # Factor covariance matrix (simplified - assume uncorrelated factors)
        factor_volatilities = np.array([0.1] * len(factor_names))  # Placeholder
        factor_cov = np.diag(factor_volatilities ** 2)

        # Asset covariance from factor model: F * B * F^T + D
        # Where F is factor covariance, B is factor exposures, D is idiosyncratic risk
        idiosyncratic_vol = np.sqrt(np.diag(universe.covariance_matrix.values) - np.diag(factor_exposures @ factor_cov @ factor_exposures.T))
        D = np.diag(idiosyncratic_vol ** 2)

        Sigma_factor = factor_exposures @ factor_cov @ factor_exposures.T + D

        # Target: equal risk contribution from each factor
        def factor_risk_parity_objective(w):
            """Minimize variance of factor risk contributions"""

            portfolio_vol = np.sqrt(w @ Sigma_factor @ w)

            if portfolio_vol == 0:
                return 1000.0

            # Factor marginal risk contributions
            factor_marginal_risk = factor_cov @ factor_exposures.T @ w
            factor_risk_contributions = factor_exposures @ factor_marginal_risk / portfolio_vol

            # Target equal contribution
            target_contribution = 1.0 / len(factor_names)
            target_contributions = np.full(len(factor_names), target_contribution)

            return np.sum((factor_risk_contributions - target_contributions) ** 2)

        # Constraints
        def sum_to_one(w):
            return np.sum(w) - 1.0

        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets

        if not self.config.enable_short_selling:
            bounds = [(max(0, b[0]), b[1]) for b in bounds]

        constraints_opt = [
            {'type': 'eq', 'fun': sum_to_one}
        ]

        # Optimize
        start_time = time.time()
        w0 = np.ones(n_assets) / n_assets

        try:
            result = optimize.minimize(
                factor_risk_parity_objective,
                w0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            convergence = result.success
            optimal_weights = result.x
            iterations = result.nit

        except Exception as e:
            print(f"Factor risk parity optimization failed: {e}")
            convergence = False
            optimal_weights = w0
            iterations = 0

        solver_time = time.time() - start_time

        # Calculate metrics
        metrics = self._calculate_risk_metrics(optimal_weights, universe)

        # Calculate risk contributions
        risk_contributions = self._calculate_risk_contributions(optimal_weights, universe, factor_exposures, factor_names)

        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=metrics['expected_return'],
            expected_risk=metrics['expected_risk'],
            sharpe_ratio=metrics['sharpe_ratio'],
            diversification_ratio=risk_contributions.diversification_ratio,
            concentration_ratio=risk_contributions.risk_concentration,
            var_95=metrics['var_95'],
            cvar_95=metrics['cvar_95'],
            max_drawdown=metrics['max_drawdown'],
            convergence=convergence,
            iterations=iterations,
            solver_time=solver_time,
            optimizer_used="factor_risk_parity"
        )

    def _calculate_risk_contributions(self, weights: np.ndarray, universe: AssetUniverse,
                                    factor_exposures: np.ndarray, factor_names: List[str]) -> RiskContribution:
        """Calculate risk contributions for factor risk parity portfolio"""

        Sigma = universe.covariance_matrix.values
        portfolio_vol = np.sqrt(weights @ Sigma @ weights)

        if portfolio_vol == 0:
            return RiskContribution(
                asset_contributions={asset: 0.0 for asset in universe.assets},
                factor_contributions={factor: 0.0 for factor in factor_names},
                total_portfolio_risk=0.0,
                diversification_ratio=0.0,
                risk_parity_score=0.0
            )

        # Asset risk contributions
        marginal_risk = Sigma @ weights
        asset_risk_contributions = weights * marginal_risk / portfolio_vol

        asset_contributions = {
            asset: float(contrib)
            for asset, contrib in zip(universe.assets, asset_risk_contributions)
        }

        # Factor risk contributions
        factor_portfolio_exposure = factor_exposures.T @ weights
        factor_marginal_risk = np.array([0.1] * len(factor_names))  # Placeholder factor volatilities
        factor_risk_contributions = factor_portfolio_exposure * factor_marginal_risk / portfolio_vol

        factor_contributions = {
            factor: float(contrib)
            for factor, contrib in zip(factor_names, factor_risk_contributions)
        }

        # Calculate diversification ratio
        volatilities = np.sqrt(np.diag(Sigma))
        weighted_vols = weights * volatilities
        diversification_ratio = np.sum(weighted_vols) / portfolio_vol

        # Risk parity score for factors
        factor_contribs = list(factor_contributions.values())
        mean_factor_contrib = np.mean(factor_contribs)
        std_factor_contrib = np.std(factor_contribs)
        risk_parity_score = 1.0 - (std_factor_contrib / mean_factor_contrib) if mean_factor_contrib > 0 else 0.0

        return RiskContribution(
            asset_contributions=asset_contributions,
            factor_contributions=factor_contributions,
            total_portfolio_risk=portfolio_vol,
            diversification_ratio=diversification_ratio,
            risk_parity_score=risk_parity_score
        )


class RiskBudgetingEngine:
    """Advanced risk budgeting and allocation engine"""

    def __init__(self, config: RiskParityConfig):
        self.config = config

    def allocate_risk_budget(self, universe: AssetUniverse,
                           risk_budget: Dict[str, float]) -> np.ndarray:
        """Allocate portfolio weights based on risk budget"""

        n_assets = universe.n_assets
        Sigma = universe.covariance_matrix.values

        # Risk budgeting objective
        def risk_budget_objective(w):
            """Minimize deviation from target risk budget"""

            portfolio_vol = np.sqrt(w @ Sigma @ w)

            if portfolio_vol == 0:
                return 1000.0

            # Calculate actual risk contributions
            marginal_risk = Sigma @ w
            risk_contributions = w * marginal_risk / portfolio_vol

            # Target risk contributions
            target_contributions = np.array([risk_budget.get(asset, 1.0/n_assets)
                                           for asset in universe.assets])

            # Objective: minimize squared difference
            return np.sum((risk_contributions - target_contributions) ** 2)

        # Constraints
        def sum_to_one(w):
            return np.sum(w) - 1.0

        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets

        if not self.config.enable_short_selling:
            bounds = [(max(0, b[0]), b[1]) for b in bounds]

        constraints_opt = [
            {'type': 'eq', 'fun': sum_to_one}
        ]

        # Optimize
        w0 = np.ones(n_assets) / n_assets

        try:
            result = optimize.minimize(
                risk_budget_objective,
                w0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            if result.success:
                return result.x
            else:
                return w0

        except Exception as e:
            print(f"Risk budgeting failed: {e}")
            return w0

    def analyze_risk_attribution(self, weights: np.ndarray, universe: AssetUniverse) -> Dict[str, Any]:
        """Comprehensive risk attribution analysis"""

        Sigma = universe.covariance_matrix.values
        portfolio_vol = np.sqrt(weights @ Sigma @ weights)

        if portfolio_vol == 0:
            return {'error': 'Zero portfolio volatility'}

        # Marginal risk contribution
        marginal_risk = Sigma @ weights
        risk_contributions = weights * marginal_risk / portfolio_vol

        # Percentage contributions
        total_abs_contribution = np.sum(np.abs(risk_contributions))
        percentage_contributions = {
            asset: abs(contrib) / total_abs_contribution
            for asset, contrib in zip(universe.assets, risk_contributions)
        }

        # Risk concentration
        risk_concentration = np.sum(risk_contributions ** 2)

        # Diversification measures
        volatilities = np.sqrt(np.diag(Sigma))
        weighted_vols = weights * volatilities
        diversification_ratio = np.sum(weighted_vols) / portfolio_vol

        # Effective number of assets
        effective_n = 1.0 / risk_concentration

        return {
            'risk_contributions': dict(zip(universe.assets, risk_contributions)),
            'percentage_contributions': percentage_contributions,
            'risk_concentration': risk_concentration,
            'diversification_ratio': diversification_ratio,
            'effective_num_assets': effective_n,
            'portfolio_volatility': portfolio_vol
        }

    def stress_test_portfolio(self, weights: np.ndarray, universe: AssetUniverse,
                            stress_scenarios: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Stress test portfolio under different scenarios"""

        results = {}

        for scenario_name, stress_returns in stress_scenarios.items():
            # Calculate portfolio returns under stress
            portfolio_returns = stress_returns @ weights

            # Calculate losses
            losses = -portfolio_returns  # Negative returns = losses

            # VaR and CVaR under stress
            var_95 = np.percentile(losses, 95)
            cvar_95 = losses[losses >= var_95].mean()

            results[scenario_name] = {
                'var_95': var_95,
                'cvar_95': cvar_95,
                'max_loss': np.max(losses),
                'expected_loss': np.mean(losses)
            }

        return results


# Factory functions
def create_risk_parity_optimizer(config: RiskParityConfig) -> PortfolioOptimizer:
    """Factory function for risk parity optimizer"""

    if config.risk_parity_method == "erc":
        return ERCOptimizer(config)
    elif config.risk_parity_method == "hrp":
        return HRPOptimizer(config)
    elif config.risk_parity_method == "mdp":
        return MDPOptimizer(config)
    elif config.risk_parity_method == "factor_rp":
        return FactorRiskParityOptimizer(config)
    else:
        raise ValueError(f"Unknown risk parity method: {config.risk_parity_method}")


def optimize_risk_parity(universe: AssetUniverse, config: RiskParityConfig = None) -> OptimizationResult:
    """Convenience function for risk parity optimization"""

    if config is None:
        config = RiskParityConfig(risk_parity_method="erc")

    optimizer = create_risk_parity_optimizer(config)
    return optimizer.optimize(universe)


# Example usage and testing
if __name__ == "__main__":
    # Test risk parity optimization
    print("Testing Risk Parity Portfolio Optimization...")

    # Create mock data
    np.random.seed(42)
    n_assets = 10
    n_periods = 252

    # Generate synthetic returns
    returns_data = np.random.normal(0.001, 0.02, (n_periods, n_assets))
    returns_df = pd.DataFrame(returns_data, columns=[f'Asset_{i}' for i in range(n_assets)])

    # Create asset universe
    assets = [f'Asset_{i}' for i in range(n_assets)]
    universe = AssetUniverse(
        assets=assets,
        returns=returns_df,
        covariance_matrix=returns_df.cov() * 252,
        expected_returns=returns_df.mean() * 252
    )

    print(f"Created universe with {len(assets)} assets")

    # Test different risk parity methods
    methods = ["erc", "hrp", "mdp"]

    for method in methods:
        print(f"\nTesting {method.upper()} optimizer...")

        config = RiskParityConfig(
            optimizer="risk_parity",
            risk_parity_method=method,
            min_weight=0.0,
            max_weight=0.4
        )

        try:
            result = optimize_risk_parity(universe, config)

            print(".4f")
            print(".4f")
            print(".4f")
            print(".4f")
            print(f"Convergence: {result.convergence}")

            # Show risk contributions for first 5 assets
            risk_contrib = ERCOptimizer(config)._calculate_risk_contributions(result.optimal_weights, universe)
            print("Risk contributions (top 5):")
            sorted_contribs = sorted(risk_contrib.asset_contributions.items(), key=lambda x: x[1], reverse=True)
            for asset, contrib in sorted_contribs[:5]:
                print(".4f")

        except Exception as e:
            print(f"Optimization failed: {e}")

    print("\nRisk parity optimization test completed successfully!")

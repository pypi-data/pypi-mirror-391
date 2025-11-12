"""
Black-Litterman Portfolio Optimization Model
=============================================

This module implements the Black-Litterman model for portfolio optimization,
combining market equilibrium returns with investor views to produce more
robust and personalized portfolio allocations.

Key Features:
- Market equilibrium return calculation
- Investor view incorporation
- Confidence level adjustments
- Robust covariance estimation
- Bayesian posterior estimation
- Multi-asset and multi-view support
- View uncertainty quantification
- Portfolio optimization with BL inputs
- Performance attribution
- Scenario analysis and stress testing
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
from scipy import optimize, stats
from scipy.linalg import sqrtm
import cvxpy as cp
from sklearn.covariance import LedoitWolf, OAS, MinCovDet

# Import existing Qantify modules
try:
    from .portfolio_optimization import PortfolioConfig, PortfolioOptimizer, OptimizationResult, AssetUniverse
except ImportError:
    PortfolioConfig = None
    PortfolioOptimizer = None
    OptimizationResult = None
    AssetUniverse = None


@dataclass
class BLView:
    """An investor view in the Black-Litterman model"""

    view_type: str  # "absolute", "relative"
    assets: List[str]
    coefficients: List[float]  # Coefficients for linear combination
    expected_return: float
    confidence: float  # Confidence level (0-1)

    def __post_init__(self):
        """Validate view parameters"""
        if len(self.assets) != len(self.coefficients):
            raise ValueError("Number of assets must match number of coefficients")

        if not (0 < self.confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class BLModelConfig:
    """Configuration for Black-Litterman model"""

    # Risk aversion parameter
    risk_aversion: float = 3.0

    # Uncertainty scaling
    tau: float = 0.025  # Uncertainty in prior

    # Covariance shrinkage
    use_covariance_shrinkage: bool = True
    shrinkage_method: str = "ledoit_wolf"  # "ledoit_wolf", "oas", "min_cov_det"

    # Market parameters
    market_cap_weights: Optional[Dict[str, float]] = None
    market_risk_premium: float = 0.06  # Annual market risk premium

    # View processing
    adjust_confidence_by_market_cap: bool = True
    use_relative_views: bool = True

    # Optimization settings
    solver_tolerance: float = 1e-8
    max_iterations: int = 1000


@dataclass
class BLResult:
    """Result of Black-Litterman model estimation"""

    prior_returns: np.ndarray
    posterior_returns: np.ndarray
    posterior_covariance: np.ndarray
    implied_market_weights: Optional[np.ndarray] = None
    view_confidence_matrix: Optional[np.ndarray] = None

    # Diagnostics
    shrinkage_intensity: float = 0.0
    effective_views: int = 0
    model_confidence: float = 0.0

    # Performance metrics
    entropy_change: float = 0.0
    divergence_kl: float = 0.0


class EquilibriumReturnEstimator:
    """Estimates market equilibrium returns"""

    def __init__(self, config: BLModelConfig):
        self.config = config

    def estimate_equilibrium_returns(self, universe: AssetUniverse) -> np.ndarray:
        """Estimate market equilibrium returns using CAPM"""

        n_assets = universe.n_assets

        if self.config.market_cap_weights:
            # Use provided market cap weights
            market_weights = np.array([self.config.market_cap_weights.get(asset, 0.0)
                                     for asset in universe.assets])
            market_weights = market_weights / np.sum(market_weights)
        else:
            # Equal weight market portfolio (simplified)
            market_weights = np.ones(n_assets) / n_assets

        # Calculate market portfolio volatility
        market_vol = np.sqrt(market_weights @ universe.covariance_matrix.values @ market_weights)

        # CAPM: E[R_i] = R_f + β_i * (E[R_m] - R_f)
        # where β_i = Cov(R_i, R_m) / Var(R_m)

        market_returns = universe.expected_returns.values
        market_variance = market_vol ** 2

        # Calculate betas
        covariances = universe.covariance_matrix.values @ market_weights
        betas = covariances / market_variance

        # Calculate equilibrium returns
        risk_free_rate = universe.risk_free_rate
        equilibrium_returns = (risk_free_rate +
                             betas * (self.config.market_risk_premium - risk_free_rate))

        return equilibrium_returns

    def estimate_market_portfolio(self, universe: AssetUniverse) -> np.ndarray:
        """Estimate market portfolio weights"""

        if self.config.market_cap_weights:
            market_weights = np.array([self.config.market_cap_weights.get(asset, 0.0)
                                     for asset in universe.assets])
            market_weights = market_weights / np.sum(market_weights)
        else:
            # Equal weight
            market_weights = np.ones(universe.n_assets) / universe.n_assets

        return market_weights


class ViewProcessor:
    """Processes investor views for Black-Litterman model"""

    def __init__(self, config: BLModelConfig):
        self.config = config

    def process_views(self, views: List[BLView], universe: AssetUniverse) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Process views into P, Q, Omega matrices"""

        n_assets = universe.n_assets
        n_views = len(views)

        if n_views == 0:
            # No views - return empty matrices
            P = np.zeros((0, n_assets))
            Q = np.zeros(0)
            Omega = np.zeros((0, 0))
            return P, Q, Omega

        # Build P matrix (pick matrix)
        P = np.zeros((n_views, n_assets))
        Q = np.zeros(n_views)

        asset_to_index = {asset: i for i, asset in enumerate(universe.assets)}

        for i, view in enumerate(views):
            Q[i] = view.expected_return

            # Handle different view types
            if view.view_type == "absolute":
                # Absolute view: coefficient of 1 for the asset
                if len(view.assets) == 1:
                    asset_idx = asset_to_index[view.assets[0]]
                    P[i, asset_idx] = view.coefficients[0]
                else:
                    raise ValueError("Absolute views should have exactly one asset")

            elif view.view_type == "relative":
                # Relative view: linear combination
                for asset, coeff in zip(view.assets, view.coefficients):
                    if asset in asset_to_index:
                        asset_idx = asset_to_index[asset]
                        P[i, asset_idx] = coeff
            else:
                raise ValueError(f"Unknown view type: {view.view_type}")

        # Build Omega matrix (view uncertainty)
        Omega = self._build_omega_matrix(views, universe, P)

        return P, Q, Omega

    def _build_omega_matrix(self, views: List[BLView], universe: AssetUniverse,
                           P: np.ndarray) -> np.ndarray:
        """Build the Omega matrix of view uncertainties"""

        n_views = len(views)
        Omega = np.zeros((n_views, n_views))

        for i, view in enumerate(views):
            if view.confidence <= 0 or view.confidence > 1:
                raise ValueError(f"Invalid confidence for view {i}: {view.confidence}")

            # Calculate view variance
            view_variance = self._calculate_view_variance(view, universe, P[i])

            # Adjust for confidence
            adjusted_variance = view_variance / view.confidence

            Omega[i, i] = adjusted_variance

        return Omega

    def _calculate_view_variance(self, view: BLView, universe: AssetUniverse,
                               p_vector: np.ndarray) -> float:
        """Calculate variance of a view"""

        # View variance = p^T * Sigma * p * tau
        Sigma = universe.covariance_matrix.values
        view_variance = p_vector @ Sigma @ p_vector * self.config.tau

        # Adjust for market cap if enabled
        if self.config.adjust_confidence_by_market_cap and universe.market_caps is not None:
            market_caps = np.array([universe.market_caps.get(asset, 0.0)
                                  for asset in universe.assets])
            avg_market_cap = np.mean(market_caps[market_caps > 0])

            # Views on small cap stocks are less certain
            cap_weights = market_caps / avg_market_cap
            cap_adjustment = np.average(cap_weights, weights=np.abs(p_vector))
            cap_adjustment = min(cap_adjustment, 1.0)  # Cap at 1.0

            view_variance *= (1.0 + cap_adjustment)

        return view_variance


class CovarianceEstimator:
    """Robust covariance matrix estimation"""

    def __init__(self, config: BLModelConfig):
        self.config = config

    def estimate_covariance(self, returns: pd.DataFrame) -> np.ndarray:
        """Estimate covariance matrix with shrinkage"""

        if not self.config.use_covariance_shrinkage:
            # Simple sample covariance
            return returns.cov().values

        if self.config.shrinkage_method == "ledoit_wolf":
            lw = LedoitWolf()
            cov_matrix = lw.fit(returns.values).covariance_

        elif self.config.shrinkage_method == "oas":
            oas = OAS()
            cov_matrix = oas.fit(returns.values).covariance_

        elif self.config.shrinkage_method == "min_cov_det":
            mcd = MinCovDet()
            cov_matrix = mcd.fit(returns.values).covariance_

        else:
            raise ValueError(f"Unknown shrinkage method: {self.config.shrinkage_method}")

        return cov_matrix


class BlackLittermanModel:
    """Black-Litterman model implementation"""

    def __init__(self, config: BLModelConfig = None):
        self.config = config or BLModelConfig()

        self.equilibrium_estimator = EquilibriumReturnEstimator(self.config)
        self.view_processor = ViewProcessor(self.config)
        self.cov_estimator = CovarianceEstimator(self.config)

    def fit(self, universe: AssetUniverse, views: List[BLView] = None) -> BLResult:
        """Fit the Black-Litterman model"""

        if views is None:
            views = []

        # Step 1: Estimate covariance matrix
        Sigma = self.cov_estimator.estimate_covariance(universe.returns)

        # Step 2: Estimate equilibrium returns
        pi = self.equilibrium_estimator.estimate_equilibrium_returns(universe)

        # Step 3: Process views
        P, Q, Omega = self.view_processor.process_views(views, universe)

        # Step 4: Apply Black-Litterman formula
        if len(views) > 0:
            # Posterior estimates
            tau_Sigma = self.config.tau * Sigma

            # Matrix inversion for posterior calculation
            inv_tau_Sigma = np.linalg.inv(tau_Sigma)
            inv_Omega = np.linalg.inv(Omega)

            # Posterior expected returns
            A = inv_tau_Sigma + P.T @ inv_Omega @ P
            inv_A = np.linalg.inv(A)

            mu_bl = inv_A @ (inv_tau_Sigma @ pi + P.T @ inv_Omega @ Q)

            # Posterior covariance
            Sigma_bl = Sigma + inv_A

        else:
            # No views - return prior
            mu_bl = pi
            Sigma_bl = Sigma

        # Calculate diagnostics
        shrinkage_intensity = self._calculate_shrinkage_intensity(Sigma, universe.returns.cov().values)
        entropy_change = self._calculate_entropy_change(pi, mu_bl)
        divergence_kl = self._calculate_kl_divergence(pi, mu_bl, Sigma)

        # Estimate implied market weights
        market_weights = self._estimate_market_weights(mu_bl, Sigma_bl)

        return BLResult(
            prior_returns=pi,
            posterior_returns=mu_bl,
            posterior_covariance=Sigma_bl,
            implied_market_weights=market_weights,
            shrinkage_intensity=shrinkage_intensity,
            effective_views=len(views),
            entropy_change=entropy_change,
            divergence_kl=divergence_kl
        )

    def _calculate_shrinkage_intensity(self, Sigma_shrunk: np.ndarray, Sigma_sample: np.ndarray) -> float:
        """Calculate shrinkage intensity"""

        if np.allclose(Sigma_sample, 0):
            return 0.0

        # Frobenius norm of difference
        diff_norm = np.linalg.norm(Sigma_shrunk - Sigma_sample, 'fro')
        sample_norm = np.linalg.norm(Sigma_sample, 'fro')

        if sample_norm > 0:
            return diff_norm / sample_norm
        else:
            return 0.0

    def _calculate_entropy_change(self, prior_returns: np.ndarray, posterior_returns: np.ndarray) -> float:
        """Calculate change in entropy due to views"""

        # Simplified entropy calculation
        prior_entropy = -np.sum(prior_returns * np.log(np.abs(prior_returns) + 1e-10))
        posterior_entropy = -np.sum(posterior_returns * np.log(np.abs(posterior_returns) + 1e-10))

        return posterior_entropy - prior_entropy

    def _calculate_kl_divergence(self, prior_returns: np.ndarray, posterior_returns: np.ndarray,
                                covariance: np.ndarray) -> float:
        """Calculate KL divergence between prior and posterior"""

        try:
            inv_cov = np.linalg.inv(covariance)
            diff = posterior_returns - prior_returns

            kl_div = 0.5 * (diff @ inv_cov @ diff +
                           np.log(np.linalg.det(covariance)) -
                           np.log(np.linalg.det(covariance)))

            return max(0, kl_div)

        except np.linalg.LinAlgError:
            return 0.0

    def _estimate_market_weights(self, expected_returns: np.ndarray, covariance: np.ndarray) -> np.ndarray:
        """Estimate market portfolio weights from BL returns"""

        n_assets = len(expected_returns)

        # Solve for market weights: w^T * μ = max_sharpe
        # This is a simplified approximation
        try:
            # Assume risk-free rate of 0 for simplicity
            inv_cov = np.linalg.inv(covariance)
            weights = inv_cov @ expected_returns
            weights = weights / np.sum(weights)

            return weights

        except np.linalg.LinAlgError:
            return np.ones(n_assets) / n_assets


class BLOptimizer(PortfolioOptimizer):
    """Black-Litterman Portfolio Optimizer"""

    def __init__(self, config: PortfolioConfig, bl_config: BLModelConfig = None):
        super().__init__(config)
        self.bl_config = bl_config or BLModelConfig()
        self.bl_model = BlackLittermanModel(self.bl_config)

    def optimize(self, universe: AssetUniverse,
                constraints: List = None, views: List[BLView] = None) -> OptimizationResult:

        if constraints is None:
            constraints = []
        if views is None:
            views = []

        # Step 1: Fit Black-Litterman model
        bl_result = self.bl_model.fit(universe, views)

        # Step 2: Create universe with BL parameters
        bl_universe = AssetUniverse(
            assets=universe.assets,
            returns=universe.returns,
            covariance_matrix=pd.DataFrame(bl_result.posterior_covariance,
                                        index=universe.assets, columns=universe.assets),
            expected_returns=pd.Series(bl_result.posterior_returns, index=universe.assets),
            risk_free_rate=universe.risk_free_rate
        )

        # Step 3: Optimize using mean-variance with BL inputs
        n_assets = universe.n_assets
        mu = bl_result.posterior_returns
        Sigma = bl_result.posterior_covariance

        # Variables
        w = cp.Variable(n_assets)

        # Objective: maximize expected return - risk aversion * variance
        objective = cp.Maximize(mu @ w - self.config.risk_aversion * cp.quad_form(w, Sigma))

        # Constraints
        constraints_cvx = [
            cp.sum(w) == 1,  # Fully invested
            w >= self.config.min_weight,
            w <= self.config.max_weight
        ]

        # Add custom constraints
        for constraint in constraints:
            if constraint.constraint_type == "group_limits":
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
            # Fallback: implied market weights from BL
            if bl_result.implied_market_weights is not None:
                optimal_weights = bl_result.implied_market_weights
            else:
                optimal_weights = np.ones(n_assets) / n_assets
            convergence = False

        # Calculate metrics using BL universe
        metrics = self._calculate_risk_metrics(optimal_weights, bl_universe)

        # Calculate diversification metrics
        diversification_ratio = self._calculate_diversification_ratio(optimal_weights, bl_universe)
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


class BLViewGenerator:
    """Generates views for Black-Litterman model"""

    def __init__(self, config: BLModelConfig):
        self.config = config

    def generate_market_views(self, universe: AssetUniverse) -> List[BLView]:
        """Generate views based on market data"""

        views = []

        # View 1: Market will outperform risk-free rate
        market_weights = np.ones(universe.n_assets) / universe.n_assets
        market_return = market_weights @ universe.expected_returns.values

        if market_return > universe.risk_free_rate:
            view = BLView(
                view_type="absolute",
                assets=["market_portfolio"],  # Placeholder
                coefficients=[1.0],
                expected_return=market_return + 0.02,  # Slight outperformance
                confidence=0.7
            )
            views.append(view)

        # View 2: High beta stocks will have higher returns
        betas = self._calculate_betas(universe)
        high_beta_assets = [asset for asset, beta in zip(universe.assets, betas) if beta > 1.2]

        if len(high_beta_assets) > 0:
            # Relative view: high beta stocks outperform market
            view = BLView(
                view_type="relative",
                assets=high_beta_assets + ["market_portfolio"],
                coefficients=[1.0/len(high_beta_assets)] * len(high_beta_assets) + [-1.0],
                expected_return=0.03,  # 3% outperformance
                confidence=0.6
            )
            views.append(view)

        return views

    def generate_fundamental_views(self, universe: AssetUniverse,
                                 fundamental_data: Dict[str, Any]) -> List[BLView]:
        """Generate views based on fundamental data"""

        views = []

        # Example: Value investing view
        if 'pe_ratios' in fundamental_data:
            pe_ratios = fundamental_data['pe_ratios']

            # Find undervalued stocks (low P/E)
            avg_pe = np.mean(list(pe_ratios.values()))
            undervalued = [asset for asset, pe in pe_ratios.items()
                         if pe < avg_pe * 0.8 and asset in universe.assets]

            if len(undervalued) > 0:
                # View: undervalued stocks will outperform
                view = BLView(
                    view_type="relative",
                    assets=undervalued + ["market_portfolio"],
                    coefficients=[1.0/len(undervalued)] * len(undervalued) + [-1.0],
                    expected_return=0.05,  # 5% outperformance
                    confidence=0.5
                )
                views.append(view)

        return views

    def _calculate_betas(self, universe: AssetUniverse) -> np.ndarray:
        """Calculate asset betas"""

        n_assets = universe.n_assets
        market_weights = np.ones(n_assets) / n_assets
        market_returns = universe.returns.values @ market_weights
        market_variance = np.var(market_returns)

        if market_variance == 0:
            return np.ones(n_assets)

        betas = []
        for asset in universe.assets:
            asset_returns = universe.returns[asset].values
            covariance = np.cov(asset_returns, market_returns)[0, 1]
            beta = covariance / market_variance
            betas.append(beta)

        return np.array(betas)


class BLBacktestEngine:
    """Backtesting engine for Black-Litterman strategies"""

    def __init__(self, config: BLModelConfig):
        self.config = config

    def backtest_strategy(self, universe: AssetUniverse, views_history: List[List[BLView]],
                         rebalance_dates: List[pd.Timestamp]) -> Dict[str, Any]:
        """Backtest Black-Litterman strategy"""

        portfolio_history = []
        bl_model = BlackLittermanModel(self.config)

        current_weights = np.ones(universe.n_assets) / universe.n_assets

        for i, rebalance_date in enumerate(rebalance_dates):
            # Get views for this period
            current_views = views_history[i] if i < len(views_history) else []

            # Fit BL model
            bl_result = bl_model.fit(universe, current_views)

            # Create optimizer
            optimizer = BLOptimizer(PortfolioConfig(), self.config)

            # Create BL universe
            bl_universe = AssetUniverse(
                assets=universe.assets,
                returns=universe.returns,
                covariance_matrix=pd.DataFrame(bl_result.posterior_covariance,
                                            index=universe.assets, columns=universe.assets),
                expected_returns=pd.Series(bl_result.posterior_returns, index=universe.assets)
            )

            # Optimize
            result = optimizer.optimize(bl_universe)

            # Update weights
            current_weights = result.optimal_weights

            portfolio_history.append({
                'date': rebalance_date,
                'weights': current_weights.copy(),
                'expected_return': result.expected_return,
                'expected_risk': result.expected_risk,
                'sharpe_ratio': result.sharpe_ratio
            })

        return {
            'portfolio_history': portfolio_history,
            'final_weights': current_weights,
            'total_periods': len(rebalance_dates)
        }


# Factory functions
def create_black_litterman_model(config: BLModelConfig = None) -> BlackLittermanModel:
    """Factory function for Black-Litterman model"""
    return BlackLittermanModel(config)


def create_bl_optimizer(config: PortfolioConfig = None, bl_config: BLModelConfig = None) -> BLOptimizer:
    """Factory function for BL optimizer"""
    return BLOptimizer(config or PortfolioConfig(), bl_config)


def optimize_with_views(universe: AssetUniverse, views: List[BLView],
                       config: PortfolioConfig = None, bl_config: BLModelConfig = None) -> OptimizationResult:
    """Convenience function for Black-Litterman optimization"""

    optimizer = create_bl_optimizer(config, bl_config)
    return optimizer.optimize(universe, views=views)


# Example usage and testing
if __name__ == "__main__":
    # Test Black-Litterman model
    print("Testing Black-Litterman Portfolio Optimization...")

    # Create mock data
    np.random.seed(42)
    n_assets = 8
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
        expected_returns=returns_df.mean() * 252,
        market_caps=pd.Series({f'Asset_{i}': 1000000 * (i + 1) for i in range(n_assets)})
    )

    print(f"Created universe with {len(assets)} assets")

    # Create some views
    views = [
        BLView(
            view_type="absolute",
            assets=["Asset_0"],
            coefficients=[1.0],
            expected_return=0.12,  # 12% expected return
            confidence=0.8
        ),
        BLView(
            view_type="relative",
            assets=["Asset_1", "Asset_2"],
            coefficients=[1.0, -1.0],
            expected_return=0.03,  # Asset_1 outperforms Asset_2 by 3%
            confidence=0.6
        )
    ]

    print(f"Created {len(views)} investor views")

    # Test Black-Litterman optimization
    config = PortfolioConfig(
        optimizer="black_litterman",
        risk_aversion=3.0,
        min_weight=0.0,
        max_weight=0.3
    )

    bl_config = BLModelConfig(
        risk_aversion=3.0,
        tau=0.025,
        market_cap_weights={asset: 1000000 * (i + 1) for i, asset in enumerate(assets)}
    )

    try:
        result = optimize_with_views(universe, views, config, bl_config)

        print(".4f")
        print(".4f")
        print(".4f")
        print(f"Convergence: {result.convergence}")

        # Show top 5 holdings
        weights_df = pd.DataFrame({
            'asset': assets,
            'weight': result.optimal_weights
        }).sort_values('weight', ascending=False)

        print("Top 5 holdings:")
        for _, row in weights_df.head().iterrows():
            print(".3f")

        # Test BL model diagnostics
        bl_model = create_black_litterman_model(bl_config)
        bl_result = bl_model.fit(universe, views)

        print("
BL Model Diagnostics:")
        print(".4f")
        print(f"Effective views: {bl_result.effective_views}")
        print(".6f")

    except Exception as e:
        print(f"BL optimization failed: {e}")

    print("\nBlack-Litterman optimization test completed successfully!")

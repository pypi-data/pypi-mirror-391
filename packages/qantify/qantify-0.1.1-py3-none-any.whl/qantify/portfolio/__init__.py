"""
Portfolio Optimization Module for Qantify
==========================================

This module provides comprehensive portfolio optimization capabilities for
quantitative trading and investment management. Includes traditional and
modern optimization techniques with advanced risk management.

Modules:
- portfolio_optimization: Core optimization engine with multiple algorithms
- risk_parity: Advanced risk parity strategies (ERC, HRP, MDP, Factor RP)
- black_litterman: Black-Litterman model with investor views integration

Key Features:
- Mean-Variance Optimization (Markowitz)
- Risk Parity and Equal Risk Contribution
- Hierarchical Risk Parity (HRP)
- Maximum Diversification Portfolios
- Black-Litterman Model with views
- Factor-based Portfolio Construction
- Transaction cost modeling
- Portfolio rebalancing strategies
- Risk budgeting and attribution
- Performance analytics
- ESG and sustainability integration
- Dynamic portfolio optimization
"""

from .portfolio_optimization import (
    PortfolioConfig,
    OptimizationResult,
    PortfolioConstraint,
    AssetUniverse,
    PortfolioOptimizer,
    MeanVarianceOptimizer,
    BlackLittermanOptimizer,
    PortfolioRebalancer,
    PortfolioAnalytics,
    create_portfolio_optimizer,
    create_asset_universe,
    optimize_portfolio
)

from .risk_parity import (
    RiskParityConfig,
    RiskContribution,
    ERCOptimizer,
    HRPOptimizer,
    MDPOptimizer,
    FactorRiskParityOptimizer,
    RiskBudgetingEngine,
    create_risk_parity_optimizer,
    optimize_risk_parity
)

from .black_litterman import (
    BLView,
    BLModelConfig,
    BLResult,
    EquilibriumReturnEstimator,
    ViewProcessor,
    CovarianceEstimator,
    BlackLittermanModel,
    BLOptimizer,
    BLViewGenerator,
    BLBacktestEngine,
    create_black_litterman_model,
    create_bl_optimizer,
    optimize_with_views
)

__all__ = [
    # Core Portfolio Optimization
    'PortfolioConfig',
    'OptimizationResult',
    'PortfolioConstraint',
    'AssetUniverse',
    'PortfolioOptimizer',
    'MeanVarianceOptimizer',
    'BlackLittermanOptimizer',
    'PortfolioRebalancer',
    'PortfolioAnalytics',
    'create_portfolio_optimizer',
    'create_asset_universe',
    'optimize_portfolio',

    # Risk Parity
    'RiskParityConfig',
    'RiskContribution',
    'ERCOptimizer',
    'HRPOptimizer',
    'MDPOptimizer',
    'FactorRiskParityOptimizer',
    'RiskBudgetingEngine',
    'create_risk_parity_optimizer',
    'optimize_risk_parity',

    # Black-Litterman
    'BLView',
    'BLModelConfig',
    'BLResult',
    'EquilibriumReturnEstimator',
    'ViewProcessor',
    'CovarianceEstimator',
    'BlackLittermanModel',
    'BLOptimizer',
    'BLViewGenerator',
    'BLBacktestEngine',
    'create_black_litterman_model',
    'create_bl_optimizer',
    'optimize_with_views'
]

__version__ = "1.0.0"
__author__ = "Qantify Team"
__description__ = "Advanced portfolio optimization for quantitative trading"

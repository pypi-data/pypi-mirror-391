"""Backtesting engines and portfolio simulators."""

# Core backtest components
from .event import EventBacktester, EventBacktestResult
from .vectorized import (
    VectorizedBacktestResult,
    run as run_vectorized,
    PositionSizer,
    FixedPositionSizer,
    PercentagePositionSizer,
    KellyPositionSizer,
    VolatilityAdjustedSizer,
    MLPositionSizer,
    MultiTimeframeEngine,
)

# Risk management
from .risk import (
    DailyLossRule,
    LeverageLimitRule,
    MaxDrawdownRule,
    MaxPositionRule,
    NetExposureLimitRule,
    RiskEvent,
    RiskManager,
    RiskRule,
    ValueAtRiskRule,
    ExpectedShortfallRule,
    CorrelationRiskRule,
    LiquidityRiskRule,
    MLVolatilityRule,
    KellyCriterionRule,
    PortfolioOptimizer,
)

# Scenarios and stress testing
from .scenarios import (
    GapScenario,
    StressScenario,
    run_scenarios,
    MarketRegime,
    RegimeBasedScenario,
    MultiAssetStressScenario,
    CircuitBreakerScenario,
    LiquidityCrunchScenario,
    BlackSwanScenario,
    RegimeDetectionEngine,
    ScenarioGenerator,
    run_multi_asset_scenarios,
    create_extreme_scenarios,
    create_correlation_break_scenarios,
    benchmark_scenario_performance,
)

# Compliance
from .compliance import (
    ComplianceCheck,
    ComplianceEngine,
    ComplianceEvent,
    RealTimeConstraintCheck,
    ShortLocateCheck,
    WashTradeCheck,
    RegulationType,
    PatternDetectionCheck,
    ConcentrationLimitCheck,
    MarketImpactCheck,
    InsiderTradingPatternCheck,
    RegulatoryReportingEngine,
)

# Batch processing and optimization
from .batch import (
    run_parallel_event_backtests,
    run_hyperparameter_optimization,
    run_walk_forward_optimization,
    BatchBacktestResult,
    OptimizationObjective,
    SharpeRatioObjective,
    MaxDrawdownObjective,
    CalmarRatioObjective,
    ProfitFactorObjective,
    HyperparameterOptimizer,
    GridSearchOptimizer,
    BayesianOptimizer,
    HyperparameterOptimizationResult,
    DistributedBacktestManager,
)

# Core infrastructure
from .costs import CommissionModel, NoCommission, NoSlippage, PercentageCommission, SlippageModel
from .reporting import equity_statistics, fills_to_frame, orders_to_frame, trades_to_frame
from .portfolio import Portfolio, PortfolioState

__all__ = [
    # Vectorized backtesting
    "run_vectorized",
    "VectorizedBacktestResult",
    "PositionSizer",
    "FixedPositionSizer",
    "PercentagePositionSizer",
    "KellyPositionSizer",
    "VolatilityAdjustedSizer",
    "MLPositionSizer",
    "MultiTimeframeEngine",

    # Event backtesting
    "EventBacktester",
    "EventBacktestResult",

    # Risk management
    "RiskManager",
    "RiskRule",
    "RiskEvent",
    "MaxDrawdownRule",
    "MaxPositionRule",
    "DailyLossRule",
    "NetExposureLimitRule",
    "LeverageLimitRule",
    "ValueAtRiskRule",
    "ExpectedShortfallRule",
    "CorrelationRiskRule",
    "LiquidityRiskRule",
    "MLVolatilityRule",
    "KellyCriterionRule",
    "PortfolioOptimizer",

    # Scenarios
    "StressScenario",
    "GapScenario",
    "run_scenarios",
    "MarketRegime",
    "RegimeBasedScenario",
    "MultiAssetStressScenario",
    "CircuitBreakerScenario",
    "LiquidityCrunchScenario",
    "BlackSwanScenario",
    "RegimeDetectionEngine",
    "ScenarioGenerator",
    "run_multi_asset_scenarios",
    "create_extreme_scenarios",
    "create_correlation_break_scenarios",
    "benchmark_scenario_performance",

    # Compliance
    "ComplianceEngine",
    "ComplianceCheck",
    "ComplianceEvent",
    "WashTradeCheck",
    "ShortLocateCheck",
    "RealTimeConstraintCheck",
    "RegulationType",
    "PatternDetectionCheck",
    "ConcentrationLimitCheck",
    "MarketImpactCheck",
    "InsiderTradingPatternCheck",
    "RegulatoryReportingEngine",

    # Batch processing
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

    # Core infrastructure
    "CommissionModel",
    "SlippageModel",
    "NoCommission",
    "NoSlippage",
    "PercentageCommission",
    "orders_to_frame",
    "fills_to_frame",
    "trades_to_frame",
    "equity_statistics",
    
    # Portfolio
    "Portfolio",
    "PortfolioState",
]

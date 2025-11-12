"""
Market Microstructure Module
============================

Advanced market microstructure analysis including order book dynamics,
high-frequency trading strategies, latency analysis, and liquidity modeling.

This module provides comprehensive tools for:
- Order book analysis and modeling
- High-frequency trading strategies
- Latency arbitrage and optimization
- Market impact estimation
- Liquidity risk assessment
- Optimal execution algorithms
"""

from .order_book_analytics import (
    OrderBookSnapshot,
    OrderFlowEvent,
    LOBModelConfig,
    LimitOrderBook,
    LOBDynamicsModel,
    OrderBookAnalyzer,
    create_limit_order_book,
    create_lob_dynamics_model,
    create_order_book_analyzer
)

from .hft_modeling import (
    LatencyMetrics,
    HFTStrategyConfig,
    ExecutionSignal,
    LatencyArbitrageStrategy,
    OrderFlowPredictionModel,
    QueuePositionOptimizer,
    MomentumIgnitionStrategy,
    FlashCrashDetector,
    StatisticalMicroArbitrage,
    HFTRiskManager,
    create_latency_arbitrage_strategy,
    create_order_flow_prediction_model,
    create_queue_position_optimizer,
    create_flash_crash_detector,
    create_hft_risk_manager
)

from .market_impact import (
    MarketImpactModelConfig,
    TransactionCosts,
    ExecutionTrajectory,
    KyleLambdaModel,
    AlmgrenChrissModel,
    SquareRootMarketImpact,
    AdaptiveMarketImpactModel,
    OptimalExecutionEngine,
    TransactionCostAnalyzer,
    create_market_impact_model,
    create_optimal_execution_engine,
    create_transaction_cost_analyzer
)

from .liquidity_modeling import (
    LiquidityMetrics,
    LiquidityModelConfig,
    LiquidityStressTestResult,
    LiquidityRiskModel,
    MarketMakerLiquidityModel,
    LiquidityContagionModel,
    create_liquidity_risk_model,
    create_market_maker_model,
    create_liquidity_contagion_model
)

__all__ = [
    # Order Book Analytics
    'OrderBookSnapshot',
    'OrderFlowEvent',
    'LOBModelConfig',
    'LimitOrderBook',
    'LOBDynamicsModel',
    'OrderBookAnalyzer',
    'create_limit_order_book',
    'create_lob_dynamics_model',
    'create_order_book_analyzer',

    # HFT Modeling
    'LatencyMetrics',
    'HFTStrategyConfig',
    'ExecutionSignal',
    'LatencyArbitrageStrategy',
    'OrderFlowPredictionModel',
    'QueuePositionOptimizer',
    'MomentumIgnitionStrategy',
    'FlashCrashDetector',
    'StatisticalMicroArbitrage',
    'HFTRiskManager',
    'create_latency_arbitrage_strategy',
    'create_order_flow_prediction_model',
    'create_queue_position_optimizer',
    'create_flash_crash_detector',
    'create_hft_risk_manager',

    # Market Impact
    'MarketImpactModelConfig',
    'TransactionCosts',
    'ExecutionTrajectory',
    'KyleLambdaModel',
    'AlmgrenChrissModel',
    'SquareRootMarketImpact',
    'AdaptiveMarketImpactModel',
    'OptimalExecutionEngine',
    'TransactionCostAnalyzer',
    'create_market_impact_model',
    'create_optimal_execution_engine',
    'create_transaction_cost_analyzer',

    # Liquidity Modeling
    'LiquidityMetrics',
    'LiquidityModelConfig',
    'LiquidityStressTestResult',
    'LiquidityRiskModel',
    'MarketMakerLiquidityModel',
    'LiquidityContagionModel',
    'create_liquidity_risk_model',
    'create_market_maker_model',
    'create_liquidity_contagion_model'
]

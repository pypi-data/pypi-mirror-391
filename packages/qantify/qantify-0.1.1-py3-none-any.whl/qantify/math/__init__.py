"""Advanced mathematical models for time series and risk analytics."""

from .timeseries import (
    ARIMAModel, GARCHModel, VARModel,
    AdvancedMathematicalModels, QuantumInformationModels,
    AdvancedStochasticProcesses, InformationGeometryModels,
    ErgodicTheoryModels, NonEuclideanGeometryModels
)
from .stochastic import (
    BrownianMotion,
    GeometricBrownianMotion,
    HestonProcess,
    MonteCarloEngine,
)
from .portfolio import EfficientFrontier, RiskParityOptimizer, BlackLittermanModel, BlackLittermanPosterior, efficient_frontier_path
from .optimization import (
    ScenarioOptimizer,
    BayesianOptimizer,
    QuadraticProgram,
    QuadraticProgramResult,
    solve_qp,
    MeanVarianceOptimizer,
    MeanVarianceResult,
)
from .probability import DistributionToolkit, RiskMeasures
from .filters import KalmanFilter, UnscentedKalmanFilter
from .stat_arb import (
    CointegrationTestResult,
    EngleGrangerTest,
    JohansenTest,
    PairsTradingAnalytics,
    KalmanHedgeRatioEstimator,
    # New advanced statistical arbitrage
    AdvancedCointegrationTests,
    AdvancedErrorCorrectionModels,
    AdvancedArbitrageStrategies,
)
from .options import BlackScholes, BinomialTreePricer, OptionGreeks
from .risk_models import LedoitWolfShrinkage, FactorRiskModel
from .interest import HullWhiteModel, CoxIngersollRossModel
from .regime import MarkovChain, RegimeSwitchingModel
from .volatility import (
    SABRCalibrator, VolatilitySurface,
    # New advanced volatility models
    AdvancedStochasticVolatilityModels, AdvancedGARCHModels,
    StochasticVolatilityModels, VolatilityDerivativesPricing
)
from .control import AlmgrenChrissOptimalExecution, LinearQuadraticRegulator
from .pde import CrankNicolsonPricer
from .credit import HazardRateCurve, SurvivalCurve
from .numerics import (
    ConvergenceError,
    newton_raphson,
    bisection,
    simpson_integral,
    trapezoidal_integral,
    finite_difference_gradient,
)

# New advanced mathematical modules
from . import quantum_finance
from . import stochastic_processes
from . import information_theory
from . import game_theory
from . import chaos_theory
from . import mathematical_physics
from . import complexity_theory

__all__ = [
    # Original exports
    "ARIMAModel", "VARModel", "GARCHModel", "BrownianMotion", "GeometricBrownianMotion",
    "HestonProcess", "MonteCarloEngine", "EfficientFrontier", "RiskParityOptimizer",
    "BlackLittermanModel", "BlackLittermanPosterior", "efficient_frontier_path",
    "ScenarioOptimizer", "BayesianOptimizer", "QuadraticProgram", "QuadraticProgramResult",
    "solve_qp", "MeanVarianceOptimizer", "MeanVarianceResult", "DistributionToolkit",
    "RiskMeasures", "KalmanFilter", "UnscentedKalmanFilter", "EngleGrangerTest",
    "JohansenTest", "CointegrationTestResult", "PairsTradingAnalytics", "KalmanHedgeRatioEstimator",
    "BlackScholes", "BinomialTreePricer", "OptionGreeks", "LedoitWolfShrinkage",
    "FactorRiskModel", "HullWhiteModel", "CoxIngersollRossModel", "MarkovChain",
    "RegimeSwitchingModel", "SABRCalibrator", "VolatilitySurface", "AlmgrenChrissOptimalExecution",
    "LinearQuadraticRegulator", "CrankNicolsonPricer", "HazardRateCurve", "SurvivalCurve",
    "ConvergenceError", "newton_raphson", "bisection", "simpson_integral", "trapezoidal_integral",
    "finite_difference_gradient",

    # New advanced mathematical models
    "AdvancedMathematicalModels", "QuantumInformationModels", "AdvancedStochasticProcesses",
    "InformationGeometryModels", "ErgodicTheoryModels", "NonEuclideanGeometryModels",
    "AdvancedCointegrationTests", "AdvancedErrorCorrectionModels", "AdvancedArbitrageStrategies",
    "AdvancedStochasticVolatilityModels", "AdvancedGARCHModels", "StochasticVolatilityModels",
    "VolatilityDerivativesPricing",

    # New mathematical modules
    "quantum_finance", "stochastic_processes", "information_theory", "game_theory",
    "chaos_theory", "mathematical_physics", "complexity_theory"
]

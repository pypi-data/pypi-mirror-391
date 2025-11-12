"""Advanced machine learning utilities for quantitative finance."""

# Core ML utilities
from .features import (
    FeatureConfig,
    create_features,
    FeatureEngineer,
    StatisticalFeatureEngineer,
    TimeSeriesFeatureEngineer,
    NLPFeatureEngineer,
    ImageFeatureEngineer,
    AudioFeatureEngineer,
    DimensionalityReductionEngineer,
    FeatureInteractionEngineer,
    OutlierDetectionEngineer,
    AutomatedFeatureSelector,
    FeatureScalerEngineer,
    ClusteringFeatureEngineer,
    ComprehensiveFeatureEngineer,
    create_comprehensive_features,
    create_temporal_features,
    create_cross_sectional_features,
    create_interaction_features,
    create_automated_features,
    validate_features,
    optimize_feature_pipeline,
)

from .optimizer import (
    OptimizationResult,
    Optimizer,
    AdvancedOptimizer,
    MultiObjectiveStrategyOptimizer,
    OptimizationAlgorithm,
    BayesianOptimizer,
    OptunaOptimizer,
    ParticleSwarmOptimizer,
    GeneticAlgorithmOptimizer,
    MultiObjectiveOptimizer,
    ConstraintHandler,
    AutoAlgorithmSelector,
)

from .training import (
    Dataset,
    ModelTrainer,
    WalkForwardFold,
    WalkForwardResult,
    compute_future_return,
    prepare_dataset,
    ExperimentTracker,
    TrackerConfig,
    AdvancedCrossValidator,
    PurgedWalkForwardValidator,
    AdvancedEnsembleTrainer,
    NeuralNetworkTrainer,
    AutoEncoderTrainer,
    HyperparameterOptimizer,
    DistributedTrainer,
    ModelValidator,
    AutomatedModelSelector,
)

from .feature_selection import (
    FeatureSelector,
    FeatureSelectionResult,
    EnsembleFeatureSelector,
    MultiObjectiveFeatureSelector,
    AutomatedFeatureSelector,
    FeatureSelectionPipeline,
)

from .automl import (
    AutoMLRunner,
    AutoMLResult,
    ModelConfig,
    PipelineConfig,
    NeuralArchitectureResult,
    StackingResult,
    NeuralArchitectureSearch,
    AutomatedPipelineOptimizer,
    AdvancedModelStacking,
    AutomatedFeaturePreprocessor,
)

from .drift import (
    DriftMonitor,
    DriftDetector,
    DriftMetrics,
    RetrainingSchedule,
    ConceptDriftDetector,
    AlibiDriftDetector,
    PerformanceMetrics,
    ModelPerformanceMonitor,
    AdaptiveRetrainingManager,
    ModelMonitoringDashboard,
)

# New ML modules
from .ensemble import (
    EnsembleConfig,
    EnsembleResult,
    AdvancedEnsembleBuilder,
    AdaptiveEnsembleSelector,
    DynamicEnsemble,
)

from .neural_networks import (
    NeuralNetworkConfig,
    TrainingConfig,
    TrainingResult,
    FlexibleNeuralNetwork,
    AdvancedNeuralTrainer,
    SklearnCompatibleNeuralNetwork,
    AutoEncoder,
    VariationalAutoEncoder,
)

from .anomaly_detection import (
    AnomalyDetectionConfig,
    AnomalyResult,
    AnomalyEvaluationMetrics,
    AdvancedAnomalyDetector,
    StatisticalAnomalyDetector,
    EnsembleAnomalyDetector,
    TimeSeriesAnomalyDetector,
    AutoEncoderAnomalyDetector,
    AnomalyDetectionEvaluator,
)

from .time_series_forecasting import (
    TimeSeriesConfig,
    ForecastingResult,
    TimeSeriesForecaster,
    LSTMForecaster,
    EnsembleTimeSeriesForecaster,
    SklearnCompatibleTimeSeriesForecaster,
    TimeSeriesEvaluator,
)

from .model_interpretation import (
    FeatureImportanceResult,
    ExplanationResult,
    PartialDependenceResult,
    ModelInterpreter,
    ModelRobustnessAnalyzer,
    FairnessAnalyzer,
)

__all__ = [
    # Core ML utilities
    "create_features",
    "FeatureConfig",
    "FeatureEngineer",
    "StatisticalFeatureEngineer",
    "TimeSeriesFeatureEngineer",
    "NLPFeatureEngineer",
    "ImageFeatureEngineer",
    "AudioFeatureEngineer",
    "DimensionalityReductionEngineer",
    "FeatureInteractionEngineer",
    "OutlierDetectionEngineer",
    "AutomatedFeatureSelector",
    "FeatureScalerEngineer",
    "ClusteringFeatureEngineer",
    "ComprehensiveFeatureEngineer",
    "create_comprehensive_features",
    "create_temporal_features",
    "create_cross_sectional_features",
    "create_interaction_features",
    "create_automated_features",
    "validate_features",
    "optimize_feature_pipeline",

    # Optimization
    "Optimizer",
    "OptimizationResult",
    "AdvancedOptimizer",
    "MultiObjectiveStrategyOptimizer",
    "OptimizationAlgorithm",
    "BayesianOptimizer",
    "OptunaOptimizer",
    "ParticleSwarmOptimizer",
    "GeneticAlgorithmOptimizer",
    "MultiObjectiveOptimizer",
    "ConstraintHandler",
    "AutoAlgorithmSelector",

    # Training
    "Dataset",
    "ModelTrainer",
    "WalkForwardResult",
    "WalkForwardFold",
    "compute_future_return",
    "prepare_dataset",
    "ExperimentTracker",
    "TrackerConfig",
    "AdvancedCrossValidator",
    "PurgedWalkForwardValidator",
    "AdvancedEnsembleTrainer",
    "NeuralNetworkTrainer",
    "AutoEncoderTrainer",
    "HyperparameterOptimizer",
    "DistributedTrainer",
    "ModelValidator",
    "AutomatedModelSelector",

    # Feature selection
    "FeatureSelector",
    "FeatureSelectionResult",
    "EnsembleFeatureSelector",
    "MultiObjectiveFeatureSelector",
    "AutomatedFeatureSelector",
    "FeatureSelectionPipeline",

    # AutoML
    "AutoMLRunner",
    "AutoMLResult",
    "ModelConfig",
    "PipelineConfig",
    "NeuralArchitectureResult",
    "StackingResult",
    "NeuralArchitectureSearch",
    "AutomatedPipelineOptimizer",
    "AdvancedModelStacking",
    "AutomatedFeaturePreprocessor",

    # Drift detection
    "DriftMonitor",
    "DriftDetector",
    "DriftMetrics",
    "RetrainingSchedule",
    "ConceptDriftDetector",
    "AlibiDriftDetector",
    "PerformanceMetrics",
    "ModelPerformanceMonitor",
    "AdaptiveRetrainingManager",
    "ModelMonitoringDashboard",

    # Ensemble learning
    "EnsembleConfig",
    "EnsembleResult",
    "AdvancedEnsembleBuilder",
    "AdaptiveEnsembleSelector",
    "DynamicEnsemble",

    # Neural networks
    "NeuralNetworkConfig",
    "TrainingConfig",
    "TrainingResult",
    "FlexibleNeuralNetwork",
    "AdvancedNeuralTrainer",
    "SklearnCompatibleNeuralNetwork",
    "AutoEncoder",
    "VariationalAutoEncoder",

    # Anomaly detection
    "AnomalyDetectionConfig",
    "AnomalyResult",
    "AnomalyEvaluationMetrics",
    "AdvancedAnomalyDetector",
    "StatisticalAnomalyDetector",
    "EnsembleAnomalyDetector",
    "TimeSeriesAnomalyDetector",
    "AutoEncoderAnomalyDetector",
    "AnomalyDetectionEvaluator",

    # Time series forecasting
    "TimeSeriesConfig",
    "ForecastingResult",
    "TimeSeriesForecaster",
    "LSTMForecaster",
    "EnsembleTimeSeriesForecaster",
    "SklearnCompatibleTimeSeriesForecaster",
    "TimeSeriesEvaluator",

    # Model interpretation
    "FeatureImportanceResult",
    "ExplanationResult",
    "PartialDependenceResult",
    "ModelInterpreter",
    "ModelRobustnessAnalyzer",
    "FairnessAnalyzer",
]

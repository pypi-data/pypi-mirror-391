"""Strategy base classes and helper mixins."""

from .base import (
    IndicatorFrame,
    IndicatorSeries,
    Strategy,
    StrategyExecutionMode,
    StrategyPerformanceMetrics,
    MLModelProtocol,
    FeatureEngineer,
    AutoMLTrainer,
    NeuralSignalPredictor,
    DeepLearningTrainer,
    StrategyEnsemble,
    MultiAgentStrategySystem,
    AdaptiveStrategyManager,
    MLStrategy,
)
from .logging import logs_to_dataframe, write_csv, write_jsonl, write_parquet
from .parameters import Parameter, ParameterSpace, collect_parameters, parameter
from .registry import (
    available_strategies,
    get_strategy,
    register_strategy,
    StrategyRegistry,
    StrategyMetadata,
    StrategyEntry,
    StrategyCategory,
    StrategyStatus,
    StrategyRisk,
    DependencyType,
)
from .persistence import (
    RedisStateStore,
    SQLiteStateStore,
    MongoDBStateStore,
    S3StateStore,
    StateSnapshot,
    StateStore,
    SimpleEncryptionKeyProvider,
    StateManagerConfig,
    StrategyStateManager,
    StateVersionControl,
    StateMigrationManager,
    StateReplicationManager,
    StorageBackend,
    CompressionType,
    StateVersion,
)
from .monitor import (
    CompositeMonitor,
    InMemoryMonitor,
    InfluxDBMonitor,
    NullMonitor,
    PrometheusMonitor,
    StrategyMonitor,
    ComprehensiveMonitor,
    EmailNotifier,
    MonitoringDashboard,
)
from .dsl import when, Rule, RuleEngine
from .copilot import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    LocalLLMProvider,
    StrategyBlueprint,
    StrategyGenerator,
    AutoStrategyOptimizer,
    MultiAgentStrategySystem as CopilotMultiAgentSystem,
    StrategyValidator,
    StrategyDeploymentManager,
    AdvancedStrategyCoPilot,
    InteractiveStrategyRefinement,
    StrategyAutoPilot,
    StrategyCoPilot,
)
from .packs import (
    StrategyPack,
    StrategyPackResult,
    StrategyPackMetadata,
    StrategyPackBacktestConfig,
    StrategyPackRegistryError,
    register_pack,
    get_pack,
    available_packs,
)

__all__ = [
    # Base strategy classes
    "Strategy",
    "MLStrategy",
    "IndicatorSeries",
    "IndicatorFrame",
    "StrategyExecutionMode",
    "StrategyPerformanceMetrics",
    "MLModelProtocol",
    "FeatureEngineer",
    "AutoMLTrainer",
    "NeuralSignalPredictor",
    "DeepLearningTrainer",
    "StrategyEnsemble",
    "MultiAgentStrategySystem",
    "AdaptiveStrategyManager",

    # Parameters
    "Parameter",
    "ParameterSpace",
    "parameter",
    "collect_parameters",

    # Registry
    "register_strategy",
    "get_strategy",
    "available_strategies",
    "StrategyRegistry",
    "StrategyMetadata",
    "StrategyEntry",
    "StrategyCategory",
    "StrategyStatus",
    "StrategyRisk",
    "DependencyType",

    # Logging
    "logs_to_dataframe",
    "write_jsonl",
    "write_csv",
    "write_parquet",

    # Persistence
    "StateStore",
    "SQLiteStateStore",
    "RedisStateStore",
    "MongoDBStateStore",
    "S3StateStore",
    "StateSnapshot",
    "SimpleEncryptionKeyProvider",
    "StateManagerConfig",
    "StrategyStateManager",
    "StateVersionControl",
    "StateMigrationManager",
    "StateReplicationManager",
    "StorageBackend",
    "CompressionType",
    "StateVersion",

    # Monitoring
    "StrategyMonitor",
    "NullMonitor",
    "InMemoryMonitor",
    "PrometheusMonitor",
    "InfluxDBMonitor",
    "CompositeMonitor",
    "ComprehensiveMonitor",
    "EmailNotifier",
    "MonitoringDashboard",

    # DSL
    "when",
    "Rule",
    "RuleEngine",

    # Packs
    "StrategyPack",
    "StrategyPackResult",
    "StrategyPackMetadata",
    "StrategyPackBacktestConfig",
    "StrategyPackRegistryError",
    "register_pack",
    "get_pack",
    "available_packs",

    # Copilot
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalLLMProvider",
    "StrategyBlueprint",
    "StrategyGenerator",
    "AutoStrategyOptimizer",
    "CopilotMultiAgentSystem",
    "StrategyValidator",
    "StrategyDeploymentManager",
    "AdvancedStrategyCoPilot",
    "InteractiveStrategyRefinement",
    "StrategyAutoPilot",
    "StrategyCoPilot",
]

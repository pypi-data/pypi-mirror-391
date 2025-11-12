"""
Distributed Computing Module for Qantify
========================================

This module provides comprehensive distributed computing capabilities for
large-scale quantitative trading operations. It includes parallel backtesting,
cloud infrastructure management, distributed execution, and intelligent load balancing.

Modules:
- parallel_backtesting: High-performance distributed backtesting engine
- cloud_infrastructure: Multi-cloud infrastructure management (AWS, GCP, Azure)
- distributed_execution: Multi-machine task orchestration and workflow management
- load_balancer: Intelligent workload distribution and resource optimization

Key Features:
- Multi-core and multi-machine processing
- Cloud-native architecture with auto-scaling
- Fault-tolerant distributed execution
- Intelligent load balancing with ML optimization
- Real-time monitoring and performance analytics
- Geographic load balancing for latency optimization
- High availability and disaster recovery
- Container orchestration support (Kubernetes)
- Serverless computing integration
"""

from .parallel_backtesting import (
    DistributedConfig,
    BacktestTask,
    TaskResult,
    WorkerNode,
    TaskScheduler,
    ParallelBacktestEngine,
    ResultsCollector,
    PerformanceMonitor,
    create_parallel_backtest_engine,
    create_distributed_config,
    run_parallel_backtest
)

from .cloud_infrastructure import (
    CloudConfig,
    InstanceInfo,
    ClusterInfo,
    CloudProvider,
    AWSProvider,
    GCPProvider,
    AzureProvider,
    KubernetesManager,
    CostOptimizer,
    CloudInfrastructureManager,
    create_cloud_infrastructure_manager,
    create_cloud_config
)

from .distributed_execution import (
    ExecutionConfig,
    DistributedTask,
    Workflow,
    WorkerNode as ExecutionWorkerNode,
    DistributedCache,
    TaskScheduler as ExecutionTaskScheduler,
    DistributedExecutor,
    ExecutionMonitor,
    create_linear_workflow,
    create_parallel_workflow,
    create_distributed_executor,
    create_execution_config
)

from .load_balancer import (
    LoadBalancingConfig,
    ResourceMetrics,
    LoadDecision,
    LoadBalancingAlgorithm,
    RoundRobinAlgorithm,
    LeastLoadedAlgorithm,
    WeightedAlgorithm,
    AdaptiveAlgorithm,
    GeographicLoadBalancer,
    IntelligentLoadBalancer,
    create_load_balancer,
    create_load_balancing_config
)

__all__ = [
    # Parallel Backtesting
    'DistributedConfig',
    'BacktestTask',
    'TaskResult',
    'WorkerNode',
    'TaskScheduler',
    'ParallelBacktestEngine',
    'ResultsCollector',
    'PerformanceMonitor',
    'create_parallel_backtest_engine',
    'create_distributed_config',
    'run_parallel_backtest',

    # Cloud Infrastructure
    'CloudConfig',
    'InstanceInfo',
    'ClusterInfo',
    'CloudProvider',
    'AWSProvider',
    'GCPProvider',
    'AzureProvider',
    'KubernetesManager',
    'CostOptimizer',
    'CloudInfrastructureManager',
    'create_cloud_infrastructure_manager',
    'create_cloud_config',

    # Distributed Execution
    'ExecutionConfig',
    'DistributedTask',
    'Workflow',
    'ExecutionWorkerNode',
    'DistributedCache',
    'ExecutionTaskScheduler',
    'DistributedExecutor',
    'ExecutionMonitor',
    'create_linear_workflow',
    'create_parallel_workflow',
    'create_distributed_executor',
    'create_execution_config',

    # Load Balancer
    'LoadBalancingConfig',
    'ResourceMetrics',
    'LoadDecision',
    'LoadBalancingAlgorithm',
    'RoundRobinAlgorithm',
    'LeastLoadedAlgorithm',
    'WeightedAlgorithm',
    'AdaptiveAlgorithm',
    'GeographicLoadBalancer',
    'IntelligentLoadBalancer',
    'create_load_balancer',
    'create_load_balancing_config'
]

__version__ = "1.0.0"
__author__ = "Qantify Team"
__description__ = "Distributed computing capabilities for quantitative trading"

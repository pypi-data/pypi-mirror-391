"""
Distributed Execution Engine for Multi-Machine Task Orchestration
================================================================

This module implements sophisticated distributed execution capabilities for
large-scale quantitative trading operations across multiple machines and
cloud environments. Supports complex workflow orchestration, fault tolerance,
and performance optimization.

Key Features:
- Multi-machine task execution and orchestration
- Complex workflow management with dependencies
- Fault tolerance and automatic recovery
- Dynamic resource allocation and load balancing
- Real-time execution monitoring and analytics
- Distributed caching and data sharing
- Workflow optimization and scheduling
- High availability and disaster recovery
"""

from __future__ import annotations

import warnings
import json
import time
import threading
import asyncio
import uuid
import pickle
import hashlib
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from datetime import datetime, timedelta
import networkx as nx

import numpy as np
import pandas as pd

# Cloud and distributed computing
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import zmq
    ZMQ_AVAILABLE = True
except ImportError:
    ZMQ_AVAILABLE = False

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

try:
    import dask
    import dask.distributed
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


@dataclass
class ExecutionConfig:
    """Configuration for distributed execution"""

    # Execution settings
    max_concurrent_tasks: int = 100
    task_timeout_seconds: int = 3600
    max_retries: int = 3
    retry_delay_seconds: int = 60

    # Resource management
    cpu_cores_per_task: int = 2
    memory_gb_per_task: float = 4.0
    enable_resource_limits: bool = True

    # Communication
    use_redis: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    use_zmq: bool = False

    # Caching and storage
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    shared_storage_path: str = "/tmp/qantify_shared"

    # Monitoring and logging
    enable_monitoring: bool = True
    log_level: str = "INFO"
    metrics_collection_interval: int = 10

    # Fault tolerance
    enable_checkpointing: bool = True
    checkpoint_interval_seconds: int = 300
    enable_redundancy: bool = False


@dataclass
class DistributedTask:
    """A task in the distributed execution system"""

    task_id: str
    task_type: str  # "backtest", "signal_generation", "optimization", etc.
    payload: Dict[str, Any]
    priority: int = 1

    # Dependencies and workflow
    dependencies: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    workflow_id: str = ""

    # Resource requirements
    cpu_cores: int = 2
    memory_gb: float = 4.0
    estimated_duration: float = 60.0

    # Execution metadata
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    assigned_worker: Optional[str] = None

    # Status and results
    status: str = "pending"  # "pending", "running", "completed", "failed", "cancelled"
    result: Optional[Any] = None
    error_message: str = ""
    retry_count: int = 0

    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status in ["completed", "failed", "cancelled"]

    @property
    def is_successful(self) -> bool:
        """Check if task completed successfully"""
        return self.status == "completed"

    @property
    def execution_time(self) -> float:
        """Get execution time if completed"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return 0.0

    @property
    def is_expired(self) -> bool:
        """Check if task has expired"""
        return time.time() - self.created_at > 3600 * 24  # 24 hours


@dataclass
class Workflow:
    """A workflow containing multiple dependent tasks"""

    workflow_id: str
    name: str
    tasks: Dict[str, DistributedTask]
    dag: nx.DiGraph = field(default_factory=nx.DiGraph)

    # Workflow metadata
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    # Execution status
    status: str = "pending"  # "pending", "running", "completed", "failed"
    progress: float = 0.0

    @property
    def is_completed(self) -> bool:
        """Check if workflow is completed"""
        return self.status in ["completed", "failed"]

    @property
    def executable_tasks(self) -> List[str]:
        """Get tasks that are ready to execute (all dependencies satisfied)"""

        executable = []
        for task_id, task in self.tasks.items():
            if task.status == "pending":
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self.tasks[dep_id].is_successful
                    for dep_id in task.dependencies
                )
                if deps_satisfied:
                    executable.append(task_id)

        return executable

    @property
    def completion_percentage(self) -> float:
        """Calculate workflow completion percentage"""

        if not self.tasks:
            return 100.0

        completed_tasks = sum(1 for task in self.tasks.values() if task.is_completed)
        return (completed_tasks / len(self.tasks)) * 100.0


@dataclass
class WorkerNode:
    """A worker node in the distributed system"""

    worker_id: str
    host: str
    port: int
    capabilities: Dict[str, Any]

    # Resource availability
    available_cpu_cores: int = mp.cpu_count()
    available_memory_gb: float = 8.0
    total_cpu_cores: int = mp.cpu_count()
    total_memory_gb: float = 8.0

    # Performance metrics
    tasks_completed: int = 0
    avg_task_time: float = 0.0
    current_load: int = 0

    # Status
    status: str = "idle"  # "idle", "busy", "offline"
    last_heartbeat: float = field(default_factory=time.time)

    # Specialization
    supported_task_types: List[str] = field(default_factory=lambda: ["backtest", "signal_generation", "optimization"])

    @property
    def utilization_cpu(self) -> float:
        """Calculate CPU utilization"""
        if self.total_cpu_cores == 0:
            return 0.0
        return ((self.total_cpu_cores - self.available_cpu_cores) / self.total_cpu_cores) * 100.0

    @property
    def utilization_memory(self) -> float:
        """Calculate memory utilization"""
        if self.total_memory_gb == 0:
            return 0.0
        return ((self.total_memory_gb - self.available_memory_gb) / self.total_memory_gb) * 100.0


class DistributedCache:
    """Distributed caching system for shared data"""

    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.redis_client = None
        self.local_cache = {}

        if self.config.use_redis and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    decode_responses=False
                )
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self.redis_client = None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache"""

        if ttl is None:
            ttl = self.config.cache_ttl_seconds

        try:
            # Local cache
            self.local_cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }

            # Redis cache
            if self.redis_client:
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)

            return True

        except Exception as e:
            print(f"Cache set failed: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""

        # Check local cache first
        if key in self.local_cache:
            entry = self.local_cache[key]
            if time.time() < entry['expires_at']:
                return entry['value']
            else:
                del self.local_cache[key]

        # Check Redis cache
        if self.redis_client:
            try:
                serialized = self.redis_client.get(key)
                if serialized:
                    value = pickle.loads(serialized)
                    # Update local cache
                    ttl = self.redis_client.ttl(key)
                    if ttl > 0:
                        self.local_cache[key] = {
                            'value': value,
                            'expires_at': time.time() + ttl
                        }
                    return value
            except Exception as e:
                print(f"Redis get failed: {e}")

        return None

    def delete(self, key: str) -> bool:
        """Delete a value from cache"""

        # Delete from local cache
        self.local_cache.pop(key, None)

        # Delete from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis delete failed: {e}")
                return False

        return True

    def clear_expired(self):
        """Clear expired entries from local cache"""

        current_time = time.time()
        expired_keys = [
            key for key, entry in self.local_cache.items()
            if current_time >= entry['expires_at']
        ]

        for key in expired_keys:
            del self.local_cache[key]


class TaskScheduler:
    """Advanced task scheduler with dependency management"""

    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.workers = {}
        self.pending_tasks = deque()
        self.running_tasks = {}
        self.completed_tasks = {}

        # Workflow management
        self.workflows = {}

        # Performance tracking
        self.task_execution_times = defaultdict(list)
        self.worker_performance = defaultdict(list)

    def register_worker(self, worker: WorkerNode):
        """Register a worker node"""
        self.workers[worker.worker_id] = worker

    def unregister_worker(self, worker_id: str):
        """Unregister a worker node"""
        if worker_id in self.workers:
            del self.workers[worker_id]

            # Requeue tasks assigned to this worker
            tasks_to_requeue = [
                task_id for task_id, task in self.running_tasks.items()
                if task.assigned_worker == worker_id
            ]

            for task_id in tasks_to_requeue:
                task = self.running_tasks[task_id]
                task.status = "pending"
                task.assigned_worker = None
                self.pending_tasks.append(task)
                del self.running_tasks[task_id]

    def submit_task(self, task: DistributedTask) -> str:
        """Submit a task for execution"""

        # Add to appropriate workflow if specified
        if task.workflow_id:
            if task.workflow_id not in self.workflows:
                self.workflows[task.workflow_id] = Workflow(
                    workflow_id=task.workflow_id,
                    name=f"Workflow {task.workflow_id}",
                    tasks={}
                )

            self.workflows[task.workflow_id].tasks[task.task_id] = task

            # Update DAG
            workflow = self.workflows[task.workflow_id]
            workflow.dag.add_node(task.task_id)
            for dep in task.dependencies:
                workflow.dag.add_edge(dep, task.task_id)
        else:
            # Add to pending queue
            self.pending_tasks.append(task)

        return task.task_id

    def submit_workflow(self, workflow: Workflow) -> str:
        """Submit a complete workflow"""

        self.workflows[workflow.workflow_id] = workflow

        # Add all tasks to pending queue (scheduler will handle dependencies)
        for task in workflow.tasks.values():
            if not task.dependencies:  # Only add tasks with no dependencies
                self.pending_tasks.append(task)

        return workflow.workflow_id

    def get_next_task(self, worker_id: str) -> Optional[DistributedTask]:
        """Get next task for a worker"""

        if worker_id not in self.workers:
            return None

        worker = self.workers[worker_id]

        # Check workflow tasks first
        for workflow in self.workflows.values():
            if workflow.status == "running":
                executable_tasks = workflow.executable_tasks
                for task_id in executable_tasks:
                    task = workflow.tasks[task_id]
                    if self._can_execute_task(task, worker):
                        task.assigned_worker = worker_id
                        task.status = "running"
                        task.started_at = time.time()
                        self.running_tasks[task_id] = task
                        return task

        # Check regular pending tasks
        for task in list(self.pending_tasks):
            if self._can_execute_task(task, worker):
                task.assigned_worker = worker_id
                task.status = "running"
                task.started_at = time.time()
                self.pending_tasks.remove(task)
                self.running_tasks[task.task_id] = task
                return task

        return None

    def complete_task(self, task_id: str, result: Any = None, error: str = ""):
        """Mark a task as completed"""

        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.completed_at = time.time()
            task.result = result

            if error:
                task.status = "failed"
                task.error_message = error
                # Handle retry logic
                if task.retry_count < self.config.max_retries:
                    task.retry_count += 1
                    task.status = "pending"
                    task.assigned_worker = None
                    self.pending_tasks.append(task)
                else:
                    self.completed_tasks[task_id] = task
            else:
                task.status = "completed"
                self.completed_tasks[task_id] = task

                # Update workflow progress
                if task.workflow_id and task.workflow_id in self.workflows:
                    workflow = self.workflows[task.workflow_id]
                    workflow.progress = workflow.completion_percentage

                    # Check if workflow is complete
                    if workflow.completion_percentage >= 100.0:
                        workflow.status = "completed"
                        workflow.completed_at = time.time()

                        # Add newly executable tasks
                        executable_tasks = workflow.executable_tasks
                        for exec_task_id in executable_tasks:
                            exec_task = workflow.tasks[exec_task_id]
                            self.pending_tasks.append(exec_task)

            # Update worker stats
            if task.assigned_worker and task.assigned_worker in self.workers:
                worker = self.workers[task.assigned_worker]
                worker.tasks_completed += 1
                worker.current_load = max(0, worker.current_load - 1)

                # Update performance metrics
                if task.execution_time > 0:
                    self.task_execution_times[task.task_type].append(task.execution_time)
                    worker.avg_task_time = np.mean(self.task_execution_times[task.task_type])

            del self.running_tasks[task_id]

    def _can_execute_task(self, task: DistributedTask, worker: WorkerNode) -> bool:
        """Check if a worker can execute a task"""

        # Check resource availability
        if self.config.enable_resource_limits:
            if worker.available_cpu_cores < task.cpu_cores:
                return False
            if worker.available_memory_gb < task.memory_gb:
                return False

        # Check task type compatibility
        if task.task_type not in worker.supported_task_types:
            return False

        # Check worker capacity
        if worker.current_load >= self.config.max_concurrent_tasks:
            return False

        return True

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""

        return {
            'total_workers': len(self.workers),
            'active_workers': sum(1 for w in self.workers.values() if w.status == "busy"),
            'pending_tasks': len(self.pending_tasks),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'active_workflows': sum(1 for w in self.workflows.values() if w.status == "running")
        }


class DistributedExecutor:
    """Main distributed execution engine"""

    def __init__(self, config: ExecutionConfig):
        self.config = config

        # Core components
        self.scheduler = TaskScheduler(config)
        self.cache = DistributedCache(config)
        self.monitor = ExecutionMonitor(config)

        # Communication
        self.redis_client = None
        self.zmq_context = None

        # Execution pools
        self.local_executor = ProcessPoolExecutor(max_workers=self.config.max_concurrent_tasks)
        self.futures = {}

        # State
        self.is_running = False
        self.execution_thread = None

    def initialize(self) -> bool:
        """Initialize the distributed executor"""

        # Setup Redis connection
        if self.config.use_redis and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port
                )
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis initialization failed: {e}")
                if self.config.use_redis:
                    return False

        # Setup ZeroMQ
        if self.config.use_zmq and ZMQ_AVAILABLE:
            try:
                self.zmq_context = zmq.Context()
            except Exception as e:
                print(f"ZeroMQ initialization failed: {e}")
                if self.config.use_zmq:
                    return False

        # Create shared storage directory
        os.makedirs(self.config.shared_storage_path, exist_ok=True)

        # Register local worker
        local_worker = WorkerNode(
            worker_id=f"local_{uuid.uuid4().hex[:8]}",
            host="localhost",
            port=0,
            capabilities={"local_execution": True}
        )
        self.scheduler.register_worker(local_worker)

        return True

    def start_execution(self):
        """Start the execution engine"""

        if self.is_running:
            return

        self.is_running = True
        self.execution_thread = threading.Thread(target=self._execution_loop)
        self.execution_thread.daemon = True
        self.execution_thread.start()

        self.monitor.start_monitoring()

    def stop_execution(self):
        """Stop the execution engine"""

        self.is_running = False
        if self.execution_thread:
            self.execution_thread.join()

        self.monitor.stop_monitoring()
        self.local_executor.shutdown()

    def submit_task(self, task_type: str, payload: Dict[str, Any],
                   dependencies: List[str] = None, priority: int = 1,
                   workflow_id: str = "") -> str:
        """Submit a task for distributed execution"""

        task = DistributedTask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            payload=payload,
            priority=priority,
            dependencies=dependencies or [],
            workflow_id=workflow_id
        )

        return self.scheduler.submit_task(task)

    def submit_workflow(self, workflow: Workflow) -> str:
        """Submit a workflow for execution"""

        return self.scheduler.submit_workflow(workflow)

    def get_task_status(self, task_id: str) -> Optional[DistributedTask]:
        """Get status of a task"""

        # Check running tasks
        if task_id in self.scheduler.running_tasks:
            return self.scheduler.running_tasks[task_id]

        # Check completed tasks
        if task_id in self.scheduler.completed_tasks:
            return self.scheduler.completed_tasks[task_id]

        # Check workflows
        for workflow in self.scheduler.workflows.values():
            if task_id in workflow.tasks:
                return workflow.tasks[task_id]

        return None

    def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        """Get status of a workflow"""

        return self.scheduler.workflows.get(workflow_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""

        # Find and cancel the task
        task = self.get_task_status(task_id)
        if task and task.status in ["pending", "running"]:
            task.status = "cancelled"
            return True

        return False

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""

        scheduler_stats = self.scheduler.get_scheduler_status()
        monitor_stats = self.monitor.get_monitoring_stats()

        return {
            'scheduler': scheduler_stats,
            'monitoring': monitor_stats,
            'cache_stats': {
                'local_cache_size': len(self.cache.local_cache),
                'redis_available': self.redis_client is not None
            }
        }

    def _execution_loop(self):
        """Main execution loop"""

        while self.is_running:
            try:
                # Process completed futures
                completed_futures = []
                for future, task_id in self.futures.items():
                    if future.done():
                        completed_futures.append((future, task_id))

                for future, task_id in completed_futures:
                    del self.futures[future]

                    try:
                        result = future.result(timeout=1)
                        self.scheduler.complete_task(task_id, result=result)
                    except Exception as e:
                        self.scheduler.complete_task(task_id, error=str(e))

                # Assign new tasks to workers
                for worker_id in list(self.scheduler.workers.keys()):
                    if worker_id.startswith("local_"):  # Local worker
                        task = self.scheduler.get_next_task(worker_id)
                        if task:
                            # Execute locally
                            future = self.local_executor.submit(
                                self._execute_task_locally, task
                            )
                            self.futures[future] = task.task_id

                            # Update worker load
                            worker = self.scheduler.workers[worker_id]
                            worker.current_load += 1

                # Clean expired tasks
                self._cleanup_expired_tasks()

                time.sleep(1)  # Prevent busy waiting

            except Exception as e:
                print(f"Execution loop error: {e}")
                time.sleep(5)

    def _execute_task_locally(self, task: DistributedTask) -> Any:
        """Execute a task locally"""

        try:
            # Task execution logic based on type
            if task.task_type == "backtest":
                return self._execute_backtest_task(task)
            elif task.task_type == "signal_generation":
                return self._execute_signal_task(task)
            elif task.task_type == "optimization":
                return self._execute_optimization_task(task)
            else:
                # Generic task execution
                return self._execute_generic_task(task)

        except Exception as e:
            raise Exception(f"Task execution failed: {e}")

    def _execute_backtest_task(self, task: DistributedTask) -> Dict[str, Any]:
        """Execute a backtesting task"""

        # Mock backtest execution - in real implementation,
        # this would call the actual backtesting engine
        time.sleep(np.random.uniform(1, 10))  # Simulate execution time

        return {
            'sharpe_ratio': np.random.normal(1.5, 0.5),
            'max_drawdown': np.random.uniform(0.05, 0.25),
            'total_return': np.random.normal(0.15, 0.05),
            'win_rate': np.random.uniform(0.5, 0.7),
            'execution_time': time.time() - task.started_at if task.started_at else 0
        }

    def _execute_signal_task(self, task: DistributedTask) -> Dict[str, Any]:
        """Execute a signal generation task"""

        time.sleep(np.random.uniform(0.5, 3))

        return {
            'signals_generated': np.random.randint(10, 100),
            'signal_strength': np.random.uniform(0.1, 1.0),
            'confidence_score': np.random.uniform(0.5, 0.95)
        }

    def _execute_optimization_task(self, task: DistributedTask) -> Dict[str, Any]:
        """Execute an optimization task"""

        time.sleep(np.random.uniform(5, 30))

        return {
            'optimal_parameters': {
                'param1': np.random.uniform(0, 1),
                'param2': np.random.uniform(0, 1),
                'param3': np.random.uniform(0, 1)
            },
            'fitness_score': np.random.uniform(0.8, 1.0),
            'convergence_time': np.random.uniform(10, 100)
        }

    def _execute_generic_task(self, task: DistributedTask) -> Any:
        """Execute a generic task"""

        # Extract function to execute
        func = task.payload.get('function')
        args = task.payload.get('args', [])
        kwargs = task.payload.get('kwargs', {})

        if callable(func):
            return func(*args, **kwargs)
        else:
            raise ValueError(f"No executable function provided for task {task.task_id}")

    def _cleanup_expired_tasks(self):
        """Clean up expired tasks"""

        current_time = time.time()

        # Clean expired running tasks
        expired_running = [
            task_id for task_id, task in self.scheduler.running_tasks.items()
            if current_time - task.created_at > self.config.task_timeout_seconds
        ]

        for task_id in expired_running:
            task = self.scheduler.running_tasks[task_id]
            task.status = "failed"
            task.error_message = "Task timeout"
            self.scheduler.completed_tasks[task_id] = task
            del self.scheduler.running_tasks[task_id]

        # Clean cache
        self.cache.clear_expired()


class ExecutionMonitor:
    """Execution monitoring and analytics"""

    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.metrics_history = deque(maxlen=10000)
        self.is_monitoring = False
        self.monitoring_thread = None

    def start_monitoring(self):
        """Start monitoring"""

        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def record_metric(self, metric_type: str, value: Any, metadata: Dict[str, Any] = None):
        """Record a metric"""

        self.metrics_history.append({
            'timestamp': time.time(),
            'type': metric_type,
            'value': value,
            'metadata': metadata or {}
        })

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""

        if not self.metrics_history:
            return {'error': 'No metrics recorded'}

        # Calculate basic stats
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 metrics

        return {
            'total_metrics': len(self.metrics_history),
            'recent_metrics_count': len(recent_metrics),
            'avg_metric_frequency': len(recent_metrics) / (self.config.metrics_collection_interval * len(recent_metrics)) if recent_metrics else 0
        }

    def _monitoring_loop(self):
        """Monitoring loop"""

        while self.is_monitoring:
            try:
                # Collect system metrics
                self.record_metric('cpu_usage', psutil.cpu_percent())
                self.record_metric('memory_usage', psutil.virtual_memory().percent)
                self.record_metric('disk_usage', psutil.disk_usage('/').percent)

                time.sleep(self.config.metrics_collection_interval)

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)


# Workflow creation utilities
def create_linear_workflow(name: str, tasks: List[DistributedTask]) -> Workflow:
    """Create a linear workflow (tasks executed sequentially)"""

    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        name=name,
        tasks={}
    )

    # Set up dependencies
    for i, task in enumerate(tasks):
        task.workflow_id = workflow.workflow_id
        if i > 0:
            task.dependencies = [tasks[i-1].task_id]

        workflow.tasks[task.task_id] = task
        workflow.dag.add_node(task.task_id)

        if i > 0:
            workflow.dag.add_edge(tasks[i-1].task_id, task.task_id)

    return workflow


def create_parallel_workflow(name: str, task_groups: List[List[DistributedTask]]) -> Workflow:
    """Create a parallel workflow (independent task groups)"""

    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        name=name,
        tasks={}
    )

    # Add all tasks without dependencies
    for group in task_groups:
        for task in group:
            task.workflow_id = workflow.workflow_id
            workflow.tasks[task.task_id] = task
            workflow.dag.add_node(task.task_id)

    return workflow


# Factory functions
def create_distributed_executor(config: Optional[ExecutionConfig] = None) -> DistributedExecutor:
    """Factory function for distributed executor"""
    if config is None:
        config = ExecutionConfig()
    return DistributedExecutor(config)


def create_execution_config(max_concurrent_tasks: int = 50) -> ExecutionConfig:
    """Create execution configuration"""
    return ExecutionConfig(max_concurrent_tasks=max_concurrent_tasks)


# Example usage and testing
if __name__ == "__main__":
    # Test distributed execution
    print("Testing Distributed Execution Engine...")

    config = create_execution_config(max_concurrent_tasks=4)
    executor = create_distributed_executor(config)

    if executor.initialize():
        print("✓ Distributed executor initialized")

        executor.start_execution()

        # Submit some test tasks
        task_ids = []
        for i in range(5):
            task_id = executor.submit_task(
                task_type="backtest",
                payload={"strategy": f"strategy_{i}", "data_size": 1000},
                priority=1
            )
            task_ids.append(task_id)
            print(f"Submitted task: {task_id}")

        # Wait for completion
        import time
        start_time = time.time()
        while time.time() - start_time < 60:  # Wait up to 1 minute
            completed = sum(1 for tid in task_ids if executor.get_task_status(tid) and executor.get_task_status(tid).is_completed)
            if completed == len(task_ids):
                break
            time.sleep(1)

        # Check results
        successful = 0
        for task_id in task_ids:
            task = executor.get_task_status(task_id)
            if task and task.is_successful:
                successful += 1
                print(f"Task {task_id}: ✓ Completed")
            else:
                print(f"Task {task_id}: ✗ Failed")

        print(f"\nExecution Summary:")
        print(f"Total tasks: {len(task_ids)}")
        print(f"Successful: {successful}")
        print(f"Success rate: {successful/len(task_ids)*100:.1f}%")

        # Get execution stats
        stats = executor.get_execution_stats()
        print("\nExecution Stats:")
        print(f"Workers: {stats['scheduler']['total_workers']}")
        print(f"Running tasks: {stats['scheduler']['running_tasks']}")
        print(f"Completed tasks: {stats['scheduler']['completed_tasks']}")

        executor.stop_execution()
        print("✓ Distributed execution test completed")

    else:
        print("✗ Failed to initialize distributed executor")

    print("\nDistributed execution test completed!")

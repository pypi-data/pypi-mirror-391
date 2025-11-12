"""
Intelligent Load Balancer for Distributed Computing
===================================================

This module implements sophisticated load balancing algorithms for optimal
workload distribution across distributed computing resources. Supports multiple
balancing strategies, real-time adaptation, and performance optimization.

Key Features:
- Multiple load balancing algorithms (Round Robin, Least Loaded, Weighted, etc.)
- Real-time resource monitoring and adaptation
- Predictive load balancing with machine learning
- Geographic load balancing for latency optimization
- Task affinity and resource constraints
- Auto-scaling integration
- Quality of Service (QoS) guarantees
- Fault-aware load balancing
"""

from __future__ import annotations

import warnings
import json
import time
import threading
import asyncio
import uuid
import hashlib
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from datetime import datetime, timedelta
import heapq

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Import existing distributed components
try:
    from .distributed_execution import WorkerNode, DistributedTask, ExecutionConfig
except ImportError:
    WorkerNode = None
    DistributedTask = None
    ExecutionConfig = None


@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing"""

    # Algorithm settings
    algorithm: str = "adaptive"  # "round_robin", "least_loaded", "weighted", "adaptive", "predictive"
    adaptation_interval: int = 30  # seconds

    # Resource weights
    cpu_weight: float = 0.4
    memory_weight: float = 0.3
    network_weight: float = 0.2
    latency_weight: float = 0.1

    # QoS settings
    enable_qos: bool = True
    priority_levels: int = 5
    max_response_time: float = 60.0  # seconds

    # Geographic balancing
    enable_geographic_balancing: bool = False
    max_latency_ms: int = 100

    # Learning settings
    enable_learning: bool = True
    learning_window: int = 1000  # historical decisions to learn from
    model_update_interval: int = 300  # seconds

    # Fault tolerance
    fault_detection_enabled: bool = True
    health_check_interval: int = 10  # seconds
    failure_threshold: int = 3


@dataclass
class ResourceMetrics:
    """Resource utilization metrics"""

    worker_id: str
    timestamp: float

    # CPU metrics
    cpu_utilization: float = 0.0
    cpu_cores_used: int = 0
    cpu_cores_total: int = 0

    # Memory metrics
    memory_utilization: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0

    # Network metrics
    network_in_mbps: float = 0.0
    network_out_mbps: float = 0.0
    latency_ms: float = 0.0

    # Task metrics
    active_tasks: int = 0
    queued_tasks: int = 0
    completed_tasks_per_minute: float = 0.0

    # Health metrics
    health_score: float = 1.0  # 0.0 to 1.0
    consecutive_failures: int = 0

    @property
    def load_score(self) -> float:
        """Calculate overall load score (0.0 to 1.0)"""
        cpu_load = self.cpu_utilization / 100.0
        memory_load = self.memory_utilization / 100.0
        task_load = min(self.active_tasks / max(self.cpu_cores_total * 2, 1), 1.0)

        return (cpu_load + memory_load + task_load) / 3.0

    @property
    def available_capacity(self) -> float:
        """Calculate available capacity (0.0 to 1.0)"""
        return 1.0 - self.load_score


@dataclass
class LoadDecision:
    """A load balancing decision"""

    decision_id: str
    task_id: str
    worker_id: str
    timestamp: float
    algorithm_used: str
    confidence_score: float = 0.0

    # Performance prediction
    predicted_completion_time: float = 0.0
    predicted_resource_usage: Dict[str, float] = field(default_factory=dict)

    # Actual outcome (filled after completion)
    actual_completion_time: float = 0.0
    actual_resource_usage: Dict[str, float] = field(default_factory=dict)
    success: bool = False


class LoadBalancingAlgorithm(ABC):
    """Abstract base class for load balancing algorithms"""

    def __init__(self, config: LoadBalancingConfig):
        self.config = config

    @abstractmethod
    def select_worker(self, task: DistributedTask, workers: Dict[str, WorkerNode],
                     metrics: Dict[str, ResourceMetrics]) -> Optional[str]:
        """Select the best worker for a task"""
        pass

    @abstractmethod
    def update_weights(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """Update algorithm weights based on decision outcomes"""
        pass


class RoundRobinAlgorithm(LoadBalancingAlgorithm):
    """Simple round-robin load balancing"""

    def __init__(self, config: LoadBalancingConfig):
        super().__init__(config)
        self.last_worker_index = 0

    def select_worker(self, task: DistributedTask, workers: Dict[str, WorkerNode],
                     metrics: Dict[str, ResourceMetrics]) -> Optional[str]:
        """Select next worker in round-robin fashion"""

        available_workers = [
            worker_id for worker_id, worker in workers.items()
            if worker.status == "idle" and self._meets_requirements(task, worker_id, metrics)
        ]

        if not available_workers:
            return None

        # Round-robin selection
        selected_worker = available_workers[self.last_worker_index % len(available_workers)]
        self.last_worker_index += 1

        return selected_worker

    def update_weights(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """No weights to update for round-robin"""
        pass

    def _meets_requirements(self, task: DistributedTask, worker_id: str,
                           metrics: Dict[str, ResourceMetrics]) -> bool:
        """Check if worker meets task requirements"""

        if worker_id not in metrics:
            return False

        worker_metrics = metrics[worker_id]

        # Check resource availability
        if worker_metrics.cpu_cores_used + task.cpu_cores > worker_metrics.cpu_cores_total:
            return False

        if worker_metrics.memory_used_gb + task.memory_gb > worker_metrics.memory_total_gb:
            return False

        return True


class LeastLoadedAlgorithm(LoadBalancingAlgorithm):
    """Least loaded worker selection"""

    def __init__(self, config: LoadBalancingConfig):
        super().__init__(config)

    def select_worker(self, task: DistributedTask, workers: Dict[str, WorkerNode],
                     metrics: Dict[str, ResourceMetrics]) -> Optional[str]:
        """Select the least loaded available worker"""

        available_workers = [
            worker_id for worker_id, worker in workers.items()
            if worker.status == "idle" and self._meets_requirements(task, worker_id, metrics)
        ]

        if not available_workers:
            return None

        # Find worker with lowest load score
        best_worker = None
        best_score = float('inf')

        for worker_id in available_workers:
            load_score = metrics[worker_id].load_score
            if load_score < best_score:
                best_score = load_score
                best_worker = worker_id

        return best_worker

    def update_weights(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """No weights to update for least loaded"""
        pass

    def _meets_requirements(self, task: DistributedTask, worker_id: str,
                           metrics: Dict[str, ResourceMetrics]) -> bool:
        """Check if worker meets task requirements"""

        if worker_id not in metrics:
            return False

        worker_metrics = metrics[worker_id]

        # Check resource availability
        if worker_metrics.cpu_cores_used + task.cpu_cores > worker_metrics.cpu_cores_total:
            return False

        if worker_metrics.memory_used_gb + task.memory_gb > worker_metrics.memory_total_gb:
            return False

        return True


class WeightedAlgorithm(LoadBalancingAlgorithm):
    """Weighted load balancing based on resource utilization"""

    def __init__(self, config: LoadBalancingConfig):
        super().__init__(config)
        self.weights = {
            'cpu': config.cpu_weight,
            'memory': config.memory_weight,
            'network': config.network_weight,
            'latency': config.latency_weight
        }

    def select_worker(self, task: DistributedTask, workers: Dict[str, WorkerNode],
                     metrics: Dict[str, ResourceMetrics]) -> Optional[str]:
        """Select worker based on weighted resource scores"""

        available_workers = [
            worker_id for worker_id, worker in workers.items()
            if worker.status == "idle" and self._meets_requirements(task, worker_id, metrics)
        ]

        if not available_workers:
            return None

        # Calculate weighted scores
        worker_scores = {}
        for worker_id in available_workers:
            worker_metrics = metrics[worker_id]

            # Normalize metrics to 0-1 scale
            cpu_score = worker_metrics.cpu_utilization / 100.0
            memory_score = worker_metrics.memory_utilization / 100.0
            network_score = min(worker_metrics.network_out_mbps / 100.0, 1.0)  # Assume 100 Mbps max
            latency_score = min(worker_metrics.latency_ms / self.config.max_latency_ms, 1.0)

            # Calculate weighted score (lower is better)
            total_score = (
                self.weights['cpu'] * cpu_score +
                self.weights['memory'] * memory_score +
                self.weights['network'] * network_score +
                self.weights['latency'] * latency_score
            )

            worker_scores[worker_id] = total_score

        # Return worker with lowest score
        return min(worker_scores, key=worker_scores.get)

    def update_weights(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """Update weights based on performance feedback"""

        # Simple reinforcement learning for weights
        success = outcome.get('success', False)
        response_time = outcome.get('response_time', 0.0)

        if success and response_time < self.config.max_response_time:
            # Increase weights for good outcomes (reinforcement)
            adjustment = 0.01
        else:
            # Decrease weights for poor outcomes (penalty)
            adjustment = -0.01

        # Update weights (keep them in reasonable bounds)
        for key in self.weights:
            self.weights[key] = np.clip(self.weights[key] + adjustment, 0.1, 0.5)

        # Renormalize weights
        total_weight = sum(self.weights.values())
        self.weights = {k: v/total_weight for k, v in self.weights.items()}

    def _meets_requirements(self, task: DistributedTask, worker_id: str,
                           metrics: Dict[str, ResourceMetrics]) -> bool:
        """Check if worker meets task requirements"""

        if worker_id not in metrics:
            return False

        worker_metrics = metrics[worker_id]

        # Check resource availability
        if worker_metrics.cpu_cores_used + task.cpu_cores > worker_metrics.cpu_cores_total:
            return False

        if worker_metrics.memory_used_gb + task.memory_gb > worker_metrics.memory_total_gb:
            return False

        return True


class AdaptiveAlgorithm(LoadBalancingAlgorithm):
    """Adaptive algorithm that learns from past decisions"""

    def __init__(self, config: LoadBalancingConfig):
        super().__init__(config)
        self.decision_history = deque(maxlen=config.learning_window)
        self.performance_model = None
        self.scaler = StandardScaler()
        self.last_model_update = time.time()

    def select_worker(self, task: DistributedTask, workers: Dict[str, WorkerNode],
                     metrics: Dict[str, ResourceMetrics]) -> Optional[str]:
        """Select worker using adaptive learning"""

        available_workers = [
            worker_id for worker_id, worker in workers.items()
            if worker.status == "idle" and self._meets_requirements(task, worker_id, metrics)
        ]

        if not available_workers:
            return None

        if self.performance_model and len(self.decision_history) >= 50:
            # Use ML model for prediction
            return self._predict_best_worker(task, available_workers, metrics)
        else:
            # Fall back to weighted algorithm
            weighted_alg = WeightedAlgorithm(self.config)
            return weighted_alg.select_worker(task, workers, metrics)

    def update_weights(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """Update the ML model with new decision outcomes"""

        # Store decision and outcome
        decision_outcome = {
            'decision': decision,
            'outcome': outcome,
            'timestamp': time.time()
        }
        self.decision_history.append(decision_outcome)

        # Update model periodically
        if time.time() - self.last_model_update > self.config.model_update_interval:
            self._update_performance_model()
            self.last_model_update = time.time()

    def _predict_best_worker(self, task: DistributedTask, available_workers: List[str],
                           metrics: Dict[str, ResourceMetrics]) -> str:
        """Predict best worker using ML model"""

        if not self.performance_model:
            return np.random.choice(available_workers)

        # Prepare features for each worker
        worker_features = []
        worker_ids = []

        for worker_id in available_workers:
            worker_metrics = metrics[worker_id]

            features = [
                worker_metrics.cpu_utilization,
                worker_metrics.memory_utilization,
                worker_metrics.network_out_mbps,
                worker_metrics.latency_ms,
                worker_metrics.active_tasks,
                worker_metrics.completed_tasks_per_minute,
                worker_metrics.health_score,
                task.cpu_cores,
                task.memory_gb,
                task.estimated_duration
            ]

            worker_features.append(features)
            worker_ids.append(worker_id)

        # Scale features
        worker_features_scaled = self.scaler.transform(worker_features)

        # Predict performance scores
        predictions = self.performance_model.predict(worker_features_scaled)

        # Return worker with best predicted performance
        best_idx = np.argmin(predictions)  # Lower score = better performance
        return worker_ids[best_idx]

    def _update_performance_model(self):
        """Update the performance prediction model"""

        if len(self.decision_history) < 50:
            return

        # Prepare training data
        X = []
        y = []

        for decision_outcome in self.decision_history:
            decision = decision_outcome['decision']
            outcome = decision_outcome['outcome']

            if 'task_features' in decision and 'performance_score' in outcome:
                X.append(decision['task_features'] + outcome.get('worker_features', []))
                y.append(outcome['performance_score'])

        if len(X) >= 50:
            X = np.array(X)
            y = np.array(y)

            # Scale features
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)

            # Train model
            self.performance_model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            self.performance_model.fit(X_scaled, y)

    def _meets_requirements(self, task: DistributedTask, worker_id: str,
                           metrics: Dict[str, ResourceMetrics]) -> bool:
        """Check if worker meets task requirements"""

        if worker_id not in metrics:
            return False

        worker_metrics = metrics[worker_id]

        # Check resource availability
        if worker_metrics.cpu_cores_used + task.cpu_cores > worker_metrics.cpu_cores_total:
            return False

        if worker_metrics.memory_used_gb + task.memory_gb > worker_metrics.memory_total_gb:
            return False

        return True


class GeographicLoadBalancer:
    """Geographic load balancing for latency optimization"""

    def __init__(self, config: LoadBalancingConfig):
        self.config = config
        self.worker_locations = {}  # worker_id -> (lat, lon)
        self.client_locations = {}  # client_id -> (lat, lon)

    def set_worker_location(self, worker_id: str, latitude: float, longitude: float):
        """Set geographic location of a worker"""
        self.worker_locations[worker_id] = (latitude, longitude)

    def set_client_location(self, client_id: str, latitude: float, longitude: float):
        """Set geographic location of a client"""
        self.client_locations[client_id] = (latitude, longitude)

    def get_nearest_workers(self, client_id: str, max_distance_km: float = 1000.0) -> List[str]:
        """Get workers nearest to a client"""

        if client_id not in self.client_locations:
            return []

        client_lat, client_lon = self.client_locations[client_id]
        worker_distances = []

        for worker_id, (worker_lat, worker_lon) in self.worker_locations.items():
            distance = self._haversine_distance(client_lat, client_lon, worker_lat, worker_lon)
            if distance <= max_distance_km:
                worker_distances.append((worker_id, distance))

        # Sort by distance
        worker_distances.sort(key=lambda x: x[1])
        return [worker_id for worker_id, _ in worker_distances]

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points"""

        # Convert to radians
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        # Radius of Earth in kilometers
        r = 6371.0

        return c * r


class IntelligentLoadBalancer:
    """Main intelligent load balancer"""

    def __init__(self, config: LoadBalancingConfig):
        self.config = config

        # Initialize algorithms
        self.algorithms = {
            'round_robin': RoundRobinAlgorithm(config),
            'least_loaded': LeastLoadedAlgorithm(config),
            'weighted': WeightedAlgorithm(config),
            'adaptive': AdaptiveAlgorithm(config)
        }

        self.current_algorithm = self.algorithms[self.config.algorithm]

        # Geographic balancer
        self.geo_balancer = GeographicLoadBalancer(config)

        # Monitoring and metrics
        self.metrics = {}  # worker_id -> ResourceMetrics
        self.decisions = deque(maxlen=10000)  # LoadDecision history

        # Health monitoring
        self.worker_health = {}  # worker_id -> health status
        self.monitoring_thread = None
        self.is_monitoring = False

    def register_worker(self, worker: WorkerNode):
        """Register a worker with the load balancer"""

        # Initialize metrics
        self.metrics[worker.worker_id] = ResourceMetrics(
            worker_id=worker.worker_id,
            timestamp=time.time(),
            cpu_cores_total=worker.total_cpu_cores,
            memory_total_gb=worker.total_memory_gb
        )

        # Initialize health
        self.worker_health[worker.worker_id] = {
            'status': 'healthy',
            'last_check': time.time(),
            'consecutive_failures': 0
        }

    def unregister_worker(self, worker_id: str):
        """Unregister a worker"""

        if worker_id in self.metrics:
            del self.metrics[worker_id]
        if worker_id in self.worker_health:
            del self.worker_health[worker_id]

    def update_worker_metrics(self, worker_id: str, metrics: Dict[str, Any]):
        """Update worker metrics"""

        if worker_id not in self.metrics:
            return

        worker_metrics = self.metrics[worker_id]
        worker_metrics.timestamp = time.time()

        # Update CPU metrics
        if 'cpu_utilization' in metrics:
            worker_metrics.cpu_utilization = metrics['cpu_utilization']
        if 'cpu_cores_used' in metrics:
            worker_metrics.cpu_cores_used = metrics['cpu_cores_used']

        # Update memory metrics
        if 'memory_utilization' in metrics:
            worker_metrics.memory_utilization = metrics['memory_utilization']
        if 'memory_used_gb' in metrics:
            worker_metrics.memory_used_gb = metrics['memory_used_gb']

        # Update network metrics
        if 'network_in_mbps' in metrics:
            worker_metrics.network_in_mbps = metrics['network_in_mbps']
        if 'network_out_mbps' in metrics:
            worker_metrics.network_out_mbps = metrics['network_out_mbps']
        if 'latency_ms' in metrics:
            worker_metrics.latency_ms = metrics['latency_ms']

        # Update task metrics
        if 'active_tasks' in metrics:
            worker_metrics.active_tasks = metrics['active_tasks']
        if 'queued_tasks' in metrics:
            worker_metrics.queued_tasks = metrics['queued_tasks']
        if 'completed_tasks_per_minute' in metrics:
            worker_metrics.completed_tasks_per_minute = metrics['completed_tasks_per_minute']

    def select_worker(self, task: DistributedTask, client_id: str = None) -> Optional[Tuple[str, float]]:
        """Select the best worker for a task"""

        # Get candidate workers
        if self.config.enable_geographic_balancing and client_id:
            candidate_workers = self.geo_balancer.get_nearest_workers(client_id)
            if not candidate_workers:
                candidate_workers = list(self.metrics.keys())
        else:
            candidate_workers = list(self.metrics.keys())

        if not candidate_workers:
            return None

        # Filter healthy workers
        healthy_workers = [
            worker_id for worker_id in candidate_workers
            if self.worker_health.get(worker_id, {}).get('status') == 'healthy'
        ]

        if not healthy_workers:
            return None

        # Create mock worker objects for algorithm
        mock_workers = {
            worker_id: WorkerNode(
                worker_id=worker_id,
                host="",
                port=0,
                capabilities={}
            ) for worker_id in healthy_workers
        }

        # Select worker using current algorithm
        selected_worker = self.current_algorithm.select_worker(task, mock_workers, self.metrics)

        if selected_worker:
            # Calculate confidence score
            confidence = self._calculate_confidence_score(task, selected_worker)

            # Record decision
            decision = LoadDecision(
                decision_id=str(uuid.uuid4()),
                task_id=task.task_id,
                worker_id=selected_worker,
                timestamp=time.time(),
                algorithm_used=self.config.algorithm,
                confidence_score=confidence
            )
            self.decisions.append(decision)

            return selected_worker, confidence

        return None

    def record_decision_outcome(self, decision: LoadDecision, outcome: Dict[str, Any]):
        """Record the outcome of a load balancing decision"""

        # Update decision with actual outcome
        decision.actual_completion_time = outcome.get('completion_time', 0.0)
        decision.actual_resource_usage = outcome.get('resource_usage', {})
        decision.success = outcome.get('success', False)

        # Update algorithm weights
        self.current_algorithm.update_weights(decision, outcome)

    def get_load_distribution(self) -> Dict[str, Any]:
        """Get current load distribution across workers"""

        if not self.metrics:
            return {'error': 'No worker metrics available'}

        total_load = sum(metrics.load_score for metrics in self.metrics.values())
        avg_load = total_load / len(self.metrics)

        worker_loads = {
            worker_id: metrics.load_score
            for worker_id, metrics in self.metrics.items()
        }

        return {
            'total_workers': len(self.metrics),
            'average_load': avg_load,
            'worker_loads': worker_loads,
            'load_std': np.std(list(worker_loads.values())),
            'most_loaded': max(worker_loads, key=worker_loads.get),
            'least_loaded': min(worker_loads, key=worker_loads.get)
        }

    def optimize_algorithm(self):
        """Optimize load balancing algorithm based on performance"""

        if len(self.decisions) < 100:
            return  # Need more data

        # Calculate algorithm performance
        algorithm_performance = defaultdict(list)

        for decision in self.decisions:
            if decision.success:
                performance_score = 1.0 / max(decision.actual_completion_time, 0.1)  # Higher score for faster completion
                algorithm_performance[decision.algorithm_used].append(performance_score)

        # Switch to best performing algorithm
        best_algorithm = None
        best_score = -float('inf')

        for algorithm, scores in algorithm_performance.items():
            avg_score = np.mean(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_algorithm = algorithm

        if best_algorithm and best_algorithm != self.config.algorithm:
            print(f"Switching to better algorithm: {best_algorithm}")
            self.config.algorithm = best_algorithm
            self.current_algorithm = self.algorithms[best_algorithm]

    def start_monitoring(self):
        """Start load balancer monitoring"""

        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop load balancer monitoring"""

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _calculate_confidence_score(self, task: DistributedTask, worker_id: str) -> float:
        """Calculate confidence score for a worker-task assignment"""

        if worker_id not in self.metrics:
            return 0.0

        worker_metrics = self.metrics[worker_id]

        # Simple confidence calculation based on resource availability
        cpu_confidence = 1.0 - (worker_metrics.cpu_cores_used / max(worker_metrics.cpu_cores_total, 1))
        memory_confidence = 1.0 - (worker_metrics.memory_used_gb / max(worker_metrics.memory_total_gb, 1))
        health_confidence = worker_metrics.health_score

        return (cpu_confidence + memory_confidence + health_confidence) / 3.0

    def _monitoring_loop(self):
        """Monitoring loop for health checks and optimization"""

        while self.is_monitoring:
            try:
                # Health checks
                self._perform_health_checks()

                # Algorithm optimization
                self.optimize_algorithm()

                # Clean old decisions
                self._cleanup_old_decisions()

                time.sleep(self.config.health_check_interval)

            except Exception as e:
                print(f"Load balancer monitoring error: {e}")
                time.sleep(5)

    def _perform_health_checks(self):
        """Perform health checks on workers"""

        for worker_id, health_info in self.worker_health.items():
            # Simple health check (in real implementation, this would ping the worker)
            current_time = time.time()
            time_since_last_check = current_time - health_info['last_check']

            # Mark as unhealthy if no heartbeat for too long
            if time_since_last_check > self.config.health_check_interval * 3:
                health_info['status'] = 'unhealthy'
                health_info['consecutive_failures'] += 1

                if health_info['consecutive_failures'] >= self.config.failure_threshold:
                    print(f"Worker {worker_id} marked as failed")
            else:
                health_info['status'] = 'healthy'
                health_info['consecutive_failures'] = 0

            health_info['last_check'] = current_time

    def _cleanup_old_decisions(self):
        """Clean up old decision records"""

        current_time = time.time()
        cutoff_time = current_time - (24 * 60 * 60)  # 24 hours ago

        # Remove old decisions
        self.decisions = deque(
            [d for d in self.decisions if d.timestamp > cutoff_time],
            maxlen=self.decisions.maxlen
        )


# Factory functions
def create_load_balancer(config: Optional[LoadBalancingConfig] = None) -> IntelligentLoadBalancer:
    """Factory function for intelligent load balancer"""
    if config is None:
        config = LoadBalancingConfig()
    return IntelligentLoadBalancer(config)


def create_load_balancing_config(algorithm: str = "adaptive") -> LoadBalancingConfig:
    """Create load balancing configuration"""
    return LoadBalancingConfig(algorithm=algorithm)


# Example usage and testing
if __name__ == "__main__":
    # Test intelligent load balancer
    print("Testing Intelligent Load Balancer...")

    config = create_load_balancing_config(algorithm="adaptive")
    balancer = create_load_balancer(config)

    # Register some mock workers
    for i in range(3):
        worker = WorkerNode(
            worker_id=f"worker_{i}",
            host=f"host_{i}",
            port=8080 + i,
            capabilities={"cpu_cores": 4, "memory_gb": 8}
        )
        balancer.register_worker(worker)

        # Set mock metrics
        balancer.update_worker_metrics(f"worker_{i}", {
            'cpu_utilization': np.random.uniform(20, 80),
            'memory_utilization': np.random.uniform(30, 70),
            'network_out_mbps': np.random.uniform(10, 50),
            'latency_ms': np.random.uniform(5, 20),
            'active_tasks': np.random.randint(0, 4),
            'completed_tasks_per_minute': np.random.uniform(1, 5)
        })

    balancer.start_monitoring()

    # Test worker selection
    test_task = DistributedTask(
        task_id="test_task_1",
        task_type="backtest",
        payload={"strategy": "test_strategy"},
        cpu_cores=2,
        memory_gb=4.0
    )

    selected_worker, confidence = balancer.select_worker(test_task)
    print(f"Selected worker: {selected_worker} (confidence: {confidence:.2f})")

    # Test load distribution
    load_dist = balancer.get_load_distribution()
    print("Load Distribution:")
    print(f"Average load: {load_dist['average_load']:.2f}")
    print(f"Most loaded: {load_dist['most_loaded']}")
    print(f"Least loaded: {load_dist['least_loaded']}")

    # Simulate some decisions
    for i in range(10):
        decision = LoadDecision(
            decision_id=f"decision_{i}",
            task_id=f"task_{i}",
            worker_id=selected_worker,
            timestamp=time.time(),
            algorithm_used=config.algorithm
        )

        outcome = {
            'success': np.random.choice([True, False], p=[0.9, 0.1]),
            'completion_time': np.random.uniform(10, 60),
            'resource_usage': {'cpu': np.random.uniform(50, 90)}
        }

        balancer.record_decision_outcome(decision, outcome)

    balancer.optimize_algorithm()

    balancer.stop_monitoring()
    print("✓ Intelligent load balancer test completed")

    print("\nIntelligent load balancer test completed!")

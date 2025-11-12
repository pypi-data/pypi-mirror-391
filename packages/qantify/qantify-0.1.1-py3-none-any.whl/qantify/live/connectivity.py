"""Robust market connectivity layer with failover and load balancing."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from collections import defaultdict

from qantify.live.adapters import RestExchangeAdapter, WebsocketExchangeAdapter


logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection states for connectivity management."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAILED = "failed"
    CLOSED = "closed"


class FailoverStrategy(Enum):
    """Failover strategies for connection management."""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    GEOGRAPHIC = "geographic"


@dataclass(slots=True)
class ConnectionEndpoint:
    """Represents a connection endpoint."""
    name: str
    url: str
    region: str = "global"
    priority: int = 1  # Higher = preferred
    weight: float = 1.0  # For load balancing
    healthy: bool = True
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    failed_requests: int = 0


@dataclass(slots=True)
class ConnectionPool:
    """Pool of connection endpoints with failover support."""
    endpoints: List[ConnectionEndpoint] = field(default_factory=list)
    strategy: FailoverStrategy = FailoverStrategy.PRIORITY_BASED
    health_check_interval: int = 30
    max_failures: int = 3
    recovery_time: int = 300  # 5 minutes

    current_index: int = 0
    last_failover: Optional[datetime] = None

    def add_endpoint(self, endpoint: ConnectionEndpoint) -> None:
        """Add an endpoint to the pool."""
        self.endpoints.append(endpoint)
        logger.info(f"Added endpoint: {endpoint.name} ({endpoint.url})")

    def remove_endpoint(self, endpoint_name: str) -> bool:
        """Remove an endpoint from the pool."""
        for i, endpoint in enumerate(self.endpoints):
            if endpoint.name == endpoint_name:
                removed = self.endpoints.pop(i)
                logger.info(f"Removed endpoint: {removed.name}")
                return True
        return False

    def get_healthy_endpoints(self) -> List[ConnectionEndpoint]:
        """Get all healthy endpoints."""
        return [ep for ep in self.endpoints if ep.healthy]

    def select_endpoint(self) -> Optional[ConnectionEndpoint]:
        """Select an endpoint based on strategy."""
        healthy = self.get_healthy_endpoints()
        if not healthy:
            return None

        if self.strategy == FailoverStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy)
        elif self.strategy == FailoverStrategy.PRIORITY_BASED:
            return self._priority_select(healthy)
        elif self.strategy == FailoverStrategy.LOAD_BALANCED:
            return self._load_balanced_select(healthy)
        else:
            return healthy[0]

    def _round_robin_select(self, endpoints: List[ConnectionEndpoint]) -> ConnectionEndpoint:
        """Round-robin endpoint selection."""
        endpoint = endpoints[self.current_index % len(endpoints)]
        self.current_index += 1
        return endpoint

    def _priority_select(self, endpoints: List[ConnectionEndpoint]) -> ConnectionEndpoint:
        """Priority-based endpoint selection."""
        # Sort by priority (highest first)
        sorted_endpoints = sorted(endpoints, key=lambda x: x.priority, reverse=True)
        return sorted_endpoints[0]

    def _load_balanced_select(self, endpoints: List[ConnectionEndpoint]) -> ConnectionEndpoint:
        """Load-balanced endpoint selection."""
        # Simple weighted random selection
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]

        import random
        pick = random.uniform(0, total_weight)
        current_weight = 0

        for endpoint in endpoints:
            current_weight += endpoint.weight
            if current_weight >= pick:
                return endpoint

        return endpoints[0]

    def mark_failed(self, endpoint_name: str) -> None:
        """Mark an endpoint as failed."""
        for endpoint in self.endpoints:
            if endpoint.name == endpoint_name:
                endpoint.consecutive_failures += 1
                endpoint.failed_requests += 1

                if endpoint.consecutive_failures >= self.max_failures:
                    endpoint.healthy = False
                    logger.warning(f"Endpoint {endpoint_name} marked as unhealthy")
                break

    def mark_success(self, endpoint_name: str) -> None:
        """Mark an endpoint as successful."""
        for endpoint in self.endpoints:
            if endpoint.name == endpoint_name:
                endpoint.consecutive_failures = 0
                endpoint.total_requests += 1

                if not endpoint.healthy:
                    endpoint.healthy = True
                    logger.info(f"Endpoint {endpoint_name} recovered")

    async def health_check_all(self) -> None:
        """Perform health checks on all endpoints."""
        for endpoint in self.endpoints:
            await self._health_check_endpoint(endpoint)

    async def _health_check_endpoint(self, endpoint: ConnectionEndpoint) -> None:
        """Health check a specific endpoint."""
        try:
            # Simple connectivity check
            # In practice, this would make actual API calls
            endpoint.last_health_check = datetime.utcnow()

            if endpoint.consecutive_failures >= self.max_failures:
                # Check if enough time has passed for recovery
                if endpoint.last_health_check and endpoint.healthy is False:
                    time_since_failure = (datetime.utcnow() - endpoint.last_health_check).seconds
                    if time_since_failure >= self.recovery_time:
                        # Attempt recovery
                        endpoint.consecutive_failures = 0
                        endpoint.healthy = True
                        logger.info(f"Endpoint {endpoint.name} recovery attempted")

        except Exception as e:
            logger.error(f"Health check failed for {endpoint.name}: {e}")


@dataclass(slots=True)
class CircuitBreaker:
    """Circuit breaker for connection resilience."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Tuple[Exception, ...] = (Exception,)

    state: ConnectionState = ConnectionState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None

    def call(self, func: Callable) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == ConnectionState.OPEN:
            if self._should_attempt_reset():
                self.state = ConnectionState.HALF_OPEN
            else:
                raise CircuitBreakerOpenException()

        try:
            result = func()
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = (datetime.utcnow() - self.last_failure_time).seconds
        return time_since_failure >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == ConnectionState.HALF_OPEN:
            self.state = ConnectionState.CLOSED
            self.failure_count = 0
            logger.info("Circuit breaker reset to closed")

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = ConnectionState.OPEN
            logger.warning("Circuit breaker opened")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


@dataclass(slots=True)
class ConnectivityMetrics:
    """Connectivity performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    circuit_breaker_trips: int = 0
    endpoint_failovers: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ConnectivityManager:
    """Main connectivity manager with failover and load balancing."""

    def __init__(
        self,
        pool: ConnectionPool,
        circuit_breaker: Optional[CircuitBreaker] = None,
        metrics_enabled: bool = True
    ):
        self.pool = pool
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.metrics_enabled = metrics_enabled

        self.metrics = ConnectivityMetrics()
        self.endpoint_adapters: Dict[str, RestExchangeAdapter] = {}
        self.websocket_adapters: Dict[str, WebsocketExchangeAdapter] = {}

        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start connectivity management."""
        if self._running:
            return

        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Connectivity manager started")

    async def stop(self) -> None:
        """Stop connectivity management."""
        self._running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        logger.info("Connectivity manager stopped")

    def add_adapter(self, endpoint_name: str, adapter: RestExchangeAdapter) -> None:
        """Add an adapter for an endpoint."""
        self.endpoint_adapters[endpoint_name] = adapter

    def add_websocket_adapter(self, endpoint_name: str, adapter: WebsocketExchangeAdapter) -> None:
        """Add a WebSocket adapter for an endpoint."""
        self.websocket_adapters[endpoint_name] = adapter

    async def execute_request(
        self,
        request_func: Callable[[RestExchangeAdapter], Any],
        operation_name: str = "request"
    ) -> Any:
        """Execute a request with failover and circuit breaker protection."""
        start_time = time.time()

        def _execute_with_adapter(adapter: RestExchangeAdapter) -> Any:
            return request_func(adapter)

        result = await self._execute_with_failover(_execute_with_adapter, operation_name)

        # Update metrics
        if self.metrics_enabled:
            response_time = (time.time() - start_time) * 1000
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_requests - 1)) + response_time
            ) / self.metrics.total_requests

        return result

    async def _execute_with_failover(
        self,
        request_func: Callable[[RestExchangeAdapter], Any],
        operation_name: str
    ) -> Any:
        """Execute request with automatic failover."""
        max_attempts = len(self.pool.endpoints)
        attempt = 0

        while attempt < max_attempts:
            endpoint = self.pool.select_endpoint()
            if not endpoint:
                raise Exception("No healthy endpoints available")

            adapter = self.endpoint_adapters.get(endpoint.name)
            if not adapter:
                logger.warning(f"No adapter found for endpoint {endpoint.name}")
                self.pool.mark_failed(endpoint.name)
                attempt += 1
                continue

            try:
                # Execute with circuit breaker
                result = self.circuit_breaker.call(lambda: request_func(adapter))

                # Mark success
                self.pool.mark_success(endpoint.name)
                return result

            except Exception as e:
                logger.warning(f"Request failed on {endpoint.name}: {e}")

                # Mark failure
                self.pool.mark_failed(endpoint.name)
                self.metrics.failed_requests += 1

                # Check if circuit breaker opened
                if isinstance(e, CircuitBreakerOpenException):
                    self.metrics.circuit_breaker_trips += 1

                attempt += 1

                # Wait before retry
                if attempt < max_attempts:
                    await asyncio.sleep(0.1 * attempt)  # Exponential backoff

        raise Exception(f"All endpoints failed for {operation_name}")

    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while self._running:
            try:
                await asyncio.sleep(self.pool.health_check_interval)
                await self.pool.health_check_all()
            except Exception as e:
                logger.error(f"Health check loop error: {e}")

    def get_connectivity_status(self) -> Dict[str, Any]:
        """Get overall connectivity status."""
        healthy_endpoints = len(self.pool.get_healthy_endpoints())
        total_endpoints = len(self.pool.endpoints)

        return {
            "healthy_endpoints": healthy_endpoints,
            "total_endpoints": total_endpoints,
            "health_percentage": healthy_endpoints / total_endpoints if total_endpoints > 0 else 0,
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.successful_requests / self.metrics.total_requests
                               if self.metrics.total_requests > 0 else 0,
                "average_response_time": self.metrics.average_response_time,
                "circuit_breaker_trips": self.metrics.circuit_breaker_trips,
                "endpoint_failovers": self.metrics.endpoint_failovers
            }
        }


# Convenience functions for common setups
def create_binance_connectivity() -> ConnectivityManager:
    """Create connectivity manager for Binance."""
    pool = ConnectionPool(strategy=FailoverStrategy.PRIORITY_BASED)

    # Add multiple Binance endpoints for redundancy
    pool.add_endpoint(ConnectionEndpoint(
        name="binance_primary",
        url="https://api.binance.com",
        region="global",
        priority=10
    ))

    pool.add_endpoint(ConnectionEndpoint(
        name="binance_backup",
        url="https://api.binance.us",  # US endpoint
        region="us",
        priority=5
    ))

    manager = ConnectivityManager(pool)
    return manager


def create_alpaca_connectivity(paper: bool = True) -> ConnectivityManager:
    """Create connectivity manager for Alpaca."""
    pool = ConnectionPool(strategy=FailoverStrategy.PRIORITY_BASED)

    base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"

    pool.add_endpoint(ConnectionEndpoint(
        name="alpaca_primary",
        url=base_url,
        region="us",
        priority=10
    ))

    manager = ConnectivityManager(pool)
    return manager


__all__ = [
    "ConnectivityManager",
    "ConnectionPool",
    "ConnectionEndpoint",
    "CircuitBreaker",
    "CircuitBreakerOpenException",
    "ConnectivityMetrics",
    "ConnectionState",
    "FailoverStrategy",
    "create_binance_connectivity",
    "create_alpaca_connectivity"
]

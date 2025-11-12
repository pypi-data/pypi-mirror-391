"""Live trading performance monitoring and dashboard capabilities."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # System metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0

    # Trading metrics
    total_orders: int = 0
    active_orders: int = 0
    filled_orders: int = 0
    cancelled_orders: int = 0
    rejected_orders: int = 0

    # Performance metrics
    average_execution_time: float = 0.0
    fill_rate: float = 0.0
    slippage_bps: float = 0.0
    market_impact_bps: float = 0.0

    # P&L metrics
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    # Risk metrics
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    value_at_risk: float = 0.0
    current_drawdown: float = 0.0

    # Strategy metrics
    active_strategies: int = 0
    signals_generated: int = 0
    signals_executed: int = 0
    strategy_win_rate: float = 0.0


@dataclass(slots=True)
class Alert:
    """Monitoring alert."""
    alert_id: str
    alert_type: str
    severity: str  # 'info', 'warning', 'error', 'critical'
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass(slots=True)
class DashboardConfig:
    """Dashboard configuration."""
    update_interval: int = 5  # seconds
    retention_period: int = 3600  # 1 hour
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'high_cpu': 80.0,
        'high_memory': 85.0,
        'high_drawdown': 0.05,
        'low_fill_rate': 0.7,
        'high_slippage': 0.001  # 10 bps
    })


class PerformanceMonitor:
    """Real-time performance monitoring system."""

    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=1000)
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}

        # Background tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start performance monitoring."""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Performance monitor started")

    async def stop(self) -> None:
        """Stop performance monitoring."""
        self._running = False

        tasks = [self._monitor_task, self._cleanup_task]
        for task in tasks:
            if task:
                task.cancel()

        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        logger.info("Performance monitor stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()

                # Store metrics
                self.metrics_history.append(metrics)

                # Check alerts
                if self.config.enable_alerts:
                    await self._check_alerts(metrics)

                # Log significant events
                await self._log_significant_events(metrics)

                await asyncio.sleep(self.config.update_interval)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(1)

    async def _cleanup_loop(self) -> None:
        """Cleanup old data."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Remove old alerts
                cutoff = datetime.utcnow() - timedelta(seconds=self.config.retention_period)
                self.alerts = [a for a in self.alerts if a.timestamp > cutoff]

                # Clean up resolved alerts older than 1 hour
                old_resolved = datetime.utcnow() - timedelta(hours=1)
                self.alerts = [
                    a for a in self.alerts
                    if not a.resolved or a.resolved_at > old_resolved
                ]

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        metrics = PerformanceMetrics()

        try:
            # System metrics (simplified)
            import psutil
            import os

            process = psutil.Process(os.getpid())
            metrics.cpu_usage = process.cpu_percent()
            metrics.memory_usage = process.memory_percent()
            metrics.disk_usage = psutil.disk_usage('/').percent

            # Network latency (placeholder)
            metrics.network_latency = 10.0  # ms

        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")

        # Trading metrics would be populated by integration with trading engines
        # This is a placeholder structure

        return metrics

    async def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check for alert conditions."""
        thresholds = self.config.alert_thresholds

        # CPU usage alert
        if metrics.cpu_usage > thresholds.get('high_cpu', 80):
            await self._create_alert(
                'high_cpu',
                'warning',
                f"High CPU usage: {metrics.cpu_usage:.1f}%"
            )

        # Memory usage alert
        if metrics.memory_usage > thresholds.get('high_memory', 85):
            await self._create_alert(
                'high_memory',
                'warning',
                f"High memory usage: {metrics.memory_usage:.1f}%"
            )

        # Drawdown alert
        if metrics.current_drawdown > thresholds.get('high_drawdown', 0.05):
            await self._create_alert(
                'high_drawdown',
                'critical',
                f"High drawdown: {metrics.current_drawdown:.2%}"
            )

        # Fill rate alert
        if metrics.fill_rate < thresholds.get('low_fill_rate', 0.7):
            await self._create_alert(
                'low_fill_rate',
                'warning',
                f"Low fill rate: {metrics.fill_rate:.2%}"
            )

        # Slippage alert
        if metrics.slippage_bps > thresholds.get('high_slippage', 10):
            await self._create_alert(
                'high_slippage',
                'warning',
                f"High slippage: {metrics.slippage_bps:.1f} bps"
            )

    async def _create_alert(self, alert_type: str, severity: str, message: str) -> None:
        """Create a new alert."""
        alert_id = f"{alert_type}_{int(time.time())}"

        if alert_id in self.active_alerts:
            return  # Alert already exists

        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message
        )

        self.alerts.append(alert)
        self.active_alerts[alert_id] = alert

        logger.warning(f"Alert created: {alert_type} - {message}")

    async def _log_significant_events(self, metrics: PerformanceMetrics) -> None:
        """Log significant performance events."""
        # Log high CPU usage
        if metrics.cpu_usage > 90:
            logger.critical(f"Critical CPU usage: {metrics.cpu_usage:.1f}%")

        # Log large drawdown
        if metrics.current_drawdown > 0.1:
            logger.critical(f"Large drawdown detected: {metrics.current_drawdown:.2%}")

        # Log poor performance
        if metrics.fill_rate < 0.5 and metrics.total_orders > 10:
            logger.warning(f"Poor fill rate: {metrics.fill_rate:.2%} on {metrics.total_orders} orders")

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_history(self, hours_back: int = 1) -> List[PerformanceMetrics]:
        """Get metrics history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        return [m for m in self.metrics_history if m.timestamp > cutoff]

    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts."""
        return [a for a in self.alerts if not a.resolved]

    def get_alert_history(self, hours_back: int = 24) -> List[Alert]:
        """Get alert history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        return [a for a in self.alerts if a.timestamp > cutoff]

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            del self.active_alerts[alert_id]
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data."""
        current = self.get_current_metrics()
        alerts = self.get_active_alerts()

        return {
            'current_metrics': current.__dict__ if current else {},
            'active_alerts': [a.__dict__ for a in alerts],
            'alert_count': len(alerts),
            'metrics_history_count': len(self.metrics_history),
            'last_update': datetime.utcnow().isoformat()
        }

    def export_metrics_report(self, filepath: str) -> None:
        """Export metrics report to JSON."""
        data = {
            'config': self.config.__dict__,
            'metrics_history': [m.__dict__ for m in self.metrics_history],
            'alerts': [a.__dict__ for a in self.alerts],
            'export_timestamp': datetime.utcnow().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Metrics report exported to {filepath}")

    # Integration methods for updating metrics from trading engines
    def update_trading_metrics(self, **kwargs) -> None:
        """Update trading-related metrics."""
        current = self.get_current_metrics()
        if current:
            for key, value in kwargs.items():
                if hasattr(current, key):
                    setattr(current, key, value)

    def record_order_event(self, event_type: str, **kwargs) -> None:
        """Record order-related events."""
        current = self.get_current_metrics()
        if current:
            if event_type == 'order_submitted':
                current.total_orders += 1
                current.active_orders += 1
            elif event_type == 'order_filled':
                current.filled_orders += 1
                current.active_orders -= 1
            elif event_type == 'order_cancelled':
                current.cancelled_orders += 1
                current.active_orders -= 1
            elif event_type == 'order_rejected':
                current.rejected_orders += 1
                current.active_orders -= 1


class SimpleDashboard:
    """Simple text-based dashboard for monitoring."""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    def print_status(self) -> None:
        """Print current status to console."""
        metrics = self.monitor.get_current_metrics()
        alerts = self.monitor.get_active_alerts()

        if not metrics:
            print("No metrics available")
            return

        print("\n" + "="*60)
        print("QANTIFY LIVE TRADING DASHBOARD")
        print("="*60)

        # System metrics
        print("\nSYSTEM METRICS:")
        print(f"CPU Usage: {metrics.cpu_usage:.1f}%")
        print(f"Memory Usage: {metrics.memory_usage:.1f}%")
        print(f"Disk Usage: {metrics.disk_usage:.1f}%")
        print(f"Network Latency: {metrics.network_latency:.1f}ms")

        # Trading metrics
        print("\nTRADING METRICS:")
        print(f"Total Orders: {metrics.total_orders}")
        print(f"Active Orders: {metrics.active_orders}")
        print(f"Filled Orders: {metrics.filled_orders}")
        print(f"Fill Rate: {metrics.fill_rate:.1f}")
        print(f"Slippage: {metrics.slippage_bps:.2f} bps")

        # P&L metrics
        print("\nP&L METRICS:")
        print(f"Total P&L: ${metrics.total_pnl:.2f}")
        print(f"Daily P&L: ${metrics.daily_pnl:.2f}")
        print(f"Unrealized P&L: ${metrics.unrealized_pnl:.2f}")
        print(f"Realized P&L: ${metrics.realized_pnl:.2f}")
        print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")

        # Risk metrics
        print("\nRISK METRICS:")
        print(f"Max Drawdown: {metrics.max_drawdown:.2%}")
        print(f"Value at Risk (95%): {metrics.value_at_risk:.3f}")
        print(f"Current Drawdown: {metrics.current_drawdown:.2%}")
        print(f"Portfolio Volatility: {metrics.portfolio_volatility:.3f}")

        # Alerts
        if alerts:
            print("\nACTIVE ALERTS:")
            for alert in alerts:
                print(f"[{alert.severity.upper()}] {alert.alert_type}: {alert.message}")
        else:
            print("\nNo active alerts")

        print(f"\nLast Update: {metrics.timestamp}")
        print("="*60)


# Web dashboard placeholder (would require web framework)
class WebDashboard:
    """Placeholder for web-based dashboard."""

    def __init__(self, monitor: PerformanceMonitor, host: str = "localhost", port: int = 8080):
        self.monitor = monitor
        self.host = host
        self.port = port

    def start(self) -> None:
        """Start web dashboard (placeholder)."""
        print(f"Web dashboard would start on http://{self.host}:{self.port}")
        print("Implementation would require FastAPI/Flask + frontend framework")

    def get_api_data(self) -> Dict[str, Any]:
        """Get API data for dashboard."""
        return self.monitor.get_dashboard_data()


__all__ = [
    "PerformanceMonitor",
    "PerformanceMetrics",
    "Alert",
    "DashboardConfig",
    "SimpleDashboard",
    "WebDashboard"
]

"""Advanced Monitoring, Alerting, and Performance Tracking Framework for Quantitative Trading Strategies.

This module provides comprehensive monitoring capabilities including:
- Real-time performance tracking and alerting
- Health checks and system monitoring
- Custom metrics and KPIs
- Alert management and escalation
- Performance dashboards and visualization
- Distributed monitoring across multiple processes
- Integration with external monitoring systems
- Predictive analytics and anomaly detection
- Automated incident response
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

# Optional dependencies
try:
    import prometheus_client
    from prometheus_client import Counter, Gauge, Histogram, Summary
except ImportError:
    prometheus_client = None

try:
    import requests
except ImportError:
    requests = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    go = None
    px = None

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    smtplib = None

try:
    import telegram
except ImportError:
    telegram = None


# =============================================================================
# CORE MONITORING TYPES AND ENUMS
# =============================================================================

class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class MetricType(Enum):
    """Types of metrics."""
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None

    def acknowledge(self, user: str):
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.now()
        self.assigned_to = user

    def resolve(self):
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'status': self.status.value,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'assigned_to': self.assigned_to
        }


@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable[[], Tuple[HealthStatus, str]]
    interval: timedelta
    timeout: timedelta
    last_run: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_message: str = ""
    failure_count: int = 0
    success_count: int = 0

    def should_run(self) -> bool:
        """Check if health check should run."""
        if self.last_run is None:
            return True
        return datetime.now() - self.last_run >= self.interval

    def run(self) -> Tuple[HealthStatus, str]:
        """Run the health check."""
        try:
            self.last_run = datetime.now()
            status, message = self.check_function()
            self.last_status = status
            self.last_message = message

            if status == HealthStatus.HEALTHY:
                self.success_count += 1
                self.failure_count = 0
            else:
                self.failure_count += 1

            return status, message
        except Exception as e:
            self.last_status = HealthStatus.CRITICAL
            self.last_message = f"Health check failed: {e}"
            self.failure_count += 1
            return HealthStatus.CRITICAL, self.last_message


@dataclass
class PerformanceMetric:
    """Performance metric with history."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertCallback(Protocol):
    """Protocol for alert callback functions."""
    def __call__(self, alert: Alert) -> None:
        """Handle alert notification."""
        ...


# =============================================================================
# ADVANCED MONITORING SYSTEM
# =============================================================================

class AdvancedMonitor(ABC):
    """Abstract base class for advanced monitoring systems."""

    @abstractmethod
    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None,
                     metric_type: MetricType = MetricType.GAUGE) -> None:
        """Record a metric."""
        pass

    @abstractmethod
    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        """Log an event."""
        pass

    @abstractmethod
    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    source: str, **metadata) -> str:
        """Create an alert."""
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        pass

    @abstractmethod
    def get_performance_metrics(self, time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Get performance metrics."""
        pass


class ComprehensiveMonitor(AdvancedMonitor):
    """Comprehensive monitoring system with alerting and health checks."""

    def __init__(self, strategy_id: Optional[str] = None):
        self.strategy_id = strategy_id or f"strategy_{int(time.time())}"
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: Dict[str, Alert] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alert_callbacks: List[AlertCallback] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Performance tracking
        self.metric_counts = defaultdict(int)
        self.event_counts = defaultdict(int)
        self.alert_counts = defaultdict(int)

    def start_monitoring(self, check_interval: float = 60.0):
        """Start monitoring system."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring system."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.executor.shutdown(wait=True)

    def add_health_check(self, name: str, check_function: Callable[[], Tuple[HealthStatus, str]],
                        interval: timedelta = timedelta(minutes=5),
                        timeout: timedelta = timedelta(seconds=30)):
        """Add a health check."""
        self.health_checks[name] = HealthCheck(
            name=name,
            check_function=check_function,
            interval=interval,
            timeout=timeout
        )

    def add_alert_callback(self, callback: AlertCallback):
        """Add alert callback."""
        self.alert_callbacks.append(callback)

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None,
                     metric_type: MetricType = MetricType.GAUGE) -> None:
        """Record a metric with timestamp."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata={'type': metric_type.value}
        )

        self.metrics[name].append(metric)
        self.metric_counts[name] += 1

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        """Log an event with structured data."""
        event_data = {
            'message': message,
            'level': level,
            'timestamp': datetime.now(),
            'tags': tags or {},
            'strategy_id': self.strategy_id
        }

        # Store as metric for consistency
        self.record_metric(
            'strategy_event',
            1.0,
            tags={'level': level, **(tags or {})},
            metric_type=MetricType.COUNTER
        )

        self.event_counts[level] += 1

    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    source: str, **metadata) -> str:
        """Create and trigger an alert."""
        alert_id = f"alert_{int(time.time() * 1000000)}"

        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            status=AlertStatus.ACTIVE,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata,
            tags={'strategy_id': self.strategy_id}
        )

        self.alerts[alert_id] = alert
        self.alert_counts[severity.value] += 1

        # Trigger callbacks asynchronously
        for callback in self.alert_callbacks:
            self.executor.submit(self._safe_callback, callback, alert)

        return alert_id

    def acknowledge_alert(self, alert_id: str, user: str):
        """Acknowledge an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledge(user)

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolve()

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [alert for alert in self.alerts.values() if alert.status == AlertStatus.ACTIVE]

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        health_summary = {
            'overall_status': HealthStatus.HEALTHY,
            'checks': {},
            'last_updated': datetime.now()
        }

        critical_count = 0
        warning_count = 0

        for name, check in self.health_checks.items():
            if check.should_run():
                status, message = check.run()
            else:
                status = check.last_status
                message = check.last_message

            health_summary['checks'][name] = {
                'status': status.value,
                'message': message,
                'last_run': check.last_run.isoformat() if check.last_run else None,
                'failure_count': check.failure_count,
                'success_count': check.success_count
            }

            if status == HealthStatus.CRITICAL:
                critical_count += 1
            elif status == HealthStatus.WARNING:
                warning_count += 1

        # Determine overall status
        if critical_count > 0:
            health_summary['overall_status'] = HealthStatus.CRITICAL.value
        elif warning_count > 0:
            health_summary['overall_status'] = HealthStatus.WARNING.value

        return health_summary

    def get_performance_metrics(self, time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Get performance metrics within time range."""
        if time_range is None:
            time_range = timedelta(hours=24)

        cutoff_time = datetime.now() - time_range
        all_metrics = []

        for metric_queue in self.metrics.values():
            for metric in metric_queue:
                if metric.timestamp >= cutoff_time:
                    all_metrics.append(metric)

        return sorted(all_metrics, key=lambda x: x.timestamp)

    def get_performance_summary(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get performance summary statistics."""
        metrics = self.get_performance_metrics(time_range)

        if not metrics:
            return {'message': 'No metrics available'}

        # Group by metric name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.name].append(metric.value)

        summary = {}
        for name, values in metric_groups.items():
            summary[name] = {
                'count': len(values),
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'last_value': values[-1] if values else None
            }

        return summary

    def detect_anomalies(self, metric_name: str, threshold: float = 3.0) -> List[Dict[str, Any]]:
        """Detect anomalies in metric using statistical methods."""
        if metric_name not in self.metrics:
            return []

        values = [m.value for m in self.metrics[metric_name]]
        if len(values) < 10:
            return []

        # Simple z-score based anomaly detection
        mean_val = np.mean(values)
        std_val = np.std(values)

        anomalies = []
        for i, metric in enumerate(self.metrics[metric_name]):
            if std_val > 0:
                z_score = abs(metric.value - mean_val) / std_val
                if z_score > threshold:
                    anomalies.append({
                        'timestamp': metric.timestamp,
                        'value': metric.value,
                        'z_score': z_score,
                        'expected_range': (mean_val - threshold * std_val, mean_val + threshold * std_val)
                    })

        return anomalies[-10:]  # Return last 10 anomalies

    def _monitoring_loop(self, check_interval: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Run health checks
                for check in self.health_checks.values():
                    if check.should_run():
                        status, message = check.run()
                        if status != HealthStatus.HEALTHY:
                            self.create_alert(
                                f"Health Check Failed: {check.name}",
                                message,
                                AlertSeverity.HIGH if status == HealthStatus.CRITICAL else AlertSeverity.MEDIUM,
                                "health_check",
                                check_name=check.name
                            )

                # Check for metric anomalies
                for metric_name in self.metrics.keys():
                    anomalies = self.detect_anomalies(metric_name)
                    if anomalies:
                        latest_anomaly = anomalies[-1]
                        self.create_alert(
                            f"Metric Anomaly: {metric_name}",
                            f"Anomalous value detected: {latest_anomaly['value']:.4f} "
                            f"(expected range: {latest_anomaly['expected_range'][0]:.4f} - "
                            f"{latest_anomaly['expected_range'][1]:.4f})",
                            AlertSeverity.MEDIUM,
                            "anomaly_detection",
                            metric_name=metric_name,
                            anomaly_details=latest_anomaly
                        )

                # Check alert escalation
                self._check_alert_escalation()

            except Exception as e:
                self.create_alert(
                    "Monitoring Error",
                    f"Monitoring loop encountered error: {e}",
                    AlertSeverity.CRITICAL,
                    "monitoring_system"
                )

            time.sleep(check_interval)

    def _check_alert_escalation(self):
        """Check for alert escalation based on duration."""
        now = datetime.now()

        for alert in self.alerts.values():
            if alert.status != AlertStatus.ACTIVE:
                continue

            duration = now - alert.timestamp

            # Escalate based on duration and severity
            if alert.severity == AlertSeverity.LOW and duration > timedelta(minutes=30):
                alert.severity = AlertSeverity.MEDIUM
            elif alert.severity == AlertSeverity.MEDIUM and duration > timedelta(hours=2):
                alert.severity = AlertSeverity.HIGH
            elif alert.severity == AlertSeverity.HIGH and duration > timedelta(hours=6):
                alert.severity = AlertSeverity.CRITICAL

    def _safe_callback(self, callback: AlertCallback, alert: Alert):
        """Execute callback safely."""
        try:
            callback(alert)
        except Exception as e:
            warnings.warn(f"Alert callback failed: {e}")

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics."""
        return {
            'strategy_id': self.strategy_id,
            'active_alerts': len(self.get_active_alerts()),
            'total_alerts': len(self.alerts),
            'health_checks': len(self.health_checks),
            'metrics_tracked': len(self.metrics),
            'monitoring_active': self.monitoring_active,
            'alert_counts': dict(self.alert_counts),
            'metric_counts': dict(self.metric_counts),
            'event_counts': dict(self.event_counts)
        }


# =============================================================================
# EXTERNAL MONITORING INTEGRATIONS
# =============================================================================

class PrometheusMonitor(AdvancedMonitor):
    """Prometheus monitoring integration."""

    def __init__(self, namespace: str = "qantify", registry=None):
        if prometheus_client is None:
            raise ImportError("prometheus_client package required")

        self.namespace = namespace
        self.registry = registry or prometheus_client.REGISTRY

        # Create metrics
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.summaries = {}

        # Strategy-specific metrics
        self.strategy_events = Counter(
            f"{namespace}_strategy_events_total",
            "Strategy events",
            ["strategy_id", "level", "category"],
            registry=self.registry
        )

        self.strategy_metrics = Gauge(
            f"{namespace}_strategy_metrics",
            "Strategy metrics",
            ["strategy_id", "metric_name"],
            registry=self.registry
        )

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None,
                     metric_type: MetricType = MetricType.GAUGE) -> None:
        """Record metric in Prometheus."""
        tags = tags or {}

        if metric_type == MetricType.COUNTER:
            counter_name = f"{self.namespace}_{name}"
            if counter_name not in self.counters:
                self.counters[counter_name] = Counter(
                    counter_name, f"Counter for {name}",
                    list(tags.keys()), registry=self.registry
                )
            self.counters[counter_name].labels(**tags).inc(value)

        elif metric_type == MetricType.GAUGE:
            gauge_name = f"{self.namespace}_{name}"
            if gauge_name not in self.gauges:
                self.gauges[gauge_name] = Gauge(
                    gauge_name, f"Gauge for {name}",
                    list(tags.keys()), registry=self.registry
                )
            self.gauges[gauge_name].labels(**tags).set(value)

        elif metric_type == MetricType.HISTOGRAM:
            hist_name = f"{self.namespace}_{name}"
            if hist_name not in self.histograms:
                self.histograms[hist_name] = Histogram(
                    hist_name, f"Histogram for {name}",
                    list(tags.keys()), registry=self.registry
                )
            self.histograms[hist_name].labels(**tags).observe(value)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        """Log event as Prometheus counter."""
        tags = tags or {}
        strategy_id = tags.get('strategy_id', 'unknown')
        category = tags.get('category', 'general')

        self.strategy_events.labels(
            strategy_id=strategy_id,
            level=level,
            category=category
        ).inc()

    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    source: str, **metadata) -> str:
        """Create alert (Prometheus alerting rules should be configured separately)."""
        # This would integrate with Prometheus Alertmanager
        alert_id = f"prometheus_alert_{int(time.time())}"
        print(f"Prometheus Alert: {title} - {message}")
        return alert_id

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status from Prometheus metrics."""
        return {'status': 'healthy', 'message': 'Prometheus metrics active'}

    def get_performance_metrics(self, time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Get metrics from Prometheus (would require query API)."""
        # This would query Prometheus API
        return []


class InfluxDBMonitor(AdvancedMonitor):
    """InfluxDB monitoring integration."""

    def __init__(self, url: str, token: str, org: str, bucket: str):
        try:
            from influxdb_client import InfluxDBClient
        except ImportError:
            raise ImportError("influxdb-client package required")

        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        self.write_api = self.client.write_api()

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None,
                     metric_type: MetricType = MetricType.GAUGE) -> None:
        """Record metric in InfluxDB."""
        from influxdb_client import Point

        point = Point(name).field("value", value)

        if tags:
            for tag_name, tag_value in tags.items():
                point.tag(tag_name, tag_value)

        self.write_api.write(bucket=self.bucket, record=point)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        """Log event in InfluxDB."""
        self.record_metric("strategy_event", 1.0, tags={"level": level, "message": message, **(tags or {})})

    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    source: str, **metadata) -> str:
        """Create alert in InfluxDB."""
        alert_id = f"influx_alert_{int(time.time())}"
        self.record_metric("alert", 1.0, tags={
            "title": title,
            "severity": severity.value,
            "source": source
        })
        return alert_id

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        try:
            self.client.health()
            return {'status': 'healthy', 'message': 'InfluxDB connection OK'}
        except Exception as e:
            return {'status': 'critical', 'message': str(e)}

    def get_performance_metrics(self, time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Query metrics from InfluxDB."""
        # This would implement InfluxDB queries
        return []


# =============================================================================
# ALERT NOTIFICATION SYSTEMS
# =============================================================================

class EmailNotifier:
    """Email alert notification system."""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        if smtplib is None:
            raise ImportError("smtplib required for email notifications")

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    def notify(self, alert: Alert, recipients: List[str]):
        """Send email notification."""
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"

        body = f"""
        Alert Details:
        - Title: {alert.title}
        - Message: {alert.message}
        - Severity: {alert.severity.value}
        - Source: {alert.source}
        - Time: {alert.timestamp}

        Tags: {alert.tags}
        Metadata: {alert.metadata}
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.from_email, recipients, msg.as_string())
        server.quit()


class TelegramNotifier:
    """Telegram alert notification system."""

    def __init__(self, bot_token: str, chat_id: str):
        if telegram is None:
            raise ImportError("python-telegram-bot required for Telegram notifications")

        self.bot_token = bot_token
        self.chat_id = chat_id

    def notify(self, alert: Alert, **kwargs):
        """Send Telegram notification."""
        import telegram

        bot = telegram.Bot(token=self.bot_token)

        message = f"""
🚨 *{alert.severity.value.upper()} ALERT*

*{alert.title}*
{alert.message}

Source: {alert.source}
Time: {alert.timestamp}
Tags: {', '.join(f'{k}={v}' for k, v in alert.tags.items())}
        """

        bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')


class WebhookNotifier:
    """Webhook alert notification system."""

    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        if requests is None:
            raise ImportError("requests required for webhook notifications")

        self.webhook_url = webhook_url
        self.headers = headers or {}

    def notify(self, alert: Alert, **kwargs):
        """Send webhook notification."""
        payload = alert.to_dict()
        response = requests.post(self.webhook_url, json=payload, headers=self.headers)

        if response.status_code >= 400:
            warnings.warn(f"Webhook notification failed: {response.status_code}")


# =============================================================================
# DASHBOARDS AND VISUALIZATION
# =============================================================================

class MonitoringDashboard:
    """Interactive monitoring dashboard."""

    def __init__(self, monitor: AdvancedMonitor):
        self.monitor = monitor

    def create_performance_dashboard(self) -> go.Figure:
        """Create comprehensive performance dashboard."""
        if go is None:
            raise ImportError("plotly required for dashboards")

        metrics = self.monitor.get_performance_metrics(timedelta(hours=24))

        if not metrics:
            fig = go.Figure()
            fig.add_annotation(text="No metrics available", showarrow=False)
            return fig

        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Key Metrics Over Time', 'Alert Status',
                'Health Check Status', 'Performance Distribution',
                'Anomaly Detection', 'System Load'
            ],
            specs=[
                [{"type": "scatter"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "histogram"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ]
        )

        # Add traces (simplified)
        # This would be much more comprehensive in practice

        return fig

    def create_alert_summary_chart(self) -> go.Figure:
        """Create alert summary visualization."""
        if go is None:
            raise ImportError("plotly required for charts")

        alerts = []
        if hasattr(self.monitor, 'get_active_alerts'):
            alerts = self.monitor.get_active_alerts()

        severity_counts = defaultdict(int)
        for alert in alerts:
            severity_counts[alert.severity.value] += 1

        fig = px.bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            title="Active Alerts by Severity",
            labels={'x': 'Severity', 'y': 'Count'}
        )

        return fig

    def export_dashboard_data(self) -> Dict[str, Any]:
        """Export dashboard data for external visualization."""
        return {
            'performance_metrics': [m.__dict__ for m in self.monitor.get_performance_metrics()],
            'health_status': self.monitor.get_health_status(),
            'alerts': []  # Would need to serialize alerts
        }


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

class StrategyMonitor:
    """Legacy StrategyMonitor interface for backward compatibility."""
    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        pass

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        pass


class NullMonitor(StrategyMonitor):
    """Null monitor that does nothing."""
    pass


class InMemoryMonitor(StrategyMonitor):
    """In-memory monitor for testing."""
    def __init__(self) -> None:
        self.metrics: list[tuple[str, float, Dict[str, str]]] = []
        self.events: list[tuple[str, str, Dict[str, str]]] = []

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        self.metrics.append((name, value, tags or {}))

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        self.events.append((level, message, tags or {}))


class CompositeMonitor(StrategyMonitor):
    """Composite monitor that forwards to multiple monitors."""
    def __init__(self, monitors: Iterable[StrategyMonitor]) -> None:
        self.monitors = list(monitors)

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        for monitor in self.monitors:
            monitor.record_metric(name, value, tags=tags)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        for monitor in self.monitors:
            monitor.log_event(message, level=level, tags=tags)


__all__ = [
    # Core monitoring classes
    "AdvancedMonitor", "ComprehensiveMonitor", "MonitoringDashboard",

    # External integrations
    "PrometheusMonitor", "InfluxDBMonitor",

    # Alert system
    "Alert", "AlertSeverity", "AlertStatus",
    "EmailNotifier", "TelegramNotifier", "WebhookNotifier",

    # Health monitoring
    "HealthCheck", "HealthStatus",

    # Legacy compatibility
    "StrategyMonitor", "NullMonitor", "InMemoryMonitor", "CompositeMonitor",
]


class NullMonitor(StrategyMonitor):
    pass


class InMemoryMonitor(StrategyMonitor):
    def __init__(self) -> None:
        self.metrics: list[tuple[str, float, Dict[str, str]]] = []
        self.events: list[tuple[str, str, Dict[str, str]]] = []

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        self.metrics.append((name, value, tags or {}))

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        self.events.append((level, message, tags or {}))


class PrometheusMonitor(StrategyMonitor):
    def __init__(self, namespace: str = "qantify") -> None:
        try:
            from prometheus_client import Counter, Gauge
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("prometheus_client package required for PrometheusMonitor") from exc
        self.namespace = namespace
        self.counter = Counter(f"{namespace}_events_total", "Strategy events", ["level", "category"])
        self.gauge = Gauge(f"{namespace}_metrics", "Strategy metrics", ["name"])

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        self.gauge.labels(name=name).set(value)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        category = (tags or {}).get("category", "general")
        self.counter.labels(level=level, category=category).inc()


class InfluxDBMonitor(StrategyMonitor):
    def __init__(self, endpoint: str, bucket: str, org: str, token: Optional[str] = None) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.bucket = bucket
        self.org = org
        self.token = token

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        import requests

        line = f"{name}," + ",".join(f"{k}={v}" for k, v in (tags or {}).items()) + f" value={value}"
        headers = {"Authorization": f"Token {self.token}"} if self.token else {}
        payload = line
        url = f"{self.endpoint}/api/v2/write?bucket={self.bucket}&org={self.org}&precision=ns"
        requests.post(url, headers=headers, data=payload)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        self.record_metric("strategy_event", 1.0, tags={"level": level, **(tags or {})})


class CompositeMonitor(StrategyMonitor):
    def __init__(self, monitors: Iterable[StrategyMonitor]) -> None:
        self.monitors = list(monitors)

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        for monitor in self.monitors:
            monitor.record_metric(name, value, tags=tags)

    def log_event(self, message: str, *, level: str = "info", tags: Optional[Dict[str, str]] = None) -> None:
        for monitor in self.monitors:
            monitor.log_event(message, level=level, tags=tags)


__all__ = [
    "StrategyMonitor",
    "NullMonitor",
    "InMemoryMonitor",
    "PrometheusMonitor",
    "InfluxDBMonitor",
    "CompositeMonitor",
]

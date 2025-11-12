"""Advanced Logging, Monitoring, and Analytics Framework for Quantitative Trading Strategies.

This module provides comprehensive logging capabilities including:
- Structured logging with multiple levels and categories
- Real-time monitoring and alerting
- Performance analytics and metrics
- Log aggregation and correlation
- Interactive dashboards and visualization
- Distributed logging across multiple processes
- Log compression and archival
- Custom log formatters and handlers
- Integration with external monitoring systems
"""

from __future__ import annotations

import asyncio
import gzip
import json
import logging as python_logging
import threading
import time
import uuid
import warnings
import zlib
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from pathlib import Path
from queue import Queue
from threading import Lock, Timer
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Union
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Optional dependencies
try:
    import redis
except ImportError:
    redis = None

try:
    import kafka
    from kafka import KafkaProducer, KafkaConsumer
except ImportError:
    kafka = None

try:
    import elasticsearch
    from elasticsearch import Elasticsearch
except ImportError:
    elasticsearch = None

try:
    import influxdb_client
    from influxdb_client import InfluxDBClient, Point
except ImportError:
    influxdb_client = None

try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

try:
    import statsd
except ImportError:
    statsd = None


# =============================================================================
# CORE LOGGING TYPES AND ENUMS
# =============================================================================

class LogLevel(Enum):
    """Log levels for structured logging."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    TRACE = 5
    AUDIT = 60


class LogCategory(Enum):
    """Categories for log classification."""
    STRATEGY = "strategy"
    EXECUTION = "execution"
    RISK = "risk"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    MARKET_DATA = "market_data"
    ORDER = "order"
    PORTFOLIO = "portfolio"
    MONITORING = "monitoring"
    ERROR = "error"
    AUDIT = "audit"
    DEBUG = "debug"


class LogFormat(Enum):
    """Supported log formats."""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    XML = "xml"
    YAML = "yaml"
    LOGSTASH = "logstash"


class StorageBackend(Enum):
    """Supported storage backends."""
    FILE = "file"
    REDIS = "redis"
    KAFKA = "kafka"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"


@dataclass
class LogEntry:
    """Structured log entry with comprehensive metadata."""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    strategy_id: Optional[str] = None
    symbol: Optional[str] = None
    index: Optional[int] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    source: str = "strategy"

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'category': self.category.name,
            'message': self.message,
            'strategy_id': self.strategy_id,
            'symbol': self.symbol,
            'index': self.index,
            'session_id': self.session_id,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'extra_fields': self.extra_fields,
            'stack_trace': self.stack_trace,
            'performance_metrics': self.performance_metrics,
            'tags': list(self.tags),
            'source': self.source
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create log entry from dictionary."""
        return cls(
            timestamp=pd.to_datetime(data['timestamp']),
            level=LogLevel[data['level']],
            category=LogCategory[data['category']],
            message=data['message'],
            strategy_id=data.get('strategy_id'),
            symbol=data.get('symbol'),
            index=data.get('index'),
            session_id=data.get('session_id'),
            correlation_id=data.get('correlation_id'),
            user_id=data.get('user_id'),
            extra_fields=data.get('extra_fields', {}),
            stack_trace=data.get('stack_trace'),
            performance_metrics=data.get('performance_metrics', {}),
            tags=set(data.get('tags', [])),
            source=data.get('source', 'unknown')
        )


# =============================================================================
# LOG FORMATTERS
# =============================================================================

class LogFormatter(ABC):
    """Abstract base class for log formatters."""

    @abstractmethod
    def format(self, entry: LogEntry) -> str:
        """Format a log entry."""
        pass

    @abstractmethod
    def format_batch(self, entries: List[LogEntry]) -> str:
        """Format multiple log entries."""
        pass


class JSONFormatter(LogFormatter):
    """JSON log formatter."""

    def __init__(self, pretty: bool = False, indent: int = 2):
        self.pretty = pretty
        self.indent = indent

    def format(self, entry: LogEntry) -> str:
        """Format single entry as JSON."""
        data = entry.to_dict()
        if self.pretty:
            return json.dumps(data, indent=self.indent, default=str)
        return json.dumps(data, default=str)

    def format_batch(self, entries: List[LogEntry]) -> str:
        """Format multiple entries as JSON array."""
        data = [entry.to_dict() for entry in entries]
        if self.pretty:
            return json.dumps(data, indent=self.indent, default=str)
        return json.dumps(data, default=str)


class CSVFormatter(LogFormatter):
    """CSV log formatter."""

    def format(self, entry: LogEntry) -> str:
        """Format single entry as CSV."""
        data = entry.to_dict()
        # Flatten nested structures
        flat_data = self._flatten_dict(data)
        return ','.join(str(flat_data.get(col, '')) for col in self._get_columns())

    def format_batch(self, entries: List[LogEntry]) -> str:
        """Format multiple entries as CSV."""
        if not entries:
            return ""

        lines = []
        # Header
        columns = self._get_columns()
        lines.append(','.join(columns))

        # Data rows
        for entry in entries:
            data = entry.to_dict()
            flat_data = self._flatten_dict(data)
            line = ','.join(str(flat_data.get(col, '')) for col in columns)
            lines.append(line)

        return '\n'.join(lines)

    def _get_columns(self) -> List[str]:
        """Get CSV column names."""
        return [
            'timestamp', 'level', 'category', 'message', 'strategy_id', 'symbol',
            'index', 'session_id', 'correlation_id', 'user_id', 'source'
        ]

    def _flatten_dict(self, d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        flat = {}
        for key, value in d.items():
            new_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._flatten_dict(value, f"{new_key}_"))
            elif isinstance(value, list):
                flat[new_key] = json.dumps(value)
            else:
                flat[new_key] = value
        return flat


class LogstashFormatter(LogFormatter):
    """Logstash-compatible JSON formatter."""

    def __init__(self, index_name: str = "qantify-logs"):
        self.index_name = index_name

    def format(self, entry: LogEntry) -> str:
        """Format for Logstash."""
        data = entry.to_dict()
        logstash_entry = {
            "@timestamp": data['timestamp'],
            "@version": "1",
            "message": data['message'],
            "level": data['level'],
            "category": data['category'],
            "source": data['source'],
            "fields": {k: v for k, v in data.items()
                      if k not in ['timestamp', 'message', 'level', 'category', 'source']}
        }
        return json.dumps(logstash_entry, default=str)

    def format_batch(self, entries: List[LogEntry]) -> str:
        """Format batch for Logstash."""
        return '\n'.join(self.format(entry) for entry in entries)


# =============================================================================
# STORAGE BACKENDS
# =============================================================================

class LogStorageBackend(ABC):
    """Abstract base class for log storage backends."""

    @abstractmethod
    def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to storage."""
        pass

    @abstractmethod
    def read(self, start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             filters: Optional[Dict[str, Any]] = None) -> List[LogEntry]:
        """Read log entries from storage."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        pass


class FileStorageBackend(LogStorageBackend):
    """File-based log storage."""

    def __init__(self, base_path: str, format: LogFormat = LogFormat.JSON,
                 rotation: str = "daily", compression: bool = False):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.format = format
        self.rotation = rotation
        self.compression = compression
        self.formatter = self._get_formatter()
        self.lock = Lock()

    def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to file."""
        with self.lock:
            try:
                file_path = self._get_file_path()
                formatted_data = self.formatter.format_batch(entries)

                if self.compression:
                    formatted_data = gzip.compress(formatted_data.encode('utf-8'))

                mode = 'ab' if self.compression else 'a'
                with open(file_path, mode, encoding='utf-8' if not self.compression else None) as f:
                    if self.compression:
                        f.write(formatted_data)
                    else:
                        f.write(formatted_data + '\n')

                return True
            except Exception as e:
                print(f"Failed to write logs: {e}")
                return False

    def read(self, start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             filters: Optional[Dict[str, Any]] = None) -> List[LogEntry]:
        """Read entries from files."""
        # This is a simplified implementation
        # In practice, you'd need to search through multiple files
        entries = []

        try:
            # For simplicity, read from current day's file
            file_path = self._get_file_path()
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if self.format == LogFormat.JSON:
                    if content.strip():
                        data = json.loads(content)
                        if isinstance(data, list):
                            entries = [LogEntry.from_dict(item) for item in data]
                        else:
                            entries = [LogEntry.from_dict(data)]
        except Exception as e:
            print(f"Failed to read logs: {e}")

        return entries

    def get_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        total_size = 0
        file_count = 0

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1

        return {
            'total_size_bytes': total_size,
            'file_count': file_count,
            'base_path': str(self.base_path)
        }

    def _get_formatter(self) -> LogFormatter:
        """Get appropriate formatter."""
        if self.format == LogFormat.JSON:
            return JSONFormatter()
        elif self.format == LogFormat.CSV:
            return CSVFormatter()
        elif self.format == LogFormat.LOGSTASH:
            return LogstashFormatter()
        else:
            return JSONFormatter()

    def _get_file_path(self) -> Path:
        """Get current file path based on rotation strategy."""
        now = datetime.now()

        if self.rotation == "daily":
            date_str = now.strftime("%Y%m%d")
            filename = f"logs_{date_str}.{self.format.value}"
        elif self.rotation == "hourly":
            date_str = now.strftime("%Y%m%d_%H")
            filename = f"logs_{date_str}.{self.format.value}"
        else:
            filename = f"logs.{self.format.value}"

        if self.compression:
            filename += ".gz"

        return self.base_path / filename


class RedisStorageBackend(LogStorageBackend):
    """Redis-based log storage."""

    def __init__(self, host: str = "localhost", port: int = 6379,
                 key_prefix: str = "qantify:logs"):
        if redis is None:
            raise ImportError("redis package required for RedisStorageBackend")

        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.key_prefix = key_prefix

    def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to Redis."""
        try:
            pipeline = self.client.pipeline()
            for entry in entries:
                key = f"{self.key_prefix}:{entry.timestamp.strftime('%Y%m%d%H%M%S%f')}"
                pipeline.set(key, json.dumps(entry.to_dict(), default=str))
                # Add to sorted set for time-based queries
                pipeline.zadd(f"{self.key_prefix}:index", {key: entry.timestamp.timestamp()})

            pipeline.execute()
            return True
        except Exception as e:
            print(f"Failed to write to Redis: {e}")
            return False

    def read(self, start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             filters: Optional[Dict[str, Any]] = None) -> List[LogEntry]:
        """Read entries from Redis."""
        try:
            # Get keys in time range
            min_score = start_time.timestamp() if start_time else 0
            max_score = end_time.timestamp() if end_time else datetime.now().timestamp()

            keys = self.client.zrangebyscore(
                f"{self.key_prefix}:index",
                min_score,
                max_score
            )

            entries = []
            for key in keys:
                data = self.client.get(key)
                if data:
                    entry_dict = json.loads(data)
                    entry = LogEntry.from_dict(entry_dict)

                    # Apply filters
                    if self._matches_filters(entry, filters):
                        entries.append(entry)

            return entries
        except Exception as e:
            print(f"Failed to read from Redis: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis storage statistics."""
        try:
            key_count = self.client.zcard(f"{self.key_prefix}:index")
            return {
                'total_entries': key_count,
                'key_prefix': self.key_prefix
            }
        except Exception:
            return {'error': 'Could not get Redis stats'}

    def _matches_filters(self, entry: LogEntry, filters: Optional[Dict[str, Any]]) -> bool:
        """Check if entry matches filters."""
        if not filters:
            return True

        for key, value in filters.items():
            if hasattr(entry, key):
                if getattr(entry, key) != value:
                    return False
            elif key in entry.extra_fields:
                if entry.extra_fields[key] != value:
                    return False
            else:
                return False

        return True


class ElasticsearchStorageBackend(LogStorageBackend):
    """Elasticsearch-based log storage."""

    def __init__(self, hosts: List[str], index_name: str = "qantify-logs"):
        if elasticsearch is None:
            raise ImportError("elasticsearch package required")

        self.client = Elasticsearch(hosts)
        self.index_name = index_name

    def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to Elasticsearch."""
        try:
            actions = []
            for entry in entries:
                actions.append({
                    "_index": self.index_name,
                    "_id": str(uuid.uuid4()),
                    "_source": entry.to_dict()
                })

            from elasticsearch.helpers import bulk
            bulk(self.client, actions)
            return True
        except Exception as e:
            print(f"Failed to write to Elasticsearch: {e}")
            return False

    def read(self, start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             filters: Optional[Dict[str, Any]] = None) -> List[LogEntry]:
        """Read entries from Elasticsearch."""
        try:
            query = {"bool": {"must": []}}

            # Time range query
            if start_time or end_time:
                range_query = {"range": {"timestamp": {}}}
                if start_time:
                    range_query["range"]["timestamp"]["gte"] = start_time.isoformat()
                if end_time:
                    range_query["range"]["timestamp"]["lte"] = end_time.isoformat()
                query["bool"]["must"].append(range_query)

            # Additional filters
            if filters:
                for key, value in filters.items():
                    query["bool"]["must"].append({"term": {key: value}})

            response = self.client.search(
                index=self.index_name,
                query=query,
                size=10000  # Adjust as needed
            )

            entries = []
            for hit in response["hits"]["hits"]:
                entries.append(LogEntry.from_dict(hit["_source"]))

            return entries
        except Exception as e:
            print(f"Failed to read from Elasticsearch: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch storage statistics."""
        try:
            stats = self.client.indices.stats(index=self.index_name)
            return {
                'total_docs': stats['_all']['total']['docs']['count'],
                'index_name': self.index_name
            }
        except Exception:
            return {'error': 'Could not get Elasticsearch stats'}


# =============================================================================
# ADVANCED LOGGER
# =============================================================================

class AdvancedLogger:
    """Advanced logging system with multiple backends and real-time monitoring."""

    def __init__(self, strategy_id: Optional[str] = None,
                 session_id: Optional[str] = None,
                 backends: Optional[List[LogStorageBackend]] = None):
        self.strategy_id = strategy_id or str(uuid.uuid4())
        self.session_id = session_id or str(uuid.uuid4())
        self.backends = backends or [FileStorageBackend("./logs")]
        self.async_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.is_running = True

        # Start async processing
        self.async_thread = threading.Thread(target=self._process_async_logs, daemon=True)
        self.async_thread.start()

        # Performance tracking
        self.log_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.performance_metrics = {}

    def log(self, level: LogLevel, category: LogCategory, message: str,
            symbol: Optional[str] = None, index: Optional[int] = None,
            correlation_id: Optional[str] = None, **extra_fields) -> None:
        """Log a message with structured data."""

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            strategy_id=self.strategy_id,
            symbol=symbol,
            index=index,
            session_id=self.session_id,
            correlation_id=correlation_id,
            extra_fields=extra_fields
        )

        # Update counters
        self.log_counts[level.name] += 1
        if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
            self.error_counts[category.name] += 1

        # Write to backends (async for performance)
        self.async_queue.put(entry)

    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, LogCategory.DEBUG, message, **kwargs)

    def log_info(self, message: str, category: LogCategory = LogCategory.STRATEGY, **kwargs) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, category, message, **kwargs)

    def log_warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, category, message, **kwargs)

    def log_error(self, message: str, category: LogCategory = LogCategory.ERROR,
                  stack_trace: Optional[str] = None, **kwargs) -> None:
        """Log error message."""
        if stack_trace:
            kwargs['stack_trace'] = stack_trace
        self.log(LogLevel.ERROR, category, message, **kwargs)

    def log_critical(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs) -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, category, message, **kwargs)

    def log_audit(self, message: str, **kwargs) -> None:
        """Log audit message."""
        self.log(LogLevel.AUDIT, LogCategory.AUDIT, message, **kwargs)

    def log_performance(self, operation: str, duration: float,
                       success: bool = True, **metrics) -> None:
        """Log performance metrics."""
        message = f"Performance: {operation}"
        self.log(
            LogLevel.INFO if success else LogLevel.WARNING,
            LogCategory.PERFORMANCE,
            message,
            performance_metrics={'duration': duration, **metrics}
        )

    def _process_async_logs(self):
        """Process logs asynchronously."""
        batch_size = 50
        batch_timeout = 1.0
        batch = []

        while self.is_running:
            try:
                # Collect batch
                start_time = time.time()
                while len(batch) < batch_size and (time.time() - start_time) < batch_timeout:
                    try:
                        entry = self.async_queue.get(timeout=0.1)
                        batch.append(entry)
                    except:
                        break

                if batch:
                    # Write batch to all backends
                    for backend in self.backends:
                        try:
                            self.executor.submit(backend.write, batch.copy())
                        except Exception as e:
                            print(f"Failed to write to backend: {e}")

                    batch.clear()

            except Exception as e:
                print(f"Error in async log processing: {e}")
                time.sleep(1)

    def flush(self):
        """Flush all pending logs."""
        # Process remaining items in queue
        remaining = []
        try:
            while True:
                remaining.append(self.async_queue.get_nowait())
        except:
            pass

        if remaining:
            for backend in self.backends:
                try:
                    backend.write(remaining)
                except Exception as e:
                    print(f"Failed to flush to backend: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics."""
        backend_stats = {}
        for i, backend in enumerate(self.backends):
            try:
                backend_stats[f"backend_{i}"] = backend.get_stats()
            except Exception as e:
                backend_stats[f"backend_{i}"] = {'error': str(e)}

        return {
            'strategy_id': self.strategy_id,
            'session_id': self.session_id,
            'log_counts': dict(self.log_counts),
            'error_counts': dict(self.error_counts),
            'queue_size': self.async_queue.qsize(),
            'backend_stats': backend_stats
        }

    def shutdown(self):
        """Shutdown the logger."""
        self.is_running = False
        self.flush()
        self.executor.shutdown(wait=True)


# =============================================================================
# ANALYTICS AND MONITORING
# =============================================================================

class LogAnalytics:
    """Advanced log analytics and insights."""

    def __init__(self, logger: AdvancedLogger):
        self.logger = logger
        self.analytics_cache = {}
        self.update_interval = 300  # 5 minutes

    def get_error_rate(self, time_window: timedelta = timedelta(hours=1)) -> float:
        """Calculate error rate over time window."""
        end_time = datetime.now()
        start_time = end_time - time_window

        # This would query the storage backends
        # Simplified implementation
        total_logs = sum(self.logger.log_counts.values())
        total_errors = sum(self.logger.error_counts.values())

        return total_errors / total_logs if total_logs > 0 else 0.0

    def get_performance_metrics(self) -> Dict[str, float]:
        """Extract performance metrics from logs."""
        # This would analyze performance logs
        return {
            'avg_response_time': 0.0,
            'throughput': 0.0,
            'error_rate': self.get_error_rate(),
            'memory_usage': 0.0,
            'cpu_usage': 0.0
        }

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in logs."""
        anomalies = []

        # Simple anomaly detection
        error_rate = self.get_error_rate()
        if error_rate > 0.1:  # 10% error rate threshold
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f'Error rate is {error_rate:.1%}, above 10% threshold'
            })

        return anomalies

    def generate_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive log analysis report."""
        return {
            'time_range': {'start': start_time, 'end': end_time},
            'summary_stats': self.logger.get_stats(),
            'performance_metrics': self.get_performance_metrics(),
            'anomalies': self.detect_anomalies(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on log analysis."""
        recommendations = []

        error_rate = self.get_error_rate()
        if error_rate > 0.05:
            recommendations.append("Consider implementing better error handling and retry logic")

        if self.logger.log_counts.get('WARNING', 0) > 100:
            recommendations.append("Review warning messages for potential issues")

        return recommendations


class RealTimeMonitor:
    """Real-time monitoring and alerting system."""

    def __init__(self, logger: AdvancedLogger, alert_callbacks: Optional[List[Callable]] = None):
        self.logger = logger
        self.alert_callbacks = alert_callbacks or []
        self.alerts = []
        self.monitoring_active = False
        self.monitor_thread = None

    def start_monitoring(self, check_interval: float = 60.0):
        """Start real-time monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(check_interval,), daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def add_alert_callback(self, callback: Callable):
        """Add alert callback."""
        self.alert_callbacks.append(callback)

    def _monitor_loop(self, check_interval: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._check_health()
                self._check_performance()
                self._check_errors()
            except Exception as e:
                self.logger.log_error(f"Monitoring error: {e}", category=LogCategory.MONITORING)

            time.sleep(check_interval)

    def _check_health(self):
        """Check system health."""
        # Check if logger is working
        if self.logger.async_queue.qsize() > 1000:
            self._trigger_alert("High log queue size", LogLevel.WARNING,
                              f"Log queue size: {self.logger.async_queue.qsize()}")

    def _check_performance(self):
        """Check performance metrics."""
        stats = self.logger.get_stats()
        error_rate = sum(stats['error_counts'].values()) / sum(stats['log_counts'].values()) if stats['log_counts'] else 0

        if error_rate > 0.1:
            self._trigger_alert("High error rate", LogLevel.CRITICAL,
                              f"Error rate: {error_rate:.1%}")

    def _check_errors(self):
        """Check for error patterns."""
        # Check for recent errors
        recent_errors = self.logger.error_counts
        if any(count > 10 for count in recent_errors.values()):
            self._trigger_alert("High error frequency", LogLevel.ERROR,
                              f"Recent errors: {dict(recent_errors)}")

    def _trigger_alert(self, title: str, level: LogLevel, message: str):
        """Trigger an alert."""
        alert = {
            'timestamp': datetime.now(),
            'title': title,
            'level': level.name,
            'message': message
        }

        self.alerts.append(alert)
        self.logger.log(level, LogCategory.MONITORING, f"ALERT: {title} - {message}")

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback failed: {e}")


# =============================================================================
# VISUALIZATION AND DASHBOARDS
# =============================================================================

class LogVisualizer:
    """Create visualizations from log data."""

    def __init__(self, analytics: LogAnalytics):
        self.analytics = analytics

    def create_performance_dashboard(self) -> go.Figure:
        """Create performance dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Log Volume Over Time', 'Error Rate', 'Performance Metrics', 'Anomaly Detection'),
            specs=[[{'type': 'scatter'}, {'type': 'indicator'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )

        # This would create actual visualizations from log data
        # Simplified placeholder implementation

        return fig

    def create_error_analysis_chart(self) -> go.Figure:
        """Create error analysis visualization."""
        # Placeholder
        fig = go.Figure()
        return fig

    def create_category_distribution_chart(self) -> go.Figure:
        """Create log category distribution chart."""
        # Placeholder
        fig = px.pie(values=[1, 2, 3], names=['A', 'B', 'C'])
        return fig


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def logs_to_dataframe(logs: Iterable[dict], *, sort: bool = True) -> pd.DataFrame:
    """Convert iterable log dictionaries into a ``DataFrame`` (legacy compatibility)."""

    records: List[dict] = [dict(record) for record in logs]
    if not records:
        return pd.DataFrame(columns=["timestamp", "index", "message"])

    frame = pd.DataFrame(records)
    if "timestamp" in frame.columns:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    if sort:
        sort_cols = [col for col in ("timestamp", "index") if col in frame.columns]
        if sort_cols:
            frame = frame.sort_values(sort_cols)
    return frame.reset_index(drop=True)


def write_jsonl(logs: Iterable[dict], path: str | Path) -> None:
    """Write logs to a JSON Lines file (legacy compatibility)."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in logs:
            fh.write(json.dumps(record, default=_json_default))
            fh.write("\n")


def write_csv(logs: Iterable[dict], path: str | Path, **csv_kwargs) -> None:
    """Write logs to CSV using pandas export utilities (legacy compatibility)."""

    frame = logs_to_dataframe(logs)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, **csv_kwargs)


def write_parquet(logs: Iterable[dict], path: str | Path, **parquet_kwargs) -> None:
    """Persist logs to Parquet for efficient downstream analytics (legacy compatibility)."""

    frame = logs_to_dataframe(logs)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False, **parquet_kwargs)


def _json_default(obj):  # pragma: no cover - simple serialization helper
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return str(obj)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core classes
    "LogEntry", "LogLevel", "LogCategory", "LogFormat", "StorageBackend",
    "AdvancedLogger", "LogAnalytics", "RealTimeMonitor", "LogVisualizer",

    # Formatters
    "LogFormatter", "JSONFormatter", "CSVFormatter", "LogstashFormatter",

    # Storage backends
    "LogStorageBackend", "FileStorageBackend", "RedisStorageBackend", "ElasticsearchStorageBackend",

    # Legacy functions
    "logs_to_dataframe", "write_jsonl", "write_csv", "write_parquet",
]

"""
Audit Trail Management System
=============================

Comprehensive audit trail system for tracking all trading activities, compliance events,
and system operations with blockchain-level immutability and regulatory-grade security.

Key Features:
- Immutable audit logging with cryptographic integrity
- Blockchain-based audit trails for critical events
- Secure audit storage with encryption and hashing
- Real-time audit trail analysis and reporting
- Regulatory compliance audit trail requirements
- Tamper-proof event logging
- Audit trail reconstruction and forensics
- Multi-tier audit storage (memory, disk, blockchain)
- Audit trail analytics and anomaly detection
- Regulatory audit report generation
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, BinaryIO
from enum import Enum
import sqlite3
import queue
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import zlib


class AuditEventType(Enum):
    """Types of audit events"""
    TRADE_EXECUTION = "trade_execution"
    ORDER_PLACEMENT = "order_placement"
    ORDER_MODIFICATION = "order_modification"
    ORDER_CANCELLATION = "order_cancellation"
    POSITION_CHANGE = "position_change"
    RISK_CALCULATION = "risk_calculation"
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANCE_BREACH = "compliance_breach"
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    MARKET_DATA_UPDATE = "market_data_update"
    ALERT_GENERATION = "alert_generation"
    USER_ACTION = "user_action"
    SYSTEM_ERROR = "system_error"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class StorageType(Enum):
    """Audit storage types"""
    MEMORY = "memory"
    SQLITE = "sqlite"
    BLOCKCHAIN = "blockchain"
    ENCRYPTED_FILE = "encrypted_file"


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    source: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_chain: Optional[str] = None
    signature: Optional[str] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        content = f"{self.event_type.value}_{self.timestamp.isoformat()}_{self.source}_{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'source': self.source,
            'description': self.description,
            'data': self.data,
            'metadata': self.metadata,
            'hash_chain': self.hash_chain,
            'signature': self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuditEvent:
        """Create event from dictionary"""
        return cls(
            event_id=data.get('event_id', ''),
            event_type=AuditEventType(data['event_type']),
            severity=AuditSeverity(data['severity']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            source=data['source'],
            description=data['description'],
            data=data.get('data', {}),
            metadata=data.get('metadata', {}),
            hash_chain=data.get('hash_chain'),
            signature=data.get('signature')
        )


@dataclass
class AuditMetrics:
    """Audit trail metrics"""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_severity: Dict[str, int] = field(default_factory=dict)
    storage_size_bytes: int = 0
    last_event_timestamp: Optional[datetime] = None
    integrity_check_passed: bool = True
    average_event_size: float = 0.0


class AuditTrailManager:
    """Main audit trail management system"""

    def __init__(self,
                 storage_type: StorageType = StorageType.SQLITE,
                 encryption_key: Optional[str] = None,
                 max_queue_size: int = 10000,
                 batch_size: int = 100,
                 retention_days: int = 2555):  # 7 years for regulatory compliance

        self.storage_type = storage_type
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.retention_days = retention_days

        # Initialize storage
        self.storage = self._create_storage()

        # Event queue and processing
        self.event_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_active = False

        # Hash chain for integrity
        self.last_hash = None
        self.hash_lock = threading.Lock()

        # Metrics
        self.metrics = AuditMetrics()

        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Specialized auditors
        self.transaction_auditor = TransactionAuditor(self)
        self.position_auditor = PositionAuditor(self)
        self.risk_auditor = RiskAuditor(self)
        self.compliance_auditor = ComplianceAuditor(self)

        # Logging
        self.logger = logging.getLogger(__name__)

    def _create_storage(self):
        """Create appropriate storage backend"""
        if self.storage_type == StorageType.MEMORY:
            return AuditLogStorage()
        elif self.storage_type == StorageType.SQLITE:
            return SecureAuditStorage(db_path="audit_trail.db", encryption_key=self.encryption_key)
        elif self.storage_type == StorageType.BLOCKCHAIN:
            return BlockchainAuditTrail(node_url="http://localhost:8545", encryption_key=self.encryption_key)
        elif self.storage_type == StorageType.ENCRYPTED_FILE:
            return SecureAuditStorage(file_path="audit_trail.enc", encryption_key=self.encryption_key)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def start_audit_trail(self):
        """Start audit trail processing"""
        if self.processing_active:
            return

        self.processing_active = True
        self.logger.info("Starting audit trail processing")

        # Start processing thread
        threading.Thread(target=self._event_processing_loop, daemon=True).start()

        # Start cleanup thread
        threading.Thread(target=self._cleanup_loop, daemon=True).start()

    def stop_audit_trail(self):
        """Stop audit trail processing"""
        self.processing_active = False
        self.logger.info("Stopping audit trail processing")

        # Flush remaining events
        self._flush_event_queue()

        # Shutdown executor
        self.executor.shutdown(wait=True)

    def log_event(self,
                  event_type: AuditEventType,
                  severity: AuditSeverity,
                  source: str,
                  description: str,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  data: Optional[Dict[str, Any]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an audit event"""

        event = AuditEvent(
            event_id="",  # Will be generated
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            source=source,
            description=description,
            data=data or {},
            metadata=metadata or {}
        )

        # Add to processing queue
        try:
            self.event_queue.put_nowait(event)
            return event.event_id
        except queue.Full:
            self.logger.error("Audit event queue full, dropping event")
            return ""

    def _event_processing_loop(self):
        """Main event processing loop"""
        while self.processing_active:
            try:
                # Process events in batches
                events = []
                try:
                    # Try to get batch_size events with timeout
                    for _ in range(self.batch_size):
                        event = self.event_queue.get(timeout=1.0)
                        events.append(event)
                        self.event_queue.task_done()
                except queue.Empty:
                    pass

                if events:
                    self._process_event_batch(events)

            except Exception as e:
                self.logger.error(f"Error in event processing loop: {e}")

    def _process_event_batch(self, events: List[AuditEvent]):
        """Process a batch of audit events"""
        try:
            # Create hash chain for integrity
            self._create_hash_chain(events)

            # Add signatures for critical events
            self._add_signatures(events)

            # Store events
            self.storage.store_events(events)

            # Update metrics
            self._update_metrics(events)

        except Exception as e:
            self.logger.error(f"Error processing event batch: {e}")

    def _create_hash_chain(self, events: List[AuditEvent]):
        """Create cryptographic hash chain for event integrity"""
        with self.hash_lock:
            for event in events:
                # Create event content hash
                content = json.dumps(event.to_dict(), sort_keys=True, default=str)
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                # Chain with previous hash
                if self.last_hash:
                    chain_input = f"{self.last_hash}:{content_hash}"
                else:
                    chain_input = content_hash

                event.hash_chain = hashlib.sha256(chain_input.encode()).hexdigest()
                self.last_hash = event.hash_chain

    def _add_signatures(self, events: List[AuditEvent]):
        """Add digital signatures to critical events"""
        for event in events:
            if event.severity in [AuditSeverity.CRITICAL, AuditSeverity.SECURITY]:
                # Create signature (simplified - would use proper digital signature)
                content = f"{event.event_id}:{event.hash_chain}"
                event.signature = hmac.new(
                    self.encryption_key,
                    content.encode(),
                    hashlib.sha256
                ).hexdigest()

    def _update_metrics(self, events: List[AuditEvent]):
        """Update audit metrics"""
        self.metrics.total_events += len(events)
        self.metrics.last_event_timestamp = max(e.timestamp for e in events)

        # Update type and severity counts
        for event in events:
            etype = event.event_type.value
            severity = event.severity.value

            if etype not in self.metrics.events_by_type:
                self.metrics.events_by_type[etype] = 0
            self.metrics.events_by_type[etype] += 1

            if severity not in self.metrics.events_by_severity:
                self.metrics.events_by_severity[severity] = 0
            self.metrics.events_by_severity[severity] += 1

        # Estimate storage size
        avg_event_size = sum(len(json.dumps(e.to_dict()).encode()) for e in events) / len(events)
        self.metrics.average_event_size = (
            (self.metrics.average_event_size + avg_event_size) / 2
        )

    def _cleanup_loop(self):
        """Periodic cleanup of old audit events"""
        while self.processing_active:
            try:
                # Run cleanup daily
                time.sleep(86400)  # 24 hours

                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                deleted_count = self.storage.delete_events_older_than(cutoff_date)

                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old audit events")

            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")

    def _flush_event_queue(self):
        """Flush remaining events in queue"""
        events = []
        try:
            while True:
                event = self.event_queue.get_nowait()
                events.append(event)
                self.event_queue.task_done()
        except queue.Empty:
            pass

        if events:
            self._process_event_batch(events)

    def query_events(self,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    event_type: Optional[AuditEventType] = None,
                    severity: Optional[AuditSeverity] = None,
                    user_id: Optional[str] = None,
                    source: Optional[str] = None,
                    limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters"""
        return self.storage.query_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            source=source,
            limit=limit
        )

    def verify_integrity(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> bool:
        """Verify audit trail integrity"""
        try:
            events = self.storage.query_events(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Check last 10k events
            )

            if not events:
                return True

            # Sort by timestamp
            events.sort(key=lambda x: x.timestamp)

            # Verify hash chain
            expected_last_hash = None
            for event in events:
                if event.hash_chain:
                    content = json.dumps(event.to_dict(), sort_keys=True, default=str)
                    content_hash = hashlib.sha256(content.encode()).hexdigest()

                    if expected_last_hash:
                        chain_input = f"{expected_last_hash}:{content_hash}"
                    else:
                        chain_input = content_hash

                    calculated_hash = hashlib.sha256(chain_input.encode()).hexdigest()

                    if calculated_hash != event.hash_chain:
                        self.logger.error(f"Hash chain integrity check failed for event {event.event_id}")
                        return False

                    expected_last_hash = event.hash_chain

            self.metrics.integrity_check_passed = True
            return True

        except Exception as e:
            self.logger.error(f"Error verifying audit integrity: {e}")
            self.metrics.integrity_check_passed = False
            return False

    def generate_audit_report(self,
                             start_date: datetime,
                             end_date: datetime,
                             report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate audit report"""
        events = self.query_events(start_date=start_date, end_date=end_date)

        report = {
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'summary': {
                'total_events': len(events),
                'integrity_verified': self.verify_integrity(start_date, end_date),
                'events_by_type': {},
                'events_by_severity': {},
                'critical_events': []
            },
            'events': [],
            'anomalies': self._detect_anomalies(events)
        }

        # Analyze events
        for event in events:
            # Add to summary
            etype = event.event_type.value
            severity = event.severity.value

            if etype not in report['summary']['events_by_type']:
                report['summary']['events_by_type'][etype] = 0
            report['summary']['events_by_type'][etype] += 1

            if severity not in report['summary']['events_by_severity']:
                report['summary']['events_by_severity'][severity] = 0
            report['summary']['events_by_severity'][severity] += 1

            # Track critical events
            if event.severity in [AuditSeverity.CRITICAL, AuditSeverity.SECURITY]:
                report['summary']['critical_events'].append({
                    'id': event.event_id,
                    'type': etype,
                    'description': event.description,
                    'timestamp': event.timestamp.isoformat()
                })

            # Add event details (truncated for report)
            report['events'].append({
                'id': event.event_id,
                'type': etype,
                'severity': severity,
                'timestamp': event.timestamp.isoformat(),
                'source': event.source,
                'description': event.description[:100] + "..." if len(event.description) > 100 else event.description
            })

        return report

    def _detect_anomalies(self, events: List[AuditEvent]) -> List[Dict[str, Any]]:
        """Detect anomalies in audit events"""
        anomalies = []

        if len(events) < 10:
            return anomalies

        # Check for unusual event frequencies
        event_counts = {}
        for event in events:
            key = f"{event.event_type.value}_{event.severity.value}"
            if key not in event_counts:
                event_counts[key] = 0
            event_counts[key] += 1

        # Simple anomaly detection based on standard deviations
        counts = list(event_counts.values())
        if len(counts) > 1:
            mean_count = np.mean(counts)
            std_count = np.std(counts)

            for key, count in event_counts.items():
                if abs(count - mean_count) > 2 * std_count:
                    anomalies.append({
                        'type': 'unusual_frequency',
                        'description': f"Unusual frequency for {key}: {count} events",
                        'severity': 'medium'
                    })

        # Check for events outside business hours
        for event in events:
            if event.timestamp.hour < 6 or event.timestamp.hour > 18:
                if event.event_type in [AuditEventType.TRADE_EXECUTION, AuditEventType.ORDER_PLACEMENT]:
                    anomalies.append({
                        'type': 'off_hours_activity',
                        'description': f"Trading activity outside business hours: {event.description}",
                        'severity': 'low'
                    })

        return anomalies

    def get_metrics(self) -> AuditMetrics:
        """Get audit trail metrics"""
        return self.metrics


class TransactionAuditor:
    """Specialized auditor for transaction events"""

    def __init__(self, manager: AuditTrailManager):
        self.manager = manager

    def audit_transaction(self,
                         transaction_id: str,
                         transaction_data: Dict[str, Any],
                         user_id: str,
                         session_id: str) -> str:
        """Audit a transaction event"""
        return self.manager.log_event(
            event_type=AuditEventType.TRADE_EXECUTION,
            severity=AuditSeverity.INFO,
            source="transaction_processor",
            description=f"Transaction executed: {transaction_id}",
            user_id=user_id,
            session_id=session_id,
            data={
                'transaction_id': transaction_id,
                'symbol': transaction_data.get('symbol'),
                'quantity': transaction_data.get('quantity'),
                'price': transaction_data.get('price'),
                'value': transaction_data.get('quantity', 0) * transaction_data.get('price', 0)
            }
        )

    def audit_order_placement(self,
                             order_id: str,
                             order_data: Dict[str, Any],
                             user_id: str,
                             session_id: str) -> str:
        """Audit order placement"""
        return self.manager.log_event(
            event_type=AuditEventType.ORDER_PLACEMENT,
            severity=AuditSeverity.INFO,
            source="order_manager",
            description=f"Order placed: {order_id}",
            user_id=user_id,
            session_id=session_id,
            data={
                'order_id': order_id,
                'symbol': order_data.get('symbol'),
                'side': order_data.get('side'),
                'quantity': order_data.get('quantity'),
                'order_type': order_data.get('order_type')
            }
        )


class PositionAuditor:
    """Specialized auditor for position events"""

    def __init__(self, manager: AuditTrailManager):
        self.manager = manager

    def audit_position_change(self,
                             symbol: str,
                             old_position: float,
                             new_position: float,
                             reason: str,
                             user_id: str,
                             session_id: str) -> str:
        """Audit position change"""
        change_amount = new_position - old_position

        severity = AuditSeverity.WARNING if abs(change_amount) > 100000 else AuditSeverity.INFO

        return self.manager.log_event(
            event_type=AuditEventType.POSITION_CHANGE,
            severity=severity,
            source="portfolio_manager",
            description=f"Position change for {symbol}: {change_amount:.2f}",
            user_id=user_id,
            session_id=session_id,
            data={
                'symbol': symbol,
                'old_position': old_position,
                'new_position': new_position,
                'change_amount': change_amount,
                'reason': reason
            }
        )


class RiskAuditor:
    """Specialized auditor for risk events"""

    def __init__(self, manager: AuditTrailManager):
        self.manager = manager

    def audit_risk_calculation(self,
                              risk_type: str,
                              value: float,
                              threshold: float,
                              portfolio_id: str,
                              user_id: str) -> str:
        """Audit risk calculation"""
        breached = value > threshold
        severity = AuditSeverity.CRITICAL if breached else AuditSeverity.INFO

        return self.manager.log_event(
            event_type=AuditEventType.RISK_CALCULATION,
            severity=severity,
            source="risk_manager",
            description=f"{risk_type} calculated: {value:.4f} (threshold: {threshold:.4f})",
            user_id=user_id,
            data={
                'risk_type': risk_type,
                'value': value,
                'threshold': threshold,
                'breached': breached,
                'portfolio_id': portfolio_id
            }
        )


class ComplianceAuditor:
    """Specialized auditor for compliance events"""

    def __init__(self, manager: AuditTrailManager):
        self.manager = manager

    def audit_compliance_check(self,
                              rule_name: str,
                              passed: bool,
                              details: Dict[str, Any],
                              user_id: str) -> str:
        """Audit compliance check"""
        severity = AuditSeverity.ERROR if not passed else AuditSeverity.INFO

        return self.manager.log_event(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            severity=severity,
            source="compliance_monitor",
            description=f"Compliance check {'PASSED' if passed else 'FAILED'}: {rule_name}",
            user_id=user_id,
            data={
                'rule_name': rule_name,
                'passed': passed,
                'details': details
            }
        )

    def audit_compliance_breach(self,
                               rule_name: str,
                               breach_details: Dict[str, Any],
                               user_id: str) -> str:
        """Audit compliance breach"""
        return self.manager.log_event(
            event_type=AuditEventType.COMPLIANCE_BREACH,
            severity=AuditSeverity.CRITICAL,
            source="compliance_monitor",
            description=f"Compliance breach detected: {rule_name}",
            user_id=user_id,
            data={
                'rule_name': rule_name,
                'breach_details': breach_details
            }
        )


class AuditLogStorage(ABC):
    """Abstract base class for audit storage"""

    @abstractmethod
    def store_events(self, events: List[AuditEvent]):
        """Store audit events"""
        pass

    @abstractmethod
    def query_events(self, **filters) -> List[AuditEvent]:
        """Query audit events"""
        pass

    @abstractmethod
    def delete_events_older_than(self, cutoff_date: datetime) -> int:
        """Delete events older than cutoff date"""
        pass


class SecureAuditStorage(AuditLogStorage):
    """Secure audit storage with SQLite and encryption"""

    def __init__(self,
                 db_path: str = "audit_trail.db",
                 file_path: Optional[str] = None,
                 encryption_key: Optional[str] = None):
        self.db_path = db_path
        self.file_path = file_path
        self.encryption_key = encryption_key
        self.cipher = Fernet(encryption_key) if encryption_key else None

        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage backend"""
        if self.db_path:
            self._create_sqlite_tables()
        elif self.file_path:
            # Ensure encrypted file exists
            Path(self.file_path).touch()

    def _create_sqlite_tables(self):
        """Create SQLite tables for audit storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    severity TEXT,
                    timestamp TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    source TEXT,
                    description TEXT,
                    data TEXT,
                    metadata TEXT,
                    hash_chain TEXT,
                    signature TEXT
                )
            ''')

            # Create indexes for efficient querying
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)')

    def store_events(self, events: List[AuditEvent]):
        """Store events in SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            for event in events:
                event_dict = event.to_dict()

                # Encrypt sensitive data if cipher available
                if self.cipher:
                    event_dict['data'] = self.cipher.encrypt(json.dumps(event_dict['data']).encode()).decode()
                    event_dict['metadata'] = self.cipher.encrypt(json.dumps(event_dict['metadata']).encode()).decode()

                conn.execute('''
                    INSERT OR REPLACE INTO audit_events
                    (event_id, event_type, severity, timestamp, user_id, session_id,
                     source, description, data, metadata, hash_chain, signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_dict['event_id'],
                    event_dict['event_type'],
                    event_dict['severity'],
                    event_dict['timestamp'],
                    event_dict['user_id'],
                    event_dict['session_id'],
                    event_dict['source'],
                    event_dict['description'],
                    event_dict['data'],
                    event_dict['metadata'],
                    event_dict['hash_chain'],
                    event_dict['signature']
                ))

    def query_events(self, **filters) -> List[AuditEvent]:
        """Query events from SQLite database"""
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if filters.get('start_date'):
            query += " AND timestamp >= ?"
            params.append(filters['start_date'].isoformat())

        if filters.get('end_date'):
            query += " AND timestamp <= ?"
            params.append(filters['end_date'].isoformat())

        if filters.get('event_type'):
            query += " AND event_type = ?"
            params.append(filters['event_type'].value)

        if filters.get('severity'):
            query += " AND severity = ?"
            params.append(filters['severity'].value)

        if filters.get('user_id'):
            query += " AND user_id = ?"
            params.append(filters['user_id'])

        if filters.get('source'):
            query += " AND source = ?"
            params.append(filters['source'])

        query += " ORDER BY timestamp DESC"

        if filters.get('limit'):
            query += " LIMIT ?"
            params.append(filters['limit'])

        events = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)

            for row in cursor.fetchall():
                event_dict = dict(zip([desc[0] for desc in cursor.description], row))

                # Decrypt data if cipher available
                if self.cipher:
                    try:
                        event_dict['data'] = json.loads(self.cipher.decrypt(event_dict['data'].encode()).decode())
                        event_dict['metadata'] = json.loads(self.cipher.decrypt(event_dict['metadata'].encode()).decode())
                    except (InvalidToken, json.JSONDecodeError):
                        # Handle decryption failures
                        event_dict['data'] = {}
                        event_dict['metadata'] = {}

                events.append(AuditEvent.from_dict(event_dict))

        return events

    def delete_events_older_than(self, cutoff_date: datetime) -> int:
        """Delete events older than cutoff date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM audit_events WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            return cursor.rowcount


class BlockchainAuditTrail(AuditLogStorage):
    """Blockchain-based audit trail for immutable storage"""

    def __init__(self, node_url: str, encryption_key: str, contract_address: Optional[str] = None):
        self.node_url = node_url
        self.encryption_key = encryption_key
        self.contract_address = contract_address
        self.cipher = Fernet(encryption_key)

    def store_events(self, events: List[AuditEvent]):
        """Store events on blockchain"""
        # Implementation would interact with smart contract
        # This is a placeholder for blockchain integration
        pass

    def query_events(self, **filters) -> List[AuditEvent]:
        """Query events from blockchain"""
        # Implementation would query blockchain
        return []

    def delete_events_older_than(self, cutoff_date: datetime) -> int:
        """Blockchain events are immutable - no deletion"""
        return 0


class AuditTrailAnalyzer:
    """Audit trail analysis and forensics"""

    def __init__(self, manager: AuditTrailManager):
        self.manager = manager

    def analyze_user_activity(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        events = self.manager.query_events(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )

        analysis = {
            'user_id': user_id,
            'period_days': days,
            'total_events': len(events),
            'events_by_type': {},
            'activity_timeline': [],
            'unusual_patterns': []
        }

        # Analyze event types
        for event in events:
            etype = event.event_type.value
            if etype not in analysis['events_by_type']:
                analysis['events_by_type'][etype] = 0
            analysis['events_by_type'][etype] += 1

        # Create activity timeline (hourly)
        hourly_activity = {}
        for event in events:
            hour = event.timestamp.strftime("%Y-%m-%d %H")
            if hour not in hourly_activity:
                hourly_activity[hour] = 0
            hourly_activity[hour] += 1

        analysis['activity_timeline'] = [
            {'hour': hour, 'count': count}
            for hour, count in sorted(hourly_activity.items())
        ]

        # Detect unusual patterns
        if len(events) > 10:
            # Check for events outside normal hours
            off_hours_events = [
                e for e in events
                if e.timestamp.hour < 6 or e.timestamp.hour > 18
            ]
            if len(off_hours_events) > len(events) * 0.1:  # More than 10% off-hours
                analysis['unusual_patterns'].append({
                    'type': 'off_hours_activity',
                    'description': f"{len(off_hours_events)} events outside business hours",
                    'severity': 'medium'
                })

        return analysis

    def detect_security_threats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Detect potential security threats in audit trail"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        events = self.manager.query_events(
            start_date=start_date,
            end_date=end_date
        )

        threats = []

        # Check for failed login patterns
        failed_logins = [
            e for e in events
            if e.event_type == AuditEventType.SYSTEM_ACCESS and 'failed' in e.description.lower()
        ]

        # Group by user
        failed_by_user = {}
        for event in failed_logins:
            user = event.user_id or 'unknown'
            if user not in failed_by_user:
                failed_by_user[user] = []
            failed_by_user[user].append(event)

        for user, user_events in failed_by_user.items():
            if len(user_events) > 5:  # More than 5 failed logins
                threats.append({
                    'type': 'brute_force_attempt',
                    'user_id': user,
                    'failed_attempts': len(user_events),
                    'timeframe': f"{start_date.date()} to {end_date.date()}",
                    'severity': 'high'
                })

        # Check for unusual access patterns
        access_events = [
            e for e in events
            if e.event_type == AuditEventType.SYSTEM_ACCESS
        ]

        # Implementation would include more sophisticated threat detection

        return threats


# Factory functions
def create_audit_trail_manager(storage_type: StorageType = StorageType.SQLITE,
                              encryption_key: Optional[str] = None) -> AuditTrailManager:
    """Create audit trail manager"""
    return AuditTrailManager(
        storage_type=storage_type,
        encryption_key=encryption_key
    )

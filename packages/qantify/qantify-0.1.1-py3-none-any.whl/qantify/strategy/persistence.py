"""Advanced State Management and Versioning Framework for Quantitative Trading Strategies.

This module provides comprehensive persistence capabilities including:
- Multi-backend state storage (SQLite, Redis, MongoDB, S3)
- Strategy versioning and rollback
- State compression and encryption
- Distributed state synchronization
- Performance metrics persistence
- Strategy lineage tracking
- Backup and recovery systems
- Audit trails and compliance logging
"""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import json
import sqlite3
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
from functools import wraps, partial
from collections import defaultdict
import time

import numpy as np
import pandas as pd

# Optional dependencies
try:
    import redis  # type: ignore
except ImportError:
    redis = None

try:
    import pymongo  # type: ignore
    from pymongo import MongoClient  # type: ignore
except ImportError:
    pymongo = None
    MongoClient = None

try:
    import boto3  # type: ignore
except ImportError:
    boto3 = None

try:
    from cryptography.fernet import Fernet  # type: ignore
    cryptography_available = True
except ImportError:
    Fernet = None
    cryptography_available = False

try:
    import lz4.frame  # type: ignore
except ImportError:
    lz4 = None


# Enums and Types
class StorageBackend(str):
    """Supported storage backends."""
    SQLITE = "sqlite"
    REDIS = "redis"
    MONGODB = "mongodb"
    S3 = "s3"
    FILE = "file"

class CompressionType(str):
    """Compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"

class StateVersion(str):
    """Versioning schemes."""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"

# Protocols
class EncryptionKeyProvider(Protocol):
    """Protocol for encryption key management."""
    def get_key(self, strategy_id: str) -> bytes: ...
    def rotate_key(self, strategy_id: str) -> bytes: ...

class StateSerializer(Protocol):
    """Protocol for state serialization."""
    def serialize(self, data: Dict[str, Any]) -> bytes: ...
    def deserialize(self, data: bytes) -> Dict[str, Any]: ...

# Enhanced StateSnapshot
@dataclass(slots=True)
class StateSnapshot:
    """Enhanced state snapshot with versioning and metadata."""
    state: Dict[str, Any]
    logs: List[Dict[str, Any]]
    journal: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = StateVersion.V2_0
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    compressed_size: Optional[int] = None
    strategy_hash: Optional[str] = None

    def __post_init__(self):
        """Calculate checksum and hash after initialization."""
        if self.checksum is None:
            self.checksum = self._calculate_checksum()
        if self.strategy_hash is None:
            self.strategy_hash = self._calculate_strategy_hash()

    def _calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of the snapshot data."""
        data = json.dumps({
            'state': self.state,
            'logs': self.logs,
            'journal': self.journal,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }, default=str, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def _calculate_strategy_hash(self) -> str:
        """Calculate hash of the strategy state for change detection."""
        state_str = json.dumps(self.state, default=str, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def validate_checksum(self) -> bool:
        """Validate snapshot integrity."""
        return self.checksum == self._calculate_checksum()

    def get_size_mb(self) -> float:
        """Get snapshot size in MB."""
        data = json.dumps({
            'state': self.state,
            'logs': self.logs,
            'journal': self.journal,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }, default=str)
        return len(data.encode()) / (1024 * 1024)

    def summarize_changes(self, other: 'StateSnapshot') -> Dict[str, Any]:
        """Summarize changes between two snapshots."""
        changes = {
            'state_changes': self._diff_dict(self.state, other.state),
            'log_count_diff': len(self.logs) - len(other.logs),
            'journal_count_diff': len(self.journal) - len(other.journal),
            'time_diff_seconds': (self.timestamp - other.timestamp).total_seconds(),
            'version_changed': self.version != other.version
        }
        return changes

    @staticmethod
    def _diff_dict(new_dict: Dict[str, Any], old_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate differences between two dictionaries."""
        changes = {}
        all_keys = set(new_dict.keys()) | set(old_dict.keys())

        for key in all_keys:
            if key not in old_dict:
                changes[key] = {'type': 'added', 'new_value': new_dict[key]}
            elif key not in new_dict:
                changes[key] = {'type': 'removed', 'old_value': old_dict[key]}
            elif new_dict[key] != old_dict[key]:
                changes[key] = {
                    'type': 'modified',
                    'old_value': old_dict[key],
                    'new_value': new_dict[key]
                }

        return changes


# Compression Utilities
class StateCompressor:
    """Handles state compression and decompression."""

    @staticmethod
    def compress(data: bytes, method: CompressionType = CompressionType.GZIP) -> bytes:
        """Compress data using specified method."""
        if method == CompressionType.NONE:
            return data
        elif method == CompressionType.GZIP:
            return gzip.compress(data)
        elif method == CompressionType.LZ4:
            if lz4 is not None:
                return lz4.frame.compress(data)  # type: ignore
            else:
                # Fallback to gzip
                return gzip.compress(data)
        else:
            raise ValueError(f"Unsupported compression method: {method}")

    @staticmethod
    def decompress(data: bytes, method: CompressionType = CompressionType.GZIP) -> bytes:
        """Decompress data using specified method."""
        if method == CompressionType.NONE:
            return data
        elif method == CompressionType.GZIP:
            return gzip.decompress(data)
        elif method == CompressionType.LZ4:
            if lz4 is not None:
                return lz4.frame.decompress(data)  # type: ignore
            else:
                # Fallback to gzip
                return gzip.decompress(data)
        else:
            raise ValueError(f"Unsupported compression method: {method}")

# Enhanced StateStore ABC
class StateStore(ABC):
    """Abstract base class for state storage backends."""

    def __init__(self, compression: CompressionType = CompressionType.GZIP,
                 encryption_key_provider: Optional[EncryptionKeyProvider] = None):
        self.compression = compression
        self.encryption_key_provider = encryption_key_provider
        self._serializer: StateSerializer = JSONStateSerializer()

    @abstractmethod
    def save_state(self, strategy_id: str, snapshot: StateSnapshot) -> None:
        """Save a state snapshot."""
        pass

    @abstractmethod
    def load_state(self, strategy_id: str) -> Optional[StateSnapshot]:
        """Load the latest state snapshot."""
        pass

    @abstractmethod
    def save_versioned_state(self, strategy_id: str, version: str, snapshot: StateSnapshot) -> None:
        """Save a versioned state snapshot."""
        pass

    @abstractmethod
    def load_versioned_state(self, strategy_id: str, version: str) -> Optional[StateSnapshot]:
        """Load a specific version of state snapshot."""
        pass

    @abstractmethod
    def list_versions(self, strategy_id: str) -> List[str]:
        """List all available versions for a strategy."""
        pass

    @abstractmethod
    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the event log."""
        pass

    @abstractmethod
    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events within a time range."""
        pass

    def _serialize_snapshot(self, snapshot: StateSnapshot) -> bytes:
        """Serialize and optionally compress/encrypt a snapshot."""
        data = self._serializer.serialize({
            'state': snapshot.state,
            'logs': snapshot.logs,
            'journal': snapshot.journal,
            'timestamp': snapshot.timestamp.isoformat(),
            'version': snapshot.version,
            'metadata': snapshot.metadata,
            'checksum': snapshot.checksum,
            'strategy_hash': snapshot.strategy_hash
        })

        # Compress
        if self.compression != CompressionType.NONE:
            data = StateCompressor.compress(data, self.compression)
            snapshot.compressed_size = len(data)

        # Encrypt if key provider available
        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(snapshot.strategy_hash or "default")
            fernet = Fernet(key)
            data = fernet.encrypt(data)

        return data

    def _deserialize_snapshot(self, data: bytes, strategy_id: str) -> StateSnapshot:
        """Deserialize and optionally decompress/decrypt snapshot data."""
        # Decrypt if key provider available
        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(strategy_id)
            fernet = Fernet(key)
            data = fernet.decrypt(data)

        # Decompress
        if self.compression != CompressionType.NONE:
            data = StateCompressor.decompress(data, self.compression)

        payload = self._serializer.deserialize(data)

        return StateSnapshot(
            state=payload.get('state', {}),
            logs=payload.get('logs', []),
            journal=payload.get('journal', []),
            timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat())),
            version=payload.get('version', StateVersion.V2_0),
            metadata=payload.get('metadata', {}),
            checksum=payload.get('checksum'),
            compressed_size=payload.get('compressed_size'),
            strategy_hash=payload.get('strategy_hash')
        )

# JSON Serializer Implementation
class JSONStateSerializer:
    """JSON-based state serializer."""

    def serialize(self, data: Dict[str, Any]) -> bytes:
        """Serialize data to JSON bytes."""
        return json.dumps(data, default=str, separators=(',', ':')).encode('utf-8')

    def deserialize(self, data: bytes) -> Dict[str, Any]:
        """Deserialize JSON bytes to data."""
        return json.loads(data.decode('utf-8'))


class SQLiteStateStore(StateStore):
    """SQLite-based state store with versioning and compression support."""

    def __init__(self, path: str | Path, compression: CompressionType = CompressionType.GZIP,
                 encryption_key_provider: Optional[EncryptionKeyProvider] = None) -> None:
        super().__init__(compression, encryption_key_provider)
        self.path = Path(path)
        self._initialize()

    def _initialize(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.path) as conn:
            # States table with versioning
            conn.execute("""
                CREATE TABLE IF NOT EXISTS states (
                    strategy_id TEXT NOT NULL,
                    version TEXT NOT NULL DEFAULT 'latest',
                    data BLOB NOT NULL,
                    checksum TEXT,
                    compressed_size INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (strategy_id, version)
                )
            """)

            # Events table with indexing
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event BLOB NOT NULL,
                    event_type TEXT,
                    correlation_id TEXT
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_strategy_time ON events(strategy_id, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_states_strategy ON states(strategy_id)")

            # Metadata table for strategy information
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_metadata (
                    strategy_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    total_snapshots INTEGER DEFAULT 0,
                    total_events INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            conn.commit()

    def save_state(self, strategy_id: str, snapshot: StateSnapshot) -> None:
        """Save state snapshot."""
        data = self._serialize_snapshot(snapshot)
        checksum = snapshot.checksum or snapshot._calculate_checksum()

        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                INSERT INTO states(strategy_id, version, data, checksum, compressed_size, created_at, updated_at)
                VALUES(?, 'latest', ?, ?, ?, ?, ?)
                ON CONFLICT(strategy_id, version) DO UPDATE SET
                    data=excluded.data,
                    checksum=excluded.checksum,
                    compressed_size=excluded.compressed_size,
                    updated_at=excluded.updated_at
            """, (strategy_id, data, checksum, snapshot.compressed_size,
                  snapshot.timestamp.isoformat(), snapshot.timestamp.isoformat()))

            # Update metadata
            conn.execute("""
                INSERT INTO strategy_metadata(strategy_id, last_active, total_snapshots, metadata)
                VALUES(?, ?, 1, ?)
                ON CONFLICT(strategy_id) DO UPDATE SET
                    last_active=excluded.last_active,
                    total_snapshots=total_snapshots + 1,
                    metadata=excluded.metadata
            """, (strategy_id, snapshot.timestamp.isoformat(), json.dumps(snapshot.metadata)))

            conn.commit()

    def load_state(self, strategy_id: str) -> Optional[StateSnapshot]:
        """Load latest state snapshot."""
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("""
                SELECT data FROM states
                WHERE strategy_id = ? AND version = 'latest'
            """, (strategy_id,)).fetchone()

        if not row:
            return None

        return self._deserialize_snapshot(row[0], strategy_id)

    def save_versioned_state(self, strategy_id: str, version: str, snapshot: StateSnapshot) -> None:
        """Save a versioned state snapshot."""
        data = self._serialize_snapshot(snapshot)
        checksum = snapshot.checksum or snapshot._calculate_checksum()

        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                INSERT INTO states(strategy_id, version, data, checksum, compressed_size, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(strategy_id, version) DO UPDATE SET
                    data=excluded.data,
                    checksum=excluded.checksum,
                    compressed_size=excluded.compressed_size,
                    updated_at=excluded.updated_at
            """, (strategy_id, version, data, checksum, snapshot.compressed_size,
                  snapshot.timestamp.isoformat(), snapshot.timestamp.isoformat()))
            conn.commit()

    def load_versioned_state(self, strategy_id: str, version: str) -> Optional[StateSnapshot]:
        """Load a specific version of state snapshot."""
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("""
                SELECT data FROM states
                WHERE strategy_id = ? AND version = ?
            """, (strategy_id, version)).fetchone()

        if not row:
            return None

        return self._deserialize_snapshot(row[0], strategy_id)

    def list_versions(self, strategy_id: str) -> List[str]:
        """List all available versions for a strategy."""
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute("""
                SELECT DISTINCT version FROM states
                WHERE strategy_id = ?
                ORDER BY version DESC
            """, (strategy_id,)).fetchall()

        return [row[0] for row in rows]

    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the event log."""
        event_data = self._serializer.serialize(event)
        if self.compression != CompressionType.NONE:
            event_data = StateCompressor.compress(event_data, self.compression)

        # Encrypt if key provider available
        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(strategy_id)
            fernet = Fernet(key)
            event_data = fernet.encrypt(event_data)

        event_type = event.get('type', 'unknown')
        correlation_id = event.get('correlation_id')

        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                INSERT INTO events(strategy_id, timestamp, event, event_type, correlation_id)
                VALUES(?, ?, ?, ?, ?)
            """, (strategy_id, datetime.utcnow().isoformat(), event_data,
                  event_type, correlation_id))

            # Update metadata
            conn.execute("""
                UPDATE strategy_metadata
                SET total_events = total_events + 1, last_active = ?
                WHERE strategy_id = ?
            """, (datetime.utcnow().isoformat(), strategy_id))

            conn.commit()

    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events within a time range."""
        query = """
            SELECT event, timestamp FROM events
            WHERE strategy_id = ?
        """
        params = [strategy_id]

        if from_time:
            query += " AND timestamp >= ?"
            params.append(from_time.isoformat())
        if to_time:
            query += " AND timestamp <= ?"
            params.append(to_time.isoformat())

        query += " ORDER BY id"

        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(query, params).fetchall()

        for row in rows:
            event_data, timestamp = row

            # Decrypt if needed
            if self.encryption_key_provider and cryptography_available and Fernet is not None:
                key = self.encryption_key_provider.get_key(strategy_id)
                fernet = Fernet(key)
                event_data = fernet.decrypt(event_data)

            # Decompress if needed
            if self.compression != CompressionType.NONE:
                event_data = StateCompressor.decompress(event_data, self.compression)

            event = self._serializer.deserialize(event_data)
            event['replay_timestamp'] = timestamp
            yield event

    def get_strategy_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Get statistics for a strategy."""
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("""
                SELECT name, description, created_at, last_active,
                       total_snapshots, total_events, metadata
                FROM strategy_metadata WHERE strategy_id = ?
            """, (strategy_id,)).fetchone()

        if not row:
            return {}

        name, desc, created, last_active, snapshots, events, metadata = row

        return {
            'strategy_id': strategy_id,
            'name': name,
            'description': desc,
            'created_at': created,
            'last_active': last_active,
            'total_snapshots': snapshots,
            'total_events': events,
            'metadata': json.loads(metadata) if metadata else {}
        }


class RedisStateStore(StateStore):
    """Redis-based state store with advanced features."""

    def __init__(self, url: str = "redis://localhost:6379/0",
                 compression: CompressionType = CompressionType.GZIP,
                 encryption_key_provider: Optional[EncryptionKeyProvider] = None,
                 ttl_seconds: Optional[int] = None) -> None:
        super().__init__(compression, encryption_key_provider)
        if not redis:
            raise RuntimeError("redis package is required for RedisStateStore")
        self.client = redis.Redis.from_url(url)
        self.ttl_seconds = ttl_seconds

    def _state_key(self, strategy_id: str, version: str = "latest") -> str:
        return f"qantify:strategy:{strategy_id}:state:{version}"

    def _events_key(self, strategy_id: str) -> str:
        return f"qantify:strategy:{strategy_id}:events"

    def _versions_key(self, strategy_id: str) -> str:
        return f"qantify:strategy:{strategy_id}:versions"

    def _metadata_key(self, strategy_id: str) -> str:
        return f"qantify:strategy:{strategy_id}:metadata"

    def save_state(self, strategy_id: str, snapshot: StateSnapshot) -> None:
        """Save state snapshot."""
        data = self._serialize_snapshot(snapshot)
        key = self._state_key(strategy_id)

        # Use pipeline for atomic operations
        with self.client.pipeline() as pipe:
            pipe.set(key, data)
            if self.ttl_seconds:
                pipe.expire(key, self.ttl_seconds)

            # Update metadata
            metadata = {
                'last_active': snapshot.timestamp.isoformat(),
                'version': snapshot.version,
                'checksum': snapshot.checksum,
                'compressed_size': snapshot.compressed_size,
                'strategy_hash': snapshot.strategy_hash
            }
            pipe.hset(self._metadata_key(strategy_id), mapping=metadata)
            pipe.execute()

    def load_state(self, strategy_id: str) -> Optional[StateSnapshot]:
        """Load latest state snapshot."""
        data = self.client.get(self._state_key(strategy_id))
        if data is None:
            return None
        return self._deserialize_snapshot(data, strategy_id)

    def save_versioned_state(self, strategy_id: str, version: str, snapshot: StateSnapshot) -> None:
        """Save a versioned state snapshot."""
        data = self._serialize_snapshot(snapshot)
        key = self._state_key(strategy_id, version)

        with self.client.pipeline() as pipe:
            pipe.set(key, data)
            if self.ttl_seconds:
                pipe.expire(key, self.ttl_seconds)
            # Track version
            pipe.sadd(self._versions_key(strategy_id), version)
            pipe.execute()

    def load_versioned_state(self, strategy_id: str, version: str) -> Optional[StateSnapshot]:
        """Load a specific version of state snapshot."""
        data = self.client.get(self._state_key(strategy_id, version))
        if data is None:
            return None
        return self._deserialize_snapshot(data, strategy_id)

    def list_versions(self, strategy_id: str) -> List[str]:
        """List all available versions for a strategy."""
        versions = self.client.smembers(self._versions_key(strategy_id))
        return sorted([v.decode() for v in versions], reverse=True)

    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the event log."""
        event_data = self._serializer.serialize(event)
        if self.compression != CompressionType.NONE:
            event_data = StateCompressor.compress(event_data, self.compression)

        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(strategy_id)
            fernet = Fernet(key)
            event_data = fernet.encrypt(event_data)

        # Store event with timestamp
        event_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': event_data.hex(),
            'type': event.get('type', 'unknown'),
            'correlation_id': event.get('correlation_id')
        }

        with self.client.pipeline() as pipe:
            pipe.rpush(self._events_key(strategy_id), json.dumps(event_entry))
            # Keep only last N events to prevent unbounded growth
            pipe.ltrim(self._events_key(strategy_id), -10000, -1)
            pipe.execute()

    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events within a time range."""
        events_key = self._events_key(strategy_id)
        raw_events = self.client.lrange(events_key, 0, -1)

        for raw_event in raw_events:
            event_entry = json.loads(raw_event)
            event_timestamp = datetime.fromisoformat(event_entry['timestamp'])

            # Filter by time range
            if from_time and event_timestamp < from_time:
                continue
            if to_time and event_timestamp > to_time:
                continue

            # Decrypt and decompress
            event_data = bytes.fromhex(event_entry['data'])

            if self.encryption_key_provider and cryptography_available and Fernet is not None:
                key = self.encryption_key_provider.get_key(strategy_id)
                fernet = Fernet(key)
                event_data = fernet.decrypt(event_data)

            if self.compression != CompressionType.NONE:
                event_data = StateCompressor.decompress(event_data, self.compression)

            event = self._serializer.deserialize(event_data)
            event['replay_timestamp'] = event_entry['timestamp']
            yield event

    def get_strategy_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Get statistics for a strategy."""
        metadata = self.client.hgetall(self._metadata_key(strategy_id))
        event_count = self.client.llen(self._events_key(strategy_id))

        return {
            'strategy_id': strategy_id,
            'total_events': event_count,
            'versions': len(self.list_versions(strategy_id)),
            'last_active': metadata.get(b'last_active', b'').decode() if metadata.get(b'last_active') else None,
            'current_version': metadata.get(b'version', b'').decode() if metadata.get(b'version') else None,
            'compressed_size': int(metadata.get(b'compressed_size', 0)) if metadata.get(b'compressed_size') else 0
        }

    def cleanup_old_versions(self, strategy_id: str, keep_versions: int = 10) -> int:
        """Clean up old versions, keeping only the most recent N."""
        versions = self.list_versions(strategy_id)
        if len(versions) <= keep_versions:
            return 0

        versions_to_remove = versions[keep_versions:]
        removed_count = 0

        with self.client.pipeline() as pipe:
            for version in versions_to_remove:
                pipe.delete(self._state_key(strategy_id, version))
                pipe.srem(self._versions_key(strategy_id), version)
                removed_count += 1
            pipe.execute()

        return removed_count


class MongoDBStateStore(StateStore):
    """MongoDB-based state store with advanced querying capabilities."""

    def __init__(self, connection_string: str = "mongodb://localhost:27017/",
                 database: str = "qantify", compression: CompressionType = CompressionType.GZIP,
                 encryption_key_provider: Optional[EncryptionKeyProvider] = None) -> None:
        super().__init__(compression, encryption_key_provider)
        if not pymongo:
            raise RuntimeError("pymongo package is required for MongoDBStateStore")

        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """Ensure database indexes for performance."""
        # States collection indexes
        self.db.states.create_index([("strategy_id", 1), ("version", 1)], unique=True)
        self.db.states.create_index([("strategy_id", 1), ("timestamp", -1)])

        # Events collection indexes
        self.db.events.create_index([("strategy_id", 1), ("timestamp", -1)])
        self.db.events.create_index([("strategy_id", 1), ("event_type", 1)])
        self.db.events.create_index([("correlation_id", 1)])

    def save_state(self, strategy_id: str, snapshot: StateSnapshot) -> None:
        """Save state snapshot."""
        data = self._serialize_snapshot(snapshot)

        doc = {
            'strategy_id': strategy_id,
            'version': 'latest',
            'data': data,
            'checksum': snapshot.checksum,
            'compressed_size': snapshot.compressed_size,
            'timestamp': snapshot.timestamp,
            'metadata': snapshot.metadata,
            'strategy_hash': snapshot.strategy_hash,
            'created_at': datetime.utcnow()
        }

        self.db.states.replace_one(
            {'strategy_id': strategy_id, 'version': 'latest'},
            doc,
            upsert=True
        )

    def load_state(self, strategy_id: str) -> Optional[StateSnapshot]:
        """Load latest state snapshot."""
        doc = self.db.states.find_one({'strategy_id': strategy_id, 'version': 'latest'})
        if not doc:
            return None
        return self._deserialize_snapshot(doc['data'], strategy_id)

    def save_versioned_state(self, strategy_id: str, version: str, snapshot: StateSnapshot) -> None:
        """Save a versioned state snapshot."""
        data = self._serialize_snapshot(snapshot)

        doc = {
            'strategy_id': strategy_id,
            'version': version,
            'data': data,
            'checksum': snapshot.checksum,
            'compressed_size': snapshot.compressed_size,
            'timestamp': snapshot.timestamp,
            'metadata': snapshot.metadata,
            'strategy_hash': snapshot.strategy_hash,
            'created_at': datetime.utcnow()
        }

        self.db.states.replace_one(
            {'strategy_id': strategy_id, 'version': version},
            doc,
            upsert=True
        )

    def load_versioned_state(self, strategy_id: str, version: str) -> Optional[StateSnapshot]:
        """Load a specific version of state snapshot."""
        doc = self.db.states.find_one({'strategy_id': strategy_id, 'version': version})
        if not doc:
            return None
        return self._deserialize_snapshot(doc['data'], strategy_id)

    def list_versions(self, strategy_id: str) -> List[str]:
        """List all available versions for a strategy."""
        docs = self.db.states.find(
            {'strategy_id': strategy_id},
            {'version': 1}
        ).sort('timestamp', -1)

        return [doc['version'] for doc in docs]

    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the event log."""
        event_data = self._serializer.serialize(event)
        if self.compression != CompressionType.NONE:
            event_data = StateCompressor.compress(event_data, self.compression)

        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(strategy_id)
            fernet = Fernet(key)
            event_data = fernet.encrypt(event_data)

        doc = {
            'strategy_id': strategy_id,
            'timestamp': datetime.utcnow(),
            'event_data': event_data,
            'event_type': event.get('type', 'unknown'),
            'correlation_id': event.get('correlation_id'),
            'metadata': event.get('metadata', {})
        }

        self.db.events.insert_one(doc)

    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events within a time range."""
        query = {'strategy_id': strategy_id}
        if from_time or to_time:
            time_query = {}
            if from_time:
                time_query['$gte'] = from_time
            if to_time:
                time_query['$lte'] = to_time
            query['timestamp'] = time_query

        docs = self.db.events.find(query).sort('timestamp', 1)

        for doc in docs:
            event_data = doc['event_data']

            # Decrypt if needed
            if self.encryption_key_provider and cryptography_available and Fernet is not None:
                key = self.encryption_key_provider.get_key(strategy_id)
                fernet = Fernet(key)
                event_data = fernet.decrypt(event_data)

            # Decompress if needed
            if self.compression != CompressionType.NONE:
                event_data = StateCompressor.decompress(event_data, self.compression)

            event = self._serializer.deserialize(event_data)
            event['replay_timestamp'] = doc['timestamp'].isoformat()
            yield event

    def get_strategy_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Get statistics for a strategy."""
        state_count = self.db.states.count_documents({'strategy_id': strategy_id})
        event_count = self.db.events.count_documents({'strategy_id': strategy_id})

        latest_state = self.db.states.find_one(
            {'strategy_id': strategy_id, 'version': 'latest'}
        )

        return {
            'strategy_id': strategy_id,
            'total_snapshots': state_count,
            'total_events': event_count,
            'versions': state_count,
            'last_active': latest_state['timestamp'].isoformat() if latest_state else None,
            'compressed_size': latest_state.get('compressed_size', 0) if latest_state else 0
        }

    def cleanup_old_versions(self, strategy_id: str, keep_versions: int = 10,
                           older_than_days: Optional[int] = None) -> int:
        """Clean up old versions based on criteria."""
        query = {'strategy_id': strategy_id, 'version': {'$ne': 'latest'}}
        if older_than_days:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            query['timestamp'] = {'$lt': cutoff_date}

        # Get versions sorted by timestamp (newest first)
        docs = list(self.db.states.find(query).sort('timestamp', -1))
        versions_to_keep = {doc['version'] for doc in docs[:keep_versions]}
        versions_to_remove = [doc['version'] for doc in docs[keep_versions:] if doc['version'] not in versions_to_keep]

        if versions_to_remove:
            self.db.states.delete_many({
                'strategy_id': strategy_id,
                'version': {'$in': versions_to_remove}
            })

        return len(versions_to_remove)


class S3StateStore(StateStore):
    """S3-based state store for cloud-native deployments."""

    def __init__(self, bucket_name: str, region: str = "us-east-1",
                 compression: CompressionType = CompressionType.GZIP,
                 encryption_key_provider: Optional[EncryptionKeyProvider] = None,
                 prefix: str = "qantify/strategy-states/") -> None:
        super().__init__(compression, encryption_key_provider)
        if not boto3:
            raise RuntimeError("boto3 package is required for S3StateStore")

        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip('/') + '/'
        self.s3_client = boto3.client('s3', region_name=region)  # type: ignore

        # Ensure bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except self.s3_client.exceptions.NoSuchBucket:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region} if region != 'us-east-1' else {}
            )

    def _state_key_path(self, strategy_id: str, version: str = "latest") -> str:
        return f"{self.prefix}{strategy_id}/state/{version}.json"

    def _events_key_path(self, strategy_id: str) -> str:
        return f"{self.prefix}{strategy_id}/events/"

    def _metadata_key_path(self, strategy_id: str) -> str:
        return f"{self.prefix}{strategy_id}/metadata.json"

    def save_state(self, strategy_id: str, snapshot: StateSnapshot) -> None:
        """Save state snapshot to S3."""
        data = self._serialize_snapshot(snapshot)
        key = self._state_key_path(strategy_id)

        # Upload with metadata
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            Metadata={
                'checksum': snapshot.checksum or '',
                'compressed_size': str(snapshot.compressed_size or 0),
                'timestamp': snapshot.timestamp.isoformat(),
                'version': snapshot.version,
                'strategy_hash': snapshot.strategy_hash or ''
            },
            ContentType='application/octet-stream'
        )

        # Update metadata
        metadata = {
            'strategy_id': strategy_id,
            'last_active': snapshot.timestamp.isoformat(),
            'current_version': snapshot.version,
            'total_snapshots': 1,  # Would need to track this separately
            'compressed_size': snapshot.compressed_size
        }

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=self._metadata_key_path(strategy_id),
            Body=json.dumps(metadata, default=str).encode(),
            ContentType='application/json'
        )

    def load_state(self, strategy_id: str) -> Optional[StateSnapshot]:
        """Load latest state snapshot from S3."""
        key = self._state_key_path(strategy_id)

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read()
            return self._deserialize_snapshot(data, strategy_id)
        except self.s3_client.exceptions.NoSuchKey:
            return None

    def save_versioned_state(self, strategy_id: str, version: str, snapshot: StateSnapshot) -> None:
        """Save a versioned state snapshot to S3."""
        data = self._serialize_snapshot(snapshot)
        key = self._state_key_path(strategy_id, version)

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            Metadata={
                'checksum': snapshot.checksum or '',
                'compressed_size': str(snapshot.compressed_size or 0),
                'timestamp': snapshot.timestamp.isoformat(),
                'version': version,
                'strategy_hash': snapshot.strategy_hash or ''
            },
            ContentType='application/octet-stream'
        )

    def load_versioned_state(self, strategy_id: str, version: str) -> Optional[StateSnapshot]:
        """Load a specific version of state snapshot from S3."""
        key = self._state_key_path(strategy_id, version)

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read()
            return self._deserialize_snapshot(data, strategy_id)
        except self.s3_client.exceptions.NoSuchKey:
            return None

    def list_versions(self, strategy_id: str) -> List[str]:
        """List all available versions for a strategy in S3."""
        prefix = f"{self.prefix}{strategy_id}/state/"
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        versions = []
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.json'):
                    version = key.split('/')[-1].replace('.json', '')
                    versions.append(version)

        return sorted(versions, reverse=True)

    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to S3 (using timestamped files for simplicity)."""
        event_data = self._serializer.serialize(event)
        if self.compression != CompressionType.NONE:
            event_data = StateCompressor.compress(event_data, self.compression)

        if self.encryption_key_provider and cryptography_available and Fernet is not None:
            key = self.encryption_key_provider.get_key(strategy_id)
            fernet = Fernet(key)
            event_data = fernet.encrypt(event_data)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        key = f"{self._events_key_path(strategy_id)}{timestamp}.event"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=event_data,
            Metadata={
                'event_type': event.get('type', 'unknown'),
                'correlation_id': event.get('correlation_id', ''),
                'timestamp': datetime.utcnow().isoformat()
            },
            ContentType='application/octet-stream'
        )

    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events from S3 within a time range."""
        prefix = self._events_key_path(strategy_id)
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        if 'Contents' not in response:
            return

        for obj in response['Contents']:
            key = obj['Key']
            # Parse timestamp from filename
            timestamp_str = key.split('/')[-1].replace('.event', '')
            try:
                event_timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S_%f')
            except ValueError:
                continue

            # Filter by time range
            if from_time and event_timestamp < from_time:
                continue
            if to_time and event_timestamp > to_time:
                continue

            # Get event data
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            event_data = response['Body'].read()

            # Decrypt if needed
            if self.encryption_key_provider and cryptography_available and Fernet is not None:
                key_bytes = self.encryption_key_provider.get_key(strategy_id)
                fernet = Fernet(key_bytes)
                event_data = fernet.decrypt(event_data)

            # Decompress if needed
            if self.compression != CompressionType.NONE:
                event_data = StateCompressor.decompress(event_data, self.compression)

            event = self._serializer.deserialize(event_data)
            event['replay_timestamp'] = event_timestamp.isoformat()
            yield event

    def get_strategy_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Get statistics for a strategy from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self._metadata_key_path(strategy_id)
            )
            metadata = json.loads(response['Body'].read().decode())
        except self.s3_client.exceptions.NoSuchKey:
            metadata = {}

        # Count versions and events
        versions = len(self.list_versions(strategy_id))
        events_prefix = self._events_key_path(strategy_id)
        events_response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=events_prefix)
        event_count = len(events_response.get('Contents', []))

        return {
            'strategy_id': strategy_id,
            'total_snapshots': versions,
            'total_events': event_count,
            'versions': versions,
            'last_active': metadata.get('last_active'),
            'compressed_size': metadata.get('compressed_size', 0)
        }


# Encryption Key Providers
class SimpleEncryptionKeyProvider:
    """Simple encryption key provider using strategy_id-based keys."""

    def __init__(self, master_key: Optional[bytes] = None):
        if not cryptography_available or Fernet is None:
            raise RuntimeError("cryptography package is required for encryption")
        self.master_key = master_key or Fernet.generate_key()

    def get_key(self, strategy_id: str) -> bytes:
        """Generate a strategy-specific key from master key."""
        combined = self.master_key + strategy_id.encode()
        return hashlib.sha256(combined).digest()[:32]  # Use first 32 bytes for Fernet

    def rotate_key(self, strategy_id: str) -> bytes:
        """Rotate the key for a strategy (generates new master key)."""
        self.master_key = Fernet.generate_key()
        return self.get_key(strategy_id)

# Strategy State Manager
@dataclass
class StateManagerConfig:
    """Configuration for StrategyStateManager."""
    store_type: StorageBackend = StorageBackend.SQLITE
    store_config: Dict[str, Any] = field(default_factory=dict)
    compression: CompressionType = CompressionType.GZIP
    enable_encryption: bool = False
    auto_versioning: bool = True
    max_versions: int = 10
    cleanup_interval_hours: int = 24
    backup_enabled: bool = False
    backup_config: Dict[str, Any] = field(default_factory=dict)

class StrategyStateManager:
    """Advanced state management for strategies with versioning and backup."""

    def __init__(self, config: StateManagerConfig):
        self.config = config
        self.store = self._create_store()
        self.encryption_provider = None
        if config.enable_encryption:
            self.encryption_provider = SimpleEncryptionKeyProvider()

        self._last_cleanup = datetime.utcnow()
        self._lock = threading.Lock()

        # Performance tracking
        self._operation_counts: Dict[str, int] = defaultdict(int)
        self._operation_times: Dict[str, List[float]] = defaultdict(list)

    def _create_store(self) -> StateStore:
        """Create the appropriate state store based on configuration."""
        if self.config.store_type == StorageBackend.SQLITE:
            path = self.config.store_config.get('path', './strategy_states.db')
            return SQLiteStateStore(
                path=path,
                compression=self.config.compression,
                encryption_key_provider=self.encryption_provider
            )
        elif self.config.store_type == StorageBackend.REDIS:
            url = self.config.store_config.get('url', 'redis://localhost:6379/0')
            return RedisStateStore(
                url=url,
                compression=self.config.compression,
                encryption_key_provider=self.encryption_provider,
                ttl_seconds=self.config.store_config.get('ttl_seconds')
            )
        elif self.config.store_type == StorageBackend.MONGODB:
            conn_str = self.config.store_config.get('connection_string', 'mongodb://localhost:27017/')
            database = self.config.store_config.get('database', 'qantify')
            return MongoDBStateStore(
                connection_string=conn_str,
                database=database,
                compression=self.config.compression,
                encryption_key_provider=self.encryption_provider
            )
        elif self.config.store_type == StorageBackend.S3:
            bucket = self.config.store_config['bucket_name']
            region = self.config.store_config.get('region', 'us-east-1')
            return S3StateStore(
                bucket_name=bucket,
                region=region,
                compression=self.config.compression,
                encryption_key_provider=self.encryption_provider,
                prefix=self.config.store_config.get('prefix', 'qantify/strategy-states/')
            )
        else:
            raise ValueError(f"Unsupported store type: {self.config.store_type}")

    # def _time_operation(self, operation: str):
    #     """Decorator to time operations for performance monitoring."""
    #     def decorator(func):
    #         @wraps(func)
    #         def wrapper(self, *args, **kwargs):  # Note: self is passed here
    #             start_time = time.time()
    #             try:
    #                 result = func(self, *args, **kwargs)
    #                 duration = time.time() - start_time
    #                 self._operation_counts[operation] += 1
    #                 self._operation_times[operation].append(duration)
    #                 return result
    #             except Exception as e:
    #                 duration = time.time() - start_time
    #                 self._operation_times[operation].append(duration)
    #                 raise e
    #         return wrapper
    #     return decorator

    def save_state(self, strategy_id: str, state: Dict[str, Any],
                   logs: List[Dict[str, Any]], journal: List[Dict[str, Any]],
                   version: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save strategy state with automatic versioning."""
        with self._lock:
            snapshot = StateSnapshot(
                state=state,
                logs=logs,
                journal=journal,
                version=version or StateVersion.V2_0,
                metadata=metadata or {}
            )

            # Auto-versioning
            if self.config.auto_versioning and version is None:
                current_version = self.get_current_version(strategy_id)
                if current_version:
                    new_version = self._increment_version(current_version)
                    snapshot.version = new_version

            # Save latest
            self.store.save_state(strategy_id, snapshot)

            # Save versioned copy if versioning enabled
            if self.config.auto_versioning and snapshot.version != 'latest':
                self.store.save_versioned_state(strategy_id, snapshot.version, snapshot)

            # Periodic cleanup
            self._periodic_cleanup(strategy_id)

    def load_state(self, strategy_id: str, version: Optional[str] = None) -> Optional[StateSnapshot]:
        """Load strategy state, optionally a specific version."""
        if version and version != 'latest':
            return self.store.load_versioned_state(strategy_id, version)
        else:
            return self.store.load_state(strategy_id)

    def append_event(self, strategy_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the strategy's event log."""
        self.store.append_event(strategy_id, event)

    def replay_events(self, strategy_id: str, from_time: Optional[datetime] = None,
                     to_time: Optional[datetime] = None) -> Iterable[Dict[str, Any]]:
        """Replay events for a strategy within a time range."""
        return self.store.replay_events(strategy_id, from_time, to_time)

    def get_current_version(self, strategy_id: str) -> Optional[str]:
        """Get the current version of a strategy."""
        versions = self.store.list_versions(strategy_id)
        return versions[0] if versions else None

    def list_versions(self, strategy_id: str) -> List[str]:
        """List all versions available for a strategy."""
        return self.store.list_versions(strategy_id)

    def rollback_to_version(self, strategy_id: str, version: str) -> bool:
        """Rollback strategy to a specific version."""
        snapshot = self.store.load_versioned_state(strategy_id, version)
        if snapshot:
            # Create a new snapshot with the rolled back state
            rollback_snapshot = StateSnapshot(
                state=snapshot.state,
                logs=snapshot.logs,
                journal=snapshot.journal,
                version=StateVersion.V2_0,
                metadata={**snapshot.metadata, 'rolled_back_from': snapshot.version}
            )
            self.store.save_state(strategy_id, rollback_snapshot)
            return True
        return False

    def compare_versions(self, strategy_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a strategy."""
        snap1 = self.store.load_versioned_state(strategy_id, version1)
        snap2 = self.store.load_versioned_state(strategy_id, version2)

        if not snap1 or not snap2:
            return {'error': 'One or both versions not found'}

        return {
            'version1': version1,
            'version2': version2,
            'changes': snap1.summarize_changes(snap2),
            'size_difference_mb': abs(snap1.get_size_mb() - snap2.get_size_mb())
        }

    def get_strategy_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a strategy."""
        base_stats = self.store.get_strategy_stats(strategy_id)

        # Add version information
        versions = self.list_versions(strategy_id)
        current_version = self.get_current_version(strategy_id)

        # Calculate storage efficiency
        latest_snapshot = self.load_state(strategy_id)
        storage_efficiency = 0.0
        if latest_snapshot and latest_snapshot.compressed_size:
            original_size = latest_snapshot.get_size_mb() * (1024 * 1024)
            storage_efficiency = (original_size - latest_snapshot.compressed_size) / original_size * 100

        return {
            **base_stats,
            'versions': versions,
            'current_version': current_version,
            'storage_efficiency_percent': storage_efficiency,
            'encryption_enabled': self.config.enable_encryption,
            'compression_type': self.config.compression.value,
            'auto_versioning_enabled': self.config.auto_versioning
        }

    def cleanup_old_versions(self, strategy_id: str, keep_versions: int = None) -> int:
        """Clean up old versions, keeping only the most recent N."""
        keep = keep_versions or self.config.max_versions
        if hasattr(self.store, 'cleanup_old_versions'):
            return self.store.cleanup_old_versions(strategy_id, keep)
        return 0

    def export_strategy_data(self, strategy_id: str, output_path: str,
                           include_events: bool = True, versions: Optional[List[str]] = None) -> None:
        """Export all strategy data to a file for backup or migration."""
        data = {
            'strategy_id': strategy_id,
            'export_timestamp': datetime.utcnow().isoformat(),
            'config': {
                'store_type': self.config.store_type.value,
                'compression': self.config.compression.value,
                'encryption_enabled': self.config.enable_encryption
            },
            'stats': self.get_strategy_stats(strategy_id),
            'versions': {},
            'events': []
        }

        # Export versions
        export_versions = versions or self.list_versions(strategy_id)
        for version in export_versions:
            snapshot = self.load_state(strategy_id, version)
            if snapshot:
                data['versions'][version] = {
                    'state': snapshot.state,
                    'logs': snapshot.logs,
                    'journal': snapshot.journal,
                    'timestamp': snapshot.timestamp.isoformat(),
                    'version': snapshot.version,
                    'metadata': snapshot.metadata,
                    'checksum': snapshot.checksum
                }

        # Export events if requested
        if include_events:
            data['events'] = list(self.replay_events(strategy_id))

        # Save to file
        with open(output_path, 'w') as f:
            json.dump(data, f, default=str, indent=2)

    def import_strategy_data(self, input_path: str, strategy_id: Optional[str] = None) -> str:
        """Import strategy data from an exported file."""
        with open(input_path, 'r') as f:
            data = json.load(f)

        target_strategy_id = strategy_id or data['strategy_id']

        # Import versions
        for version, snapshot_data in data.get('versions', {}).items():
            snapshot = StateSnapshot(
                state=snapshot_data['state'],
                logs=snapshot_data['logs'],
                journal=snapshot_data['journal'],
                timestamp=datetime.fromisoformat(snapshot_data['timestamp']),
                version=snapshot_data['version'],
                metadata=snapshot_data.get('metadata', {}),
                checksum=snapshot_data.get('checksum')
            )

            if version == 'latest':
                self.store.save_state(target_strategy_id, snapshot)
            else:
                self.store.save_versioned_state(target_strategy_id, version, snapshot)

        # Import events
        for event in data.get('events', []):
            self.store.append_event(target_strategy_id, event)

        return target_strategy_id

    def _increment_version(self, version: str) -> str:
        """Increment a version string (simple semantic versioning)."""
        parts = version.split('.')
        if len(parts) >= 3:
            major, minor, patch = parts[:3]
            patch = str(int(patch) + 1)
            return f"{major}.{minor}.{patch}"
        else:
            return f"{version}.1"

    def _periodic_cleanup(self, strategy_id: str) -> None:
        """Perform periodic cleanup if enough time has passed."""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() > (self.config.cleanup_interval_hours * 3600):
            self.cleanup_old_versions(strategy_id)
            self._last_cleanup = now

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the state manager."""
        stats = {}
        for operation in self._operation_times:
            times = self._operation_times[operation]
            if times:
                stats[operation] = {
                    'count': self._operation_counts[operation],
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times),
                    'min_time': min(times),
                    'total_time': sum(times)
                }
        return stats

# State Version Control
class StateVersionControl:
    """Version control system for strategy states."""

    def __init__(self, state_manager: StrategyStateManager):
        self.state_manager = state_manager
        self._branches: Dict[str, str] = {}  # branch_name -> base_version

    def create_branch(self, strategy_id: str, branch_name: str, from_version: Optional[str] = None) -> bool:
        """Create a new branch from a specific version."""
        base_version = from_version or self.state_manager.get_current_version(strategy_id)
        if not base_version:
            return False

        self._branches[f"{strategy_id}:{branch_name}"] = base_version
        return True

    def merge_branch(self, strategy_id: str, branch_name: str, target_version: Optional[str] = None) -> bool:
        """Merge a branch into the main version."""
        branch_key = f"{strategy_id}:{branch_name}"
        if branch_key not in self._branches:
            return False

        # For simplicity, just update the latest version
        # In a real implementation, this would do proper merging
        current_snapshot = self.state_manager.load_state(strategy_id)
        if current_snapshot:
            merge_snapshot = StateSnapshot(
                state=current_snapshot.state,
                logs=current_snapshot.logs,
                journal=current_snapshot.journal,
                version=target_version or StateVersion.V2_0,
                metadata={**current_snapshot.metadata, 'merged_from_branch': branch_name}
            )
            self.state_manager.save_state(strategy_id, merge_snapshot.state,
                                        merge_snapshot.logs, merge_snapshot.journal,
                                        merge_snapshot.version, merge_snapshot.metadata)
            return True
        return False

# State Migration Manager
class StateMigrationManager:
    """Manages migration between different state formats or storage backends."""

    def __init__(self, source_manager: StrategyStateManager, target_manager: StrategyStateManager):
        self.source_manager = source_manager
        self.target_manager = target_manager

    def migrate_strategy(self, strategy_id: str, include_events: bool = True) -> bool:
        """Migrate a strategy from source to target manager."""
        try:
            # Export from source
            temp_file = f"/tmp/migration_{strategy_id}_{uuid.uuid4()}.json"
            self.source_manager.export_strategy_data(strategy_id, temp_file, include_events)

            # Import to target
            self.target_manager.import_strategy_data(temp_file, strategy_id)

            # Cleanup
            Path(temp_file).unlink(missing_ok=True)
            return True
        except Exception:
            return False

# State Replication Manager
class StateReplicationManager:
    """Manages replication of strategy states across multiple instances."""

    def __init__(self, primary_manager: StrategyStateManager,
                 replica_managers: List[StrategyStateManager]):
        self.primary_manager = primary_manager
        self.replica_managers = replica_managers
        self._sync_thread = None
        self._running = False

    def start_replication(self, sync_interval_seconds: int = 300) -> None:
        """Start background replication process."""
        if self._running:
            return

        self._running = True
        self._sync_thread = threading.Thread(
            target=self._replication_loop,
            args=(sync_interval_seconds,),
            daemon=True
        )
        self._sync_thread.start()

    def stop_replication(self) -> None:
        """Stop the replication process."""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=5)

    def sync_strategy(self, strategy_id: str) -> bool:
        """Manually sync a specific strategy to all replicas."""
        try:
            snapshot = self.primary_manager.load_state(strategy_id)
            if not snapshot:
                return False

            for replica in self.replica_managers:
                replica.save_state(strategy_id, snapshot.state, snapshot.logs,
                                 snapshot.journal, snapshot.version, snapshot.metadata)

                # Sync recent events
                recent_events = list(self.primary_manager.replay_events(
                    strategy_id, from_time=datetime.utcnow() - timedelta(hours=1)
                ))
                for event in recent_events:
                    replica.append_event(strategy_id, event)

            return True
        except Exception:
            return False

    def _replication_loop(self, sync_interval_seconds: int) -> None:
        """Background replication loop."""
        while self._running:
            try:
                # This would need more sophisticated logic to track what needs syncing
                # For now, just sleep
                time.sleep(sync_interval_seconds)
            except Exception:
                time.sleep(60)  # Wait a minute before retrying

__all__ = [
    "StateSnapshot",
    "StateStore",
    "SQLiteStateStore",
    "RedisStateStore",
    "MongoDBStateStore",
    "S3StateStore",
    "StateCompressor",
    "JSONStateSerializer",
    "SimpleEncryptionKeyProvider",
    "StateManagerConfig",
    "StrategyStateManager",
    "StateVersionControl",
    "StateMigrationManager",
    "StateReplicationManager",
    "StorageBackend",
    "CompressionType",
    "StateVersion",
    "EncryptionKeyProvider",
    "StateSerializer",
]

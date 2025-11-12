"""Caching and snapshot utilities for qantify data feeds."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from qantify.core.utils import ensure_datetime


@dataclass(slots=True)
class CacheEntry:
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryCache:
    def __init__(self) -> None:
        self._store: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[CacheEntry]:
        return self._store.get(key)

    def set(self, key: str, data: pd.DataFrame, *, metadata: Optional[Dict[str, Any]] = None) -> None:
        self._store[key] = CacheEntry(data=data, metadata=metadata or {})

    def evict(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class DiskCache:
    """Simple Parquet-based cache for OHLC data."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_")
        return self.root / f"{safe}.parquet"

    def _meta_path(self, key: str) -> Path:
        return self._path(key).with_suffix(".json")

    def get(self, key: str) -> Optional[CacheEntry]:
        path = self._path(key)
        if not path.exists():
            return None
        data = pd.read_parquet(path)
        meta_path = self._meta_path(key)
        metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        return CacheEntry(data=data, metadata=metadata)

    def set(self, key: str, data: pd.DataFrame, *, metadata: Optional[Dict[str, Any]] = None) -> None:
        path = self._path(key)
        data.to_parquet(path)
        meta_path = self._meta_path(key)
        meta_path.write_text(json.dumps(metadata or {}, default=str))

    def evict(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()
        meta = self._meta_path(key)
        if meta.exists():
            meta.unlink()


class SnapshotManager:
    """Manage latest snapshots and incremental update checkpoints."""

    def __init__(self, cache: DiskCache | MemoryCache) -> None:
        self.cache = cache

    def snapshot(self, key: str, data: pd.DataFrame, *, last_timestamp: Optional[pd.Timestamp] = None) -> None:
        metadata = {"last_timestamp": (last_timestamp or data.index.max()).isoformat() if not data.empty else None}
        self.cache.set(key, data, metadata=metadata)

    def load(self, key: str) -> Optional[pd.DataFrame]:
        entry = self.cache.get(key)
        if entry is None:
            return None
        return entry.data

    def last_timestamp(self, key: str) -> Optional[pd.Timestamp]:
        entry = self.cache.get(key)
        if not entry:
            return None
        ts = entry.metadata.get("last_timestamp")
        if ts:
            return ensure_datetime(ts)
        if entry.data.empty:
            return None
        return entry.data.index.max()


def make_cache_key(*parts: str) -> str:
    """Return a normalized cache key composed of arbitrary string parts."""

    normalized = [str(part).strip().lower().replace(" ", "-") for part in parts if part is not None]
    return ":".join(normalized)


def create_snapshot_manager(
    category: str,
    *,
    root: str | Path | None = None,
) -> SnapshotManager:
    """Convenience helper to build snapshot managers with standard naming."""

    if root is None:
        cache: DiskCache | MemoryCache = MemoryCache()
    else:
        base = Path(root)
        cache = DiskCache(base / category)
    return SnapshotManager(cache)


__all__ = ["MemoryCache", "DiskCache", "SnapshotManager", "CacheEntry", "make_cache_key", "create_snapshot_manager"]

"""Feature store utilities for persisting generated signals."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Protocol

import pandas as pd

try:  # optional dependency
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency not available
    redis = None  # type: ignore

try:  # optional dependency
    from feast import FeatureStore as FeastFeatureStoreClient  # type: ignore
except Exception:  # pragma: no cover - optional dependency not available
    FeastFeatureStoreClient = None  # type: ignore


@dataclass(slots=True)
class StoredFeatures:
    features: pd.DataFrame
    metadata: Dict[str, Any]
    version: str


@dataclass(slots=True)
class FeatureKey:
    symbol: str
    name: str
    version: str = "latest"


class FeatureStoreBackend(Protocol):
    def write(
        self,
        key: FeatureKey,
        features: pd.DataFrame,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        ...

    def read(self, key: FeatureKey) -> Optional[StoredFeatures]:
        ...

    def delete(self, key: FeatureKey) -> None:
        ...

    def list_versions(self, symbol: str, name: str) -> Iterable[str]:
        ...


class ParquetFeatureStore(FeatureStoreBackend):
    """Local filesystem store with versioned schemas."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _version_path(self, key: FeatureKey) -> Path:
        safe_name = key.name.replace("/", "_")
        safe_version = key.version.replace("/", "_")
        return self.root / key.symbol / safe_name / f"{safe_version}.parquet"

    def _meta_path(self, key: FeatureKey) -> Path:
        return self._version_path(key).with_suffix(".json")

    def write(
        self,
        key: FeatureKey,
        features: pd.DataFrame,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,  # noqa: ARG002 - TTL unused for parquet
    ) -> None:
        path = self._version_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        features.to_parquet(path)
        meta = {
            "schema": list(features.columns),
            "version": key.version,
            "metadata": metadata or {},
        }
        self._meta_path(key).write_text(json.dumps(meta, default=str))

    def read(self, key: FeatureKey) -> Optional[StoredFeatures]:
        path = self._version_path(key)
        if not path.exists():
            # fallback to latest version if exists
            versions = list(self.list_versions(key.symbol, key.name))
            if not versions:
                return None
            key = FeatureKey(symbol=key.symbol, name=key.name, version=versions[-1])
            path = self._version_path(key)
            if not path.exists():
                return None
        features = pd.read_parquet(path)
        meta_path = self._meta_path(key)
        metadata_payload = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        metadata = metadata_payload.get("metadata", {})
        version = metadata_payload.get("version", key.version)
        return StoredFeatures(features=features, metadata=metadata, version=version)

    def delete(self, key: FeatureKey) -> None:
        path = self._version_path(key)
        meta = self._meta_path(key)
        if path.exists():
            path.unlink()
        if meta.exists():
            meta.unlink()

    def list_versions(self, symbol: str, name: str) -> Iterable[str]:
        safe_name = name.replace("/", "_")
        folder = self.root / symbol / safe_name
        if not folder.exists():
            return ()
        versions = sorted(
            {
                path.stem
                for path in folder.glob("*.parquet")
                if not path.stem.startswith(".")
            }
        )
        return tuple(versions)


class RedisFeatureStore(FeatureStoreBackend):
    """Redis-based realtime feature store with TTL support."""

    def __init__(self, url: str = "redis://localhost:6379/0", *, prefix: str = "qantify:features") -> None:
        if redis is None:
            raise RuntimeError("redis-py is required for RedisFeatureStore but is not installed.")
        self.prefix = prefix
        self.client = redis.Redis.from_url(url, decode_responses=False)

    def _key(self, key: FeatureKey) -> str:
        return f"{self.prefix}:{key.symbol}:{key.name}:{key.version}"

    def write(
        self,
        key: FeatureKey,
        features: pd.DataFrame,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        payload = {
            "data": features.to_json(orient="split", date_unit="ns"),
            "metadata": metadata or {},
            "schema": list(features.columns),
            "version": key.version,
        }
        raw = json.dumps(payload).encode("utf-8")
        redis_key = self._key(key)
        self.client.set(redis_key, raw)
        if ttl_seconds:
            self.client.expire(redis_key, ttl_seconds)

    def read(self, key: FeatureKey) -> Optional[StoredFeatures]:
        redis_key = self._key(key)
        raw = self.client.get(redis_key)
        if raw is None:
            return None
        payload = json.loads(raw.decode("utf-8"))
        features = pd.read_json(payload["data"], orient="split")
        features.index = pd.to_datetime(features.index, utc=True)
        return StoredFeatures(
            features=features,
            metadata=payload.get("metadata", {}),
            version=payload.get("version", key.version),
        )

    def delete(self, key: FeatureKey) -> None:
        self.client.delete(self._key(key))

    def list_versions(self, symbol: str, name: str) -> Iterable[str]:
        pattern = f"{self.prefix}:{symbol}:{name}:*"
        keys = self.client.keys(pattern)
        versions = sorted(k.decode("utf-8").rsplit(":", 1)[-1] for k in keys)
        return tuple(versions)


class FeastFeatureStoreAdapter(FeatureStoreBackend):
    """Minimal adapter to interface with a Feast feature store."""

    def __init__(self, repo_path: str | Path) -> None:
        if FeastFeatureStoreClient is None:
            raise RuntimeError("feast is required for FeastFeatureStoreAdapter but is not installed.")
        self.store = FeastFeatureStoreClient(repo_path=str(repo_path))

    def write(
        self,
        key: FeatureKey,
        features: pd.DataFrame,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,  # noqa: ARG002 - TTL handled by Feast
    ) -> None:
        table_name = f"{key.symbol}_{key.name}_{key.version}".replace("-", "_")
        entity_df = features.reset_index().rename(columns={"index": "event_timestamp"})
        entity_df["event_timestamp"] = pd.to_datetime(entity_df["event_timestamp"], utc=True)
        self.store.write_to_offline_store(table_name, entity_df)
        if metadata:
            os.environ[f"FEAST_METADATA_{table_name}"] = json.dumps(metadata)

    def read(self, key: FeatureKey) -> Optional[StoredFeatures]:
        table_name = f"{key.symbol}_{key.name}_{key.version}".replace("-", "_")
        try:
            df = self.store.get_historical_features(
                entity_df=pd.DataFrame({"event_timestamp": [pd.Timestamp.utcnow()]}),
                features=[f"{table_name}:*"],
            ).to_df()
        except Exception:
            return None
        df = df.set_index("event_timestamp")
        df.index = pd.to_datetime(df.index, utc=True)
        metadata = {}
        env_key = f"FEAST_METADATA_{table_name}"
        if env_key in os.environ:
            metadata = json.loads(os.environ[env_key])
        return StoredFeatures(features=df, metadata=metadata, version=key.version)

    def delete(self, key: FeatureKey) -> None:
        # Feast does not expose direct deletion; we simulate by dropping meta
        env_key = f"FEAST_METADATA_{key.symbol}_{key.name}_{key.version}".replace("-", "_")
        os.environ.pop(env_key, None)

    def list_versions(self, symbol: str, name: str) -> Iterable[str]:
        prefix = f"{symbol}_{name}_".replace("-", "_")
        versions = []
        for env_key in os.environ:
            if env_key.startswith("FEAST_METADATA_") and env_key[len("FEAST_METADATA_") :].startswith(prefix):
                versions.append(env_key.split(prefix, 1)[-1])
        versions.sort()
        return tuple(versions)


@dataclass(slots=True)
class FeatureStoreManager:
    """High-level manager orchestrating multiple backends."""

    backend: FeatureStoreBackend
    default_version: str = "v1"

    def write(
        self,
        symbol: str,
        name: str,
        features: pd.DataFrame,
        *,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> FeatureKey:
        version = version or self.default_version
        key = FeatureKey(symbol=symbol, name=name, version=version)
        self.backend.write(key, features, metadata=metadata, ttl_seconds=ttl_seconds)
        return key

    def read(self, symbol: str, name: str, *, version: Optional[str] = None) -> Optional[StoredFeatures]:
        version = version or self.default_version
        key = FeatureKey(symbol=symbol, name=name, version=version)
        return self.backend.read(key)

    def delete(self, symbol: str, name: str, *, version: Optional[str] = None) -> None:
        version = version or self.default_version
        key = FeatureKey(symbol=symbol, name=name, version=version)
        self.backend.delete(key)

    def list_versions(self, symbol: str, name: str) -> Iterable[str]:
        return self.backend.list_versions(symbol, name)


__all__ = [
    "StoredFeatures",
    "FeatureKey",
    "FeatureStoreBackend",
    "ParquetFeatureStore",
    "RedisFeatureStore",
    "FeastFeatureStoreAdapter",
    "FeatureStoreManager",
]
"""Feature store utilities for persisting generated signals."""


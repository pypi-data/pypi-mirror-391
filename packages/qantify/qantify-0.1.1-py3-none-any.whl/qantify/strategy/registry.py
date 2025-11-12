"""Advanced Strategy Registry and Management System.

This module provides comprehensive strategy registration, discovery, metadata management,
performance tracking, dependency resolution, versioning, and lifecycle management
for quantitative trading strategies.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type, Union
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

import numpy as np
import pandas as pd

# Strategy Categories
class StrategyCategory(str):
    """Strategy classification categories."""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    BREAKOUT = "breakout"
    MACHINE_LEARNING = "machine_learning"
    RISK_PARITY = "risk_parity"
    MARKET_NEUTRAL = "market_neutral"
    SEASONAL = "seasonal"
    MULTI_ASSET = "multi_asset"
    CRYPTO = "crypto"
    FOREX = "forex"
    OPTIONS = "options"
    FUTURES = "futures"
    FACTOR_INVESTING = "factor_investing"
    SENTIMENT_BASED = "sentiment_based"
    HIGH_FREQUENCY = "high_frequency"
    CUSTOM = "custom"

class StrategyStatus(str):
    """Strategy lifecycle status."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class StrategyRisk(str):
    """Risk classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class DependencyType(str):
    """Types of strategy dependencies."""
    DATA_PROVIDER = "data_provider"
    SIGNAL_GENERATOR = "signal_generator"
    RISK_MANAGER = "risk_manager"
    EXECUTION_HANDLER = "execution_handler"
    MONITORING = "monitoring"
    STORAGE = "storage"

# Strategy Metadata
@dataclass
class StrategyMetadata:
    """Comprehensive metadata for strategy registration."""
    name: str
    description: str
    category: StrategyCategory
    author: str
    version: str
    status: StrategyStatus = StrategyStatus.DEVELOPMENT
    risk_level: StrategyRisk = StrategyRisk.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: Set[str] = field(default_factory=set)
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dependencies: Dict[DependencyType, List[str]] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    backtest_results: Dict[str, Any] = field(default_factory=dict)
    required_data: List[str] = field(default_factory=list)
    supported_timeframes: List[str] = field(default_factory=list)
    supported_assets: List[str] = field(default_factory=list)
    license: str = "proprietary"
    documentation_url: Optional[str] = None
    source_url: Optional[str] = None
    contacts: Dict[str, str] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate metadata after initialization."""
        self._validate_metadata()

    def _validate_metadata(self):
        """Validate metadata fields."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Strategy name cannot be empty")

        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Strategy description cannot be empty")

        # Validate version format (simple semver)
        parts = self.version.split('.')
        if len(parts) < 2 or not all(p.isdigit() for p in parts):
            raise ValueError("Version must be in format 'major.minor.patch'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        data = {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'author': self.author,
            'version': self.version,
            'status': self.status,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': list(self.tags),
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'performance_metrics': self.performance_metrics,
            'backtest_results': self.backtest_results,
            'required_data': self.required_data,
            'supported_timeframes': self.supported_timeframes,
            'supported_assets': self.supported_assets,
            'license': self.license,
            'documentation_url': self.documentation_url,
            'source_url': self.source_url,
            'contacts': self.contacts,
            'custom_metadata': self.custom_metadata
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyMetadata':
        """Create metadata from dictionary."""
        # Convert datetime strings back
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['tags'] = set(data.get('tags', []))
        return cls(**data)

    def update_performance(self, metrics: Dict[str, Any]) -> None:
        """Update performance metrics."""
        self.performance_metrics.update(metrics)
        self.updated_at = datetime.utcnow()

    def add_backtest_result(self, result_id: str, result: Dict[str, Any]) -> None:
        """Add a backtest result."""
        self.backtest_results[result_id] = {
            **result,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()

# Strategy Entry
@dataclass
class StrategyEntry:
    """Complete strategy registry entry."""
    strategy_class: Type[object]
    metadata: StrategyMetadata
    registration_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    registered_at: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    health_score: float = 1.0  # 0.0 to 1.0
    error_count: int = 0
    success_count: int = 0

    def record_usage(self, success: bool = True) -> None:
        """Record strategy usage."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        # Update health score
        total = self.success_count + self.error_count
        if total > 0:
            self.health_score = self.success_count / total

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0

    def is_healthy(self, threshold: float = 0.8) -> bool:
        """Check if strategy is healthy based on success rate."""
        return self.get_success_rate() >= (threshold * 100)

# Registry Exceptions
class StrategyRegistryError(RuntimeError):
    """Base registry exception."""
    pass

class StrategyNotFoundError(StrategyRegistryError):
    """Strategy not found in registry."""
    pass

class StrategyAlreadyExistsError(StrategyRegistryError):
    """Strategy already exists in registry."""
    pass

class DependencyResolutionError(StrategyRegistryError):
    """Cannot resolve strategy dependencies."""
    pass

# Advanced Strategy Registry
class StrategyRegistry:
    """Advanced strategy registry with comprehensive management features."""

    def __init__(self):
        self._strategies: Dict[str, StrategyEntry] = {}
        self._name_to_id: Dict[str, str] = {}
        self._category_index: Dict[StrategyCategory, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._author_index: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._performance_stats: Dict[str, List[float]] = {}

    def register_strategy(
        self,
        strategy_class: Type[object],
        metadata: StrategyMetadata,
        overwrite: bool = False
    ) -> str:
        """Register a strategy with comprehensive metadata."""
        with self._lock:
            strategy_name = metadata.name.lower()
            registration_id = str(uuid.uuid4())

            # Check for existing registration
            if strategy_name in self._name_to_id and not overwrite:
                existing_id = self._name_to_id[strategy_name]
                existing_entry = self._strategies[existing_id]
                if existing_entry.strategy_class is not strategy_class:
                    raise StrategyAlreadyExistsError(
                        f"Strategy '{metadata.name}' already registered with different class"
                    )

            # Validate strategy class
            self._validate_strategy_class(strategy_class, metadata)

            # Create entry
            entry = StrategyEntry(
                strategy_class=strategy_class,
                metadata=metadata,
                registration_id=registration_id
            )

            # Store in registry
            self._strategies[registration_id] = entry
            self._name_to_id[strategy_name] = registration_id

            # Update indexes
            self._update_indexes(entry)

            return registration_id

    def unregister_strategy(self, identifier: Union[str, Type[object]]) -> bool:
        """Unregister a strategy."""
        with self._lock:
            registration_id = self._resolve_identifier(identifier)
            if registration_id not in self._strategies:
                return False

            entry = self._strategies[registration_id]
            strategy_name = entry.metadata.name.lower()

            # Remove from indexes
            self._remove_from_indexes(entry)

            # Remove from main storage
            del self._strategies[registration_id]
            if strategy_name in self._name_to_id:
                del self._name_to_id[strategy_name]

            return True

    def get_strategy(self, identifier: Union[str, Type[object]]) -> StrategyEntry:
        """Get strategy entry by identifier."""
        registration_id = self._resolve_identifier(identifier)
        if registration_id not in self._strategies:
            raise StrategyNotFoundError(f"Strategy '{identifier}' not found")
        return self._strategies[registration_id]

    def get_strategy_class(self, identifier: Union[str, Type[object]]) -> Type[object]:
        """Get strategy class by identifier."""
        entry = self.get_strategy(identifier)
        entry.record_usage(success=True)
        return entry.strategy_class

    def list_strategies(
        self,
        category: Optional[StrategyCategory] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[StrategyStatus] = None,
        risk_level: Optional[StrategyRisk] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[StrategyEntry]:
        """List strategies with advanced filtering."""
        with self._lock:
            candidates = set(self._strategies.keys())

            # Apply filters
            if category:
                candidates &= self._category_index.get(category, set())

            if author:
                candidates &= self._author_index.get(author, set())

            if tags:
                for tag in tags:
                    candidates &= self._tag_index.get(tag, set())

            if status or risk_level:
                filtered = set()
                for reg_id in candidates:
                    entry = self._strategies[reg_id]
                    if status and entry.metadata.status != status:
                        continue
                    if risk_level and entry.metadata.risk_level != risk_level:
                        continue
                    filtered.add(reg_id)
                candidates = filtered

            # Sort by registration date (newest first)
            sorted_ids = sorted(
                candidates,
                key=lambda x: self._strategies[x].registered_at,
                reverse=True
            )

            # Apply pagination
            if offset:
                sorted_ids = sorted_ids[offset:]
            if limit:
                sorted_ids = sorted_ids[:limit]

            return [self._strategies[reg_id] for reg_id in sorted_ids]

    def search_strategies(self, query: str, limit: int = 50) -> List[Tuple[StrategyEntry, float]]:
        """Search strategies using fuzzy text matching."""
        query_lower = query.lower()
        results = []

        for entry in self._strategies.values():
            score = self._calculate_search_score(entry, query_lower)
            if score > 0:
                results.append((entry, score))

        # Sort by score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def get_strategy_stats(self, identifier: Union[str, Type[object]]) -> Dict[str, Any]:
        """Get comprehensive statistics for a strategy."""
        entry = self.get_strategy(identifier)

        return {
            'registration_id': entry.registration_id,
            'name': entry.metadata.name,
            'usage_count': entry.usage_count,
            'last_used': entry.last_used.isoformat() if entry.last_used else None,
            'health_score': entry.health_score,
            'success_rate': entry.get_success_rate(),
            'error_count': entry.error_count,
            'is_healthy': entry.is_healthy(),
            'category': entry.metadata.category,
            'author': entry.metadata.author,
            'version': entry.metadata.version,
            'status': entry.metadata.status,
            'risk_level': entry.metadata.risk_level,
            'tags': list(entry.metadata.tags),
            'supported_assets': entry.metadata.supported_assets,
            'supported_timeframes': entry.metadata.supported_timeframes,
            'performance_metrics': entry.metadata.performance_metrics,
            'backtest_results': entry.metadata.backtest_results
        }

    def update_strategy_metadata(
        self,
        identifier: Union[str, Type[object]],
        updates: Dict[str, Any]
    ) -> None:
        """Update strategy metadata."""
        with self._lock:
            entry = self.get_strategy(identifier)

            # Update metadata fields
            for key, value in updates.items():
                if hasattr(entry.metadata, key):
                    setattr(entry.metadata, key, value)

            entry.metadata.updated_at = datetime.utcnow()

            # Update indexes if category/tags changed
            if 'category' in updates or 'tags' in updates:
                self._remove_from_indexes(entry)
                self._update_indexes(entry)

    def resolve_dependencies(
        self,
        strategy_entry: StrategyEntry,
        recursive: bool = True
    ) -> List[StrategyEntry]:
        """Resolve strategy dependencies."""
        resolved = []
        to_resolve = list(strategy_entry.metadata.dependencies.values())
        resolved_names = set()

        while to_resolve:
            dep_type_deps = to_resolve.pop(0)
            for dep_name in dep_type_deps:
                if dep_name in resolved_names:
                    continue

                try:
                    dep_entry = self.get_strategy(dep_name)
                    resolved.append(dep_entry)
                    resolved_names.add(dep_name)

                    if recursive:
                        # Add dependencies of this dependency
                        for sub_deps in dep_entry.metadata.dependencies.values():
                            if sub_deps not in to_resolve:
                                to_resolve.extend(sub_deps)

                except StrategyNotFoundError:
                    raise DependencyResolutionError(
                        f"Cannot resolve dependency '{dep_name}' for strategy '{strategy_entry.metadata.name}'"
                    )

        return resolved

    def export_registry(self, filepath: str, include_classes: bool = False) -> None:
        """Export registry to JSON file."""
        data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_strategies': len(self._strategies),
            'strategies': {}
        }

        for reg_id, entry in self._strategies.items():
            strategy_data = {
                'metadata': entry.metadata.to_dict(),
                'registration_id': entry.registration_id,
                'registered_at': entry.registered_at.isoformat(),
                'usage_count': entry.usage_count,
                'last_used': entry.last_used.isoformat() if entry.last_used else None,
                'health_score': entry.health_score,
                'error_count': entry.error_count,
                'success_count': entry.success_count
            }

            if include_classes:
                strategy_data['class_name'] = entry.strategy_class.__name__
                strategy_data['class_module'] = entry.strategy_class.__module__

            data['strategies'][reg_id] = strategy_data

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def import_registry(self, filepath: str, overwrite: bool = False) -> int:
        """Import registry from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        imported_count = 0
        for reg_id, strategy_data in data.get('strategies', {}).items():
            try:
                metadata = StrategyMetadata.from_dict(strategy_data['metadata'])

                # Note: We can't import the actual class objects from JSON
                # This would need to be handled separately
                dummy_class = type(metadata.name, (), {})

                self.register_strategy(dummy_class, metadata, overwrite=overwrite)
                imported_count += 1

            except Exception as e:
                print(f"Failed to import strategy {reg_id}: {e}")
                continue

        return imported_count

    def get_registry_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report for the registry."""
        total_strategies = len(self._strategies)
        if total_strategies == 0:
            return {'status': 'empty', 'total_strategies': 0}

        healthy_strategies = sum(1 for s in self._strategies.values() if s.is_healthy())
        health_rate = healthy_strategies / total_strategies

        category_distribution = {}
        for entry in self._strategies.values():
            cat = entry.metadata.category
            category_distribution[cat] = category_distribution.get(cat, 0) + 1

        status_distribution = {}
        for entry in self._strategies.values():
            status = entry.metadata.status
            status_distribution[status] = status_distribution.get(status, 0) + 1

        return {
            'total_strategies': total_strategies,
            'healthy_strategies': healthy_strategies,
            'health_rate': health_rate,
            'category_distribution': category_distribution,
            'status_distribution': status_distribution,
            'average_usage_count': sum(s.usage_count for s in self._strategies.values()) / total_strategies,
            'most_used_strategy': max(self._strategies.values(), key=lambda s: s.usage_count).metadata.name,
            'least_used_strategy': min(self._strategies.values(), key=lambda s: s.usage_count).metadata.name
        }

    def _resolve_identifier(self, identifier: Union[str, Type[object]]) -> str:
        """Resolve identifier to registration ID."""
        if isinstance(identifier, str):
            # Check if it's a registration ID
            if identifier in self._strategies:
                return identifier
            # Check if it's a strategy name
            name_key = identifier.lower()
            if name_key in self._name_to_id:
                return self._name_to_id[name_key]
            raise StrategyNotFoundError(f"Strategy '{identifier}' not found")
        else:
            # It's a class, find by class
            for reg_id, entry in self._strategies.items():
                if entry.strategy_class is identifier:
                    return reg_id
            raise StrategyNotFoundError(f"Strategy class '{identifier.__name__}' not found")

    def _validate_strategy_class(self, strategy_class: Type[object], metadata: StrategyMetadata) -> None:
        """Validate strategy class structure."""
        # Check if it's a class
        if not inspect.isclass(strategy_class):
            raise ValueError("Strategy must be a class")

        # Check for required methods (basic validation)
        required_methods = ['init', 'next']  # Basic strategy interface
        for method in required_methods:
            if not hasattr(strategy_class, method):
                raise ValueError(f"Strategy class must have '{method}' method")

    def _update_indexes(self, entry: StrategyEntry) -> None:
        """Update search indexes for a strategy entry."""
        reg_id = entry.registration_id

        # Category index
        cat = entry.metadata.category
        if cat not in self._category_index:
            self._category_index[cat] = set()
        self._category_index[cat].add(reg_id)

        # Tag index
        for tag in entry.metadata.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(reg_id)

        # Author index
        author = entry.metadata.author
        if author not in self._author_index:
            self._author_index[author] = set()
        self._author_index[author].add(reg_id)

    def _remove_from_indexes(self, entry: StrategyEntry) -> None:
        """Remove strategy from search indexes."""
        reg_id = entry.registration_id

        # Category index
        cat = entry.metadata.category
        if cat in self._category_index:
            self._category_index[cat].discard(reg_id)
            if not self._category_index[cat]:
                del self._category_index[cat]

        # Tag index
        for tag in entry.metadata.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(reg_id)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]

        # Author index
        author = entry.metadata.author
        if author in self._author_index:
            self._author_index[author].discard(reg_id)
            if not self._author_index[author]:
                del self._author_index[author]

    def _calculate_search_score(self, entry: StrategyEntry, query: str) -> float:
        """Calculate search relevance score."""
        score = 0.0
        metadata = entry.metadata

        # Name match (highest weight)
        if query in metadata.name.lower():
            score += 10.0

        # Description match
        if query in metadata.description.lower():
            score += 5.0

        # Author match
        if query in metadata.author.lower():
            score += 3.0

        # Category match
        if query in metadata.category.value.lower():
            score += 2.0

        # Tag matches
        for tag in metadata.tags:
            if query in tag.lower():
                score += 1.5

        # Usage bonus (popular strategies rank higher)
        if entry.usage_count > 100:
            score += 1.0
        elif entry.usage_count > 50:
            score += 0.5

        # Health bonus (healthy strategies rank higher)
        score += entry.health_score * 0.5

        return score

# Global Registry Instance
_global_registry = StrategyRegistry()

# Convenience Functions (Backward Compatibility)
def register_strategy(strategy_cls: Type[object], *, name: Optional[str] = None,
                     overwrite: bool = False, metadata: Optional[StrategyMetadata] = None) -> str:
    """Register a strategy (convenience function)."""
    if metadata is None:
        # Create basic metadata
        strategy_name = name or strategy_cls.__name__
        metadata = StrategyMetadata(
            name=strategy_name,
            description=f"Strategy: {strategy_name}",
            category=StrategyCategory.CUSTOM,
            author="unknown",
            version="1.0.0"
        )

    return _global_registry.register_strategy(strategy_cls, metadata, overwrite)

def get_strategy(name: str) -> Type[object]:
    """Get strategy class by name (convenience function)."""
    return _global_registry.get_strategy_class(name)

def available_strategies() -> Iterable[str]:
    """List available strategy names (convenience function)."""
    return [entry.metadata.name for entry in _global_registry.list_strategies()]

def get_registry() -> StrategyRegistry:
    """Get the global registry instance."""
    return _global_registry

__all__ = [
    "StrategyRegistry",
    "StrategyMetadata",
    "StrategyEntry",
    "StrategyCategory",
    "StrategyStatus",
    "StrategyRisk",
    "DependencyType",
    "StrategyRegistryError",
    "StrategyNotFoundError",
    "StrategyAlreadyExistsError",
    "DependencyResolutionError",
    "register_strategy",
    "get_strategy",
    "available_strategies",
    "get_registry",
]

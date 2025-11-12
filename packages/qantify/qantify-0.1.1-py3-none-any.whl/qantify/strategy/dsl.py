"""Advanced Domain-Specific Language for Quantitative Trading Strategies.

This module provides a comprehensive declarative framework for defining trading strategies
with advanced conditional logic, risk management, multi-asset coordination, and adaptive rules.
"""

from __future__ import annotations

import asyncio
import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from functools import partial, wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Protocol, Union, Tuple, Set
from collections import defaultdict
import warnings
import re

import numpy as np
import pandas as pd

if TYPE_CHECKING:  # pragma: no cover
    from qantify.strategy.base import Strategy, IndicatorSeries, IndicatorFrame


# =============================================================================
# CORE TYPES AND PROTOCOLS
# =============================================================================

Condition = Callable[["Strategy"], bool]
Action = Callable[["Strategy"], None]
ConditionModifier = Callable[[Condition], Condition]


class RulePriority(Enum):
    """Rule execution priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class RuleState(Enum):
    """Rule execution states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    EXPIRED = "expired"
    FAILED = "failed"


class RuleCategory(Enum):
    """Rule categorization for organization."""
    ENTRY = "entry"
    EXIT = "exit"
    RISK_MANAGEMENT = "risk_management"
    POSITION_SIZING = "position_sizing"
    MARKET_TIMING = "market_timing"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    ADAPTIVE = "adaptive"
    MONITORING = "monitoring"


class ExecutionContext(Enum):
    """When rules should be evaluated."""
    ALWAYS = "always"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    SPECIFIC_TIME = "specific_time"
    BAR_CLOSE = "bar_close"
    TICK_UPDATE = "tick_update"
    VOLUME_SPIKE = "volume_spike"
    PRICE_SPIKE = "price_spike"


# =============================================================================
# ADVANCED RULE SYSTEM
# =============================================================================

@dataclass(slots=True)
class RuleMetadata:
    """Comprehensive metadata for rules."""
    name: str
    description: str = ""
    category: RuleCategory = RuleCategory.ENTRY
    priority: RulePriority = RulePriority.NORMAL
    state: RuleState = RuleState.ACTIVE
    execution_context: ExecutionContext = ExecutionContext.BAR_CLOSE
    max_executions: Optional[int] = None
    execution_count: int = 0
    cooldown_period: Optional[timedelta] = None
    last_execution: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    failure_count: int = 0
    success_count: int = 0

    def can_execute(self, current_time: datetime) -> bool:
        """Check if rule can be executed."""
        if self.state != RuleState.ACTIVE:
            return False

        if self.max_executions and self.execution_count >= self.max_executions:
            self.state = RuleState.EXPIRED
            return False

        if self.cooldown_period and self.last_execution:
            if current_time - self.last_execution < self.cooldown_period:
                return False

        return True

    def record_execution(self, success: bool, current_time: datetime):
        """Record rule execution."""
        self.execution_count += 1
        self.last_execution = current_time

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.updated_at = current_time

    def get_success_rate(self) -> float:
        """Calculate rule success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass(slots=True)
class Rule:
    """Advanced rule with metadata and execution control."""
    condition: Condition
    action: Action
    metadata: RuleMetadata

    def __post_init__(self):
        if not self.metadata.name:
            self.metadata.name = f"rule_{id(self)}"

    @property
    def name(self) -> str:
        return self.metadata.name

    def evaluate(self, strategy: "Strategy") -> bool:
        """Evaluate rule condition with error handling."""
        try:
            if not self.metadata.can_execute(strategy.now or datetime.now()):
                return False

            result = self.condition(strategy)

            # Record execution attempt
            self.metadata.record_execution(result, strategy.now or datetime.now())

            return result

        except Exception as e:
            warnings.warn(f"Rule '{self.name}' evaluation failed: {e}")
            self.metadata.record_execution(False, strategy.now or datetime.now())
            return False

    def execute(self, strategy: "Strategy") -> bool:
        """Execute rule action with error handling."""
        try:
            self.action(strategy)
            return True
        except Exception as e:
            warnings.warn(f"Rule '{self.name}' execution failed: {e}")
            return False


class CompositeCondition:
    """Advanced condition composition system."""

    def __init__(self, conditions: List[Condition], operator: str = "AND"):
        self.conditions = conditions
        self.operator = operator.upper()

    def __call__(self, strategy: "Strategy") -> bool:
        results = [cond(strategy) for cond in self.conditions]

        if self.operator == "AND":
            return all(results)
        elif self.operator == "OR":
            return any(results)
        elif self.operator == "NOT":
            return not any(results)
        elif self.operator == "XOR":
            return sum(results) == 1
        elif self.operator == "MAJORITY":
            return sum(results) > len(results) / 2
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    @classmethod
    def AND(cls, *conditions: Condition) -> "CompositeCondition":
        return cls(list(conditions), "AND")

    @classmethod
    def OR(cls, *conditions: Condition) -> "CompositeCondition":
        return cls(list(conditions), "OR")

    @classmethod
    def NOT(cls, condition: Condition) -> "CompositeCondition":
        return cls([condition], "NOT")

    @classmethod
    def XOR(cls, *conditions: Condition) -> "CompositeCondition":
        return cls(list(conditions), "XOR")


class ConditionalModifier:
    """Condition modifiers for advanced logic."""

    @staticmethod
    def debounce(condition: Condition, wait_periods: int) -> Condition:
        """Debounce condition - only trigger after stable for N periods."""
        last_trigger = None

        def debounced_condition(strategy: "Strategy") -> bool:
            nonlocal last_trigger

            current_index = strategy.index
            if condition(strategy):
                if last_trigger is None or current_index - last_trigger >= wait_periods:
                    last_trigger = current_index
                    return True
            else:
                last_trigger = None

            return False

        return debounced_condition

    @staticmethod
    def throttle(condition: Condition, min_interval: int) -> Condition:
        """Throttle condition - limit execution frequency."""
        last_execution = None

        def throttled_condition(strategy: "Strategy") -> bool:
            nonlocal last_execution

            current_index = strategy.index
            if condition(strategy):
                if last_execution is None or current_index - last_execution >= min_interval:
                    last_execution = current_index
                    return True

            return False

        return throttled_condition

    @staticmethod
    def with_timeout(condition: Condition, timeout_bars: int) -> Condition:
        """Add timeout to condition - must trigger within N bars."""
        first_true = None

        def timeout_condition(strategy: "Strategy") -> bool:
            nonlocal first_true

            current_index = strategy.index

            if condition(strategy):
                if first_true is None:
                    first_true = current_index
                return True
            else:
                if first_true is not None and current_index - first_true >= timeout_bars:
                    first_true = None  # Reset for next opportunity
                return False

        return timeout_condition

    @staticmethod
    def probability_filter(condition: Condition, probability: float) -> Condition:
        """Add probabilistic filtering to condition."""
        def probabilistic_condition(strategy: "Strategy") -> bool:
            if condition(strategy):
                return np.random.random() < probability
            return False

        return probabilistic_condition


# =============================================================================
# CONDITION BUILDERS
# =============================================================================

class ConditionBuilder:
    """Fluent interface for building complex conditions."""

    def __init__(self, base_condition: Optional[Condition] = None):
        self.conditions: List[Condition] = []
        if base_condition:
            self.conditions.append(base_condition)

    def add(self, condition: Condition) -> "ConditionBuilder":
        """Add another condition."""
        self.conditions.append(condition)
        return self

    def AND(self) -> Condition:
        """Combine conditions with AND logic."""
        return CompositeCondition.AND(*self.conditions)

    def OR(self) -> Condition:
        """Combine conditions with OR logic."""
        return CompositeCondition.OR(*self.conditions)

    def NOT(self) -> Condition:
        """Negate the condition."""
        if len(self.conditions) == 1:
            return CompositeCondition.NOT(self.conditions[0])
        raise ValueError("NOT requires exactly one condition")

    def debounce(self, wait_periods: int) -> "ConditionBuilder":
        """Apply debounce modifier."""
        if self.conditions:
            self.conditions[-1] = ConditionalModifier.debounce(self.conditions[-1], wait_periods)
        return self

    def throttle(self, min_interval: int) -> "ConditionBuilder":
        """Apply throttle modifier."""
        if self.conditions:
            self.conditions[-1] = ConditionalModifier.throttle(self.conditions[-1], min_interval)
        return self

    def with_timeout(self, timeout_bars: int) -> "ConditionBuilder":
        """Apply timeout modifier."""
        if self.conditions:
            self.conditions[-1] = ConditionalModifier.with_timeout(self.conditions[-1], timeout_bars)
        return self

    def with_probability(self, probability: float) -> "ConditionBuilder":
        """Apply probability filter."""
        if self.conditions:
            self.conditions[-1] = ConditionalModifier.probability_filter(self.conditions[-1], probability)
        return self


class IndicatorConditionBuilder:
    """Specialized builder for indicator-based conditions."""

    def __init__(self, strategy_ref: str = "strategy"):
        self.strategy_ref = strategy_ref
        self.conditions: List[str] = []

    def cross_above(self, indicator1: str, indicator2: Union[str, float]) -> "IndicatorConditionBuilder":
        """Indicator crossover above condition."""
        if isinstance(indicator2, str):
            self.conditions.append(f"{self.strategy_ref}.{indicator1}.cross_above({self.strategy_ref}.{indicator2})")
        else:
            self.conditions.append(f"{self.strategy_ref}.{indicator1}.above({indicator2})")
        return self

    def cross_below(self, indicator1: str, indicator2: Union[str, float]) -> "IndicatorConditionBuilder":
        """Indicator crossover below condition."""
        if isinstance(indicator2, str):
            self.conditions.append(f"{self.strategy_ref}.{indicator1}.cross_below({self.strategy_ref}.{indicator2})")
        else:
            self.conditions.append(f"{self.strategy_ref}.{indicator1}.below({indicator2})")
        return self

    def above(self, indicator: str, value: Union[str, float]) -> "IndicatorConditionBuilder":
        """Indicator above value condition."""
        if isinstance(value, str):
            self.conditions.append(f"{self.strategy_ref}.{indicator}.above({self.strategy_ref}.{value})")
        else:
            self.conditions.append(f"{self.strategy_ref}.{indicator}.above({value})")
        return self

    def below(self, indicator: str, value: Union[str, float]) -> "IndicatorConditionBuilder":
        """Indicator below value condition."""
        if isinstance(value, str):
            self.conditions.append(f"{self.strategy_ref}.{indicator}.below({self.strategy_ref}.{value})")
        else:
            self.conditions.append(f"{self.strategy_ref}.{indicator}.below({value})")
        return self

    def between(self, indicator: str, lower: float, upper: float) -> "IndicatorConditionBuilder":
        """Indicator between values condition."""
        self.conditions.append(f"{lower} <= {self.strategy_ref}.{indicator}.current <= {upper}")
        return self

    def trending_up(self, indicator: str, periods: int = 5) -> "IndicatorConditionBuilder":
        """Indicator trending upward."""
        self.conditions.append(f"{self.strategy_ref}.{indicator}.current > {self.strategy_ref}.{indicator}.shift({periods})")
        return self

    def trending_down(self, indicator: str, periods: int = 5) -> "IndicatorConditionBuilder":
        """Indicator trending downward."""
        self.conditions.append(f"{self.strategy_ref}.{indicator}.current < {self.strategy_ref}.{indicator}.shift({periods})")
        return self

    def to_condition(self) -> Condition:
        """Convert to executable condition."""
        if not self.conditions:
            return lambda s: True

        condition_code = " and ".join(f"({cond})" for cond in self.conditions)

        def dynamic_condition(strategy: "Strategy") -> bool:
            try:
                # Create a local namespace with strategy reference
                namespace = {'strategy': strategy, 'np': np, 'pd': pd}
                return eval(condition_code, namespace)
            except Exception as e:
                warnings.warn(f"Condition evaluation failed: {e}")
                return False

        return dynamic_condition


# =============================================================================
# ACTION BUILDERS
# =============================================================================

class ActionBuilder:
    """Fluent interface for building complex actions."""

    def __init__(self):
        self.actions: List[Action] = []

    def add(self, action: Action) -> "ActionBuilder":
        """Add an action."""
        self.actions.append(action)
        return self

    def buy(self, size: Union[float, str] = 1.0, symbol: Optional[str] = None) -> "ActionBuilder":
        """Add buy action."""
        def buy_action(strategy: "Strategy"):
            if isinstance(size, str):
                actual_size = getattr(strategy, size, 1.0)
            else:
                actual_size = size
            strategy.buy(size=actual_size, symbol=symbol)
        self.actions.append(buy_action)
        return self

    def sell(self, size: Union[float, str] = 1.0, symbol: Optional[str] = None) -> "ActionBuilder":
        """Add sell action."""
        def sell_action(strategy: "Strategy"):
            if isinstance(size, str):
                actual_size = getattr(strategy, size, 1.0)
            else:
                actual_size = size
            strategy.sell(size=actual_size, symbol=symbol)
        self.actions.append(sell_action)
        return self

    def close_position(self, symbol: Optional[str] = None) -> "ActionBuilder":
        """Add close position action."""
        def close_action(strategy: "Strategy"):
            strategy.close(symbol=symbol)
        self.actions.append(close_action)
        return self

    def log(self, message: str, **fields) -> "ActionBuilder":
        """Add logging action."""
        def log_action(strategy: "Strategy"):
            strategy.log(message, **fields)
        self.actions.append(log_action)
        return self

    def set_state(self, key: str, value: Any) -> "ActionBuilder":
        """Add state setting action."""
        def set_state_action(strategy: "Strategy"):
            strategy.set_state(key, value)
        self.actions.append(set_state_action)
        return self

    def limit_order(self, price: Union[float, str], side: str, size: Union[float, str] = 1.0,
                   symbol: Optional[str] = None) -> "ActionBuilder":
        """Add limit order action."""
        def limit_action(strategy: "Strategy"):
            if isinstance(price, str):
                actual_price = getattr(strategy, price, strategy.price())
            else:
                actual_price = price

            if isinstance(size, str):
                actual_size = getattr(strategy, size, 1.0)
            else:
                actual_size = size

            if side.lower() == 'buy':
                strategy.limit(actual_price, size=actual_size, symbol=symbol)
            else:
                strategy.limit(actual_price, side='sell', size=actual_size, symbol=symbol)

        self.actions.append(limit_action)
        return self

    def stop_order(self, price: Union[float, str], side: str, size: Union[float, str] = 1.0,
                  symbol: Optional[str] = None) -> "ActionBuilder":
        """Add stop order action."""
        def stop_action(strategy: "Strategy"):
            if isinstance(price, str):
                actual_price = getattr(strategy, price, strategy.price())
            else:
                actual_price = price

            if isinstance(size, str):
                actual_size = getattr(strategy, size, 1.0)
            else:
                actual_size = size

            strategy.stop(actual_price, side=side, size=actual_size, symbol=symbol)

        self.actions.append(stop_action)
        return self

    def to_action(self) -> Action:
        """Convert to executable action."""
        def composite_action(strategy: "Strategy"):
            for action in self.actions:
                try:
                    action(strategy)
                except Exception as e:
                    warnings.warn(f"Action execution failed: {e}")

        return composite_action


# =============================================================================
# RULE BUILDERS AND DSL
# =============================================================================

class RuleBuilder:
    """Advanced rule builder with fluent interface."""

    def __init__(self, condition: Condition, name: Optional[str] = None):
        self.condition = condition
        self.metadata = RuleMetadata(
            name=name or f"rule_{id(self)}",
            description="",
            category=RuleCategory.ENTRY,
            priority=RulePriority.NORMAL
        )

    def named(self, name: str) -> "RuleBuilder":
        """Set rule name."""
        self.metadata.name = name
        return self

    def described_as(self, description: str) -> "RuleBuilder":
        """Set rule description."""
        self.metadata.description = description
        return self

    def with_category(self, category: RuleCategory) -> "RuleBuilder":
        """Set rule category."""
        self.metadata.category = category
        return self

    def with_priority(self, priority: RulePriority) -> "RuleBuilder":
        """Set rule priority."""
        self.metadata.priority = priority
        return self

    def with_cooldown(self, cooldown: timedelta) -> "RuleBuilder":
        """Set cooldown period."""
        self.metadata.cooldown_period = cooldown
        return self

    def with_max_executions(self, max_executions: int) -> "RuleBuilder":
        """Set maximum executions."""
        self.metadata.max_executions = max_executions
        return self

    def with_tags(self, *tags: str) -> "RuleBuilder":
        """Add tags."""
        self.metadata.tags.update(tags)
        return self

    def depends_on(self, *rule_names: str) -> "RuleBuilder":
        """Set dependencies."""
        self.metadata.dependencies.update(rule_names)
        return self

    def executes_in(self, context: ExecutionContext) -> "RuleBuilder":
        """Set execution context."""
        self.metadata.execution_context = context
        return self

    def then(self, action: Action) -> Rule:
        """Build the final rule."""
        return Rule(
            condition=self.condition,
            action=action,
            metadata=self.metadata
        )


def when(condition: Union[Condition, str], *, name: Optional[str] = None) -> RuleBuilder:
    """Create a rule builder from condition."""
    if isinstance(condition, str):
        # Parse string condition
        def string_condition(strategy: "Strategy") -> bool:
            try:
                namespace = {'strategy': strategy, 'np': np, 'pd': pd}
                return eval(condition, namespace)
            except Exception as e:
                warnings.warn(f"String condition evaluation failed: {e}")
                return False
        condition = string_condition

    return RuleBuilder(condition, name=name)


def when_indicators(*, strategy_ref: str = "strategy") -> IndicatorConditionBuilder:
    """Create indicator-based condition builder."""
    return IndicatorConditionBuilder(strategy_ref)


def do(*actions: Action) -> ActionBuilder:
    """Create action builder."""
    builder = ActionBuilder()
    for action in actions:
        builder.add(action)
    return builder


# =============================================================================
# ADVANCED RULE MANAGEMENT
# =============================================================================

class RuleEngine:
    """Advanced rule execution engine with prioritization and conflict resolution."""

    def __init__(self):
        self.rules: List[Rule] = []
        self.rule_index: Dict[str, Rule] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.conflict_resolver = self._default_conflict_resolver

    def add_rule(self, rule: Rule):
        """Add a rule to the engine."""
        if rule.name in self.rule_index:
            warnings.warn(f"Rule '{rule.name}' already exists, replacing")
            self.remove_rule(rule.name)

        self.rules.append(rule)
        self.rule_index[rule.name] = rule

        # Sort rules by priority
        self.rules.sort(key=lambda r: r.metadata.priority.value)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        if rule_name not in self.rule_index:
            return False

        rule = self.rule_index[rule_name]
        self.rules.remove(rule)
        del self.rule_index[rule_name]
        return True

    def get_rule(self, rule_name: str) -> Optional[Rule]:
        """Get rule by name."""
        return self.rule_index.get(rule_name)

    def list_rules(self, category: Optional[RuleCategory] = None,
                  state: Optional[RuleState] = None) -> List[Rule]:
        """List rules with optional filtering."""
        rules = self.rules

        if category:
            rules = [r for r in rules if r.metadata.category == category]

        if state:
            rules = [r for r in rules if r.metadata.state == state]

        return rules

    def execute_rules(self, strategy: "Strategy", context: ExecutionContext = ExecutionContext.BAR_CLOSE) -> List[str]:
        """Execute applicable rules."""
        executed_rules = []
        conflicting_actions = []

        # Group rules by priority
        priority_groups = defaultdict(list)
        for rule in self.rules:
            if rule.metadata.execution_context == context or rule.metadata.execution_context == ExecutionContext.ALWAYS:
                priority_groups[rule.metadata.priority].append(rule)

        # Execute rules by priority
        for priority in sorted(priority_groups.keys()):
            priority_rules = priority_groups[priority]

            for rule in priority_rules:
                if rule.evaluate(strategy):
                    # Check for conflicts
                    if self._has_conflicts(rule, executed_rules):
                        conflicting_actions.append(rule.name)
                        continue

                    rule.execute(strategy)
                    executed_rules.append(rule.name)

                    # Record execution
                    self.execution_history.append({
                        'rule_name': rule.name,
                        'timestamp': strategy.now,
                        'success': True,
                        'context': context.value
                    })

        return executed_rules

    def _has_conflicts(self, rule: Rule, executed_rules: List[str]) -> bool:
        """Check if rule conflicts with previously executed rules."""
        # Check dependencies
        for dep in rule.metadata.dependencies:
            if dep not in executed_rules:
                return True

        # Custom conflict resolution
        return self.conflict_resolver(rule, executed_rules)

    def _default_conflict_resolver(self, rule: Rule, executed_rules: List[str]) -> bool:
        """Default conflict resolution logic."""
        # Simple logic: no conflicts by default
        # Can be customized based on rule categories
        executed_categories = {self.rule_index[name].metadata.category for name in executed_rules}

        # Prevent multiple entries/exits in same bar
        if (rule.metadata.category in [RuleCategory.ENTRY, RuleCategory.EXIT] and
            rule.metadata.category in executed_categories):
            return True

        return False

    def set_conflict_resolver(self, resolver: Callable[[Rule, List[str]], bool]):
        """Set custom conflict resolver."""
        self.conflict_resolver = resolver

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        stats = {
            'total_rules': len(self.rules),
            'executions': len(self.execution_history),
            'successful_executions': sum(1 for h in self.execution_history if h['success']),
            'rule_performance': {}
        }

        # Per-rule statistics
        rule_stats = defaultdict(lambda: {'executions': 0, 'successes': 0})
        for execution in self.execution_history:
            rule_name = execution['rule_name']
            rule_stats[rule_name]['executions'] += 1
            if execution['success']:
                rule_stats[rule_name]['successes'] += 1

        for rule_name, stat in rule_stats.items():
            stat['success_rate'] = stat['successes'] / stat['executions'] if stat['executions'] > 0 else 0

        stats['rule_performance'] = dict(rule_stats)
        return stats


# =============================================================================
# TIME-BASED AND EVENT-BASED RULES
# =============================================================================

class TimeBasedRule(Rule):
    """Rule that executes at specific times."""

    def __init__(self, condition: Condition, action: Action, execution_time: time,
                 metadata: RuleMetadata):
        super().__init__(condition, action, metadata)
        self.execution_time = execution_time

    def should_execute_now(self, current_time: datetime) -> bool:
        """Check if rule should execute at current time."""
        return (current_time.time().hour == self.execution_time.hour and
                current_time.time().minute == self.execution_time.minute)


class EventBasedRule(Rule):
    """Rule that executes on specific events."""

    def __init__(self, condition: Condition, action: Action, event_type: str,
                 metadata: RuleMetadata):
        super().__init__(condition, action, metadata)
        self.event_type = event_type


class AdaptiveRule(Rule):
    """Rule that adapts its behavior based on performance."""

    def __init__(self, base_condition: Condition, action: Action, adaptation_logic: Callable,
                 metadata: RuleMetadata):
        super().__init__(base_condition, action, metadata)
        self.adaptation_logic = adaptation_logic
        self.performance_history = []

    def adapt(self, performance_metrics: Dict[str, float]):
        """Adapt rule based on performance."""
        self.performance_history.append(performance_metrics)

        # Apply adaptation logic
        try:
            self.condition = self.adaptation_logic(self.condition, self.performance_history)
        except Exception as e:
            warnings.warn(f"Rule adaptation failed: {e}")


# =============================================================================
# MULTI-ASSET AND PORTFOLIO RULES
# =============================================================================

class MultiAssetRule(Rule):
    """Rule that operates across multiple assets."""

    def __init__(self, condition: Condition, action: Action, assets: List[str],
                 coordination_logic: str, metadata: RuleMetadata):
        super().__init__(condition, action, metadata)
        self.assets = assets
        self.coordination_logic = coordination_logic  # "sequential", "parallel", "weighted"

    def evaluate_multi_asset(self, strategy: "Strategy") -> Dict[str, bool]:
        """Evaluate condition for each asset."""
        results = {}
        for asset in self.assets:
            # Temporarily switch strategy context to asset
            original_symbol = strategy.symbol
            original_data = strategy.data

            try:
                strategy.symbol = asset
                strategy.data = strategy.data_for(asset)
                results[asset] = self.condition(strategy)
            finally:
                # Restore original context
                strategy.symbol = original_symbol
                strategy.data = original_data

        return results

    def execute_coordinated(self, strategy: "Strategy", asset_results: Dict[str, bool]):
        """Execute action with coordination across assets."""
        if self.coordination_logic == "sequential":
            for asset, should_execute in asset_results.items():
                if should_execute:
                    self._execute_for_asset(strategy, asset)

        elif self.coordination_logic == "parallel":
            for asset, should_execute in asset_results.items():
                if should_execute:
                    # Execute in parallel (simplified)
                    self._execute_for_asset(strategy, asset)

        elif self.coordination_logic == "weighted":
            # Weighted execution based on some criteria
            total_signals = sum(asset_results.values())
            if total_signals > 0:
                for asset, should_execute in asset_results.items():
                    if should_execute:
                        weight = 1.0 / total_signals
                        self._execute_weighted(strategy, asset, weight)

    def _execute_for_asset(self, strategy: "Strategy", asset: str):
        """Execute action for specific asset."""
        original_symbol = strategy.symbol
        try:
            strategy.symbol = asset
            self.action(strategy)
        finally:
            strategy.symbol = original_symbol

    def _execute_weighted(self, strategy: "Strategy", asset: str, weight: float):
        """Execute action with weight for specific asset."""
        # Implementation depends on action type
        pass


# =============================================================================
# RULE TEMPLATES AND PRESETS
# =============================================================================

class RuleTemplates:
    """Pre-built rule templates for common strategies."""

    @staticmethod
    def moving_average_crossover(fast_period: int = 20, slow_period: int = 50) -> Rule:
        """Moving average crossover entry rule."""
        condition = lambda s: s.I(lambda x: x['close'].rolling(fast_period).mean(), name='fast_ma').cross_above(
                               s.I(lambda x: x['close'].rolling(slow_period).mean(), name='slow_ma'))

        action = lambda s: s.buy(size=1.0)

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"ma_crossover_{fast_period}_{slow_period}",
                description=f"Moving average crossover ({fast_period}, {slow_period})",
                category=RuleCategory.ENTRY
            )
        )

    @staticmethod
    def rsi_divergence(rsi_period: int = 14, overbought: int = 70) -> Rule:
        """RSI overbought exit rule."""
        condition = lambda s: s.I(lambda x: x['close'].rolling(rsi_period).mean(), name='rsi').above(overbought)

        action = lambda s: s.sell(size=0.5)

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"rsi_overbought_{rsi_period}_{overbought}",
                description=f"RSI overbought exit at {overbought}",
                category=RuleCategory.EXIT
            )
        )

    @staticmethod
    def stop_loss_loss_percentage(loss_threshold: float = 0.05) -> Rule:
        """Stop loss rule based on percentage loss."""
        condition = lambda s: (s.equity / s.portfolio_state.initial_equity - 1) < -loss_threshold

        action = lambda s: s.close()

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"stop_loss_{loss_threshold:.0%}",
                description=f"Stop loss at {loss_threshold:.0%} loss",
                category=RuleCategory.RISK_MANAGEMENT,
                priority=RulePriority.CRITICAL
            )
        )

    @staticmethod
    def take_profit_percentage(gain_threshold: float = 0.10) -> Rule:
        """Take profit rule based on percentage gain."""
        condition = lambda s: (s.equity / s.portfolio_state.initial_equity - 1) > gain_threshold

        action = lambda s: s.close()

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"take_profit_{gain_threshold:.0%}",
                description=f"Take profit at {gain_threshold:.0%} gain",
                category=RuleCategory.EXIT
            )
        )

    @staticmethod
    def volume_spike_threshold(multiplier: float = 2.0, lookback: int = 20) -> Rule:
        """Volume spike entry rule."""
        condition = lambda s: s.data['volume'].iloc[s.index] > (s.data['volume'].rolling(lookback).mean().iloc[s.index] * multiplier)

        action = lambda s: s.buy(size=0.5)

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"volume_spike_{multiplier}x_{lookback}",
                description=f"Volume spike {multiplier}x above {lookback}-period average",
                category=RuleCategory.ENTRY
            )
        )

    @staticmethod
    def bollinger_breakout(period: int = 20, deviation: float = 2.0) -> Rule:
        """Bollinger Band breakout rule."""
        def condition(s):
            close = s.data['close'].iloc[s.index]
            sma = s.data['close'].rolling(period).mean().iloc[s.index]
            std = s.data['close'].rolling(period).std().iloc[s.index]
            upper_band = sma + (std * deviation)
            return close > upper_band

        action = lambda s: s.buy(size=1.0)

        return Rule(
            condition=condition,
            action=action,
            metadata=RuleMetadata(
                name=f"bollinger_breakout_{period}_{deviation}",
                description=f"Bollinger breakout ({period}, {deviation}σ)",
                category=RuleCategory.ENTRY
            )
        )


# =============================================================================
# DSL SHORTCUTS AND UTILITIES
# =============================================================================

# Convenience functions for common operations
def buy_signal(size: Union[float, str] = 1.0, symbol: Optional[str] = None) -> Action:
    """Create a buy action."""
    return lambda s: s.buy(size=size, symbol=symbol)

def sell_signal(size: Union[float, str] = 1.0, symbol: Optional[str] = None) -> Action:
    """Create a sell action."""
    return lambda s: s.sell(size=size, symbol=symbol)

def log_signal(message: str, **fields) -> Action:
    """Create a logging action."""
    return lambda s: s.log(message, **fields)

def close_all_positions() -> Action:
    """Create a close all positions action."""
    return lambda s: s.close()

def limit_buy(price: Union[float, str], size: Union[float, str] = 1.0) -> Action:
    """Create a limit buy action."""
    return lambda s: s.limit(price, size=size, symbol=s.symbol)

def limit_sell(price: Union[float, str], size: Union[float, str] = 1.0) -> Action:
    """Create a limit sell action."""
    return lambda s: s.limit(price, side='sell', size=size, symbol=s.symbol)


__all__ = [
    # Core classes
    "Rule", "RuleMetadata", "RuleBuilder", "RuleEngine",

    # Builders
    "ConditionBuilder", "ActionBuilder", "IndicatorConditionBuilder",

    # Advanced rules
    "TimeBasedRule", "EventBasedRule", "AdaptiveRule", "MultiAssetRule",

    # Templates
    "RuleTemplates",

    # Enums
    "RulePriority", "RuleState", "RuleCategory", "ExecutionContext",

    # DSL functions
    "when", "when_indicators", "do",

    # Action shortcuts
    "buy_signal", "sell_signal", "log_signal", "close_all_positions",
    "limit_buy", "limit_sell",

    # Condition utilities
    "CompositeCondition", "ConditionalModifier",
]

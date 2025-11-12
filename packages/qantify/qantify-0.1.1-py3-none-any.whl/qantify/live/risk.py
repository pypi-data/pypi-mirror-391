"""Advanced live trading risk management with institutional-grade controls."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from qantify.backtest.portfolio import Portfolio
from qantify.backtest.types import OrderSide
from qantify.data.streaming import MarketData, DataFeedType


logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskViolationType(Enum):
    """Types of risk violations."""
    POSITION_SIZE = "position_size"
    NOTIONAL_EXPOSURE = "notional_exposure"
    DRAWDOWN = "drawdown"
    DAILY_LOSS = "daily_loss"
    CONCENTRATION = "concentration"
    VOLATILITY = "volatility"
    CORRELATION = "correlation"
    LIQUIDITY = "liquidity"
    MARKET_IMPACT = "market_impact"
    COUNTERPARTY = "counterparty"


@dataclass(slots=True)
class RiskViolation:
    """Risk violation record."""
    violation_type: RiskViolationType
    severity: RiskLevel
    symbol: Optional[str]
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskMetrics:
    """Comprehensive risk metrics."""
    # Portfolio level
    total_equity: float = 0.0
    portfolio_value: float = 0.0
    buying_power: float = 0.0
    maintenance_margin: float = 0.0
    leverage_ratio: float = 0.0

    # Risk measures
    value_at_risk_95: float = 0.0  # 95% VaR
    expected_shortfall_95: float = 0.0  # 95% ES
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0

    # Position metrics
    position_count: int = 0
    largest_position_pct: float = 0.0
    concentration_ratio: float = 0.0

    # Performance metrics
    daily_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    # Market risk
    beta_to_market: float = 0.0
    market_volatility: float = 0.0
    portfolio_volatility: float = 0.0

    # Liquidity metrics
    liquidity_ratio: float = 0.0
    time_to_liquidate: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class RiskLimits:
    """Dynamic risk limits that adapt to market conditions."""
    # Static limits
    max_position_size: Optional[float] = None
    max_notional: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_leverage: Optional[float] = None

    # Dynamic limits (adjust based on market conditions)
    volatility_adjustment: bool = True
    market_regime_adjustment: bool = True
    correlation_adjustment: bool = True

    # Market condition multipliers
    high_volatility_multiplier: float = 0.7  # Reduce limits by 30% in high vol
    low_volatility_multiplier: float = 1.2   # Increase limits by 20% in low vol
    stressed_market_multiplier: float = 0.5  # Reduce limits by 50% in stressed markets

    # Position limits
    max_positions: int = 20
    max_sector_exposure: float = 0.3  # 30% max per sector
    max_region_exposure: float = 0.5  # 50% max per region

    # Trading limits
    max_orders_per_minute: int = 10
    max_notional_per_minute: float = 100000
    min_order_interval: float = 0.1  # seconds

    # Circuit breakers
    circuit_breaker_enabled: bool = True
    circuit_breaker_drawdown: float = 0.05  # 5% drawdown triggers circuit breaker
    circuit_breaker_daily_loss: float = 0.03  # 3% daily loss triggers circuit breaker


GuardFunction = Callable[[Portfolio, Dict[str, float]], bool]


@dataclass(slots=True)
class RiskConfig:
    """Enhanced risk configuration with dynamic limits."""
    # Core limits
    max_position_size: Optional[float] = None
    max_notional: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_unrealized_loss: Optional[float] = None
    daily_loss_limit: Optional[float] = None

    # Advanced limits
    max_leverage: Optional[float] = None
    max_concentration: Optional[float] = None
    max_var_95: Optional[float] = None
    max_expected_shortfall: Optional[float] = None

    # Trading controls
    throttle_threshold: Optional[int] = None
    throttle_window: int = 60
    trade_cooldown: Optional[int] = None
    max_orders_per_minute: int = 10

    # Market-aware limits
    volatility_based_limits: bool = True
    correlation_limits: bool = True
    liquidity_limits: bool = True

    # Emergency controls
    auto_hedge_threshold: Optional[float] = None
    auto_reduce_threshold: Optional[float] = None
    emergency_stop_loss: Optional[float] = None


class RiskGuardrails:
    """Advanced risk management system with real-time monitoring and dynamic limits."""

    def __init__(self, config: RiskConfig, limits: Optional[RiskLimits] = None) -> None:
        self.config = config
        self.limits = limits or RiskLimits()

        # Core tracking
        self.order_counts: Dict[str, deque[datetime]] = defaultdict(lambda: deque(maxlen=1000))
        self.portfolio_history: deque[Tuple[datetime, float]] = deque(maxlen=10000)
        self.last_trade_time: Dict[str, datetime] = {}
        self.daily_pnl: Dict[str, float] = {}

        # Risk tracking
        self.violations: deque[RiskViolation] = deque(maxlen=1000)
        self.risk_metrics_history: deque[RiskMetrics] = deque(maxlen=1000)
        self.market_data_cache: Dict[str, MarketData] = {}

        # Position tracking
        self.position_volatility: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=100))
        self.position_correlations: Dict[Tuple[str, str], float] = {}
        self.sector_exposure: Dict[str, float] = {}
        self.region_exposure: Dict[str, float] = {}

        # Trading activity tracking
        self.order_timestamps: deque[datetime] = deque(maxlen=1000)
        self.notional_traded: deque[float] = deque(maxlen=1000)

        # Circuit breaker state
        self.circuit_breaker_triggered: bool = False
        self.circuit_breaker_timestamp: Optional[datetime] = None
        self.emergency_stop_triggered: bool = False

        # Background tasks
        self._risk_monitor_task: Optional[asyncio.Task] = None
        self._metrics_update_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start risk monitoring."""
        if self._running:
            return

        self._running = True
        logger.info("Starting advanced risk management system")

        # Start background tasks
        self._risk_monitor_task = asyncio.create_task(self._continuous_risk_monitor())
        self._metrics_update_task = asyncio.create_task(self._periodic_metrics_update())

    async def stop(self) -> None:
        """Stop risk monitoring."""
        self._running = False

        # Cancel tasks
        tasks = [self._risk_monitor_task, self._metrics_update_task]
        for task in tasks:
            if task:
                task.cancel()

        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        logger.info("Risk management system stopped")

    def update_market_data(self, symbol: str, market_data: MarketData) -> None:
        """Update market data for risk calculations."""
        self.market_data_cache[symbol] = market_data

        # Update volatility tracking
        if market_data.price is not None:
            self.position_volatility[symbol].append(market_data.price)

    def get_dynamic_limit(self, limit_type: str, base_limit: Optional[float],
                         symbol: Optional[str] = None) -> Optional[float]:
        """Calculate dynamic limit based on market conditions."""
        if not base_limit:
            return None

        multiplier = 1.0

        # Volatility adjustment
        if self.limits.volatility_adjustment and symbol:
            volatility = self._calculate_volatility(symbol)
            if volatility > 0.05:  # High volatility
                multiplier *= self.limits.high_volatility_multiplier
            elif volatility < 0.01:  # Low volatility
                multiplier *= self.limits.low_volatility_multiplier

        # Market regime adjustment
        if self.limits.market_regime_adjustment:
            regime_multiplier = self._get_market_regime_multiplier()
            multiplier *= regime_multiplier

        return base_limit * multiplier

    def _calculate_volatility(self, symbol: str) -> float:
        """Calculate position volatility."""
        prices = list(self.position_volatility[symbol])
        if len(prices) < 10:
            return 0.02  # Default 2%

        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(252)  # Annualized

    def _get_market_regime_multiplier(self) -> float:
        """Get multiplier based on market regime."""
        # This would integrate with market regime detection
        # For now, return neutral multiplier
        return 1.0

    def record_portfolio(self, timestamp: datetime, equity: float) -> None:
        """Record portfolio equity for risk tracking."""
        self.portfolio_history.append((timestamp, equity))
        date_key = timestamp.date().isoformat()
        self.daily_pnl[date_key] = equity

    def current_equity(self) -> float:
        """Get current portfolio equity."""
        if not self.portfolio_history:
            return 0.0
        return self.portfolio_history[-1][1]

    def check_order(
        self,
        portfolio: Portfolio,
        *,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        timestamp: datetime,
    ) -> bool:
        """Enhanced order risk check with dynamic limits."""
        # Get dynamic limits
        max_pos_size = self.get_dynamic_limit("position_size", self.config.max_position_size, symbol)
        max_notional = self.get_dynamic_limit("notional", self.config.max_notional, symbol)

        # Check position size
        if not self._check_position_limit(portfolio, symbol, side, quantity, max_pos_size):
            return False

        # Check notional exposure
        if not self._check_notional_limit(symbol, side, quantity, price, max_notional):
            return False

        # Check trading throttle
        if not self._check_throttle(symbol, timestamp):
            return False

        # Check circuit breaker
        if self.circuit_breaker_triggered:
            logger.warning("Circuit breaker active - order rejected")
            return False

        # Record order activity
        self.order_timestamps.append(timestamp)
        self.notional_traded.append(quantity * price)

        return True

    def _check_position_limit(
        self,
        portfolio: Portfolio,
        symbol: str,
        side: OrderSide,
        quantity: float,
        max_position_size: Optional[float]
    ) -> bool:
        """Check position size limits."""
        if not max_position_size:
            return True

        position = portfolio.state.positions.get(symbol)
        current_qty = position.quantity if position else 0.0
        projected = current_qty + quantity if side == OrderSide.BUY else current_qty - quantity

        if abs(projected) > max_position_size:
            violation = RiskViolation(
                violation_type=RiskViolationType.POSITION_SIZE,
                severity=RiskLevel.HIGH,
                symbol=symbol,
                value=abs(projected),
                threshold=max_position_size,
                description=f"Position size {abs(projected)} exceeds limit {max_position_size}"
            )
            self._record_violation(violation)
            return False

        return True

    def _check_notional_limit(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        max_notional: Optional[float]
    ) -> bool:
        """Check notional exposure limits."""
        if not max_notional:
            return True

        notional = quantity * price
        if notional > max_notional:
            violation = RiskViolation(
                violation_type=RiskViolationType.NOTIONAL_EXPOSURE,
                severity=RiskLevel.MEDIUM,
                symbol=symbol,
                value=notional,
                threshold=max_notional,
                description=f"Notional exposure {notional} exceeds limit {max_notional}"
            )
            self._record_violation(violation)
            return False

        return True

    def _check_throttle(self, symbol: str, timestamp: datetime) -> bool:
        """Check trading throttle limits."""
        # Remove old timestamps
        cutoff = timestamp - timedelta(seconds=self.config.throttle_window)
        while self.order_counts[symbol] and self.order_counts[symbol][0] < cutoff:
            self.order_counts[symbol].popleft()

        # Check throttle threshold
        if self.config.throttle_threshold and len(self.order_counts[symbol]) >= self.config.throttle_threshold:
            violation = RiskViolation(
                violation_type=RiskViolationType.POSITION_SIZE,  # Reusing for throttle
                severity=RiskLevel.LOW,
                symbol=symbol,
                value=len(self.order_counts[symbol]),
                threshold=self.config.throttle_threshold,
                description=f"Throttle limit exceeded: {len(self.order_counts[symbol])} orders in {self.config.throttle_window}s"
            )
            self._record_violation(violation)
            return False

        # Check trade cooldown
        if self.config.trade_cooldown and symbol in self.last_trade_time:
            time_since_last_trade = (timestamp - self.last_trade_time[symbol]).total_seconds()
            if time_since_last_trade < self.config.trade_cooldown:
                return False

        # Record order
        self.order_counts[symbol].append(timestamp)
        self.last_trade_time[symbol] = timestamp

        return True

    def _record_violation(self, violation: RiskViolation) -> None:
        """Record a risk violation."""
        self.violations.append(violation)

        # Log violation
        logger.warning(f"Risk violation: {violation.violation_type.value} - {violation.description}")

        # Trigger circuit breaker if critical
        if violation.severity == RiskLevel.CRITICAL:
            self._trigger_circuit_breaker(violation)

    def _trigger_circuit_breaker(self, violation: RiskViolation) -> None:
        """Trigger circuit breaker."""
        if not self.limits.circuit_breaker_enabled:
            return

        self.circuit_breaker_triggered = True
        self.circuit_breaker_timestamp = datetime.utcnow()

        logger.critical(f"Circuit breaker triggered by {violation.violation_type.value}: {violation.description}")

        # This would trigger emergency procedures
        # - Cancel all orders
        # - Reduce positions
        # - Send alerts

    def check_drawdown(self, equity: float) -> bool:
        """Check drawdown limits."""
        if not self.config.max_drawdown or not self.portfolio_history:
            return True

        # Find peak equity
        peak_equity = max(equity for _, equity in self.portfolio_history)

        if peak_equity <= 0:
            return True

        drawdown = 1 - equity / peak_equity

        if drawdown > self.config.max_drawdown:
            violation = RiskViolation(
                violation_type=RiskViolationType.DRAWDOWN,
                severity=RiskLevel.CRITICAL if drawdown > self.limits.circuit_breaker_drawdown else RiskLevel.HIGH,
                symbol=None,
                value=drawdown,
                threshold=self.config.max_drawdown,
                description=f"Drawdown {drawdown:.2%} exceeds limit {self.config.max_drawdown:.2%}"
            )
            self._record_violation(violation)
            return False

        return True

    def check_daily_loss(self, equity: float, timestamp: datetime) -> bool:
        """Check daily loss limits."""
        if not self.config.daily_loss_limit:
            return True

        date_key = timestamp.date().isoformat()
        start_equity = self.daily_pnl.get(date_key, equity)
        loss = 1 - equity / max(start_equity, 1e-9)

        if loss > self.config.daily_loss_limit:
            violation = RiskViolation(
                violation_type=RiskViolationType.DAILY_LOSS,
                severity=RiskLevel.CRITICAL if loss > self.limits.circuit_breaker_daily_loss else RiskLevel.HIGH,
                symbol=None,
                value=loss,
                threshold=self.config.daily_loss_limit,
                description=f"Daily loss {loss:.2%} exceeds limit {self.config.daily_loss_limit:.2%}"
            )
            self._record_violation(violation)
            return False

        return True

    async def _continuous_risk_monitor(self) -> None:
        """Continuous risk monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(1)  # Check every second

                # Get current equity
                current_equity = self.current_equity()

                # Check drawdown
                if not self.check_drawdown(current_equity):
                    # Emergency action would be taken here
                    pass

                # Check other risk metrics
                self._check_concentration_risk()
                self._check_volatility_risk()
                self._check_liquidity_risk()

            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")

    async def _periodic_metrics_update(self) -> None:
        """Periodic risk metrics update."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Update every minute

                # Calculate comprehensive risk metrics
                metrics = self._calculate_risk_metrics()
                self.risk_metrics_history.append(metrics)

                # Log significant changes
                if metrics.max_drawdown > 0.05:  # 5% drawdown
                    logger.warning(f"High drawdown detected: {metrics.max_drawdown:.2%}")

            except Exception as e:
                logger.error(f"Metrics update error: {e}")

    def _calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        metrics = RiskMetrics()

        if not self.portfolio_history:
            return metrics

        # Basic portfolio metrics
        current_equity = self.current_equity()
        metrics.total_equity = current_equity

        # Calculate returns for risk metrics
        equities = [eq for _, eq in self.portfolio_history]
        if len(equities) > 1:
            returns = np.diff(np.log(equities))

            # VaR calculation (simplified)
            if len(returns) > 30:
                metrics.value_at_risk_95 = np.percentile(returns, 5) * np.sqrt(252)  # Annualized
                metrics.expected_shortfall_95 = np.mean(returns[returns <= metrics.value_at_risk_95])

            # Volatility
            metrics.portfolio_volatility = np.std(returns) * np.sqrt(252)

            # Sharpe ratio (simplified, assuming 2% risk-free rate)
            if metrics.portfolio_volatility > 0:
                avg_return = np.mean(returns)
                metrics.sharpe_ratio = (avg_return * 252 - 0.02) / metrics.portfolio_volatility

        # Max drawdown calculation
        peak = max(equities)
        if peak > 0:
            metrics.max_drawdown = 1 - current_equity / peak

        return metrics

    def _check_concentration_risk(self) -> None:
        """Check portfolio concentration risk."""
        # This would analyze position concentrations
        # Simplified implementation
        pass

    def _check_volatility_risk(self) -> None:
        """Check volatility-based risk."""
        # Check if portfolio volatility exceeds limits
        if self.config.max_var_95:
            current_metrics = self.risk_metrics_history[-1] if self.risk_metrics_history else None
            if current_metrics and abs(current_metrics.value_at_risk_95) > self.config.max_var_95:
                violation = RiskViolation(
                    violation_type=RiskViolationType.VOLATILITY,
                    severity=RiskLevel.MEDIUM,
                    symbol=None,
                    value=abs(current_metrics.value_at_risk_95),
                    threshold=self.config.max_var_95,
                    description=f"VaR {current_metrics.value_at_risk_95:.2%} exceeds limit {self.config.max_var_95:.2%}"
                )
                self._record_violation(violation)

    def _check_liquidity_risk(self) -> None:
        """Check liquidity risk."""
        # This would check time to liquidate positions
        pass

    # Public interface methods
    def get_risk_violations(self, limit: int = 50) -> List[RiskViolation]:
        """Get recent risk violations."""
        return list(self.violations)[-limit:]

    def get_risk_metrics_history(self, limit: int = 100) -> List[RiskMetrics]:
        """Get risk metrics history."""
        return list(self.risk_metrics_history)[-limit:]

    def get_current_risk_metrics(self) -> Optional[RiskMetrics]:
        """Get current risk metrics."""
        return self.risk_metrics_history[-1] if self.risk_metrics_history else None

    def is_circuit_breaker_active(self) -> bool:
        """Check if circuit breaker is active."""
        return self.circuit_breaker_triggered

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker (admin function)."""
        self.circuit_breaker_triggered = False
        self.circuit_breaker_timestamp = None
        logger.info("Circuit breaker reset")

    def get_risk_limits(self) -> RiskLimits:
        """Get current risk limits."""
        return self.limits

    def update_risk_limits(self, updates: Dict[str, Any]) -> None:
        """Update risk limits dynamically."""
        for key, value in updates.items():
            if hasattr(self.limits, key):
                setattr(self.limits, key, value)
                logger.info(f"Updated risk limit {key}: {value}")

    def export_risk_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Export comprehensive risk report."""
        violations = [
            v for v in self.violations
            if start_date <= v.timestamp <= end_date
        ]

        metrics_history = [
            m for m in self.risk_metrics_history
            if start_date <= m.timestamp <= end_date
        ]

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "violations": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity.value,
                    "symbol": v.symbol,
                    "value": v.value,
                    "threshold": v.threshold,
                    "timestamp": v.timestamp.isoformat(),
                    "description": v.description
                } for v in violations
            ],
            "risk_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "total_equity": m.total_equity,
                    "value_at_risk_95": m.value_at_risk_95,
                    "max_drawdown": m.max_drawdown,
                    "sharpe_ratio": m.sharpe_ratio,
                    "portfolio_volatility": m.portfolio_volatility
                } for m in metrics_history
            ],
            "summary": {
                "total_violations": len(violations),
                "critical_violations": len([v for v in violations if v.severity == RiskLevel.CRITICAL]),
                "avg_drawdown": np.mean([m.max_drawdown for m in metrics_history]) if metrics_history else 0,
                "max_drawdown": max([m.max_drawdown for m in metrics_history]) if metrics_history else 0
            }
        }


__all__ = [
    "RiskLevel",
    "RiskViolationType",
    "RiskViolation",
    "RiskMetrics",
    "RiskLimits",
    "RiskConfig",
    "RiskGuardrails"
]

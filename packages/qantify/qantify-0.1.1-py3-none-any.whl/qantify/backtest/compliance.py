"""Advanced regulatory compliance checks with pattern detection and automated reporting."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import timedelta
from typing import Dict, Optional, Protocol, Iterable, List, Any, Callable, Union
from abc import ABC, abstractmethod
import re
from enum import Enum
import numpy as np

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .types import Order, OrderSide, Fill, PortfolioSnapshot


@dataclass(slots=True)
class ComplianceEvent:
    timestamp: pd.Timestamp
    check: str
    message: str
    severity: str = "warning"


@dataclass(slots=True)
class ComplianceContext:
    symbol: str
    price: float
    snapshot: PortfolioSnapshot
    timestamp: pd.Timestamp


class ComplianceCheck(Protocol):
    name: str

    def reset(self) -> None:  # pragma: no cover
        ...

    def on_context(self, context: ComplianceContext) -> None:  # pragma: no cover
        ...

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:  # pragma: no cover
        ...

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:  # pragma: no cover
        ...


class BaseComplianceCheck:
    name = "base"

    def reset(self) -> None:
        pass

    def on_context(self, context: ComplianceContext) -> None:
        pass

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        return None

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        pass


class WashTradeCheck(BaseComplianceCheck):
    """Detect immediate buy-sell (or sell-buy) sequences that resemble wash trades."""

    name = "wash_trade"

    def __init__(self, *, window: pd.Timedelta = pd.Timedelta("1min")) -> None:
        self.window = window
        self._last_fills: Dict[str, Fill] = {}

    def reset(self) -> None:
        self._last_fills.clear()

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        last = self._last_fills.get(fill.symbol)
        if last is not None:
            delta = fill.timestamp - last.timestamp
            if (
                delta <= self.window
                and last.side != fill.side
                and abs(last.quantity - fill.quantity) <= max(last.quantity, fill.quantity) * 0.05
            ):
                raise ComplianceViolationError(
                    f"Potential wash trade detected: {fill.symbol} {last.side}->{fill.side} within {delta.total_seconds():.1f}s."
                )
        self._last_fills[fill.symbol] = fill


class ComplianceViolationError(Exception):
    """Internal exception used to signal compliance violations."""


class ShortLocateCheck(BaseComplianceCheck):
    """Ensure sufficient locate inventory before opening short positions."""

    name = "short_locate"

    def __init__(self, locates: Optional[Dict[str, float]] = None) -> None:
        self.locates = locates or {}

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        if order.side != OrderSide.SELL:
            return None
        current = self.locates.get(order.symbol, 0.0)
        if current < order.remaining:
            return f"Insufficient locates for short sale: required {order.remaining:.2f}, available {current:.2f}."
        return None

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        if order.side == OrderSide.SELL:
            current = self.locates.get(order.symbol, 0.0)
            self.locates[order.symbol] = max(0.0, current - fill.quantity)


class RealTimeConstraintCheck(BaseComplianceCheck):
    """Apply user-defined portfolio constraint callbacks (e.g. exposure, leverage)."""

    name = "portfolio_constraint"

    def __init__(self, constraint: callable, description: str) -> None:
        self.constraint = constraint
        self.description = description

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        if not self.constraint(order, context):
            return self.description
        return None


class RegulationType(Enum):
    SEC = "sec"
    FCA = "fca"
    ASIC = "asic"
    MAS = "mas"
    GENERAL = "general"


class PatternDetectionCheck(BaseComplianceCheck):
    """Advanced pattern detection for suspicious trading activities."""

    name = "pattern_detection"

    def __init__(self, regulation: RegulationType = RegulationType.GENERAL) -> None:
        self.regulation = regulation
        self.order_history: List[Order] = []
        self.fill_history: List[Fill] = []
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def reset(self) -> None:
        self.order_history.clear()
        self.fill_history.clear()
        self.is_trained = False

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        self.fill_history.append(fill)

        # Train anomaly detection model periodically
        if len(self.fill_history) >= 100 and not self.is_trained:
            self._train_anomaly_detector()

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        self.order_history.append(order)

        # Check for various suspicious patterns
        pattern_violations = []

        # Round number trading (potential spoofing)
        if self._is_round_number_trading(order):
            pattern_violations.append("Round number concentration detected")

        # Layering detection
        if self._detect_layering(order, context):
            pattern_violations.append("Potential layering pattern detected")

        # Momentum ignition (marking the close)
        if self._detect_momentum_ignition(order, context):
            pattern_violations.append("Momentum ignition pattern detected")

        # Cross-market manipulation
        if self._detect_cross_market_manipulation(order):
            pattern_violations.append("Cross-market manipulation pattern detected")

        # ML-based anomaly detection
        if self.is_trained and self._detect_ml_anomaly(order, context):
            pattern_violations.append("ML-detected anomalous trading pattern")

        if pattern_violations:
            return f"Pattern violations: {', '.join(pattern_violations)}"

        return None

    def _train_anomaly_detector(self) -> None:
        """Train ML model for anomaly detection."""
        if len(self.fill_history) < 50:
            return

        # Create features for anomaly detection
        features = []
        for fill in self.fill_history[-200:]:  # Use recent history
            hour = fill.timestamp.hour
            minute = fill.timestamp.minute
            size_category = 1 if fill.quantity > 1000 else 0
            price_movement = 0  # Would need price context

            features.append([hour, minute, size_category, fill.quantity, price_movement])

        features = np.array(features)
        scaled_features = self.scaler.fit_transform(features)

        self.isolation_forest.fit(scaled_features)
        self.is_trained = True

    def _detect_ml_anomaly(self, order: Order, context: ComplianceContext) -> bool:
        """Use ML to detect anomalous orders."""
        if not self.is_trained:
            return False

        hour = order.timestamp.hour
        minute = order.timestamp.minute
        size_category = 1 if order.quantity > 1000 else 0
        price_movement = 0  # Simplified

        features = np.array([[hour, minute, size_category, order.quantity, price_movement]])
        scaled_features = self.scaler.transform(features)

        # Isolation Forest returns -1 for anomalies
        return self.isolation_forest.predict(scaled_features)[0] == -1

    def _is_round_number_trading(self, order: Order) -> bool:
        """Detect trading at round number prices."""
        price_str = f"{order.price:.2f}"
        return price_str.endswith('.00') and len(self.order_history) > 10

    def _detect_layering(self, order: Order, context: ComplianceContext) -> bool:
        """Detect layering (placing/canceling orders to create false depth)."""
        recent_orders = [o for o in self.order_history[-20:] if o.symbol == order.symbol]
        if len(recent_orders) < 5:
            return False

        # Check for rapid order placement and cancellation patterns
        timestamps = [o.timestamp for o in recent_orders]
        if len(timestamps) > 1:
            avg_interval = np.mean(np.diff([t.timestamp() for t in timestamps]))
            return avg_interval < 60  # Less than 1 minute average

        return False

    def _detect_momentum_ignition(self, order: Order, context: ComplianceContext) -> bool:
        """Detect attempts to mark the close or create momentum."""
        if order.timestamp.hour != 15 or order.timestamp.minute < 55:
            return False

        # Large order near market close
        return order.quantity > 10000  # Threshold would be asset-specific

    def _detect_cross_market_manipulation(self, order: Order) -> bool:
        """Detect coordinated trading across related instruments."""
        # This would require tracking multiple symbols
        # Simplified version: check for correlated timing patterns
        recent_orders = self.order_history[-10:]
        if len(recent_orders) < 3:
            return False

        # Check if orders are placed within short time windows
        timestamps = [o.timestamp for o in recent_orders]
        time_diffs = np.diff([t.timestamp() for t in timestamps])
        return np.any(time_diffs < 30)  # Within 30 seconds


class ConcentrationLimitCheck(BaseComplianceCheck):
    """Monitor position concentration limits (SEC Rule 12d1, etc.)."""

    name = "concentration_limit"

    def __init__(self, max_position_pct: float = 0.05, max_sector_pct: float = 0.25,
                 sector_mappings: Optional[Dict[str, str]] = None) -> None:
        self.max_position_pct = max_position_pct
        self.max_sector_pct = max_sector_pct
        self.sector_mappings = sector_mappings or {}
        self.position_holdings: Dict[str, float] = {}
        self.sector_holdings: Dict[str, float] = {}

    def reset(self) -> None:
        self.position_holdings.clear()
        self.sector_holdings.clear()

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        # Update holdings
        current_holding = self.position_holdings.get(order.symbol, 0)
        projected_holding = current_holding + order.remaining

        portfolio_value = context.snapshot.equity + context.snapshot.gross_exposure

        if portfolio_value <= 0:
            return None

        position_pct = (projected_holding * context.price) / portfolio_value

        # Check position concentration limit
        if position_pct > self.max_position_pct:
            return ".2%"

        # Check sector concentration limit
        sector = self.sector_mappings.get(order.symbol, "unknown")
        current_sector_holding = self.sector_holdings.get(sector, 0)
        projected_sector_holding = current_sector_holding + (order.remaining * context.price)
        sector_pct = projected_sector_holding / portfolio_value

        if sector_pct > self.max_sector_pct:
            return ".2%"

        return None

    def on_fill(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        # Update actual holdings after fill
        self.position_holdings[order.symbol] = self.position_holdings.get(order.symbol, 0) + fill.quantity

        sector = self.sector_mappings.get(order.symbol, "unknown")
        self.sector_holdings[sector] = self.sector_holdings.get(sector, 0) + (fill.quantity * fill.price)


class MarketImpactCheck(BaseComplianceCheck):
    """Monitor market impact and ensure orders don't move the market excessively."""

    name = "market_impact"

    def __init__(self, max_impact_pct: float = 0.01, avg_daily_volume: Optional[Dict[str, float]] = None) -> None:
        self.max_impact_pct = max_impact_pct
        self.avg_daily_volume = avg_daily_volume or {}
        self.recent_volume: Dict[str, List[float]] = {}

    def reset(self) -> None:
        self.recent_volume.clear()

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        symbol_volume = self.avg_daily_volume.get(order.symbol, 1000000)  # Default 1M shares

        # Estimate market impact using square root formula
        participation_rate = order.remaining / symbol_volume
        estimated_impact = 0.5 * np.sqrt(participation_rate) * 100  # Rough estimate in basis points

        if estimated_impact > (self.max_impact_pct * 100):
            return ".2%"

        return None


class InsiderTradingPatternCheck(BaseComplianceCheck):
    """Detect patterns that may indicate insider trading."""

    name = "insider_trading"

    def __init__(self) -> None:
        self.order_sequences: Dict[str, List[Order]] = {}
        self.price_history: Dict[str, List[float]] = {}

    def reset(self) -> None:
        self.order_sequences.clear()
        self.price_history.clear()

    def approve_order(self, order: Order, context: ComplianceContext) -> Optional[str]:
        symbol = order.symbol

        # Track price movements around orders
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(context.price)

        # Keep only recent history
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol].pop(0)

        # Check for suspicious patterns
        if self._detect_run_up_before_buy(order, context):
            return "Potential insider trading: price run-up before purchase"

        if self._detect_dump_before_sell(order, context):
            return "Potential insider trading: price decline before sale"

        return None

    def _detect_run_up_before_buy(self, order: Order, context: ComplianceContext) -> bool:
        """Detect price run-up before buying."""
        if order.side != OrderSide.BUY:
            return False

        prices = self.price_history.get(order.symbol, [])
        if len(prices) < 20:
            return False

        # Check if price has been rising for several periods before order
        recent_returns = np.diff(prices[-20:]) / prices[-20:-1]
        positive_streak = sum(1 for r in recent_returns[-5:] if r > 0.005)  # 0.5% daily moves

        return positive_streak >= 4  # 4 out of last 5 days positive

    def _detect_dump_before_sell(self, order: Order, context: ComplianceContext) -> bool:
        """Detect price decline before selling."""
        if order.side != OrderSide.SELL:
            return False

        prices = self.price_history.get(order.symbol, [])
        if len(prices) < 20:
            return False

        # Check if price has been falling before order
        recent_returns = np.diff(prices[-20:]) / prices[-20:-1]
        negative_streak = sum(1 for r in recent_returns[-5:] if r < -0.005)

        return negative_streak >= 4


class RegulatoryReportingEngine:
    """Automated regulatory reporting and compliance documentation."""

    def __init__(self, firm_name: str = "Qantify Capital", regulator: RegulationType = RegulationType.SEC):
        self.firm_name = firm_name
        self.regulator = regulator
        self.trade_log: List[Dict[str, Any]] = []
        self.violation_log: List[Dict[str, Any]] = []

    def log_trade(self, order: Order, fill: Fill, context: ComplianceContext) -> None:
        """Log trade for regulatory reporting."""
        trade_record = {
            "timestamp": fill.timestamp,
            "symbol": fill.symbol,
            "side": fill.side.value,
            "quantity": fill.quantity,
            "price": fill.price,
            "value": fill.quantity * fill.price,
            "commission": fill.commission,
            "slippage": fill.slippage,
            "portfolio_value": context.snapshot.equity,
            "regulation": self.regulator.value
        }
        self.trade_log.append(trade_record)

    def log_violation(self, violation: ComplianceEvent) -> None:
        """Log compliance violations."""
        violation_record = {
            "timestamp": violation.timestamp,
            "check": violation.check,
            "message": violation.message,
            "severity": violation.severity,
            "regulation": self.regulator.value
        }
        self.violation_log.append(violation_record)

    def generate_daily_report(self, date: pd.Timestamp) -> Dict[str, Any]:
        """Generate daily compliance report."""
        day_trades = [t for t in self.trade_log if t["timestamp"].date() == date.date()]
        day_violations = [v for v in self.violation_log if v["timestamp"].date() == date.date()]

        report = {
            "date": date.date(),
            "firm": self.firm_name,
            "regulator": self.regulator.value,
            "total_trades": len(day_trades),
            "total_volume": sum(t["value"] for t in day_trades),
            "total_commissions": sum(t["commission"] for t in day_trades),
            "violations": len(day_violations),
            "violation_details": day_violations,
            "largest_trade": max(day_trades, key=lambda x: x["value"]) if day_trades else None,
            "compliance_status": "PASS" if len(day_violations) == 0 else "REVIEW_REQUIRED"
        }

        return report

    def generate_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly compliance summary."""
        monthly_trades = [t for t in self.trade_log
                         if t["timestamp"].year == year and t["timestamp"].month == month]
        monthly_violations = [v for v in self.violation_log
                             if v["timestamp"].year == year and v["timestamp"].month == month]

        summary = {
            "period": f"{year}-{month:02d}",
            "firm": self.firm_name,
            "regulator": self.regulator.value,
            "monthly_trades": len(monthly_trades),
            "monthly_volume": sum(t["value"] for t in monthly_trades),
            "monthly_violations": len(monthly_violations),
            "violation_breakdown": self._violation_breakdown(monthly_violations),
            "compliance_score": self._calculate_compliance_score(monthly_trades, monthly_violations)
        }

        return summary

    def _violation_breakdown(self, violations: List[Dict]) -> Dict[str, int]:
        """Break down violations by type."""
        breakdown = {}
        for v in violations:
            check = v["check"]
            breakdown[check] = breakdown.get(check, 0) + 1
        return breakdown

    def _calculate_compliance_score(self, trades: List[Dict], violations: List[Dict]) -> float:
        """Calculate compliance score (0-100)."""
        if not trades:
            return 100.0

        base_score = 100.0
        violation_penalty = len(violations) * 5.0  # 5 points per violation
        volume_penalty = 0.0

        # Additional penalties for large violations
        severe_violations = [v for v in violations if v.get("severity") == "alert"]
        severe_penalty = len(severe_violations) * 10.0

        final_score = max(0.0, base_score - violation_penalty - severe_penalty - volume_penalty)
        return round(final_score, 2)


@dataclass(slots=True)
class ComplianceEngine:
    checks: List[ComplianceCheck] = field(default_factory=list)
    events: List[ComplianceEvent] = field(default_factory=list)
    context: Optional[ComplianceContext] = None
    reporting_engine: Optional[RegulatoryReportingEngine] = None

    def __post_init__(self) -> None:
        if self.reporting_engine is None:
            self.reporting_engine = RegulatoryReportingEngine()

    def reset(self) -> None:
        for check in self.checks:
            check.reset()
        self.events.clear()
        self.context = None
        if self.reporting_engine:
            self.reporting_engine.trade_log.clear()
            self.reporting_engine.violation_log.clear()

    def update_context(self, context: ComplianceContext) -> None:
        self.context = context
        for check in self.checks:
            check.on_context(context)

    def approve(self, order: Order) -> bool:
        if self.context is None:
            return True
        allowed = True
        for check in self.checks:
            message = check.approve_order(order, self.context)
            if message:
                allowed = False
                event = ComplianceEvent(timestamp=self.context.timestamp, check=check.name, message=message, severity="block")
                self.events.append(event)
                if self.reporting_engine:
                    self.reporting_engine.log_violation(event)
        return allowed

    def on_fill(self, order: Order, fill: Fill) -> None:
        if self.context is None:
            return

        # Log trade for reporting
        if self.reporting_engine:
            self.reporting_engine.log_trade(order, fill, self.context)

        for check in self.checks:
            try:
                check.on_fill(order, fill, self.context)
            except ComplianceViolationError as exc:
                event = ComplianceEvent(
                    timestamp=self.context.timestamp,
                    check=check.name,
                    message=str(exc),
                    severity="alert",
                )
                self.events.append(event)
                if self.reporting_engine:
                    self.reporting_engine.log_violation(event)

    def summary(self) -> pd.DataFrame:
        if not self.events:
            return pd.DataFrame(columns=["timestamp", "check", "message", "severity"])
        frame = pd.DataFrame([asdict(event) for event in self.events])
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame

    def generate_compliance_report(self, date: pd.Timestamp) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if not self.reporting_engine:
            return {}

        daily_report = self.reporting_engine.generate_daily_report(date)

        # Add additional analytics
        events_df = self.summary()
        if not events_df.empty:
            # Events by check type
            check_summary = events_df.groupby('check').size().to_dict()

            # Severity distribution
            severity_summary = events_df.groupby('severity').size().to_dict()

            daily_report.update({
                "check_summary": check_summary,
                "severity_summary": severity_summary,
                "most_common_violation": max(check_summary.items(), key=lambda x: x[1]) if check_summary else None
            })

        return daily_report

    def get_compliance_score(self) -> float:
        """Calculate overall compliance score."""
        if not self.reporting_engine:
            return 100.0

        total_trades = len(self.reporting_engine.trade_log)
        total_violations = len(self.reporting_engine.violation_log)

        if total_trades == 0:
            return 100.0

        # Base score calculation
        violation_rate = total_violations / total_trades
        score = max(0.0, 100.0 - (violation_rate * 1000))  # Penalty per violation

        # Adjust for severity
        severe_violations = sum(1 for v in self.reporting_engine.violation_log
                              if v.get("severity") == "alert")
        score = max(0.0, score - (severe_violations * 5.0))

        return round(score, 2)

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Generate risk assessment based on compliance data."""
        assessment = {
            "overall_risk_level": "LOW",
            "risk_factors": [],
            "recommendations": []
        }

        score = self.get_compliance_score()

        if score >= 90:
            assessment["overall_risk_level"] = "LOW"
        elif score >= 70:
            assessment["overall_risk_level"] = "MEDIUM"
            assessment["recommendations"].append("Review compliance procedures")
        elif score >= 50:
            assessment["overall_risk_level"] = "HIGH"
            assessment["recommendations"].extend([
                "Immediate compliance review required",
                "Consider reducing trading activity",
                "Review risk management procedures"
            ])
        else:
            assessment["overall_risk_level"] = "CRITICAL"
            assessment["recommendations"].extend([
                "Cease trading activities",
                "Conduct full compliance audit",
                "Report to regulatory authorities"
            ])

        # Identify risk factors
        events_df = self.summary()
        if not events_df.empty:
            top_checks = events_df['check'].value_counts().head(3).index.tolist()
            assessment["risk_factors"] = top_checks

        return assessment


__all__ = [
    "ComplianceEngine",
    "ComplianceCheck",
    "ComplianceContext",
    "ComplianceEvent",
    "RegulationType",
    "WashTradeCheck",
    "ShortLocateCheck",
    "RealTimeConstraintCheck",
    "PatternDetectionCheck",
    "ConcentrationLimitCheck",
    "MarketImpactCheck",
    "InsiderTradingPatternCheck",
    "RegulatoryReportingEngine",
]


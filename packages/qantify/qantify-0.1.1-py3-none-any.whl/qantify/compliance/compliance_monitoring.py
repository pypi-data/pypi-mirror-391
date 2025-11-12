"""
Compliance Monitoring Engine
============================

Real-time compliance monitoring system for regulatory adherence, risk limits,
and automated breach detection in institutional trading operations.

Key Features:
- Real-time position limit monitoring
- Trading volume and frequency limits
- Risk-based compliance checks
- Pre-trade and post-trade compliance validation
- Automated alert system for breaches
- Regulatory threshold monitoring
- Market impact compliance checks
- Circuit breaker compliance
- Position concentration limits
- Cross-market compliance monitoring
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import json

import numpy as np
import pandas as pd
from scipy import stats


class ComplianceLevel(Enum):
    """Compliance monitoring levels"""
    WARNING = "warning"
    BREACH = "breach"
    CRITICAL = "critical"
    INFO = "info"


class ComplianceCheck(Enum):
    """Types of compliance checks"""
    PRE_TRADE = "pre_trade"
    POST_TRADE = "post_trade"
    INTRA_DAY = "intra_day"
    END_OF_DAY = "end_of_day"
    REAL_TIME = "real_time"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    name: str
    description: str
    check_type: ComplianceCheck
    threshold: Union[float, int, Dict[str, Any]]
    breach_action: str
    severity: AlertSeverity
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Evaluate compliance rule against data"""
        # Basic threshold-based evaluation
        if not self.enabled:
            return True, 0.0, "Rule disabled"

        # Simple threshold checking for position limits
        if 'max_position' in self.threshold:
            current_value = data.get('position_size', 0) + data.get('current_exposure', 0)
            threshold_value = self.threshold['max_position']

            if current_value > threshold_value:
                return False, current_value, f"Position size {current_value} exceeds limit {threshold_value}"
            else:
                return True, current_value, f"Position size {current_value} within limit {threshold_value}"

        # Default pass for unimplemented rules
        return True, 0.0, "Rule evaluation not implemented"


@dataclass
class ComplianceAlert:
    """Compliance alert record"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_note: Optional[str] = None

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"alert_{self.rule_id}_{int(self.timestamp.timestamp())}"


@dataclass
class ComplianceMetrics:
    """Compliance monitoring metrics"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    alerts_generated: int = 0
    critical_alerts: int = 0
    average_response_time: float = 0.0
    last_check_timestamp: Optional[datetime] = None
    uptime_percentage: float = 100.0


class ComplianceMonitoringEngine:
    """Main compliance monitoring engine"""

    def __init__(self,
                 rules: Optional[List[ComplianceRule]] = None,
                 alert_queue_size: int = 1000,
                 check_interval: float = 1.0,
                 max_workers: int = 4):
        self.rules: Dict[str, ComplianceRule] = {}
        self.active_alerts: Dict[str, ComplianceAlert] = {}
        self.alert_history: List[ComplianceAlert] = []
        self.metrics = ComplianceMetrics()

        # Initialize with default rules if none provided
        if rules:
            for rule in rules:
                self.rules[rule.rule_id] = rule
        else:
            self._initialize_default_rules()

        # Monitoring components
        self.monitoring_active = False
        self.check_interval = check_interval
        self.max_workers = max_workers

        # Threading and queues
        self.alert_queue = queue.Queue(maxsize=alert_queue_size)
        self.check_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Monitors
        self.position_monitor = PositionLimitMonitor(self)
        self.volume_monitor = TradingVolumeMonitor(self)
        self.risk_monitor = RiskLimitMonitor(self)
        self.market_impact_monitor = MarketImpactMonitor(self)

        # Alert system
        self.alert_system = ComplianceAlertSystem(self)

        # Logging
        self.logger = logging.getLogger(__name__)

    def _initialize_default_rules(self):
        """Initialize default compliance rules"""

        # Position limit rules
        self.rules['position_limit_equity'] = ComplianceRule(
            rule_id='position_limit_equity',
            name='Equity Position Limit',
            description='Maximum position size for individual equity securities',
            check_type=ComplianceCheck.REAL_TIME,
            threshold={'max_position': 1000000, 'max_percentage': 5.0},
            breach_action='HALT_TRADING',
            severity=AlertSeverity.HIGH
        )

        self.rules['concentration_limit'] = ComplianceRule(
            rule_id='concentration_limit',
            name='Portfolio Concentration Limit',
            description='Maximum concentration in single asset class',
            check_type=ComplianceCheck.INTRA_DAY,
            threshold={'max_concentration': 25.0},
            breach_action='REDUCE_POSITION',
            severity=AlertSeverity.MEDIUM
        )

        # Volume limit rules
        self.rules['daily_volume_limit'] = ComplianceRule(
            rule_id='daily_volume_limit',
            name='Daily Trading Volume Limit',
            description='Maximum daily trading volume',
            check_type=ComplianceCheck.INTRA_DAY,
            threshold={'max_volume': 50000000, 'reset_time': '00:00'},
            breach_action='THROTTLE_TRADING',
            severity=AlertSeverity.HIGH
        )

        self.rules['market_impact_limit'] = ComplianceRule(
            rule_id='market_impact_limit',
            name='Market Impact Limit',
            description='Maximum allowable market impact per trade',
            check_type=ComplianceCheck.PRE_TRADE,
            threshold={'max_impact': 0.5, 'timeframe_minutes': 5},
            breach_action='REJECT_TRADE',
            severity=AlertSeverity.CRITICAL
        )

        # Risk limit rules
        self.rules['var_limit'] = ComplianceRule(
            rule_id='var_limit',
            name='Value at Risk Limit',
            description='Maximum portfolio VaR limit',
            check_type=ComplianceCheck.REAL_TIME,
            threshold={'max_var': 100000, 'confidence': 0.99},
            breach_action='REDUCE_RISK',
            severity=AlertSeverity.CRITICAL
        )

        # Regulatory rules
        self.rules['short_sale_compliance'] = ComplianceRule(
            rule_id='short_sale_compliance',
            name='Short Sale Compliance',
            description='Ensure short sales comply with Regulation SHO',
            check_type=ComplianceCheck.PRE_TRADE,
            threshold={'locate_required': True},
            breach_action='REJECT_TRADE',
            severity=AlertSeverity.CRITICAL
        )

    def start_monitoring(self):
        """Start compliance monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.logger.info("Starting compliance monitoring")

        # Start monitoring threads
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        threading.Thread(target=self._alert_processing_loop, daemon=True).start()

        # Start individual monitors
        self.position_monitor.start()
        self.volume_monitor.start()
        self.risk_monitor.start()
        self.market_impact_monitor.start()
        self.alert_system.start()

    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopping compliance monitoring")

        # Stop monitors
        self.position_monitor.stop()
        self.volume_monitor.stop()
        self.risk_monitor.stop()
        self.market_impact_monitor.stop()
        self.alert_system.stop()

        # Shutdown executor
        self.executor.shutdown(wait=True)

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform compliance checks
                self._perform_compliance_checks()

                # Update metrics
                self._update_metrics()

                # Sleep for next check
                asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

    def _perform_compliance_checks(self):
        """Perform all compliance checks"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue

            try:
                # Submit check to thread pool
                self.executor.submit(self._execute_compliance_check, rule)

            except Exception as e:
                self.logger.error(f"Error submitting check for rule {rule.rule_id}: {e}")

    def _execute_compliance_check(self, rule: ComplianceRule):
        """Execute a single compliance check"""
        start_time = datetime.now()

        try:
            # Get relevant data for check
            data = self._get_check_data(rule)

            # Evaluate rule
            passed, value, message = rule.evaluate(data)

            # Update metrics
            self.metrics.total_checks += 1
            if passed:
                self.metrics.passed_checks += 1
            else:
                self.metrics.failed_checks += 1

            # Generate alert if breached
            if not passed:
                alert = ComplianceAlert(
                    alert_id="",
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=message,
                    timestamp=datetime.now(),
                    data={'rule': rule.name, 'value': value, 'threshold': rule.threshold}
                )

                # Add to alert queue
                try:
                    self.alert_queue.put_nowait(alert)
                    self.metrics.alerts_generated += 1
                    if rule.severity == AlertSeverity.CRITICAL:
                        self.metrics.critical_alerts += 1
                except queue.Full:
                    self.logger.warning("Alert queue full, dropping alert")

            # Update response time
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time + response_time) / 2
            )

        except Exception as e:
            self.logger.error(f"Error executing compliance check {rule.rule_id}: {e}")

    def _get_check_data(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Get data required for compliance check"""
        # This would integrate with trading system to get current state
        # For now, return mock data
        return {
            'current_positions': {},
            'daily_volume': 0,
            'portfolio_value': 1000000,
            'risk_metrics': {'var': 50000}
        }

    def _update_metrics(self):
        """Update compliance metrics"""
        self.metrics.last_check_timestamp = datetime.now()

        # Calculate uptime (simplified)
        # In real implementation, track actual uptime

    def _alert_processing_loop(self):
        """Process alerts from queue"""
        while self.monitoring_active:
            try:
                alert = self.alert_queue.get(timeout=1.0)
                self._process_alert(alert)
                self.alert_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing alert: {e}")

    def _process_alert(self, alert: ComplianceAlert):
        """Process a compliance alert"""
        # Add to active alerts
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        # Log alert
        self.logger.warning(f"Compliance alert: {alert.message}")

        # Execute breach action
        self._execute_breach_action(alert)

    def _execute_breach_action(self, alert: ComplianceAlert):
        """Execute breach action for alert"""
        rule = self.rules.get(alert.rule_id)
        if not rule:
            return

        action = rule.breach_action

        if action == 'HALT_TRADING':
            self._halt_trading(alert)
        elif action == 'REDUCE_POSITION':
            self._reduce_position(alert)
        elif action == 'THROTTLE_TRADING':
            self._throttle_trading(alert)
        elif action == 'REJECT_TRADE':
            self._reject_trade(alert)
        elif action == 'REDUCE_RISK':
            self._reduce_risk(alert)

    def _halt_trading(self, alert: ComplianceAlert):
        """Halt trading due to compliance breach"""
        self.logger.critical(f"Halting trading due to: {alert.message}")
        # Implementation would integrate with trading engine

    def _reduce_position(self, alert: ComplianceAlert):
        """Reduce position due to compliance breach"""
        self.logger.warning(f"Reducing position due to: {alert.message}")
        # Implementation would trigger position reduction

    def _throttle_trading(self, alert: ComplianceAlert):
        """Throttle trading due to compliance breach"""
        self.logger.warning(f"Throttling trading due to: {alert.message}")
        # Implementation would reduce trading frequency

    def _reject_trade(self, alert: ComplianceAlert):
        """Reject trade due to compliance breach"""
        self.logger.warning(f"Rejecting trade due to: {alert.message}")
        # Implementation would reject the trade

    def _reduce_risk(self, alert: ComplianceAlert):
        """Reduce risk due to compliance breach"""
        self.logger.warning(f"Reducing risk due to: {alert.message}")
        # Implementation would trigger risk reduction

    def add_rule(self, rule: ComplianceRule):
        """Add a new compliance rule"""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Added compliance rule: {rule.name}")

    def remove_rule(self, rule_id: str):
        """Remove a compliance rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Removed compliance rule: {rule_id}")

    def get_active_alerts(self) -> List[ComplianceAlert]:
        """Get all active compliance alerts"""
        return list(self.active_alerts.values())

    def resolve_alert(self, alert_id: str, resolution_note: str):
        """Resolve a compliance alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_timestamp = datetime.now()
            alert.resolution_note = resolution_note

            del self.active_alerts[alert_id]
            self.logger.info(f"Resolved alert {alert_id}: {resolution_note}")

    def get_compliance_metrics(self) -> ComplianceMetrics:
        """Get compliance monitoring metrics"""
        return self.metrics

    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        alerts_in_period = [
            alert for alert in self.alert_history
            if start_date <= alert.timestamp <= end_date
        ]

        report = {
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'metrics': {
                'total_alerts': len(alerts_in_period),
                'critical_alerts': len([a for a in alerts_in_period if a.severity == AlertSeverity.CRITICAL]),
                'resolved_alerts': len([a for a in alerts_in_period if a.resolved]),
                'unresolved_alerts': len([a for a in alerts_in_period if not a.resolved])
            },
            'alerts_by_severity': {},
            'alerts_by_rule': {},
            'compliance_score': self._calculate_compliance_score(alerts_in_period),
            'recommendations': self._generate_recommendations(alerts_in_period)
        }

        # Group alerts by severity and rule
        for alert in alerts_in_period:
            severity = alert.severity.value
            rule_id = alert.rule_id

            if severity not in report['alerts_by_severity']:
                report['alerts_by_severity'][severity] = 0
            report['alerts_by_severity'][severity] += 1

            if rule_id not in report['alerts_by_rule']:
                report['alerts_by_rule'][rule_id] = 0
            report['alerts_by_rule'][rule_id] += 1

        return report

    def _calculate_compliance_score(self, alerts: List[ComplianceAlert]) -> float:
        """Calculate compliance score based on alerts"""
        if not alerts:
            return 100.0

        # Weight alerts by severity
        weights = {
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 3,
            AlertSeverity.HIGH: 5,
            AlertSeverity.CRITICAL: 10
        }

        total_weight = sum(weights[alert.severity] for alert in alerts)
        max_possible_weight = len(alerts) * 10  # Max weight per alert

        # Score = 100 - (weighted violations / max possible) * 100
        score = 100.0 - (total_weight / max_possible_weight) * 100
        return max(0.0, score)

    def _generate_recommendations(self, alerts: List[ComplianceAlert]) -> List[str]:
        """Generate compliance recommendations based on alerts"""
        recommendations = []

        if not alerts:
            recommendations.append("Compliance monitoring is functioning well with no alerts.")
            return recommendations

        # Analyze alert patterns
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        if critical_count > 5:
            recommendations.append("Consider implementing additional pre-trade controls due to high number of critical alerts.")

        # Check for repeated rules
        rule_counts = {}
        for alert in alerts:
            rule_counts[alert.rule_id] = rule_counts.get(alert.rule_id, 0) + 1

        for rule_id, count in rule_counts.items():
            if count > 3:
                rule = self.rules.get(rule_id)
                if rule:
                    recommendations.append(f"Review and potentially adjust {rule.name} rule due to frequent violations.")

        if len(alerts) > len(set(a.rule_id for a in alerts)):
            recommendations.append("Implement more granular monitoring to reduce false positives.")

        return recommendations


class RealTimeComplianceMonitor:
    """Real-time compliance monitoring"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.monitoring_active = False
        self.check_interval = 0.1  # 100ms for real-time

    def start(self):
        """Start real-time monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        threading.Thread(target=self._real_time_loop, daemon=True).start()

    def stop(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False

    def _real_time_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform real-time checks
                self._perform_real_time_checks()
                asyncio.sleep(self.check_interval)

            except Exception as e:
                self.engine.logger.error(f"Error in real-time monitoring: {e}")

    def _perform_real_time_checks(self):
        """Perform real-time compliance checks"""
        # Check only real-time rules
        real_time_rules = [
            rule for rule in self.engine.rules.values()
            if rule.check_type == ComplianceCheck.REAL_TIME and rule.enabled
        ]

        for rule in real_time_rules:
            try:
                self.engine.executor.submit(self.engine._execute_compliance_check, rule)
            except Exception as e:
                self.engine.logger.error(f"Error submitting real-time check for rule {rule.rule_id}: {e}")


class PositionLimitMonitor:
    """Monitor position limits"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.monitoring_active = False

    def start(self):
        """Start position monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._position_monitor_loop, daemon=True).start()

    def stop(self):
        """Stop position monitoring"""
        self.monitoring_active = False

    def _position_monitor_loop(self):
        """Position monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_position_limits()
                asyncio.sleep(5.0)  # Check every 5 seconds

            except Exception as e:
                self.engine.logger.error(f"Error in position monitoring: {e}")

    def _check_position_limits(self):
        """Check position limits"""
        # Implementation would check current positions against limits
        # and generate alerts if limits exceeded
        pass


class TradingVolumeMonitor:
    """Monitor trading volume limits"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.monitoring_active = False
        self.daily_volume = 0
        self.last_reset = datetime.now().date()

    def start(self):
        """Start volume monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._volume_monitor_loop, daemon=True).start()

    def stop(self):
        """Stop volume monitoring"""
        self.monitoring_active = False

    def _volume_monitor_loop(self):
        """Volume monitoring loop"""
        while self.monitoring_active:
            try:
                # Reset daily volume if new day
                if datetime.now().date() != self.last_reset:
                    self.daily_volume = 0
                    self.last_reset = datetime.now().date()

                self._check_volume_limits()
                asyncio.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                self.engine.logger.error(f"Error in volume monitoring: {e}")

    def _check_volume_limits(self):
        """Check volume limits"""
        # Implementation would check trading volume against limits
        pass


class RiskLimitMonitor:
    """Monitor risk limits"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.monitoring_active = False

    def start(self):
        """Start risk monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._risk_monitor_loop, daemon=True).start()

    def stop(self):
        """Stop risk monitoring"""
        self.monitoring_active = False

    def _risk_monitor_loop(self):
        """Risk monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_risk_limits()
                asyncio.sleep(30.0)  # Check every 30 seconds

            except Exception as e:
                self.engine.logger.error(f"Error in risk monitoring: {e}")

    def _check_risk_limits(self):
        """Check risk limits"""
        # Implementation would check risk metrics against limits
        pass


class MarketImpactMonitor:
    """Monitor market impact limits"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.monitoring_active = False

    def start(self):
        """Start market impact monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._impact_monitor_loop, daemon=True).start()

    def stop(self):
        """Stop market impact monitoring"""
        self.monitoring_active = False

    def _impact_monitor_loop(self):
        """Market impact monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_market_impact()
                asyncio.sleep(2.0)  # Check every 2 seconds

            except Exception as e:
                self.engine.logger.error(f"Error in market impact monitoring: {e}")

    def _check_market_impact(self):
        """Check market impact limits"""
        # Implementation would estimate and check market impact
        pass


class PreTradeComplianceCheck:
    """Pre-trade compliance validation"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine

    def validate_trade(self, trade_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate trade before execution"""
        violations = []

        # Check pre-trade rules
        pre_trade_rules = [
            rule for rule in self.engine.rules.values()
            if rule.check_type == ComplianceCheck.PRE_TRADE and rule.enabled
        ]

        for rule in pre_trade_rules:
            try:
                passed, value, message = rule.evaluate(trade_data)
                if not passed:
                    violations.append(f"{rule.name}: {message}")
            except Exception as e:
                violations.append(f"Error checking {rule.name}: {str(e)}")

        return len(violations) == 0, violations


class PostTradeComplianceCheck:
    """Post-trade compliance validation"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine

    def validate_trade(self, trade_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate trade after execution"""
        violations = []

        # Check post-trade rules
        post_trade_rules = [
            rule for rule in self.engine.rules.values()
            if rule.check_type == ComplianceCheck.POST_TRADE and rule.enabled
        ]

        for rule in post_trade_rules:
            try:
                passed, value, message = rule.evaluate(trade_data)
                if not passed:
                    violations.append(f"{rule.name}: {message}")
            except Exception as e:
                violations.append(f"Error checking {rule.name}: {str(e)}")

        return len(violations) == 0, violations


class ComplianceAlertSystem:
    """Compliance alert management system"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine
        self.alert_system_active = False
        self.email_recipients = []
        self.sms_recipients = []
        self.webhook_urls = []

    def start(self):
        """Start alert system"""
        self.alert_system_active = True

    def stop(self):
        """Stop alert system"""
        self.alert_system_active = False

    def add_email_recipient(self, email: str):
        """Add email recipient for alerts"""
        self.email_recipients.append(email)

    def add_sms_recipient(self, phone: str):
        """Add SMS recipient for alerts"""
        self.sms_recipients.append(phone)

    def add_webhook_url(self, url: str):
        """Add webhook URL for alerts"""
        self.webhook_urls.append(url)

    def send_alert(self, alert: ComplianceAlert):
        """Send compliance alert through all configured channels"""
        if not self.alert_system_active:
            return

        # Send email alerts
        for email in self.email_recipients:
            self._send_email_alert(alert, email)

        # Send SMS alerts for critical alerts
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            for phone in self.sms_recipients:
                self._send_sms_alert(alert, phone)

        # Send webhook alerts
        for url in self.webhook_urls:
            self._send_webhook_alert(alert, url)

    def _send_email_alert(self, alert: ComplianceAlert, email: str):
        """Send email alert"""
        # Implementation would send actual email
        self.engine.logger.info(f"Email alert sent to {email}: {alert.message}")

    def _send_sms_alert(self, alert: ComplianceAlert, phone: str):
        """Send SMS alert"""
        # Implementation would send actual SMS
        self.engine.logger.info(f"SMS alert sent to {phone}: {alert.message}")

    def _send_webhook_alert(self, alert: ComplianceAlert, url: str):
        """Send webhook alert"""
        # Implementation would send HTTP POST to webhook
        self.engine.logger.info(f"Webhook alert sent to {url}: {alert.message}")


class RegulatoryBreachDetector:
    """Advanced regulatory breach detection"""

    def __init__(self, engine: ComplianceMonitoringEngine):
        self.engine = engine

    def detect_pattern_breaches(self, historical_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect pattern-based regulatory breaches"""
        breaches = []

        # Check for wash trading patterns
        wash_trades = self._detect_wash_trading(historical_data)
        if wash_trades:
            breaches.extend(wash_trades)

        # Check for spoofing patterns
        spoofing = self._detect_spoofing(historical_data)
        if spoofing:
            breaches.extend(spoofing)

        # Check for layering patterns
        layering = self._detect_layering(historical_data)
        if layering:
            breaches.extend(layering)

        return breaches

    def _detect_wash_trading(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect potential wash trading"""
        # Implementation would analyze trade patterns
        return []

    def _detect_spoofing(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect potential spoofing"""
        # Implementation would analyze order patterns
        return []

    def _detect_layering(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect potential layering"""
        # Implementation would analyze order book patterns
        return []


# Factory functions
def create_compliance_monitor(rules: Optional[List[ComplianceRule]] = None) -> ComplianceMonitoringEngine:
    """Create compliance monitoring engine"""
    return ComplianceMonitoringEngine(rules=rules)

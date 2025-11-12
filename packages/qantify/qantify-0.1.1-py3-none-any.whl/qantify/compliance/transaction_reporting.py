"""
Transaction Reporting Engine
============================

Comprehensive transaction reporting system for regulatory compliance.
Handles trade reporting, order reporting, execution reporting, settlement reporting,
and regulatory transaction disclosures across multiple jurisdictions.

Key Features:
- Trade reporting (FINRA, FCA, MAS, ASIC)
- Order reporting and tracking
- Execution quality reporting
- Settlement reporting
- Cross-border transaction reporting
- Transaction cost analysis
- Regulatory deadline management
- Automated filing systems
- Transaction reconciliation
- Best execution reporting
- Transaction impact analysis
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum
import json
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


class TransactionType(Enum):
    """Types of financial transactions"""
    EQUITY_TRADE = "equity_trade"
    BOND_TRADE = "bond_trade"
    DERIVATIVE_TRADE = "derivative_trade"
    FX_TRADE = "fx_trade"
    COMMODITY_TRADE = "commodity_trade"
    CRYPTO_TRADE = "crypto_trade"
    OTC_DERIVATIVE = "otc_derivative"
    REPO_TRANSACTION = "repo_transaction"
    SECURITIES_LENDING = "securities_lending"


class ReportingStatus(Enum):
    """Transaction reporting status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"


class ExecutionVenue(Enum):
    """Execution venues"""
    EXCHANGE = "exchange"
    OTC = "otc"
    DARK_POOL = "dark_pool"
    INTERNAL_CROSS = "internal_cross"
    SYSTEMATIC_INTERNALISER = "systematic_internaliser"


@dataclass
class TransactionReport:
    """Transaction report data structure"""
    report_id: str
    transaction_id: str
    reporting_firm: str
    counterparty: str
    transaction_type: TransactionType
    execution_venue: ExecutionVenue
    trade_date: date
    settlement_date: date
    instrument_id: str
    instrument_name: str
    quantity: float
    price: float
    currency: str
    gross_amount: float
    net_amount: float
    commission: float
    fees: float
    taxes: float
    reporting_timestamp: datetime
    reporting_status: ReportingStatus = ReportingStatus.PENDING
    regulatory_authority: str = ""
    report_format: str = "standard"
    validation_errors: List[str] = field(default_factory=list)
    amendments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.report_id:
            self.report_id = f"TR_{self.transaction_id}_{int(self.reporting_timestamp.timestamp())}"


@dataclass
class OrderReport:
    """Order report data structure"""
    order_id: str
    client_id: str
    instrument_id: str
    order_type: str
    side: str  # Buy/Sell
    quantity: float
    limit_price: Optional[float]
    stop_price: Optional[float]
    order_timestamp: datetime
    execution_reports: List[Dict[str, Any]] = field(default_factory=list)
    order_status: str = "active"
    total_executed: float = 0.0
    average_price: float = 0.0
    reporting_required: bool = True


@dataclass
class ExecutionReport:
    """Execution report data structure"""
    execution_id: str
    order_id: str
    transaction_id: str
    execution_timestamp: datetime
    quantity: float
    price: float
    venue: ExecutionVenue
    counterparty: str
    execution_quality: Dict[str, Any] = field(default_factory=dict)
    market_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SettlementReport:
    """Settlement report data structure"""
    settlement_id: str
    transaction_id: str
    settlement_date: date
    settlement_amount: float
    settlement_currency: str
    settlement_status: str = "pending"
    settlement_instructions: Dict[str, Any] = field(default_factory=dict)
    confirmation_timestamp: Optional[datetime] = None
    failure_reason: Optional[str] = None


class TransactionReportingEngine:
    """Main transaction reporting engine"""

    def __init__(self, firm_id: str, regulatory_frameworks: Optional[List[str]] = None):
        self.firm_id = firm_id
        self.regulatory_frameworks = regulatory_frameworks or ['FINRA', 'SEC', 'FCA']
        self.transaction_reports: Dict[str, TransactionReport] = {}
        self.order_reports: Dict[str, OrderReport] = {}
        self.execution_reports: Dict[str, ExecutionReport] = {}
        self.settlement_reports: Dict[str, SettlementReport] = {}

        # Initialize reporters
        self.trade_reporter = TradeReporting(self)
        self.order_reporter = OrderReporting(self)
        self.execution_reporter = ExecutionReporting(self)
        self.settlement_reporter = SettlementReporting(self)
        self.cross_reporter = CrossReporting(self)
        self.regulatory_reporter = RegulatoryTradeReporting(self)
        self.cost_analyzer = TransactionCostAnalysis(self)

        # Reporting queues and processing
        self.pending_reports: List[TransactionReport] = []
        self.reporting_deadlines: Dict[str, datetime] = {}

        self._initialize_reporting_deadlines()

    def _initialize_reporting_deadlines(self):
        """Initialize regulatory reporting deadlines"""
        # T+1 for US equity trades
        self.reporting_deadlines['US_EQUITY'] = datetime.now() + timedelta(days=1)
        # T+2 for settlement
        self.reporting_deadlines['SETTLEMENT'] = datetime.now() + timedelta(days=2)

    def submit_transaction_report(self, transaction_data: Dict[str, Any]) -> str:
        """Submit a transaction for reporting"""
        # Create transaction report
        report = TransactionReport(
            report_id="",
            transaction_id=transaction_data['transaction_id'],
            reporting_firm=self.firm_id,
            counterparty=transaction_data['counterparty'],
            transaction_type=TransactionType(transaction_data['transaction_type']),
            execution_venue=ExecutionVenue(transaction_data['execution_venue']),
            trade_date=transaction_data['trade_date'],
            settlement_date=transaction_data['settlement_date'],
            instrument_id=transaction_data['instrument_id'],
            instrument_name=transaction_data['instrument_name'],
            quantity=transaction_data['quantity'],
            price=transaction_data['price'],
            currency=transaction_data.get('currency', 'USD'),
            gross_amount=transaction_data['quantity'] * transaction_data['price'],
            net_amount=transaction_data.get('net_amount', transaction_data['quantity'] * transaction_data['price']),
            commission=transaction_data.get('commission', 0.0),
            fees=transaction_data.get('fees', 0.0),
            taxes=transaction_data.get('taxes', 0.0),
            reporting_timestamp=datetime.now(),
            regulatory_authority=transaction_data.get('regulatory_authority', 'FINRA')
        )

        # Validate report
        is_valid, errors = self._validate_transaction_report(report)
        if not is_valid:
            report.validation_errors = errors
            report.reporting_status = ReportingStatus.REJECTED

        # Store report
        self.transaction_reports[report.report_id] = report

        # Add to pending reports if valid
        if is_valid:
            self.pending_reports.append(report)

        return report.report_id

    def _validate_transaction_report(self, report: TransactionReport) -> Tuple[bool, List[str]]:
        """Validate transaction report"""
        errors = []

        # Required fields validation
        required_fields = [
            'transaction_id', 'reporting_firm', 'counterparty', 'instrument_id',
            'quantity', 'price', 'trade_date', 'settlement_date'
        ]

        for field in required_fields:
            value = getattr(report, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"Missing required field: {field}")

        # Business logic validation
        if report.quantity <= 0:
            errors.append("Quantity must be positive")

        if report.price <= 0:
            errors.append("Price must be positive")

        if report.settlement_date < report.trade_date:
            errors.append("Settlement date cannot be before trade date")

        # Regulatory-specific validation
        if report.regulatory_authority == 'FINRA':
            errors.extend(self._validate_finra_report(report))
        elif report.regulatory_authority == 'FCA':
            errors.extend(self._validate_fca_report(report))

        return len(errors) == 0, errors

    def _validate_finra_report(self, report: TransactionReport) -> List[str]:
        """Validate FINRA-specific requirements"""
        errors = []

        # FINRA T+1 reporting requirement
        reporting_deadline = report.trade_date + timedelta(days=1)
        if datetime.now() > datetime.combine(reporting_deadline, datetime.max.time()):
            errors.append("FINRA reporting deadline (T+1) exceeded")

        # Market center validation
        valid_venues = ['NSDQ', 'NYSE', 'ARCA', 'BATS', 'EDGX']
        if hasattr(report.execution_venue, 'value'):
            venue_code = report.execution_venue.value.upper()
            if venue_code not in valid_venues:
                errors.append(f"Invalid FINRA market center: {venue_code}")

        return errors

    def _validate_fca_report(self, report: TransactionReport) -> List[str]:
        """Validate FCA/MiFID II requirements"""
        errors = []

        # MiFID II validation
        required_mifid_fields = ['investment_decision', 'execution_decision']
        for field in required_mifid_fields:
            if field not in report.metadata:
                errors.append(f"Missing MiFID II required field: {field}")

        # Client categorization
        if 'client_type' not in report.metadata:
            errors.append("Missing client type categorization for MiFID II")

        return errors

    def submit_order_report(self, order_data: Dict[str, Any]) -> str:
        """Submit order for reporting"""
        order_report = OrderReport(
            order_id=order_data['order_id'],
            client_id=order_data['client_id'],
            instrument_id=order_data['instrument_id'],
            order_type=order_data['order_type'],
            side=order_data['side'],
            quantity=order_data['quantity'],
            limit_price=order_data.get('limit_price'),
            stop_price=order_data.get('stop_price'),
            order_timestamp=order_data.get('timestamp', datetime.now())
        )

        self.order_reports[order_report.order_id] = order_report
        return order_report.order_id

    def submit_execution_report(self, execution_data: Dict[str, Any]) -> str:
        """Submit execution for reporting"""
        execution_report = ExecutionReport(
            execution_id=execution_data['execution_id'],
            order_id=execution_data['order_id'],
            transaction_id=execution_data['transaction_id'],
            execution_timestamp=execution_data.get('timestamp', datetime.now()),
            quantity=execution_data['quantity'],
            price=execution_data['price'],
            venue=ExecutionVenue(execution_data['venue']),
            counterparty=execution_data['counterparty'],
            execution_quality=execution_data.get('execution_quality', {}),
            market_conditions=execution_data.get('market_conditions', {})
        )

        self.execution_reports[execution_report.execution_id] = execution_report

        # Update order report
        if execution_report.order_id in self.order_reports:
            order = self.order_reports[execution_report.order_id]
            order.execution_reports.append({
                'execution_id': execution_report.execution_id,
                'quantity': execution_report.quantity,
                'price': execution_report.price,
                'timestamp': execution_report.execution_timestamp
            })

            # Update order statistics
            total_quantity = sum(ex['quantity'] for ex in order.execution_reports)
            total_value = sum(ex['quantity'] * ex['price'] for ex in order.execution_reports)

            order.total_executed = total_quantity
            if total_quantity > 0:
                order.average_price = total_value / total_quantity

        return execution_report.execution_id

    def submit_settlement_report(self, settlement_data: Dict[str, Any]) -> str:
        """Submit settlement for reporting"""
        settlement_report = SettlementReport(
            settlement_id=settlement_data['settlement_id'],
            transaction_id=settlement_data['transaction_id'],
            settlement_date=settlement_data['settlement_date'],
            settlement_amount=settlement_data['settlement_amount'],
            settlement_currency=settlement_data.get('currency', 'USD'),
            settlement_instructions=settlement_data.get('instructions', {}),
            confirmation_timestamp=datetime.now() if settlement_data.get('confirmed') else None
        )

        self.settlement_reports[settlement_report.settlement_id] = settlement_report
        return settlement_report.settlement_id

    def generate_trade_report(self,
                            start_date: date,
                            end_date: date,
                            regulatory_authority: str = "FINRA") -> Dict[str, Any]:
        """Generate trade reporting file"""
        # Filter reports by date and authority
        reports = [
            report for report in self.transaction_reports.values()
            if start_date <= report.trade_date <= end_date and
            report.regulatory_authority == regulatory_authority
        ]

        report_data = {
            'reporting_period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'reporting_firm': self.firm_id,
            'regulatory_authority': regulatory_authority,
            'total_trades': len(reports),
            'trades': [],
            'summary': self._calculate_trade_summary(reports)
        }

        # Add trade details
        for report in reports:
            trade_detail = {
                'report_id': report.report_id,
                'transaction_id': report.transaction_id,
                'trade_date': report.trade_date.isoformat(),
                'settlement_date': report.settlement_date.isoformat(),
                'instrument_id': report.instrument_id,
                'instrument_name': report.instrument_name,
                'quantity': report.quantity,
                'price': report.price,
                'gross_amount': report.gross_amount,
                'counterparty': report.counterparty,
                'execution_venue': report.execution_venue.value,
                'reporting_status': report.reporting_status.value
            }
            report_data['trades'].append(trade_detail)

        return report_data

    def _calculate_trade_summary(self, reports: List[TransactionReport]) -> Dict[str, Any]:
        """Calculate trade summary statistics"""
        if not reports:
            return {}

        quantities = [r.quantity for r in reports]
        prices = [r.price for r in reports]
        gross_amounts = [r.gross_amount for r in reports]

        return {
            'total_quantity': sum(quantities),
            'average_price': np.mean(prices),
            'total_gross_amount': sum(gross_amounts),
            'average_trade_size': np.mean(gross_amounts),
            'trade_count': len(reports),
            'price_volatility': np.std(prices) if len(prices) > 1 else 0.0,
            'venue_distribution': self._calculate_venue_distribution(reports)
        }

    def _calculate_venue_distribution(self, reports: List[TransactionReport]) -> Dict[str, int]:
        """Calculate trade distribution by venue"""
        venue_counts = {}
        for report in reports:
            venue = report.execution_venue.value
            venue_counts[venue] = venue_counts.get(venue, 0) + 1
        return venue_counts

    def generate_execution_quality_report(self,
                                       order_id: str,
                                       benchmark_period: int = 30) -> Dict[str, Any]:
        """Generate execution quality report for an order"""
        order = self.order_reports.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        executions = order.execution_reports

        if not executions:
            return {'order_id': order_id, 'message': 'No executions found'}

        # Calculate execution quality metrics
        execution_times = [ex['timestamp'] for ex in executions]
        prices = [ex['price'] for ex in executions]
        quantities = [ex['quantity'] for ex in executions]

        # Market impact calculation (simplified)
        avg_price = sum(p * q for p, q in zip(prices, quantities)) / sum(quantities)

        # VWAP calculation (simplified - would need market data)
        vwap = avg_price  # Placeholder

        # Implementation shortfall
        arrival_price = prices[0] if prices else 0  # First execution price as proxy
        implementation_shortfall = (avg_price - arrival_price) / arrival_price if arrival_price > 0 else 0

        return {
            'order_id': order_id,
            'execution_summary': {
                'total_executed': order.total_executed,
                'average_price': order.average_price,
                'execution_count': len(executions),
                'time_to_completion': (max(execution_times) - min(execution_times)).total_seconds() if execution_times else 0
            },
            'execution_quality': {
                'vwap_comparison': (avg_price - vwap) / vwap if vwap > 0 else 0,
                'implementation_shortfall': implementation_shortfall,
                'market_impact_estimate': self._estimate_market_impact(order, executions),
                'timing_quality': self._assess_timing_quality(executions)
            },
            'best_execution_analysis': {
                'benchmark_compliance': True,  # Placeholder
                'price_improvement': self._calculate_price_improvement(order, executions),
                'liquidity_assessment': 'Good'  # Placeholder
            }
        }

    def _estimate_market_impact(self, order: OrderReport, executions: List[Dict[str, Any]]) -> float:
        """Estimate market impact of executions"""
        # Simplified market impact model
        total_quantity = sum(ex['quantity'] for ex in executions)
        avg_daily_volume = 1000000  # Placeholder - would need real market data

        participation_rate = total_quantity / avg_daily_volume
        market_impact = 0.1 * participation_rate  # Simplified model

        return market_impact

    def _assess_timing_quality(self, executions: List[Dict[str, Any]]) -> str:
        """Assess timing quality of executions"""
        if len(executions) <= 1:
            return "Single execution - timing N/A"

        # Check if executions are spread throughout the day
        timestamps = [ex['timestamp'] for ex in executions]
        time_span = max(timestamps) - min(timestamps)

        if time_span.total_seconds() > 3600:  # More than 1 hour
            return "Good - executions spread over time"
        else:
            return "Poor - executions concentrated in time"

    def _calculate_price_improvement(self, order: OrderReport, executions: List[Dict[str, Any]]) -> float:
        """Calculate price improvement over limit price"""
        if not order.limit_price:
            return 0.0

        avg_execution_price = order.average_price
        limit_price = order.limit_price

        if order.side.upper() == 'BUY':
            improvement = (limit_price - avg_execution_price) / limit_price
        else:  # SELL
            improvement = (avg_execution_price - limit_price) / limit_price

        return improvement

    def generate_transaction_cost_analysis(self,
                                       start_date: date,
                                       end_date: date) -> Dict[str, Any]:
        """Generate transaction cost analysis report"""
        reports = [
            report for report in self.transaction_reports.values()
            if start_date <= report.trade_date <= end_date
        ]

        if not reports:
            return {'message': 'No transactions found in period'}

        # Calculate cost metrics
        total_commission = sum(r.commission for r in reports)
        total_fees = sum(r.fees for r in reports)
        total_taxes = sum(r.taxes for r in reports)
        total_gross_amount = sum(r.gross_amount for r in reports)

        total_cost = total_commission + total_fees + total_taxes
        cost_percentage = (total_cost / total_gross_amount) * 100 if total_gross_amount > 0 else 0

        # Cost breakdown by transaction type
        cost_by_type = {}
        for report in reports:
            tx_type = report.transaction_type.value
            if tx_type not in cost_by_type:
                cost_by_type[tx_type] = {'count': 0, 'total_cost': 0.0, 'total_amount': 0.0}

            cost_by_type[tx_type]['count'] += 1
            cost_by_type[tx_type]['total_cost'] += report.commission + report.fees + report.taxes
            cost_by_type[tx_type]['total_amount'] += report.gross_amount

        # Calculate averages
        for tx_type in cost_by_type:
            data = cost_by_type[tx_type]
            if data['total_amount'] > 0:
                data['avg_cost_percentage'] = (data['total_cost'] / data['total_amount']) * 100

        return {
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'summary': {
                'total_transactions': len(reports),
                'total_gross_amount': total_gross_amount,
                'total_cost': total_cost,
                'cost_percentage': cost_percentage,
                'average_cost_per_trade': total_cost / len(reports) if reports else 0
            },
            'cost_breakdown': {
                'commission': total_commission,
                'fees': total_fees,
                'taxes': total_taxes
            },
            'cost_by_type': cost_by_type,
            'cost_efficiency_metrics': {
                'cost_per_million': (total_cost / total_gross_amount) * 1000000 if total_gross_amount > 0 else 0,
                'cost_trend': self._calculate_cost_trend(reports)
            }
        }

    def _calculate_cost_trend(self, reports: List[TransactionReport]) -> str:
        """Calculate cost trend over time"""
        if len(reports) < 10:
            return "Insufficient data for trend analysis"

        # Sort by trade date
        sorted_reports = sorted(reports, key=lambda r: r.trade_date)

        # Calculate rolling average cost percentage
        cost_percentages = [
            ((r.commission + r.fees + r.taxes) / r.gross_amount) * 100
            for r in sorted_reports if r.gross_amount > 0
        ]

        if len(cost_percentages) < 5:
            return "Insufficient data for trend analysis"

        # Simple trend analysis
        first_half = np.mean(cost_percentages[:len(cost_percentages)//2])
        second_half = np.mean(cost_percentages[len(cost_percentages)//2:])

        if second_half > first_half * 1.05:
            return "Increasing"
        elif second_half < first_half * 0.95:
            return "Decreasing"
        else:
            return "Stable"

    def get_reporting_status(self, report_id: str) -> Optional[ReportingStatus]:
        """Get reporting status for a transaction"""
        report = self.transaction_reports.get(report_id)
        return report.reporting_status if report else None

    def update_reporting_status(self, report_id: str, status: ReportingStatus, notes: str = ""):
        """Update reporting status"""
        report = self.transaction_reports.get(report_id)
        if report:
            report.reporting_status = status
            report.metadata['status_update_notes'] = notes
            report.metadata['status_update_timestamp'] = datetime.now()

    def get_pending_reports(self) -> List[TransactionReport]:
        """Get all pending reports"""
        return [r for r in self.pending_reports if r.reporting_status == ReportingStatus.PENDING]

    def export_reports(self, format: str = 'json') -> str:
        """Export all reports"""
        data = {
            'transaction_reports': [vars(r) for r in self.transaction_reports.values()],
            'order_reports': [vars(r) for r in self.order_reports.values()],
            'execution_reports': [vars(r) for r in self.execution_reports.values()],
            'settlement_reports': [vars(r) for r in self.settlement_reports.values()],
            'export_timestamp': datetime.now().isoformat()
        }

        if format == 'json':
            return json.dumps(data, default=str, indent=2)
        else:
            return json.dumps(data, default=str)  # Default to JSON


# Specialized Reporting Components
class TradeReporting:
    """Trade reporting component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def generate_finra_report(self, trades: List[TransactionReport]) -> str:
        """Generate FINRA trade reporting format"""
        # FINRA TRF format
        report_lines = []

        for trade in trades:
            line = (
                f"{trade.transaction_id}|"
                f"{trade.trade_date.strftime('%Y%m%d')}|"
                f"{trade.settlement_date.strftime('%Y%m%d')}|"
                f"{trade.instrument_id}|"
                f"{trade.quantity}|"
                f"{trade.price}|"
                f"{trade.counterparty}|"
                f"{trade.execution_venue.value}|"
                f"{self.engine.firm_id}"
            )
            report_lines.append(line)

        return "\n".join(report_lines)

    def generate_fca_report(self, trades: List[TransactionReport]) -> str:
        """Generate FCA/MiFID II reporting format"""
        # XML format for FCA reporting
        root = ET.Element("MIFIDTransactionReport")
        ET.SubElement(root, "ReportingEntity").text = self.engine.firm_id

        for trade in trades:
            trade_elem = ET.SubElement(root, "Transaction")
            ET.SubElement(trade_elem, "TransactionID").text = trade.transaction_id
            ET.SubElement(trade_elem, "TradeDate").text = trade.trade_date.isoformat()
            ET.SubElement(trade_elem, "InstrumentID").text = trade.instrument_id
            ET.SubElement(trade_elem, "Quantity").text = str(trade.quantity)
            ET.SubElement(trade_elem, "Price").text = str(trade.price)
            ET.SubElement(trade_elem, "Venue").text = trade.execution_venue.value

        return ET.tostring(root, encoding='unicode')


class OrderReporting:
    """Order reporting component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def track_order_lifecycle(self, order_id: str) -> Dict[str, Any]:
        """Track complete order lifecycle"""
        order = self.engine.order_reports.get(order_id)
        if not order:
            return {'error': f'Order {order_id} not found'}

        executions = order.execution_reports

        lifecycle = {
            'order_id': order_id,
            'order_timestamp': order.order_timestamp,
            'total_quantity': order.quantity,
            'executed_quantity': order.total_executed,
            'remaining_quantity': order.quantity - order.total_executed,
            'execution_percentage': (order.total_executed / order.quantity) * 100 if order.quantity > 0 else 0,
            'execution_summary': {
                'execution_count': len(executions),
                'average_price': order.average_price,
                'best_price': min(ex['price'] for ex in executions) if executions else None,
                'worst_price': max(ex['price'] for ex in executions) if executions else None
            },
            'timing_analysis': self._analyze_execution_timing(executions),
            'venue_analysis': self._analyze_venue_usage(executions)
        }

        return lifecycle

    def _analyze_execution_timing(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze execution timing patterns"""
        if not executions:
            return {}

        timestamps = [ex['timestamp'] for ex in executions]
        time_span = max(timestamps) - min(timestamps)

        return {
            'total_duration_seconds': time_span.total_seconds(),
            'first_execution': min(timestamps),
            'last_execution': max(timestamps),
            'execution_pace': len(executions) / max(time_span.total_seconds() / 3600, 1)  # executions per hour
        }

    def _analyze_venue_usage(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze execution venue usage"""
        venue_counts = {}
        for ex in executions:
            venue = ex.get('venue', 'unknown')
            venue_counts[venue] = venue_counts.get(venue, 0) + 1

        return {
            'venue_distribution': venue_counts,
            'primary_venue': max(venue_counts.keys(), key=lambda k: venue_counts[k]) if venue_counts else None,
            'venue_count': len(venue_counts)
        }


class ExecutionReporting:
    """Execution reporting component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def calculate_execution_quality(self, execution_id: str) -> Dict[str, Any]:
        """Calculate execution quality metrics"""
        execution = self.engine.execution_reports.get(execution_id)
        if not execution:
            return {'error': f'Execution {execution_id} not found'}

        # Quality metrics calculation
        quality_metrics = {
            'execution_id': execution_id,
            'market_conditions': execution.market_conditions,
            'quality_indicators': {
                'price_improvement': self._calculate_price_improvement(execution),
                'market_impact': self._estimate_market_impact(execution),
                'timing_quality': self._assess_timing_quality(execution),
                'liquidity_quality': self._assess_liquidity_quality(execution)
            },
            'benchmark_comparison': {
                'vwap_comparison': 0.0,  # Would need market data
                'arrival_price_comparison': 0.0,  # Would need order data
                'benchmark_execution_time': 0.0  # Would need market data
            }
        }

        return quality_metrics

    def _calculate_price_improvement(self, execution: ExecutionReport) -> float:
        """Calculate price improvement"""
        # Simplified - would need order reference price
        return 0.0

    def _estimate_market_impact(self, execution: ExecutionReport) -> float:
        """Estimate market impact"""
        # Simplified model
        quantity = execution.quantity
        avg_daily_volume = 1000000  # Placeholder
        participation_rate = quantity / avg_daily_volume
        return 0.05 * participation_rate  # Simplified impact model

    def _assess_timing_quality(self, execution: ExecutionReport) -> str:
        """Assess timing quality"""
        # Simplified assessment
        return "Good"

    def _assess_liquidity_quality(self, execution: ExecutionReport) -> str:
        """Assess liquidity quality"""
        # Simplified assessment
        return "Adequate"


class SettlementReporting:
    """Settlement reporting component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def track_settlement_status(self, transaction_id: str) -> Dict[str, Any]:
        """Track settlement status for transaction"""
        settlement_reports = [
            r for r in self.engine.settlement_reports.values()
            if r.transaction_id == transaction_id
        ]

        if not settlement_reports:
            return {'transaction_id': transaction_id, 'status': 'No settlement record'}

        latest_settlement = max(settlement_reports, key=lambda r: r.confirmation_timestamp or datetime.min)

        return {
            'transaction_id': transaction_id,
            'settlement_id': latest_settlement.settlement_id,
            'settlement_date': latest_settlement.settlement_date,
            'settlement_amount': latest_settlement.settlement_amount,
            'settlement_status': latest_settlement.settlement_status,
            'confirmation_timestamp': latest_settlement.confirmation_timestamp,
            'instructions': latest_settlement.settlement_instructions,
            'failure_reason': latest_settlement.failure_reason
        }


class CrossReporting:
    """Cross-border transaction reporting"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def identify_cross_border_trades(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Identify cross-border transactions requiring reporting"""
        reports = [
            r for r in self.engine.transaction_reports.values()
            if start_date <= r.trade_date <= end_date
        ]

        cross_border_trades = []
        for report in reports:
            # Simplified cross-border detection
            # In practice, would check counterparty jurisdiction, execution venue, etc.
            if report.counterparty_country != 'US':  # Assuming US domestic
                cross_border_trades.append({
                    'transaction_id': report.transaction_id,
                    'counterparty_country': report.counterparty_country,
                    'execution_venue': report.execution_venue.value,
                    'reporting_requirements': self._determine_reporting_requirements(report)
                })

        return cross_border_trades

    def _determine_reporting_requirements(self, report: TransactionReport) -> List[str]:
        """Determine reporting requirements for cross-border trade"""
        requirements = []

        counterparty_country = report.counterparty_country

        # EU reporting requirements
        if counterparty_country in ['GB', 'DE', 'FR', 'IT', 'ES']:
            requirements.append('FCA_MiFID_II')
            requirements.append('EMIR')

        # US reporting requirements
        if counterparty_country == 'US':
            requirements.append('FINRA')
            requirements.append('SEC_Form_13F')

        # Other jurisdictions
        if counterparty_country == 'SG':
            requirements.append('MAS')

        if counterparty_country == 'AU':
            requirements.append('ASIC')

        return requirements


class RegulatoryTradeReporting:
    """Regulatory trade reporting component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def generate_regulatory_reports(self, start_date: date, end_date: date) -> Dict[str, List[str]]:
        """Generate all required regulatory reports"""
        reports = {}

        # FINRA reports
        if 'FINRA' in self.engine.regulatory_frameworks:
            finra_trades = [
                r for r in self.engine.transaction_reports.values()
                if r.regulatory_authority == 'FINRA' and start_date <= r.trade_date <= end_date
            ]
            reports['FINRA'] = self.engine.trade_reporter.generate_finra_report(finra_trades)

        # FCA reports
        if 'FCA' in self.engine.regulatory_frameworks:
            fca_trades = [
                r for r in self.engine.transaction_reports.values()
                if r.regulatory_authority == 'FCA' and start_date <= r.trade_date <= end_date
            ]
            reports['FCA'] = self.engine.trade_reporter.generate_fca_report(fca_trades)

        return reports


class TransactionCostAnalysis:
    """Transaction cost analysis component"""

    def __init__(self, engine: TransactionReportingEngine):
        self.engine = engine

    def analyze_cost_efficiency(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Analyze transaction cost efficiency"""
        return self.engine.generate_transaction_cost_analysis(start_date, end_date)

    def benchmark_costs(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Benchmark transaction costs against industry standards"""
        analysis = self.analyze_cost_efficiency(start_date, end_date)

        # Simplified benchmarking
        benchmarks = {
            'equity_trades': {
                'industry_average': 0.15,  # 15 bps
                'top_quartile': 0.10,     # 10 bps
                'bottom_quartile': 0.25   # 25 bps
            },
            'fixed_income': {
                'industry_average': 0.08,  # 8 bps
                'top_quartile': 0.05,
                'bottom_quartile': 0.15
            }
        }

        cost_percentage = analysis.get('summary', {}).get('cost_percentage', 0)

        if cost_percentage <= 0.10:
            performance = 'Top quartile'
        elif cost_percentage <= 0.15:
            performance = 'Above average'
        elif cost_percentage <= 0.25:
            performance = 'Below average'
        else:
            performance = 'Bottom quartile'

        return {
            'actual_cost_percentage': cost_percentage,
            'performance_rating': performance,
            'benchmarks': benchmarks,
            'recommendations': self._generate_cost_recommendations(cost_percentage, performance)
        }

    def _generate_cost_recommendations(self, cost_percentage: float, performance: str) -> List[str]:
        """Generate cost reduction recommendations"""
        recommendations = []

        if performance in ['Below average', 'Bottom quartile']:
            recommendations.append("Consider using lower-cost execution venues")
            recommendations.append("Implement algorithmic trading to reduce market impact")
            recommendations.append("Negotiate better commission rates with brokers")

        if cost_percentage > 0.20:
            recommendations.append("Review order sizing strategy to reduce market impact")
            recommendations.append("Implement smart order routing for better execution")

        recommendations.append("Regularly benchmark execution costs against industry standards")

        return recommendations


# Factory functions
def create_transaction_reporter(firm_id: str,
                              regulatory_frameworks: Optional[List[str]] = None) -> TransactionReportingEngine:
    """Create transaction reporting engine"""
    return TransactionReportingEngine(firm_id, regulatory_frameworks)

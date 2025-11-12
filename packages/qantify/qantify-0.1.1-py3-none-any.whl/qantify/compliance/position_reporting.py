"""
Position Reporting Engine
========================

Comprehensive position reporting system for regulatory compliance and risk management.
Handles portfolio position reporting, security position tracking, derivative positions,
FX positions, position aggregation, and regulatory disclosures.

Key Features:
- Portfolio position reporting
- Security position tracking
- Derivative position reporting
- FX position reporting
- Position aggregation and consolidation
- Position reconciliation
- Regulatory position disclosures
- Position limit monitoring
- Concentration risk reporting
- Position valuation and P&L reporting
- Intraday position tracking
- End-of-day position reporting
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


class PositionType(Enum):
    """Types of financial positions"""
    LONG = "long"
    SHORT = "short"
    CASH = "cash"
    SECURITY = "security"
    DERIVATIVE = "derivative"
    FX = "fx"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAPS = "swaps"
    BONDS = "bonds"


class AssetClass(Enum):
    """Asset class classifications"""
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    DERIVATIVES = "derivatives"
    FX = "fx"
    COMMODITIES = "commodities"
    ALTERNATIVES = "alternatives"
    CASH = "cash"


class ReportingFrequency(Enum):
    """Position reporting frequencies"""
    INTRADAY = "intraday"
    END_OF_DAY = "end_of_day"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class PositionRecord:
    """Position record data structure"""
    position_id: str
    portfolio_id: str
    instrument_id: str
    instrument_name: str
    asset_class: AssetClass
    position_type: PositionType
    quantity: float
    average_cost: float
    market_price: float
    market_value: float
    unrealized_pnl: float
    currency: str
    counterparty: Optional[str] = None
    maturity_date: Optional[date] = None
    strike_price: Optional[float] = None
    underlying_asset: Optional[str] = None
    reporting_date: date = field(default_factory=date.today)
    valuation_date: date = field(default_factory=date.today)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.position_id:
            self.position_id = f"POS_{self.portfolio_id}_{self.instrument_id}_{int(datetime.now().timestamp())}"


@dataclass
class PositionReconciliation:
    """Position reconciliation record"""
    portfolio_id: str
    reconciliation_date: date
    source_system: str
    target_system: str
    total_positions: int
    matched_positions: int
    unmatched_positions: int
    reconciliation_id: str = ""
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    reconciliation_status: str = "in_progress"
    reconciliation_report: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.reconciliation_id:
            self.reconciliation_id = f"RECON_{self.portfolio_id}_{self.reconciliation_date}_{uuid.uuid4().hex[:8]}"


@dataclass
class PortfolioPosition:
    """Portfolio-level position aggregation"""
    portfolio_id: str
    reporting_date: date
    total_value: float
    total_pnl: float
    positions: List[PositionRecord] = field(default_factory=list)
    asset_allocation: Dict[str, float] = field(default_factory=dict)
    sector_allocation: Dict[str, float] = field(default_factory=dict)
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, Any] = field(default_factory=dict)

    def calculate_allocations(self):
        """Calculate asset and sector allocations"""
        if not self.positions or self.total_value <= 0:
            return

        # Asset class allocation
        asset_values = {}
        sector_values = {}

        for position in self.positions:
            asset_class = position.asset_class.value
            sector = position.metadata.get('sector', 'Unknown')

            if asset_class not in asset_values:
                asset_values[asset_class] = 0
            asset_values[asset_class] += position.market_value

            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += position.market_value

        # Convert to percentages
        self.asset_allocation = {
            asset: (value / self.total_value) * 100
            for asset, value in asset_values.items()
        }

        self.sector_allocation = {
            sector: (value / self.total_value) * 100
            for sector, value in sector_values.items()
        }


@dataclass
class PositionReconciliation:
    """Position reconciliation record"""
    reconciliation_id: str
    portfolio_id: str
    reconciliation_date: date
    source_system: str
    target_system: str
    total_positions: int
    matched_positions: int
    unmatched_positions: int
    reconciliation_status: str = "pending"
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    reconciliation_report: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.reconciliation_id:
            self.reconciliation_id = f"REC_{self.portfolio_id}_{int(datetime.now().timestamp())}"


class PositionReportingEngine:
    """Main position reporting engine"""

    def __init__(self, firm_id: str):
        self.firm_id = firm_id
        self.positions: Dict[str, PositionRecord] = {}
        self.portfolio_positions: Dict[str, PortfolioPosition] = {}
        self.reconciliations: Dict[str, PositionReconciliation] = {}

        # Initialize reporters
        self.portfolio_reporter = PortfolioPositionReporter(self)
        self.security_reporter = SecurityPositionReporter(self)
        self.derivative_reporter = DerivativePositionReporter(self)
        self.fx_reporter = FXPositionReporter(self)
        self.aggregation_engine = PositionAggregationEngine(self)
        # reconciliation_engine is self for compatibility
        self.reconciliation_engine = self

        # Reporting configuration
        self.reporting_frequencies = {
            'intraday': timedelta(hours=1),
            'end_of_day': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
            'quarterly': timedelta(days=90)
        }

    def record_position(self, position_data: Dict[str, Any]) -> str:
        """Record a position"""
        position = PositionRecord(
            position_id=position_data.get('position_id', ''),
            portfolio_id=position_data['portfolio_id'],
            instrument_id=position_data['instrument_id'],
            instrument_name=position_data['instrument_name'],
            asset_class=AssetClass(position_data['asset_class']),
            position_type=PositionType(position_data['position_type']),
            quantity=position_data['quantity'],
            average_cost=position_data['average_cost'],
            market_price=position_data['market_price'],
            market_value=position_data['market_value'],
            unrealized_pnl=position_data.get('unrealized_pnl', 0.0),
            currency=position_data.get('currency', 'USD'),
            counterparty=position_data.get('counterparty'),
            maturity_date=position_data.get('maturity_date'),
            strike_price=position_data.get('strike_price'),
            underlying_asset=position_data.get('underlying_asset'),
            metadata=position_data.get('metadata', {})
        )

        # Calculate unrealized P&L if not provided
        if position.unrealized_pnl == 0.0:
            position.unrealized_pnl = (position.market_price - position.average_cost) * position.quantity

        self.positions[position.position_id] = position
        return position.position_id

    def update_position(self, position_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing position"""
        if position_id not in self.positions:
            return False

        position = self.positions[position_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(position, key):
                setattr(position, key, value)

        # Recalculate unrealized P&L
        position.unrealized_pnl = (position.market_price - position.average_cost) * position.quantity
        position.market_value = position.market_price * position.quantity

        return True

    def get_portfolio_positions(self, portfolio_id: str, reporting_date: Optional[date] = None) -> PortfolioPosition:
        """Get aggregated portfolio positions"""
        if reporting_date is None:
            reporting_date = date.today()

        # Get positions for portfolio (ignore date filter for now)
        portfolio_positions = [
            pos for pos in self.positions.values()
            if pos.portfolio_id == portfolio_id
        ]

        # Group by instrument (latest position per instrument)
        latest_positions = {}
        for pos in portfolio_positions:
            instrument_key = pos.instrument_id
            if instrument_key not in latest_positions:
                latest_positions[instrument_key] = pos

        positions = list(latest_positions.values())

        # Calculate totals
        total_value = sum(pos.market_value for pos in positions)
        total_pnl = sum(pos.unrealized_pnl for pos in positions)

        # Create portfolio position object
        portfolio_position = PortfolioPosition(
            portfolio_id=portfolio_id,
            reporting_date=reporting_date,
            total_value=total_value,
            total_pnl=total_pnl,
            positions=positions
        )

        # Calculate allocations
        portfolio_position.calculate_allocations()

        # Calculate risk metrics
        portfolio_position.risk_metrics = self._calculate_portfolio_risk_metrics(positions)

        # Store for later retrieval
        self.portfolio_positions[f"{portfolio_id}_{reporting_date}"] = portfolio_position

        return portfolio_position

    def _calculate_portfolio_risk_metrics(self, positions: List[PositionRecord]) -> Dict[str, Any]:
        """Calculate portfolio-level risk metrics"""
        if not positions:
            return {}

        # Calculate concentration metrics
        total_value = sum(pos.market_value for pos in positions)

        # Largest position
        if positions:
            largest_position = max(pos.market_value for pos in positions)
            concentration_ratio = (largest_position / total_value) * 100 if total_value > 0 else 0
        else:
            concentration_ratio = 0

        # Top 10 concentration
        sorted_positions = sorted(positions, key=lambda p: p.market_value, reverse=True)
        top_10_value = sum(pos.market_value for pos in sorted_positions[:10])
        top_10_ratio = (top_10_value / total_value) * 100 if total_value > 0 else 0

        # Asset class diversification
        asset_classes = {}
        for pos in positions:
            asset_class = pos.asset_class.value
            if asset_class not in asset_classes:
                asset_classes[asset_class] = 0
            asset_classes[asset_class] += pos.market_value

        diversification_score = len(asset_classes)  # Simple count-based score

        # Position volatility (simplified - would need historical data)
        position_volatility = np.std([pos.market_value for pos in positions]) if len(positions) > 1 else 0

        return {
            'concentration_ratio': concentration_ratio,
            'top_10_concentration': top_10_ratio,
            'asset_class_count': len(asset_classes),
            'diversification_score': diversification_score,
            'position_volatility': position_volatility,
            'total_positions': len(positions),
            'long_positions': len([p for p in positions if p.position_type == PositionType.LONG]),
            'short_positions': len([p for p in positions if p.position_type == PositionType.SHORT])
        }

    def reconcile_positions(self,
                           portfolio_id: str,
                           source_positions: List[Dict[str, Any]],
                           target_positions: List[Dict[str, Any]],
                           reconciliation_date: date) -> str:
        """Reconcile positions between systems"""
        reconciliation = PositionReconciliation(
            portfolio_id=portfolio_id,
            reconciliation_date=reconciliation_date,
            source_system="trading_system",
            target_system="risk_system",
            total_positions=max(len(source_positions), len(target_positions)),
            matched_positions=0,
            unmatched_positions=0
        )

        # Convert to position records for matching
        source_pos_dict = {pos['instrument_id']: pos for pos in source_positions}
        target_pos_dict = {pos['instrument_id']: pos for pos in target_positions}

        matched = 0
        discrepancies = []

        # Check all instruments
        all_instruments = set(source_pos_dict.keys()) | set(target_pos_dict.keys())

        for instrument_id in all_instruments:
            source_pos = source_pos_dict.get(instrument_id)
            target_pos = target_pos_dict.get(instrument_id)

            if source_pos and target_pos:
                # Both systems have position - check for matches
                quantity_match = abs(source_pos['quantity'] - target_pos['quantity']) < 0.01
                value_match = abs(source_pos['market_value'] - target_pos['market_value']) < 1.0

                if quantity_match and value_match:
                    matched += 1
                else:
                    discrepancies.append({
                        'instrument_id': instrument_id,
                        'type': 'quantity_value_mismatch',
                        'source_quantity': source_pos['quantity'],
                        'target_quantity': target_pos['quantity'],
                        'source_value': source_pos['market_value'],
                        'target_value': target_pos['market_value']
                    })
            elif source_pos and not target_pos:
                # Only in source system
                discrepancies.append({
                    'instrument_id': instrument_id,
                    'type': 'missing_in_target',
                    'source_quantity': source_pos['quantity'],
                    'source_value': source_pos['market_value']
                })
            elif not source_pos and target_pos:
                # Only in target system
                discrepancies.append({
                    'instrument_id': instrument_id,
                    'type': 'missing_in_source',
                    'target_quantity': target_pos['quantity'],
                    'target_value': target_pos['market_value']
                })

        reconciliation.matched_positions = matched
        reconciliation.unmatched_positions = len(discrepancies)
        reconciliation.discrepancies = discrepancies
        reconciliation.reconciliation_status = "completed" if len(discrepancies) == 0 else "discrepancies_found"

        # Generate reconciliation report
        reconciliation.reconciliation_report = {
            'match_percentage': (matched / len(all_instruments)) * 100 if all_instruments else 100,
            'total_discrepancies': len(discrepancies),
            'discrepancy_types': self._categorize_discrepancies(discrepancies),
            'reconciliation_summary': f"{matched} positions matched, {len(discrepancies)} discrepancies found"
        }

        self.reconciliations[reconciliation.reconciliation_id] = reconciliation
        
        return reconciliation.reconciliation_id
    
    def get_reconciliation_status(self, reconciliation_id: str) -> Optional[PositionReconciliation]:
        """Get reconciliation status by ID"""
        return self.reconciliations.get(reconciliation_id)

    def _categorize_discrepancies(self, discrepancies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize discrepancies by type"""
        categories = {}
        for disc in discrepancies:
            disc_type = disc['type']
            categories[disc_type] = categories.get(disc_type, 0) + 1
        return categories

    def generate_position_report(self,
                               portfolio_id: str,
                               reporting_date: date,
                               report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate position report"""
        portfolio_position = self.get_portfolio_positions(portfolio_id, reporting_date)

        report = {
            'portfolio_id': portfolio_id,
            'reporting_date': reporting_date.isoformat(),
            'report_type': report_type,
            'summary': {
                'total_value': portfolio_position.total_value,
                'total_pnl': portfolio_position.total_pnl,
                'total_positions': len(portfolio_position.positions),
                'asset_classes': len(portfolio_position.asset_allocation),
                'pnl_percentage': (portfolio_position.total_pnl / portfolio_position.total_value) * 100 if portfolio_position.total_value > 0 else 0
            },
            'allocations': {
                'asset_allocation': portfolio_position.asset_allocation,
                'sector_allocation': portfolio_position.sector_allocation
            },
            'risk_metrics': portfolio_position.risk_metrics,
            'positions': []
        }

        # Add position details
        for position in portfolio_position.positions:
            position_detail = {
                'position_id': position.position_id,
                'instrument_id': position.instrument_id,
                'instrument_name': position.instrument_name,
                'asset_class': position.asset_class.value,
                'position_type': position.position_type.value,
                'quantity': position.quantity,
                'average_cost': position.average_cost,
                'market_price': position.market_price,
                'market_value': position.market_value,
                'unrealized_pnl': position.unrealized_pnl,
                'currency': position.currency,
                'pnl_percentage': (position.unrealized_pnl / position.market_value) * 100 if position.market_value > 0 else 0
            }
            report['positions'].append(position_detail)

        # Sort positions by market value
        report['positions'].sort(key=lambda p: p['market_value'], reverse=True)

        return report

    def generate_regulatory_position_report(self,
                                          portfolio_id: str,
                                          reporting_date: date,
                                          regulatory_framework: str = "SEC") -> Dict[str, Any]:
        """Generate regulatory position report"""
        portfolio_position = self.get_portfolio_positions(portfolio_id, reporting_date)

        if regulatory_framework == "SEC":
            return self._generate_sec_position_report(portfolio_position)
        elif regulatory_framework == "FINRA":
            return self._generate_finra_position_report(portfolio_position)
        elif regulatory_framework == "FCA":
            return self._generate_fca_position_report(portfolio_position)
        else:
            return self.generate_position_report(portfolio_id, reporting_date)

    def _generate_sec_position_report(self, portfolio_position: PortfolioPosition) -> Dict[str, Any]:
        """Generate SEC Form 13F-style position report"""
        # Filter for reportable securities (typically >$200M AUM requirement)
        reportable_positions = [
            pos for pos in portfolio_position.positions
            if pos.asset_class in [AssetClass.EQUITY, AssetClass.FIXED_INCOME]
        ]

        report = {
            'form_type': '13F',
            'reporting_date': portfolio_position.reporting_date.isoformat(),
            'portfolio_value': portfolio_position.total_value,
            'positions': []
        }

        for position in reportable_positions:
            position_data = {
                'name_of_issuer': position.instrument_name,
                'title_of_class': position.metadata.get('class_title', 'Common Stock'),
                'cusip': position.instrument_id,  # Simplified
                'value': position.market_value,
                'shares_or_principal_amount': position.quantity,
                'shares_or_principal_amount_type': 'SH' if position.asset_class == AssetClass.EQUITY else 'PRN',
                'put_or_call': position.metadata.get('put_call', ''),
                'investment_discretion': 'SOLE',
                'other_manager': '',
                'voting_authority': {
                    'sole': position.quantity,
                    'shared': 0,
                    'none': 0
                }
            }
            report['positions'].append(position_data)

        return report

    def _generate_finra_position_report(self, portfolio_position: PortfolioPosition) -> Dict[str, Any]:
        """Generate FINRA position report"""
        # FINRA position reporting requirements
        return {
            'reporting_entity': self.firm_id,
            'reporting_date': portfolio_position.reporting_date.isoformat(),
            'positions': [
                {
                    'instrument_id': pos.instrument_id,
                    'position_type': pos.position_type.value,
                    'quantity': pos.quantity,
                    'market_value': pos.market_value,
                    'unrealized_pnl': pos.unrealized_pnl
                }
                for pos in portfolio_position.positions
            ]
        }

    def _generate_fca_position_report(self, portfolio_position: PortfolioPosition) -> Dict[str, Any]:
        """Generate FCA position report"""
        # FCA position reporting requirements
        return {
            'reporting_entity': self.firm_id,
            'reporting_date': portfolio_position.reporting_date.isoformat(),
            'positions': [
                {
                    'instrument_identifier': pos.instrument_id,
                    'position_type': pos.position_type.value,
                    'quantity': pos.quantity,
                    'market_value': pos.market_value,
                    'currency': pos.currency
                }
                for pos in portfolio_position.positions
            ]
        }

    def get_position_limits(self, portfolio_id: str) -> Dict[str, Any]:
        """Get position limits for portfolio"""
        # Simplified position limits - would be configurable
        return {
            'max_single_position': 0.10,  # 10% of portfolio
            'max_sector_exposure': 0.25,  # 25% sector exposure
            'max_asset_class': 0.50,      # 50% asset class
            'min_diversification': 10,    # Minimum 10 positions
            'max_concentration': 0.05     # Max 5% concentration warning
        }

    def check_position_limits(self, portfolio_id: str, reporting_date: Optional[date] = None) -> Dict[str, Any]:
        """Check if portfolio positions exceed limits"""
        portfolio_position = self.get_portfolio_positions(portfolio_id, reporting_date)
        limits = self.get_position_limits(portfolio_id)

        violations = []

        # Check concentration limits
        if portfolio_position.risk_metrics.get('concentration_ratio', 0) > limits['max_single_position'] * 100:
            violations.append({
                'type': 'concentration_limit',
                'description': f"Single position exceeds {limits['max_single_position']*100:.1f}% limit",
                'current_value': portfolio_position.risk_metrics['concentration_ratio'],
                'limit_value': limits['max_single_position'] * 100
            })

        # Check diversification
        if portfolio_position.risk_metrics.get('total_positions', 0) < limits['min_diversification']:
            violations.append({
                'type': 'diversification_minimum',
                'description': f"Portfolio has fewer than {limits['min_diversification']} positions",
                'current_value': portfolio_position.risk_metrics['total_positions'],
                'limit_value': limits['min_diversification']
            })

        # Check sector concentrations
        for sector, allocation in portfolio_position.sector_allocation.items():
            if allocation > limits['max_sector_exposure'] * 100:
                violations.append({
                    'type': 'sector_concentration',
                    'description': f"Sector {sector} exceeds {limits['max_sector_exposure']*100:.1f}% limit",
                    'current_value': allocation,
                    'limit_value': limits['max_sector_exposure'] * 100
                })

        return {
            'portfolio_id': portfolio_id,
            'reporting_date': portfolio_position.reporting_date.isoformat(),
            'limits_checked': len(limits),
            'violations_found': len(violations),
            'violations': violations,
            'compliance_status': 'compliant' if len(violations) == 0 else 'non_compliant'
        }

    def export_positions(self, portfolio_id: str, format: str = 'json') -> str:
        """Export positions in specified format"""
        portfolio_position = self.get_portfolio_positions(portfolio_id)

        data = {
            'portfolio_id': portfolio_id,
            'reporting_date': portfolio_position.reporting_date.isoformat(),
            'total_value': portfolio_position.total_value,
            'positions': [
                {
                    'instrument_id': pos.instrument_id,
                    'instrument_name': pos.instrument_name,
                    'quantity': pos.quantity,
                    'market_price': pos.market_price,
                    'market_value': pos.market_value,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'asset_class': pos.asset_class.value,
                    'position_type': pos.position_type.value
                }
                for pos in portfolio_position.positions
            ]
        }

        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            df = pd.DataFrame(data['positions'])
            return df.to_csv(index=False)
        else:
            return json.dumps(data)


# Specialized Position Reporters
class PortfolioPositionReporter:
    """Portfolio-level position reporting"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def generate_portfolio_summary(self, portfolio_id: str, reporting_date: date) -> Dict[str, Any]:
        """Generate portfolio position summary"""
        portfolio_position = self.engine.get_portfolio_positions(portfolio_id, reporting_date)

        return {
            'portfolio_id': portfolio_id,
            'reporting_date': reporting_date.isoformat(),
            'total_value': portfolio_position.total_value,
            'total_pnl': portfolio_position.total_pnl,
            'asset_allocation': portfolio_position.asset_allocation,
            'sector_allocation': portfolio_position.sector_allocation,
            'risk_metrics': portfolio_position.risk_metrics,
            'position_count': len(portfolio_position.positions),
            'pnl_percentage': (portfolio_position.total_pnl / portfolio_position.total_value) * 100 if portfolio_position.total_value > 0 else 0
        }


class SecurityPositionReporter:
    """Security-level position reporting"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def generate_security_report(self, instrument_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate security position history report"""
        positions = [
            pos for pos in self.engine.positions.values()
            if pos.instrument_id == instrument_id and start_date <= pos.reporting_date <= end_date
        ]

        if not positions:
            return {'instrument_id': instrument_id, 'message': 'No positions found'}

        # Sort by date
        positions.sort(key=lambda p: p.reporting_date)

        return {
            'instrument_id': instrument_id,
            'instrument_name': positions[0].instrument_name if positions else '',
            'reporting_period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'position_history': [
                {
                    'date': pos.reporting_date.isoformat(),
                    'quantity': pos.quantity,
                    'market_price': pos.market_price,
                    'market_value': pos.market_value,
                    'unrealized_pnl': pos.unrealized_pnl
                }
                for pos in positions
            ],
            'summary': {
                'total_positions': len(positions),
                'avg_quantity': np.mean([p.quantity for p in positions]),
                'avg_price': np.mean([p.market_price for p in positions]),
                'price_volatility': np.std([p.market_price for p in positions]) if len(positions) > 1 else 0,
                'total_pnl': sum(p.unrealized_pnl for p in positions)
            }
        }


class DerivativePositionReporter:
    """Derivative position reporting"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def generate_derivative_exposure_report(self, portfolio_id: str, reporting_date: date) -> Dict[str, Any]:
        """Generate derivative exposure report"""
        portfolio_position = self.engine.get_portfolio_positions(portfolio_id, reporting_date)

        derivative_positions = [
            pos for pos in portfolio_position.positions
            if pos.asset_class == AssetClass.DERIVATIVES
        ]

        total_derivative_exposure = sum(abs(pos.market_value) for pos in derivative_positions)

        # Group by type
        by_type = {}
        for pos in derivative_positions:
            pos_type = pos.position_type.value
            if pos_type not in by_type:
                by_type[pos_type] = {'count': 0, 'exposure': 0.0}
            by_type[pos_type]['count'] += 1
            by_type[pos_type]['exposure'] += abs(pos.market_value)

        return {
            'portfolio_id': portfolio_id,
            'reporting_date': reporting_date.isoformat(),
            'total_derivative_positions': len(derivative_positions),
            'total_derivative_exposure': total_derivative_exposure,
            'derivative_types': by_type,
            'positions': [
                {
                    'instrument_id': pos.instrument_id,
                    'instrument_name': pos.instrument_name,
                    'position_type': pos.position_type.value,
                    'quantity': pos.quantity,
                    'market_value': pos.market_value,
                    'underlying_asset': pos.underlying_asset,
                    'maturity_date': pos.maturity_date.isoformat() if pos.maturity_date else None,
                    'strike_price': pos.strike_price
                }
                for pos in derivative_positions
            ]
        }


class FXPositionReporter:
    """FX position reporting"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def generate_fx_exposure_report(self, portfolio_id: str, reporting_date: date) -> Dict[str, Any]:
        """Generate FX exposure report"""
        portfolio_position = self.engine.get_portfolio_positions(portfolio_id, reporting_date)

        fx_positions = [
            pos for pos in portfolio_position.positions
            if pos.asset_class == AssetClass.FX
        ]

        # Group by currency
        currency_exposure = {}
        for pos in fx_positions:
            currency = pos.currency
            if currency not in currency_exposure:
                currency_exposure[currency] = {'long': 0.0, 'short': 0.0, 'net': 0.0}

            if pos.position_type == PositionType.LONG:
                currency_exposure[currency]['long'] += pos.market_value
            else:
                currency_exposure[currency]['short'] += pos.market_value

            currency_exposure[currency]['net'] = (
                currency_exposure[currency]['long'] - currency_exposure[currency]['short']
            )

        return {
            'portfolio_id': portfolio_id,
            'reporting_date': reporting_date.isoformat(),
            'total_fx_positions': len(fx_positions),
            'currency_exposure': currency_exposure,
            'net_fx_exposure': sum(abs(exp['net']) for exp in currency_exposure.values()),
            'fx_positions': [
                {
                    'instrument_id': pos.instrument_id,
                    'currency': pos.currency,
                    'position_type': pos.position_type.value,
                    'quantity': pos.quantity,
                    'market_value': pos.market_value,
                    'unrealized_pnl': pos.unrealized_pnl
                }
                for pos in fx_positions
            ]
        }


class PositionAggregationEngine:
    """Position aggregation and consolidation"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def aggregate_positions(self, portfolio_ids: List[str], reporting_date: date) -> PortfolioPosition:
        """Aggregate positions across multiple portfolios"""
        all_positions = []

        for portfolio_id in portfolio_ids:
            portfolio_position = self.engine.get_portfolio_positions(portfolio_id, reporting_date)
            all_positions.extend(portfolio_position.positions)

        # Group by instrument
        aggregated_positions = {}
        for pos in all_positions:
            key = pos.instrument_id
            if key not in aggregated_positions:
                aggregated_positions[key] = PositionRecord(
                    position_id=f"AGG_{key}",
                    portfolio_id="AGGREGATED",
                    instrument_id=pos.instrument_id,
                    instrument_name=pos.instrument_name,
                    asset_class=pos.asset_class,
                    position_type=pos.position_type,
                    quantity=0,
                    average_cost=0,
                    market_price=pos.market_price,
                    market_value=0,
                    unrealized_pnl=0,
                    currency=pos.currency,
                    reporting_date=reporting_date
                )

            # Aggregate quantities and values
            agg_pos = aggregated_positions[key]
            total_quantity = agg_pos.quantity + pos.quantity

            if total_quantity != 0:
                # Weighted average cost
                agg_pos.average_cost = (
                    (agg_pos.average_cost * agg_pos.quantity) + (pos.average_cost * pos.quantity)
                ) / total_quantity

            agg_pos.quantity = total_quantity
            agg_pos.market_value = agg_pos.quantity * agg_pos.market_price
            agg_pos.unrealized_pnl = (agg_pos.market_price - agg_pos.average_cost) * agg_pos.quantity

        positions = list(aggregated_positions.values())

        # Create aggregated portfolio position
        total_value = sum(pos.market_value for pos in positions)
        total_pnl = sum(pos.unrealized_pnl for pos in positions)

        aggregated_portfolio = PortfolioPosition(
            portfolio_id="AGGREGATED",
            reporting_date=reporting_date,
            total_value=total_value,
            total_pnl=total_pnl,
            positions=positions
        )

        aggregated_portfolio.calculate_allocations()
        aggregated_portfolio.risk_metrics = self.engine._calculate_portfolio_risk_metrics(positions)

        return aggregated_portfolio


class PositionReconciliation:
    """Position reconciliation component"""

    def __init__(self, engine: PositionReportingEngine):
        self.engine = engine

    def get_reconciliation_status(self, reconciliation_id: str) -> Optional[PositionReconciliation]:
        """Get reconciliation by ID"""
        return self.engine.reconciliations.get(reconciliation_id)

    def generate_reconciliation_report(self, reconciliation_id: str) -> Dict[str, Any]:
        """Generate detailed reconciliation report"""
        reconciliation = self.get_reconciliation_status(reconciliation_id)
        if not reconciliation:
            return {'error': f'Reconciliation {reconciliation_id} not found'}

        return {
            'reconciliation_id': reconciliation.reconciliation_id,
            'portfolio_id': reconciliation.portfolio_id,
            'reconciliation_date': reconciliation.reconciliation_date.isoformat(),
            'source_system': reconciliation.source_system,
            'target_system': reconciliation.target_system,
            'summary': {
                'total_positions': reconciliation.total_positions,
                'matched_positions': reconciliation.matched_positions,
                'unmatched_positions': reconciliation.unmatched_positions,
                'match_percentage': (reconciliation.matched_positions / reconciliation.total_positions) * 100 if reconciliation.total_positions > 0 else 100,
                'status': reconciliation.reconciliation_status
            },
            'discrepancies': reconciliation.discrepancies,
            'reconciliation_report': reconciliation.reconciliation_report
        }


# Factory functions
def create_position_reporter(firm_id: str) -> PositionReportingEngine:
    """Create position reporting engine"""
    return PositionReportingEngine(firm_id)

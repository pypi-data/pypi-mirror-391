"""
Regulatory Reporting Engine
===========================

Comprehensive regulatory reporting system for SEC, FINRA, FCA, MAS, ASIC compliance.
Handles automated filing of Form 13F, 13D/G, 13H, transaction reports, and regulatory disclosures.

Key Features:
- SEC Form 13F (Institutional Holdings)
- SEC Form 13D/G (Beneficial Ownership)
- SEC Form 13H (Large Trader Registration)
- FINRA Regulatory Reporting
- FCA/MiFID II Transaction Reporting
- MAS Regulatory Compliance
- ASIC Derivative Reporting
- Automated Filing Systems
- Regulatory Communication Protocols
- Filing Status Tracking
- Regulatory Deadline Management
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import hashlib
import hmac
import requests
from urllib.parse import urljoin

import numpy as np
import pandas as pd

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    Fernet = None

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    jwt = None


class RegulatoryAuthority(Enum):
    """Supported regulatory authorities"""
    SEC = "sec"
    FINRA = "finra"
    FCA = "fca"
    MAS = "mas"
    ASIC = "asic"
    CFTC = "cftc"
    FCA_MIFID = "fca_mifid"


class FilingStatus(Enum):
    """Filing status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDED = "amended"


class FilingPriority(Enum):
    """Filing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FilingRecord:
    """Regulatory filing record"""
    filing_id: str
    authority: RegulatoryAuthority
    form_type: str
    period_end_date: date
    submission_date: Optional[datetime] = None
    status: FilingStatus = FilingStatus.DRAFT
    priority: FilingPriority = FilingPriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    amendments: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.filing_id:
            self.filing_id = self._generate_filing_id()

    def _generate_filing_id(self) -> str:
        """Generate unique filing ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.md5(str(self.content).encode()).hexdigest()[:8]
        return f"{self.authority.value}_{self.form_type}_{timestamp}_{content_hash}"


@dataclass
class ComplianceDeadline:
    """Regulatory deadline tracking"""
    authority: RegulatoryAuthority
    form_type: str
    deadline_type: str
    due_date: date
    grace_period_days: int = 0
    is_hard_deadline: bool = True
    notification_sent: bool = False


class RegulatoryReportingEngine:
    """Main regulatory reporting engine"""

    def __init__(self,
                 firm_id: str,
                 encryption_key: Optional[str] = None,
                 api_credentials: Optional[Dict[str, Dict[str, str]]] = None):
        self.firm_id = firm_id
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.api_credentials = api_credentials or {}
        self.filings: Dict[str, FilingRecord] = {}
        self.deadlines: List[ComplianceDeadline] = []
        self.filing_history: List[FilingRecord] = []

        # Initialize reporters
        self.sec_reporter = SECReporting(self)
        self.finra_reporter = FINRAReporting(self)
        self.fca_reporter = FCAReporting(self)
        self.mas_reporter = MASReporting(self)
        self.asic_reporter = ASICReporting(self)

        self._initialize_deadlines()
        self._load_filing_history()

    def _initialize_deadlines(self):
        """Initialize regulatory deadlines"""
        current_year = datetime.now().year

        # SEC Form 13F - Quarterly, due within 45 days
        quarter_end_dates = {
            3: date(current_year, 3, 31),
            6: date(current_year, 6, 30),
            9: date(current_year, 9, 30),
            12: date(current_year, 12, 31)
        }

        for quarter, end_date in quarter_end_dates.items():
            due_date = end_date + timedelta(days=45)
            self.deadlines.append(ComplianceDeadline(
                RegulatoryAuthority.SEC, "13F", "quarterly",
                due_date, grace_period_days=5
            ))

        # SEC Form 13H - Annual, due by February 28
        self.deadlines.append(ComplianceDeadline(
            RegulatoryAuthority.SEC, "13H", "annual",
            date(current_year + 1, 2, 28)
        ))

    def _load_filing_history(self):
        """Load filing history from storage"""
        # Implementation would load from database/blockchain
        pass

    def create_filing(self,
                     authority: RegulatoryAuthority,
                     form_type: str,
                     period_end_date: date,
                     content: Dict[str, Any],
                     priority: FilingPriority = FilingPriority.NORMAL) -> str:
        """Create a new regulatory filing"""

        filing = FilingRecord(
            filing_id="",  # Will be generated
            authority=authority,
            form_type=form_type,
            period_end_date=period_end_date,
            content=content,
            priority=priority
        )

        self.filings[filing.filing_id] = filing
        return filing.filing_id

    def validate_filing(self, filing_id: str) -> bool:
        """Validate a filing for compliance"""
        if filing_id not in self.filings:
            raise ValueError(f"Filing {filing_id} not found")

        filing = self.filings[filing_id]
        validator = self._get_validator(filing.authority, filing.form_type)

        if validator:
            is_valid, errors = validator.validate(filing.content)
            filing.validation_errors = errors
            return is_valid

        return True

    def _get_validator(self, authority: RegulatoryAuthority, form_type: str):
        """Get appropriate validator for authority and form type"""
        if authority == RegulatoryAuthority.SEC:
            if form_type == "13F":
                return SECForm13FValidator()
            elif form_type == "13H":
                return SECForm13HValidator()
        elif authority == RegulatoryAuthority.FINRA:
            return FINRAValidator()

        return None

    def submit_filing(self, filing_id: str) -> bool:
        """Submit filing to regulatory authority"""
        if filing_id not in self.filings:
            raise ValueError(f"Filing {filing_id} not found")

        filing = self.filings[filing_id]

        # Validate before submission
        if not self.validate_filing(filing_id):
            raise ValueError(f"Filing {filing_id} validation failed: {filing.validation_errors}")

        # Get appropriate submitter
        submitter = self._get_submitter(filing.authority)

        if submitter:
            success, response = submitter.submit(filing)
            if success:
                filing.status = FilingStatus.SUBMITTED
                filing.submission_date = datetime.now()
                self.filing_history.append(filing)
                return True
            else:
                filing.status = FilingStatus.REJECTED
                filing.metadata['submission_error'] = response
                return False

        return False

    def _get_submitter(self, authority: RegulatoryAuthority):
        """Get appropriate submitter for authority"""
        if authority == RegulatoryAuthority.SEC:
            return SECSubmitter(self.api_credentials.get('sec', {}))
        elif authority == RegulatoryAuthority.FINRA:
            return FINRASubmitter(self.api_credentials.get('finra', {}))
        elif authority == RegulatoryAuthority.FCA:
            return FCASubmitter(self.api_credentials.get('fca', {}))

        return None

    def get_filing_status(self, filing_id: str) -> Optional[FilingStatus]:
        """Get filing status"""
        filing = self.filings.get(filing_id)
        return filing.status if filing else None

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[ComplianceDeadline]:
        """Get upcoming regulatory deadlines"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        return [d for d in self.deadlines if d.due_date <= cutoff_date]

    def generate_compliance_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        # Include both submitted filings and current filings
        all_filings = list(self.filing_history) + [f for f in self.filings.values() if f.status == FilingStatus.SUBMITTED]
        
        filings_in_period = [
            f for f in all_filings
            if f.submission_date and start_date <= f.submission_date.date() <= end_date
        ]
        
        # Also include filings by period_end_date if submission_date not available
        if len(filings_in_period) == 0:
            filings_in_period = [
                f for f in self.filings.values()
                if f.period_end_date and start_date <= f.period_end_date <= end_date
            ]

        report = {
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_filings': len(filings_in_period),
                'by_authority': {},
                'by_status': {},
                'on_time_filings': 0,
                'late_filings': 0
            },
            'filings': [],
            'compliance_score': 0.0,
            'recommendations': []
        }

        # Analyze filings
        for filing in filings_in_period:
            report['filings'].append({
                'id': filing.filing_id,
                'authority': filing.authority.value,
                'form_type': filing.form_type,
                'status': filing.status.value,
                'submission_date': filing.submission_date.isoformat() if filing.submission_date else None
            })

            # Update summary statistics
            auth = filing.authority.value
            status = filing.status.value

            if auth not in report['summary']['by_authority']:
                report['summary']['by_authority'][auth] = 0
            report['summary']['by_authority'][auth] += 1

            if status not in report['summary']['by_status']:
                report['summary']['by_status'][status] = 0
            report['summary']['by_status'][status] += 1

        # Calculate compliance score
        total_filings = report['summary']['total_filings']
        if total_filings > 0:
            on_time_ratio = report['summary']['on_time_filings'] / total_filings
            acceptance_ratio = report['summary']['by_status'].get('accepted', 0) / total_filings
            report['compliance_score'] = (on_time_ratio + acceptance_ratio) / 2

        return report


class SECReporting:
    """SEC regulatory reporting"""

    def __init__(self, engine: RegulatoryReportingEngine):
        self.engine = engine

    def create_form_13f(self,
                       holdings: List[Dict[str, Any]],
                       period_end: date,
                       filer_info: Dict[str, Any]) -> str:
        """Create SEC Form 13F filing"""

        content = {
            'filer_info': filer_info,
            'report_calendar_or_quarter': period_end.strftime("%m-%d-%Y"),
            'holdings': holdings,
            'summary': self._calculate_13f_summary(holdings)
        }

        return self.engine.create_filing(
            RegulatoryAuthority.SEC,
            "13F",
            period_end,
            content
        )

    def _calculate_13f_summary(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate Form 13F summary statistics"""
        total_value = sum(h.get('market_value', 0) for h in holdings)
        total_shares = sum(h.get('shares_or_principal_amount', 0) for h in holdings)

        return {
            'total_number_of_holders': len(holdings),
            'total_value': total_value,
            'total_shares': total_shares,
            'other_included_managers_count': 0  # For institutional investment managers
        }

    def create_form_13h(self,
                       large_trader_info: Dict[str, Any],
                       trading_activity: List[Dict[str, Any]],
                       period_end: date) -> str:
        """Create SEC Form 13H filing"""

        content = {
            'large_trader_info': large_trader_info,
            'reporting_period': {
                'start': (period_end - timedelta(days=364)).strftime("%m-%d-%Y"),
                'end': period_end.strftime("%m-%d-%Y")
            },
            'trading_activity': trading_activity,
            'identification': self._generate_identification_info(large_trader_info)
        }

        return self.engine.create_filing(
            RegulatoryAuthority.SEC,
            "13H",
            period_end,
            content
        )

    def _generate_identification_info(self, trader_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Form 13H identification information"""
        return {
            'name': trader_info.get('name', ''),
            'address': trader_info.get('address', {}),
            'tax_id': trader_info.get('tax_id', ''),
            'lei': trader_info.get('lei', ''),
            'contact_info': trader_info.get('contact', {})
        }


class FINRAReporting:
    """FINRA regulatory reporting"""

    def __init__(self, engine: RegulatoryReportingEngine):
        self.engine = engine

    def create_trade_reporting(self,
                              trades: List[Dict[str, Any]],
                              reporting_period: date) -> str:
        """Create FINRA trade reporting filing"""

        # Process trades for FINRA reporting requirements
        processed_trades = []
        for trade in trades:
            processed_trade = {
                'trade_id': trade.get('id'),
                'symbol': trade.get('symbol'),
                'quantity': trade.get('quantity'),
                'price': trade.get('price'),
                'trade_date': trade.get('date'),
                'buyer_id': trade.get('buyer_id'),
                'seller_id': trade.get('seller_id'),
                'market_center': trade.get('market_center', 'NSDQ'),
                'reporting_party': 'firm_id_here'
            }
            processed_trades.append(processed_trade)

        content = {
            'reporting_period': reporting_period.strftime("%Y-%m-%d"),
            'trades': processed_trades,
            'summary': {
                'total_trades': len(processed_trades),
                'total_volume': sum(t['quantity'] for t in processed_trades),
                'total_value': sum(t['quantity'] * t['price'] for t in processed_trades)
            }
        }

        return self.engine.create_filing(
            RegulatoryAuthority.FINRA,
            "TRADE_REPORT",
            reporting_period,
            content
        )


class FCAReporting:
    """FCA/MiFID II regulatory reporting"""

    def __init__(self, engine: RegulatoryReportingEngine):
        self.engine = engine

    def create_mifid_transaction_report(self,
                                       transactions: List[Dict[str, Any]],
                                       reporting_date: date) -> str:
        """Create MiFID II transaction reporting"""

        processed_transactions = []
        for tx in transactions:
            mifid_tx = {
                'transaction_id': tx.get('id'),
                'trading_date': tx.get('date').strftime("%Y-%m-%d") if tx.get('date') else None,
                'trading_time': tx.get('time'),
                'instrument_id': tx.get('instrument_id'),
                'instrument_name': tx.get('symbol'),
                'quantity': tx.get('quantity'),
                'price': tx.get('price'),
                'venue': tx.get('venue'),
                'buyer_id': tx.get('buyer_id'),
                'seller_id': tx.get('seller_id'),
                'investment_decision': tx.get('investment_decision'),
                'execution_decision': tx.get('execution_decision'),
                'client_type': tx.get('client_type', 'RETAIL'),
                'trading_capacity': tx.get('trading_capacity', 'DEAL')
            }
            processed_transactions.append(mifid_tx)

        content = {
            'reporting_date': reporting_date.strftime("%Y-%m-%d"),
            'reporting_entity': self.engine.firm_id,
            'transactions': processed_transactions,
            'validation': self._validate_mifid_fields(processed_transactions)
        }

        return self.engine.create_filing(
            RegulatoryAuthority.FCA,
            "MiFID_TRANSACTION",
            reporting_date,
            content
        )

    def _validate_mifid_fields(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate MiFID II required fields"""
        validation = {
            'total_transactions': len(transactions),
            'valid_transactions': 0,
            'invalid_transactions': 0,
            'errors': []
        }

        required_fields = [
            'transaction_id', 'trading_date', 'instrument_id',
            'quantity', 'price', 'venue', 'buyer_id', 'seller_id'
        ]

        for tx in transactions:
            missing_fields = [f for f in required_fields if not tx.get(f)]
            if missing_fields:
                validation['invalid_transactions'] += 1
                validation['errors'].append(f"Transaction {tx.get('transaction_id')}: missing {missing_fields}")
            else:
                validation['valid_transactions'] += 1

        return validation


class MASReporting:
    """MAS regulatory reporting (Singapore)"""

    def __init__(self, engine: RegulatoryReportingEngine):
        self.engine = engine

    def create_derivative_reporting(self,
                                   positions: List[Dict[str, Any]],
                                   reporting_date: date) -> str:
        """Create MAS derivative position reporting"""

        processed_positions = []
        for pos in positions:
            mas_pos = {
                'position_id': pos.get('id'),
                'instrument_type': pos.get('type'),
                'underlying_asset': pos.get('underlying'),
                'notional_amount': pos.get('notional'),
                'market_value': pos.get('market_value'),
                'position_type': pos.get('position_type'),  # Long/Short
                'counterparty': pos.get('counterparty'),
                'maturity_date': pos.get('maturity'),
                'reporting_entity': self.engine.firm_id
            }
            processed_positions.append(mas_pos)

        content = {
            'reporting_date': reporting_date.strftime("%Y-%m-%d"),
            'reporting_entity': self.engine.firm_id,
            'positions': processed_positions,
            'aggregates': self._calculate_mas_aggregates(processed_positions)
        }

        return self.engine.create_filing(
            RegulatoryAuthority.MAS,
            "DERIVATIVE_POSITION",
            reporting_date,
            content
        )

    def _calculate_mas_aggregates(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate MAS reporting aggregates"""
        total_notional = sum(p.get('notional_amount', 0) for p in positions)
        total_market_value = sum(p.get('market_value', 0) for p in positions)

        return {
            'total_positions': len(positions),
            'total_notional': total_notional,
            'total_market_value': total_market_value,
            'net_exposure': self._calculate_net_exposure(positions)
        }

    def _calculate_net_exposure(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate net exposure for MAS reporting"""
        long_exposure = sum(p.get('market_value', 0) for p in positions
                           if p.get('position_type') == 'LONG')
        short_exposure = sum(p.get('market_value', 0) for p in positions
                            if p.get('position_type') == 'SHORT')
        return long_exposure - short_exposure


class ASICReporting:
    """ASIC regulatory reporting (Australia)"""

    def __init__(self, engine: RegulatoryReportingEngine):
        self.engine = engine

    def create_otc_derivative_report(self,
                                    derivatives: List[Dict[str, Any]],
                                    reporting_date: date) -> str:
        """Create ASIC OTC derivative reporting"""

        processed_derivatives = []
        for deriv in derivatives:
            asic_deriv = {
                'trade_id': deriv.get('id'),
                'product_type': deriv.get('product_type'),
                'underlying_asset': deriv.get('underlying'),
                'notional_amount': deriv.get('notional'),
                'trade_date': deriv.get('trade_date'),
                'maturity_date': deriv.get('maturity'),
                'counterparty_a': deriv.get('counterparty_a'),
                'counterparty_b': deriv.get('counterparty_b'),
                'reporting_party': self.engine.firm_id
            }
            processed_derivatives.append(asic_deriv)

        content = {
            'reporting_date': reporting_date.strftime("%Y-%m-%d"),
            'reporting_entity': self.engine.firm_id,
            'derivatives': processed_derivatives,
            'summary': {
                'total_derivatives': len(processed_derivatives),
                'by_product_type': self._group_by_product_type(processed_derivatives),
                'total_notional': sum(d.get('notional_amount', 0) for d in processed_derivatives)
            }
        }

        return self.engine.create_filing(
            RegulatoryAuthority.ASIC,
            "OTC_DERIVATIVE",
            reporting_date,
            content
        )

    def _group_by_product_type(self, derivatives: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group derivatives by product type"""
        product_counts = {}
        for deriv in derivatives:
            product_type = deriv.get('product_type', 'UNKNOWN')
            product_counts[product_type] = product_counts.get(product_type, 0) + 1
        return product_counts


# Form-specific reporters
class Form13FReporter:
    """SEC Form 13F specific reporter"""

    def __init__(self, sec_reporter: SECReporting):
        self.sec_reporter = sec_reporter

    def generate_13f_xml(self, holdings: List[Dict[str, Any]], filer_info: Dict[str, Any]) -> str:
        """Generate Form 13F XML filing"""
        # Create XML structure for SEC Form 13F
        root = ET.Element("form13F")
        header = ET.SubElement(root, "headerData")

        # Filer information
        filer = ET.SubElement(header, "filerInfo")
        ET.SubElement(filer, "cik").text = filer_info.get('cik', '')
        ET.SubElement(filer, "name").text = filer_info.get('name', '')

        # Holdings
        info_table = ET.SubElement(root, "informationTable")
        for holding in holdings:
            info = ET.SubElement(info_table, "info")

            ET.SubElement(info, "nameOfIssuer").text = holding.get('issuer_name', '')
            ET.SubElement(info, "titleOfClass").text = holding.get('class_title', '')
            ET.SubElement(info, "cusip").text = holding.get('cusip', '')
            ET.SubElement(info, "value").text = str(holding.get('market_value', 0))
            ET.SubElement(info, "sshPrnamt").text = str(holding.get('shares', 0))
            ET.SubElement(info, "sshPrnamtType").text = holding.get('shares_type', 'SH')
            ET.SubElement(info, "putCall").text = holding.get('put_call', '')

        # Convert to string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


class Form13DGReporter:
    """SEC Form 13D/G specific reporter"""

    def __init__(self, sec_reporter: SECReporting):
        self.sec_reporter = sec_reporter

    def create_13d_filing(self,
                         issuer_info: Dict[str, Any],
                         beneficial_owner: Dict[str, Any],
                         ownership_info: Dict[str, Any],
                         purpose_statement: str) -> str:
        """Create SEC Form 13D filing"""

        content = {
            'form_type': '13D',
            'issuer_info': issuer_info,
            'beneficial_owner': beneficial_owner,
            'ownership_info': ownership_info,
            'purpose_statement': purpose_statement,
            'exhibits': []
        }

        # This would normally create the filing through the main engine
        return f"13D_{issuer_info.get('name', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}"

    def create_13g_filing(self,
                         issuer_info: Dict[str, Any],
                         beneficial_owner: Dict[str, Any],
                         ownership_info: Dict[str, Any]) -> str:
        """Create SEC Form 13G filing"""

        content = {
            'form_type': '13G',
            'issuer_info': issuer_info,
            'beneficial_owner': beneficial_owner,
            'ownership_info': ownership_info,
            'exemption_claimed': '7'  # Common exemption for institutional investors
        }

        return f"13G_{issuer_info.get('name', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}"


class Form13HReporter:
    """SEC Form 13H specific reporter"""

    def __init__(self, sec_reporter: SECReporting):
        self.sec_reporter = sec_reporter

    def create_large_trader_registration(self,
                                       trader_info: Dict[str, Any],
                                       trading_strategy: str,
                                       average_daily_volume: float) -> str:
        """Create Form 13H large trader registration"""

        content = {
            'trader_info': trader_info,
            'trading_strategy': trading_strategy,
            'average_daily_volume': average_daily_volume,
            'registration_type': 'INITIAL' if average_daily_volume >= 2000000 else 'UPDATE',
            'reporting_period_start': (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            'reporting_period_end': datetime.now().strftime("%Y-%m-%d")
        }

        return f"13H_{trader_info.get('name', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}"


# Validators
class SECForm13FValidator:
    """Validator for SEC Form 13F"""

    def validate(self, content: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate Form 13F content"""
        errors = []

        # Check required fields
        if 'filer_info' not in content:
            errors.append("Missing filer information")
        else:
            filer_info = content['filer_info']
            required_filer_fields = ['cik', 'name']
            for field in required_filer_fields:
                if field not in filer_info or not filer_info[field]:
                    errors.append(f"Missing required filer field: {field}")

        # Check holdings
        if 'holdings' not in content:
            errors.append("Missing holdings information")
        else:
            holdings = content['holdings']
            for i, holding in enumerate(holdings):
                # Check for shares or shares_or_principal_amount
                if 'shares' not in holding and 'shares_or_principal_amount' not in holding:
                    errors.append(f"Holding {i+1}: missing required field 'shares' or 'shares_or_principal_amount'")
                
                # Check other required fields
                required_fields = ['issuer_name', 'cusip', 'market_value']
                for field in required_fields:
                    if field not in holding or holding[field] is None:
                        errors.append(f"Holding {i+1}: missing required field {field}")

                # Validate market value
                if 'market_value' in holding:
                    try:
                        value = float(holding['market_value'])
                        if value < 0:
                            errors.append(f"Holding {i+1}: negative market value")
                    except (ValueError, TypeError):
                        errors.append(f"Holding {i+1}: invalid market value format")

        return len(errors) == 0, errors


class SECForm13HValidator:
    """Validator for SEC Form 13H"""

    def validate(self, content: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate Form 13H content"""
        errors = []

        # Check trader info
        if 'large_trader_info' not in content:
            errors.append("Missing large trader information")
        else:
            trader_info = content['large_trader_info']
            required_fields = ['name', 'tax_id', 'address']
            for field in required_fields:
                if field not in trader_info or not trader_info[field]:
                    errors.append(f"Missing required trader field: {field}")

        # Check trading activity
        if 'trading_activity' not in content:
            errors.append("Missing trading activity information")
        else:
            activity = content['trading_activity']
            if not isinstance(activity, list) or len(activity) == 0:
                errors.append("Trading activity must be non-empty list")

        return len(errors) == 0, errors


class FINRAValidator:
    """Validator for FINRA filings"""

    def validate(self, content: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate FINRA filing content"""
        errors = []

        # Check trades
        if 'trades' not in content:
            errors.append("Missing trades information")
        else:
            trades = content['trades']
            for i, trade in enumerate(trades):
                required_fields = ['trade_id', 'symbol', 'quantity', 'price', 'trade_date']
                for field in required_fields:
                    if field not in trade or trade[field] is None:
                        errors.append(f"Trade {i+1}: missing required field {field}")

                # Validate quantity and price
                try:
                    qty = float(trade.get('quantity', 0))
                    price = float(trade.get('price', 0))
                    if qty <= 0:
                        errors.append(f"Trade {i+1}: invalid quantity {qty}")
                    if price <= 0:
                        errors.append(f"Trade {i+1}: invalid price {price}")
                except (ValueError, TypeError):
                    errors.append(f"Trade {i+1}: invalid numeric fields")

        return len(errors) == 0, errors


# Submitters
class SECSubmitter:
    """SEC filing submitter"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.base_url = "https://www.sec.gov/cgi-bin/"
        self.api_key = credentials.get('api_key', '')
        self.cik = credentials.get('cik', '')

    def submit(self, filing: FilingRecord) -> tuple[bool, str]:
        """Submit filing to SEC"""
        try:
            # In real implementation, this would make actual API calls
            # For now, simulate submission

            if filing.form_type == "13F":
                return self._submit_13f(filing)
            elif filing.form_type == "13H":
                return self._submit_13h(filing)
            else:
                return False, "Unsupported form type"

        except Exception as e:
            return False, f"Submission failed: {str(e)}"

    def _submit_13f(self, filing: FilingRecord) -> tuple[bool, str]:
        """Submit Form 13F"""
        # Simulate SEC EDGAR filing
        return True, f"Form 13F accepted with accession number {filing.filing_id}"

    def _submit_13h(self, filing: FilingRecord) -> tuple[bool, str]:
        """Submit Form 13H"""
        # Simulate SEC filing
        return True, f"Form 13H accepted with confirmation number {filing.filing_id}"


class FINRASubmitter:
    """FINRA filing submitter"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.base_url = "https://www.finra.org/"
        self.api_key = credentials.get('api_key', '')

    def submit(self, filing: FilingRecord) -> tuple[bool, str]:
        """Submit filing to FINRA"""
        try:
            # Simulate FINRA submission
            return True, f"FINRA filing {filing.filing_id} accepted"

        except Exception as e:
            return False, f"FINRA submission failed: {str(e)}"


class FCASubmitter:
    """FCA filing submitter"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.base_url = "https://www.fca.org.uk/"
        self.api_key = credentials.get('api_key', '')

    def submit(self, filing: FilingRecord) -> tuple[bool, str]:
        """Submit filing to FCA"""
        try:
            # Simulate FCA submission
            return True, f"FCA MiFID filing {filing.filing_id} accepted"

        except Exception as e:
            return False, f"FCA submission failed: {str(e)}"


# Factory functions
def create_regulatory_reporter(firm_id: str,
                              api_credentials: Optional[Dict[str, Dict[str, str]]] = None) -> RegulatoryReportingEngine:
    """Create regulatory reporting engine"""
    return RegulatoryReportingEngine(firm_id, api_credentials=api_credentials)


def generate_compliance_report(engine: RegulatoryReportingEngine,
                              start_date: date,
                              end_date: date) -> Dict[str, Any]:
    """Generate compliance report"""
    return engine.generate_compliance_report(start_date, end_date)

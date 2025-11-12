"""
KYC/AML System
==============

Know Your Customer and Anti-Money Laundering compliance system.
Provides comprehensive customer due diligence, transaction monitoring,
sanctions screening, and regulatory reporting capabilities.

Key Features:
- Customer Due Diligence (CDD)
- Enhanced Due Diligence (EDD)
- Sanctions and PEP screening
- Transaction monitoring and alerts
- Risk scoring and profiling
- Regulatory reporting and filings
- Watchlist management
- Adverse media screening
- Source of wealth verification
- Politically Exposed Persons (PEP) checks
- Automated compliance workflows
- Audit trail and documentation
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum
import json
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy.process import extractOne


class KYCStatus(Enum):
    """KYC verification status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class RiskLevel(Enum):
    """Customer risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AMLAlertType(Enum):
    """AML alert types"""
    SANCTIONS_MATCH = "sanctions_match"
    PEP_ASSOCIATION = "pep_association"
    UNUSUAL_TRANSACTION = "unusual_transaction"
    STRUCTURING = "structuring"
    SMURFING = "smurfing"
    ROUND_DOLLAR = "round_dollar"
    RAPID_MOVEMENT = "rapid_movement"
    HIGH_RISK_JURISDICTION = "high_risk_jurisdiction"


class VerificationType(Enum):
    """Document verification types"""
    IDENTITY = "identity"
    ADDRESS = "address"
    SOURCE_OF_WEALTH = "source_of_wealth"
    SOURCE_OF_FUNDS = "source_of_funds"
    TAX_ID = "tax_id"
    BUSINESS_LICENSE = "business_license"


@dataclass
class CustomerProfile:
    """Customer profile data structure"""
    customer_id: str
    customer_type: str  # Individual, Business, Trust, etc.
    full_name: str
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    residence_country: Optional[str] = None
    address: Dict[str, Any] = field(default_factory=dict)
    contact_info: Dict[str, Any] = field(default_factory=dict)
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[float] = None
    source_of_wealth: Optional[str] = None
    politically_exposed: bool = False
    pep_details: Dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    kyc_status: KYCStatus = KYCStatus.PENDING
    kyc_completion_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    documents: List[Dict[str, Any]] = field(default_factory=list)
    watchlist_flags: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.customer_id:
            self.customer_id = f"CUST_{hashlib.md5(self.full_name.encode()).hexdigest()[:8].upper()}"


@dataclass
class TransactionRecord:
    """Transaction record for AML monitoring"""
    transaction_id: str
    customer_id: str
    transaction_date: datetime
    transaction_type: str
    amount: float
    currency: str
    counterparty: Optional[str] = None
    counterparty_country: Optional[str] = None
    payment_method: Optional[str] = None
    transaction_purpose: Optional[str] = None
    suspicious_flags: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    reviewed: bool = False
    review_date: Optional[datetime] = None
    review_notes: Optional[str] = None


@dataclass
class AMLAlert:
    """AML alert record"""
    alert_id: str
    customer_id: str
    alert_type: AMLAlertType
    severity: str
    description: str
    transaction_ids: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    status: str = "open"  # open, investigating, closed, false_positive
    assigned_to: Optional[str] = None
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"AML_{self.alert_type.value}_{int(self.created_date.timestamp())}"


@dataclass
class SanctionsEntry:
    """Sanctions list entry"""
    entity_id: str
    entity_name: str
    entity_type: str  # Individual, Entity, Vessel, Aircraft
    aliases: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    sanctions_program: str = ""
    sanctions_type: str = ""
    listing_date: Optional[date] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None


class KYCAMLSystem:
    """Main KYC/AML compliance system"""

    def __init__(self,
                 sanctions_lists: Optional[List[str]] = None,
                 watchlist_providers: Optional[List[str]] = None,
                 risk_thresholds: Optional[Dict[str, float]] = None):
        self.customers: Dict[str, CustomerProfile] = {}
        self.transactions: List[TransactionRecord] = []
        self.alerts: Dict[str, AMLAlert] = []
        self.sanctions_database: List[SanctionsEntry] = []

        # Initialize components
        self.customer_due_diligence = CustomerDueDiligence(self)
        self.enhanced_due_diligence = EnhancedDueDiligence(self)
        self.aml_monitoring = AMLTransactionMonitoring(self)
        self.sanctions_screening = SanctionsScreening(self)
        self.pep_check = PEPCheck(self)
        self.adverse_media = AdverseMediaScreening(self)
        self.risk_scorer = RiskScoringEngine(self)

        # Load default configurations
        self._initialize_sanctions_lists(sanctions_lists or ['OFAC', 'EU', 'UN'])
        self._initialize_risk_thresholds(risk_thresholds)

    def _initialize_sanctions_lists(self, lists: List[str]):
        """Initialize sanctions screening lists"""
        # In production, this would load from external sources
        # For now, initialize with sample data
        self.sanctions_database = [
            SanctionsEntry(
                entity_id="SAMPLE_001",
                entity_name="John Doe",
                entity_type="Individual",
                aliases=["Johnny Doe", "J. Doe"],
                countries=["Country X"],
                sanctions_program="OFAC",
                listing_date=date(2020, 1, 1)
            ),
            SanctionsEntry(
                entity_id="SAMPLE_002",
                entity_name="Evil Corp",
                entity_type="Entity",
                aliases=["Bad Company Ltd"],
                countries=["Country Y"],
                sanctions_program="EU",
                listing_date=date(2021, 6, 15)
            )
        ]

    def _initialize_risk_thresholds(self, thresholds: Optional[Dict[str, float]]):
        """Initialize risk scoring thresholds"""
        self.risk_thresholds = thresholds or {
            'low_risk_max': 0.3,
            'medium_risk_max': 0.6,
            'high_risk_max': 0.8,
            'critical_risk_max': 1.0,
            'transaction_amount_threshold': 10000,
            'frequency_threshold': 5,
            'geographic_risk_weight': 0.3,
            'behavioral_risk_weight': 0.4,
            'transaction_risk_weight': 0.3
        }

    def onboard_customer(self, customer_data: Dict[str, Any]) -> str:
        """Onboard a new customer with KYC process"""
        # Create customer profile
        customer = CustomerProfile(
            customer_id="",  # Will be generated
            customer_type=customer_data.get('customer_type', 'Individual'),
            full_name=customer_data['full_name'],
            date_of_birth=customer_data.get('date_of_birth'),
            nationality=customer_data.get('nationality'),
            residence_country=customer_data.get('residence_country'),
            address=customer_data.get('address', {}),
            contact_info=customer_data.get('contact_info', {}),
            occupation=customer_data.get('occupation'),
            employer=customer_data.get('employer'),
            annual_income=customer_data.get('annual_income'),
            source_of_wealth=customer_data.get('source_of_wealth')
        )

        # Store customer
        self.customers[customer.customer_id] = customer

        # Perform initial KYC checks
        self._perform_initial_kyc_checks(customer)

        return customer.customer_id

    def _perform_initial_kyc_checks(self, customer: CustomerProfile):
        """Perform initial KYC verification checks"""
        # Sanctions screening
        sanctions_hit = self.sanctions_screening.screen_customer(customer)
        if sanctions_hit:
            customer.kyc_status = KYCStatus.REJECTED
            customer.compliance_notes.append("Customer matched sanctions list")
            return

        # PEP screening
        pep_hit = self.pep_check.screen_customer(customer)
        if pep_hit:
            customer.politically_exposed = True
            customer.pep_details = pep_hit
            customer.kyc_status = KYCStatus.IN_REVIEW

        # Risk scoring
        risk_score = self.risk_scorer.calculate_risk_score(customer)
        customer.risk_level = self._determine_risk_level(risk_score)

        # Set KYC status based on risk level
        if customer.risk_level == RiskLevel.CRITICAL:
            customer.kyc_status = KYCStatus.REJECTED
            customer.compliance_notes.append("High risk profile - requires enhanced due diligence")
        elif customer.risk_level == RiskLevel.HIGH:
            customer.kyc_status = KYCStatus.IN_REVIEW
            customer.compliance_notes.append("Medium-high risk profile - requires review")
        else:
            customer.kyc_status = KYCStatus.APPROVED
            customer.kyc_completion_date = datetime.now()

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        thresholds = self.risk_thresholds
        if risk_score <= thresholds['low_risk_max']:
            return RiskLevel.LOW
        elif risk_score <= thresholds['medium_risk_max']:
            return RiskLevel.MEDIUM
        elif risk_score <= thresholds['high_risk_max']:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def submit_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Submit transaction for AML monitoring"""
        # Create transaction record
        transaction = TransactionRecord(
            transaction_id=transaction_data.get('transaction_id', f"TXN_{int(datetime.now().timestamp())}"),
            customer_id=transaction_data['customer_id'],
            transaction_date=transaction_data.get('transaction_date', datetime.now()),
            transaction_type=transaction_data['transaction_type'],
            amount=transaction_data['amount'],
            currency=transaction_data.get('currency', 'USD'),
            counterparty=transaction_data.get('counterparty'),
            counterparty_country=transaction_data.get('counterparty_country'),
            payment_method=transaction_data.get('payment_method'),
            transaction_purpose=transaction_data.get('transaction_purpose')
        )

        # Perform AML checks
        self._perform_aml_checks(transaction)

        # Store transaction
        self.transactions.append(transaction)

        return transaction.transaction_id

    def _perform_aml_checks(self, transaction: TransactionRecord):
        """Perform AML monitoring on transaction"""
        customer = self.customers.get(transaction.customer_id)
        if not customer:
            return

        # Check transaction against AML rules
        alerts = self.aml_monitoring.analyze_transaction(transaction, customer)

        # Create alerts if necessary
        for alert_data in alerts:
            alert = AMLAlert(
                alert_id="",
                customer_id=transaction.customer_id,
                alert_type=alert_data['type'],
                severity=alert_data['severity'],
                description=alert_data['description'],
                transaction_ids=[transaction.transaction_id],
                risk_indicators=alert_data.get('indicators', [])
            )
            self.alerts.append(alert)

            # Update transaction
            transaction.suspicious_flags.extend(alert.risk_indicators)
            transaction.risk_score = max(transaction.risk_score, self._calculate_alert_severity_score(alert))

    def _calculate_alert_severity_score(self, alert: AMLAlert) -> float:
        """Calculate risk score from alert severity"""
        severity_scores = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'critical': 1.0
        }
        return severity_scores.get(alert.severity, 0.5)

    def get_customer_status(self, customer_id: str) -> Optional[KYCStatus]:
        """Get customer KYC status"""
        customer = self.customers.get(customer_id)
        return customer.kyc_status if customer else None

    def get_customer_risk_level(self, customer_id: str) -> Optional[RiskLevel]:
        """Get customer risk level"""
        customer = self.customers.get(customer_id)
        return customer.risk_level if customer else None

    def get_open_alerts(self, customer_id: Optional[str] = None) -> List[AMLAlert]:
        """Get open AML alerts"""
        alerts = [alert for alert in self.alerts if alert.status == 'open']
        if customer_id:
            alerts = [alert for alert in alerts if alert.customer_id == customer_id]
        return alerts

    def resolve_alert(self, alert_id: str, resolution_notes: str, resolved_by: str):
        """Resolve an AML alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = 'closed'
                alert.resolution_date = datetime.now()
                alert.resolution_notes = resolution_notes
                alert.assigned_to = resolved_by
                break

    def generate_compliance_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate KYC/AML compliance report"""
        # Filter data by date range
        period_transactions = [
            tx for tx in self.transactions
            if start_date <= tx.transaction_date.date() <= end_date
        ]

        period_alerts = [
            alert for alert in self.alerts
            if start_date <= alert.created_date.date() <= end_date
        ]

        # Calculate metrics
        total_customers = len(self.customers)
        approved_customers = len([c for c in self.customers.values() if c.kyc_status == KYCStatus.APPROVED])
        rejected_customers = len([c for c in self.customers.values() if c.kyc_status == KYCStatus.REJECTED])

        high_risk_customers = len([c for c in self.customers.values() if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        pep_customers = len([c for c in self.customers.values() if c.politically_exposed])

        report = {
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'customer_metrics': {
                'total_customers': total_customers,
                'approved_customers': approved_customers,
                'rejected_customers': rejected_customers,
                'pending_reviews': len([c for c in self.customers.values() if c.kyc_status == KYCStatus.IN_REVIEW]),
                'approval_rate': (approved_customers / total_customers) * 100 if total_customers > 0 else 0,
                'high_risk_customers': high_risk_customers,
                'pep_customers': pep_customers
            },
            'transaction_metrics': {
                'total_transactions': len(period_transactions),
                'suspicious_transactions': len([tx for tx in period_transactions if tx.suspicious_flags]),
                'high_value_transactions': len([tx for tx in period_transactions if tx.amount > self.risk_thresholds['transaction_amount_threshold']])
            },
            'alert_metrics': {
                'total_alerts': len(period_alerts),
                'open_alerts': len([alert for alert in period_alerts if alert.status == 'open']),
                'closed_alerts': len([alert for alert in period_alerts if alert.status == 'closed']),
                'false_positives': len([alert for alert in period_alerts if alert.status == 'false_positive']),
                'critical_alerts': len([alert for alert in period_alerts if alert.severity == 'critical'])
            },
            'compliance_score': self._calculate_compliance_score(),
            'recommendations': self._generate_compliance_recommendations()
        }

        return report

    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        # Simple scoring based on various factors
        customer_approval_rate = len([c for c in self.customers.values() if c.kyc_status == KYCStatus.APPROVED]) / len(self.customers) if self.customers else 0

        open_alerts = len([alert for alert in self.alerts if alert.status == 'open'])
        total_alerts = len(self.alerts)
        alert_resolution_rate = (total_alerts - open_alerts) / total_alerts if total_alerts > 0 else 1.0

        # Weighted score
        score = (customer_approval_rate * 0.4) + (alert_resolution_rate * 0.4) + (0.2)  # Base score
        return min(100.0, score * 100)

    def _generate_compliance_recommendations(self) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        # Check approval rate
        approval_rate = len([c for c in self.customers.values() if c.kyc_status == KYCStatus.APPROVED]) / len(self.customers) if self.customers else 0
        if approval_rate < 0.7:
            recommendations.append("Low customer approval rate. Review KYC processes and criteria.")

        # Check alert resolution
        open_alerts = len([alert for alert in self.alerts if alert.status == 'open'])
        if open_alerts > 10:
            recommendations.append("High number of open alerts. Increase resources for alert investigation.")

        # Check high-risk customers
        high_risk_count = len([c for c in self.customers.values() if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        if high_risk_count > len(self.customers) * 0.1:
            recommendations.append("High proportion of high-risk customers. Review risk assessment criteria.")

        return recommendations


class CustomerDueDiligence:
    """Customer Due Diligence (CDD) component"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def perform_due_diligence(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Perform customer due diligence"""
        results = {
            'identity_verification': self._verify_identity(customer),
            'address_verification': self._verify_address(customer),
            'source_of_wealth': self._verify_source_of_wealth(customer),
            'overall_risk_assessment': RiskLevel.MEDIUM,
            'recommendations': []
        }

        # Determine overall risk
        risk_factors = 0
        if not results['identity_verification']['verified']:
            risk_factors += 1
        if not results['address_verification']['verified']:
            risk_factors += 1
        if not results['source_of_wealth']['verified']:
            risk_factors += 1

        if risk_factors >= 2:
            results['overall_risk_assessment'] = RiskLevel.HIGH
        elif risk_factors == 1:
            results['overall_risk_assessment'] = RiskLevel.MEDIUM
        else:
            results['overall_risk_assessment'] = RiskLevel.LOW

        return results

    def _verify_identity(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Verify customer identity"""
        # Simplified identity verification
        return {
            'verified': True,  # Assume verified for demo
            'verification_method': 'Document Review',
            'confidence_score': 0.9,
            'documents_reviewed': ['passport', 'drivers_license']
        }

    def _verify_address(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Verify customer address"""
        # Simplified address verification
        return {
            'verified': True,  # Assume verified for demo
            'verification_method': 'Utility Bill',
            'confidence_score': 0.85
        }

    def _verify_source_of_wealth(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Verify source of wealth"""
        # Simplified source of wealth verification
        return {
            'verified': bool(customer.source_of_wealth),
            'verification_method': 'Declaration',
            'confidence_score': 0.8 if customer.source_of_wealth else 0.0
        }


class EnhancedDueDiligence:
    """Enhanced Due Diligence (EDD) for high-risk customers"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def perform_enhanced_due_diligence(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Perform enhanced due diligence for high-risk customers"""
        results = {
            'background_check': self._perform_background_check(customer),
            'financial_analysis': self._perform_financial_analysis(customer),
            'relationship_mapping': self._map_relationships(customer),
            'enhanced_risk_assessment': RiskLevel.CRITICAL,
            'edd_recommendations': []
        }

        # Enhanced risk assessment
        risk_score = 0

        if results['background_check']['adverse_findings']:
            risk_score += 0.4

        if results['financial_analysis']['complex_structures']:
            risk_score += 0.3

        if results['relationship_mapping']['high_risk_connections']:
            risk_score += 0.3

        if risk_score > 0.6:
            results['enhanced_risk_assessment'] = RiskLevel.CRITICAL
        elif risk_score > 0.3:
            results['enhanced_risk_assessment'] = RiskLevel.HIGH
        else:
            results['enhanced_risk_assessment'] = RiskLevel.MEDIUM

        return results

    def _perform_background_check(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Perform comprehensive background check"""
        return {
            'adverse_findings': False,  # Assume no findings for demo
            'criminal_records': False,
            'civil_litigation': False,
            'regulatory_actions': False,
            'reputation_risk': 'Low'
        }

    def _perform_financial_analysis(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Perform financial analysis"""
        return {
            'complex_structures': False,
            'unusual_wealth_sources': False,
            'tax_compliance': True,
            'financial_stability': 'Stable'
        }

    def _map_relationships(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Map customer relationships"""
        return {
            'high_risk_connections': False,
            'pep_associations': customer.politically_exposed,
            'sanctions_exposure': False,
            'network_analysis': 'Low Risk'
        }


class AMLTransactionMonitoring:
    """AML transaction monitoring component"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def analyze_transaction(self, transaction: TransactionRecord, customer: CustomerProfile) -> List[Dict[str, Any]]:
        """Analyze transaction for AML risks"""
        alerts = []

        # Check transaction amount
        if transaction.amount > self.system.risk_thresholds['transaction_amount_threshold']:
            alerts.append({
                'type': AMLAlertType.UNUSUAL_TRANSACTION,
                'severity': 'medium',
                'description': f'High value transaction: ${transaction.amount:,.2f}',
                'indicators': ['high_amount']
            })

        # Check for round dollar amounts
        if self._is_round_amount(transaction.amount):
            alerts.append({
                'type': AMLAlertType.ROUND_DOLLAR,
                'severity': 'low',
                'description': f'Round dollar transaction: ${transaction.amount:,.2f}',
                'indicators': ['round_amount']
            })

        # Check transaction frequency
        recent_transactions = self._get_recent_transactions(customer.customer_id, hours=24)
        if len(recent_transactions) > self.system.risk_thresholds['frequency_threshold']:
            alerts.append({
                'type': AMLAlertType.RAPID_MOVEMENT,
                'severity': 'medium',
                'description': f'High transaction frequency: {len(recent_transactions)} transactions in 24 hours',
                'indicators': ['high_frequency']
            })

        # Check for structuring (smurfing)
        if self._detect_structuring(transaction, customer):
            alerts.append({
                'type': AMLAlertType.STRUCTURING,
                'severity': 'high',
                'description': 'Potential structuring/smurfing detected',
                'indicators': ['structuring_pattern']
            })

        # Check counterparty risk
        if transaction.counterparty_country in ['High_Risk_Country_1', 'High_Risk_Country_2']:
            alerts.append({
                'type': AMLAlertType.HIGH_RISK_JURISDICTION,
                'severity': 'medium',
                'description': f'Transaction to high-risk jurisdiction: {transaction.counterparty_country}',
                'indicators': ['high_risk_jurisdiction']
            })

        return alerts

    def _is_round_amount(self, amount: float) -> bool:
        """Check if amount is round (multiple of 1000)"""
        return amount % 1000 == 0 and amount >= 10000

    def _get_recent_transactions(self, customer_id: str, hours: int) -> List[TransactionRecord]:
        """Get recent transactions for customer"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            tx for tx in self.system.transactions
            if tx.customer_id == customer_id and tx.transaction_date > cutoff_time
        ]

    def _detect_structuring(self, transaction: TransactionRecord, customer: CustomerProfile) -> bool:
        """Detect potential structuring/smurfing"""
        # Simplified detection logic
        recent_txs = self._get_recent_transactions(customer.customer_id, hours=24)
        similar_amounts = [
            tx for tx in recent_txs
            if abs(tx.amount - transaction.amount) / transaction.amount < 0.1
        ]

        return len(similar_amounts) >= 3  # Multiple similar amounts


class SanctionsScreening:
    """Sanctions screening component"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def screen_customer(self, customer: CustomerProfile) -> Optional[Dict[str, Any]]:
        """Screen customer against sanctions lists"""
        # Check name matches
        for entry in self.system.sanctions_database:
            if self._name_match(customer.full_name, entry.entity_name, entry.aliases):
                return {
                    'sanctions_entry': entry,
                    'match_type': 'name_match',
                    'confidence': 0.95,
                    'sanctions_program': entry.sanctions_program
                }

        return None

    def screen_transaction(self, transaction: TransactionRecord) -> Optional[Dict[str, Any]]:
        """Screen transaction counterparties"""
        counterparty = transaction.counterparty
        if not counterparty:
            return None

        for entry in self.system.sanctions_database:
            if self._name_match(counterparty, entry.entity_name, entry.aliases):
                return {
                    'sanctions_entry': entry,
                    'match_type': 'counterparty_match',
                    'confidence': 0.9,
                    'transaction_id': transaction.transaction_id
                }

        return None

    def _name_match(self, name1: str, name2: str, aliases: List[str] = None) -> bool:
        """Check if names match (with fuzzy matching)"""
        names_to_check = [name2] + (aliases or [])

        for name in names_to_check:
            # Exact match
            if name1.lower() == name.lower():
                return True

            # Fuzzy match (80% similarity)
            similarity = fuzz.token_sort_ratio(name1, name)
            if similarity >= 80:
                return True

        return False


class PEPCheck:
    """Politically Exposed Persons screening"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system
        # In production, this would load from PEP databases
        self.pep_database = [
            {'name': 'John Smith', 'position': 'Minister', 'country': 'Country X'},
            {'name': 'Jane Doe', 'position': 'President', 'country': 'Country Y'}
        ]

    def screen_customer(self, customer: CustomerProfile) -> Optional[Dict[str, Any]]:
        """Screen customer for PEP status"""
        for pep in self.pep_database:
            if fuzz.token_sort_ratio(customer.full_name, pep['name']) >= 85:
                return {
                    'pep_entry': pep,
                    'match_confidence': 0.9,
                    'relationship': 'direct'  # Could be family member, close associate, etc.
                }

        return None


class AdverseMediaScreening:
    """Adverse media screening component"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def screen_customer(self, customer: CustomerProfile) -> Dict[str, Any]:
        """Screen customer for adverse media"""
        # In production, this would query news databases and adverse media sources
        return {
            'adverse_findings': False,
            'media_mentions': [],
            'reputation_score': 'Good',
            'last_screening_date': datetime.now()
        }


class RiskScoringEngine:
    """Risk scoring engine for customers"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def calculate_risk_score(self, customer: CustomerProfile) -> float:
        """Calculate comprehensive risk score for customer"""
        score = 0.0

        # Geographic risk
        geographic_risk = self._calculate_geographic_risk(customer)
        score += geographic_risk * self.system.risk_thresholds['geographic_risk_weight']

        # Behavioral risk
        behavioral_risk = self._calculate_behavioral_risk(customer)
        score += behavioral_risk * self.system.risk_thresholds['behavioral_risk_weight']

        # Transaction risk
        transaction_risk = self._calculate_transaction_risk(customer)
        score += transaction_risk * self.system.risk_thresholds['transaction_risk_weight']

        return min(1.0, score)

    def _calculate_geographic_risk(self, customer: CustomerProfile) -> float:
        """Calculate geographic risk score"""
        high_risk_countries = ['High_Risk_Country_1', 'High_Risk_Country_2']

        risk = 0.0
        if customer.nationality in high_risk_countries:
            risk += 0.5
        if customer.residence_country in high_risk_countries:
            risk += 0.5

        return risk

    def _calculate_behavioral_risk(self, customer: CustomerProfile) -> float:
        """Calculate behavioral risk score"""
        risk = 0.0

        if customer.politically_exposed:
            risk += 0.4

        if customer.risk_level == RiskLevel.HIGH:
            risk += 0.3
        elif customer.risk_level == RiskLevel.CRITICAL:
            risk += 0.6

        return risk

    def _calculate_transaction_risk(self, customer: CustomerProfile) -> float:
        """Calculate transaction-based risk score"""
        customer_transactions = [
            tx for tx in self.system.transactions
            if tx.customer_id == customer.customer_id
        ]

        if not customer_transactions:
            return 0.0

        # Calculate average transaction amount
        avg_amount = np.mean([tx.amount for tx in customer_transactions])

        # High amount transactions
        high_amount_count = len([
            tx for tx in customer_transactions
            if tx.amount > self.system.risk_thresholds['transaction_amount_threshold']
        ])

        risk = 0.0
        if avg_amount > self.system.risk_thresholds['transaction_amount_threshold']:
            risk += 0.3

        if high_amount_count > len(customer_transactions) * 0.1:  # >10% high amount
            risk += 0.4

        return risk


class KYCStatusManager:
    """KYC status management component"""

    def __init__(self, system: KYCAMLSystem):
        self.system = system

    def update_kyc_status(self, customer_id: str, new_status: KYCStatus, notes: str = ""):
        """Update customer KYC status"""
        customer = self.system.customers.get(customer_id)
        if customer:
            customer.kyc_status = new_status
            if new_status == KYCStatus.APPROVED:
                customer.kyc_completion_date = datetime.now()
            customer.compliance_notes.append(f"Status updated to {new_status.value}: {notes}")

    def schedule_review(self, customer_id: str, review_date: date, reason: str):
        """Schedule KYC review"""
        customer = self.system.customers.get(customer_id)
        if customer:
            customer.next_review_date = datetime.combine(review_date, datetime.min.time())
            customer.compliance_notes.append(f"Review scheduled for {review_date}: {reason}")

    def check_expiring_kyc(self, days_ahead: int = 30) -> List[str]:
        """Check for expiring KYC statuses"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        expiring = []

        for customer_id, customer in self.system.customers.items():
            if customer.next_review_date and customer.next_review_date <= cutoff_date:
                expiring.append(customer_id)

        return expiring


# Factory functions
def create_kyc_aml_system(sanctions_lists: Optional[List[str]] = None,
                         watchlist_providers: Optional[List[str]] = None) -> KYCAMLSystem:
    """Create KYC/AML compliance system"""
    return KYCAMLSystem(sanctions_lists, watchlist_providers)

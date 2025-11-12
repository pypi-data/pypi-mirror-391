"""
Compliance & Regulatory Reporting Module
========================================

Enterprise-grade compliance and regulatory reporting system for Qantify.
Provides comprehensive regulatory compliance, audit trails, risk reporting,
and automated regulatory filings for institutional trading operations.

Key Features:
- SEC Form 13F, 13D/G, 13H reporting
- FINRA regulatory compliance
- FCA/MiFID II compliance (UK/EU)
- MAS compliance (Singapore)
- ASIC compliance (Australia)
- KYC/AML integration
- Comprehensive audit trails
- Real-time compliance monitoring
- Risk reporting and disclosures
- Transaction and position reporting
- Automated filing systems
- Regulatory communication protocols

Supported Regulations:
- US Securities Laws (SEC, FINRA)
- EU MiFID II/MiFIR
- UK FCA regulations
- Singapore MAS regulations
- Australia ASIC regulations
- Global AML/KYC standards
- Basel III capital requirements
- Dodd-Frank Act compliance
"""

from .regulatory_reporting import (
    RegulatoryReportingEngine,
    SECReporting,
    FINRAReporting,
    FCAReporting,
    MASReporting,
    ASICReporting,
    Form13FReporter,
    Form13DGReporter,
    Form13HReporter,
    create_regulatory_reporter,
    generate_compliance_report
)

from .compliance_monitoring import (
    ComplianceMonitoringEngine,
    RealTimeComplianceMonitor,
    PositionLimitMonitor,
    TradingVolumeMonitor,
    RiskLimitMonitor,
    MarketImpactMonitor,
    PreTradeComplianceCheck,
    PostTradeComplianceCheck,
    ComplianceAlertSystem,
    RegulatoryBreachDetector,
    create_compliance_monitor
)

from .audit_trail import (
    AuditTrailManager,
    TransactionAuditor,
    PositionAuditor,
    RiskAuditor,
    ComplianceAuditor,
    AuditLogStorage,
    BlockchainAuditTrail,
    SecureAuditStorage,
    AuditTrailAnalyzer,
    create_audit_trail_manager
)

from .risk_reporting import (
    RiskReportingEngine,
    ValueAtRiskReporter,
    StressTestReporter,
    ScenarioAnalysisReporter,
    LiquidityRiskReporter,
    CreditRiskReporter,
    OperationalRiskReporter,
    MarketRiskReporter,
    RegulatoryRiskReporter,
    RiskDisclosureGenerator,
    create_risk_reporting_engine
)

from .kyc_aml import (
    KYCAMLSystem,
    CustomerDueDiligence,
    EnhancedDueDiligence,
    AMLTransactionMonitoring,
    SanctionsScreening,
    PEPCheck,
    AdverseMediaScreening,
    RiskScoringEngine,
    KYCStatusManager,
    create_kyc_aml_system
)

from .transaction_reporting import (
    TransactionReportingEngine,
    TradeReporting,
    OrderReporting,
    ExecutionReporting,
    SettlementReporting,
    CrossReporting,
    RegulatoryTradeReporting,
    TransactionCostAnalysis,
    create_transaction_reporter
)

from .position_reporting import (
    PositionReportingEngine,
    PortfolioPositionReporter,
    SecurityPositionReporter,
    DerivativePositionReporter,
    FXPositionReporter,
    PositionAggregationEngine,
    PositionReconciliation,
    create_position_reporter
)

__all__ = [
    # Regulatory Reporting
    'RegulatoryReportingEngine', 'SECReporting', 'FINRAReporting', 'FCAReporting',
    'MASReporting', 'ASICReporting', 'Form13FReporter', 'Form13DGReporter',
    'Form13HReporter', 'create_regulatory_reporter', 'generate_compliance_report',

    # Compliance Monitoring
    'ComplianceMonitoringEngine', 'RealTimeComplianceMonitor', 'PositionLimitMonitor',
    'TradingVolumeMonitor', 'RiskLimitMonitor', 'MarketImpactMonitor',
    'PreTradeComplianceCheck', 'PostTradeComplianceCheck', 'ComplianceAlertSystem',
    'RegulatoryBreachDetector', 'create_compliance_monitor',

    # Audit Trail
    'AuditTrailManager', 'TransactionAuditor', 'PositionAuditor', 'RiskAuditor',
    'ComplianceAuditor', 'AuditLogStorage', 'BlockchainAuditTrail', 'SecureAuditStorage',
    'AuditTrailAnalyzer', 'create_audit_trail_manager',

    # Risk Reporting
    'RiskReportingEngine', 'ValueAtRiskReporter', 'StressTestReporter', 'ScenarioAnalysisReporter',
    'LiquidityRiskReporter', 'CreditRiskReporter', 'OperationalRiskReporter',
    'MarketRiskReporter', 'RegulatoryRiskReporter', 'RiskDisclosureGenerator',
    'create_risk_reporting_engine',

    # KYC/AML
    'KYCAMLSystem', 'CustomerDueDiligence', 'EnhancedDueDiligence', 'AMLTransactionMonitoring',
    'SanctionsScreening', 'PEPCheck', 'AdverseMediaScreening', 'RiskScoringEngine',
    'KYCStatusManager', 'create_kyc_aml_system',

    # Transaction Reporting
    'TransactionReportingEngine', 'TradeReporting', 'OrderReporting', 'ExecutionReporting',
    'SettlementReporting', 'CrossReporting', 'RegulatoryTradeReporting',
    'TransactionCostAnalysis', 'create_transaction_reporter',

    # Position Reporting
    'PositionReportingEngine', 'PortfolioPositionReporter', 'SecurityPositionReporter',
    'DerivativePositionReporter', 'FXPositionReporter', 'PositionAggregationEngine',
    'PositionReconciliation', 'create_position_reporter'
]

# Version information
__version__ = "1.0.0"
__author__ = "Qantify Team"
__description__ = "Enterprise-grade compliance and regulatory reporting system"

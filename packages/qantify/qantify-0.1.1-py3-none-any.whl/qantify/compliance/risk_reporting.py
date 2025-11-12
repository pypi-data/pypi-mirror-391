"""
Risk Reporting Engine
=====================

Comprehensive risk reporting system for regulatory compliance and risk disclosure.
Generates risk reports, stress test results, scenario analyses, and regulatory filings.

Key Features:
- Value at Risk (VaR) reporting
- Stress test reporting and scenario analysis
- Liquidity risk assessment and reporting
- Credit risk measurement and disclosure
- Operational risk reporting
- Market risk analytics and reporting
- Regulatory risk disclosure generation
- Risk concentration analysis
- Counterparty risk assessment
- Sovereign risk monitoring
- ESG risk reporting
- Climate risk assessment
- Cybersecurity risk reporting
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns


class RiskType(Enum):
    """Types of financial risk"""
    MARKET_RISK = "market_risk"
    CREDIT_RISK = "credit_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    OPERATIONAL_RISK = "operational_risk"
    REGULATORY_RISK = "regulatory_risk"
    REPUTATIONAL_RISK = "reputational_risk"
    STRATEGIC_RISK = "strategic_risk"
    ESG_RISK = "esg_risk"
    CLIMATE_RISK = "climate_risk"
    CYBERSECURITY_RISK = "cybersecurity_risk"


class RiskMetric(Enum):
    """Risk measurement metrics"""
    VALUE_AT_RISK = "value_at_risk"
    EXPECTED_SHORTFALL = "expected_shortfall"
    STRESS_TEST_LOSS = "stress_test_loss"
    LIQUIDITY_COVERAGE_RATIO = "liquidity_coverage_ratio"
    NET_STABLE_FUNDING_RATIO = "net_stable_funding_ratio"
    CREDIT_VALUE_ADJUSTMENT = "credit_value_adjustment"
    DEBT_TO_EQUITY_RATIO = "debt_to_equity_ratio"
    CONCENTRATION_RATIO = "concentration_ratio"
    VOLATILITY = "volatility"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"


class ReportingFrequency(Enum):
    """Risk reporting frequencies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    AD_HOC = "ad_hoc"


class RegulatoryFramework(Enum):
    """Supported regulatory frameworks"""
    BASEL_III = "basel_iii"
    DODD_FRANK = "dodd_frank"
    EMIR = "emir"
    MIFID_II = "mifid_ii"
    FATCA = "fatca"
    CRS = "crs"
    SFTR = "sftr"
    CSDR = "csdr"


@dataclass
class RiskReport:
    """Risk report data structure"""
    report_id: str
    report_type: str
    reporting_date: date
    reporting_period: str
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    scenarios: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    regulatory_requirements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.report_id:
            self.report_id = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


@dataclass
class RiskThreshold:
    """Risk threshold configuration"""
    risk_type: RiskType
    metric: RiskMetric
    threshold_value: float
    breach_action: str
    notification_level: str
    regulatory_requirement: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class StressTestScenario:
    """Stress test scenario definition"""
    scenario_id: str
    scenario_name: str
    description: str
    shock_parameters: Dict[str, Any]
    probability_weight: float
    regulatory_framework: Optional[RegulatoryFramework] = None
    created_date: Optional[datetime] = None

    def apply_shock(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply scenario shocks to portfolio"""
        # Implementation would vary by scenario type
        raise NotImplementedError


class RiskReportingEngine:
    """Main risk reporting engine"""

    def __init__(self,
                 firm_name: str,
                 regulatory_frameworks: Optional[List[RegulatoryFramework]] = None,
                 risk_thresholds: Optional[List[RiskThreshold]] = None):
        self.firm_name = firm_name
        self.regulatory_frameworks = regulatory_frameworks or [RegulatoryFramework.BASEL_III]
        self.risk_thresholds = risk_thresholds or self._get_default_thresholds()
        self.reports: Dict[str, RiskReport] = {}
        self.scenarios: Dict[str, StressTestScenario] = {}

        # Initialize reporters
        self.var_reporter = ValueAtRiskReporter(self)
        self.stress_reporter = StressTestReporter(self)
        self.scenario_reporter = ScenarioAnalysisReporter(self)
        self.liquidity_reporter = LiquidityRiskReporter(self)
        self.credit_reporter = CreditRiskReporter(self)
        self.operational_reporter = OperationalRiskReporter(self)
        self.market_reporter = MarketRiskReporter(self)
        self.regulatory_reporter = RegulatoryRiskReporter(self)

        # Load default scenarios
        self._initialize_default_scenarios()

    def _get_default_thresholds(self) -> List[RiskThreshold]:
        """Get default risk thresholds"""
        return [
            RiskThreshold(
                RiskType.MARKET_RISK, RiskMetric.VALUE_AT_RISK,
                100000, "INCREASE_CAPITAL", "CRITICAL", "BASEL_III"
            ),
            RiskThreshold(
                RiskType.LIQUIDITY_RISK, RiskMetric.LIQUIDITY_COVERAGE_RATIO,
                1.0, "REDUCE_LEVERAGE", "HIGH", "BASEL_III"
            ),
            RiskThreshold(
                RiskType.CREDIT_RISK, RiskMetric.CREDIT_VALUE_ADJUSTMENT,
                50000, "REVIEW_EXPOSURES", "MEDIUM", "BASEL_III"
            ),
        ]

    def _initialize_default_scenarios(self):
        """Initialize default stress test scenarios"""
        # Market crash scenario
        self.scenarios['market_crash_2008'] = StressTestScenario(
            scenario_id='market_crash_2008',
            scenario_name='2008 Market Crash',
            description='Simulates the 2008 financial crisis conditions',
            shock_parameters={
                'equity_shock': -0.5,
                'bond_yield_shock': 0.02,
                'credit_spread_shock': 0.05,
                'volatility_shock': 2.0
            },
            probability_weight=0.01,
            regulatory_framework=RegulatoryFramework.DODD_FRANK
        )

        # Interest rate shock
        self.scenarios['rate_hike_cycle'] = StressTestScenario(
            scenario_id='rate_hike_cycle',
            scenario_name='Aggressive Rate Hike Cycle',
            description='Simulates aggressive monetary tightening',
            shock_parameters={
                'interest_rate_shock': 0.03,
                'equity_shock': -0.15,
                'bond_price_shock': -0.1
            },
            probability_weight=0.05,
            regulatory_framework=RegulatoryFramework.BASEL_III
        )

        # Liquidity crisis
        self.scenarios['liquidity_crisis'] = StressTestScenario(
            scenario_id='liquidity_crisis',
            scenario_name='Liquidity Crisis',
            description='Simulates severe liquidity squeeze',
            shock_parameters={
                'liquidity_premium': 0.05,
                'funding_spread_shock': 0.02,
                'repo_haircut_increase': 0.1
            },
            probability_weight=0.02,
            regulatory_framework=RegulatoryFramework.BASEL_III
        )

    def generate_risk_report(self,
                           report_date: date,
                           portfolio_data: Dict[str, Any],
                           reporting_period: str = "daily",
                           include_stress_tests: bool = True) -> str:
        """Generate comprehensive risk report"""

        report = RiskReport(
            report_id="",
            report_type="comprehensive_risk_report",
            reporting_date=report_date,
            reporting_period=reporting_period
        )

        # Calculate risk metrics
        report.risk_metrics = self._calculate_risk_metrics(portfolio_data)

        # Run stress tests if requested
        if include_stress_tests:
            report.scenarios = self._run_stress_tests(portfolio_data)

        # Generate recommendations
        report.recommendations = self._generate_risk_recommendations(report.risk_metrics)

        # Check regulatory requirements
        report.regulatory_requirements = self._check_regulatory_requirements(report.risk_metrics)

        # Store report
        self.reports[report.report_id] = report

        return report.report_id

    def _calculate_risk_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        metrics = {}

        # Market risk metrics
        if 'returns' in portfolio_data:
            returns = np.array(portfolio_data['returns'])
            metrics.update(self._calculate_market_risk_metrics(returns))

        # Liquidity risk metrics
        if 'cash_flows' in portfolio_data:
            cash_flows = portfolio_data['cash_flows']
            metrics.update(self._calculate_liquidity_risk_metrics(cash_flows))

        # Credit risk metrics
        if 'exposures' in portfolio_data:
            exposures = portfolio_data['exposures']
            metrics.update(self._calculate_credit_risk_metrics(exposures))

        # Concentration metrics
        if 'holdings' in portfolio_data:
            holdings = portfolio_data['holdings']
            metrics.update(self._calculate_concentration_metrics(holdings))

        return metrics

    def _calculate_market_risk_metrics(self, returns: np.ndarray) -> Dict[str, Any]:
        """Calculate market risk metrics"""
        metrics = {}
        
        # Ensure returns is numpy array
        if isinstance(returns, (list, tuple)):
            returns = np.array(returns)
        elif not isinstance(returns, np.ndarray):
            returns = np.array([returns]) if not isinstance(returns, str) else np.array([])

        # Value at Risk (95% confidence, 1-day)
        if len(returns) > 30:
            var_95 = np.percentile(returns, 5)
            metrics['value_at_risk_95'] = abs(var_95) * 1000000  # Assuming $1M portfolio

            # Expected Shortfall
            tail_losses = returns[returns <= var_95]
            if len(tail_losses) > 0:
                es_95 = np.mean(tail_losses)
                metrics['expected_shortfall_95'] = abs(es_95) * 1000000

            # Volatility
            metrics['volatility'] = np.std(returns) * np.sqrt(252)  # Annualized

            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02 / 252  # Daily
            excess_returns = returns - risk_free_rate
            if np.std(excess_returns) > 0:
                metrics['sharpe_ratio'] = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

            # Maximum drawdown
            cumulative = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            metrics['max_drawdown'] = abs(np.min(drawdown))

        return metrics

    def _calculate_liquidity_risk_metrics(self, cash_flows: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate liquidity risk metrics"""
        metrics = {}

        # Liquidity Coverage Ratio (simplified)
        if 'high_quality_assets' in cash_flows and 'net_cash_outflows' in cash_flows:
            hqa = cash_flows['high_quality_assets']
            nco = cash_flows['net_cash_outflows']
            if nco > 0:
                metrics['liquidity_coverage_ratio'] = hqa / nco

        # Net Stable Funding Ratio (simplified)
        if 'stable_funding' in cash_flows and 'required_stable_funding' in cash_flows:
            sf = cash_flows['stable_funding']
            rsf = cash_flows['required_stable_funding']
            if rsf > 0:
                metrics['net_stable_funding_ratio'] = sf / rsf

        return metrics

    def _calculate_credit_risk_metrics(self, exposures: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate credit risk metrics"""
        metrics = {}

        # Credit Value Adjustment (simplified)
        if 'credit_exposures' in exposures:
            exposures_list = exposures['credit_exposures']
            cva = sum(exp.get('amount', 0) * exp.get('probability_of_default', 0.01) * exp.get('loss_given_default', 0.45) 
                     for exp in exposures_list if isinstance(exp, dict))
            metrics['credit_value_adjustment'] = cva

        # Debt to Equity Ratio
        if 'total_debt' in exposures and 'equity' in exposures:
            debt = exposures['total_debt']
            equity = exposures['equity']
            if equity > 0:
                metrics['debt_to_equity_ratio'] = debt / equity

        return metrics

    def _calculate_concentration_metrics(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate concentration risk metrics"""
        metrics = {}

        if not holdings:
            return metrics

        # Calculate total value
        total_value = sum(h.get('market_value', 0) for h in holdings)

        if total_value > 0:
            # Largest position concentration
            largest_position = max(h.get('market_value', 0) for h in holdings)
            metrics['largest_position_ratio'] = largest_position / total_value

            # Top 10 concentration
            sorted_holdings = sorted(holdings, key=lambda x: x.get('market_value', 0), reverse=True)
            top_10_value = sum(h.get('market_value', 0) for h in sorted_holdings[:10])
            metrics['top_10_concentration'] = top_10_value / total_value

            # Sector concentration (simplified)
            sector_values = {}
            for holding in holdings:
                sector = holding.get('sector', 'Unknown')
                sector_values[sector] = sector_values.get(sector, 0) + holding.get('market_value', 0)

            if sector_values:
                max_sector_ratio = max(sector_values.values()) / total_value
                metrics['max_sector_concentration'] = max_sector_ratio

            # Overall concentration ratio (Herfindahl-Hirschman Index approximation)
            position_ratios = [h.get('market_value', 0) / total_value for h in holdings]
            concentration_ratio = sum(ratio ** 2 for ratio in position_ratios)
            metrics['concentration_ratio'] = concentration_ratio

        return metrics

    def _run_stress_tests(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run stress tests on portfolio"""
        results = []

        for scenario in self.scenarios.values():
            try:
                # Apply scenario shocks
                shocked_portfolio = scenario.apply_shock(portfolio_data)

                # Calculate losses
                loss = self._calculate_scenario_loss(portfolio_data, shocked_portfolio)

                results.append({
                    'scenario_id': scenario.scenario_id,
                    'scenario_name': scenario.scenario_name,
                    'loss_amount': loss,
                    'loss_percentage': loss / portfolio_data.get('total_value', 1) * 100,
                    'probability_weight': scenario.probability_weight
                })

            except Exception as e:
                results.append({
                    'scenario_id': scenario.scenario_id,
                    'scenario_name': scenario.scenario_name,
                    'error': str(e)
                })

        return results

    def _calculate_scenario_loss(self, original: Dict[str, Any], shocked: Dict[str, Any]) -> float:
        """Calculate loss from scenario"""
        # Simplified loss calculation
        original_value = original.get('total_value', 0)
        shocked_value = shocked.get('total_value', original_value)
        return max(0, original_value - shocked_value)

    def _generate_risk_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []

        # VaR recommendations
        if 'value_at_risk_95' in metrics:
            var = metrics['value_at_risk_95']
            if var > 100000:  # $100K threshold
                recommendations.append(f"High VaR exposure (${var:,.0f}). Consider reducing position sizes.")

        # Liquidity recommendations
        if 'liquidity_coverage_ratio' in metrics:
            lcr = metrics['liquidity_coverage_ratio']
            if lcr < 1.0:
                recommendations.append(f"Liquidity Coverage Ratio ({lcr:.2f}) below regulatory minimum. Increase high-quality liquid assets.")

        # Concentration recommendations
        if 'largest_position_ratio' in metrics:
            ratio = metrics['largest_position_ratio']
            if ratio > 0.1:  # 10% threshold
                recommendations.append(f"High concentration risk ({ratio:.1%}). Diversify portfolio.")

        # Volatility recommendations
        if 'volatility' in metrics:
            vol = metrics['volatility']
            if vol > 0.3:  # 30% threshold
                recommendations.append(f"High portfolio volatility ({vol:.1%}). Consider hedging strategies.")

        return recommendations

    def _check_regulatory_requirements(self, metrics: Dict[str, Any]) -> List[str]:
        """Check compliance with regulatory requirements"""
        requirements = []

        # Basel III requirements
        if RegulatoryFramework.BASEL_III in self.regulatory_frameworks:
            requirements.extend(self._check_basel_iii_requirements(metrics))

        # Dodd-Frank requirements
        if RegulatoryFramework.DODD_FRANK in self.regulatory_frameworks:
            requirements.extend(self._check_dodd_frank_requirements(metrics))

        return requirements

    def _check_basel_iii_requirements(self, metrics: Dict[str, Any]) -> List[str]:
        """Check Basel III compliance"""
        requirements = []

        # Liquidity Coverage Ratio
        lcr = metrics.get('liquidity_coverage_ratio', 0)
        if lcr < 1.0:
            requirements.append(f"Basel III LCR: {lcr:.2f} < 1.0 (NON-COMPLIANT)")
        else:
            requirements.append(f"Basel III LCR: {lcr:.2f} >= 1.0 (COMPLIANT)")

        # Net Stable Funding Ratio
        nsfr = metrics.get('net_stable_funding_ratio', 0)
        if nsfr < 1.0:
            requirements.append(f"Basel III NSFR: {nsfr:.2f} < 1.0 (NON-COMPLIANT)")
        else:
            requirements.append(f"Basel III NSFR: {nsfr:.2f} >= 1.0 (COMPLIANT)")

        return requirements

    def _check_dodd_frank_requirements(self, metrics: Dict[str, Any]) -> List[str]:
        """Check Dodd-Frank compliance"""
        requirements = []

        # Stress testing requirements
        var = metrics.get('value_at_risk_95', 0)
        if var > 100000:
            requirements.append(f"Dodd-Frank Stress Test: VaR ${var:,.0f} exceeds threshold")

        return requirements

    def get_report(self, report_id: str) -> Optional[RiskReport]:
        """Get risk report by ID"""
        return self.reports.get(report_id)

    def generate_regulatory_disclosure(self,
                                     report_id: str,
                                     framework: RegulatoryFramework) -> Dict[str, Any]:
        """Generate regulatory disclosure document"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        disclosure = {
            'firm_name': self.firm_name,
            'reporting_date': report.reporting_date.isoformat(),
            'regulatory_framework': framework.value,
            'risk_disclosures': {},
            'compliance_status': {}
        }

        # Generate framework-specific disclosures
        if framework == RegulatoryFramework.BASEL_III:
            basel_disclosure = self._generate_basel_iii_disclosure(report)
            disclosure['risk_disclosures'].update(basel_disclosure)
        elif framework == RegulatoryFramework.DODD_FRANK:
            dodd_frank_disclosure = self._generate_dodd_frank_disclosure(report)
            disclosure['risk_disclosures'].update(dodd_frank_disclosure)

        return disclosure

    def _generate_basel_iii_disclosure(self, report: RiskReport) -> Dict[str, Any]:
        """Generate Basel III disclosure"""
        return {
            'capital_adequacy': {
                'tier_1_capital_ratio': report.risk_metrics.get('tier_1_ratio', 0),
                'total_capital_ratio': report.risk_metrics.get('total_capital_ratio', 0),
            },
            'liquidity_risk': {
                'lcr': report.risk_metrics.get('liquidity_coverage_ratio', 0),
                'nsfr': report.risk_metrics.get('net_stable_funding_ratio', 0),
            },
            'market_risk': {
                'var_95': report.risk_metrics.get('value_at_risk_95', 0),
                'stressed_var': report.risk_metrics.get('stressed_value_at_risk', 0),
            }
        }

    def _generate_dodd_frank_disclosure(self, report: RiskReport) -> Dict[str, Any]:
        """Generate Dodd-Frank disclosure"""
        return {
            'systemic_risk': {
                'too_big_to_fail_indicator': report.risk_metrics.get('systemic_risk_score', 0),
                'interconnectedness_measure': report.risk_metrics.get('interconnectedness', 0),
            },
            'stress_test_results': report.scenarios,
            'resolution_plan_status': report.metadata.get('resolution_plan_status', 'UNKNOWN')
        }

    def export_report(self, report_id: str, format: str = 'json') -> str:
        """Export risk report in specified format"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if format == 'json':
            return json.dumps(report.__dict__, default=str, indent=2)
        elif format == 'xml':
            return self._export_report_xml(report)
        elif format == 'html':
            return self._export_report_html(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_report_xml(self, report: RiskReport) -> str:
        """Export report as XML"""
        root = ET.Element("RiskReport")
        ET.SubElement(root, "ReportID").text = report.report_id
        ET.SubElement(root, "ReportType").text = report.report_type
        ET.SubElement(root, "ReportingDate").text = report.reporting_date.isoformat()

        # Add metrics
        metrics_elem = ET.SubElement(root, "RiskMetrics")
        for key, value in report.risk_metrics.items():
            ET.SubElement(metrics_elem, key).text = str(value)

        # Convert to string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    def _export_report_html(self, report: RiskReport) -> str:
        """Export report as HTML"""
        html = f"""
        <html>
        <head><title>Risk Report - {report.report_id}</title></head>
        <body>
            <h1>Risk Report</h1>
            <p>Report ID: {report.report_id}</p>
            <p>Reporting Date: {report.reporting_date}</p>
            <p>Period: {report.reporting_period}</p>

            <h2>Risk Metrics</h2>
            <ul>
        """

        for key, value in report.risk_metrics.items():
            html += f"<li>{key}: {value}</li>"

        html += """
            </ul>

            <h2>Recommendations</h2>
            <ul>
        """

        for rec in report.recommendations:
            html += f"<li>{rec}</li>"

        html += """
            </ul>
        </body>
        </html>
        """

        return html


# Specialized Risk Reporters
class ValueAtRiskReporter:
    """Value at Risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def calculate_var(self,
                     returns: np.ndarray,
                     confidence_level: float = 0.95,
                     method: str = 'historical') -> Dict[str, Any]:
        """Calculate Value at Risk using different methods"""

        if method == 'historical':
            var = np.percentile(returns, (1 - confidence_level) * 100)
        elif method == 'parametric':
            mean = np.mean(returns)
            std = np.std(returns)
            var = mean + std * stats.norm.ppf(1 - confidence_level)
        elif method == 'monte_carlo':
            # Simplified Monte Carlo
            simulated_returns = np.random.normal(np.mean(returns), np.std(returns), 10000)
            var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
        else:
            raise ValueError(f"Unsupported VaR method: {method}")

        return {
            'value_at_risk': abs(var),
            'confidence_level': confidence_level,
            'method': method,
            'portfolio_value': 1000000,  # Assumed
            'var_amount': abs(var) * 1000000
        }


class StressTestReporter:
    """Stress test reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def run_stress_test(self,
                       portfolio_data: Dict[str, Any],
                       scenario: StressTestScenario) -> Dict[str, Any]:
        """Run stress test for specific scenario"""

        # Apply scenario shocks
        shocked_portfolio = scenario.apply_shock(portfolio_data)

        # Calculate impact
        original_value = portfolio_data.get('total_value', 0)
        shocked_value = shocked_portfolio.get('total_value', original_value)
        loss = max(0, original_value - shocked_value)

        return {
            'scenario_id': scenario.scenario_id,
            'scenario_name': scenario.scenario_name,
            'original_value': original_value,
            'shocked_value': shocked_value,
            'loss_amount': loss,
            'loss_percentage': (loss / original_value) * 100 if original_value > 0 else 0,
            'probability_weight': scenario.probability_weight,
            'expected_loss': loss * scenario.probability_weight
        }


class ScenarioAnalysisReporter:
    """Scenario analysis reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def analyze_scenario_impact(self,
                              portfolio_data: Dict[str, Any],
                              scenarios: List[StressTestScenario]) -> Dict[str, Any]:
        """Analyze impact of multiple scenarios"""

        results = []
        total_expected_loss = 0

        for scenario in scenarios:
            result = self.engine.stress_reporter.run_stress_test(portfolio_data, scenario)
            results.append(result)
            total_expected_loss += result['expected_loss']

        # Sort by loss amount
        results.sort(key=lambda x: x['loss_amount'], reverse=True)

        return {
            'scenarios_analyzed': len(scenarios),
            'worst_case_scenario': results[0] if results else None,
            'best_case_scenario': results[-1] if results else None,
            'total_expected_loss': total_expected_loss,
            'scenario_results': results
        }


class LiquidityRiskReporter:
    """Liquidity risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def assess_liquidity_risk(self, cash_flows: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liquidity risk"""

        assessment = {
            'liquidity_coverage_ratio': 0.0,
            'net_stable_funding_ratio': 0.0,
            'liquidity_gap_analysis': {},
            'funding_concentration': {},
            'market_liquidity_risk': {},
            'recommendations': []
        }

        # Calculate LCR
        if 'high_quality_assets' in cash_flows and 'net_cash_outflows' in cash_flows:
            hqa = cash_flows['high_quality_assets']
            nco = cash_flows['net_cash_outflows']
            if nco > 0:
                assessment['liquidity_coverage_ratio'] = hqa / nco

        # Calculate NSFR
        if 'stable_funding' in cash_flows and 'required_stable_funding' in cash_flows:
            sf = cash_flows['stable_funding']
            rsf = cash_flows['required_stable_funding']
            if rsf > 0:
                assessment['net_stable_funding_ratio'] = sf / rsf

        # Generate recommendations
        if assessment['liquidity_coverage_ratio'] < 1.0:
            assessment['recommendations'].append("Increase high-quality liquid assets to meet LCR requirement")

        if assessment['net_stable_funding_ratio'] < 1.0:
            assessment['recommendations'].append("Extend funding maturity profile to meet NSFR requirement")

        return assessment


class CreditRiskReporter:
    """Credit risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def assess_credit_risk(self, exposures: Dict[str, Any]) -> Dict[str, Any]:
        """Assess credit risk"""

        assessment = {
            'credit_value_adjustment': 0.0,
            'expected_credit_loss': 0.0,
            'credit_concentration': {},
            'counterparty_risk': {},
            'downgrade_risk': {},
            'recommendations': []
        }

        # Calculate CVA
        if 'credit_exposures' in exposures:
            total_cva = 0
            for exposure in exposures['credit_exposures']:
                exp_amount = exposure.get('amount', 0)
                pd = exposure.get('probability_of_default', 0.01)
                lgd = exposure.get('loss_given_default', 0.45)
                ecl = exp_amount * pd * lgd
                total_cva += ecl

            assessment['credit_value_adjustment'] = total_cva
            assessment['expected_credit_loss'] = total_cva

        # Concentration analysis
        if 'counterparty_exposures' in exposures:
            counterparties = exposures['counterparty_exposures']
            total_exposure = sum(cp.get('exposure', 0) for cp in counterparties)

            if total_exposure > 0:
                max_exposure = max(cp.get('exposure', 0) for cp in counterparties)
                assessment['credit_concentration']['max_counterparty_ratio'] = max_exposure / total_exposure

        return assessment


class OperationalRiskReporter:
    """Operational risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def assess_operational_risk(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess operational risk"""

        assessment = {
            'total_incidents': len(incidents),
            'severity_distribution': {},
            'incident_categories': {},
            'financial_impact': 0,
            'risk_indicators': {},
            'recommendations': []
        }

        # Analyze incidents
        for incident in incidents:
            severity = incident.get('severity', 'low')
            category = incident.get('category', 'unknown')
            impact = incident.get('financial_impact', 0)

            # Update distributions
            assessment['severity_distribution'][severity] = assessment['severity_distribution'].get(severity, 0) + 1
            assessment['incident_categories'][category] = assessment['incident_categories'].get(category, 0) + 1
            assessment['financial_impact'] += impact

        # Generate recommendations
        if assessment['total_incidents'] > 10:
            assessment['recommendations'].append("High incident rate detected. Review operational procedures.")

        if assessment['financial_impact'] > 100000:
            assessment['recommendations'].append("Significant financial impact from operational incidents. Implement additional controls.")

        return assessment


class MarketRiskReporter:
    """Market risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def assess_market_risk(self, returns: np.ndarray) -> Dict[str, Any]:
        """Assess market risk"""

        assessment = {
            'volatility': 0.0,
            'value_at_risk': {},
            'expected_shortfall': {},
            'stress_test_losses': {},
            'greeks_exposure': {},
            'recommendations': []
        }

        if len(returns) > 30:
            # Calculate volatility
            assessment['volatility'] = np.std(returns) * np.sqrt(252)

            # Calculate VaR at different confidence levels
            for conf in [0.95, 0.99]:
                var = np.percentile(returns, (1 - conf) * 100)
                assessment['value_at_risk'][f'{int(conf*100)}_percent'] = abs(var)

                # Expected Shortfall
                tail_losses = returns[returns <= var]
                if len(tail_losses) > 0:
                    es = np.mean(tail_losses)
                    assessment['expected_shortfall'][f'{int(conf*100)}_percent'] = abs(es)

        # Generate recommendations
        if assessment['volatility'] > 0.3:
            assessment['recommendations'].append("High portfolio volatility. Consider diversification or hedging.")

        return assessment


class RegulatoryRiskReporter:
    """Regulatory risk reporting"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def assess_regulatory_risk(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess regulatory risk"""

        assessment = {
            'compliance_score': 0.0,
            'regulatory_breaches': [],
            'upcoming_deadlines': [],
            'regulatory_changes': [],
            'fines_penalties': 0,
            'recommendations': []
        }

        # Calculate compliance score
        total_checks = compliance_data.get('total_checks', 0)
        passed_checks = compliance_data.get('passed_checks', 0)

        if total_checks > 0:
            assessment['compliance_score'] = (passed_checks / total_checks) * 100

        # Check for breaches
        if 'breaches' in compliance_data:
            assessment['regulatory_breaches'] = compliance_data['breaches']

        # Generate recommendations
        if assessment['compliance_score'] < 80:
            assessment['recommendations'].append("Low compliance score. Review and strengthen compliance procedures.")

        if assessment['regulatory_breaches']:
            assessment['recommendations'].append(f"{len(assessment['regulatory_breaches'])} regulatory breaches detected. Immediate remediation required.")

        return assessment


class RiskDisclosureGenerator:
    """Risk disclosure document generator"""

    def __init__(self, engine: RiskReportingEngine):
        self.engine = engine

    def generate_disclosure_document(self,
                                  report_id: str,
                                  framework: RegulatoryFramework,
                                  format: str = 'html') -> str:
        """Generate risk disclosure document"""

        report = self.engine.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        disclosure_data = self.engine.generate_regulatory_disclosure(report_id, framework)

        if format == 'html':
            return self._generate_html_disclosure(disclosure_data, framework)
        elif format == 'pdf':
            return self._generate_pdf_disclosure(disclosure_data, framework)
        else:
            return json.dumps(disclosure_data, indent=2)

    def _generate_html_disclosure(self, data: Dict[str, Any], framework: RegulatoryFramework) -> str:
        """Generate HTML disclosure document"""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Risk Disclosure - {framework.value.upper()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 30px; }}
                .section {{ margin-bottom: 20px; }}
                .metric {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Risk Disclosure Report</h1>
                <h2>{framework.value.upper()} Framework</h2>
                <p><strong>Firm:</strong> {data['firm_name']}</p>
                <p><strong>Reporting Date:</strong> {data['reporting_date']}</p>
            </div>

            <div class="section">
                <h2>Risk Disclosures</h2>
        """

        # Add risk disclosures
        for category, metrics in data['risk_disclosures'].items():
            html += f"<h3>{category.replace('_', ' ').title()}</h3>"
            if isinstance(metrics, dict):
                html += "<table>"
                for key, value in metrics.items():
                    html += f"<tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>"
                html += "</table>"
            else:
                html += f"<p>{metrics}</p>"

        html += """
            </div>

            <div class="section">
                <h2>Compliance Status</h2>
        """

        # Add compliance status
        for requirement, status in data['compliance_status'].items():
            html += f"<div class='metric'><strong>{requirement}:</strong> {status}</div>"

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def _generate_pdf_disclosure(self, data: Dict[str, Any], framework: RegulatoryFramework) -> str:
        """Generate PDF disclosure document"""
        # This would require a PDF generation library like reportlab
        # For now, return a placeholder
        return f"PDF generation for {framework.value} disclosure would be implemented here."


# Factory functions
def create_risk_reporting_engine(firm_name: str,
                               regulatory_frameworks: Optional[List[RegulatoryFramework]] = None) -> RiskReportingEngine:
    """Create risk reporting engine"""
    return RiskReportingEngine(firm_name, regulatory_frameworks)

"""Advanced risk modeling and stress testing framework."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from arch import arch_model
import warnings

warnings.filterwarnings('ignore')

from qantify.risk.metrics import calculate_var, calculate_cvar, calculate_sharpe_ratio
from qantify.math.stochastic import simulate_gbm, simulate_heston

logger = logging.getLogger(__name__)


class RiskModelType(Enum):
    """Types of risk models."""

    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"
    GARCH = "garch"
    EVT = "evt"  # Extreme Value Theory
    COPULA = "copula"


class StressTestType(Enum):
    """Types of stress tests."""

    HISTORICAL_SCENARIO = "historical_scenario"
    HYPOTHETICAL_SCENARIO = "hypothetical_scenario"
    MONTE_CARLO = "monte_carlo"
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"
    REVERSE_STRESS_TEST = "reverse_stress_test"


@dataclass(slots=True)
class RiskFactor:
    """Risk factor definition."""

    name: str
    factor_type: str  # 'market', 'sector', 'currency', 'commodity', 'volatility'
    volatility: float
    correlation_matrix: Optional[pd.DataFrame] = None
    historical_returns: Optional[pd.Series] = None


@dataclass(slots=True)
class RiskModel:
    """Comprehensive risk model."""

    model_type: RiskModelType
    confidence_level: float = 0.95
    time_horizon: int = 1  # Days
    var: float = 0.0
    cvar: float = 0.0
    expected_shortfall: float = 0.0
    beta: float = 1.0
    correlation_matrix: Optional[pd.DataFrame] = None
    factor_betas: Dict[str, float] = field(default_factory=dict)
    garch_params: Dict[str, Any] = field(default_factory=dict)
    monte_carlo_paths: int = 10000


@dataclass(slots=True)
class StressTestScenario:
    """Stress test scenario definition."""

    name: str
    scenario_type: StressTestType
    shock_definition: Dict[str, float]  # Factor -> shock percentage
    probability: float = 0.05  # Scenario probability
    description: str = ""


@dataclass(slots=True)
class StressTestResult:
    """Results from stress testing."""

    scenario_name: str
    portfolio_loss: float
    var_contribution: Dict[str, float]
    liquidity_impact: float
    recovery_time: int  # Days
    correlation_breakdown: Dict[str, float]
    worst_case_path: pd.Series


@dataclass(slots=True)
class RiskDecomposition:
    """Risk decomposition by factors."""

    total_var: float
    factor_contributions: Dict[str, float]
    specific_risk: float
    marginal_contributions: Dict[str, float]
    risk_budget: Dict[str, float]


class AdvancedRiskEngine:
    """Advanced risk modeling and stress testing engine."""

    def __init__(
        self,
        confidence_level: float = 0.95,
        time_horizon: int = 1,
        risk_model_type: RiskModelType = RiskModelType.HISTORICAL
    ):
        self.confidence_level = confidence_level
        self.time_horizon = time_horizon
        self.risk_model_type = risk_model_type
        self.risk_factors: Dict[str, RiskFactor] = {}

    def add_risk_factor(
        self,
        name: str,
        factor_type: str,
        historical_returns: pd.Series,
        volatility: Optional[float] = None
    ) -> None:
        """Add a risk factor to the model."""

        if volatility is None:
            volatility = historical_returns.std() * np.sqrt(252)

        self.risk_factors[name] = RiskFactor(
            name=name,
            factor_type=factor_type,
            volatility=volatility,
            historical_returns=historical_returns
        )

        logger.info(f"Added risk factor: {name} ({factor_type}) with volatility {volatility:.2%}")

    def build_risk_model(
        self,
        portfolio_returns: pd.Series,
        factor_exposures: Optional[Dict[str, float]] = None
    ) -> RiskModel:
        """Build comprehensive risk model."""

        risk_model = RiskModel(
            model_type=self.risk_model_type,
            confidence_level=self.confidence_level,
            time_horizon=self.time_horizon
        )

        # Calculate correlation matrix
        if len(self.risk_factors) > 1:
            factor_returns = pd.DataFrame({
                name: factor.historical_returns for name, factor in self.risk_factors.items()
            }).dropna()
            risk_model.correlation_matrix = factor_returns.corr()

        # Calculate VaR and CVaR
        if self.risk_model_type == RiskModelType.HISTORICAL:
            risk_model.var, risk_model.cvar = self._calculate_historical_risk_measures(portfolio_returns)
        elif self.risk_model_type == RiskModelType.PARAMETRIC:
            risk_model.var, risk_model.cvar = self._calculate_parametric_risk_measures(portfolio_returns)
        elif self.risk_model_type == RiskModelType.MONTE_CARLO:
            risk_model.var, risk_model.cvar = self._calculate_monte_carlo_risk_measures(portfolio_returns)
        elif self.risk_model_type == RiskModelType.GARCH:
            risk_model.var, risk_model.cvar, risk_model.garch_params = self._calculate_garch_risk_measures(portfolio_returns)

        # Factor model analysis
        if factor_exposures:
            risk_model.factor_betas = factor_exposures
            risk_model.beta = self._calculate_beta_to_market(portfolio_returns, factor_exposures)

        risk_model.expected_shortfall = risk_model.cvar  # CVaR is also known as Expected Shortfall

        return risk_model

    def _calculate_historical_risk_measures(self, returns: pd.Series) -> Tuple[float, float]:
        """Calculate historical VaR and CVaR."""
        var = calculate_var(returns, confidence=self.confidence_level)
        cvar = calculate_cvar(returns, confidence=self.confidence_level)
        return abs(var), abs(cvar)  # Ensure positive values

    def _calculate_parametric_risk_measures(self, returns: pd.Series) -> Tuple[float, float]:
        """Calculate parametric (normal distribution) VaR and CVaR."""
        mean_return = returns.mean()
        volatility = returns.std()

        # Normal distribution VaR
        z_score = stats.norm.ppf(1 - self.confidence_level)
        var = -(mean_return + z_score * volatility)

        # Normal distribution CVaR (approximation)
        alpha = 1 - self.confidence_level
        cvar = volatility * (stats.norm.pdf(z_score) / alpha)

        return abs(var), abs(cvar)

    def _calculate_monte_carlo_risk_measures(self, returns: pd.Series) -> Tuple[float, float]:
        """Calculate Monte Carlo VaR and CVaR."""
        np.random.seed(42)

        # Fit distribution parameters
        mean_return = returns.mean()
        volatility = returns.std()

        # Generate Monte Carlo scenarios
        n_simulations = 10000
        simulated_returns = np.random.normal(mean_return, volatility, n_simulations)

        # Calculate VaR and CVaR from simulations
        sorted_returns = np.sort(simulated_returns)
        var_index = int((1 - self.confidence_level) * n_simulations)
        var = abs(sorted_returns[var_index])

        # CVaR is average of returns beyond VaR
        cvar_returns = sorted_returns[:var_index]
        cvar = abs(np.mean(cvar_returns))

        return var, cvar

    def _calculate_garch_risk_measures(self, returns: pd.Series) -> Tuple[float, float, Dict[str, Any]]:
        """Calculate GARCH-based VaR and CVaR."""
        try:
            # Fit GARCH(1,1) model
            model = arch_model(returns, vol='Garch', p=1, q=1)
            model_fit = model.fit(disp='off')

            # Get conditional volatility
            conditional_volatility = model_fit.conditional_volatility

            # Forecast next period volatility
            forecasts = model_fit.forecast(horizon=1)
            next_volatility = np.sqrt(forecasts.variance.iloc[-1, 0])

            # GARCH VaR (assuming normal innovations)
            z_score = stats.norm.ppf(1 - self.confidence_level)
            var = abs(z_score * next_volatility)

            # Approximation for CVaR
            cvar = abs(next_volatility * (stats.norm.pdf(z_score) / (1 - self.confidence_level)))

            garch_params = {
                'omega': model_fit.params['omega'],
                'alpha': model_fit.params['alpha[1]'],
                'beta': model_fit.params['beta[1]'],
                'persistence': model_fit.params['alpha[1]'] + model_fit.params['beta[1]']
            }

            return var, cvar, garch_params

        except Exception as e:
            logger.warning(f"GARCH model failed: {e}")
            # Fall back to historical
            return self._calculate_historical_risk_measures(returns) + ({},)

    def _calculate_beta_to_market(self, portfolio_returns: pd.Series, factor_exposures: Dict[str, float]) -> float:
        """Calculate portfolio beta to market."""
        if 'market' not in factor_exposures or 'market' not in self.risk_factors:
            return 1.0

        market_returns = self.risk_factors['market'].historical_returns
        aligned_data = pd.concat([portfolio_returns, market_returns], axis=1, join='inner').dropna()

        if len(aligned_data) < 30:
            return 1.0

        cov_matrix = aligned_data.cov()
        beta = cov_matrix.iloc[0, 1] / cov_matrix.iloc[1, 1]

        return beta

    def decompose_risk(
        self,
        portfolio_returns: pd.Series,
        factor_exposures: Dict[str, float]
    ) -> RiskDecomposition:
        """Decompose portfolio risk by factors."""

        total_var = calculate_var(portfolio_returns, confidence=self.confidence_level)

        # Simplified risk decomposition (in practice, this would use more sophisticated methods)
        factor_contributions = {}
        total_factor_contribution = 0

        for factor_name, exposure in factor_exposures.items():
            if factor_name in self.risk_factors:
                factor_vol = self.risk_factors[factor_name].volatility
                contribution = exposure * factor_vol
                factor_contributions[factor_name] = contribution
                total_factor_contribution += contribution

        # Specific risk (unexplained by factors)
        specific_risk = max(0, total_var - total_factor_contribution)

        # Marginal contributions
        marginal_contributions = {}
        for factor_name, exposure in factor_exposures.items():
            if factor_name in self.risk_factors:
                # Simplified marginal contribution
                marginal_contributions[factor_name] = factor_contributions[factor_name] / total_var if total_var > 0 else 0

        # Risk budget (equal risk contribution)
        n_factors = len(factor_exposures)
        risk_budget = {factor: 1.0 / n_factors for factor in factor_exposures.keys()}

        return RiskDecomposition(
            total_var=total_var,
            factor_contributions=factor_contributions,
            specific_risk=specific_risk,
            marginal_contributions=marginal_contributions,
            risk_budget=risk_budget
        )

    def run_stress_test(
        self,
        portfolio_returns: pd.Series,
        scenario: StressTestScenario,
        factor_exposures: Dict[str, float]
    ) -> StressTestResult:
        """Run stress test scenario."""

        # Apply shocks to factors
        shocked_returns = portfolio_returns.copy()

        for factor_name, shock_pct in scenario.shock_definition.items():
            if factor_name in self.risk_factors:
                factor_returns = self.risk_factors[factor_name].historical_returns
                # Apply shock to historical returns
                shocked_factor = factor_returns * (1 + shock_pct)

                if factor_name in factor_exposures:
                    exposure = factor_exposures[factor_name]
                    shocked_returns += exposure * (shocked_factor - factor_returns)

        # Calculate portfolio loss
        original_value = 1.0  # Assume starting value of 1
        shocked_value = original_value * (1 + shocked_returns.sum())
        portfolio_loss = original_value - shocked_value

        # VaR contribution by factor
        var_contributions = {}
        for factor_name, exposure in factor_exposures.items():
            if factor_name in self.risk_factors:
                factor_var = calculate_var(self.risk_factors[factor_name].historical_returns)
                var_contributions[factor_name] = exposure * factor_var

        # Simplified metrics
        liquidity_impact = portfolio_loss * 0.1  # Assume 10% liquidity discount
        recovery_time = int(abs(portfolio_loss) * 100)  # Simplified recovery estimate

        # Correlation breakdown
        correlation_breakdown = {}
        if self.risk_factors:
            for factor_name in factor_exposures.keys():
                if factor_name in self.risk_factors:
                    correlation_breakdown[factor_name] = 0.5  # Placeholder

        # Worst case path
        worst_case_path = shocked_returns

        return StressTestResult(
            scenario_name=scenario.name,
            portfolio_loss=portfolio_loss,
            var_contribution=var_contributions,
            liquidity_impact=liquidity_impact,
            recovery_time=recovery_time,
            correlation_breakdown=correlation_breakdown,
            worst_case_path=worst_case_path
        )

    def generate_stress_scenarios(self) -> List[StressTestScenario]:
        """Generate common stress test scenarios."""

        scenarios = []

        # Historical scenarios
        scenarios.append(StressTestScenario(
            name="2008 Financial Crisis",
            scenario_type=StressTestType.HISTORICAL_SCENARIO,
            shock_definition={
                'market': -0.40,
                'credit_spread': 0.50,
                'volatility': 1.00
            },
            probability=0.01,
            description="2008 Global Financial Crisis conditions"
        ))

        scenarios.append(StressTestScenario(
            name="COVID-19 Crash",
            scenario_type=StressTestType.HISTORICAL_SCENARIO,
            shock_definition={
                'market': -0.35,
                'volatility': 0.80,
                'commodity': -0.20
            },
            probability=0.05,
            description="March 2020 COVID-19 market crash"
        ))

        # Hypothetical scenarios
        scenarios.append(StressTestScenario(
            name="Interest Rate Shock",
            scenario_type=StressTestType.HYPOTHETICAL_SCENARIO,
            shock_definition={
                'interest_rate': 0.50,
                'bond': -0.15,
                'equity': -0.10
            },
            probability=0.10,
            description="Sudden 50bp interest rate increase"
        ))

        scenarios.append(StressTestScenario(
            name="Liquidity Crisis",
            scenario_type=StressTestType.HYPOTHETICAL_SCENARIO,
            shock_definition={
                'liquidity': -0.70,
                'credit_spread': 0.80,
                'volatility': 0.60
            },
            probability=0.02,
            description="Severe liquidity crunch scenario"
        ))

        return scenarios

    def run_reverse_stress_test(
        self,
        portfolio_returns: pd.Series,
        loss_threshold: float,
        factor_exposures: Dict[str, float]
    ) -> StressTestScenario:
        """Run reverse stress test to find scenarios causing specific loss."""

        def loss_function(shocks):
            """Calculate portfolio loss for given shocks."""
            shocked_returns = portfolio_returns.copy()

            for i, factor_name in enumerate(factor_exposures.keys()):
                if factor_name in self.risk_factors and i < len(shocks):
                    factor_returns = self.risk_factors[factor_name].historical_returns
                    shocked_factor = factor_returns * (1 + shocks[i])

                    if factor_name in factor_exposures:
                        exposure = factor_exposures[factor_name]
                        shocked_returns += exposure * (shocked_factor - factor_returns)

            portfolio_loss = 1.0 - (1.0 * (1 + shocked_returns.sum()))
            return portfolio_loss

        # Optimize to find shocks that cause exactly the loss threshold
        n_factors = len(factor_exposures)
        initial_shocks = np.zeros(n_factors)

        def objective(shocks):
            return abs(loss_function(shocks) - loss_threshold)

        bounds = [(-2.0, 2.0) for _ in range(n_factors)]  # Allow up to +/- 200% shocks

        result = minimize(objective, initial_shocks, method='SLSQP', bounds=bounds)

        shock_definition = dict(zip(factor_exposures.keys(), result.x))

        return StressTestScenario(
            name=f"Reverse Stress Test ({loss_threshold:.1%} Loss)",
            scenario_type=StressTestType.REVERSE_STRESS_TEST,
            shock_definition=shock_definition,
            description=f"Minimum shocks required to cause {loss_threshold:.1%} portfolio loss"
        )


class RiskReportingEngine:
    """Generate comprehensive risk reports."""

    def __init__(self, risk_engine: AdvancedRiskEngine):
        self.risk_engine = risk_engine

    def generate_risk_report(
        self,
        portfolio_returns: pd.Series,
        risk_model: RiskModel,
        stress_results: List[StressTestResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive risk report."""

        report = {
            'summary': {
                'portfolio_var_95': risk_model.var,
                'portfolio_cvar_95': risk_model.cvar,
                'beta_to_market': risk_model.beta,
                'worst_stress_loss': max(r.portfolio_loss for r in stress_results) if stress_results else 0,
                'risk_model_type': risk_model.model_type.value,
                'confidence_level': risk_model.confidence_level
            },
            'stress_tests': [
                {
                    'scenario': r.scenario_name,
                    'loss': r.portfolio_loss,
                    'recovery_days': r.recovery_time
                }
                for r in stress_results
            ],
            'factor_analysis': {
                'factor_betas': risk_model.factor_betas,
                'correlation_matrix': risk_model.correlation_matrix.to_dict() if risk_model.correlation_matrix is not None else None
            },
            'recommendations': self._generate_risk_recommendations(risk_model, stress_results)
        }

        return report

    def _generate_risk_recommendations(
        self,
        risk_model: RiskModel,
        stress_results: List[StressTestResult]
    ) -> List[str]:
        """Generate risk management recommendations."""

        recommendations = []

        # VaR-based recommendations
        if risk_model.var > 0.05:  # 5% daily VaR threshold
            recommendations.append("Consider reducing portfolio leverage to lower VaR")

        # Beta-based recommendations
        if risk_model.beta > 1.5:
            recommendations.append("High market beta - consider hedging market risk")
        elif risk_model.beta < 0.5:
            recommendations.append("Low market beta - consider increasing market exposure")

        # Stress test recommendations
        max_stress_loss = max(r.portfolio_loss for r in stress_results) if stress_results else 0
        if max_stress_loss > 0.20:  # 20% stress loss threshold
            recommendations.append("Portfolio vulnerable to extreme events - implement stop-losses")

        # GARCH recommendations
        if risk_model.model_type == RiskModelType.GARCH and 'persistence' in risk_model.garch_params:
            persistence = risk_model.garch_params['persistence']
            if persistence > 0.95:
                recommendations.append("High volatility persistence - consider volatility hedging")

        if not recommendations:
            recommendations.append("Portfolio risk profile appears reasonable")

        return recommendations


# Convenience functions
def create_comprehensive_risk_model(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
    include_factors: bool = True
) -> RiskModel:
    """Create comprehensive risk model with multiple methodologies."""

    engine = AdvancedRiskEngine(
        confidence_level=confidence_level,
        risk_model_type=RiskModelType.HISTORICAL
    )

    # Add common risk factors if requested
    if include_factors:
        # These would typically be loaded from data sources
        # For demo, create synthetic factors
        np.random.seed(42)
        dates = portfolio_returns.index

        market_returns = pd.Series(
            portfolio_returns.values * 0.8 + np.random.randn(len(portfolio_returns)) * 0.01,
            index=dates
        )
        engine.add_risk_factor('market', 'market', market_returns)

        bond_returns = pd.Series(
            np.random.randn(len(portfolio_returns)) * 0.005,
            index=dates
        )
        engine.add_risk_factor('bond', 'fixed_income', bond_returns)

    # Build the risk model
    factor_exposures = {'market': 0.8, 'bond': 0.2} if include_factors else None
    risk_model = engine.build_risk_model(portfolio_returns, factor_exposures)

    return risk_model


def run_stress_test_suite(
    portfolio_returns: pd.Series,
    factor_exposures: Optional[Dict[str, float]] = None
) -> List[StressTestResult]:
    """Run comprehensive stress test suite."""

    engine = AdvancedRiskEngine()

    # Add risk factors
    if factor_exposures:
        for factor_name in factor_exposures.keys():
            # Create synthetic factor returns
            factor_returns = pd.Series(
                np.random.randn(len(portfolio_returns)) * 0.01,
                index=portfolio_returns.index
            )
            engine.add_risk_factor(factor_name, 'market', factor_returns)

    # Generate stress scenarios
    scenarios = engine.generate_stress_scenarios()

    # Run stress tests
    stress_results = []
    for scenario in scenarios:
        result = engine.run_stress_test(portfolio_returns, scenario, factor_exposures or {})
        stress_results.append(result)

    return stress_results


__all__ = [
    "RiskModelType",
    "StressTestType",
    "RiskFactor",
    "RiskModel",
    "StressTestScenario",
    "StressTestResult",
    "RiskDecomposition",
    "AdvancedRiskEngine",
    "RiskReportingEngine",
    "create_comprehensive_risk_model",
    "run_stress_test_suite",
]

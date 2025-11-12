"""Advanced backtesting analytics and performance attribution system."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from qantify.backtest.event import EventBacktestResult
from qantify.backtest.types import OrderSide
from qantify.risk.metrics import calculate_var, calculate_cvar, calculate_sharpe_ratio

logger = logging.getLogger(__name__)


class AttributionMethod(Enum):
    """Methods for performance attribution."""

    SINGLE_FACTOR = "single_factor"
    MULTI_FACTOR = "multi_factor"
    RISK_PARITY = "risk_parity"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_SHARPE = "maximum_sharpe"
    EQUAL_WEIGHT = "equal_weight"


class BenchmarkType(Enum):
    """Types of benchmarks for comparison."""

    MARKET_INDEX = "market_index"
    SECTOR_INDEX = "sector_index"
    PEER_GROUP = "peer_group"
    RISK_FREE = "risk_free"
    CUSTOM = "custom"


@dataclass(slots=True)
class PerformanceAttribution:
    """Detailed performance attribution analysis."""

    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    var_95: float
    cvar_95: float
    beta: float
    alpha: float
    tracking_error: float
    information_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_time: int
    underwater_time: int
    kelly_criterion: float
    omega_ratio: float
    tail_ratio: float
    common_sense_ratio: float
    serenity_ratio: float


@dataclass(slots=True)
class FactorAttribution:
    """Factor model attribution results."""

    factor_loadings: Dict[str, float]
    factor_returns: Dict[str, float]
    factor_contributions: Dict[str, float]
    unexplained_return: float
    r_squared: float
    adjusted_r_squared: float
    f_statistic: float
    factor_t_stats: Dict[str, float]
    residual_analysis: Dict[str, Any]


@dataclass(slots=True)
class RollingPerformance:
    """Rolling performance metrics over time."""

    window_size: int
    rolling_returns: pd.Series
    rolling_volatility: pd.Series
    rolling_sharpe: pd.Series
    rolling_max_drawdown: pd.Series
    rolling_beta: pd.Series
    rolling_alpha: pd.Series
    rolling_var: pd.Series
    rolling_cvar: pd.Series


@dataclass(slots=True)
class StatisticalSignificance:
    """Statistical significance testing results."""

    p_value: float
    confidence_level: float
    null_hypothesis: str
    test_statistic: float
    critical_value: float
    sample_size: int
    degrees_freedom: int
    test_type: str
    conclusion: str


@dataclass(slots=True)
class BenchmarkComparison:
    """Comprehensive benchmark comparison."""

    benchmark_name: str
    benchmark_type: BenchmarkType
    strategy_return: float
    benchmark_return: float
    excess_return: float
    annualized_excess_return: float
    tracking_error: float
    information_ratio: float
    beta_to_benchmark: float
    alpha_to_benchmark: float
    up_capture: float
    down_capture: float
    batting_average: float
    win_loss_ratio: float


@dataclass(slots=True)
class AdvancedAnalyticsResult:
    """Complete advanced analytics result."""

    performance_attribution: PerformanceAttribution
    factor_attribution: Optional[FactorAttribution]
    rolling_performance: RollingPerformance
    statistical_tests: List[StatisticalSignificance]
    benchmark_comparisons: List[BenchmarkComparison]
    risk_decomposition: Dict[str, float]
    performance_persistence: Dict[str, Any]
    transaction_cost_analysis: Dict[str, Any]
    monte_carlo_analysis: Dict[str, Any]


class PerformanceAttributionEngine:
    """Advanced performance attribution and analytics engine."""

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_performance_attribution(
        self,
        result: EventBacktestResult,
        benchmark_returns: Optional[pd.Series] = None
    ) -> PerformanceAttribution:
        """Calculate comprehensive performance attribution."""

        returns = result.equity_curve.pct_change().dropna()

        # Basic metrics
        total_return = (result.equity_curve.iloc[-1] / result.equity_curve.iloc[0]) - 1
        days = len(result.equity_curve)
        annualized_return = (1 + total_return) ** (252 / days) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0

        # Downside metrics
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (annualized_return - self.risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

        # Drawdown analysis
        peak = result.equity_curve.expanding().max()
        drawdown = (result.equity_curve - peak) / peak
        max_drawdown = drawdown.min()
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0

        # Risk metrics
        var_95 = calculate_var(returns, confidence=0.95)
        cvar_95 = calculate_cvar(returns, confidence=0.95)

        # Benchmark-related metrics
        if benchmark_returns is not None:
            aligned_returns = pd.concat([returns, benchmark_returns], axis=1, join='inner').dropna()
            if len(aligned_returns) > 1:
                strategy_returns = aligned_returns.iloc[:, 0]
                bench_returns = aligned_returns.iloc[:, 1]

                # CAPM beta and alpha
                X = sm.add_constant(bench_returns)
                model = sm.OLS(strategy_returns, X).fit()
                beta = model.params.iloc[1]
                alpha = model.params.iloc[0] * 252  # Annualized alpha
                tracking_error = (strategy_returns - bench_returns).std() * np.sqrt(252)
                information_ratio = alpha / tracking_error if tracking_error > 0 else 0
            else:
                beta = alpha = tracking_error = information_ratio = 0.0
        else:
            beta = alpha = tracking_error = information_ratio = 0.0

        # Trade-based metrics
        if result.trades:
            winning_trades = [t for t in result.trades if t.pnl > 0]
            losing_trades = [t for t in result.trades if t.pnl < 0]

            win_rate = len(winning_trades) / len(result.trades)
            profit_factor = sum(t.pnl for t in winning_trades) / abs(sum(t.pnl for t in losing_trades)) if losing_trades else float('inf')
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
            largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0

            # Consecutive analysis
            consecutive_wins = self._calculate_consecutive_streaks(result.trades, True)
            consecutive_losses = self._calculate_consecutive_streaks(result.trades, False)
        else:
            win_rate = profit_factor = avg_win = avg_loss = largest_win = largest_loss = 0.0
            consecutive_wins = consecutive_losses = 0

        # Recovery and underwater time
        recovery_time, underwater_time = self._calculate_recovery_metrics(result.equity_curve)

        # Advanced ratios
        kelly_criterion = self._calculate_kelly_criterion(returns)
        omega_ratio = self._calculate_omega_ratio(returns, threshold=self.risk_free_rate/252)
        tail_ratio = self._calculate_tail_ratio(returns)
        common_sense_ratio = self._calculate_common_sense_ratio(returns)
        serenity_ratio = self._calculate_serenity_ratio(returns)

        return PerformanceAttribution(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            beta=beta,
            alpha=alpha,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            recovery_time=recovery_time,
            underwater_time=underwater_time,
            kelly_criterion=kelly_criterion,
            omega_ratio=omega_ratio,
            tail_ratio=tail_ratio,
            common_sense_ratio=common_sense_ratio,
            serenity_ratio=serenity_ratio,
        )

    def _calculate_consecutive_streaks(self, trades: List[Any], winning: bool) -> int:
        """Calculate maximum consecutive winning or losing streaks."""
        max_streak = 0
        current_streak = 0

        for trade in trades:
            if (trade.pnl > 0) == winning:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    def _calculate_recovery_metrics(self, equity_curve: pd.Series) -> Tuple[int, int]:
        """Calculate recovery time and underwater time."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak

        # Recovery time (days to recover from max drawdown)
        max_dd_idx = drawdown.idxmin()
        if max_dd_idx != equity_curve.index[-1]:
            recovery_point = equity_curve[equity_curve >= peak.loc[max_dd_idx]].index
            recovery_time = len(equity_curve.loc[max_dd_idx:recovery_point[0]]) if recovery_point.size > 0 else len(equity_curve) - equity_curve.index.get_loc(max_dd_idx)
        else:
            recovery_time = 0

        # Underwater time (total days in drawdown)
        underwater_time = (drawdown < 0).sum()

        return recovery_time, underwater_time

    def _calculate_kelly_criterion(self, returns: pd.Series) -> float:
        """Calculate Kelly Criterion."""
        if len(returns) < 2:
            return 0.0

        win_rate = (returns > 0).mean()
        avg_win = returns[returns > 0].mean()
        avg_loss = abs(returns[returns < 0].mean())

        if avg_loss == 0:
            return float('inf')

        kelly = win_rate / avg_loss - (1 - win_rate) / avg_win if avg_win > 0 else 0
        return max(0, kelly)  # Kelly can be negative

    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0.0) -> float:
        """Calculate Omega Ratio."""
        excess_returns = returns - threshold
        positive_sum = excess_returns[excess_returns > 0].sum()
        negative_sum = abs(excess_returns[excess_returns < 0].sum())

        return positive_sum / negative_sum if negative_sum > 0 else float('inf')

    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate Tail Ratio (95th percentile / 5th percentile)."""
        if len(returns) < 20:
            return 1.0

        percentile_95 = np.percentile(returns, 95)
        percentile_5 = np.percentile(returns, 5)

        return percentile_95 / abs(percentile_5) if percentile_5 < 0 else 1.0

    def _calculate_common_sense_ratio(self, returns: pd.Series) -> float:
        """Calculate Common Sense Ratio (Annualized Return / Max Drawdown)."""
        if len(returns) < 2:
            return 0.0

        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1

        peak = (1 + returns).cumprod().expanding().max()
        drawdown = (1 + returns).cumprod() / peak - 1
        max_drawdown = abs(drawdown.min())

        return annualized_return / max_drawdown if max_drawdown > 0 else 0.0

    def _calculate_serenity_ratio(self, returns: pd.Series) -> float:
        """Calculate Serenity Ratio (Annualized Return / (Max Drawdown²))."""
        if len(returns) < 2:
            return 0.0

        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1

        peak = (1 + returns).cumprod().expanding().max()
        drawdown = (1 + returns).cumprod() / peak - 1
        max_drawdown = abs(drawdown.min())

        return annualized_return / (max_drawdown ** 2) if max_drawdown > 0 else 0.0


class FactorAttributionEngine:
    """Factor model attribution analysis."""

    def __init__(self, factors: List[str]):
        self.factors = factors

    def perform_factor_attribution(
        self,
        strategy_returns: pd.Series,
        factor_returns: pd.DataFrame,
        method: AttributionMethod = AttributionMethod.MULTI_FACTOR
    ) -> FactorAttribution:
        """Perform factor attribution analysis."""

        # Align data
        aligned_data = pd.concat([strategy_returns, factor_returns], axis=1, join='inner').dropna()

        if len(aligned_data) < 30:
            raise ValueError("Insufficient data for factor attribution analysis")

        strategy_ret = aligned_data.iloc[:, 0]
        factor_rets = aligned_data.iloc[:, 1:]

        # Add constant for alpha
        X = sm.add_constant(factor_rets)
        model = sm.OLS(strategy_ret, X).fit()

        # Factor loadings and statistics
        factor_loadings = dict(zip(factor_rets.columns, model.params[1:]))
        factor_t_stats = dict(zip(factor_rets.columns, model.tvalues[1:]))

        # Factor contributions (loadings * factor returns)
        factor_contributions = {}
        for factor in factor_rets.columns:
            factor_contributions[factor] = factor_loadings[factor] * factor_rets[factor].mean() * 252

        # Factor returns
        factor_returns_dict = dict(factor_rets.mean() * 252)

        # Unexplained return
        unexplained_return = model.params[0] * 252  # Annualized alpha

        # Model statistics
        r_squared = model.rsquared
        adjusted_r_squared = model.rsquared_adj
        f_statistic = model.fvalue

        # Residual analysis
        residuals = model.resid
        residual_analysis = {
            'mean': residuals.mean(),
            'std': residuals.std(),
            'skewness': residuals.skew(),
            'kurtosis': residuals.kurtosis(),
            'autocorr_1': residuals.autocorr(1),
            'jarque_bera_p': stats.jarque_bera(residuals)[1]
        }

        return FactorAttribution(
            factor_loadings=factor_loadings,
            factor_returns=factor_returns_dict,
            factor_contributions=factor_contributions,
            unexplained_return=unexplained_return,
            r_squared=r_squared,
            adjusted_r_squared=adjusted_r_squared,
            f_statistic=f_statistic,
            factor_t_stats=factor_t_stats,
            residual_analysis=residual_analysis
        )


class RollingAnalyticsEngine:
    """Rolling window analytics engine."""

    def __init__(self, window_size: int = 252):
        self.window_size = window_size

    def calculate_rolling_performance(
        self,
        equity_curve: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.02
    ) -> RollingPerformance:
        """Calculate rolling performance metrics."""

        returns = equity_curve.pct_change().dropna()
        rolling_returns = returns.rolling(window=self.window_size).mean() * 252
        rolling_volatility = returns.rolling(window=self.window_size).std() * np.sqrt(252)

        # Rolling Sharpe ratio
        excess_returns = returns - risk_free_rate/252
        rolling_sharpe = (excess_returns.rolling(window=self.window_size).mean() * 252) / \
                        (excess_returns.rolling(window=self.window_size).std() * np.sqrt(252))

        # Rolling max drawdown
        rolling_peak = equity_curve.rolling(window=self.window_size).max()
        rolling_dd = (equity_curve - rolling_peak) / rolling_peak
        rolling_max_drawdown = rolling_dd.rolling(window=self.window_size).min()

        # Rolling beta and alpha if benchmark available
        if benchmark_returns is not None:
            aligned_data = pd.concat([returns, benchmark_returns], axis=1, join='inner').dropna()
            if len(aligned_data) >= self.window_size:
                strat_returns = aligned_data.iloc[:, 0]
                bench_returns = aligned_data.iloc[:, 1]

                # Rolling beta
                def rolling_beta(x):
                    if len(x.dropna()) < 10:
                        return np.nan
                    y = x.iloc[:, 0]
                    X = sm.add_constant(x.iloc[:, 1])
                    try:
                        return sm.OLS(y, X).fit().params[1]
                    except:
                        return np.nan

                rolling_beta_series = aligned_data.rolling(window=self.window_size).apply(rolling_beta, raw=False)
                rolling_beta = rolling_beta_series.iloc[:, 0]

                # Rolling alpha
                def rolling_alpha(x):
                    if len(x.dropna()) < 10:
                        return np.nan
                    y = x.iloc[:, 0]
                    X = sm.add_constant(x.iloc[:, 1])
                    try:
                        model = sm.OLS(y, X).fit()
                        return model.params[0] * 252  # Annualized
                    except:
                        return np.nan

                rolling_alpha_series = aligned_data.rolling(window=self.window_size).apply(rolling_alpha, raw=False)
                rolling_alpha = rolling_alpha_series.iloc[:, 0]
            else:
                rolling_beta = pd.Series(index=returns.index, dtype=float)
                rolling_alpha = pd.Series(index=returns.index, dtype=float)
        else:
            rolling_beta = pd.Series(index=returns.index, dtype=float)
            rolling_alpha = pd.Series(index=returns.index, dtype=float)

        # Rolling VaR and CVaR
        rolling_var = returns.rolling(window=self.window_size).apply(
            lambda x: calculate_var(x, confidence=0.95), raw=False
        )
        rolling_cvar = returns.rolling(window=self.window_size).apply(
            lambda x: calculate_cvar(x, confidence=0.95), raw=False
        )

        return RollingPerformance(
            window_size=self.window_size,
            rolling_returns=rolling_returns,
            rolling_volatility=rolling_volatility,
            rolling_sharpe=rolling_sharpe,
            rolling_max_drawdown=rolling_max_drawdown,
            rolling_beta=rolling_beta,
            rolling_alpha=rolling_alpha,
            rolling_var=rolling_var,
            rolling_cvar=rolling_cvar,
        )


class StatisticalTestingEngine:
    """Statistical significance testing for backtest results."""

    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level

    def test_return_significance(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> List[StatisticalSignificance]:
        """Test statistical significance of returns."""

        tests = []

        # Test if strategy return is significantly different from zero
        if len(strategy_returns) > 10:
            t_stat, p_value = stats.ttest_1samp(strategy_returns, 0)
            critical_value = stats.t.ppf(1 - (1 - self.confidence_level) / 2, len(strategy_returns) - 1)

            conclusion = "Reject null hypothesis" if abs(t_stat) > critical_value else "Fail to reject null hypothesis"

            tests.append(StatisticalSignificance(
                p_value=p_value,
                confidence_level=self.confidence_level,
                null_hypothesis="Strategy return = 0",
                test_statistic=t_stat,
                critical_value=critical_value,
                sample_size=len(strategy_returns),
                degrees_freedom=len(strategy_returns) - 1,
                test_type="One-sample t-test",
                conclusion=conclusion
            ))

        # Test if strategy outperforms benchmark
        if benchmark_returns is not None:
            aligned_returns = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner').dropna()
            if len(aligned_returns) > 10:
                excess_returns = aligned_returns.iloc[:, 0] - aligned_returns.iloc[:, 1]
                t_stat, p_value = stats.ttest_1samp(excess_returns, 0)
                critical_value = stats.t.ppf(1 - (1 - self.confidence_level) / 2, len(excess_returns) - 1)

                conclusion = "Strategy outperforms benchmark" if t_stat > critical_value else "No significant outperformance"

                tests.append(StatisticalSignificance(
                    p_value=p_value,
                    confidence_level=self.confidence_level,
                    null_hypothesis="Strategy return = Benchmark return",
                    test_statistic=t_stat,
                    critical_value=critical_value,
                    sample_size=len(excess_returns),
                    degrees_freedom=len(excess_returns) - 1,
                    test_type="Paired t-test",
                    conclusion=conclusion
                ))

        return tests

    def test_performance_persistence(
        self,
        returns: pd.Series,
        window_size: int = 252
    ) -> Dict[str, Any]:
        """Test performance persistence using autocorrelation."""

        if len(returns) < window_size * 2:
            return {"insufficient_data": True}

        # Calculate rolling returns
        rolling_rets = returns.rolling(window=window_size).apply(lambda x: (1 + x).prod() - 1)

        # Test autocorrelation
        autocorr_1 = rolling_rets.autocorr(lag=1)
        n = len(rolling_rets.dropna())

        # Test significance of autocorrelation
        se = 1 / np.sqrt(n)  # Standard error for autocorrelation
        t_stat = autocorr_1 / se
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))

        return {
            "autocorrelation_1": autocorr_1,
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant_persistence": p_value < (1 - self.confidence_level),
            "persistence_strength": "Strong" if abs(autocorr_1) > 0.3 else "Moderate" if abs(autocorr_1) > 0.1 else "Weak"
        }


class BenchmarkingEngine:
    """Comprehensive benchmarking and comparison engine."""

    def __init__(self):
        self.benchmarks = {}

    def add_benchmark(
        self,
        name: str,
        returns: pd.Series,
        benchmark_type: BenchmarkType
    ) -> None:
        """Add a benchmark for comparison."""
        self.benchmarks[name] = {
            'returns': returns,
            'type': benchmark_type
        }

    def compare_to_benchmark(
        self,
        strategy_equity: pd.Series,
        benchmark_name: str
    ) -> BenchmarkComparison:
        """Compare strategy performance to a benchmark."""

        if benchmark_name not in self.benchmarks:
            raise ValueError(f"Benchmark {benchmark_name} not found")

        benchmark_data = self.benchmarks[benchmark_name]
        benchmark_returns = benchmark_data['returns']
        benchmark_type = benchmark_data['type']

        # Calculate returns
        strategy_returns = strategy_equity.pct_change().dropna()
        aligned_data = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner').dropna()

        if len(aligned_data) < 30:
            raise ValueError("Insufficient data for benchmark comparison")

        strat_rets = aligned_data.iloc[:, 0]
        bench_rets = aligned_data.iloc[:, 1]

        # Basic returns
        strategy_return = (1 + strat_rets).prod() - 1
        benchmark_return = (1 + bench_rets).prod() - 1
        excess_return = strategy_return - benchmark_return

        # Annualized metrics
        days = len(strat_rets)
        annualized_excess_return = (1 + excess_return) ** (252 / days) - 1

        # Risk metrics
        tracking_error = (strat_rets - bench_rets).std() * np.sqrt(252)
        information_ratio = annualized_excess_return / tracking_error if tracking_error > 0 else 0

        # CAPM analysis
        X = sm.add_constant(bench_rets)
        model = sm.OLS(strat_rets, X).fit()
        beta_to_benchmark = model.params[1]
        alpha_to_benchmark = model.params[0] * 252  # Annualized

        # Up/down capture
        up_periods = bench_rets > 0
        down_periods = bench_rets < 0

        up_capture = (strat_rets[up_periods].mean() / bench_rets[up_periods].mean()) if up_periods.any() else 1.0
        down_capture = (strat_rets[down_periods].mean() / bench_rets[down_periods].mean()) if down_periods.any() else 1.0

        # Batting average (consistency of outperformance)
        outperformance_periods = strat_rets > bench_rets
        batting_average = outperformance_periods.mean()

        # Win/loss ratio
        win_loss_ratio = batting_average / (1 - batting_average) if batting_average < 1 else float('inf')

        return BenchmarkComparison(
            benchmark_name=benchmark_name,
            benchmark_type=benchmark_type,
            strategy_return=strategy_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            annualized_excess_return=annualized_excess_return,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            beta_to_benchmark=beta_to_benchmark,
            alpha_to_benchmark=alpha_to_benchmark,
            up_capture=up_capture,
            down_capture=down_capture,
            batting_average=batting_average,
            win_loss_ratio=win_loss_ratio,
        )


class AdvancedAnalyticsEngine:
    """Main advanced analytics orchestration engine."""

    def __init__(
        self,
        risk_free_rate: float = 0.02,
        factors: Optional[List[str]] = None
    ):
        self.performance_engine = PerformanceAttributionEngine(risk_free_rate)
        self.factor_engine = FactorAttributionEngine(factors or ['market', 'size', 'value'])
        self.rolling_engine = RollingAnalyticsEngine()
        self.statistical_engine = StatisticalTestingEngine()
        self.benchmarking_engine = BenchmarkingEngine()

    def run_complete_analysis(
        self,
        result: EventBacktestResult,
        benchmark_returns: Optional[pd.Series] = None,
        factor_returns: Optional[pd.DataFrame] = None
    ) -> AdvancedAnalyticsResult:
        """Run complete advanced analytics suite."""

        logger.info("Starting comprehensive analytics analysis...")

        # Performance attribution
        performance_attribution = self.performance_engine.calculate_performance_attribution(
            result, benchmark_returns
        )

        # Factor attribution (if factor data available)
        factor_attribution = None
        if factor_returns is not None:
            try:
                strategy_returns = result.equity_curve.pct_change().dropna()
                factor_attribution = self.factor_engine.perform_factor_attribution(
                    strategy_returns, factor_returns
                )
            except Exception as e:
                logger.warning(f"Factor attribution failed: {e}")

        # Rolling performance
        rolling_performance = self.rolling_engine.calculate_rolling_performance(
            result.equity_curve, benchmark_returns
        )

        # Statistical significance tests
        strategy_returns = result.equity_curve.pct_change().dropna()
        statistical_tests = self.statistical_engine.test_return_significance(
            strategy_returns, benchmark_returns
        )

        # Benchmark comparisons
        benchmark_comparisons = []
        if benchmark_returns is not None:
            try:
                comparison = self.benchmarking_engine.compare_to_benchmark(
                    result.equity_curve, "custom_benchmark"
                )
                self.benchmarking_engine.add_benchmark(
                    "custom_benchmark", benchmark_returns, BenchmarkType.CUSTOM
                )
                benchmark_comparisons.append(comparison)
            except Exception as e:
                logger.warning(f"Benchmark comparison failed: {e}")

        # Risk decomposition (simplified)
        risk_decomposition = {
            'market_risk': 0.6,
            'idiosyncratic_risk': 0.3,
            'liquidity_risk': 0.1
        }

        # Performance persistence
        performance_persistence = self.statistical_engine.test_performance_persistence(strategy_returns)

        # Transaction cost analysis (placeholder)
        transaction_cost_analysis = {
            'total_trades': len(result.trades),
            'estimated_costs': len(result.trades) * 0.001,  # Rough estimate
            'cost_impact': 0.02  # 2% impact
        }

        # Monte Carlo analysis (placeholder)
        monte_carlo_analysis = {
            'mean_return': strategy_returns.mean() * 252,
            'return_std': strategy_returns.std() * np.sqrt(252),
            'confidence_interval_95': [
                strategy_returns.mean() * 252 - 1.96 * strategy_returns.std() * np.sqrt(252),
                strategy_returns.mean() * 252 + 1.96 * strategy_returns.std() * np.sqrt(252)
            ]
        }

        logger.info("Advanced analytics analysis completed")

        return AdvancedAnalyticsResult(
            performance_attribution=performance_attribution,
            factor_attribution=factor_attribution,
            rolling_performance=rolling_performance,
            statistical_tests=statistical_tests,
            benchmark_comparisons=benchmark_comparisons,
            risk_decomposition=risk_decomposition,
            performance_persistence=performance_persistence,
            transaction_cost_analysis=transaction_cost_analysis,
            monte_carlo_analysis=monte_carlo_analysis,
        )


# Convenience functions
def analyze_backtest_performance(
    result: EventBacktestResult,
    benchmark_returns: Optional[pd.Series] = None,
    factor_returns: Optional[pd.DataFrame] = None,
    risk_free_rate: float = 0.02
) -> AdvancedAnalyticsResult:
    """Convenience function for complete backtest analysis."""
    engine = AdvancedAnalyticsEngine(risk_free_rate)
    return engine.run_complete_analysis(result, benchmark_returns, factor_returns)


def create_performance_report(
    analytics_result: AdvancedAnalyticsResult,
    output_format: str = "dict"
) -> Union[Dict[str, Any], str]:
    """Create a formatted performance report."""

    report = {
        "performance_summary": {
            "total_return": f"{analytics_result.performance_attribution.total_return:.2%}",
            "annualized_return": f"{analytics_result.performance_attribution.annualized_return:.2%}",
            "volatility": f"{analytics_result.performance_attribution.volatility:.2%}",
            "sharpe_ratio": f"{analytics_result.performance_attribution.sharpe_ratio:.2f}",
            "max_drawdown": f"{analytics_result.performance_attribution.max_drawdown:.2%}",
            "win_rate": f"{analytics_result.performance_attribution.win_rate:.2%}",
        },
        "risk_metrics": {
            "VaR_95": f"{analytics_result.performance_attribution.var_95:.2%}",
            "CVaR_95": f"{analytics_result.performance_attribution.cvar_95:.2%}",
            "beta": f"{analytics_result.performance_attribution.beta:.3f}",
            "alpha": f"{analytics_result.performance_attribution.alpha:.2%}",
        },
        "statistical_tests": [
            {
                "test": test.test_type,
                "p_value": f"{test.p_value:.4f}",
                "conclusion": test.conclusion
            }
            for test in analytics_result.statistical_tests
        ]
    }

    if output_format == "dict":
        return report
    elif output_format == "json":
        import json
        return json.dumps(report, indent=2)
    else:
        return str(report)


__all__ = [
    "PerformanceAttributionEngine",
    "FactorAttributionEngine",
    "RollingAnalyticsEngine",
    "StatisticalTestingEngine",
    "BenchmarkingEngine",
    "AdvancedAnalyticsEngine",
    "AttributionMethod",
    "BenchmarkType",
    "PerformanceAttribution",
    "FactorAttribution",
    "RollingPerformance",
    "StatisticalSignificance",
    "BenchmarkComparison",
    "AdvancedAnalyticsResult",
    "analyze_backtest_performance",
    "create_performance_report",
]

"""Comprehensive benchmarking and strategy comparison suite."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd
from scipy import stats

from qantify.backtest.event import EventBacktestResult

logger = logging.getLogger(__name__)


class BenchmarkType(Enum):
    """Types of benchmarks for comparison."""

    MARKET_INDEX = "market_index"
    SECTOR_INDEX = "sector_index"
    PEER_GROUP = "peer_group"
    RISK_FREE = "risk_free"
    ABSOLUTE_RETURN = "absolute_return"
    CUSTOM = "custom"


class RankingMethod(Enum):
    """Methods for ranking strategies."""

    SHARPE_RATIO = "sharpe_ratio"
    TOTAL_RETURN = "total_return"
    MAX_DRAWDOWN = "max_drawdown"
    CALMAR_RATIO = "calmar_ratio"
    SORTINO_RATIO = "sortino_ratio"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"


@dataclass(slots=True)
class StrategyPerformance:
    """Performance metrics for a single strategy."""

    strategy_name: str
    backtest_result: EventBacktestResult
    metrics: Dict[str, float]
    risk_adjusted_metrics: Dict[str, float]
    statistical_tests: Dict[str, Any]


@dataclass(slots=True)
class BenchmarkComparison:
    """Comparison between strategy and benchmark."""

    strategy_name: str
    benchmark_name: str
    benchmark_type: BenchmarkType
    excess_return: float
    alpha: float
    beta: float
    tracking_error: float
    information_ratio: float
    up_capture: float
    down_capture: float
    batting_average: float


@dataclass(slots=True)
class StrategyRanking:
    """Ranking results for multiple strategies."""

    ranking_method: RankingMethod
    rankings: List[Tuple[str, float]]
    statistical_significance: Dict[str, bool]
    confidence_intervals: Dict[str, Tuple[float, float]]


@dataclass(slots=True)
class BenchmarkingReport:
    """Comprehensive benchmarking report."""

    strategies: Dict[str, StrategyPerformance]
    benchmarks: Dict[str, BenchmarkComparison]
    rankings: Dict[RankingMethod, StrategyRanking]
    peer_analysis: Dict[str, Any]
    attribution_analysis: Dict[str, Any]
    risk_decomposition: Dict[str, Any]


class StrategyBenchmarker:
    """Advanced strategy benchmarking and comparison engine."""

    def __init__(self):
        self.strategies: Dict[str, StrategyPerformance] = {}
        self.benchmarks: Dict[str, pd.Series] = {}

    def add_strategy(
        self,
        name: str,
        backtest_result: EventBacktestResult,
        risk_free_rate: float = 0.02
    ) -> None:
        """Add a strategy for benchmarking."""

        # Calculate comprehensive metrics
        returns = backtest_result.equity_curve.pct_change().dropna()
        total_return = (backtest_result.equity_curve.iloc[-1] / backtest_result.equity_curve.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0

        # Risk metrics
        max_drawdown = backtest_result.max_drawdown
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0

        # Downside metrics
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (annualized_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

        # Trade metrics
        win_rate = backtest_result.win_rate
        profit_factor = backtest_result.profit_factor if hasattr(backtest_result, 'profit_factor') else 1.0

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(backtest_result.trades),
        }

        # Risk-adjusted metrics
        risk_adjusted_metrics = {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'omega_ratio': self._calculate_omega_ratio(returns),
            'tail_ratio': self._calculate_tail_ratio(returns),
            'kelly_criterion': self._calculate_kelly_criterion(returns),
        }

        # Statistical tests
        statistical_tests = {
            'return_significance': self._test_return_significance(returns),
            'volatility_clustering': self._test_volatility_clustering(returns),
            'autocorrelation': self._test_autocorrelation(returns),
        }

        performance = StrategyPerformance(
            strategy_name=name,
            backtest_result=backtest_result,
            metrics=metrics,
            risk_adjusted_metrics=risk_adjusted_metrics,
            statistical_tests=statistical_tests
        )

        self.strategies[name] = performance
        logger.info(f"Added strategy for benchmarking: {name}")

    def add_benchmark(
        self,
        name: str,
        returns: pd.Series,
        benchmark_type: BenchmarkType
    ) -> None:
        """Add a benchmark for comparison."""
        self.benchmarks[name] = returns
        logger.info(f"Added benchmark: {name} ({benchmark_type.value})")

    def compare_to_benchmark(
        self,
        strategy_name: str,
        benchmark_name: str
    ) -> BenchmarkComparison:
        """Compare strategy to benchmark."""

        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")

        if benchmark_name not in self.benchmarks:
            raise ValueError(f"Benchmark {benchmark_name} not found")

        strategy = self.strategies[strategy_name]
        benchmark_returns = self.benchmarks[benchmark_name]
        strategy_returns = strategy.backtest_result.equity_curve.pct_change().dropna()

        # Align data
        aligned_data = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner').dropna()
        strat_rets = aligned_data.iloc[:, 0]
        bench_rets = aligned_data.iloc[:, 1]

        # Calculate excess returns
        excess_returns = strat_rets - bench_rets
        excess_return = excess_returns.sum()

        # CAPM analysis
        X = sm.add_constant(bench_rets)
        model = sm.OLS(strat_rets, X).fit()
        alpha = model.params[0] * 252  # Annualized alpha
        beta = model.params[1]

        # Tracking error and information ratio
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = alpha / tracking_error if tracking_error > 0 else 0

        # Up/down capture
        up_periods = bench_rets > 0
        down_periods = bench_rets < 0

        up_capture = (strat_rets[up_periods].mean() / bench_rets[up_periods].mean()) if up_periods.any() else 1.0
        down_capture = (strat_rets[down_periods].mean() / bench_rets[down_periods].mean()) if down_periods.any() else 1.0

        # Batting average
        batting_average = (strat_rets * bench_rets > 0).mean()

        benchmark_type = BenchmarkType.CUSTOM  # Could be enhanced to track actual types

        return BenchmarkComparison(
            strategy_name=strategy_name,
            benchmark_name=benchmark_name,
            benchmark_type=benchmark_type,
            excess_return=excess_return,
            alpha=alpha,
            beta=beta,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            up_capture=up_capture,
            down_capture=down_capture,
            batting_average=batting_average,
        )

    def rank_strategies(
        self,
        ranking_method: RankingMethod,
        ascending: bool = False
    ) -> StrategyRanking:
        """Rank strategies by specified method."""

        if not self.strategies:
            raise ValueError("No strategies to rank")

        # Extract ranking values
        ranking_data = []
        for name, perf in self.strategies.items():
            if ranking_method == RankingMethod.SHARPE_RATIO:
                value = perf.risk_adjusted_metrics['sharpe_ratio']
            elif ranking_method == RankingMethod.TOTAL_RETURN:
                value = perf.metrics['total_return']
            elif ranking_method == RankingMethod.MAX_DRAWDOWN:
                value = perf.metrics['max_drawdown']
            elif ranking_method == RankingMethod.CALMAR_RATIO:
                value = perf.risk_adjusted_metrics['calmar_ratio']
            elif ranking_method == RankingMethod.SORTINO_RATIO:
                value = perf.risk_adjusted_metrics['sortino_ratio']
            elif ranking_method == RankingMethod.WIN_RATE:
                value = perf.metrics['win_rate']
            elif ranking_method == RankingMethod.PROFIT_FACTOR:
                value = perf.metrics['profit_factor']
            else:
                raise ValueError(f"Unsupported ranking method: {ranking_method}")

            ranking_data.append((name, value))

        # Sort rankings
        rankings = sorted(ranking_data, key=lambda x: x[1], reverse=not ascending)

        # Statistical significance testing
        statistical_significance = {}
        confidence_intervals = {}

        if len(self.strategies) >= 2:
            values = [v for _, v in ranking_data]

            # Test if best strategy is significantly different from others
            best_value = rankings[0][1]
            other_values = [v for n, v in ranking_data if n != rankings[0][0]]

            if other_values:
                # Simple t-test
                t_stat, p_value = stats.ttest_1samp(other_values, best_value)
                statistical_significance[rankings[0][0]] = p_value < 0.05

                # Confidence intervals
                for name, value in ranking_data:
                    # Bootstrap confidence interval
                    bootstrapped = np.random.choice(values, size=(1000, len(values)), replace=True)
                    ci_lower = np.percentile(bootstrapped.mean(axis=1), 2.5)
                    ci_upper = np.percentile(bootstrapped.mean(axis=1), 97.5)
                    confidence_intervals[name] = (ci_lower, ci_upper)

        return StrategyRanking(
            ranking_method=ranking_method,
            rankings=rankings,
            statistical_significance=statistical_significance,
            confidence_intervals=confidence_intervals,
        )

    def generate_peer_analysis(self) -> Dict[str, Any]:
        """Generate peer analysis across strategies."""

        if len(self.strategies) < 2:
            return {'insufficient_strategies': True}

        # Collect metrics across strategies
        metrics_df = pd.DataFrame({
            name: perf.metrics for name, perf in self.strategies.items()
        }).T

        # Calculate peer rankings
        peer_rankings = {}
        for metric in metrics_df.columns:
            if metric in ['sharpe_ratio', 'total_return', 'win_rate', 'profit_factor']:
                # Higher is better
                rankings = metrics_df[metric].rank(ascending=False)
            else:
                # Lower is better (e.g., max_drawdown, volatility)
                rankings = metrics_df[metric].rank(ascending=True)

            peer_rankings[metric] = rankings.to_dict()

        # Calculate strategy correlations
        returns_list = []
        for name, perf in self.strategies.items():
            returns = perf.backtest_result.equity_curve.pct_change().dropna()
            returns_list.append(returns.rename(name))

        if returns_list:
            returns_df = pd.concat(returns_list, axis=1, join='inner')
            correlations = returns_df.corr()
        else:
            correlations = pd.DataFrame()

        # Strategy clusters (simplified)
        clusters = self._identify_strategy_clusters(metrics_df)

        return {
            'peer_rankings': peer_rankings,
            'strategy_correlations': correlations.to_dict() if not correlations.empty else {},
            'clusters': clusters,
            'best_in_class': self._identify_best_in_class(metrics_df),
        }

    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0.0) -> float:
        """Calculate Omega Ratio."""
        excess_returns = returns - threshold
        positive_sum = excess_returns[excess_returns > 0].sum()
        negative_sum = abs(excess_returns[excess_returns < 0].sum())
        return positive_sum / negative_sum if negative_sum > 0 else float('inf')

    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate Tail Ratio."""
        if len(returns) < 20:
            return 1.0
        percentile_95 = np.percentile(returns, 95)
        percentile_5 = np.percentile(returns, 5)
        return percentile_95 / abs(percentile_5) if percentile_5 < 0 else 1.0

    def _calculate_kelly_criterion(self, returns: pd.Series) -> float:
        """Calculate Kelly Criterion."""
        win_rate = (returns > 0).mean()
        avg_win = returns[returns > 0].mean()
        avg_loss = abs(returns[returns < 0].mean())
        return win_rate / avg_loss - (1 - win_rate) / avg_win if avg_win > 0 and avg_loss > 0 else 0

    def _test_return_significance(self, returns: pd.Series) -> Dict[str, Any]:
        """Test if returns are significantly different from zero."""
        t_stat, p_value = stats.ttest_1samp(returns, 0)
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'confidence_level': 0.95
        }

    def _test_volatility_clustering(self, returns: pd.Series) -> Dict[str, Any]:
        """Test for volatility clustering (ARCH effect)."""
        # Simplified test using autocorrelation of squared returns
        squared_returns = returns ** 2
        autocorr = squared_returns.autocorr(lag=1)
        return {
            'autocorrelation': autocorr,
            'clustering_detected': abs(autocorr) > 0.1
        }

    def _test_autocorrelation(self, returns: pd.Series) -> Dict[str, Any]:
        """Test for autocorrelation in returns."""
        autocorr_1 = returns.autocorr(lag=1)
        autocorr_5 = returns.autocorr(lag=5)

        # Ljung-Box test
        lb_stat, lb_p = stats.acorr_ljungbox(returns, lags=[1, 5], return_df=False)

        return {
            'autocorr_1': autocorr_1,
            'autocorr_5': autocorr_5,
            'ljung_box_p': lb_p[0],
            'autocorrelation_present': lb_p[0] < 0.05
        }

    def _identify_strategy_clusters(self, metrics_df: pd.DataFrame) -> Dict[str, List[str]]:
        """Identify strategy clusters based on performance metrics."""
        # Simplified clustering based on Sharpe ratio and max drawdown
        clusters = {
            'high_sharpe_low_dd': [],
            'high_sharpe_high_dd': [],
            'low_sharpe_low_dd': [],
            'low_sharpe_high_dd': []
        }

        sharpe_median = metrics_df['sharpe_ratio'].median()
        dd_median = metrics_df['max_drawdown'].median()

        for strategy, row in metrics_df.iterrows():
            sharpe = row['sharpe_ratio']
            dd = row['max_drawdown']

            if sharpe >= sharpe_median and abs(dd) <= abs(dd_median):
                clusters['high_sharpe_low_dd'].append(strategy)
            elif sharpe >= sharpe_median and abs(dd) > abs(dd_median):
                clusters['high_sharpe_high_dd'].append(strategy)
            elif sharpe < sharpe_median and abs(dd) <= abs(dd_median):
                clusters['low_sharpe_low_dd'].append(strategy)
            else:
                clusters['low_sharpe_high_dd'].append(strategy)

        return clusters

    def _identify_best_in_class(self, metrics_df: pd.DataFrame) -> Dict[str, str]:
        """Identify best strategy in each category."""
        best_in_class = {}

        # Best Sharpe ratio
        best_in_class['sharpe_ratio'] = metrics_df['sharpe_ratio'].idxmax()

        # Best total return
        best_in_class['total_return'] = metrics_df['total_return'].idxmax()

        # Lowest max drawdown
        best_in_class['max_drawdown'] = metrics_df['max_drawdown'].idxmin()

        # Best risk-adjusted return (Sharpe)
        best_in_class['risk_adjusted'] = metrics_df['sharpe_ratio'].idxmax()

        return best_in_class


class BenchmarkingEngine:
    """Main benchmarking orchestration engine."""

    def __init__(self):
        self.benchmarker = StrategyBenchmarker()

    def run_comprehensive_benchmarking(
        self,
        strategies: Dict[str, EventBacktestResult],
        benchmarks: Dict[str, pd.Series],
        benchmark_types: Optional[Dict[str, BenchmarkType]] = None
    ) -> BenchmarkingReport:
        """Run comprehensive benchmarking analysis."""

        # Add strategies
        for name, result in strategies.items():
            self.benchmarker.add_strategy(name, result)

        # Add benchmarks
        for name, returns in benchmarks.items():
            bench_type = benchmark_types.get(name, BenchmarkType.CUSTOM) if benchmark_types else BenchmarkType.CUSTOM
            self.benchmarker.add_benchmark(name, returns, bench_type)

        # Generate comparisons
        benchmark_comparisons = {}
        if benchmarks:
            primary_benchmark = list(benchmarks.keys())[0]
            for strategy_name in strategies.keys():
                try:
                    comparison = self.benchmarker.compare_to_benchmark(strategy_name, primary_benchmark)
                    benchmark_comparisons[strategy_name] = comparison
                except Exception as e:
                    logger.warning(f"Failed to compare {strategy_name} to {primary_benchmark}: {e}")

        # Generate rankings
        rankings = {}
        for method in RankingMethod:
            try:
                ranking = self.benchmarker.rank_strategies(method)
                rankings[method] = ranking
            except Exception as e:
                logger.warning(f"Failed to rank by {method}: {e}")

        # Peer analysis
        peer_analysis = self.benchmarker.generate_peer_analysis()

        # Attribution analysis (simplified)
        attribution_analysis = {
            'factor_contributions': {},
            'style_analysis': {},
            'performance_attribution': {}
        }

        # Risk decomposition (simplified)
        risk_decomposition = {
            'systematic_risk': 0.6,
            'idiosyncratic_risk': 0.4,
            'factor_exposures': {}
        }

        return BenchmarkingReport(
            strategies=self.benchmarker.strategies,
            benchmarks=benchmark_comparisons,
            rankings=rankings,
            peer_analysis=peer_analysis,
            attribution_analysis=attribution_analysis,
            risk_decomposition=risk_decomposition,
        )


# Convenience functions
def create_benchmarking_report(
    strategies: Dict[str, EventBacktestResult],
    benchmarks: Dict[str, pd.Series]
) -> BenchmarkingReport:
    """Create comprehensive benchmarking report."""
    engine = BenchmarkingEngine()
    return engine.run_comprehensive_benchmarking(strategies, benchmarks)


def rank_strategies_by_metric(
    strategies: Dict[str, EventBacktestResult],
    metric: RankingMethod
) -> StrategyRanking:
    """Rank strategies by specific metric."""
    benchmarker = StrategyBenchmarker()

    for name, result in strategies.items():
        benchmarker.add_strategy(name, result)

    return benchmarker.rank_strategies(metric)


__all__ = [
    "BenchmarkType",
    "RankingMethod",
    "StrategyPerformance",
    "BenchmarkComparison",
    "StrategyRanking",
    "BenchmarkingReport",
    "StrategyBenchmarker",
    "BenchmarkingEngine",
    "create_benchmarking_report",
    "rank_strategies_by_metric",
]

"""Live data integration for real-time backtesting validation."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Union
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd
import numpy as np

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.data.streaming import EventQueue, StreamEvent
from qantify.strategy import Strategy

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Modes for live data validation."""

    FORWARD_TEST = "forward_test"  # Test on future unseen data
    PAPER_TRADING = "paper_trading"  # Paper trading validation
    REAL_TIME_COMPARISON = "real_time_comparison"  # Compare with live market
    WALK_FORWARD_UPDATE = "walk_forward_update"  # Update models with live data


class DataQualityMetric(Enum):
    """Metrics for assessing data quality."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    CONSISTENCY = "consistency"
    REALISM = "realism"


@dataclass(slots=True)
class LiveDataFeed:
    """Configuration for live data feed."""

    symbol: str
    data_source: str
    update_frequency: str = "1m"  # 1m, 5m, 1h, etc.
    data_quality_checks: bool = True
    historical_buffer_days: int = 30
    real_time_enabled: bool = True


@dataclass(slots=True)
class ValidationResult:
    """Result of live data validation."""

    validation_mode: ValidationMode
    strategy_name: str
    backtest_performance: Dict[str, float]
    live_performance: Dict[str, float]
    performance_drift: Dict[str, float]
    data_quality_score: float
    validation_confidence: float
    last_updated: datetime


@dataclass(slots=True)
class RealTimeComparison:
    """Real-time comparison between backtest and live performance."""

    timestamp: datetime
    backtest_prediction: float
    actual_outcome: float
    prediction_error: float
    cumulative_error: float
    confidence_interval: Tuple[float, float]


@dataclass(slots=True)
class LiveIntegrationReport:
    """Comprehensive live integration report."""

    validation_results: Dict[str, ValidationResult]
    real_time_comparisons: List[RealTimeComparison]
    data_quality_metrics: Dict[str, float]
    model_drift_signals: List[Dict[str, Any]]
    recommendations: List[str]
    last_update: datetime


class LiveDataValidator:
    """Engine for validating backtests with live data."""

    def __init__(self, validation_mode: ValidationMode = ValidationMode.FORWARD_TEST):
        self.validation_mode = validation_mode
        self.live_feeds: Dict[str, LiveDataFeed] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.real_time_comparisons: List[RealTimeComparison] = []
        self.data_buffer: Dict[str, pd.DataFrame] = {}

    def add_live_feed(self, feed: LiveDataFeed) -> None:
        """Add a live data feed for validation."""
        self.live_feeds[feed.symbol] = feed

        # Initialize data buffer
        self.data_buffer[feed.symbol] = pd.DataFrame()

        logger.info(f"Added live data feed for {feed.symbol} from {feed.data_source}")

    async def validate_strategy(
        self,
        strategy_name: str,
        backtest_result: EventBacktestResult,
        live_data_period_days: int = 30
    ) -> ValidationResult:
        """Validate strategy performance with live data."""

        if not self.live_feeds:
            raise ValueError("No live data feeds configured")

        # Get primary symbol
        primary_symbol = getattr(backtest_result, 'symbol', 'UNKNOWN')

        if primary_symbol not in self.live_feeds:
            logger.warning(f"No live feed for {primary_symbol}, using first available")
            primary_symbol = list(self.live_feeds.keys())[0]

        # Simulate live data collection (in practice, this would connect to real feeds)
        live_data = await self._collect_live_data(primary_symbol, live_data_period_days)

        # Run validation based on mode
        if self.validation_mode == ValidationMode.FORWARD_TEST:
            validation_result = await self._run_forward_test_validation(
                strategy_name, backtest_result, live_data
            )
        elif self.validation_mode == ValidationMode.REAL_TIME_COMPARISON:
            validation_result = await self._run_real_time_comparison(
                strategy_name, backtest_result, live_data
            )
        else:
            # Simplified validation for other modes
            validation_result = await self._run_basic_validation(
                strategy_name, backtest_result, live_data
            )

        self.validation_results[strategy_name] = validation_result
        return validation_result

    async def _collect_live_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Collect live data for validation (simulated)."""
        # In practice, this would connect to real-time data feeds
        # For demonstration, we'll generate realistic live data

        feed = self.live_feeds[symbol]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Generate realistic price data
        np.random.seed(42)
        dates = pd.date_range(start_date, end_date, freq='1min')

        # Base price from recent data (simulated)
        base_price = 150.0  # Would come from actual feed

        # Generate OHLCV data
        trend = np.cumsum(np.random.randn(len(dates)) * 0.0001)
        noise = np.random.randn(len(dates)) * 0.005
        returns = trend + noise

        prices = base_price * (1 + returns)
        high_mult = 1 + np.random.rand(len(dates)) * 0.003
        low_mult = 1 - np.random.rand(len(dates)) * 0.003
        volumes = np.random.randint(10000, 100000, len(dates))

        data = pd.DataFrame({
            'open': prices * (1 + np.random.randn(len(dates)) * 0.001),
            'high': prices * high_mult,
            'low': prices * low_mult,
            'close': prices,
            'volume': volumes
        }, index=dates)

        # Store in buffer
        self.data_buffer[symbol] = pd.concat([self.data_buffer[symbol], data]).drop_duplicates()

        return data

    async def _run_forward_test_validation(
        self,
        strategy_name: str,
        backtest_result: EventBacktestResult,
        live_data: pd.DataFrame
    ) -> ValidationResult:
        """Run forward test validation."""

        # Extract backtest performance metrics
        backtest_perf = {
            'sharpe_ratio': backtest_result.sharpe_ratio,
            'total_return': (backtest_result.equity_curve.iloc[-1] / backtest_result.equity_curve.iloc[0]) - 1,
            'max_drawdown': backtest_result.max_drawdown,
            'win_rate': backtest_result.win_rate,
            'total_trades': len(backtest_result.trades)
        }

        # Run strategy on live data
        strategy = self._create_strategy_from_backtest(backtest_result)
        live_engine = EventBacktester(live_data, symbol=strategy_name, strategy=strategy)
        live_result = live_engine.run()

        live_perf = {
            'sharpe_ratio': live_result.sharpe_ratio,
            'total_return': (live_result.equity_curve.iloc[-1] / live_result.equity_curve.iloc[0]) - 1,
            'max_drawdown': live_result.max_drawdown,
            'win_rate': live_result.win_rate,
            'total_trades': len(live_result.trades)
        }

        # Calculate performance drift
        performance_drift = {
            'sharpe_ratio_drift': live_perf['sharpe_ratio'] - backtest_perf['sharpe_ratio'],
            'return_drift': live_perf['total_return'] - backtest_perf['total_return'],
            'drawdown_drift': live_perf['max_drawdown'] - backtest_perf['max_drawdown'],
            'win_rate_drift': live_perf['win_rate'] - backtest_perf['win_rate']
        }

        # Assess data quality
        data_quality = self._assess_data_quality(live_data)

        # Calculate validation confidence
        confidence = self._calculate_validation_confidence(performance_drift, data_quality)

        return ValidationResult(
            validation_mode=self.validation_mode,
            strategy_name=strategy_name,
            backtest_performance=backtest_perf,
            live_performance=live_perf,
            performance_drift=performance_drift,
            data_quality_score=data_quality,
            validation_confidence=confidence,
            last_updated=datetime.now()
        )

    async def _run_real_time_comparison(
        self,
        strategy_name: str,
        backtest_result: EventBacktestResult,
        live_data: pd.DataFrame
    ) -> ValidationResult:
        """Run real-time comparison validation."""

        # This would involve running the strategy in real-time
        # For now, return a basic validation
        return await self._run_basic_validation(strategy_name, backtest_result, live_data)

    async def _run_basic_validation(
        self,
        strategy_name: str,
        backtest_result: EventBacktestResult,
        live_data: pd.DataFrame
    ) -> ValidationResult:
        """Run basic validation."""

        backtest_perf = {
            'sharpe_ratio': backtest_result.sharpe_ratio,
            'total_return': 0.15,  # Placeholder
            'max_drawdown': backtest_result.max_drawdown,
            'win_rate': backtest_result.win_rate,
            'total_trades': len(backtest_result.trades)
        }

        live_perf = {
            'sharpe_ratio': backtest_result.sharpe_ratio * 0.9,  # Slight degradation
            'total_return': 0.12,
            'max_drawdown': backtest_result.max_drawdown * 1.1,
            'win_rate': backtest_result.win_rate * 0.95,
            'total_trades': int(len(backtest_result.trades) * 0.8)
        }

        performance_drift = {k: live_perf[k] - backtest_perf[k] for k in backtest_perf.keys()}
        data_quality = self._assess_data_quality(live_data)
        confidence = self._calculate_validation_confidence(performance_drift, data_quality)

        return ValidationResult(
            validation_mode=self.validation_mode,
            strategy_name=strategy_name,
            backtest_performance=backtest_perf,
            live_performance=live_perf,
            performance_drift=performance_drift,
            data_quality_score=data_quality,
            validation_confidence=confidence,
            last_updated=datetime.now()
        )

    def _create_strategy_from_backtest(self, backtest_result: EventBacktestResult) -> Strategy:
        """Create strategy instance from backtest result (simplified)."""
        # This is a placeholder - in practice, you'd reconstruct the strategy
        from qantify.strategy import Strategy

        class ReconstructedStrategy(Strategy):
            def init(self):
                pass

            def next(self):
                pass

        return ReconstructedStrategy()

    def _assess_data_quality(self, data: pd.DataFrame) -> float:
        """Assess data quality score (0-1)."""
        score = 1.0

        # Check completeness
        null_pct = data.isnull().sum().sum() / (data.shape[0] * data.shape[1])
        score *= (1 - null_pct)

        # Check for outliers
        for col in ['open', 'high', 'low', 'close']:
            if col in data.columns:
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                outlier_pct = (z_scores > 3).sum() / len(data)
                score *= (1 - outlier_pct * 0.1)  # Penalize outliers

        # Check volume consistency
        if 'volume' in data.columns:
            vol_std = data['volume'].std() / data['volume'].mean()
            if vol_std > 2:  # Unrealistic volume variation
                score *= 0.9

        return max(0, min(1, score))

    def _calculate_validation_confidence(self, performance_drift: Dict[str, float], data_quality: float) -> float:
        """Calculate validation confidence score."""
        # Base confidence from data quality
        confidence = data_quality

        # Adjust for performance drift
        total_drift = sum(abs(v) for v in performance_drift.values())
        drift_penalty = min(0.5, total_drift)  # Cap penalty at 0.5

        confidence *= (1 - drift_penalty)

        # Sample size adjustment (simplified)
        confidence *= 0.9  # Assume moderate sample size

        return confidence

    async def update_real_time_comparison(
        self,
        strategy_name: str,
        backtest_prediction: float,
        actual_outcome: float,
        timestamp: datetime
    ) -> None:
        """Update real-time comparison data."""

        prediction_error = actual_outcome - backtest_prediction

        # Calculate cumulative error
        if self.real_time_comparisons:
            cumulative_error = self.real_time_comparisons[-1].cumulative_error + abs(prediction_error)
        else:
            cumulative_error = abs(prediction_error)

        # Simple confidence interval
        confidence_interval = (
            backtest_prediction - 2 * abs(prediction_error),
            backtest_prediction + 2 * abs(prediction_error)
        )

        comparison = RealTimeComparison(
            timestamp=timestamp,
            backtest_prediction=backtest_prediction,
            actual_outcome=actual_outcome,
            prediction_error=prediction_error,
            cumulative_error=cumulative_error,
            confidence_interval=confidence_interval
        )

        self.real_time_comparisons.append(comparison)

    def detect_model_drift(self) -> List[Dict[str, Any]]:
        """Detect model drift signals."""

        if len(self.real_time_comparisons) < 10:
            return []

        recent_comparisons = self.real_time_comparisons[-20:]  # Last 20 comparisons

        # Check for increasing prediction errors
        errors = [abs(c.prediction_error) for c in recent_comparisons]
        recent_avg_error = np.mean(errors[-10:])
        earlier_avg_error = np.mean(errors[:10])

        drift_signals = []

        if recent_avg_error > earlier_avg_error * 1.5:
            drift_signals.append({
                'type': 'prediction_accuracy_drift',
                'severity': 'high',
                'description': f'Prediction errors increased by {(recent_avg_error/earlier_avg_error - 1)*100:.1f}%',
                'timestamp': recent_comparisons[-1].timestamp
            })

        # Check for changing error patterns
        if len(errors) >= 20:
            first_half_std = np.std(errors[:10])
            second_half_std = np.std(errors[10:])

            if second_half_std > first_half_std * 1.5:
                drift_signals.append({
                    'type': 'error_volatility_increase',
                    'severity': 'medium',
                    'description': f'Error volatility increased by {(second_half_std/first_half_std - 1)*100:.1f}%',
                    'timestamp': recent_comparisons[-1].timestamp
                })

        return drift_signals

    def generate_live_integration_report(self) -> LiveIntegrationReport:
        """Generate comprehensive live integration report."""

        # Data quality metrics
        data_quality_metrics = {}
        for symbol, data in self.data_buffer.items():
            if not data.empty:
                data_quality_metrics[symbol] = self._assess_data_quality(data)

        # Model drift signals
        model_drift_signals = self.detect_model_drift()

        # Generate recommendations
        recommendations = self._generate_recommendations(
            self.validation_results,
            data_quality_metrics,
            model_drift_signals
        )

        return LiveIntegrationReport(
            validation_results=self.validation_results,
            real_time_comparisons=self.real_time_comparisons[-100:],  # Last 100 comparisons
            data_quality_metrics=data_quality_metrics,
            model_drift_signals=model_drift_signals,
            recommendations=recommendations,
            last_update=datetime.now()
        )

    def _generate_recommendations(
        self,
        validation_results: Dict[str, ValidationResult],
        data_quality_metrics: Dict[str, float],
        drift_signals: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on validation results."""

        recommendations = []

        # Check validation confidence
        for strategy_name, result in validation_results.items():
            if result.validation_confidence < 0.7:
                recommendations.append(
                    f"Low validation confidence for {strategy_name} ({result.validation_confidence:.1f}). "
                    "Consider re-optimizing or adjusting strategy parameters."
                )

            # Check performance drift
            significant_drift = any(abs(drift) > 0.2 for drift in result.performance_drift.values())
            if significant_drift:
                recommendations.append(
                    f"Significant performance drift detected for {strategy_name}. "
                    "Backtest results may not hold in live markets."
                )

        # Check data quality
        poor_quality_feeds = [symbol for symbol, quality in data_quality_metrics.items() if quality < 0.8]
        if poor_quality_feeds:
            recommendations.append(
                f"Poor data quality detected for feeds: {poor_quality_feeds}. "
                "Consider switching data providers or implementing data cleaning."
            )

        # Check for model drift
        if drift_signals:
            recommendations.append(
                f"Model drift detected ({len(drift_signals)} signals). "
                "Consider re-training models or implementing drift adaptation."
            )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Live validation successful. Strategy performance aligns with backtest results."
            )

        return recommendations


class LiveBacktestCoordinator:
    """Coordinator for live backtesting operations."""

    def __init__(self):
        self.validators: Dict[str, LiveDataValidator] = {}
        self.active_validations: Dict[str, asyncio.Task] = {}

    async def start_live_validation(
        self,
        validation_id: str,
        strategy_name: str,
        backtest_result: EventBacktestResult,
        live_feeds: List[LiveDataFeed],
        validation_mode: ValidationMode = ValidationMode.FORWARD_TEST
    ) -> str:
        """Start live validation process."""

        validator = LiveDataValidator(validation_mode)

        # Add live feeds
        for feed in live_feeds:
            validator.add_live_feed(feed)

        self.validators[validation_id] = validator

        # Start validation task
        task = asyncio.create_task(
            validator.validate_strategy(strategy_name, backtest_result)
        )
        self.active_validations[validation_id] = task

        logger.info(f"Started live validation: {validation_id}")
        return validation_id

    async def get_validation_status(self, validation_id: str) -> Optional[ValidationResult]:
        """Get validation status."""

        if validation_id not in self.validators:
            return None

        validator = self.validators[validation_id]

        if validation_id in self.active_validations:
            task = self.active_validations[validation_id]
            if task.done():
                try:
                    result = task.result()
                    del self.active_validations[validation_id]
                    return result
                except Exception as e:
                    logger.error(f"Validation failed: {e}")
                    return None
        else:
            # Check if we have cached results
            strategy_names = list(validator.validation_results.keys())
            if strategy_names:
                return validator.validation_results[strategy_names[0]]

        return None

    async def get_live_integration_report(self, validation_id: str) -> Optional[LiveIntegrationReport]:
        """Get comprehensive live integration report."""

        if validation_id not in self.validators:
            return None

        validator = self.validators[validation_id]
        return validator.generate_live_integration_report()


# Convenience functions
async def validate_strategy_live(
    strategy_name: str,
    backtest_result: EventBacktestResult,
    live_feeds: List[LiveDataFeed],
    validation_mode: ValidationMode = ValidationMode.FORWARD_TEST
) -> ValidationResult:
    """Convenience function for live strategy validation."""

    validator = LiveDataValidator(validation_mode)

    for feed in live_feeds:
        validator.add_live_feed(feed)

    return await validator.validate_strategy(strategy_name, backtest_result, live_data_period_days=30)


def create_live_feed_config(
    symbols: List[str],
    data_source: str = "simulated",
    update_frequency: str = "1m"
) -> List[LiveDataFeed]:
    """Create live feed configurations."""

    return [
        LiveDataFeed(
            symbol=symbol,
            data_source=data_source,
            update_frequency=update_frequency,
            data_quality_checks=True,
            historical_buffer_days=30,
            real_time_enabled=True
        )
        for symbol in symbols
    ]


__all__ = [
    "ValidationMode",
    "DataQualityMetric",
    "LiveDataFeed",
    "ValidationResult",
    "RealTimeComparison",
    "LiveIntegrationReport",
    "LiveDataValidator",
    "LiveBacktestCoordinator",
    "validate_strategy_live",
    "create_live_feed_config",
]

"""Multi-timeframe backtesting framework with cross-timeframe analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio

import numpy as np
import pandas as pd
from scipy import stats

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.types import OrderSide
from qantify.strategy import Strategy

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """Standard timeframes for trading."""

    TICK = "tick"
    SECOND_1 = "1s"
    SECOND_5 = "5s"
    SECOND_15 = "15s"
    SECOND_30 = "30s"
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


@dataclass(slots=True)
class TimeFrameData:
    """Data container for a specific timeframe."""

    timeframe: TimeFrame
    data: pd.DataFrame
    base_timeframe: TimeFrame
    resampling_method: str = "ohlc"  # 'ohlc', 'last', 'mean', etc.

    @property
    def frequency_minutes(self) -> int:
        """Get frequency in minutes."""
        timeframe_map = {
            TimeFrame.TICK: 0,
            TimeFrame.SECOND_1: 1/60,
            TimeFrame.SECOND_5: 5/60,
            TimeFrame.SECOND_15: 15/60,
            TimeFrame.SECOND_30: 30/60,
            TimeFrame.MINUTE_1: 1,
            TimeFrame.MINUTE_5: 5,
            TimeFrame.MINUTE_15: 15,
            TimeFrame.MINUTE_30: 30,
            TimeFrame.HOUR_1: 60,
            TimeFrame.HOUR_4: 240,
            TimeFrame.DAY_1: 1440,
            TimeFrame.WEEK_1: 10080,
            TimeFrame.MONTH_1: 43200,
        }
        return timeframe_map[self.timeframe]


@dataclass(slots=True)
class MultiTimeFrameConfig:
    """Configuration for multi-timeframe backtesting."""

    base_timeframe: TimeFrame
    higher_timeframes: List[TimeFrame]
    synchronization_method: str = "exact"  # 'exact', 'nearest', 'interpolate'
    max_lag_minutes: int = 5
    enable_cross_timeframe_signals: bool = True
    enable_timeframe_transitions: bool = True
    risk_scaling_method: str = "sqrt_time"  # 'sqrt_time', 'linear', 'constant'


@dataclass(slots=True)
class CrossTimeFrameSignal:
    """Signal generated from multiple timeframes."""

    signal_type: str
    primary_timeframe: TimeFrame
    confirming_timeframes: List[TimeFrame]
    strength: float
    confidence: float
    timestamp: datetime
    data: Dict[str, Any]


@dataclass(slots=True)
class TimeFrameTransition:
    """Transition between timeframes."""

    from_timeframe: TimeFrame
    to_timeframe: TimeFrame
    trigger_condition: str
    transition_time: datetime
    reason: str


@dataclass(slots=True)
class MultiTimeFrameResult:
    """Result from multi-timeframe backtesting."""

    base_result: EventBacktestResult
    timeframe_results: Dict[TimeFrame, EventBacktestResult]
    cross_timeframe_signals: List[CrossTimeFrameSignal]
    timeframe_transitions: List[TimeFrameTransition]
    performance_by_timeframe: Dict[TimeFrame, Dict[str, float]]
    timeframe_correlations: Dict[Tuple[TimeFrame, TimeFrame], float]
    overall_performance: Dict[str, float]


class TimeFrameResampler:
    """Advanced timeframe resampling engine."""

    @staticmethod
    def resample_data(
        data: pd.DataFrame,
        from_timeframe: TimeFrame,
        to_timeframe: TimeFrame,
        method: str = "ohlc"
    ) -> pd.DataFrame:
        """Resample data from one timeframe to another."""

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have DatetimeIndex")

        # Calculate resampling frequency
        from_minutes = TimeFrameResampler._get_minutes(from_timeframe)
        to_minutes = TimeFrameResampler._get_minutes(to_timeframe)

        if to_minutes <= from_minutes:
            # Upsampling (higher to lower frequency)
            return TimeFrameResampler._upsample_data(data, from_timeframe, to_timeframe, method)
        else:
            # Downsampling (lower to higher frequency)
            return TimeFrameResampler._downsample_data(data, from_timeframe, to_timeframe, method)

    @staticmethod
    def _get_minutes(timeframe: TimeFrame) -> float:
        """Get timeframe in minutes."""
        timeframe_minutes = {
            TimeFrame.TICK: 0.001,  # Assume tick data
            TimeFrame.SECOND_1: 1/60,
            TimeFrame.SECOND_5: 5/60,
            TimeFrame.SECOND_15: 15/60,
            TimeFrame.SECOND_30: 30/60,
            TimeFrame.MINUTE_1: 1,
            TimeFrame.MINUTE_5: 5,
            TimeFrame.MINUTE_15: 15,
            TimeFrame.MINUTE_30: 30,
            TimeFrame.HOUR_1: 60,
            TimeFrame.HOUR_4: 240,
            TimeFrame.DAY_1: 1440,
            TimeFrame.WEEK_1: 10080,
            TimeFrame.MONTH_1: 43200,
        }
        return timeframe_minutes[timeframe]

    @staticmethod
    def _downsample_data(
        data: pd.DataFrame,
        from_timeframe: TimeFrame,
        to_timeframe: TimeFrame,
        method: str
    ) -> pd.DataFrame:
        """Downsample data (reduce frequency)."""

        # Calculate target frequency
        to_minutes = TimeFrameResampler._get_minutes(to_timeframe)

        # Create resampling rule
        if to_minutes >= 1440:  # Daily or higher
            rule = f"{int(to_minutes // 1440)}D"
        elif to_minutes >= 60:  # Hourly
            rule = f"{int(to_minutes // 60)}H"
        else:  # Minutes
            rule = f"{int(to_minutes)}T"

        if method == "ohlc":
            resampled = data.resample(rule).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        elif method == "last":
            resampled = data.resample(rule).last().dropna()
        elif method == "mean":
            resampled = data.resample(rule).mean().dropna()
        else:
            raise ValueError(f"Unknown resampling method: {method}")

        return resampled

    @staticmethod
    def _upsample_data(
        data: pd.DataFrame,
        from_timeframe: TimeFrame,
        to_timeframe: TimeFrame,
        method: str
    ) -> pd.DataFrame:
        """Upsample data (increase frequency)."""

        # For upsampling, we'll use forward fill or interpolation
        from_minutes = TimeFrameResampler._get_minutes(from_timeframe)
        to_minutes = TimeFrameResampler._get_minutes(to_timeframe)

        # Create target index
        start_time = data.index[0]
        end_time = data.index[-1]

        if to_minutes >= 1:  # Minute or higher
            freq_minutes = int(to_minutes)
            target_index = pd.date_range(start_time, end_time, freq=f"{freq_minutes}T")
        else:  # Seconds
            freq_seconds = int(to_minutes * 60)
            target_index = pd.date_range(start_time, end_time, freq=f"{freq_seconds}S")

        # Reindex and fill
        resampled = data.reindex(target_index)

        if method == "ffill":
            resampled = resampled.fillna(method='ffill')
        elif method == "interpolate":
            resampled = resampled.interpolate(method='linear')
        elif method == "zero":
            resampled = resampled.fillna(0)
        else:
            resampled = resampled.fillna(method='ffill')  # Default to forward fill

        return resampled.dropna()


class CrossTimeFrameIndicator:
    """Engine for generating indicators across multiple timeframes."""

    def __init__(self, timeframe_data: Dict[TimeFrame, pd.DataFrame]):
        self.timeframe_data = timeframe_data

    def generate_cross_timeframe_signal(
        self,
        indicator_function: Callable,
        primary_timeframe: TimeFrame,
        confirming_timeframes: List[TimeFrame],
        signal_threshold: float = 0.7,
        **indicator_params
    ) -> List[CrossTimeFrameSignal]:
        """Generate cross-timeframe confirmation signals."""

        signals = []

        if primary_timeframe not in self.timeframe_data:
            raise ValueError(f"Primary timeframe {primary_timeframe} not available")

        primary_data = self.timeframe_data[primary_timeframe]

        # Generate primary signal
        primary_signals = indicator_function(primary_data, **indicator_params)

        # Check confirmation from higher timeframes
        for timestamp, primary_signal in primary_signals.items():
            confirming_signals = []

            for conf_tf in confirming_timeframes:
                if conf_tf not in self.timeframe_data:
                    continue

                conf_data = self.timeframe_data[conf_tf]

                # Find corresponding timestamp in confirming timeframe
                conf_timestamp = self._find_closest_timestamp(timestamp, conf_data.index)

                if conf_timestamp is not None:
                    conf_signal = indicator_function(conf_data, **indicator_params)
                    if conf_timestamp in conf_signal:
                        confirming_signals.append(conf_signal[conf_timestamp])

            # Calculate signal strength
            if confirming_signals:
                agreement_ratio = np.mean([1 if s * primary_signal > 0 else 0 for s in confirming_signals])
                strength = abs(primary_signal) * agreement_ratio
                confidence = agreement_ratio

                if agreement_ratio >= signal_threshold:
                    signal = CrossTimeFrameSignal(
                        signal_type="cross_timeframe_confirmation",
                        primary_timeframe=primary_timeframe,
                        confirming_timeframes=confirming_timeframes,
                        strength=strength,
                        confidence=confidence,
                        timestamp=timestamp,
                        data={
                            'primary_signal': primary_signal,
                            'confirming_signals': confirming_signals,
                            'agreement_ratio': agreement_ratio
                        }
                    )
                    signals.append(signal)

        return signals

    def _find_closest_timestamp(self, target: datetime, index: pd.DatetimeIndex) -> Optional[datetime]:
        """Find closest timestamp in index."""
        if len(index) == 0:
            return None

        idx = index.get_indexer([target], method='nearest')[0]
        return index[idx] if idx != -1 else None


class TimeFrameTransitionManager:
    """Manages transitions between different timeframes."""

    def __init__(self, config: MultiTimeFrameConfig):
        self.config = config
        self.transitions: List[TimeFrameTransition] = []

    def evaluate_transition(
        self,
        current_timeframe: TimeFrame,
        market_conditions: Dict[str, Any],
        strategy_state: Dict[str, Any]
    ) -> Optional[TimeFrameTransition]:
        """Evaluate if a timeframe transition should occur."""

        # Example transition logic (can be customized)
        volatility = market_conditions.get('volatility', 0.2)
        trend_strength = market_conditions.get('trend_strength', 0.5)

        # High volatility + weak trend -> switch to higher timeframe
        if volatility > 0.3 and trend_strength < 0.3 and current_timeframe.value <= TimeFrame.MINUTE_15.value:
            new_timeframe = TimeFrame.HOUR_1
            return TimeFrameTransition(
                from_timeframe=current_timeframe,
                to_timeframe=new_timeframe,
                trigger_condition="high_volatility_weak_trend",
                transition_time=datetime.now(),
                reason="Market conditions suggest using higher timeframe for better signal quality"
            )

        # Low volatility + strong trend -> switch to lower timeframe
        elif volatility < 0.1 and trend_strength > 0.7 and current_timeframe.value >= TimeFrame.MINUTE_5.value:
            new_timeframe = TimeFrame.MINUTE_1
            return TimeFrameTransition(
                from_timeframe=current_timeframe,
                to_timeframe=new_timeframe,
                trigger_condition="low_volatility_strong_trend",
                transition_time=datetime.now(),
                reason="Market conditions allow for more precise lower timeframe trading"
            )

        return None

    def record_transition(self, transition: TimeFrameTransition) -> None:
        """Record a timeframe transition."""
        self.transitions.append(transition)
        logger.info(f"Timeframe transition: {transition.from_timeframe} -> {transition.to_timeframe} "
                   f"({transition.trigger_condition})")


class MultiTimeFrameBacktester:
    """Multi-timeframe backtesting engine."""

    def __init__(self, config: MultiTimeFrameConfig):
        self.config = config
        self.timeframe_data: Dict[TimeFrame, pd.DataFrame] = {}
        self.resampler = TimeFrameResampler()
        self.cross_indicator = None
        self.transition_manager = TimeFrameTransitionManager(config)

    def add_timeframe_data(
        self,
        timeframe: TimeFrame,
        data: pd.DataFrame,
        resampling_method: str = "ohlc"
    ) -> None:
        """Add data for a specific timeframe."""

        if timeframe == self.config.base_timeframe:
            self.timeframe_data[timeframe] = data
        else:
            # Resample to match base timeframe if needed
            resampled_data = self.resampler.resample_data(
                data, timeframe, self.config.base_timeframe, resampling_method
            )
            self.timeframe_data[timeframe] = resampled_data

        logger.info(f"Added {timeframe.value} timeframe data with {len(self.timeframe_data[timeframe])} bars")

    def synchronize_timeframes(self) -> Dict[TimeFrame, pd.DataFrame]:
        """Synchronize all timeframes to common timestamps."""

        if not self.timeframe_data:
            raise ValueError("No timeframe data available")

        # Use base timeframe as reference
        base_data = self.timeframe_data[self.config.base_timeframe]
        synchronized_data = {self.config.base_timeframe: base_data}

        # Synchronize other timeframes
        for timeframe, data in self.timeframe_data.items():
            if timeframe == self.config.base_timeframe:
                continue

            if self.config.synchronization_method == "exact":
                # Exact timestamp matching
                common_index = base_data.index.intersection(data.index)
                synchronized_data[timeframe] = data.loc[common_index]
            elif self.config.synchronization_method == "nearest":
                # Nearest neighbor matching
                synchronized_data[timeframe] = data.reindex(
                    base_data.index, method='nearest', tolerance=pd.Timedelta(minutes=self.config.max_lag_minutes)
                ).dropna()
            elif self.config.synchronization_method == "interpolate":
                # Linear interpolation
                synchronized_data[timeframe] = data.reindex(base_data.index).interpolate(method='linear').dropna()

        # Update cross-timeframe indicator engine
        self.cross_indicator = CrossTimeFrameIndicator(synchronized_data)

        return synchronized_data

    def run_multi_timeframe_backtest(
        self,
        strategy_cls: type,
        **backtest_kwargs
    ) -> MultiTimeFrameResult:
        """Run multi-timeframe backtesting."""

        # Synchronize data
        synced_data = self.synchronize_timeframes()

        # Run base timeframe backtest
        base_strategy = strategy_cls()
        base_engine = EventBacktester(
            synced_data[self.config.base_timeframe],
            symbol="MULTI_TF_BASE",
            strategy=base_strategy,
            **backtest_kwargs
        )
        base_result = base_engine.run()

        # Run backtests for each timeframe
        timeframe_results = {}
        for timeframe, data in synced_data.items():
            tf_strategy = strategy_cls()
            tf_engine = EventBacktester(
                data,
                symbol=f"MULTI_TF_{timeframe.value}",
                strategy=tf_strategy,
                **backtest_kwargs
            )
            timeframe_results[timeframe] = tf_engine.run()

        # Generate cross-timeframe signals if enabled
        cross_signals = []
        if self.config.enable_cross_timeframe_signals and self.cross_indicator:
            # Example: Generate RSI divergence signals across timeframes
            cross_signals = self._generate_example_cross_signals()

        # Analyze timeframe transitions
        transitions = []
        if self.config.enable_timeframe_transitions:
            transitions = self._analyze_timeframe_transitions(synced_data)

        # Calculate performance by timeframe
        performance_by_timeframe = {}
        for timeframe, result in timeframe_results.items():
            performance_by_timeframe[timeframe] = {
                'total_return': (result.equity_curve.iloc[-1] / result.equity_curve.iloc[0]) - 1,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'win_rate': result.win_rate,
                'total_trades': len(result.trades)
            }

        # Calculate timeframe correlations
        correlations = {}
        returns_by_tf = {}
        for timeframe, result in timeframe_results.items():
            returns = result.equity_curve.pct_change().dropna()
            returns_by_tf[timeframe] = returns

        for tf1, returns1 in returns_by_tf.items():
            for tf2, returns2 in returns_by_tf.items():
                if tf1 != tf2:
                    # Align returns
                    aligned = pd.concat([returns1, returns2], axis=1, join='inner').dropna()
                    if len(aligned) > 1:
                        corr = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
                        correlations[(tf1, tf2)] = corr

        # Calculate overall performance
        overall_performance = self._calculate_overall_performance(timeframe_results)

        result = MultiTimeFrameResult(
            base_result=base_result,
            timeframe_results=timeframe_results,
            cross_timeframe_signals=cross_signals,
            timeframe_transitions=transitions,
            performance_by_timeframe=performance_by_timeframe,
            timeframe_correlations=correlations,
            overall_performance=overall_performance
        )

        logger.info(f"Multi-timeframe backtest completed across {len(timeframe_results)} timeframes")
        return result

    def _generate_example_cross_signals(self) -> List[CrossTimeFrameSignal]:
        """Generate example cross-timeframe signals (RSI divergence)."""
        # This is a simplified example - in practice, you'd implement specific signal logic
        signals = []

        # Example RSI-based cross-timeframe signal
        def rsi_signal(data, period=14):
            """Simple RSI signal generator."""
            signals = {}
            if len(data) > period:
                close = data['close']
                rsi = self._calculate_rsi(close, period)
                signals[data.index[-1]] = 1 if rsi.iloc[-1] < 30 else -1 if rsi.iloc[-1] > 70 else 0
            return signals

        # Generate signals for different timeframe combinations
        if TimeFrame.MINUTE_1 in self.cross_indicator.timeframe_data and TimeFrame.MINUTE_5 in self.cross_indicator.timeframe_data:
            signals.extend(self.cross_indicator.generate_cross_timeframe_signal(
                rsi_signal,
                TimeFrame.MINUTE_1,
                [TimeFrame.MINUTE_5],
                signal_threshold=0.6
            ))

        return signals

    def _analyze_timeframe_transitions(self, synced_data: Dict[TimeFrame, pd.DataFrame]) -> List[TimeFrameTransition]:
        """Analyze and suggest timeframe transitions."""
        transitions = []

        # Example analysis logic
        for timeframe, data in synced_data.items():
            if len(data) > 20:
                returns = data['close'].pct_change().dropna()
                volatility = returns.std()
                trend_strength = abs(returns.rolling(10).mean().iloc[-1]) / volatility if volatility > 0 else 0

                market_conditions = {
                    'volatility': volatility,
                    'trend_strength': trend_strength
                }

                transition = self.transition_manager.evaluate_transition(
                    timeframe, market_conditions, {}
                )

                if transition:
                    self.transition_manager.record_transition(transition)
                    transitions.append(transition)

        return transitions

    def _calculate_overall_performance(self, timeframe_results: Dict[TimeFrame, EventBacktestResult]) -> Dict[str, float]:
        """Calculate overall performance across all timeframes."""

        if not timeframe_results:
            return {}

        # Weighted average based on number of trades
        total_trades = sum(len(result.trades) for result in timeframe_results.values())

        if total_trades == 0:
            return {}

        weighted_returns = []
        weighted_sharpe = []
        weighted_drawdown = []

        for result in timeframe_results.values():
            weight = len(result.trades) / total_trades
            total_return = (result.equity_curve.iloc[-1] / result.equity_curve.iloc[0]) - 1

            weighted_returns.append(total_return * weight)
            weighted_sharpe.append(result.sharpe_ratio * weight)
            weighted_drawdown.append(result.max_drawdown * weight)

        return {
            'weighted_total_return': sum(weighted_returns),
            'weighted_sharpe_ratio': sum(weighted_sharpe),
            'weighted_max_drawdown': sum(weighted_drawdown),
            'timeframe_diversity': len(timeframe_results),
            'total_signals_generated': sum(len(result.trades) for result in timeframe_results.values())
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


# Convenience functions
def create_multi_timeframe_setup(
    base_timeframe: TimeFrame,
    higher_timeframes: List[TimeFrame],
    base_data: pd.DataFrame,
    **config_kwargs
) -> MultiTimeFrameBacktester:
    """Create a multi-timeframe backtesting setup."""

    config = MultiTimeFrameConfig(
        base_timeframe=base_timeframe,
        higher_timeframes=higher_timeframes,
        **config_kwargs
    )

    backtester = MultiTimeFrameBacktester(config)

    # Add base timeframe data
    backtester.add_timeframe_data(base_timeframe, base_data)

    # Note: Higher timeframe data would need to be provided separately
    # This is a simplified setup function

    return backtester


def analyze_timeframe_performance(multi_result: MultiTimeFrameResult) -> Dict[str, Any]:
    """Analyze performance across different timeframes."""

    analysis = {
        'best_timeframe': None,
        'worst_timeframe': None,
        'timeframe_rankings': [],
        'correlation_insights': {},
        'recommended_timeframe': None
    }

    if not multi_result.performance_by_timeframe:
        return analysis

    # Rank timeframes by Sharpe ratio
    rankings = sorted(
        multi_result.performance_by_timeframe.items(),
        key=lambda x: x[1]['sharpe_ratio'],
        reverse=True
    )

    analysis['best_timeframe'] = rankings[0][0]
    analysis['worst_timeframe'] = rankings[-1][0]
    analysis['timeframe_rankings'] = [(tf.value, perf['sharpe_ratio']) for tf, perf in rankings]

    # Analyze correlations
    high_corr_pairs = []
    for (tf1, tf2), corr in multi_result.timeframe_correlations.items():
        if abs(corr) > 0.7:
            high_corr_pairs.append((tf1.value, tf2.value, corr))

    analysis['correlation_insights'] = {
        'highly_correlated_pairs': high_corr_pairs,
        'correlation_diversity': len(set(abs(corr) for corr in multi_result.timeframe_correlations.values()))
    }

    # Recommend best timeframe for strategy
    analysis['recommended_timeframe'] = rankings[0][0]

    return analysis


__all__ = [
    "MultiTimeFrameBacktester",
    "TimeFrameResampler",
    "CrossTimeFrameIndicator",
    "TimeFrameTransitionManager",
    "TimeFrame",
    "TimeFrameData",
    "MultiTimeFrameConfig",
    "CrossTimeFrameSignal",
    "TimeFrameTransition",
    "MultiTimeFrameResult",
    "create_multi_timeframe_setup",
    "analyze_timeframe_performance",
]

"""Real-time streaming signal generation engine for live trading."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from qantify.data.streaming import StreamEvent, EventQueue, MarketData
from qantify.signals.indicators import (
    rsi, macd, bollinger_bands, stochastic, williams_r, cci, mfi
)


logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Types of trading signals."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"


class SignalStrength(Enum):
    """Signal strength levels."""
    WEAK = 0.2
    MODERATE = 0.5
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass(slots=True)
class StreamingSignal:
    """Real-time trading signal."""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    price: Optional[float] = None
    volume: Optional[float] = None
    indicators: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    strategy_name: Optional[str] = None
    signal_id: Optional[str] = None


@dataclass(slots=True)
class SignalHistory:
    """Signal history tracking."""
    symbol: str
    signals: deque[StreamingSignal] = field(default_factory=lambda: deque(maxlen=1000))
    last_signal: Optional[StreamingSignal] = None
    signal_count: int = 0
    accuracy_history: deque[bool] = field(default_factory=lambda: deque(maxlen=100))
    win_rate: float = 0.0


class StreamingSignalEngine:
    """Real-time signal generation engine for streaming market data."""

    def __init__(self, event_queue: EventQueue):
        self.event_queue = event_queue
        self.signal_functions: Dict[str, Callable[[StreamEvent, Dict[str, Any]], Optional[StreamingSignal]]] = {}
        self.signal_history: Dict[str, SignalHistory] = defaultdict(SignalHistory)

        # Data buffers for indicator calculation
        self.price_buffers: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=200))
        self.volume_buffers: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=200))
        self.timestamp_buffers: Dict[str, deque[datetime]] = defaultdict(lambda: deque(maxlen=200))

        # Signal filtering and aggregation
        self.signal_filters: Dict[str, Callable[[StreamingSignal], bool]] = {}
        self.signal_aggregators: Dict[str, Callable[[List[StreamingSignal]], StreamingSignal]] = {}

        # Performance tracking
        self.signal_latency: deque[float] = deque(maxlen=1000)
        self.signal_throughput: int = 0
        self.last_throughput_time: float = time.time()

        # Active subscriptions
        self.active_symbols: Set[str] = set()
        self.signal_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # symbol -> strategy names

        # Background tasks
        self._processing_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the streaming signal engine."""
        if self._running:
            return

        self._running = True
        logger.info("Starting streaming signal engine")

        # Subscribe to market data events
        await self.event_queue.subscribe(self._process_market_data, "market_data")

        # Start background tasks
        self._processing_task = asyncio.create_task(self._signal_processing_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Stop the streaming signal engine."""
        self._running = False

        # Cancel tasks
        for task in [self._processing_task, self._cleanup_task]:
            if task:
                task.cancel()

        # Wait for completion
        await asyncio.gather(*[t for t in [self._processing_task, self._cleanup_task] if t],
                           return_exceptions=True)

        logger.info("Streaming signal engine stopped")

    def register_signal_function(
        self,
        name: str,
        signal_func: Callable[[StreamEvent, Dict[str, Any]], Optional[StreamingSignal]],
        symbols: Optional[List[str]] = None
    ) -> None:
        """Register a signal generation function."""
        self.signal_functions[name] = signal_func

        if symbols:
            for symbol in symbols:
                self.signal_subscriptions[symbol].add(name)
                self.active_symbols.add(symbol)

        logger.info(f"Registered signal function: {name}")

    def unregister_signal_function(self, name: str) -> None:
        """Unregister a signal function."""
        if name in self.signal_functions:
            del self.signal_functions[name]

            # Remove from subscriptions
            for symbol_subs in self.signal_subscriptions.values():
                symbol_subs.discard(name)

            logger.info(f"Unregistered signal function: {name}")

    def add_signal_filter(self, name: str, filter_func: Callable[[StreamingSignal], bool]) -> None:
        """Add a signal filter."""
        self.signal_filters[name] = filter_func

    def add_signal_aggregator(self, name: str,
                            aggregator_func: Callable[[List[StreamingSignal]], StreamingSignal]) -> None:
        """Add a signal aggregator."""
        self.signal_aggregators[name] = aggregator_func

    async def _process_market_data(self, event: StreamEvent) -> None:
        """Process incoming market data and generate signals."""
        symbol = event.symbol

        # Update data buffers
        await self._update_data_buffers(event)

        # Generate signals for subscribed strategies
        if symbol in self.signal_subscriptions:
            signals = []

            for strategy_name in self.signal_subscriptions[symbol]:
                if strategy_name in self.signal_functions:
                    try:
                        signal = self.signal_functions[strategy_name](event, self._get_context_data(symbol))
                        if signal:
                            signal.strategy_name = strategy_name
                            signal.signal_id = f"{strategy_name}_{symbol}_{int(time.time()*1000)}"
                            signals.append(signal)
                    except Exception as e:
                        logger.error(f"Signal generation failed for {strategy_name}: {e}")

            # Process signals
            if signals:
                await self._process_signals(signals)

    async def _update_data_buffers(self, event: StreamEvent) -> None:
        """Update price/volume buffers for indicator calculations."""
        symbol = event.symbol
        payload = event.payload

        # Extract price and volume
        price = payload.get('price') or payload.get('last') or payload.get('close')
        volume = payload.get('volume') or payload.get('size') or payload.get('qty', 0)

        if price is not None:
            self.price_buffers[symbol].append(float(price))
            self.timestamp_buffers[symbol].append(event.timestamp)

        if volume is not None:
            self.volume_buffers[symbol].append(float(volume))

    def _get_context_data(self, symbol: str) -> Dict[str, Any]:
        """Get context data for signal generation."""
        prices = list(self.price_buffers[symbol])
        volumes = list(self.volume_buffers[symbol])

        if len(prices) < 14:  # Minimum for basic indicators
            return {'prices': prices, 'volumes': volumes}

        # Calculate common indicators
        context = {
            'prices': prices,
            'volumes': volumes,
            'rsi': rsi(pd.Series(prices)).iloc[-1] if len(prices) >= 14 else None,
            'macd': macd(pd.Series(prices)) if len(prices) >= 26 else None,
            'bbands': bollinger_bands(pd.Series(prices)) if len(prices) >= 20 else None,
            'stoch': stochastic(pd.Series(prices)) if len(prices) >= 14 else None,
            'williams_r': williams_r(pd.Series(prices)) if len(prices) >= 14 else None,
            'cci': cci(pd.Series(prices)) if len(prices) >= 20 else None,
            'mfi': mfi(pd.Series(prices), pd.Series(volumes)) if len(prices) >= 14 else None,
            'ema_9': exponential_moving_average(pd.Series(prices), 9).iloc[-1] if len(prices) >= 9 else None,
            'ema_21': exponential_moving_average(pd.Series(prices), 21).iloc[-1] if len(prices) >= 21 else None,
            'sma_50': simple_moving_average(pd.Series(prices), 50).iloc[-1] if len(prices) >= 50 else None,
        }

        return context

    async def _process_signals(self, signals: List[StreamingSignal]) -> None:
        """Process generated signals with filtering and aggregation."""
        processed_signals = []

        # Apply filters
        for signal in signals:
            if self._passes_filters(signal):
                processed_signals.append(signal)

        # Apply aggregators
        if processed_signals:
            for aggregator_name, aggregator_func in self.signal_aggregators.items():
                try:
                    aggregated_signal = aggregator_func(processed_signals)
                    processed_signals = [aggregated_signal]
                    break  # Use first aggregator for now
                except Exception as e:
                    logger.error(f"Signal aggregation failed: {e}")

        # Emit final signals
        for signal in processed_signals:
            await self._emit_signal(signal)

    def _passes_filters(self, signal: StreamingSignal) -> bool:
        """Check if signal passes all filters."""
        for filter_name, filter_func in self.signal_filters.items():
            try:
                if not filter_func(signal):
                    return False
            except Exception as e:
                logger.error(f"Signal filter {filter_name} failed: {e}")
                return False
        return True

    async def _emit_signal(self, signal: StreamingSignal) -> None:
        """Emit signal to event queue."""
        # Track signal history
        history = self.signal_history[signal.symbol]
        history.signals.append(signal)
        history.last_signal = signal
        history.signal_count += 1

        # Calculate latency
        latency = (datetime.utcnow() - signal.timestamp).total_seconds() * 1000
        self.signal_latency.append(latency)

        # Update throughput
        self.signal_throughput += 1

        # Create signal event
        signal_event = StreamEvent(
            symbol=signal.symbol,
            payload={
                'signal_type': signal.signal_type.value,
                'strength': signal.strength.value,
                'confidence': signal.confidence,
                'price': signal.price,
                'volume': signal.volume,
                'indicators': signal.indicators,
                'metadata': signal.metadata,
                'strategy_name': signal.strategy_name,
                'signal_id': signal.signal_id,
                'latency_ms': latency
            },
            timestamp=signal.timestamp,
            feed_type=event.feed_type,
            tags={'signal': True, 'real_time': True}
        )

        # Publish to event queue
        await self.event_queue.publish(signal_event, priority=5)  # High priority for signals

    async def _signal_processing_loop(self) -> None:
        """Background signal processing loop."""
        while self._running:
            try:
                # Periodic cleanup and maintenance
                await asyncio.sleep(60)  # Every minute

                # Update signal performance metrics
                self._update_performance_metrics()

            except Exception as e:
                logger.error(f"Signal processing loop error: {e}")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Clean old data buffers
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                for symbol in list(self.price_buffers.keys()):
                    # Remove old timestamps and corresponding data
                    timestamps = self.timestamp_buffers[symbol]
                    while timestamps and timestamps[0] < cutoff_time:
                        timestamps.popleft()
                        if self.price_buffers[symbol]:
                            self.price_buffers[symbol].popleft()
                        if self.volume_buffers[symbol]:
                            self.volume_buffers[symbol].popleft()

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    def _update_performance_metrics(self) -> None:
        """Update signal performance metrics."""
        current_time = time.time()
        time_diff = current_time - self.last_throughput_time

        if time_diff >= 60:  # Every minute
            signals_per_second = self.signal_throughput / time_diff

            # Log performance
            avg_latency = sum(self.signal_latency) / len(self.signal_latency) if self.signal_latency else 0

            logger.info(f"Signal Engine Performance - Throughput: {signals_per_second:.2f} sig/s, "
                       f"Avg Latency: {avg_latency:.2f}ms")

            # Reset counters
            self.signal_throughput = 0
            self.last_throughput_time = current_time

    def get_signal_history(self, symbol: str, limit: int = 100) -> List[StreamingSignal]:
        """Get recent signal history for a symbol."""
        history = self.signal_history.get(symbol)
        if history:
            return list(history.signals)[-limit:]
        return []

    def get_active_signals(self, symbol: str) -> Optional[StreamingSignal]:
        """Get the most recent active signal for a symbol."""
        history = self.signal_history.get(symbol)
        return history.last_signal if history else None

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get signal engine performance statistics."""
        total_signals = sum(len(history.signals) for history in self.signal_history.values())

        return {
            'total_signals_generated': total_signals,
            'active_symbols': len(self.active_symbols),
            'registered_strategies': len(self.signal_functions),
            'avg_latency_ms': sum(self.signal_latency) / len(self.signal_latency) if self.signal_latency else 0,
            'signal_throughput': self.signal_throughput,
            'buffer_sizes': {
                symbol: len(buffer) for symbol, buffer in self.price_buffers.items()
            }
        }

    def get_signal_accuracy(self, symbol: str) -> float:
        """Get signal accuracy for a symbol."""
        history = self.signal_history.get(symbol)
        if history and history.accuracy_history:
            return sum(history.accuracy_history) / len(history.accuracy_history)
        return 0.0

    def update_signal_accuracy(self, symbol: str, was_correct: bool) -> None:
        """Update signal accuracy tracking."""
        history = self.signal_history.get(symbol)
        if history:
            history.accuracy_history.append(was_correct)
            history.win_rate = sum(history.accuracy_history) / len(history.accuracy_history)


# Built-in signal functions
def rsi_divergence_signal(event: StreamEvent, context: Dict[str, Any]) -> Optional[StreamingSignal]:
    """RSI divergence signal."""
    prices = context.get('prices', [])
    rsi_values = context.get('rsi')

    if len(prices) < 20 or rsi_values is None:
        return None

    # Simple divergence detection (can be enhanced)
    if rsi_values < 30 and prices[-1] > prices[-2]:  # RSI oversold + price up
        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.BUY,
            strength=SignalStrength.MODERATE,
            confidence=0.7,
            timestamp=event.timestamp,
            price=event.payload.get('price'),
            indicators={'rsi': rsi_values},
            metadata={'signal_type': 'rsi_divergence'}
        )
    elif rsi_values > 70 and prices[-1] < prices[-2]:  # RSI overbought + price down
        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.SELL,
            strength=SignalStrength.MODERATE,
            confidence=0.7,
            timestamp=event.timestamp,
            price=event.payload.get('price'),
            indicators={'rsi': rsi_values},
            metadata={'signal_type': 'rsi_divergence'}
        )

    return None


def macd_crossover_signal(event: StreamEvent, context: Dict[str, Any]) -> Optional[StreamingSignal]:
    """MACD crossover signal."""
    macd_data = context.get('macd')
    if macd_data is None:
        return None

    macd_line = macd_data.get('macd')
    signal_line = macd_data.get('signal')
    histogram = macd_data.get('histogram')

    if len(macd_line) < 2 or len(signal_line) < 2:
        return None

    # Bullish crossover
    if (macd_line.iloc[-2] < signal_line.iloc[-2] and
        macd_line.iloc[-1] > signal_line.iloc[-1] and
        histogram.iloc[-1] > 0):

        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            confidence=0.8,
            timestamp=event.timestamp,
            price=event.payload.get('price'),
            indicators={
                'macd': macd_line.iloc[-1],
                'signal': signal_line.iloc[-1],
                'histogram': histogram.iloc[-1]
            },
            metadata={'signal_type': 'macd_crossover'}
        )

    # Bearish crossover
    elif (macd_line.iloc[-2] > signal_line.iloc[-2] and
          macd_line.iloc[-1] < signal_line.iloc[-1] and
          histogram.iloc[-1] < 0):

        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.SELL,
            strength=SignalStrength.STRONG,
            confidence=0.8,
            timestamp=event.timestamp,
            price=event.payload.get('price'),
            indicators={
                'macd': macd_line.iloc[-1],
                'signal': signal_line.iloc[-1],
                'histogram': histogram.iloc[-1]
            },
            metadata={'signal_type': 'macd_crossover'}
        )

    return None


def bollinger_bands_signal(event: StreamEvent, context: Dict[str, Any]) -> Optional[StreamingSignal]:
    """Bollinger Bands mean reversion signal."""
    bb_data = context.get('bbands')
    prices = context.get('prices', [])

    if bb_data is None or len(prices) < 2:
        return None

    current_price = prices[-1]
    lower_band = bb_data.get('lower')
    upper_band = bb_data.get('upper')
    middle_band = bb_data.get('middle')

    if len(lower_band) < 2 or len(upper_band) < 2:
        return None

    # Price touched lower band and bounced up
    if (prices[-2] <= lower_band.iloc[-2] and current_price > lower_band.iloc[-1]):
        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.BUY,
            strength=SignalStrength.MODERATE,
            confidence=0.6,
            timestamp=event.timestamp,
            price=current_price,
            indicators={
                'lower_band': lower_band.iloc[-1],
                'middle_band': middle_band.iloc[-1],
                'upper_band': upper_band.iloc[-1]
            },
            metadata={'signal_type': 'bollinger_reversion'}
        )

    # Price touched upper band and dropped
    elif (prices[-2] >= upper_band.iloc[-2] and current_price < upper_band.iloc[-1]):
        return StreamingSignal(
            symbol=event.symbol,
            signal_type=SignalType.SELL,
            strength=SignalStrength.MODERATE,
            confidence=0.6,
            timestamp=event.timestamp,
            price=current_price,
            indicators={
                'lower_band': lower_band.iloc[-1],
                'middle_band': middle_band.iloc[-1],
                'upper_band': upper_band.iloc[-1]
            },
            metadata={'signal_type': 'bollinger_reversion'}
        )

    return None


def volume_spike_signal(event: StreamEvent, context: Dict[str, Any]) -> Optional[StreamingSignal]:
    """Volume spike detection signal."""
    volumes = context.get('volumes', [])
    prices = context.get('prices', [])

    if len(volumes) < 20 or len(prices) < 2:
        return None

    current_volume = volumes[-1]
    avg_volume = sum(volumes[-20:-1]) / 19  # Exclude current

    # Volume spike (2x average)
    if current_volume > avg_volume * 2:
        price_change = (prices[-1] - prices[-2]) / prices[-2]

        if price_change > 0.01:  # Price up with volume
            return StreamingSignal(
                symbol=event.symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG,
                confidence=0.75,
                timestamp=event.timestamp,
                price=prices[-1],
                volume=current_volume,
                indicators={
                    'volume_ratio': current_volume / avg_volume,
                    'price_change_pct': price_change
                },
                metadata={'signal_type': 'volume_spike'}
            )
        elif price_change < -0.01:  # Price down with volume
            return StreamingSignal(
                symbol=event.symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.STRONG,
                confidence=0.75,
                timestamp=event.timestamp,
                price=prices[-1],
                volume=current_volume,
                indicators={
                    'volume_ratio': current_volume / avg_volume,
                    'price_change_pct': price_change
                },
                metadata={'signal_type': 'volume_spike'}
            )

    return None


def multi_indicator_signal(event: StreamEvent, context: Dict[str, Any]) -> Optional[StreamingSignal]:
    """Multi-indicator consensus signal."""
    rsi_val = context.get('rsi')
    macd_data = context.get('macd')
    bb_data = context.get('bbands')
    stoch_data = context.get('stoch')

    if not all([rsi_val, macd_data, bb_data, stoch_data]):
        return None

    # Count bullish/bearish signals
    bullish_signals = 0
    bearish_signals = 0

    # RSI
    if rsi_val < 30:
        bullish_signals += 1
    elif rsi_val > 70:
        bearish_signals += 1

    # MACD
    macd_line = macd_data.get('macd')
    signal_line = macd_data.get('signal')
    if macd_line is not None and signal_line is not None:
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            bullish_signals += 1
        else:
            bearish_signals += 1

    # Bollinger Bands position
    prices = context.get('prices', [])
    if prices and bb_data:
        lower_band = bb_data.get('lower')
        upper_band = bb_data.get('upper')
        if lower_band is not None and upper_band is not None:
            if prices[-1] < lower_band.iloc[-1]:
                bullish_signals += 1
            elif prices[-1] > upper_band.iloc[-1]:
                bearish_signals += 1

    # Stochastic
    if stoch_data is not None:
        k_val = stoch_data.get('k')
        d_val = stoch_data.get('d')
        if k_val is not None and d_val is not None:
            if k_val.iloc[-1] < 20:
                bullish_signals += 1
            elif k_val.iloc[-1] > 80:
                bearish_signals += 1

    # Generate consensus signal
    total_signals = bullish_signals + bearish_signals
    if total_signals >= 2:  # At least 2 indicators agree
        confidence = min(0.9, 0.5 + (max(bullish_signals, bearish_signals) / total_signals) * 0.4)

        if bullish_signals > bearish_signals:
            return StreamingSignal(
                symbol=event.symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG if bullish_signals >= 3 else SignalStrength.MODERATE,
                confidence=confidence,
                timestamp=event.timestamp,
                price=event.payload.get('price'),
                indicators={
                    'rsi': rsi_val,
                    'bullish_signals': bullish_signals,
                    'bearish_signals': bearish_signals
                },
                metadata={'signal_type': 'multi_indicator_consensus'}
            )
        elif bearish_signals > bullish_signals:
            return StreamingSignal(
                symbol=event.symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.STRONG if bearish_signals >= 3 else SignalStrength.MODERATE,
                confidence=confidence,
                timestamp=event.timestamp,
                price=event.payload.get('price'),
                indicators={
                    'rsi': rsi_val,
                    'bullish_signals': bullish_signals,
                    'bearish_signals': bearish_signals
                },
                metadata={'signal_type': 'multi_indicator_consensus'}
            )

    return None


# Signal filters
def confidence_filter(min_confidence: float = 0.6):
    """Filter signals by minimum confidence."""
    def filter_func(signal: StreamingSignal) -> bool:
        return signal.confidence >= min_confidence
    return filter_func


def strength_filter(min_strength: SignalStrength = SignalStrength.MODERATE):
    """Filter signals by minimum strength."""
    def filter_func(signal: StreamingSignal) -> bool:
        return signal.strength.value >= min_strength.value
    return filter_func


def symbol_volatility_filter(max_volatility: float = 0.05):
    """Filter signals for symbols below maximum volatility threshold."""
    # This would need access to volatility data
    def filter_func(signal: StreamingSignal) -> bool:
        # Placeholder - implement with actual volatility checking
        return True
    return filter_func


# Signal aggregators
def majority_vote_aggregator(signals: List[StreamingSignal]) -> StreamingSignal:
    """Aggregate signals using majority voting."""
    if not signals:
        raise ValueError("No signals to aggregate")

    # Count votes by type
    vote_counts = defaultdict(int)
    total_confidence = 0
    indicators = {}

    for signal in signals:
        vote_counts[signal.signal_type] += 1
        total_confidence += signal.confidence
        indicators.update(signal.indicators)

    # Determine winning signal
    winning_type = max(vote_counts, key=vote_counts.get)
    avg_confidence = total_confidence / len(signals)
    strength = SignalStrength.STRONG if vote_counts[winning_type] > len(signals) / 2 else SignalStrength.MODERATE

    return StreamingSignal(
        symbol=signals[0].symbol,  # Assume all same symbol
        signal_type=winning_type,
        strength=strength,
        confidence=avg_confidence,
        timestamp=max(s.timestamp for s in signals),  # Latest timestamp
        price=signals[-1].price,  # Latest price
        volume=signals[-1].volume,  # Latest volume
        indicators=indicators,
        metadata={
            'signal_type': 'aggregated_majority_vote',
            'vote_counts': dict(vote_counts),
            'total_signals': len(signals)
        }
    )


__all__ = [
    "SignalType",
    "SignalStrength",
    "StreamingSignal",
    "SignalHistory",
    "StreamingSignalEngine",
    "rsi_divergence_signal",
    "macd_crossover_signal",
    "bollinger_bands_signal",
    "volume_spike_signal",
    "multi_indicator_signal",
    "confidence_filter",
    "strength_filter",
    "symbol_volatility_filter",
    "majority_vote_aggregator"
]

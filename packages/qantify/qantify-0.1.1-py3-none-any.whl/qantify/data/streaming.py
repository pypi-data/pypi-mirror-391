"""Advanced real-time streaming utilities for institutional-grade market data."""

from __future__ import annotations

import asyncio
import gzip
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin

import aiohttp
import pandas as pd

from qantify.core.utils import ensure_datetime


logger = logging.getLogger(__name__)


class DataFeedType(Enum):
    """Types of market data feeds."""
    TRADES = "trades"
    QUOTES = "quotes"
    ORDER_BOOK = "order_book"
    MARKET_DEPTH = "market_depth"
    TIME_AND_SALES = "time_and_sales"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
    OPTIONS = "options"
    FUTURES = "futures"
    CRYPTO = "crypto"


class FeedQuality(Enum):
    """Data feed quality levels."""
    REALTIME = "realtime"
    DELAYED = "delayed"
    SNAPSHOT = "snapshot"
    HISTORICAL = "historical"


class ConnectionStatus(Enum):
    """WebSocket connection status."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class DataNormalizationError(Exception):
    """Error during data normalization."""
    pass


class FeedConnectionError(Exception):
    """Error with feed connection."""
    pass


@dataclass(slots=True)
class StreamEvent:
    """Enhanced streaming event with metadata."""
    symbol: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    feed_type: DataFeedType = DataFeedType.TRADES
    feed_quality: FeedQuality = FeedQuality.REALTIME
    sequence_number: Optional[int] = None
    source: Optional[str] = None
    normalized: bool = False
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketData:
    """Normalized market data structure."""
    symbol: str
    timestamp: datetime
    feed_type: DataFeedType

    # Common fields
    price: Optional[float] = None
    volume: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None

    # Order book data
    bids: List[Tuple[float, float]] = field(default_factory=list)  # [(price, size), ...]
    asks: List[Tuple[float, float]] = field(default_factory=list)  # [(price, size), ...]

    # Trade data
    trade_id: Optional[str] = None
    trade_price: Optional[float] = None
    trade_volume: Optional[float] = None
    trade_side: Optional[str] = None  # 'buy', 'sell', 'unknown'

    # Quote data
    bid_exchange: Optional[str] = None
    ask_exchange: Optional[str] = None

    # Additional metadata
    source: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0  # 0.0 to 1.0


@dataclass(slots=True)
class FeedSubscription:
    """Feed subscription configuration."""
    symbols: Set[str]
    feed_types: Set[DataFeedType]
    quality: FeedQuality = FeedQuality.REALTIME
    parameters: Dict[str, Any] = field(default_factory=dict)
    active: bool = True


@dataclass(slots=True)
class ConnectionMetrics:
    """Connection performance metrics."""
    connection_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    messages_received: int = 0
    messages_processed: int = 0
    bytes_received: int = 0
    last_message_time: Optional[datetime] = None
    average_latency_ms: float = 0.0
    reconnect_count: int = 0
    uptime_seconds: float = 0.0


@dataclass(slots=True)
class DataQualityMetrics:
    """Data quality and completeness metrics."""
    symbols_tracked: int = 0
    data_points_received: int = 0
    missing_data_points: int = 0
    out_of_order_events: int = 0
    duplicate_events: int = 0
    normalization_errors: int = 0
    average_delay_ms: float = 0.0
    data_completeness: float = 1.0  # 0.0 to 1.0


class EventQueue:
    """Advanced asynchronous event queue with filtering and priority support."""

    def __init__(self, *, maxsize: int = 100_000, enable_filtering: bool = True) -> None:
        self._queue: asyncio.Queue[Tuple[StreamEvent, int]] = asyncio.Queue(maxsize=maxsize)  # (event, priority)
        self._subscribers: Dict[str, List[Callable[[StreamEvent], Awaitable[None]]]] = defaultdict(list)
        self._filters: Dict[str, Callable[[StreamEvent], bool]] = {}
        self._task: Optional[asyncio.Task[None]] = None
        self._running = False
        self._enable_filtering = enable_filtering

        # Performance metrics
        self.events_processed: int = 0
        self.events_filtered: int = 0
        self.queue_size_history: deque[int] = deque(maxlen=1000)
        self.processing_times: deque[float] = deque(maxlen=1000)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._dispatcher())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            # Send stop signal with high priority
            await self._queue.put((StreamEvent(symbol="__STOP__", payload={}), 999))
            await self._task
            self._task = None

    async def publish(self, event: StreamEvent, priority: int = 0) -> None:
        """Publish event with optional priority (higher = more important)."""
        await self._queue.put((event, priority))

    def subscribe(self, callback: Callable[[StreamEvent], Awaitable[None]],
                  filter_key: Optional[str] = None) -> str:
        """Subscribe to events with optional filtering."""
        subscription_id = f"sub_{id(callback)}_{time.time()}"
        self._subscribers[subscription_id].append(callback)

        if filter_key and self._enable_filtering:
            self._filters[subscription_id] = self._filters.get(filter_key, lambda e: True)

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        """Remove subscription."""
        self._subscribers.pop(subscription_id, None)
        self._filters.pop(subscription_id, None)

    def add_filter(self, filter_key: str, filter_func: Callable[[StreamEvent], bool]) -> None:
        """Add a named filter for subscriptions."""
        self._filters[filter_key] = filter_func

    async def _dispatcher(self) -> None:
        """Priority-based event dispatcher."""
        while self._running:
            try:
                # Get event with priority
                event, priority = await self._queue.get()
                start_time = time.time()

                if event.symbol == "__STOP__":
                    break

                # Track queue size
                self.queue_size_history.append(self._queue.qsize())

                # Dispatch to subscribers
                tasks = []

                for subscription_id, subscribers in self._subscribers.items():
                    # Apply filtering if enabled
                    if self._enable_filtering and subscription_id in self._filters:
                        if not self._filters[subscription_id](event):
                            self.events_filtered += 1
                            continue

                    # Add subscriber tasks
                    tasks.extend([subscriber(event) for subscriber in subscribers])

                # Execute all subscriber tasks
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Track metrics
                self.events_processed += 1
                processing_time = (time.time() - start_time) * 1000
                self.processing_times.append(processing_time)

            except Exception as e:
                logger.error(f"Event dispatcher error: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get queue performance metrics."""
        return {
            "events_processed": self.events_processed,
            "events_filtered": self.events_filtered,
            "current_queue_size": self._queue.qsize(),
            "avg_queue_size": sum(self.queue_size_history) / len(self.queue_size_history) if self.queue_size_history else 0,
            "avg_processing_time_ms": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            "active_subscriptions": len(self._subscribers),
            "total_filters": len(self._filters)
        }


class WebSocketStream:
    """Advanced WebSocket stream manager with connection resilience and data normalization."""

    def __init__(
        self,
        url: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        heartbeat_interval: int = 30,
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 10,
        enable_compression: bool = True,
        connection_timeout: int = 10,
        data_normalizer: Optional[Callable[[Dict[str, Any]], MarketData]] = None,
    ) -> None:
        self.url = url
        self._session = session
        self._owns_session = session is None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._heartbeat_interval = heartbeat_interval
        self._reconnect_interval = reconnect_interval
        self._max_reconnect_attempts = max_reconnect_attempts
        self._enable_compression = enable_compression
        self._connection_timeout = connection_timeout
        self._data_normalizer = data_normalizer

        # Connection state
        self._connected = False
        self._connecting = False
        self._reconnect_attempts = 0
        self._status = ConnectionStatus.DISCONNECTED

        # Tasks
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._reader_task: Optional[asyncio.Task[None]] = None

        # Data structures
        self.queue = EventQueue()
        self.subscriptions: Set[str] = set()
        self.pending_subscriptions: Set[str] = set()

        # Metrics
        self.metrics = ConnectionMetrics()
        self.data_metrics = DataQualityMetrics()

        # Sequence tracking for data integrity
        self.last_sequence_numbers: Dict[str, int] = {}
        self.expected_sequences: Dict[str, int] = {}

    async def __aenter__(self) -> "WebSocketStream":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        """Establish WebSocket connection with retry logic."""
        if self._connecting or self._connected:
            return

        self._connecting = True
        self._status = ConnectionStatus.CONNECTING
        self.metrics.connection_attempts += 1

        try:
            # Create session if needed
            if self._session is None:
                headers = {}
                if self._enable_compression:
                    headers['Accept-Encoding'] = 'gzip, deflate'
                self._session = aiohttp.ClientSession(headers=headers)

            # Connect with timeout
            self._ws = await asyncio.wait_for(
                self._session.ws_connect(
                    self.url,
                    compress=self._enable_compression,
                    heartbeat=self._heartbeat_interval
                ),
                timeout=self._connection_timeout
            )

            self._connected = True
            self._connecting = False
            self._status = ConnectionStatus.CONNECTED
            self._reconnect_attempts = 0
            self.metrics.successful_connections += 1
            self.metrics.uptime_seconds = time.time()

            logger.info(f"Connected to WebSocket: {self.url}")

            # Start background tasks
            await self.queue.start()
            self._heartbeat_task = asyncio.create_task(self._heartbeat())
            self._reader_task = asyncio.create_task(self._reader())

            # Resubscribe to pending subscriptions
            for symbol in self.pending_subscriptions:
                await self.subscribe_symbol(symbol)

        except Exception as e:
            self._connecting = False
            self._status = ConnectionStatus.FAILED
            self.metrics.failed_connections += 1
            logger.error(f"WebSocket connection failed: {e}")

            # Schedule reconnect if attempts remaining
            if self._reconnect_attempts < self._max_reconnect_attempts:
                self._reconnect_task = asyncio.create_task(self._schedule_reconnect())
            else:
                raise FeedConnectionError(f"Max reconnection attempts exceeded: {e}")

    async def disconnect(self) -> None:
        """Gracefully disconnect from WebSocket."""
        self._status = ConnectionStatus.DISCONNECTED

        # Cancel all tasks
        tasks_to_cancel = [self._heartbeat_task, self._reader_task, self._reconnect_task]
        for task in tasks_to_cancel:
            if task:
                task.cancel()

        # Close WebSocket
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

        # Stop queue
        await self.queue.stop()

        # Close session if owned
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

        self._connected = False
        logger.info("WebSocket disconnected")

    async def subscribe_symbol(self, symbol: str) -> None:
        """Subscribe to market data for a symbol."""
        if not self._connected:
            self.pending_subscriptions.add(symbol)
            return

        try:
            subscription_frame = self._create_subscription_frame(symbol)
            await self._ws.send_json(subscription_frame)
            self.subscriptions.add(symbol)
            self.pending_subscriptions.discard(symbol)
            logger.info(f"Subscribed to {symbol}")
        except Exception as e:
            logger.error(f"Subscription failed for {symbol}: {e}")
            self.pending_subscriptions.add(symbol)

    async def unsubscribe_symbol(self, symbol: str) -> None:
        """Unsubscribe from market data for a symbol."""
        if not self._connected:
            return

        try:
            unsubscription_frame = self._create_unsubscription_frame(symbol)
            await self._ws.send_json(unsubscription_frame)
            self.subscriptions.discard(symbol)
            logger.info(f"Unsubscribed from {symbol}")
        except Exception as e:
            logger.error(f"Unsubscription failed for {symbol}: {e}")

    async def _reader(self) -> None:
        """Read and process incoming WebSocket messages."""
        while self._connected and self._ws:
            try:
                message = await self._ws.receive()

                if message.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(message.json())
                elif message.type == aiohttp.WSMsgType.BINARY:
                    await self._handle_binary(message.data)
                elif message.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {message.data}")
                    break
                elif message.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED}:
                    logger.warning("WebSocket connection closed")
                    break

            except Exception as e:
                logger.error(f"Message reading error: {e}")
                break

        # Connection lost, attempt reconnect
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_task = asyncio.create_task(self._schedule_reconnect())

    async def _handle_message(self, payload: Any) -> None:
        """Process incoming JSON message."""
        try:
            self.metrics.messages_received += 1
            self.metrics.last_message_time = datetime.utcnow()

            # Decompress if needed
            if isinstance(payload, bytes) and self._enable_compression:
                payload = json.loads(gzip.decompress(payload).decode('utf-8'))

            # Parse and normalize data
            events = self.parse_message(payload)

            for event in events:
                # Data quality checks
                await self._check_data_quality(event)

                # Normalize data if normalizer provided
                if self._data_normalizer:
                    try:
                        normalized_data = self._data_normalizer(event.payload)
                        event.payload['normalized'] = normalized_data
                        event.normalized = True
                    except Exception as e:
                        self.data_metrics.normalization_errors += 1
                        logger.warning(f"Data normalization failed: {e}")

                # Publish to queue
                await self.queue.publish(event)
                self.metrics.messages_processed += 1

        except Exception as e:
            logger.error(f"Message handling error: {e}")

    async def _handle_binary(self, payload: bytes) -> None:
        """Process incoming binary message."""
        try:
            events = self.parse_binary(payload)
            for event in events:
                await self.queue.publish(event)
                self.metrics.messages_processed += 1
        except Exception as e:
            logger.error(f"Binary message handling error: {e}")

    async def _heartbeat(self) -> None:
        """Send periodic heartbeat to maintain connection."""
        while self._connected:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                if self._ws and not self._ws.closed:
                    await self._ws.ping()
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                break

    async def _schedule_reconnect(self) -> None:
        """Schedule reconnection attempt."""
        self._status = ConnectionStatus.RECONNECTING
        self._reconnect_attempts += 1
        self.metrics.reconnect_count += 1

        logger.info(f"Scheduling reconnect attempt {self._reconnect_attempts}/{self._max_reconnect_attempts}")

        await asyncio.sleep(self._reconnect_interval * self._reconnect_attempts)  # Exponential backoff

        if not self._connected:
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")

    async def _check_data_quality(self, event: StreamEvent) -> None:
        """Perform data quality checks."""
        symbol = event.symbol

        # Sequence number validation
        if event.sequence_number is not None:
            expected_seq = self.expected_sequences.get(symbol, event.sequence_number)
            if event.sequence_number != expected_seq:
                if event.sequence_number < expected_seq:
                    self.data_metrics.duplicate_events += 1
                else:
                    self.data_metrics.missing_data_points += (event.sequence_number - expected_seq)
                    self.data_metrics.out_of_order_events += 1

            self.expected_sequences[symbol] = event.sequence_number + 1

        # Update metrics
        self.data_metrics.symbols_tracked = len(self.expected_sequences)
        self.data_metrics.data_points_received += 1

        # Calculate delay if timestamp available
        if event.timestamp:
            delay = (datetime.utcnow() - event.timestamp).total_seconds() * 1000
            if delay > 0:
                self.data_metrics.average_delay_ms = (
                    self.data_metrics.average_delay_ms + delay
                ) / 2

    # Methods to override for specific exchanges ---------------------------
    def _create_subscription_frame(self, symbol: str) -> Dict[str, Any]:
        """Create subscription frame for specific exchange."""
        return {"type": "subscribe", "symbol": symbol}

    def _create_unsubscription_frame(self, symbol: str) -> Dict[str, Any]:
        """Create unsubscription frame for specific exchange."""
        return {"type": "unsubscribe", "symbol": symbol}

    def parse_message(self, payload: Any) -> Iterable[StreamEvent]:
        """Parse incoming JSON message into StreamEvents."""
        if isinstance(payload, dict):
            if "symbol" in payload:
                return [StreamEvent(
                    symbol=payload["symbol"],
                    payload=payload,
                    timestamp=ensure_datetime(payload.get("timestamp", datetime.utcnow())),
                    feed_type=self._infer_feed_type(payload),
                    sequence_number=payload.get("sequence"),
                    source=self.url
                )]
            elif "data" in payload and isinstance(payload["data"], list):
                # Handle batched messages
                events = []
                for item in payload["data"]:
                    if "symbol" in item:
                        events.append(StreamEvent(
                            symbol=item["symbol"],
                            payload=item,
                            timestamp=ensure_datetime(item.get("timestamp", datetime.utcnow())),
                            feed_type=self._infer_feed_type(item),
                            sequence_number=item.get("sequence"),
                            source=self.url
                        ))
                return events

        return []

    def parse_binary(self, payload: bytes) -> Iterable[StreamEvent]:
        """Parse incoming binary message into StreamEvents."""
        # Default implementation - override for binary protocols
        try:
            # Try to decode as JSON
            json_data = json.loads(payload.decode('utf-8'))
            return self.parse_message(json_data)
        except:
            # Return empty if can't parse
            return []

    def _infer_feed_type(self, payload: Dict[str, Any]) -> DataFeedType:
        """Infer feed type from message payload."""
        if "trade" in payload or "price" in payload and "volume" in payload:
            return DataFeedType.TRADES
        elif "bid" in payload and "ask" in payload:
            return DataFeedType.QUOTES
        elif "bids" in payload or "asks" in payload:
            return DataFeedType.ORDER_BOOK
        elif "news" in payload:
            return DataFeedType.NEWS
        else:
            return DataFeedType.TRADES

    # Public interface methods -------------------------------------------
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self._status

    def get_connection_metrics(self) -> ConnectionMetrics:
        """Get connection performance metrics."""
        self.metrics.uptime_seconds = time.time() - self.metrics.uptime_seconds
        return self.metrics

    def get_data_quality_metrics(self) -> DataQualityMetrics:
        """Get data quality metrics."""
        # Calculate completeness
        total_expected = sum(self.expected_sequences.values())
        if total_expected > 0:
            self.data_metrics.data_completeness = (
                self.data_metrics.data_points_received / total_expected
            )

        return self.data_metrics

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected and self._ws and not self._ws.closed


class LiveBacktestBridge:
    """Advanced bridge streaming events into backtest-compatible buffers with data aggregation."""

    def __init__(self, *, window: int = 10_000, aggregation_interval: str = "1s") -> None:
        self.window = window
        self.aggregation_interval = aggregation_interval
        self.buffers: Dict[str, deque[StreamEvent]] = defaultdict(lambda: deque(maxlen=window))
        self.aggregated_data: Dict[str, pd.DataFrame] = {}
        self.lock = asyncio.Lock()

        # Aggregation tracking
        self.last_aggregation: Dict[str, datetime] = {}
        self.aggregation_functions = {
            'price': 'last',  # Use last price for OHLC
            'volume': 'sum',  # Sum volume
            'bid': 'last',
            'ask': 'last',
            'bid_size': 'sum',
            'ask_size': 'sum'
        }

    async def consume(self, event: StreamEvent) -> None:
        """Consume streaming event and maintain rolling buffer."""
        async with self.lock:
            buffer = self.buffers[event.symbol]
            buffer.append(event)

            # Trigger aggregation if needed
            await self._aggregate_if_needed(event.symbol)

    async def _aggregate_if_needed(self, symbol: str) -> None:
        """Aggregate data into OHLCV format when time threshold reached."""
        now = datetime.utcnow()
        last_agg = self.last_aggregation.get(symbol)

        if last_agg is None or (now - last_agg).total_seconds() >= self._interval_seconds():
            await self._perform_aggregation(symbol)
            self.last_aggregation[symbol] = now

    def _interval_seconds(self) -> int:
        """Convert aggregation interval to seconds."""
        # Simple implementation - could be enhanced
        if self.aggregation_interval.endswith('s'):
            return int(self.aggregation_interval[:-1])
        elif self.aggregation_interval.endswith('m'):
            return int(self.aggregation_interval[:-1]) * 60
        elif self.aggregation_interval.endswith('h'):
            return int(self.aggregation_interval[:-1]) * 3600
        return 1  # Default 1 second

    async def _perform_aggregation(self, symbol: str) -> None:
        """Perform OHLCV aggregation on buffered data."""
        buffer = self.buffers[symbol]
        if not buffer:
            return

        # Convert to DataFrame for aggregation
        data = []
        for event in buffer:
            payload = event.payload
            row = {
                'timestamp': event.timestamp,
                'price': payload.get('price') or payload.get('last') or payload.get('close'),
                'volume': payload.get('volume', 0),
                'bid': payload.get('bid'),
                'ask': payload.get('ask'),
                'bid_size': payload.get('bid_size') or payload.get('bid_qty'),
                'ask_size': payload.get('ask_size') or payload.get('ask_qty')
            }
            data.append(row)

        if not data:
            return

        df = pd.DataFrame(data).set_index('timestamp')

        # Resample to aggregation interval
        ohlcv = df.resample(self.aggregation_interval).agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum',
            'bid': 'last',
            'ask': 'last',
            'bid_size': 'last',
            'ask_size': 'last'
        })

        # Flatten column names
        ohlcv.columns = ['open', 'high', 'low', 'close', 'volume', 'bid', 'ask', 'bid_size', 'ask_size']
        ohlcv = ohlcv.dropna()

        self.aggregated_data[symbol] = ohlcv

    async def to_dataframe(self, symbol: str, aggregated: bool = True) -> pd.DataFrame:
        """Convert buffered events to DataFrame."""
        async with self.lock:
            if aggregated and symbol in self.aggregated_data:
                return self.aggregated_data[symbol].copy()

            # Return raw events as DataFrame
            events = list(self.buffers.get(symbol, []))
            if not events:
                return pd.DataFrame(columns=["timestamp", "symbol", "payload"]).set_index("timestamp")

            return pd.DataFrame({
                "timestamp": [event.timestamp for event in events],
                "symbol": [event.symbol for event in events],
                "payload": [event.payload for event in events],
            }).set_index("timestamp")

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for symbol."""
        async with self.lock:
            buffer = self.buffers.get(symbol)
            if buffer:
                for event in reversed(buffer):
                    price = event.payload.get('price') or event.payload.get('last') or event.payload.get('close')
                    if price:
                        return float(price)
        return None

    async def get_price_history(self, symbol: str, lookback: int = 100) -> List[float]:
        """Get recent price history."""
        async with self.lock:
            buffer = self.buffers.get(symbol, [])
            prices = []
            for event in reversed(list(buffer)[-lookback:]):
                price = event.payload.get('price') or event.payload.get('last') or event.payload.get('close')
                if price:
                    prices.append(float(price))
            return prices[::-1]  # Return in chronological order


class DataNormalizer:
    """Normalize market data from different sources into consistent format."""

    @staticmethod
    def normalize_trade(payload: Dict[str, Any]) -> MarketData:
        """Normalize trade data."""
        return MarketData(
            symbol=payload.get('symbol', ''),
            timestamp=ensure_datetime(payload.get('timestamp', datetime.utcnow())),
            feed_type=DataFeedType.TRADES,
            price=payload.get('price') or payload.get('last') or payload.get('p'),
            volume=payload.get('volume') or payload.get('size') or payload.get('q'),
            trade_id=payload.get('trade_id') or payload.get('id'),
            trade_price=payload.get('price'),
            trade_volume=payload.get('volume'),
            trade_side=payload.get('side'),
            source=payload.get('source'),
            raw_data=payload
        )

    @staticmethod
    def normalize_quote(payload: Dict[str, Any]) -> MarketData:
        """Normalize quote data."""
        return MarketData(
            symbol=payload.get('symbol', ''),
            timestamp=ensure_datetime(payload.get('timestamp', datetime.utcnow())),
            feed_type=DataFeedType.QUOTES,
            bid=payload.get('bid') or payload.get('bid_price'),
            ask=payload.get('ask') or payload.get('ask_price'),
            bid_size=payload.get('bid_size') or payload.get('bid_qty'),
            ask_size=payload.get('ask_size') or payload.get('ask_qty'),
            bid_exchange=payload.get('bid_exchange'),
            ask_exchange=payload.get('ask_exchange'),
            source=payload.get('source'),
            raw_data=payload
        )

    @staticmethod
    def normalize_orderbook(payload: Dict[str, Any]) -> MarketData:
        """Normalize order book data."""
        bids = payload.get('bids', [])
        asks = payload.get('asks', [])

        # Convert bids and asks to consistent format
        bid_tuples = [(float(b[0]), float(b[1])) for b in bids[:10]] if bids else []
        ask_tuples = [(float(a[0]), float(a[1])) for a in asks[:10]] if asks else []

        return MarketData(
            symbol=payload.get('symbol', ''),
            timestamp=ensure_datetime(payload.get('timestamp', datetime.utcnow())),
            feed_type=DataFeedType.ORDER_BOOK,
            bids=bid_tuples,
            asks=ask_tuples,
            source=payload.get('source'),
            raw_data=payload
        )

    @classmethod
    def normalize(cls, payload: Dict[str, Any]) -> MarketData:
        """Auto-detect and normalize market data."""
        if 'bids' in payload or 'asks' in payload:
            return cls.normalize_orderbook(payload)
        elif 'bid' in payload and 'ask' in payload:
            return cls.normalize_quote(payload)
        elif 'price' in payload or 'volume' in payload or 'trade_id' in payload:
            return cls.normalize_trade(payload)
        else:
            # Default to trade format
            return cls.normalize_trade(payload)


class StreamingSignalEngine:
    """Real-time signal generation engine for streaming data."""

    def __init__(self, event_queue: EventQueue):
        self.event_queue = event_queue
        self.signal_functions: Dict[str, Callable] = {}
        self.active_signals: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.signal_history: Dict[str, deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=1000))

        # Subscribe to market data events
        self.event_queue.subscribe(self._process_market_data, "market_data")

    def register_signal(self, name: str, signal_func: Callable[[StreamEvent], Dict[str, Any]]) -> None:
        """Register a signal generation function."""
        self.signal_functions[name] = signal_func

    async def _process_market_data(self, event: StreamEvent) -> None:
        """Process incoming market data and generate signals."""
        symbol = event.symbol

        # Generate signals for all registered functions
        for signal_name, signal_func in self.signal_functions.items():
            try:
                signal_data = signal_func(event)

                if signal_data:
                    # Store signal
                    self.active_signals[symbol][signal_name] = signal_data

                    # Add to history
                    signal_entry = {
                        'timestamp': event.timestamp,
                        'symbol': symbol,
                        'signal_name': signal_name,
                        'data': signal_data
                    }
                    self.signal_history[symbol].append(signal_entry)

                    # Emit signal event
                    signal_event = StreamEvent(
                        symbol=symbol,
                        payload={
                            'signal_name': signal_name,
                            'signal_data': signal_data,
                            'source_event': event.payload
                        },
                        timestamp=datetime.utcnow(),
                        feed_type=DataFeedType.TRADES,  # Signals are derived from trades
                        tags={'signal': True}
                    )

                    await self.event_queue.publish(signal_event, priority=5)  # High priority for signals

            except Exception as e:
                logger.error(f"Signal generation failed for {signal_name}: {e}")

    def get_active_signals(self, symbol: str) -> Dict[str, Any]:
        """Get currently active signals for a symbol."""
        return dict(self.active_signals.get(symbol, {}))

    def get_signal_history(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent signal history for a symbol."""
        return list(self.signal_history.get(symbol, []))[-limit:]


class MarketDataAggregator:
    """Aggregate multiple data feeds and provide unified market view."""

    def __init__(self):
        self.feeds: Dict[str, WebSocketStream] = {}
        self.event_queue = EventQueue()
        self.bridge = LiveBacktestBridge()
        self.signal_engine = StreamingSignalEngine(self.event_queue)

        # Data aggregation
        self.latest_prices: Dict[str, float] = {}
        self.price_sources: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.consolidated_data: Dict[str, MarketData] = {}

    async def add_feed(self, name: str, feed: WebSocketStream) -> None:
        """Add a market data feed."""
        self.feeds[name] = feed

        # Subscribe feed to event queue
        subscription_id = await self.event_queue.subscribe(self._process_feed_data)
        feed.queue = self.event_queue  # Share the same queue

        # Subscribe to symbols of interest
        # This would be configured based on strategy requirements

    async def _process_feed_data(self, event: StreamEvent) -> None:
        """Process data from individual feeds."""
        symbol = event.symbol

        # Update latest price if available
        price = event.payload.get('price') or event.payload.get('last') or event.payload.get('close')
        if price:
            self.latest_prices[symbol] = float(price)

            # Track price sources for consensus pricing
            source = event.source or 'unknown'
            self.price_sources[symbol].append((source, float(price)))

            # Keep only recent prices (last 10)
            if len(self.price_sources[symbol]) > 10:
                self.price_sources[symbol].pop(0)

        # Normalize and consolidate data
        try:
            normalized = DataNormalizer.normalize(event.payload)
            self.consolidated_data[symbol] = normalized
        except Exception as e:
            logger.warning(f"Data normalization failed: {e}")

        # Forward to bridge for backtesting compatibility
        await self.bridge.consume(event)

    def get_consensus_price(self, symbol: str) -> Optional[float]:
        """Get consensus price across all feeds."""
        sources = self.price_sources.get(symbol, [])
        if not sources:
            return None

        # Simple average for now - could be weighted by feed quality
        prices = [price for _, price in sources[-5:]]  # Use last 5 prices
        return sum(prices) / len(prices) if prices else None

    def get_market_snapshot(self, symbol: str) -> Optional[MarketData]:
        """Get latest consolidated market data."""
        return self.consolidated_data.get(symbol)

    async def get_historical_data(self, symbol: str, start_date: datetime,
                                end_date: datetime) -> pd.DataFrame:
        """Get historical data for backtesting."""
        # This would integrate with historical data sources
        # For now, return aggregated streaming data
        return await self.bridge.to_dataframe(symbol)


# Exchange-specific implementations
class BinanceWebSocketStream(WebSocketStream):
    """Binance WebSocket stream implementation."""

    def _create_subscription_frame(self, symbol: str) -> Dict[str, Any]:
        return {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@trade", f"{symbol.lower()}@depth@100ms"],
            "id": 1
        }

    def _create_unsubscription_frame(self, symbol: str) -> Dict[str, Any]:
        return {
            "method": "UNSUBSCRIBE",
            "params": [f"{symbol.lower()}@trade", f"{symbol.lower()}@depth@100ms"],
            "id": 1
        }

    def parse_message(self, payload: Any) -> Iterable[StreamEvent]:
        if isinstance(payload, dict) and payload.get('stream'):
            stream_name = payload['stream']
            data = payload.get('data', {})

            if '@trade' in stream_name:
                yield StreamEvent(
                    symbol=data.get('s', ''),
                    payload={
                        'price': float(data.get('p', 0)),
                        'volume': float(data.get('q', 0)),
                        'trade_id': data.get('t'),
                        'timestamp': datetime.fromtimestamp(data.get('T', 0) / 1000),
                        'side': 'buy' if data.get('m') else 'sell'
                    },
                    timestamp=datetime.fromtimestamp(data.get('T', 0) / 1000),
                    feed_type=DataFeedType.TRADES,
                    source='binance'
                )
            elif '@depth' in stream_name:
                yield StreamEvent(
                    symbol=data.get('s', ''),
                    payload={
                        'bids': [(float(b[0]), float(b[1])) for b in data.get('b', [])],
                        'asks': [(float(a[0]), float(a[1])) for a in data.get('a', [])],
                        'timestamp': datetime.fromtimestamp(data.get('T', 0) / 1000)
                    },
                    timestamp=datetime.fromtimestamp(data.get('T', 0) / 1000),
                    feed_type=DataFeedType.ORDER_BOOK,
                    source='binance'
                )

    def _infer_feed_type(self, payload: Dict[str, Any]) -> DataFeedType:
        if 'bids' in payload or 'asks' in payload:
            return DataFeedType.ORDER_BOOK
        return DataFeedType.TRADES


__all__ = [
    "StreamEvent",
    "MarketData",
    "FeedSubscription",
    "ConnectionMetrics",
    "DataQualityMetrics",
    "EventQueue",
    "WebSocketStream",
    "LiveBacktestBridge",
    "DataNormalizer",
    "StreamingSignalEngine",
    "MarketDataAggregator",
    "BinanceWebSocketStream",
    "DataFeedType",
    "FeedQuality",
    "ConnectionStatus",
    "DataNormalizationError",
    "FeedConnectionError"
]

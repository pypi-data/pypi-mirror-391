"""Data acquisition and normalization layer for qantify."""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Dict, Optional

import pandas as pd

from qantify.core import Symbol

from .cache import DiskCache, MemoryCache, SnapshotManager
from .clients import (
    BinanceClient,
    BinanceFuturesClient,
    BinanceOptionsClient,
    DukascopyClient,
    PolygonClient,
)
from .streaming import EventQueue, LiveBacktestBridge, StreamEvent, WebSocketStream
from .pipeline import raw_to_frame
from .registry import create_client, list_clients, register_client

__all__ = [
    "get_candles",
    "aget_candles",
    "register_client",
    "create_client",
    "list_clients",
    "MemoryCache",
    "DiskCache",
    "SnapshotManager",
    "CorporateActionAdjuster",
    "StreamEvent",
    "EventQueue",
    "WebSocketStream",
    "LiveBacktestBridge",
]


def _register_builtin_clients() -> None:
    register_client("binance", BinanceClient)
    register_client("binance_futures", BinanceFuturesClient)
    register_client("binance_options", BinanceOptionsClient)
    register_client("dukascopy", DukascopyClient)
    register_client("polygon", PolygonClient)


_register_builtin_clients()


async def aget_candles(
    *,
    symbol: str | Symbol,
    exchange: str = "binance",
    interval: str = "1h",
    start_date: Optional[Any] = None,
    end_date: Optional[Any] = None,
    limit: Optional[int] = None,
    snapshot_manager: Optional[SnapshotManager] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Asynchronously fetch OHLCV candles for the given symbol."""

    client = create_client(exchange)
    symbol_obj = client.canonicalize_symbol(symbol)
    if symbol_obj.exchange is None:
        symbol_obj = Symbol(symbol_obj.value, exchange=exchange)

    snapshot_key = f"{exchange}:{symbol_obj.value}:{interval}"
    cached_frame: Optional[pd.DataFrame] = None
    if snapshot_manager and use_cache:
        cached_frame = snapshot_manager.load(snapshot_key)

    async with client as bound_client:
        timeframe = bound_client.resolve_timeframe(interval)
        effective_start = start_date
        if snapshot_manager and use_cache:
            last_ts = snapshot_manager.last_timestamp(snapshot_key)
            if last_ts is not None:
                next_ts = last_ts + pd.Timedelta(seconds=timeframe.seconds)
                if effective_start is None or ensure_datetime(effective_start) < next_ts.to_pydatetime():
                    effective_start = next_ts.to_pydatetime()
        raw_records = await bound_client.fetch_candles(
            symbol_obj,
            timeframe,
            start=effective_start,
            end=end_date,
            limit=limit,
        )

    frame = raw_to_frame(raw_records, symbol=symbol_obj, timeframe=timeframe)

    if cached_frame is not None and not cached_frame.empty:
        combined = pd.concat([cached_frame, frame])
        combined = combined[~combined.index.duplicated(keep="last")]
        frame = combined

    if snapshot_manager:
        snapshot_manager.snapshot(snapshot_key, frame)

    return frame


def get_candles(
    *,
    symbol: str | Symbol,
    exchange: str = "binance",
    interval: str = "1h",
    start_date: Optional[Any] = None,
    end_date: Optional[Any] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Synchronously fetch OHLCV candles.

    This helper bridges to the async implementation. If called from within an
    existing event loop (e.g. Jupyter), the coroutine is executed in a worker
    thread so the caller can remain synchronous.
    """

    async def _runner() -> pd.DataFrame:
        return await aget_candles(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_runner())

    result: list[pd.DataFrame] = []
    error: list[BaseException] = []

    def _worker() -> None:
        try:
            result.append(asyncio.run(_runner()))
        except BaseException as exc:  # pragma: no cover - re-raised below
            error.append(exc)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join()

    if error:
        raise error[0]

    return result[0]

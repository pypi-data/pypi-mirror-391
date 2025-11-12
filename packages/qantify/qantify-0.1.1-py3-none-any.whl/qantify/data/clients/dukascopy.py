"""Dukascopy forex data client."""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import Any, Iterable, Optional

import aiohttp

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime

from ..base import BaseClient
from ..errors import DataClientError


_DUKASCOPY_TIMEFRAMES = {
    "1m": TimeFrame("1m", "1T", 60),
    "5m": TimeFrame("5m", "5T", 300),
    "15m": TimeFrame("15m", "15T", 900),
    "1h": TimeFrame("1h", "1H", 3600),
    "4h": TimeFrame("4h", "4H", 14_400),
    "1d": TimeFrame("1d", "1D", 86_400),
}


class DukascopyClient(BaseClient):
    """Fetch historical forex candles from Dukascopy."""

    name = "dukascopy"
    rest_endpoint = "https://datafeed.dukascopy.com/datafeed"
    max_batch_size = 500

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _DUKASCOPY_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported Dukascopy interval '{value}'.") from exc

    async def fetch_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        await self._ensure_session()

        start_dt = ensure_datetime(start) if start else None
        end_dt = ensure_datetime(end) if end else None

        if start_dt is None or end_dt is None:
            raise ValueError("Dukascopy client requires explicit start and end datetimes.")

        if start_dt > end_dt:
            raise ValueError("start must precede end")

        records: list[dict[str, Any]] = []
        current = start_dt
        step = timedelta(seconds=timeframe.seconds)

        while current <= end_dt:
            year = current.year
            month = current.month - 1  # Dukascopy months are zero-based in URLs
            day = current.day
            hour = current.hour

            url = f"{self.rest_endpoint}/{symbol.value}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        current = current + step
                        continue
                    payload = await response.read()
            except aiohttp.ClientError as exc:
                raise DataClientError(f"Failed to fetch Dukascopy data: {exc}") from exc

            records.extend(self._decode_bi5(payload, current, timeframe))

            if limit is not None and len(records) >= limit:
                return records[:limit]

            current = current + step

        return records

    def _decode_bi5(self, payload: bytes, timestamp: datetime, timeframe: TimeFrame) -> list[dict[str, Any]]:
        import bz2
        import struct

        if not payload:
            return []
        try:
            decompressed = bz2.decompress(payload)
        except OSError:
            return []

        records = []
        for i in range(0, len(decompressed), 20):
            chunk = decompressed[i : i + 20]
            if len(chunk) < 20:
                continue
            msecs, ask, bid, ask_vol, bid_vol = struct.unpack("!lffff", chunk)
            candle_time = ensure_datetime(timestamp + timedelta(milliseconds=msecs))
            price = (ask + bid) / 2
            records.append(
                {
                    "timestamp": candle_time,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": (ask_vol + bid_vol) / 2,
                }
            )
        return records

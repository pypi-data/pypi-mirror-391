"""Synthetic satellite/footfall adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional

import pandas as pd

from qantify.core.types import TimeFrame
from qantify.data.base import BaseClient
from qantify.data.cache import SnapshotManager, create_snapshot_manager, make_cache_key
from qantify.data.normalizers_alt import normalize_footfall_series


class FootfallClient(BaseClient):
    """Satellite/alternative data client providing location foot traffic metrics."""

    name = "footfall"

    def __init__(
        self,
        *,
        cache: SnapshotManager | None = None,
        session: Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        super().__init__(session=session)
        self.cache = cache or create_snapshot_manager("footfall")

    def resolve_timeframe(self, value: str) -> TimeFrame:
        normalized = value.lower()
        mapping = {
            "1d": TimeFrame("1d", "1D", 86_400),
            "1w": TimeFrame("1w", "7D", 604_800),
        }
        if normalized not in mapping:
            raise ValueError(f"Unsupported footfall timeframe '{value}'.")
        return mapping[normalized]

    async def fetch_location_series(
        self,
        location_id: str,
        *,
        timeframe: TimeFrame,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        key = make_cache_key("footfall", location_id, timeframe.name)
        cached = self.cache.load(key) if self.cache else None
        if cached is not None:
            return cached

        data = self._generate_payload(location_id, timeframe=timeframe, start=start, end=end, limit=limit)
        frame = normalize_footfall_series(data)
        if self.cache:
            last_ts = frame.index.max() if not frame.empty else None
            self.cache.snapshot(key, frame, last_timestamp=last_ts)
        return frame

    async def fetch_candles(
        self,
        symbol: Any,
        timeframe: TimeFrame,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        location_id = str(symbol)
        frame = await self.fetch_location_series(
            location_id,
            timeframe=timeframe,
            start=start if isinstance(start, datetime) else None,
            end=end if isinstance(end, datetime) else None,
            limit=limit,
        )

        records = []
        for ts, row in frame.iterrows():
            count = float(row["count"])
            records.append(
                {
                    "timestamp": ts.to_pydatetime(),
                    "open": count,
                    "high": count,
                    "low": count,
                    "close": count,
                    "volume": count,
                }
            )
        return records

    def _generate_payload(
        self,
        location_id: str,
        *,
        timeframe: TimeFrame,
        start: Optional[datetime],
        end: Optional[datetime],
        limit: Optional[int],
    ) -> list[dict[str, Any]]:
        freq = timeframe.pandas_value.lower()
        end_ts = end or datetime.now(timezone.utc)
        if limit:
            index = pd.date_range(end=end_ts, freq=freq, periods=limit, tz="UTC")
        else:
            if start:
                index = pd.date_range(start=start, end=end_ts, freq=freq, tz="UTC")
            else:
                index = pd.date_range(end=end_ts, freq=freq, periods=26, tz="UTC")

        base = hash(location_id) % 1000
        payload = []
        for idx, ts in enumerate(index):
            count = float(base + idx * 15 + (idx % 5) * 3)
            payload.append(
                {
                    "timestamp": ts.to_pydatetime(),
                    "location_id": location_id,
                    "count": count,
                }
            )
        return payload


__all__ = ["FootfallClient"]


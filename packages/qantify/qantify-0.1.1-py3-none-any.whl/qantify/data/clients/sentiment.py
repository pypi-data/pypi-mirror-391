"""Synthetic sentiment adapters for social feeds."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional, Sequence

import pandas as pd

from qantify.core import Symbol, TimeFrame
from qantify.data.base import BaseClient
from qantify.data.cache import SnapshotManager, create_snapshot_manager, make_cache_key
from qantify.data.normalizers_alt import normalize_sentiment_scores

SOURCES: Sequence[str] = ("twitter", "reddit")


class SentimentClient(BaseClient):
    """Sentiment feed for Twitter/Reddit with simple synthetic payloads."""

    name = "sentiment"

    def __init__(
        self,
        *,
        cache: SnapshotManager | None = None,
        session: Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        super().__init__(session=session)
        self.cache = cache or create_snapshot_manager("sentiment")

    def resolve_timeframe(self, value: str) -> TimeFrame:
        mapping = {
            "1h": TimeFrame("1h", "1H", 3_600),
            "6h": TimeFrame("6h", "6H", 21_600),
            "1d": TimeFrame("1d", "1D", 86_400),
        }
        normalized = value.lower()
        if normalized not in mapping:
            raise ValueError(f"Unsupported sentiment timeframe '{value}'.")
        return mapping[normalized]

    async def fetch_sentiment(
        self,
        symbol: Symbol,
        *,
        source: str = "twitter",
        timeframe: TimeFrame | None = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        source = source.lower()
        if source not in SOURCES:
            raise ValueError(f"Unsupported sentiment source '{source}'. Choose from {SOURCES}.")

        key_parts = ["sentiment", source, str(symbol)]
        if timeframe:
            key_parts.append(timeframe.name)
        key = make_cache_key(*key_parts)

        cached = self.cache.load(key) if self.cache else None
        if cached is not None:
            return cached

        frame = normalize_sentiment_scores(
            self._generate_sentiment_payload(symbol, source=source, timeframe=timeframe, start=start, end=end, limit=limit)
        )
        if self.cache:
            last_ts = frame.index.max() if not frame.empty else None
            self.cache.snapshot(key, frame, last_timestamp=last_ts)
        return frame

    async def fetch_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        frame = await self.fetch_sentiment(
            symbol,
            source="twitter",
            timeframe=timeframe,
            start=start if isinstance(start, datetime) else None,
            end=end if isinstance(end, datetime) else None,
            limit=limit,
        )
        records = []
        for ts, row in frame.iterrows():
            score = float(row["score"])
            record = {
                "timestamp": ts.to_pydatetime(),
                "open": score,
                "high": score,
                "low": score,
                "close": score,
                "volume": float(row.get("volume", 0.0)),
            }
            records.append(record)
        return records

    def _generate_sentiment_payload(
        self,
        symbol: Symbol,
        *,
        source: str,
        timeframe: TimeFrame | None,
        start: Optional[datetime],
        end: Optional[datetime],
        limit: Optional[int],
    ) -> list[dict[str, Any]]:
        freq = (timeframe.pandas_value if timeframe else "1H").lower()
        end_ts = end or datetime.now(timezone.utc)
        if limit:
            index = pd.date_range(end=end_ts, freq=freq, periods=limit, tz="UTC")
        else:
            if start:
                index = pd.date_range(start=start, end=end_ts, freq=freq, tz="UTC")
            else:
                index = pd.date_range(end=end_ts, freq=freq, periods=24, tz="UTC")

        base = (hash(str(symbol)) + hash(source)) % 50
        payload = []
        for idx, ts in enumerate(index):
            score = (base + idx) % 100 / 100 - 0.5  # between -0.5 and 0.5
            payload.append(
                {
                    "timestamp": ts.to_pydatetime(),
                    "source": source,
                    "symbol": str(symbol),
                    "score": score,
                    "volume": float(100 + idx * 10),
                }
            )
        return payload


__all__ = ["SentimentClient"]


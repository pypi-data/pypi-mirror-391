"""Synthetic on-chain metrics client."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional

import pandas as pd

from qantify.core import Symbol, TimeFrame
from qantify.data.base import BaseClient
from qantify.data.cache import SnapshotManager, create_snapshot_manager, make_cache_key
from qantify.data.normalizers_alt import normalize_metric_series

DEFAULT_METRICS = ("active_addresses", "tx_volume_usd", "hashrate")


class OnChainMetricsClient(BaseClient):
    """Lightweight client that provides synthetic on-chain metric series."""

    name = "onchain"

    def __init__(
        self,
        *,
        cache: SnapshotManager | None = None,
        session: Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        super().__init__(session=session)
        self.cache = cache or create_snapshot_manager("onchain")

    def resolve_timeframe(self, value: str) -> TimeFrame:
        normalized = value.lower()
        mapping = {
            "1h": TimeFrame("1h", "1H", 3_600),
            "4h": TimeFrame("4h", "4H", 14_400),
            "1d": TimeFrame("1d", "1D", 86_400),
            "1w": TimeFrame("1w", "7D", 604_800),
        }
        if normalized not in mapping:
            raise ValueError(f"Unsupported timeframe '{value}' for on-chain metrics.")
        return mapping[normalized]

    async def fetch_metric_series(
        self,
        symbol: Symbol,
        *,
        metric: str,
        timeframe: TimeFrame,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        metric = metric.lower()
        if metric not in DEFAULT_METRICS:
            DEFAULT_METRICS_SET = ", ".join(DEFAULT_METRICS)
            raise ValueError(f"Unsupported metric '{metric}'. Available metrics: {DEFAULT_METRICS_SET}.")

        key = make_cache_key("onchain", metric, str(symbol), timeframe.name)
        cached = self.cache.load(key) if self.cache else None
        if cached is not None:
            return cached

        data = self._generate_series(symbol, metric=metric, timeframe=timeframe, start=start, end=end, limit=limit)
        frame = normalize_metric_series(data, metric=metric)
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
        frame = await self.fetch_metric_series(
            symbol,
            metric="tx_volume_usd",
            timeframe=timeframe,
            start=start if isinstance(start, datetime) else None,
            end=end if isinstance(end, datetime) else None,
            limit=limit,
        )
        records = []
        for ts, row in frame.iterrows():
            close = float(row.iloc[0])
            record = {
                "timestamp": ts.to_pydatetime(),
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": close,
            }
            records.append(record)
        return records

    def _generate_series(
        self,
        symbol: Symbol,
        *,
        metric: str,
        timeframe: TimeFrame,
        start: Optional[datetime],
        end: Optional[datetime],
        limit: Optional[int],
    ) -> list[dict[str, Any]]:
        end_ts = end or datetime.now(tz=timezone.utc)
        freq = timeframe.pandas_value.lower()
        if limit is None:
            periods = 30
        else:
            periods = max(1, limit)
        if start:
            index = pd.date_range(start=start, end=end_ts, freq=freq, tz="UTC")
            if len(index) > periods:
                index = index[-periods:]
        else:
            index = pd.date_range(end=end_ts, periods=periods, freq=freq, tz="UTC")

        base = hash((metric, str(symbol))) % 100
        data = []
        for idx, ts in enumerate(index):
            value = base + (idx + 1) * 5 + (idx % 3) * 2
            data.append(
                {
                    "timestamp": ts.to_pydatetime(),
                    "metric": metric,
                    "value": float(value),
                }
            )
        return data


__all__ = ["OnChainMetricsClient"]


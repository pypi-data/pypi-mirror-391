"""Normalization helpers for alternative data payloads."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import pandas as pd

from qantify.core.utils import ensure_datetime


def _ensure_dataframe(records: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    data = list(records)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame.from_records(data)


def normalize_metric_series(
    records: Iterable[Mapping[str, object]],
    *,
    metric: str | None = None,
    timestamp_key: str = "timestamp",
    value_key: str = "value",
    metric_key: str = "metric",
) -> pd.DataFrame:
    """Normalize arbitrary metric payloads into a timestamp-indexed wide DataFrame."""

    frame = _ensure_dataframe(records)
    if frame.empty:
        index = pd.DatetimeIndex([], name="timestamp", tz="UTC")
        return pd.DataFrame(index=index)

    if timestamp_key not in frame.columns or value_key not in frame.columns:
        raise KeyError(f"Payload must include '{timestamp_key}' and '{value_key}' columns.")

    if metric_key not in frame.columns:
        if metric is None:
            raise KeyError(f"Payload missing '{metric_key}' column and no default metric provided.")
        frame[metric_key] = metric

    frame[timestamp_key] = frame[timestamp_key].map(ensure_datetime)
    frame[timestamp_key] = pd.to_datetime(frame[timestamp_key], utc=True)
    frame[value_key] = pd.to_numeric(frame[value_key], errors="coerce")

    frame = frame.dropna(subset=[value_key])
    if frame.empty:
        index = pd.DatetimeIndex([], name="timestamp", tz="UTC")
        return pd.DataFrame(index=index)

    pivot = frame.pivot_table(
        index=timestamp_key,
        columns=metric_key,
        values=value_key,
        aggfunc="last",
    )
    pivot.index = pd.DatetimeIndex(pivot.index, tz="UTC")
    pivot = pivot.sort_index()
    pivot = pivot[~pivot.index.duplicated(keep="last")]
    return pivot


def normalize_sentiment_scores(
    records: Iterable[Mapping[str, object]],
    *,
    required_sources: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Normalize sentiment payloads into a tidy DataFrame."""

    frame = _ensure_dataframe(records)
    if frame.empty:
        columns = ["source", "symbol", "score", "volume"]
        index = pd.DatetimeIndex([], name="timestamp", tz="UTC")
        return pd.DataFrame(columns=columns, index=index)

    required = {"timestamp", "source", "symbol", "score"}
    missing = required.difference(frame.columns)
    if missing:
        raise KeyError(f"Sentiment payload missing required columns: {sorted(missing)}")

    frame["timestamp"] = pd.to_datetime(frame["timestamp"].map(ensure_datetime), utc=True)
    frame["score"] = pd.to_numeric(frame["score"], errors="coerce")
    if "volume" not in frame.columns:
        frame["volume"] = 0.0
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce").fillna(0.0)

    frame = frame.dropna(subset=["score"])
    if required_sources:
        frame = frame[frame["source"].isin(required_sources)]

    frame = frame.sort_values("timestamp")
    frame = frame.set_index("timestamp")
    frame.index = pd.DatetimeIndex(frame.index, tz="UTC")
    return frame


def normalize_footfall_series(
    records: Iterable[Mapping[str, object]],
    *,
    location_key: str = "location_id",
    timestamp_key: str = "timestamp",
    count_key: str = "count",
) -> pd.DataFrame:
    """Normalize satellite/footfall payloads into a tidy DataFrame."""

    frame = _ensure_dataframe(records)
    if frame.empty:
        columns = [location_key, "count"]
        index = pd.DatetimeIndex([], name="timestamp", tz="UTC")
        return pd.DataFrame(columns=columns, index=index)

    required = {location_key, timestamp_key, count_key}
    missing = required.difference(frame.columns)
    if missing:
        raise KeyError(f"Footfall payload missing required columns: {sorted(missing)}")

    frame[timestamp_key] = pd.to_datetime(frame[timestamp_key].map(ensure_datetime), utc=True)
    frame[count_key] = pd.to_numeric(frame[count_key], errors="coerce")
    frame = frame.dropna(subset=[count_key])

    frame = frame.sort_values(timestamp_key)
    frame = frame.set_index(timestamp_key)
    frame.index = pd.DatetimeIndex(frame.index, tz="UTC")
    frame.rename(columns={count_key: "count"}, inplace=True)
    return frame


__all__ = [
    "normalize_metric_series",
    "normalize_sentiment_scores",
    "normalize_footfall_series",
]


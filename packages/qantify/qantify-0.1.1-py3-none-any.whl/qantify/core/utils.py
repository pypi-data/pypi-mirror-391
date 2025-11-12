"""Core utility helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Sequence

import pandas as pd


def ensure_datetime(value: datetime | str | int | float) -> datetime:
    """Normalize various timestamp inputs into timezone-aware ``datetime``.

    Args:
        value: ``datetime`` (with or without timezone), ISO string, or POSIX
            timestamp (seconds).

    Returns:
        ``datetime`` normalized to UTC.
    """

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    parsed = pd.to_datetime(value, utc=True)
    if isinstance(parsed, pd.Series):
        raise TypeError("Expected a scalar timestamp value, not a Series.")

    return parsed.to_pydatetime()


def to_datetime_index(index_like: Sequence[datetime | str | int | float]) -> pd.DatetimeIndex:
    """Convert iterable timestamps to a UTC ``DatetimeIndex``."""

    return pd.to_datetime(list(index_like), utc=True)


def validate_ohlcv_frame(frame: pd.DataFrame, required_columns: Iterable[str] | None = None) -> None:
    """Validate that a DataFrame conforms to expected OHLCV schema."""

    columns = {"open", "high", "low", "close"}
    if required_columns:
        columns.update(required_columns)

    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"DataFrame missing required columns: {sorted(missing)}")

    if not isinstance(frame.index, pd.DatetimeIndex):
        raise TypeError("DataFrame index must be a pandas.DatetimeIndex.")

    if frame.index.tz is None:
        raise ValueError("DataFrame index must be timezone-aware (UTC).")

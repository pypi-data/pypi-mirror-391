"""Normalization pipeline transforming raw payloads into clean DataFrames."""

from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime, validate_ohlcv_frame

from .errors import DataNormalizationError


BASE_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def normalize_payload_records(records: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    """Normalize raw iterable payloads into a preliminary DataFrame."""

    data = list(records)
    if not data:
        index = pd.DatetimeIndex([], name="timestamp", tz="UTC")
        return pd.DataFrame(columns=list(BASE_COLUMNS[1:]), index=index)

    frame = pd.DataFrame.from_records(data)

    missing = set(BASE_COLUMNS).difference(frame.columns)
    if missing:
        raise DataNormalizationError(f"Missing required payload keys: {sorted(missing)}")

    frame["timestamp"] = frame["timestamp"].map(ensure_datetime)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    frame[numeric_cols] = frame[numeric_cols].apply(pd.to_numeric, errors="raise")

    frame = frame.set_index("timestamp", drop=True)
    frame = frame.sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]

    return frame


def finalize_ohlcv_frame(
    frame: pd.DataFrame,
    *,
    symbol: Symbol,
    timeframe: TimeFrame | None = None,
) -> pd.DataFrame:
    """Attach metadata columns and validate the OHLCV schema."""

    frame = frame.copy()

    frame["symbol"] = str(symbol)
    frame["timeframe"] = timeframe.name if timeframe else None

    if not frame.empty:
        validate_ohlcv_frame(frame)

    return frame


def raw_to_frame(
    raw_records: Iterable[Mapping[str, object]],
    *,
    symbol: Symbol,
    timeframe: TimeFrame | None = None,
) -> pd.DataFrame:
    """Full pipeline helper to convert raw payloads into a clean DataFrame."""

    normalized = normalize_payload_records(raw_records)
    return finalize_ohlcv_frame(normalized, symbol=symbol, timeframe=timeframe)

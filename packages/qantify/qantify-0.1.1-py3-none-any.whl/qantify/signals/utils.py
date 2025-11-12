"""Helper utilities for vectorized indicator implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Protocol, Sequence, Union

import pandas as pd


SeriesLike = Union[pd.Series, pd.DataFrame]


class SupportsInplace(Protocol):
    def copy(self) -> "SupportsInplace":  # pragma: no cover - protocol definition
        ...


@dataclass(slots=True)
class SeriesSelection:
    """Encapsulates the selected series and the parent container."""

    data: SeriesLike
    series: pd.Series
    inplace_target: Optional[pd.DataFrame]


def select_series(data: SeriesLike, column: Optional[str] = None) -> SeriesSelection:
    """Select a ``pd.Series`` from supported inputs."""

    if isinstance(data, pd.Series):
        return SeriesSelection(data=data, series=data, inplace_target=None)

    if column is None:
        raise ValueError("Column name must be provided when passing a DataFrame.")

    if column not in data.columns:
        raise KeyError(f"Column '{column}' not present in DataFrame.")

    return SeriesSelection(data=data, series=data[column], inplace_target=data)


def attach_result(
    selection: SeriesSelection,
    values: pd.Series,
    name: str,
    *,
    inplace: bool = False,
) -> SeriesLike:
    """Attach indicator results to the original container."""

    values = values.copy()
    values.name = name

    if isinstance(selection.data, pd.Series):
        return values

    target = selection.inplace_target if inplace else selection.data.copy()
    target[name] = values
    return target


def ensure_min_periods(period: int) -> int:
    """Return ``min_periods`` ensuring at least 1."""

    return max(1, period)


def require_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    """Ensure that the required columns exist within a DataFrame."""

    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise KeyError(f"DataFrame missing required columns: {missing}")


def rolling_apply(
    series: pd.Series,
    window: int,
    func: Callable[[pd.Series], float],
    *,
    min_periods: Optional[int] = None,
    center: bool = False,
) -> pd.Series:
    """Apply a callable across a rolling window while preserving index."""

    window_obj = series.rolling(window=window, min_periods=min_periods or ensure_min_periods(window), center=center)
    result = window_obj.apply(func, raw=False)
    return result


def normalize_name(base: str, suffix: str | None = None) -> str:
    if suffix:
        return f"{base}_{suffix}"
    return base


def expand_series(array: Sequence[float], index: pd.Index, name: Optional[str] = None) -> pd.Series:
    series = pd.Series(array, index=index)
    if name is not None:
        series.name = name
    return series

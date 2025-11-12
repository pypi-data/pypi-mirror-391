from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Sequence

import pandas as pd

from qantify.backtest.execution import OrderBookSnapshot


@dataclass(slots=True)
class BookEvent:
    """Represents a limit order book snapshot at a point in time."""

    timestamp: pd.Timestamp
    bids: Sequence[tuple[float, float]]
    asks: Sequence[tuple[float, float]]

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, pd.Timestamp):
            self.timestamp = pd.Timestamp(self.timestamp).tz_localize("UTC") if pd.Timestamp(self.timestamp).tzinfo is None else pd.Timestamp(self.timestamp).tz_convert("UTC")
        if not self.timestamp.tzinfo:
            self.timestamp = self.timestamp.tz_localize("UTC")
        self.bids = tuple(sorted([(float(p), float(s)) for p, s in self.bids if s > 0], key=lambda item: item[0], reverse=True))
        self.asks = tuple(sorted([(float(p), float(s)) for p, s in self.asks if s > 0], key=lambda item: item[0]))


class LimitOrderBookReplay:
    """Utility for replaying historical limit order book snapshots."""

    def __init__(self, events: Iterable[BookEvent], *, depth: int = 10) -> None:
        snapshots = sorted(events, key=lambda event: event.timestamp)
        if not snapshots:
            raise ValueError("LimitOrderBookReplay requires at least one book event.")
        self._events: List[BookEvent] = snapshots
        self.depth = max(1, depth)
        self._index = 0

    @classmethod
    def from_dataframe(
        cls,
        frame: pd.DataFrame,
        *,
        bid_columns: Sequence[str],
        ask_columns: Sequence[str],
        size_columns: Sequence[str] | None = None,
        depth: int = 10,
    ) -> "LimitOrderBookReplay":
        """Build a replay from a wide-format DataFrame.

        Parameters
        ----------
        frame:
            DataFrame indexed by timestamp (or with `timestamp` column) containing price levels.
        bid_columns:
            Column names for bid prices ordered from best to worst.
        ask_columns:
            Column names for ask prices ordered from best to worst.
        size_columns:
            Optional pair of sequences (bid_sizes, ask_sizes). If omitted, inferred from price column counterparts with `_size` suffix.
        depth:
            Maximum book depth preserved in the replay.
        """

        if "timestamp" in frame.columns:
            timestamps = pd.to_datetime(frame["timestamp"], utc=True)
        else:
            timestamps = pd.to_datetime(frame.index, utc=True)

        if size_columns is None:
            bid_sizes = [f"{col}_size" for col in bid_columns]
            ask_sizes = [f"{col}_size" for col in ask_columns]
        else:
            bid_sizes, ask_sizes = size_columns

        events = []
        for idx, row in frame.iterrows():
            bids = [
                (row[col_price], row[bid_sizes[idx_lvl]] if bid_sizes[idx_lvl] in row else row[bid_sizes[idx_lvl]])
                for idx_lvl, col_price in enumerate(bid_columns)
                if pd.notna(row[col_price])
            ]
            asks = [
                (row[col_price], row[ask_sizes[idx_lvl]] if ask_sizes[idx_lvl] in row else row[ask_sizes[idx_lvl]])
                for idx_lvl, col_price in enumerate(ask_columns)
                if pd.notna(row[col_price])
            ]
            events.append(
                BookEvent(
                    timestamp=timestamps.iloc[idx],
                    bids=bids[:depth],
                    asks=asks[:depth],
                )
            )

        return cls(events, depth=depth)

    def __iter__(self) -> Iterator[OrderBookSnapshot]:
        self._index = 0
        return self.snapshots()

    def snapshots(self) -> Iterator[OrderBookSnapshot]:
        """Iterator of depth-limited order book snapshots."""
        for event in self._events:
            yield self._to_snapshot(event)

    def snapshot_at(self, timestamp: datetime | pd.Timestamp) -> OrderBookSnapshot:
        """Return the closest snapshot at or before the supplied timestamp."""
        ts = pd.Timestamp(timestamp)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")

        candidate = None
        for event in self._events:
            if event.timestamp <= ts:
                candidate = event
            else:
                break
        if candidate is None:
            candidate = self._events[0]
        return self._to_snapshot(candidate)

    def latest(self) -> OrderBookSnapshot:
        """Return the most recent snapshot."""
        return self._to_snapshot(self._events[-1])

    def reset(self) -> None:
        self._index = 0

    def _to_snapshot(self, event: BookEvent) -> OrderBookSnapshot:
        bids = event.bids[: self.depth]
        asks = event.asks[: self.depth]
        return OrderBookSnapshot(
            timestamp=event.timestamp.to_pydatetime(),
            bids=list(bids),
            asks=list(asks),
        )


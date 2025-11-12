"""Incremental/event streaming backtester."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence

import pandas as pd

from qantify.backtest.event import EventBacktester, EventBacktestResult, EventContext

from qantify.backtest.errors import ConfigurationError


@dataclass(slots=True)
class IncrementalResult:
    """Container returned from `IncrementalBacktester.finalize`."""

    result: EventBacktestResult


class IncrementalBacktester(EventBacktester):
    """Allow bar-by-bar ingestion for live-simulation workflows."""

    def __init__(
        self,
        *,
        symbol: str,
        strategy,
        initial_cash: float = 100_000.0,
        commission_model=None,
        slippage_model=None,
        price_column: str = "close",
        execution_engine=None,
        risk_rules: Optional[Iterable] = None,
        columns: Optional[Sequence[str]] = None,
    ) -> None:
        columns = list(columns or ["open", "high", "low", "close", "volume"])
        template = pd.DataFrame(columns=columns, index=pd.DatetimeIndex([], tz="UTC"))
        super().__init__(
            template,
            symbol=symbol,
            strategy=strategy,
            initial_cash=initial_cash,
            commission_model=commission_model,
            slippage_model=slippage_model,
            price_column=price_column,
            execution_engine=execution_engine,
            risk_rules=risk_rules,
        )
        self._initialized = False
        self._bar_index = 0
        self._columns = columns

    def ingest(self, timestamp: pd.Timestamp, row: Mapping[str, float]) -> None:
        ts = pd.Timestamp(timestamp)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")

        series = pd.Series(row, index=self._columns, dtype=float)
        missing = set(self._columns) - set(series.index)
        if missing:
            for col in missing:
                series[col] = float("nan")
            series = series[self._columns]

        self.data.loc[ts] = series
        view = self.data.loc[:ts]
        current_row = view.iloc[-1]

        if not self._initialized:
            self._initialize_incremental(ts, current_row, view)
        else:
            self._process_incremental_bar(ts, current_row, view)
        self._bar_index += 1

    def run_stream(self, stream: Iterable[tuple[pd.Timestamp, Mapping[str, float]]]) -> IncrementalResult:
        for timestamp, row in stream:
            self.ingest(timestamp, row)
        return self.finalize()

    def _initialize_incremental(self, timestamp: pd.Timestamp, row: pd.Series, data_view: pd.DataFrame) -> None:
        self._initialized = True
        if self.risk_manager.rules:
            self.risk_manager.reset()

        self.broker.set_market_state(timestamp, row)
        context = EventContext(
            data=data_view,
            timestamp=timestamp,
            row=row,
            index=self._bar_index,
            broker=self.broker,
            portfolio=self.portfolio,
        )
        if hasattr(self.strategy, "on_start"):
            self.strategy.on_start(context)
        self._process_incremental_bar(timestamp, row, data_view)

    def _process_incremental_bar(self, timestamp: pd.Timestamp, row: pd.Series, data_view: pd.DataFrame) -> None:
        self.broker.set_market_state(timestamp, row)
        context = EventContext(
            data=data_view,
            timestamp=timestamp,
            row=row,
            index=self._bar_index,
            broker=self.broker,
            portfolio=self.portfolio,
        )
        self.strategy.on_bar(context)
        price = float(row[self.price_column])
        snapshot = self.portfolio.snapshot(timestamp.to_pydatetime(), {self.symbol: price})
        self.snapshots.append(snapshot)

    def finalize(self) -> IncrementalResult:
        if not self.snapshots:
            raise ConfigurationError("No bars processed in incremental backtest.")
        last_timestamp = self.data.index[-1]
        last_row = self.data.iloc[-1]
        context = EventContext(
            data=self.data,
            timestamp=last_timestamp,
            row=last_row,
            index=self._bar_index - 1,
            broker=self.broker,
            portfolio=self.portfolio,
        )
        if hasattr(self.strategy, "on_finish"):
            self.strategy.on_finish(context)

        equity_curve = pd.Series(
            data=[snapshot.equity for snapshot in self.snapshots],
            index=self.data.index[: len(self.snapshots)],
            name="equity",
        )

        result = EventBacktestResult(
            equity_curve=equity_curve,
            orders=self.orders,
            fills=self.fills,
            snapshots=self.snapshots,
            cancelled_orders=self.cancelled_orders,
            trades=self.trades,
            risk_events=self.risk_manager.summary() if self.risk_manager.rules else None,
        )
        return IncrementalResult(result=result)


__all__ = ["IncrementalBacktester", "IncrementalResult"]


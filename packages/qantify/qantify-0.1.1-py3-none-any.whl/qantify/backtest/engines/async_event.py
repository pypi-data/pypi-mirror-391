"""Async event-driven backtester with coroutine support."""

from __future__ import annotations

import asyncio
import inspect
from typing import Awaitable, Callable, Optional

import pandas as pd

from qantify.backtest.event import EventBacktester, EventContext, EventBacktestResult
from qantify.backtest.errors import ConfigurationError


async def _maybe_await(func: Optional[Callable], *args, **kwargs) -> None:
    if func is None:
        return
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        await result


class AsyncEventBacktester(EventBacktester):
    """Async variant of the event backtester that respects coroutine hooks."""

    async def run_async(self) -> EventBacktestResult:
        if self.data.empty:
            raise ConfigurationError("Cannot run event-driven backtest on empty dataset.")

        if self.risk_manager.rules:
            self.risk_manager.reset()

        first_index = 0
        first_timestamp = self.data.index[first_index]
        first_row = self.data.iloc[first_index]

        self.broker.set_market_state(first_timestamp, first_row)

        context = EventContext(
            data=self.data,
            timestamp=first_timestamp,
            row=first_row,
            index=first_index,
            broker=self.broker,
            portfolio=self.portfolio,
        )

        await _maybe_await(getattr(self.strategy, "on_start", None), context)

        for idx, (timestamp, row) in enumerate(self.data.iterrows()):
            self.broker.set_market_state(timestamp, row)

            context = EventContext(
                data=self.data,
                timestamp=timestamp,
                row=row,
                index=idx,
                broker=self.broker,
                portfolio=self.portfolio,
            )

            await _maybe_await(self.strategy.on_bar, context)

            price = float(row[self.price_column])
            snapshot = self.portfolio.snapshot(timestamp.to_pydatetime(), {self.symbol: price})
            self.snapshots.append(snapshot)

        finish_context = EventContext(
            data=self.data,
            timestamp=self.data.index[-1],
            row=self.data.iloc[-1],
            index=len(self.data) - 1,
            broker=self.broker,
            portfolio=self.portfolio,
        )
        await _maybe_await(getattr(self.strategy, "on_finish", None), finish_context)

        equity_curve = pd.Series(
            data=[snapshot.equity for snapshot in self.snapshots],
            index=self.data.index[: len(self.snapshots)],
            name="equity",
        )

        return EventBacktestResult(
            equity_curve=equity_curve,
            orders=self.orders,
            fills=self.fills,
            snapshots=self.snapshots,
            cancelled_orders=self.cancelled_orders,
            trades=self.trades,
            risk_events=self.risk_manager.summary() if self.risk_manager.rules else None,
        )

    def run(self) -> EventBacktestResult:  # type: ignore[override]
        return asyncio.run(self.run_async())


__all__ = ["AsyncEventBacktester"]


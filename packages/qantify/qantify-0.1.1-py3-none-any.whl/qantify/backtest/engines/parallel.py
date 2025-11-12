"""Parallel execution utilities for event/vectorized backtests."""

from __future__ import annotations

from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from qantify.backtest.event import EventBacktester, EventBacktestResult
from qantify.backtest.vectorized import run as run_vectorized
from qantify.strategy import Strategy


class ParallelEventExecutor:
    """Run multiple event-driven backtests in parallel threads."""

    def __init__(self, *, max_workers: Optional[int] = None) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(
        self,
        data: pd.DataFrame,
        strategy_factory: Callable[[], Strategy],
        *,
        symbol: str,
        initial_cash: float = 100_000.0,
        kwargs: Optional[dict] = None,
    ) -> Future:
        kwargs = kwargs or {}

        def _task() -> EventBacktestResult:
            strategy = strategy_factory()
            engine = EventBacktester(data, symbol=symbol, strategy=strategy, initial_cash=initial_cash, **kwargs)
            return engine.run()

        return self._executor.submit(_task)

    def run_batch(
        self,
        jobs: Sequence[Tuple[pd.DataFrame, Callable[[], Strategy], str]],
        *,
        initial_cash: float = 100_000.0,
        kwargs: Optional[dict] = None,
    ) -> List[EventBacktestResult]:
        futures = [
            self.submit(data, factory, symbol=symbol, initial_cash=initial_cash, kwargs=kwargs)
            for data, factory, symbol in jobs
        ]
        results = []
        for fut in as_completed(futures):
            results.append(fut.result())
        return results

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


class ParallelVectorizedExecutor:
    """Process vectorized backtests across processes for heavy workloads."""

    def __init__(self, *, max_workers: Optional[int] = None) -> None:
        self._executor = ProcessPoolExecutor(max_workers=max_workers)

    def submit(self, *args, **kwargs) -> Future:
        return self._executor.submit(run_vectorized, *args, **kwargs)

    def map(self, tasks: Iterable[Tuple]) -> List:
        futures = [self.submit(*task) for task in tasks]
        return [f.result() for f in futures]

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


class GPUVectorizedPipeline:
    """Simple GPU-accelerated helper leveraging CuPy when available."""

    def __init__(self) -> None:
        try:
            import cupy as cp  # type: ignore

            self.xp = cp
            self._gpu_available = True
        except Exception:  # pragma: no cover - optional dependency
            import numpy as np

            self.xp = np  # type: ignore[assignment]
            self._gpu_available = False

    @property
    def gpu_enabled(self) -> bool:
        return self._gpu_available

    def simulate_equity(self, returns: Sequence[float], initial_equity: float = 1.0) -> Sequence[float]:
        xp = self.xp
        array = xp.asarray(returns, dtype=float)
        cumulative = xp.cumprod(1 + array)
        equity = initial_equity * cumulative
        if hasattr(xp, "asnumpy"):
            return xp.asnumpy(equity).tolist()
        return equity.tolist()


__all__ = ["ParallelEventExecutor", "ParallelVectorizedExecutor", "GPUVectorizedPipeline"]


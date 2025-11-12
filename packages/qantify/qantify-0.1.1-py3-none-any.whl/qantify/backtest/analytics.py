"""Analytics and reporting utilities for backtest results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd

from .types import Order, Fill


def monte_carlo_resample(equity_curve: pd.Series, *, n_paths: int = 1000, block_size: int = 5) -> pd.DataFrame:
    """Block-bootstrap resampling of equity returns."""

    if equity_curve.empty:
        return pd.DataFrame()
    returns = equity_curve.pct_change().dropna().to_numpy()
    rng = np.random.default_rng()
    paths = []
    for _ in range(n_paths):
        samples = []
        while len(samples) < len(returns):
            start = rng.integers(0, len(returns))
            block = returns[start : start + block_size]
            samples.extend(block)
        samples = np.array(samples[: len(returns)])
        equity = np.cumprod(1 + samples) * equity_curve.iloc[0]
        paths.append(equity)
    index = equity_curve.index[1:]
    return pd.DataFrame(paths, columns=index)


def drawdown_breakdown(equity_curve: pd.Series) -> pd.DataFrame:
    """Return drawdown periods with start/end/max depth."""

    if equity_curve.empty:
        return pd.DataFrame(columns=["start", "end", "depth"])
    cumulative = equity_curve.cummax()
    drawdown = equity_curve / cumulative - 1
    results: List[Tuple[pd.Timestamp, pd.Timestamp, float]] = []
    in_drawdown = False
    start = equity_curve.index[0]
    max_depth = 0.0
    for idx, value in drawdown.items():
        if value < 0 and not in_drawdown:
            in_drawdown = True
            start = idx
            max_depth = value
        if in_drawdown:
            max_depth = min(max_depth, value)
        if value == 0 and in_drawdown:
            results.append((start, idx, max_depth))
            in_drawdown = False
    if in_drawdown:
        results.append((start, equity_curve.index[-1], max_depth))
    return pd.DataFrame(results, columns=["start", "end", "depth"])


def execution_quality_report(orders: Iterable[Order], fills: Iterable[Fill]) -> pd.DataFrame:
    """Summarise fill quality relative to benchmarks recorded in order metadata."""

    summaries = []
    fills_by_order = {fill.order.id: fill for fill in fills if fill.order is not None}
    for order in orders:
        benchmark = order.meta.get("benchmark_price", order.price)
        fill = fills_by_order.get(order.id)
        if fill is None or benchmark is None:
            continue
        slippage = fill.price - benchmark
        direction = 1 if order.side == order.side.BUY else -1
        effective = slippage * direction
        summaries.append(
            {
                "order_id": order.id,
                "side": order.side.value,
                "benchmark": benchmark,
                "fill_price": fill.price,
                "quantity": fill.quantity,
                "slippage": slippage,
                "effective_slippage": effective,
            }
        )
    return pd.DataFrame(summaries)


def factor_attribution(
    equity_returns: pd.Series,
    factor_returns: pd.DataFrame,
) -> pd.DataFrame:
    """Compute linear attribution of strategy returns to multi-factor exposures."""

    aligned = pd.concat([equity_returns, factor_returns], axis=1, join="inner").dropna()
    if aligned.empty:
        return pd.DataFrame(columns=["factor", "beta"])
    y = aligned.iloc[:, 0].to_numpy()
    X = aligned.iloc[:, 1:].to_numpy()
    X = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    intercept, exposures = beta[0], beta[1:]
    rows = [{"factor": "alpha", "beta": intercept}]
    for name, value in zip(aligned.columns[1:], exposures):
        rows.append({"factor": name, "beta": value})
    return pd.DataFrame(rows)


__all__ = [
    "monte_carlo_resample",
    "drawdown_breakdown",
    "execution_quality_report",
    "factor_attribution",
]


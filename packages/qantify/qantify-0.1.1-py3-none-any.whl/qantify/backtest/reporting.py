"""Reporting helpers for backtesting outputs."""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np
import pandas as pd

from .types import Fill, Order, Trade


def orders_to_frame(orders: Iterable[Order]) -> pd.DataFrame:
    records = []
    for order in orders:
        records.append(
            {
                "id": order.id,
                "timestamp": order.timestamp,
                "symbol": order.symbol,
                "side": order.side.value,
                "type": order.type.value,
                "quantity": order.quantity,
                "filled_quantity": order.filled_quantity,
                "status": order.status.value,
                "price": order.price,
                "stop_price": order.stop_price,
                "time_in_force": order.time_in_force.value,
            }
        )
    frame = pd.DataFrame(records)
    if not frame.empty:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    return frame


def fills_to_frame(fills: Iterable[Fill]) -> pd.DataFrame:
    records = []
    for fill in fills:
        records.append(
            {
                "timestamp": fill.timestamp,
                "symbol": fill.symbol,
                "side": fill.side.value,
                "price": fill.price,
                "quantity": fill.quantity,
                "commission": fill.commission,
                "slippage": fill.slippage,
                "order_id": fill.order.id if fill.order else None,
            }
        )
    frame = pd.DataFrame(records)
    if not frame.empty:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    return frame


def trades_to_frame(trades: Iterable[Trade]) -> pd.DataFrame:
    records = []
    for trade in trades:
        entry = trade.entry
        exit_fill = trade.exit
        records.append(
            {
                "entry_time": entry.timestamp if entry else None,
                "exit_time": exit_fill.timestamp if exit_fill else None,
                "symbol": entry.symbol if entry else None,
                "direction": trade.direction.value,
                "quantity": trade.quantity,
                "entry_price": entry.price if entry else None,
                "exit_price": exit_fill.price if exit_fill else None,
                "pnl": trade.pnl,
                "return_pct": trade.return_pct,
                "max_drawdown": trade.max_drawdown,
                "duration_secs": trade.duration,
            }
        )
    frame = pd.DataFrame(records)
    if not frame.empty:
        frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)
        frame["exit_time"] = pd.to_datetime(frame["exit_time"], utc=True)
    return frame


def equity_statistics(
    equity: pd.Series,
    *,
    risk_free: float = 0.0,
    periods_per_year: int = 252,
) -> Mapping[str, float]:
    if equity.empty:
        return {}

    equity = equity.astype(float)
    returns = equity.pct_change().dropna()
    if returns.empty:
        return {}

    mean_return = returns.mean()
    vol = returns.std()
    annual_return = (1 + mean_return) ** periods_per_year - 1
    annual_vol = vol * np.sqrt(periods_per_year)
    sharpe = np.nan if annual_vol == 0 else (annual_return - risk_free) / annual_vol

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdowns = (cumulative / running_max) - 1
    max_drawdown = drawdowns.min()

    calmar = np.nan
    if max_drawdown != 0:
        calmar = annual_return / abs(max_drawdown)

    hit_rate = (returns > 0).mean()

    return {
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_vol),
        "sharpe": float(sharpe) if not np.isnan(sharpe) else np.nan,
        "max_drawdown": float(max_drawdown),
        "calmar": float(calmar) if calmar and not np.isnan(calmar) else np.nan,
        "hit_rate": float(hit_rate),
    }


__all__ = [
    "orders_to_frame",
    "fills_to_frame",
    "trades_to_frame",
    "equity_statistics",
]

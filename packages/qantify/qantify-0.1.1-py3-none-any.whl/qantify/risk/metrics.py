"""Core performance and risk metric computations."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from qantify.backtest.types import Trade


EPS = 1e-12


@dataclass(slots=True)
class RiskMetrics:
    total_return: float
    cagr: float
    annual_volatility: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float
    ulcer_index: float
    value_at_risk: float
    expected_shortfall: float
    skewness: float
    kurtosis: float
    hit_rate: float
    tail_ratio: float

    @property
    def annual_return(self) -> float:
        """Alias for CAGR to maintain backwards compatibility."""
        return self.cagr


@dataclass(slots=True)
class TradeMetrics:
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    avg_duration_secs: Optional[float]


def compute_returns(equity: pd.Series) -> pd.Series:
    if equity.empty:
        return pd.Series(dtype=float)
    returns = equity.astype(float).pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    return returns


def compute_drawdowns(equity: pd.Series) -> pd.DataFrame:
    if equity.empty:
        return pd.DataFrame(columns=["equity", "peak", "drawdown", "drawdown_pct"])

    equity = equity.astype(float)
    rolling_max = equity.cummax()
    drawdown = equity - rolling_max
    drawdown_pct = drawdown.div(rolling_max).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return pd.DataFrame(
        {
            "equity": equity,
            "peak": rolling_max,
            "drawdown": drawdown,
            "drawdown_pct": drawdown_pct,
        }
    )


def _annualize_rate(rate: float, periods: int, periods_per_year: int) -> float:
    if periods <= 0:
        return 0.0
    return (1 + rate) ** (periods_per_year / periods) - 1


def compute_risk_metrics(
    equity: pd.Series,
    *,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.0,
    var_level: float = 0.05,
) -> RiskMetrics:
    if equity.empty:
        return RiskMetrics(*(0.0 for _ in range(14)))

    equity = equity.astype(float)
    returns = compute_returns(equity)
    if returns.empty:
        return RiskMetrics(*(0.0 for _ in range(14)))

    total_return = float(np.round(equity.iloc[-1] / equity.iloc[0] - 1, 12))
    mean_return = returns.mean()
    periods = len(returns)

    cagr = _annualize_rate(total_return, periods, periods_per_year)

    excess_returns = returns - (risk_free_rate / periods_per_year)
    volatility = returns.std(ddof=0) * sqrt(periods_per_year)
    sharpe = 0.0 if volatility == 0 else (excess_returns.mean() * periods_per_year) / volatility

    downside = returns[returns < 0]
    downside_std = 0.0
    if not downside.empty:
        downside_std = downside.std(ddof=0) * sqrt(periods_per_year)
    sortino = 0.0 if downside_std == 0 else (mean_return * periods_per_year) / downside_std

    drawdowns = compute_drawdowns(equity)
    max_drawdown = drawdowns["drawdown_pct"].min() if not drawdowns.empty else 0.0
    ulcer_index = float(np.sqrt(np.mean(drawdowns["drawdown_pct"] ** 2))) if not drawdowns.empty else 0.0

    calmar = 0.0
    if max_drawdown != 0:
        calmar = cagr / abs(max_drawdown)

    var = returns.quantile(var_level)
    tail = returns[returns <= var]
    expected_shortfall = tail.mean() if not tail.empty else 0.0

    skewness = returns.skew() if hasattr(returns, "skew") else 0.0
    kurtosis = returns.kurtosis() if hasattr(returns, "kurtosis") else 0.0

    hit_rate = (returns > 0).mean()
    tail_ratio = 0.0
    if var != 0:
        tail_ratio = abs(returns.quantile(0.95) / var)

    return RiskMetrics(
        total_return=total_return,
        cagr=cagr,
        annual_volatility=volatility,
        sharpe=sharpe,
        sortino=sortino,
        calmar=calmar,
        max_drawdown=max_drawdown,
        ulcer_index=ulcer_index,
        value_at_risk=float(var),
        expected_shortfall=float(expected_shortfall),
        skewness=float(skewness if not np.isnan(skewness) else 0.0),
        kurtosis=float(kurtosis if not np.isnan(kurtosis) else 0.0),
        hit_rate=float(hit_rate if not np.isnan(hit_rate) else 0.0),
        tail_ratio=float(tail_ratio if not np.isnan(tail_ratio) else 0.0),
    )


def compute_trade_metrics(trades: Iterable[Trade]) -> TradeMetrics:
    trades = list(trades)
    total = len(trades)
    if total == 0:
        return TradeMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None)

    pnls = np.array([trade.pnl for trade in trades], dtype=float)
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]

    win_rate = float(len(wins) / total)
    avg_win = float(wins.mean()) if wins.size else 0.0
    avg_loss = float(losses.mean()) if losses.size else 0.0
    profit_factor = 0.0
    gross_profit = wins.sum() if wins.size else 0.0
    gross_loss = abs(losses.sum()) if losses.size else 0.0
    if gross_loss > EPS:
        profit_factor = gross_profit / gross_loss

    expectancy = float(pnls.mean())
    largest_win = float(wins.max()) if wins.size else 0.0
    largest_loss = float(losses.min()) if losses.size else 0.0

    durations = [trade.duration for trade in trades if trade.duration is not None]
    avg_duration = float(np.mean(durations)) if durations else None

    return TradeMetrics(
        total_trades=total,
        win_rate=win_rate,
        profit_factor=profit_factor,
        expectancy=expectancy,
        average_win=avg_win,
        average_loss=avg_loss,
        largest_win=largest_win,
        largest_loss=largest_loss,
        avg_duration_secs=avg_duration,
    )


__all__ = [
    "RiskMetrics",
    "TradeMetrics",
    "compute_returns",
    "compute_drawdowns",
    "compute_risk_metrics",
    "compute_trade_metrics",
]

"""High-level risk report assembly utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import sqrt
from typing import Dict, Iterable, Optional

import pandas as pd

from qantify.backtest.types import Trade

from .metrics import (
    RiskMetrics,
    TradeMetrics,
    compute_drawdowns,
    compute_returns,
    compute_risk_metrics,
    compute_trade_metrics,
)


@dataclass(slots=True)
class RiskReport:
    equity_curve: pd.Series
    returns: pd.Series
    drawdowns: pd.DataFrame
    metrics: RiskMetrics
    trade_metrics: Optional[TradeMetrics] = None
    rolling_sharpe: Optional[pd.Series] = None
    rolling_sortino: Optional[pd.Series] = None
    annual_returns: Optional[pd.Series] = None
    settings: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "metrics": asdict(self.metrics),
        }
        if self.trade_metrics is not None:
            payload["trade_metrics"] = asdict(self.trade_metrics)
        payload["settings"] = dict(self.settings)
        payload["returns"] = self.returns.to_dict()
        payload["equity_curve"] = self.equity_curve.to_dict()
        payload["drawdowns"] = self.drawdowns.to_dict("list")
        if self.rolling_sharpe is not None:
            payload["rolling_sharpe"] = self.rolling_sharpe.to_dict()
        if self.rolling_sortino is not None:
            payload["rolling_sortino"] = self.rolling_sortino.to_dict()
        if self.annual_returns is not None:
            payload["annual_returns"] = self.annual_returns.to_dict()
        return payload

    def summary_frame(self) -> pd.DataFrame:
        rows = asdict(self.metrics)
        if self.trade_metrics is not None:
            rows.update({f"trade_{k}": v for k, v in asdict(self.trade_metrics).items()})
        return pd.DataFrame(rows, index=[0]).T.rename(columns={0: "value"})


def build_risk_report(
    equity_curve: pd.Series,
    *,
    trades: Optional[Iterable[Trade]] = None,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.0,
    rolling_window: int = 63,
    var_level: float = 0.05,
) -> RiskReport:
    if equity_curve.empty:
        equity_curve = pd.Series(dtype=float)

    returns = compute_returns(equity_curve)
    drawdowns = compute_drawdowns(equity_curve)
    metrics = compute_risk_metrics(
        equity_curve,
        periods_per_year=periods_per_year,
        risk_free_rate=risk_free_rate,
        var_level=var_level,
    )

    trade_metrics = compute_trade_metrics(trades) if trades is not None else None

    rolling_sharpe = None
    rolling_sortino = None
    if not returns.empty and rolling_window > 1:
        rolling_sharpe = _rolling_sharpe(returns, window=rolling_window, risk_free=risk_free_rate, periods_per_year=periods_per_year)
        rolling_sortino = _rolling_sortino(returns, window=rolling_window, periods_per_year=periods_per_year)

    annual_returns = _annual_returns(equity_curve)

    return RiskReport(
        equity_curve=equity_curve,
        returns=returns,
        drawdowns=drawdowns,
        metrics=metrics,
        trade_metrics=trade_metrics,
        rolling_sharpe=rolling_sharpe,
        rolling_sortino=rolling_sortino,
        annual_returns=annual_returns,
        settings={
            "periods_per_year": periods_per_year,
            "risk_free_rate": risk_free_rate,
            "rolling_window": rolling_window,
            "value_at_risk_level": var_level,
        },
    )


def _annual_returns(equity: pd.Series) -> Optional[pd.Series]:
    if equity.empty:
        return None
    frame = equity.to_frame(name="equity")
    frame["year"] = frame.index.to_period("Y")
    grouped = frame.groupby("year")["equity"]
    annual = grouped.last() / grouped.first() - 1
    annual.index = annual.index.to_timestamp()
    return annual


def _rolling_sharpe(
    returns: pd.Series,
    *,
    window: int,
    risk_free: float,
    periods_per_year: int,
) -> pd.Series:
    excess = returns - (risk_free / periods_per_year)

    def compute(window_values: pd.Series) -> float:
        if window_values.std(ddof=0) == 0:
            return 0.0
        return (window_values.mean() * window) / (window_values.std(ddof=0) * sqrt(window))

    return excess.rolling(window=window, min_periods=window).apply(compute, raw=False)


def _rolling_sortino(
    returns: pd.Series,
    *,
    window: int,
    periods_per_year: int,
) -> pd.Series:
    def compute(window_values: pd.Series) -> float:
        downside = window_values[window_values < 0]
        if downside.empty:
            return 0.0
        downside_std = downside.std(ddof=0)
        if downside_std == 0:
            return 0.0
        return (window_values.mean() * window) / (downside_std * sqrt(window))

    return returns.rolling(window=window, min_periods=window).apply(compute, raw=False)


__all__ = [
    "RiskReport",
    "build_risk_report",
]

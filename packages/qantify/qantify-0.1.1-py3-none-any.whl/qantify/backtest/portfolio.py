"""Portfolio accounting model for event-driven backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import numpy as np

from .errors import ExecutionError
from .types import Fill, OrderSide, Position, PositionSide, PortfolioSnapshot


@dataclass(slots=True)
class PortfolioState:
    cash_balances: Dict[str, float]
    positions: Dict[str, Position]
    realized_pnl: float = 0.0
    funding_cost: float = 0.0

    def total_equity(self, prices: Dict[str, float], fx_rates: Dict[str, float], base_currency: str) -> float:
        equity = sum(
            balance * fx_rates.get(currency, 1.0)
            for currency, balance in self.cash_balances.items()
        )
        for symbol, position in self.positions.items():
            price = prices.get(symbol, position.avg_price)
            currency = position.currency or base_currency
            fx = fx_rates.get(currency, 1.0)
            notional = position.quantity * price * fx
            if position.side == PositionSide.LONG:
                equity += notional
            else:
                equity -= notional
        return equity - self.funding_cost


class Portfolio:
    """Mutable portfolio used by the event-driven engine."""

    def __init__(
        self,
        initial_cash: float = 100_000.0,
        *,
        base_currency: str = "USD",
        allow_short: bool = True,
        cash_allocations: Optional[Dict[str, float]] = None,
    ) -> None:
        if initial_cash <= 0:
            raise ValueError("Initial cash must be positive.")
        allocations = cash_allocations or {base_currency: initial_cash}
        self.initial_cash = float(initial_cash)
        self.base_currency = base_currency
        self.allow_short = allow_short
        self.fx_rates: Dict[str, float] = {base_currency: 1.0}
        self.state = PortfolioState(cash_balances={k: float(v) for k, v in allocations.items()}, positions={})

    def apply_fill(self, fill: Fill) -> None:
        symbol = fill.symbol
        signed_fill = fill.quantity if fill.side == OrderSide.BUY else -fill.quantity

        # Cash update (buys consume cash, sells credit cash)
        currency = getattr(fill.order, "settlement_currency", self.base_currency)
        balance = self.state.cash_balances.get(currency, 0.0)
        cash_delta = -signed_fill * fill.price
        balance += cash_delta
        balance -= fill.commission
        self.state.cash_balances[currency] = balance

        position = self.state.positions.get(symbol)
        signed_position = 0.0
        avg_price = fill.price
        if position is not None:
            signed_position = position.quantity if position.side == PositionSide.LONG else -position.quantity
            avg_price = position.avg_price

        new_signed = signed_position + signed_fill

        realized_pnl = 0.0
        if signed_position * signed_fill < 0:
            close_qty = min(abs(signed_position), abs(signed_fill))
            if signed_position > 0:
                realized_pnl = close_qty * (fill.price - avg_price)
            else:
                realized_pnl = close_qty * (avg_price - fill.price)
            self.state.realized_pnl += realized_pnl

        if abs(new_signed) <= 1e-9:
            self.state.positions.pop(symbol, None)
            return

        new_side = PositionSide.LONG if new_signed > 0 else PositionSide.SHORT
        if new_side == PositionSide.SHORT and not self.allow_short:
            raise ExecutionError("Short positions are not supported by this portfolio.")

        new_quantity = abs(new_signed)

        if signed_position == 0 or np.sign(new_signed) != np.sign(signed_position):
            new_avg_price = fill.price
        elif signed_position * signed_fill > 0:
            # Increasing existing exposure
            added_qty = abs(signed_fill)
            total_qty = abs(signed_position) + added_qty
            new_avg_price = (avg_price * abs(signed_position) + fill.price * added_qty) / total_qty
        else:
            # Reducing but same direction remains
            new_avg_price = avg_price

        position_currency = getattr(fill.order, "settlement_currency", self.base_currency)
        self.state.positions[symbol] = Position(
            symbol=symbol,
            side=new_side,
            quantity=new_quantity,
            avg_price=new_avg_price,
            currency=position_currency,
        )

    def snapshot(self, timestamp: datetime, prices: Dict[str, float]) -> PortfolioSnapshot:
        positions_copy = []
        unrealized_total = 0.0
        gross_exposure = 0.0
        for position in self.state.positions.values():
            price = prices.get(position.symbol, position.avg_price)
            currency = position.currency or self.base_currency
            fx = self.fx_rates.get(currency, 1.0)
            if position.side == PositionSide.LONG:
                unrealized = (price - position.avg_price) * position.quantity * fx
                gross_exposure += position.quantity * price * fx
            else:
                unrealized = (position.avg_price - price) * position.quantity * fx
                gross_exposure += position.quantity * price * fx
            unrealized_total += unrealized
            positions_copy.append(
                Position(
                    symbol=position.symbol,
                    side=position.side,
                    quantity=position.quantity,
                    avg_price=position.avg_price,
                    unrealized_pnl=unrealized,
                    currency=position.currency,
                )
            )

        equity = self.state.total_equity(prices, self.fx_rates, self.base_currency)

        return PortfolioSnapshot(
            timestamp=timestamp,
            equity=equity,
            cash=self.state.cash_balances.get(self.base_currency, 0.0),
            positions=tuple(positions_copy),
            realized_pnl=self.state.realized_pnl,
            unrealized_pnl=unrealized_total,
            gross_exposure=gross_exposure,
        )

    def update_fx_rate(self, currency: str, rate: float) -> None:
        self.fx_rates[currency] = rate

    def apply_funding(self, currency: str, amount: float) -> None:
        balance = self.state.cash_balances.get(currency, 0.0)
        balance += amount
        self.state.cash_balances[currency] = balance
        self.state.funding_cost += abs(amount)

    def apply_corporate_action(self, symbol: str, action_type: str, value: float) -> None:
        position = self.state.positions.get(symbol)
        if not position:
            return
        if action_type == "DIVIDEND":
            currency = position.currency or self.base_currency
            self.state.cash_balances[currency] = self.state.cash_balances.get(currency, 0.0) + value * position.quantity
        elif action_type == "SPLIT" and value > 0:
            position.quantity *= value
            position.avg_price /= value
        elif action_type == "COUPON":
            currency = position.currency or self.base_currency
            self.state.cash_balances[currency] = self.state.cash_balances.get(currency, 0.0) + value

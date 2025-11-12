"""Commission and slippage abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .types import Fill, Order


class CommissionModel(ABC):
    """Interface for calculating commissions on order fills."""

    @abstractmethod
    def compute(self, order: Order, price: float, quantity: float) -> float:
        """Return commission amount for the given execution."""


class NoCommission(CommissionModel):
    """Commission model that always returns zero."""

    def compute(self, order: Order, price: float, quantity: float) -> float:
        return 0.0


class PercentageCommission(CommissionModel):
    """Commission proportional to notional value (price * quantity)."""

    def __init__(self, rate: float) -> None:
        if rate < 0:
            raise ValueError("Commission rate cannot be negative.")
        self.rate = rate

    def compute(self, order: Order, price: float, quantity: float) -> float:
        return abs(price * quantity) * self.rate


class SlippageModel(ABC):
    """Interface for slippage adjustments."""

    @abstractmethod
    def apply(self, order: Order, price: float, quantity: float) -> float:
        """Return adjusted price incorporating slippage effects."""


class NoSlippage(SlippageModel):
    """Slippage model that leaves prices unchanged."""

    def apply(self, order: Order, price: float, quantity: float) -> float:
        return price

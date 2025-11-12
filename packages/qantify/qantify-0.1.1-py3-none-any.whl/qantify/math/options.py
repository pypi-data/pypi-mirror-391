"""Option pricing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
from typing import Literal

import numpy as np


def _norm_cdf(x: np.ndarray | float) -> np.ndarray | float:
    try:
        from scipy.stats import norm  # type: ignore
        return norm.cdf(x)
    except Exception:  # pragma: no cover - fallback approximation
        return 0.5 * (1 + np.erf(np.asarray(x) / np.sqrt(2)))


@dataclass(slots=True)
class BlackScholes:
    s0: float
    strike: float
    rate: float
    sigma: float
    maturity: float

    def price(self, option_type: Literal["call", "put"] = "call") -> float:
        d1 = (log(self.s0 / self.strike) + (self.rate + 0.5 * self.sigma**2) * self.maturity) / (
            self.sigma * sqrt(self.maturity)
        )
        d2 = d1 - self.sigma * sqrt(self.maturity)
        if option_type == "call":
            price = self.s0 * _norm_cdf(d1) - self.strike * np.exp(-self.rate * self.maturity) * _norm_cdf(d2)
        else:
            price = self.strike * np.exp(-self.rate * self.maturity) * _norm_cdf(-d2) - self.s0 * _norm_cdf(-d1)
        return float(price)


class OptionGreeks:
    @staticmethod
    def delta(s0: float, strike: float, rate: float, sigma: float, maturity: float, option_type: str = "call") -> float:
        d1 = (log(s0 / strike) + (rate + 0.5 * sigma**2) * maturity) / (sigma * sqrt(maturity))
        if option_type == "call":
            return float(_norm_cdf(d1))
        return float(_norm_cdf(d1) - 1)

    @staticmethod
    def gamma(s0: float, strike: float, rate: float, sigma: float, maturity: float) -> float:
        d1 = (log(s0 / strike) + (rate + 0.5 * sigma**2) * maturity) / (sigma * sqrt(maturity))
        try:
            from scipy.stats import norm  # type: ignore
            pdf = norm.pdf(d1)
        except Exception:
            pdf = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * d1**2)
        gamma = pdf / (s0 * sigma * sqrt(maturity))
        return float(gamma)

    @staticmethod
    def vega(s0: float, strike: float, rate: float, sigma: float, maturity: float) -> float:
        d1 = (log(s0 / strike) + (rate + 0.5 * sigma**2) * maturity) / (sigma * sqrt(maturity))
        try:
            from scipy.stats import norm  # type: ignore
            pdf = norm.pdf(d1)
        except Exception:
            pdf = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * d1**2)
        return float(s0 * sqrt(maturity) * pdf)


class BinomialTreePricer:
    def __init__(self, steps: int = 100) -> None:
        self.steps = steps

    def price(
        self,
        s0: float,
        strike: float,
        rate: float,
        sigma: float,
        maturity: float,
        option_type: Literal["call", "put"] = "call",
        american: bool = False,
    ) -> float:
        dt = maturity / self.steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(rate * dt) - d) / (u - d)
        prices = np.array([s0 * (u ** j) * (d ** (self.steps - j)) for j in range(self.steps + 1)])
        if option_type == "call":
            values = np.maximum(prices - strike, 0)
        else:
            values = np.maximum(strike - prices, 0)
        discount = np.exp(-rate * dt)
        for _ in range(self.steps):
            values = discount * (p * values[1:] + (1 - p) * values[:-1])
            if american:
                prices = prices[:-1] / u
                intrinsic = np.maximum(prices - strike, 0) if option_type == "call" else np.maximum(strike - prices, 0)
                values = np.maximum(values, intrinsic)
        return float(values[0])


__all__ = ["BlackScholes", "OptionGreeks", "BinomialTreePricer"]

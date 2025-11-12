"""Finite-difference solvers for derivative pricing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(slots=True)
class CrankNicolsonPricer:
    s_max: float
    n_price_steps: int
    n_time_steps: int

    def price(
        self,
        s0: float,
        strike: float,
        rate: float,
        sigma: float,
        maturity: float,
        option_type: Literal["call", "put"] = "call",
    ) -> float:
        dt = maturity / self.n_time_steps
        ds = self.s_max / self.n_price_steps
        grid = np.zeros((self.n_time_steps + 1, self.n_price_steps + 1))
        prices = np.linspace(0, self.s_max, self.n_price_steps + 1)

        if option_type == "call":
            grid[-1] = np.maximum(prices - strike, 0.0)
        else:
            grid[-1] = np.maximum(strike - prices, 0.0)

        alpha = 0.25 * dt * ((sigma**2) * (np.arange(self.n_price_steps + 1) ** 2) - rate * np.arange(self.n_price_steps + 1))
        beta = -dt * 0.5 * ((sigma**2) * (np.arange(self.n_price_steps + 1) ** 2) + rate)
        gamma = 0.25 * dt * ((sigma**2) * (np.arange(self.n_price_steps + 1) ** 2) + rate * np.arange(self.n_price_steps + 1))

        A = np.zeros((self.n_price_steps - 1, self.n_price_steps - 1))
        B = np.zeros_like(A)
        for i in range(1, self.n_price_steps):
            if i > 1:
                A[i - 1, i - 2] = -alpha[i]
                B[i - 1, i - 2] = alpha[i]
            A[i - 1, i - 1] = 1 - beta[i]
            B[i - 1, i - 1] = 1 + beta[i]
            if i < self.n_price_steps - 1:
                A[i - 1, i] = -gamma[i]
                B[i - 1, i] = gamma[i]

        for t in range(self.n_time_steps - 1, -1, -1):
            rhs = B @ grid[t + 1, 1:-1]
            rhs[0] += alpha[1] * grid[t, 0]
            rhs[-1] += gamma[self.n_price_steps - 1] * grid[t, -1]
            grid[t, 1:-1] = np.linalg.solve(A, rhs)
            grid[t, -1] = (self.s_max - strike) * np.exp(-rate * (maturity - t * dt)) if option_type == "call" else 0.0
            grid[t, 0] = 0.0 if option_type == "call" else strike * np.exp(-rate * (maturity - t * dt))

        idx = int(s0 / ds)
        weight = (s0 - prices[idx]) / ds if idx < self.n_price_steps else 0
        price = (1 - weight) * grid[0, idx] + weight * grid[0, idx + 1]
        return float(price)


__all__ = ["CrankNicolsonPricer"]

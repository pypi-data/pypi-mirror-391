"""Interest rate modeling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(slots=True)
class HullWhiteModel:
    mean_reversion: float
    volatility: float
    theta: float
    r0: float = 0.02
    dt: float = 1 / 252

    def simulate(self, n_steps: int, *, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng()
        rates = np.zeros(n_steps)
        rates[0] = self.r0
        for t in range(1, n_steps):
            dr = self.mean_reversion * (self.theta - rates[t - 1]) * self.dt + self.volatility * np.sqrt(self.dt) * rng.normal()
            rates[t] = rates[t - 1] + dr
        return rates


@dataclass(slots=True)
class CoxIngersollRossModel:
    mean_reversion: float
    theta: float
    volatility: float
    r0: float = 0.02
    dt: float = 1 / 252

    def simulate(self, n_steps: int, *, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng()
        rates = np.zeros(n_steps)
        rates[0] = self.r0
        for t in range(1, n_steps):
            dr = (
                self.mean_reversion * (self.theta - rates[t - 1]) * self.dt
                + self.volatility * np.sqrt(max(rates[t - 1], 0)) * np.sqrt(self.dt) * rng.normal()
            )
            rates[t] = max(rates[t - 1] + dr, 0.0)
        return rates


__all__ = ["HullWhiteModel", "CoxIngersollRossModel"]

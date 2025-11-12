"""Stochastic process simulation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd


@dataclass(slots=True)
class BrownianMotion:
    dt: float = 1 / 252
    drift: float = 0.0
    sigma: float = 1.0

    def generate(self, n_steps: int, *, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng()
        increments = rng.normal(loc=self.drift * self.dt, scale=self.sigma * np.sqrt(self.dt), size=n_steps)
        return np.cumsum(increments)


@dataclass(slots=True)
class GeometricBrownianMotion:
    mu: float
    sigma: float
    s0: float = 1.0
    dt: float = 1 / 252

    def generate(self, n_steps: int, *, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng()
        increments = rng.normal(loc=(self.mu - 0.5 * self.sigma**2) * self.dt, scale=self.sigma * np.sqrt(self.dt), size=n_steps)
        log_path = np.cumsum(increments)
        return self.s0 * np.exp(log_path)


@dataclass(slots=True)
class HestonProcess:
    mu: float
    kappa: float
    theta: float
    xi: float
    rho: float
    s0: float = 1.0
    v0: float = 0.04
    dt: float = 1 / 252

    def generate(self, n_steps: int, *, rng: Optional[np.random.Generator] = None) -> pd.DataFrame:
        rng = rng or np.random.default_rng()
        s = np.zeros(n_steps)
        v = np.zeros(n_steps)
        s[0] = self.s0
        v[0] = self.v0
        for t in range(1, n_steps):
            z1 = rng.normal()
            z2 = rng.normal()
            w1 = z1
            w2 = self.rho * z1 + np.sqrt(1 - self.rho**2) * z2
            v[t] = np.abs(v[t - 1] + self.kappa * (self.theta - v[t - 1]) * self.dt + self.xi * np.sqrt(v[t - 1]) * np.sqrt(self.dt) * w2)
            s[t] = s[t - 1] * np.exp((self.mu - 0.5 * v[t]) * self.dt + np.sqrt(v[t]) * np.sqrt(self.dt) * w1)
        index = pd.RangeIndex(n_steps)
        return pd.DataFrame({"price": s, "variance": v}, index=index)


class MonteCarloEngine:
    def __init__(self, *, rng: Optional[np.random.Generator] = None) -> None:
        self.rng = rng or np.random.default_rng()

    def run(
        self,
        simulator: Callable[[int], np.ndarray | pd.DataFrame],
        *,
        n_paths: int,
        n_steps: int,
        payoff: Callable[[np.ndarray | pd.DataFrame], float],
    ) -> Dict[str, float]:
        payoffs = np.zeros(n_paths)
        for i in range(n_paths):
            path = simulator(n_steps)
            payoffs[i] = payoff(path)
        price = payoffs.mean()
        stderr = payoffs.std(ddof=1) / np.sqrt(n_paths)
        return {"price": float(price), "stderr": float(stderr)}


__all__ = [
    "BrownianMotion",
    "GeometricBrownianMotion",
    "HestonProcess",
    "MonteCarloEngine",
]

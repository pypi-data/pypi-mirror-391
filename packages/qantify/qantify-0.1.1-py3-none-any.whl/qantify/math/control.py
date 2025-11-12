"""Optimal control and execution utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(slots=True)
class AlmgrenChrissOptimalExecution:
    horizon: float
    n_steps: int
    risk_aversion: float
    volatility: float
    market_depth: float
    temporary_impact: float
    initial_position: float

    def optimal_schedule(self) -> Tuple[np.ndarray, np.ndarray]:
        dt = self.horizon / self.n_steps
        kappa = np.sqrt(self.risk_aversion * self.volatility**2 / (self.market_depth * self.temporary_impact))
        times = np.linspace(0, self.horizon, self.n_steps + 1)
        denom = np.sinh(kappa * self.horizon)
        remaining = self.initial_position * np.sinh(kappa * (self.horizon - times)) / denom
        trading_rates = -np.diff(remaining) / dt
        return remaining, trading_rates


class LinearQuadraticRegulator:
    def __init__(
        self,
        A: np.ndarray,
        B: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        *,
        terminal_cost: Optional[np.ndarray] = None,
    ) -> None:
        self.A = np.asarray(A, dtype=float)
        self.B = np.asarray(B, dtype=float)
        self.Q = np.asarray(Q, dtype=float)
        self.R = np.asarray(R, dtype=float)
        self.terminal_cost = terminal_cost if terminal_cost is not None else self.Q

    def backward_riccati(self, horizon: int) -> Tuple[np.ndarray, np.ndarray]:
        n = self.A.shape[0]
        P = np.zeros((horizon + 1, n, n))
        K = np.zeros((horizon, self.B.shape[1], n))
        P[horizon] = self.terminal_cost
        for t in range(horizon - 1, -1, -1):
            S = self.R + self.B.T @ P[t + 1] @ self.B
            K[t] = np.linalg.solve(S, self.B.T @ P[t + 1] @ self.A)
            P[t] = self.Q + self.A.T @ P[t + 1] @ (self.A - self.B @ K[t])
        return P, K

    def simulate(self, x0: np.ndarray, horizon: int) -> Tuple[np.ndarray, np.ndarray]:
        P, K = self.backward_riccati(horizon)
        x = np.zeros((horizon + 1, len(x0)))
        u = np.zeros((horizon, K.shape[1]))
        x[0] = x0
        for t in range(horizon):
            u[t] = -K[t] @ x[t]
            x[t + 1] = self.A @ x[t] + self.B @ u[t]
        cost = np.sum(np.einsum("ti,ij,tj->t", x[:-1], self.Q, x[:-1])) + np.sum(
            np.einsum("ti,ij,tj->t", u, self.R, u)
        )
        cost += x[-1].T @ P[-1] @ x[-1]
        return x, u


__all__ = ["AlmgrenChrissOptimalExecution", "LinearQuadraticRegulator"]

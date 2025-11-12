"""Optimization helpers for stress testing and Bayesian search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple, List

import numpy as np

try:  # Optional dependency for quadratic programming
    import cvxpy as cp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cp = None  # type: ignore

@dataclass(slots=True)
class ScenarioOptimizer:
    objective: Callable[[np.ndarray], float]
    bounds: Sequence[Tuple[float, float]]
    scenarios: Optional[Iterable[np.ndarray]] = None
    random_seed: Optional[int] = None

    def run(self, n_iter: int = 1000) -> Dict[str, np.ndarray | float]:
        rng = np.random.default_rng(self.random_seed)
        best_params = None
        best_value = np.inf
        if self.scenarios is not None:
            for candidate in self.scenarios:
                value = self.objective(candidate)
                if value < best_value:
                    best_value = value
                    best_params = candidate
        for _ in range(n_iter):
            candidate = np.array([rng.uniform(low, high) for low, high in self.bounds])
            value = self.objective(candidate)
            if value < best_value:
                best_value = value
                best_params = candidate
        if best_params is None:
            raise RuntimeError("No candidate evaluated during optimization.")
        return {"params": best_params, "score": float(best_value)}


class BayesianOptimizer:
    def __init__(
        self,
        objective: Callable[[np.ndarray], float],
        bounds: Sequence[Tuple[float, float]],
        *,
        random_seed: Optional[int] = None,
    ) -> None:
        self.objective = objective
        self.bounds = bounds
        self.random_seed = random_seed
        try:
            from skopt import Optimizer as SkOptimizer  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("scikit-optimize is required for BayesianOptimizer") from exc
        self._optimizer = SkOptimizer(dimensions=list(bounds), random_state=random_seed)

    def suggest(self, n_points: int = 1) -> np.ndarray:
        return np.array(self._optimizer.ask(n_points=n_points))

    def observe(self, params: np.ndarray, values: np.ndarray) -> None:
        if params.ndim == 1:
            params = params.reshape(1, -1)
        self._optimizer.tell(list(params), list(values))

    def run(self, n_iter: int = 30, init_points: int = 5) -> Dict[str, np.ndarray | float]:
        rng = np.random.default_rng(self.random_seed)
        observations: List[Tuple[np.ndarray, float]] = []
        for _ in range(init_points):
            random_point = np.array([rng.uniform(low, high) for low, high in self.bounds])
            value = self.objective(random_point)
            observations.append((random_point, value))
        self.observe(np.array([p for p, _ in observations]), np.array([v for _, v in observations]))
        for _ in range(n_iter):
            params = self.suggest()[0]
            value = self.objective(params)
            self.observe(np.array([params]), np.array([value]))
            observations.append((params, value))
        best_params, best_value = min(observations, key=lambda item: item[1])
        return {"params": best_params, "score": float(best_value)}


@dataclass(slots=True)
class QuadraticProgram:
    """Container for quadratic optimization problems."""

    P: np.ndarray
    q: np.ndarray
    G: Optional[np.ndarray] = None
    h: Optional[np.ndarray] = None
    A: Optional[np.ndarray] = None
    b: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        self.P = np.asarray(self.P, dtype=float)
        self.q = np.asarray(self.q, dtype=float)
        if self.G is not None:
            self.G = np.asarray(self.G, dtype=float)
        if self.h is not None:
            self.h = np.asarray(self.h, dtype=float)
        if self.A is not None:
            self.A = np.asarray(self.A, dtype=float)
        if self.b is not None:
            self.b = np.asarray(self.b, dtype=float)


@dataclass(slots=True)
class QuadraticProgramResult:
    x: np.ndarray
    objective_value: float
    status: str


def solve_qp(problem: QuadraticProgram) -> QuadraticProgramResult:
    """Solve a quadratic program using cvxpy if available, otherwise fallback."""

    if cp is not None:
        x = cp.Variable(len(problem.q))
        objective = 0.5 * cp.quad_form(x, problem.P) + problem.q @ x
        constraints = []
        if problem.G is not None and problem.h is not None:
            constraints.append(problem.G @ x <= problem.h)
        if problem.A is not None and problem.b is not None:
            constraints.append(problem.A @ x == problem.b)
        prob = cp.Problem(cp.Minimize(objective), constraints)
        value = prob.solve(solver=cp.OSQP, verbose=False)
        return QuadraticProgramResult(
            x=np.array(x.value).reshape(-1),
            objective_value=float(value),
            status=prob.status,
        )

    # Fallback: use numpy.linalg with KKT conditions (inequalities ignored).
    P = problem.P
    q = problem.q
    A = problem.A
    b = problem.b
    if A is None or b is None:
        # Unconstrained minimizer
        x = -np.linalg.solve(P, q)
        value = 0.5 * x.T @ P @ x + q.T @ x
        return QuadraticProgramResult(x=x, objective_value=float(value), status="fallback_unconstrained")

    KKT_top = np.hstack([P, A.T])
    KKT_bottom = np.hstack([A, np.zeros((A.shape[0], A.shape[0]))])
    KKT = np.vstack([KKT_top, KKT_bottom])
    rhs = -np.concatenate([q, b])
    solution = np.linalg.solve(KKT, rhs)
    x = solution[: P.shape[0]]
    value = 0.5 * x.T @ P @ x + q.T @ x
    return QuadraticProgramResult(x=x, objective_value=float(value), status="fallback_kkt")


@dataclass(slots=True)
class MeanVarianceResult:
    weights: np.ndarray
    expected_return: float
    volatility: float
    risk_aversion: float


class MeanVarianceOptimizer:
    """Mean-variance optimizer supporting target-return and bound constraints."""

    def __init__(self, covariance: np.ndarray, expected_returns: np.ndarray) -> None:
        self.covariance = np.asarray(covariance, dtype=float)
        self.expected_returns = np.asarray(expected_returns, dtype=float)
        if self.covariance.shape[0] != self.covariance.shape[1]:
            raise ValueError("Covariance matrix must be square.")
        if self.covariance.shape[0] != self.expected_returns.shape[0]:
            raise ValueError("Incompatible dimensions between covariance and expected returns.")

    def solve(
        self,
        *,
        risk_aversion: float = 1.0,
        target_return: Optional[float] = None,
        bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> MeanVarianceResult:
        n = len(self.expected_returns)
        lower, upper = bounds if bounds is not None else (np.full(n, -np.inf), np.full(n, np.inf))

        if cp is not None:
            w = cp.Variable(n)
            objective = cp.Minimize(risk_aversion * cp.quad_form(w, self.covariance) - self.expected_returns @ w)
            constraints = [cp.sum(w) == 1, w >= lower, w <= upper]
            if target_return is not None:
                constraints.append(self.expected_returns @ w >= target_return)
            prob = cp.Problem(objective, constraints)
            value = prob.solve(solver=cp.OSQP, verbose=False)
            weights = np.array(w.value).reshape(-1)
        else:
            ones = np.ones(n)
            inv_cov = np.linalg.pinv(self.covariance)
            if target_return is None:
                weights = inv_cov @ self.expected_returns
                weights /= ones @ weights
            else:
                mu = self.expected_returns
                A = ones @ inv_cov @ ones
                B = ones @ inv_cov @ mu
                C = mu @ inv_cov @ mu
                denom = A * C - B**2
                if abs(denom) < 1e-12:
                    raise RuntimeError("Degenerate covariance matrix for target-return solution.")
                lambda_ = (C - B * target_return) / denom
                gamma = (A * target_return - B) / denom
                weights = inv_cov @ (lambda_ * ones + gamma * mu)
            weights = np.clip(weights, lower, upper)
            weights /= weights.sum()
            value = float(risk_aversion * weights.T @ self.covariance @ weights - self.expected_returns @ weights)

        expected_return = float(weights @ self.expected_returns)
        volatility = float(np.sqrt(weights @ self.covariance @ weights))
        return MeanVarianceResult(weights=weights, expected_return=expected_return, volatility=volatility, risk_aversion=risk_aversion)


__all__ = [
    "ScenarioOptimizer",
    "BayesianOptimizer",
    "QuadraticProgram",
    "QuadraticProgramResult",
    "solve_qp",
    "MeanVarianceOptimizer",
    "MeanVarianceResult",
]

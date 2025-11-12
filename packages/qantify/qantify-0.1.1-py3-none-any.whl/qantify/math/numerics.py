"""General numerical utilities (root finding, integration, differentiation)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np


class ConvergenceError(RuntimeError):
    """Raised when an iterative numerical method fails to converge."""


def newton_raphson(
    func: Callable[[float], float],
    derivative: Callable[[float], float],
    initial_guess: float,
    *,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> float:
    """Solve ``f(x) = 0`` using Newton-Raphson."""

    x = initial_guess
    for _ in range(max_iter):
        fx = func(x)
        dfx = derivative(x)
        if abs(dfx) < 1e-12:
            raise ConvergenceError("Derivative near zero in Newton-Raphson.")
        step = fx / dfx
        x -= step
        if abs(step) < tol:
            return float(x)
    raise ConvergenceError("Newton-Raphson failed to converge.")


def bisection(
    func: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    tol: float = 1e-8,
    max_iter: int = 200,
) -> float:
    """Find root using the bisection method."""

    fl = func(lower)
    fu = func(upper)
    if fl * fu > 0:
        raise ValueError("Function must have opposite signs at interval endpoints.")

    for _ in range(max_iter):
        mid = 0.5 * (lower + upper)
        fm = func(mid)
        if abs(fm) < tol or (upper - lower) < tol:
            return float(mid)
        if fl * fm < 0:
            upper = mid
            fu = fm
        else:
            lower = mid
            fl = fm
    raise ConvergenceError("Bisection failed to converge.")


def simpson_integral(y: Iterable[float], *, dx: float) -> float:
    """Approximate integral using Simpson's rule."""

    values = np.asarray(list(y), dtype=float)
    if len(values) < 3 or len(values) % 2 == 0:
        raise ValueError("Simpson integration requires an odd number of points >= 3.")
    integral = values[0] + values[-1] + 4 * values[1:-1:2].sum() + 2 * values[2:-2:2].sum()
    return float(integral * dx / 3.0)


def trapezoidal_integral(y: Iterable[float], *, dx: float) -> float:
    values = np.asarray(list(y), dtype=float)
    return float((values[0] + values[-1] + 2 * values[1:-1].sum()) * dx / 2.0)


def finite_difference_gradient(series: np.ndarray, *, spacing: float = 1.0) -> np.ndarray:
    """Compute gradient using central differences."""

    series = np.asarray(series, dtype=float)
    gradient = np.zeros_like(series)
    gradient[1:-1] = (series[2:] - series[:-2]) / (2 * spacing)
    gradient[0] = (series[1] - series[0]) / spacing
    gradient[-1] = (series[-1] - series[-2]) / spacing
    return gradient


__all__ = [
    "ConvergenceError",
    "newton_raphson",
    "bisection",
    "simpson_integral",
    "trapezoidal_integral",
    "finite_difference_gradient",
]


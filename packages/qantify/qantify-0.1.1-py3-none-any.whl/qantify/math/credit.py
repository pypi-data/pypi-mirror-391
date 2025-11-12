"""Credit risk analytics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np


@dataclass(slots=True)
class HazardRateCurve:
    tenors: np.ndarray
    hazard_rates: np.ndarray

    def __post_init__(self) -> None:
        self.tenors = np.asarray(self.tenors, dtype=float)
        self.hazard_rates = np.asarray(self.hazard_rates, dtype=float)
        if np.any(np.diff(self.tenors) <= 0):
            raise ValueError("Tenors must be strictly increasing.")
        if self.tenors.shape != self.hazard_rates.shape:
            raise ValueError("Tenors and hazard rates must have the same shape.")

    def intensity(self, t: float) -> float:
        idx = np.searchsorted(self.tenors, t)
        idx = np.clip(idx, 0, len(self.hazard_rates) - 1)
        return float(self.hazard_rates[idx])

    def to_survival(self) -> "SurvivalCurve":
        survival = np.exp(-np.cumsum(self.hazard_rates * np.diff(np.concatenate([[0], self.tenors]))))
        return SurvivalCurve(self.tenors, survival)


@dataclass(slots=True)
class SurvivalCurve:
    tenors: np.ndarray
    survival_probabilities: np.ndarray

    def __post_init__(self) -> None:
        self.tenors = np.asarray(self.tenors, dtype=float)
        self.survival_probabilities = np.asarray(self.survival_probabilities, dtype=float)
        if np.any(np.diff(self.tenors) <= 0):
            raise ValueError("Tenors must be strictly increasing.")
        if self.tenors.shape != self.survival_probabilities.shape:
            raise ValueError("Tenors and survival probabilities must have same shape.")

    def probability(self, t: float) -> float:
        idx = np.searchsorted(self.tenors, t)
        idx = np.clip(idx, 0, len(self.survival_probabilities) - 1)
        return float(self.survival_probabilities[idx])

    def default_probability(self, t0: float, t1: float) -> float:
        return float(self.probability(t0) - self.probability(t1))

    def hazard_rate(self, t: float) -> float:
        idx = np.searchsorted(self.tenors, t)
        idx = np.clip(idx, 1, len(self.tenors) - 1)
        delta_t = self.tenors[idx] - self.tenors[idx - 1]
        s0 = self.survival_probabilities[idx - 1]
        s1 = self.survival_probabilities[idx]
        if s1 <= 0 or delta_t <= 0:
            return float("inf")
        return float(-np.log(s1 / s0) / delta_t)


__all__ = ["HazardRateCurve", "SurvivalCurve"]

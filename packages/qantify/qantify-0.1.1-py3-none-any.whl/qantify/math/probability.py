"""Probability and risk measure utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(slots=True)
class DistributionToolkit:
    sample: np.ndarray

    def __post_init__(self) -> None:
        self.sample = np.asarray(self.sample, dtype=float)

    def moments(self, order: int = 4) -> Dict[str, float]:
        mu = self.sample.mean()
        centered = self.sample - mu
        variance = centered.var(ddof=1)
        skew = (centered**3).mean() / np.power(variance, 1.5)
        kurtosis = (centered**4).mean() / (variance**2)
        return {
            "mean": float(mu),
            "variance": float(variance),
            "skew": float(skew),
            "kurtosis": float(kurtosis),
        }

    def fit_distribution(self, name: str) -> Dict[str, float]:
        try:
            from scipy import stats  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("scipy is required for distribution fitting") from exc

        dist = getattr(stats, name)
        params = dist.fit(self.sample)
        return {"params": params, "loglik": float(dist.logpdf(self.sample, *params).sum())}


class RiskMeasures:
    @staticmethod
    def value_at_risk(data: Iterable[float], level: float = 0.95) -> float:
        arr = np.sort(np.asarray(list(data), dtype=float))
        index = int((1 - level) * len(arr))
        return float(arr[index])

    @staticmethod
    def conditional_value_at_risk(data: Iterable[float], level: float = 0.95) -> float:
        arr = np.sort(np.asarray(list(data), dtype=float))
        index = int((1 - level) * len(arr))
        tail = arr[: index + 1]
        return float(tail.mean()) if len(tail) > 0 else float(arr[index])

    @staticmethod
    def partial_moment(data: Iterable[float], threshold: float, order: int = 2) -> float:
        arr = np.asarray(list(data), dtype=float)
        diff = np.clip(threshold - arr, a_min=0.0, a_max=None)
        return float(np.mean(diff**order))

    @staticmethod
    def entropy(data: Iterable[float], bins: int = 50) -> float:
        hist, _ = np.histogram(list(data), bins=bins, density=True)
        hist = hist[hist > 0]
        return float(-(hist * np.log(hist)).sum())


__all__ = ["DistributionToolkit", "RiskMeasures"]

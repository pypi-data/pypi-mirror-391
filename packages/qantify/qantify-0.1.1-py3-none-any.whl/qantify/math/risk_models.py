"""Risk modeling utilities for covariance estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


class LedoitWolfShrinkage:
    @staticmethod
    def estimate(returns: pd.DataFrame) -> pd.DataFrame:
        x = returns.values
        t, n = x.shape
        sample_cov = np.cov(x, rowvar=False, ddof=1)
        mean_variance = np.trace(sample_cov) / n
        identity = np.identity(n)
        diff = sample_cov - mean_variance * identity
        beta = np.sum(diff**2)
        centered = x - x.mean(axis=0, keepdims=True)
        phi_matrix = centered[:, :, None] * centered[:, None, :]
        phi = np.sum((phi_matrix - sample_cov) ** 2) / t
        shrinkage = min(phi / beta, 1.0) if beta != 0 else 0.0
        shrunk_cov = shrinkage * mean_variance * identity + (1 - shrinkage) * sample_cov
        return pd.DataFrame(shrunk_cov, index=returns.columns, columns=returns.columns)


@dataclass(slots=True)
class FactorRiskModel:
    factor_returns: pd.DataFrame
    factor_loadings: pd.DataFrame
    specific_risk: pd.Series

    def covariance(self) -> pd.DataFrame:
        factor_cov = np.cov(self.factor_returns.values, rowvar=False, ddof=1)
        loadings = self.factor_loadings.values
        factor_component = loadings @ factor_cov @ loadings.T
        specific_component = np.diag(self.specific_risk.values**2)
        cov = factor_component + specific_component
        return pd.DataFrame(cov, index=self.factor_loadings.index, columns=self.factor_loadings.index)

    def marginal_contribution(self, weights: pd.Series) -> pd.Series:
        cov = self.covariance()
        portfolio_variance = weights.T @ cov @ weights
        marginal = cov @ weights
        contribution = weights * marginal / np.sqrt(portfolio_variance)
        return pd.Series(contribution, index=weights.index)


__all__ = ["LedoitWolfShrinkage", "FactorRiskModel"]

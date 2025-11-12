"""Portfolio optimization utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence

import numpy as np
import pandas as pd


@dataclass(slots=True)
class EfficientFrontier:
    returns: pd.Series
    cov: pd.DataFrame

    def __post_init__(self) -> None:
        self.returns = self.returns.astype(float)
        self.cov = self.cov.astype(float)
        if not np.allclose(self.cov, self.cov.T):
            raise ValueError("Covariance matrix must be symmetric.")

    def minimum_variance(self) -> pd.Series:
        inv_cov = np.linalg.pinv(self.cov.values)
        ones = np.ones(len(inv_cov))
        weights = inv_cov @ ones
        weights /= ones @ inv_cov @ ones
        return pd.Series(weights, index=self.returns.index)

    def max_sharpe(self, risk_free: float = 0.0) -> pd.Series:
        excess_returns = self.returns - risk_free
        inv_cov = np.linalg.pinv(self.cov.values)
        weights = inv_cov @ excess_returns.values
        weights /= np.sum(weights)
        return pd.Series(weights, index=self.returns.index)

    def efficient_weights(self, target_return: float) -> pd.Series:
        mu = self.returns.values
        cov = self.cov.values
        inv_cov = np.linalg.pinv(cov)
        ones = np.ones(len(mu))
        A = ones @ inv_cov @ ones
        B = ones @ inv_cov @ mu
        C = mu @ inv_cov @ mu
        lambda_ = (C - B * target_return) / (A * C - B**2)
        gamma = (A * target_return - B) / (A * C - B**2)
        weights = inv_cov @ (lambda_ * ones + gamma * mu)
        return pd.Series(weights, index=self.returns.index)


class RiskParityOptimizer:
    def __init__(self, covariance: pd.DataFrame, max_iter: int = 500, tol: float = 1e-8) -> None:
        self.covariance = covariance.astype(float)
        self.max_iter = max_iter
        self.tol = tol

    def solve(self, initial: Optional[np.ndarray] = None) -> pd.Series:
        n = len(self.covariance)
        w = np.ones(n) / n if initial is None else initial
        cov = self.covariance.values
        for _ in range(self.max_iter):
            portfolio_variance = w.T @ cov @ w
            marginal = cov @ w
            risk_contribution = w * marginal
            target = portfolio_variance / n
            grad = risk_contribution - target
            step = 0.01
            w -= step * grad
            w = np.clip(w, 1e-8, None)
            w /= w.sum()
            if np.linalg.norm(grad) < self.tol:
                break
        return pd.Series(w, index=self.covariance.index)


@dataclass(slots=True)
class BlackLittermanPosterior:
    mean: pd.Series
    covariance: pd.DataFrame


class BlackLittermanModel:
    """Implements the Black-Litterman posterior for portfolio views.

    Parameters
    ----------
    prior_returns:
        Prior equilibrium returns (e.g. CAPM-implied).
    prior_covariance:
        Covariance matrix of asset returns.
    risk_aversion:
        Investor risk aversion parameter (lambda).
    tau:
        Scalar representing the uncertainty in the prior covariance.
    """

    def __init__(
        self,
        prior_returns: pd.Series,
        prior_covariance: pd.DataFrame,
        *,
        risk_aversion: float = 2.5,
        tau: float = 0.05,
    ) -> None:
        self.prior_returns = prior_returns.astype(float)
        self.prior_covariance = prior_covariance.astype(float)
        self.risk_aversion = risk_aversion
        self.tau = tau

    def implied_equilibrium_returns(self, market_weights: pd.Series) -> pd.Series:
        """Compute implied equilibrium returns from market-cap weights."""

        pi = self.risk_aversion * self.prior_covariance @ market_weights
        return pd.Series(pi, index=self.prior_returns.index)

    def posterior(
        self,
        P: np.ndarray,
        Q: np.ndarray,
        *,
        omega: Optional[np.ndarray] = None,
    ) -> BlackLittermanPosterior:
        """Compute posterior mean/covariance under investor views."""

        tau_sigma = self.tau * self.prior_covariance.values
        if omega is None:
            omega = np.diag(np.diag(P @ tau_sigma @ P.T))

        inv_term = np.linalg.inv(P @ tau_sigma @ P.T + omega)
        mu = self.prior_returns.values
        posterior_mean = mu + tau_sigma @ P.T @ inv_term @ (Q - P @ mu)
        posterior_cov = self.prior_covariance.values + tau_sigma - tau_sigma @ P.T @ inv_term @ P @ tau_sigma

        return BlackLittermanPosterior(
            mean=pd.Series(posterior_mean, index=self.prior_returns.index),
            covariance=pd.DataFrame(posterior_cov, index=self.prior_returns.index, columns=self.prior_returns.index),
        )


def efficient_frontier_path(
    frontier: EfficientFrontier,
    target_returns: Sequence[float],
) -> pd.DataFrame:
    """Generate efficient frontier weights for a series of target returns."""

    weights = []
    for target in target_returns:
        w = frontier.efficient_weights(target)
        weights.append(w)
    matrix = pd.concat(weights, axis=1)
    matrix.columns = [f"target_{i}" for i in range(len(target_returns))]
    return matrix


__all__ = ["EfficientFrontier", "RiskParityOptimizer", "BlackLittermanModel", "BlackLittermanPosterior", "efficient_frontier_path"]

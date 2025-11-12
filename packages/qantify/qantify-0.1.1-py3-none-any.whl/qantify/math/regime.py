"""Regime-switching and Markov-chain utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(slots=True)
class MarkovChain:
    transition_matrix: np.ndarray

    def __post_init__(self) -> None:
        self.transition_matrix = np.asarray(self.transition_matrix, dtype=float)
        if self.transition_matrix.ndim != 2 or self.transition_matrix.shape[0] != self.transition_matrix.shape[1]:
            raise ValueError("Transition matrix must be square.")
        if not np.allclose(self.transition_matrix.sum(axis=1), 1.0):
            raise ValueError("Rows of transition matrix must sum to 1.")

    @property
    def n_states(self) -> int:
        return self.transition_matrix.shape[0]

    def stationary_distribution(self) -> np.ndarray:
        eigvals, eigvecs = np.linalg.eig(self.transition_matrix.T)
        idx = np.argmin(np.abs(eigvals - 1))
        stationary = np.real(eigvecs[:, idx])
        stationary /= stationary.sum()
        stationary = np.clip(stationary, 0.0, None)
        stationary /= stationary.sum()
        return stationary

    def simulate(self, n_steps: int, *, initial_distribution: Optional[np.ndarray] = None, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        rng = rng or np.random.default_rng()
        dist = initial_distribution if initial_distribution is not None else self.stationary_distribution()
        state = rng.choice(self.n_states, p=dist)
        path = np.zeros(n_steps, dtype=int)
        for t in range(n_steps):
            path[t] = state
            state = rng.choice(self.n_states, p=self.transition_matrix[state])
        return path


@dataclass(slots=True)
class RegimeSwitchingModel:
    chain: MarkovChain
    state_means: np.ndarray
    state_vols: np.ndarray

    def __post_init__(self) -> None:
        self.state_means = np.asarray(self.state_means, dtype=float)
        self.state_vols = np.asarray(self.state_vols, dtype=float)
        if self.state_means.shape[0] != self.chain.n_states or self.state_vols.shape[0] != self.chain.n_states:
            raise ValueError("Parameter arrays must match number of states.")

    def simulate_returns(
        self,
        n_steps: int,
        *,
        initial_distribution: Optional[np.ndarray] = None,
        rng: Optional[np.random.Generator] = None,
    ) -> pd.DataFrame:
        rng = rng or np.random.default_rng()
        states = self.chain.simulate(n_steps, initial_distribution=initial_distribution, rng=rng)
        returns = rng.normal(loc=self.state_means[states], scale=self.state_vols[states])
        frame = pd.DataFrame({"state": states, "returns": returns})
        return frame

    def smoothed_probabilities(
        self,
        observations: Iterable[float],
        *,
        initial_distribution: Optional[np.ndarray] = None,
    ) -> pd.DataFrame:
        obs = np.asarray(list(observations), dtype=float)
        n_states = self.chain.n_states
        n_obs = obs.shape[0]
        transition = self.chain.transition_matrix
        means = self.state_means
        variances = self.state_vols**2

        filtered = np.zeros((n_obs, n_states))
        predicted = np.zeros((n_obs, n_states))
        likelihood = np.zeros((n_obs, n_states))

        if initial_distribution is None:
            initial_distribution = self.chain.stationary_distribution()
        filtered[0] = initial_distribution

        for t in range(n_obs):
            if t > 0:
                predicted[t] = filtered[t - 1] @ transition
            else:
                predicted[t] = filtered[0]
            for state in range(n_states):
                variance = variances[state]
                mean = means[state]
                likelihood[t, state] = (1 / np.sqrt(2 * np.pi * variance)) * np.exp(
                    -(obs[t] - mean) ** 2 / (2 * variance)
                )
            numerator = predicted[t] * likelihood[t]
            denominator = numerator.sum()
            filtered[t] = numerator / (denominator if denominator != 0 else 1)

        smoothed = np.zeros_like(filtered)
        smoothed[-1] = filtered[-1]
        for t in range(n_obs - 2, -1, -1):
            for state in range(n_states):
                smoothed[t, state] = filtered[t, state] * np.sum(
                    transition[state, :] * smoothed[t + 1] / (predicted[t + 1] + 1e-12)
                )
            total = smoothed[t].sum()
            if total != 0:
                smoothed[t] /= total
        index = pd.RangeIndex(n_obs)
        columns = [f"state_{i}" for i in range(n_states)]
        return pd.DataFrame(smoothed, index=index, columns=columns)


__all__ = ["MarkovChain", "RegimeSwitchingModel"]

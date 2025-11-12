"""Filtering and state-space estimation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np


@dataclass(slots=True)
class KalmanFilter:
    transition_matrix: np.ndarray
    observation_matrix: np.ndarray
    transition_covariance: np.ndarray
    observation_covariance: np.ndarray
    initial_state_mean: np.ndarray
    initial_state_covariance: np.ndarray

    def filter(self, observations: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        n_timesteps = observations.shape[0]
        n_dim_state = self.transition_matrix.shape[0]
        filtered_state_means = np.zeros((n_timesteps, n_dim_state))
        filtered_state_covariances = np.zeros((n_timesteps, n_dim_state, n_dim_state))

        state_mean = self.initial_state_mean
        state_covariance = self.initial_state_covariance

        for t in range(n_timesteps):
            # Predict step
            predicted_mean = self.transition_matrix @ state_mean
            predicted_cov = (
                self.transition_matrix @ state_covariance @ self.transition_matrix.T + self.transition_covariance
            )

            # Update step
            observation = observations[t]
            innovation = observation - self.observation_matrix @ predicted_mean
            innovation_cov = (
                self.observation_matrix @ predicted_cov @ self.observation_matrix.T + self.observation_covariance
            )
            kalman_gain = predicted_cov @ self.observation_matrix.T @ np.linalg.inv(innovation_cov)
            state_mean = predicted_mean + kalman_gain @ innovation
            state_covariance = predicted_cov - kalman_gain @ self.observation_matrix @ predicted_cov

            filtered_state_means[t] = state_mean
            filtered_state_covariances[t] = state_covariance

        return filtered_state_means, filtered_state_covariances


class UnscentedKalmanFilter:
    def __init__(
        self,
        transition_function: Callable[[np.ndarray], np.ndarray],
        observation_function: Callable[[np.ndarray], np.ndarray],
        process_covariance: np.ndarray,
        observation_covariance: np.ndarray,
        initial_state_mean: np.ndarray,
        initial_state_covariance: np.ndarray,
        alpha: float = 1e-3,
        beta: float = 2.0,
        kappa: float = 0.0,
    ) -> None:
        self.transition_function = transition_function
        self.observation_function = observation_function
        self.process_covariance = process_covariance
        self.observation_covariance = observation_covariance
        self.state_mean = initial_state_mean
        self.state_covariance = initial_state_covariance
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa

    def _sigma_points(self, mean: np.ndarray, covariance: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        n = mean.shape[0]
        lambda_ = self.alpha**2 * (n + self.kappa) - n
        sigma_points = np.zeros((2 * n + 1, n))
        weights_mean = np.zeros(2 * n + 1)
        weights_cov = np.zeros(2 * n + 1)
        sigma_points[0] = mean
        weights_mean[0] = lambda_ / (n + lambda_)
        weights_cov[0] = lambda_ / (n + lambda_) + (1 - self.alpha**2 + self.beta)
        sqrt_matrix = np.linalg.cholesky((n + lambda_) * covariance)
        for i in range(n):
            sigma_points[i + 1] = mean + sqrt_matrix[i]
            sigma_points[n + i + 1] = mean - sqrt_matrix[i]
            weights_mean[i + 1] = weights_cov[i + 1] = 1 / (2 * (n + lambda_))
            weights_mean[n + i + 1] = weights_cov[n + i + 1] = 1 / (2 * (n + lambda_))
        return sigma_points, weights_mean, weights_cov

    def filter(self, observations: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        n_timesteps = observations.shape[0]
        n_dim_state = self.state_mean.shape[0]
        filtered_means = np.zeros((n_timesteps, n_dim_state))
        filtered_covariances = np.zeros((n_timesteps, n_dim_state, n_dim_state))

        mean = self.state_mean
        covariance = self.state_covariance

        for t in range(n_timesteps):
            sigma_points, wm, wc = self._sigma_points(mean, covariance)
            transformed_sigma = np.array([self.transition_function(p) for p in sigma_points])
            predicted_mean = np.sum(wm[:, None] * transformed_sigma, axis=0)
            diff = transformed_sigma - predicted_mean
            predicted_cov = diff.T @ (wc[:, None] * diff) + self.process_covariance

            sigma_points, wm, wc = self._sigma_points(predicted_mean, predicted_cov)
            obs_sigma = np.array([self.observation_function(p) for p in sigma_points])
            obs_mean = np.sum(wm[:, None] * obs_sigma, axis=0)
            obs_diff = obs_sigma - obs_mean
            obs_cov = obs_diff.T @ (wc[:, None] * obs_diff) + self.observation_covariance
            cross_cov = diff.T @ (wc[:, None] * obs_diff)
            kalman_gain = cross_cov @ np.linalg.inv(obs_cov)

            observation = observations[t]
            mean = predicted_mean + kalman_gain @ (observation - obs_mean)
            covariance = predicted_cov - kalman_gain @ obs_cov @ kalman_gain.T

            filtered_means[t] = mean
            filtered_covariances[t] = covariance

        return filtered_means, filtered_covariances


__all__ = ["KalmanFilter", "UnscentedKalmanFilter"]

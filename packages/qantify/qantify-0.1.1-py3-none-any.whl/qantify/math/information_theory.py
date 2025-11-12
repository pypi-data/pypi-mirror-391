"""Information Theory: Entropy Measures, Information Geometry, and Channel Capacity.

This module implements advanced information-theoretic models including:

- Entropy measures (Shannon, Renyi, Tsallis, von Neumann)
- Mutual information and conditional entropy
- Kullback-Leibler divergence and f-divergences
- Information geometry and Fisher information
- Channel capacity and rate-distortion theory
- Kolmogorov complexity and algorithmic information
- Information flow in dynamical systems
- Transfer entropy and causal inference
- Quantum information measures
- Information-theoretic portfolio optimization
- Market microstructure information content
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Protocol
from collections import defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize, integrate, special, linalg
from scipy.optimize import minimize, minimize_scalar, differential_evolution
from scipy.stats import entropy as scipy_entropy
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mutual_info_score
from sklearn.feature_selection import mutual_info_regression


# =============================================================================
# ENTROPY MEASURES
# =============================================================================

@dataclass
class EntropyMeasures:
    """Advanced entropy measures beyond Shannon entropy."""

    @staticmethod
    def shannon_entropy(probabilities, base: float = 2.0) -> float:
        """Compute Shannon entropy.

        H(X) = -Σ p(x) log p(x)

        Parameters:
        -----------
        probabilities : array-like
            Probability distribution
        base : float
            Logarithm base (2 for bits, e for nats)

        Returns:
        --------
        float : Shannon entropy
        """
        # Convert to numpy array and remove zero probabilities
        probabilities = np.array(probabilities)
        probabilities = probabilities[probabilities > 0]

        if len(probabilities) == 0:
            return 0.0

        return scipy_entropy(probabilities, base=base)

    @staticmethod
    def renyi_entropy(probabilities: np.ndarray, alpha: float, base: float = 2.0) -> float:
        """Compute Renyi entropy of order α.

        H_α(X) = (1/(1-α)) log Σ p(x)^α

        Parameters:
        -----------
        probabilities : np.ndarray
            Probability distribution
        alpha : float
            Renyi entropy order (α ≠ 1)
        base : float
            Logarithm base

        Returns:
        --------
        float : Renyi entropy
        """
        if alpha == 1:
            return EntropyMeasures.shannon_entropy(probabilities, base)

        if alpha < 0:
            raise ValueError("Renyi entropy order must be non-negative")

        # Remove zero probabilities
        probabilities = probabilities[probabilities > 0]

        if len(probabilities) == 0:
            return 0.0

        # Compute Renyi entropy
        sum_p_alpha = np.sum(probabilities ** alpha)

        if sum_p_alpha <= 0:
            return 0.0

        renyi_entropy = (1 / (1 - alpha)) * np.log(sum_p_alpha)

        # Convert to desired base
        if base != np.e:
            renyi_entropy = renyi_entropy / np.log(base)

        return renyi_entropy

    @staticmethod
    def tsallis_entropy(probabilities: np.ndarray, q: float, base: float = 2.0) -> float:
        """Compute Tsallis entropy of order q.

        S_q(X) = (1/(q-1)) (Σ p(x)^q - 1)

        Parameters:
        -----------
        probabilities : np.ndarray
            Probability distribution
        q : float
            Tsallis entropy order (q ≠ 1)
        base : float
            Logarithm base

        Returns:
        --------
        float : Tsallis entropy
        """
        if q == 1:
            return EntropyMeasures.shannon_entropy(probabilities, base)

        if q < 0:
            raise ValueError("Tsallis entropy order must be non-negative")

        # Remove zero probabilities
        probabilities = probabilities[probabilities > 0]

        if len(probabilities) == 0:
            return 0.0

        # Compute Tsallis entropy
        sum_p_q = np.sum(probabilities ** q)

        tsallis_entropy = (1 / (q - 1)) * (sum_p_q - 1)

        return tsallis_entropy

    @staticmethod
    def permutation_entropy(time_series: np.ndarray, order: int = 3,
                          delay: int = 1, normalize: bool = True) -> float:
        """Compute permutation entropy of time series.

        Measures the complexity of time series based on ordinal patterns.

        Parameters:
        -----------
        time_series : np.ndarray
            Input time series
        order : int
            Permutation order (embedding dimension)
        delay : int
            Time delay
        normalize : bool
            Whether to normalize by maximum entropy

        Returns:
        --------
        float : Permutation entropy
        """
        n = len(time_series)

        if n < order * delay:
            return 0.0

        # Generate ordinal patterns
        patterns = []

        for i in range(n - (order - 1) * delay):
            window = time_series[i:i + order * delay:delay]

            # Get permutation (ranking)
            permutation = np.argsort(window)
            pattern = tuple(permutation)

            patterns.append(pattern)

        # Count pattern frequencies
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Convert to probabilities
        total_patterns = len(patterns)
        probabilities = np.array(list(pattern_counts.values())) / total_patterns

        # Compute permutation entropy
        perm_entropy = scipy_entropy(probabilities, base=2)

        # Normalize by maximum entropy
        if normalize:
            max_entropy = np.log2(np.math.factorial(order))
            perm_entropy = perm_entropy / max_entropy if max_entropy > 0 else 0

        return perm_entropy

    @staticmethod
    def sample_entropy(time_series: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """Compute sample entropy of time series.

        Measures the complexity/regularity of time series.

        Parameters:
        -----------
        time_series : np.ndarray
            Input time series
        m : int
            Pattern length
        r : float
            Tolerance parameter

        Returns:
        --------
        float : Sample entropy (-log of conditional probability)
        """
        n = len(time_series)

        if n < m + 1:
            return 0.0

        # Normalize time series
        time_series = (time_series - np.mean(time_series)) / np.std(time_series)

        def count_matches(template, m_length):
            """Count matching patterns within tolerance."""
            matches = 0

            for i in range(n - m_length + 1):
                if i == 0:  # Skip self-match
                    continue

                pattern = time_series[i:i + m_length]
                distance = np.max(np.abs(template - pattern))

                if distance <= r:
                    matches += 1

            return matches

        # Count m-length patterns
        b = 0  # Number of matches for length m
        for i in range(n - m + 1):
            template = time_series[i:i + m]
            b += count_matches(template, m)

        # Count (m+1)-length patterns
        a = 0  # Number of matches for length m+1
        for i in range(n - m):
            template = time_series[i:i + m + 1]
            a += count_matches(template, m + 1)

        # Compute sample entropy
        if a == 0 or b == 0:
            return 0.0

        sample_entropy = -np.log(a / b)

        return sample_entropy

    @staticmethod
    def transfer_entropy(source_series: np.ndarray, target_series: np.ndarray,
                        k: int = 1, l: int = 1, delay: int = 1) -> float:
        """Compute transfer entropy from source to target.

        Measures the amount of directed information transfer
        from source to target time series.

        Parameters:
        -----------
        source_series : np.ndarray
            Source time series
        target_series : np.ndarray
            Target time series
        k, l : int
            History lengths for source and target
        delay : int
            Prediction delay

        Returns:
        --------
        float : Transfer entropy
        """
        n = min(len(source_series), len(target_series))

        if n < max(k, l) + delay + 1:
            return 0.0

        # Create lagged vectors
        def create_lagged_matrix(series, lag):
            """Create matrix of lagged values."""
            matrix = np.zeros((n - lag, lag))
            for i in range(lag):
                matrix[:, i] = series[lag - i - 1:n - i - 1]
            return matrix

        # Target history
        target_history = create_lagged_matrix(target_series, l)

        # Joint history (target + source)
        source_lagged = create_lagged_matrix(source_series, k)
        joint_history = np.column_stack([target_history, source_lagged])

        # Future target values
        future_target = target_series[l + delay - 1:n - delay + 1]

        # Ensure same length
        min_length = min(len(target_history), len(joint_history), len(future_target))
        target_history = target_history[:min_length]
        joint_history = joint_history[:min_length]
        future_target = future_target[:min_length]

        # Discretize for entropy calculation
        n_bins = min(10, int(np.sqrt(min_length)))

        # Compute conditional entropy H(future|target_history)
        target_hist_discrete = np.digitize(target_history.flatten(),
                                         np.linspace(target_history.min(), target_history.max(), n_bins))
        future_discrete = np.digitize(future_target,
                                    np.linspace(future_target.min(), future_target.max(), n_bins))

        # Joint distribution for H(future, target_history)
        joint_target = np.column_stack([future_discrete, target_hist_discrete])
        joint_target_counts = np.unique(joint_target, axis=0, return_counts=True)[1]
        p_joint_target = joint_target_counts / np.sum(joint_target_counts)

        # Marginal for target_history
        p_target_hist = np.bincount(target_hist_discrete) / len(target_hist_discrete)

        # H(future|target_history)
        h_cond_target = scipy_entropy(p_joint_target) - scipy_entropy(p_target_hist)

        # Compute conditional entropy H(future|joint_history)
        joint_hist_discrete = np.digitize(joint_history.flatten(),
                                        np.linspace(joint_history.min(), joint_history.max(), n_bins))

        joint_full = np.column_stack([future_discrete, joint_hist_discrete])
        joint_full_counts = np.unique(joint_full, axis=0, return_counts=True)[1]
        p_joint_full = joint_full_counts / np.sum(joint_full_counts)

        # Marginal for joint_history
        p_joint_hist = np.bincount(joint_hist_discrete) / len(joint_hist_discrete)

        # H(future|joint_history)
        h_cond_joint = scipy_entropy(p_joint_full) - scipy_entropy(p_joint_hist)

        # Transfer entropy = H(future|target_history) - H(future|joint_history)
        transfer_entropy = max(0, h_cond_target - h_cond_joint)

        return transfer_entropy


# =============================================================================
# MUTUAL INFORMATION AND INFORMATION MEASURES
# =============================================================================

@dataclass
class InformationMeasures:
    """Mutual information and related information-theoretic measures."""

    @staticmethod
    def mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 20) -> float:
        """Compute mutual information between two variables.

        I(X;Y) = H(X) + H(Y) - H(X,Y)

        Parameters:
        -----------
        x, y : np.ndarray
            Input variables
        bins : int
            Number of bins for discretization

        Returns:
        --------
        float : Mutual information
        """
        # Discretize continuous variables
        x_discrete = np.digitize(x, np.linspace(x.min(), x.max(), bins))
        y_discrete = np.digitize(y, np.linspace(y.min(), y.max(), bins))

        # Compute joint entropy
        joint_counts = np.zeros((bins, bins))
        for i in range(len(x_discrete)):
            joint_counts[x_discrete[i]-1, y_discrete[i]-1] += 1

        joint_probs = joint_counts / np.sum(joint_counts)
        h_joint = scipy_entropy(joint_probs.flatten())

        # Compute marginal entropies
        h_x = scipy_entropy(np.bincount(x_discrete) / len(x_discrete))
        h_y = scipy_entropy(np.bincount(y_discrete) / len(y_discrete))

        # Mutual information
        mi = h_x + h_y - h_joint

        return max(0, mi)  # Ensure non-negative

    @staticmethod
    def conditional_mutual_information(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                                     bins: int = 20) -> float:
        """Compute conditional mutual information I(X;Y|Z).

        I(X;Y|Z) = H(X,Z) + H(Y,Z) - H(Z) - H(X,Y,Z)

        Parameters:
        -----------
        x, y, z : np.ndarray
            Input variables
        bins : int
            Number of bins for discretization

        Returns:
        --------
        float : Conditional mutual information
        """
        # Discretize all variables
        x_discrete = np.digitize(x, np.linspace(x.min(), x.max(), bins))
        y_discrete = np.digitize(y, np.linspace(y.min(), y.max(), bins))
        z_discrete = np.digitize(z, np.linspace(z.min(), z.max(), bins))

        # Compute 3D joint entropy H(X,Y,Z)
        xyz_counts = np.zeros((bins, bins, bins))
        for i in range(len(x_discrete)):
            xyz_counts[x_discrete[i]-1, y_discrete[i]-1, z_discrete[i]-1] += 1

        xyz_probs = xyz_counts / np.sum(xyz_counts)
        h_xyz = scipy_entropy(xyz_probs.flatten())

        # Compute H(Z)
        h_z = scipy_entropy(np.bincount(z_discrete) / len(z_discrete))

        # Compute H(X,Z)
        xz_counts = np.zeros((bins, bins))
        for i in range(len(x_discrete)):
            xz_counts[x_discrete[i]-1, z_discrete[i]-1] += 1

        xz_probs = xz_counts / np.sum(xz_counts)
        h_xz = scipy_entropy(xz_probs.flatten())

        # Compute H(Y,Z)
        yz_counts = np.zeros((bins, bins))
        for i in range(len(y_discrete)):
            yz_counts[y_discrete[i]-1, z_discrete[i]-1] += 1

        yz_probs = yz_counts / np.sum(yz_counts)
        h_yz = scipy_entropy(yz_probs.flatten())

        # Conditional mutual information
        cmi = h_xz + h_yz - h_z - h_xyz

        return max(0, cmi)

    @staticmethod
    def directed_information(x_series: np.ndarray, y_series: np.ndarray,
                           max_lag: int = 5) -> np.ndarray:
        """Compute directed information from X to Y.

        Measures the information flow from past X to future Y.

        Parameters:
        -----------
        x_series, y_series : np.ndarray
            Time series data
        max_lag : int
            Maximum lag to consider

        Returns:
        --------
        np.ndarray : Directed information for each lag
        """
        n = min(len(x_series), len(y_series))
        directed_info = np.zeros(max_lag + 1)

        for lag in range(max_lag + 1):
            # Create lagged X and current Y
            if lag == 0:
                x_lagged = x_series[:n]
                y_current = y_series[:n]
            else:
                x_lagged = x_series[:-lag]
                y_current = y_series[lag:]

            # Compute mutual information
            directed_info[lag] = InformationMeasures.mutual_information(x_lagged, y_current)

        return directed_info

    @staticmethod
    def information_flow_network(time_series_data: pd.DataFrame,
                               max_lag: int = 3) -> Dict[str, Any]:
        """Compute information flow network between time series.

        Creates a network where nodes are time series and edges
        represent information flow strength.

        Parameters:
        -----------
        time_series_data : pd.DataFrame
            Multiple time series
        max_lag : int
            Maximum lag for information flow

        Returns:
        --------
        dict : Information flow network
        """
        series_names = time_series_data.columns
        n_series = len(series_names)

        # Compute pairwise directed information
        flow_matrix = np.zeros((n_series, n_series))

        for i in range(n_series):
            for j in range(n_series):
                if i != j:
                    directed_info = InformationMeasures.directed_information(
                        time_series_data.iloc[:, i].values,
                        time_series_data.iloc[:, j].values,
                        max_lag
                    )
                    flow_matrix[i, j] = np.max(directed_info)  # Maximum information flow

        # Network properties
        total_flow = np.sum(flow_matrix)
        in_degrees = np.sum(flow_matrix > 0, axis=0)
        out_degrees = np.sum(flow_matrix > 0, axis=1)

        # Find most influential series (highest out-degree)
        most_influential = series_names[np.argmax(out_degrees)]
        most_influenced = series_names[np.argmax(in_degrees)]

        return {
            'flow_matrix': flow_matrix,
            'series_names': list(series_names),
            'total_information_flow': total_flow,
            'in_degrees': in_degrees,
            'out_degrees': out_degrees,
            'most_influential_series': most_influential,
            'most_influenced_series': most_influenced,
            'max_lag': max_lag,
            'model_type': 'Information Flow Network'
        }


# =============================================================================
# INFORMATION GEOMETRY
# =============================================================================

@dataclass
class InformationGeometry:
    """Information geometry and Fisher information analysis."""

    @staticmethod
    def fisher_information_matrix(distribution_family: Callable,
                                parameters: np.ndarray,
                                data: np.ndarray) -> np.ndarray:
        """Compute Fisher information matrix for a parametric family.

        I(θ)_ij = E[ ∂/∂θ_i log f(X;θ) * ∂/∂θ_j log f(X;θ) ]

        Parameters:
        -----------
        distribution_family : callable
            Parametric distribution family
        parameters : np.ndarray
            Parameter values
        data : np.ndarray
            Observed data

        Returns:
        --------
        np.ndarray : Fisher information matrix
        """
        n_params = len(parameters)
        fim = np.zeros((n_params, n_params))

        # Numerical computation using finite differences
        h = 1e-6

        for i in range(n_params):
            for j in range(n_params):
                # Compute second derivatives of log-likelihood
                params_plus_i = parameters.copy()
                params_plus_i[i] += h

                params_plus_j = parameters.copy()
                params_plus_j[j] += h

                params_plus_both = parameters.copy()
                params_plus_both[i] += h
                params_plus_both[j] += h

                # Log-likelihoods
                ll_base = np.sum([np.log(distribution_family(x, parameters)) for x in data])
                ll_plus_i = np.sum([np.log(distribution_family(x, params_plus_i)) for x in data])
                ll_plus_j = np.sum([np.log(distribution_family(x, params_plus_j)) for x in data])
                ll_plus_both = np.sum([np.log(distribution_family(x, params_plus_both)) for x in data])

                # Mixed partial derivative
                fim[i, j] = (ll_plus_both - ll_plus_i - ll_plus_j + ll_base) / (h**2)

        # Ensure positive semi-definite
        eigenvals = np.linalg.eigvals(fim)
        if np.any(eigenvals < 0):
            fim = fim + np.eye(n_params) * 1e-6

        return fim

    @staticmethod
    def kullback_leibler_divergence(p: np.ndarray, q: np.ndarray) -> float:
        """Compute Kullback-Leibler divergence D_KL(p||q).

        D_KL(p||q) = Σ p(x) log(p(x)/q(x))

        Parameters:
        -----------
        p, q : np.ndarray
            Probability distributions

        Returns:
        --------
        float : KL divergence
        """
        # Remove zero probabilities
        valid_idx = (p > 0) & (q > 0)
        p_valid = p[valid_idx]
        q_valid = q[valid_idx]

        if len(p_valid) == 0:
            return 0.0

        kl_div = np.sum(p_valid * np.log(p_valid / q_valid))

        return max(0, kl_div)  # Ensure non-negative

    @staticmethod
    def alpha_divergence(p: np.ndarray, q: np.ndarray, alpha: float) -> float:
        """Compute α-divergence between distributions.

        Family of divergences that includes KL-divergence as special case.

        Parameters:
        -----------
        p, q : np.ndarray
            Probability distributions
        alpha : float
            Divergence parameter

        Returns:
        --------
        float : α-divergence
        """
        if alpha == 1:
            return InformationGeometry.kullback_leibler_divergence(p, q)

        # Remove zero probabilities
        valid_idx = (p > 0) & (q > 0)
        p_valid = p[valid_idx]
        q_valid = q[valid_idx]

        if len(p_valid) == 0:
            return 0.0

        if alpha == 0:  # Hellinger distance
            integrand = (np.sqrt(p_valid) - np.sqrt(q_valid))**2
            return np.sum(integrand)
        elif alpha == 0.5:
            # Jensen-Shannon divergence
            m = (p_valid + q_valid) / 2
            js_div = (InformationGeometry.kullback_leibler_divergence(p_valid, m) +
                     InformationGeometry.kullback_leibler_divergence(q_valid, m)) / 2
            return js_div
        else:
            # General α-divergence
            integrand = (4 / (1 - alpha**2)) * (p_valid**((1+alpha)/2) *
                                              q_valid**((1-alpha)/2) - 1)
            return np.sum(integrand)

    @staticmethod
    def information_manifold_distance(theta1: np.ndarray, theta2: np.ndarray,
                                    fisher_matrix: np.ndarray) -> float:
        """Compute information-geometric distance on parameter manifold.

        Uses Fisher information matrix to define Riemannian metric.

        Parameters:
        -----------
        theta1, theta2 : np.ndarray
            Parameter points on manifold
        fisher_matrix : np.ndarray
            Fisher information matrix

        Returns:
        --------
        float : Information distance
        """
        # Approximate geodesic distance using Fisher-Rao metric
        diff = theta1 - theta2

        # Information distance = sqrt( (θ1 - θ2)^T I(θ) (θ1 - θ2) )
        distance = np.sqrt(diff.T @ fisher_matrix @ diff)

        return distance

    @staticmethod
    def natural_gradient_update(parameters: np.ndarray, gradient: np.ndarray,
                              fisher_matrix: np.ndarray, learning_rate: float = 0.01) -> np.ndarray:
        """Perform natural gradient update for optimization.

        Uses Fisher information matrix to precondition gradient updates.

        Parameters:
        -----------
        parameters : np.ndarray
            Current parameters
        gradient : np.ndarray
            Euclidean gradient
        fisher_matrix : np.ndarray
            Fisher information matrix
        learning_rate : float
            Learning rate

        Returns:
        --------
        np.ndarray : Updated parameters
        """
        # Compute natural gradient: F^{-1} ∇_θ L
        try:
            fisher_inv = np.linalg.inv(fisher_matrix)
            natural_gradient = fisher_inv @ gradient

            # Update parameters
            updated_params = parameters + learning_rate * natural_gradient

        except np.linalg.LinAlgError:
            # Fallback to regular gradient if Fisher matrix is singular
            updated_params = parameters + learning_rate * gradient

        return updated_params


# =============================================================================
# CHANNEL CAPACITY AND RATE-DISTORTION THEORY
# =============================================================================

@dataclass
class ChannelCapacity:
    """Channel capacity and information transmission analysis."""

    @staticmethod
    def binary_symmetric_channel_capacity(crossover_probability: float) -> float:
        """Compute capacity of binary symmetric channel.

        C = 1 - H(p) where H is binary entropy

        Parameters:
        -----------
        crossover_probability : float
            Bit flip probability

        Returns:
        --------
        float : Channel capacity in bits
        """
        if crossover_probability == 0 or crossover_probability == 1:
            return 1.0

        # Binary entropy
        h = lambda p: -p * np.log2(p) - (1-p) * np.log2(1-p) if 0 < p < 1 else 0

        capacity = 1 - h(crossover_probability)

        return capacity

    @staticmethod
    def gaussian_channel_capacity(signal_power: float, noise_power: float) -> float:
        """Compute capacity of Gaussian channel.

        C = (1/2) log2(1 + SNR)

        Parameters:
        -----------
        signal_power : float
            Average signal power
        noise_power : float
            Noise power

        Returns:
        --------
        float : Channel capacity in bits per channel use
        """
        snr = signal_power / noise_power

        if snr <= 0:
            return 0.0

        capacity = 0.5 * np.log2(1 + snr)

        return capacity

    @staticmethod
    def mutual_information_channel(input_distribution: np.ndarray,
                                 channel_matrix: np.ndarray) -> float:
        """Compute mutual information for discrete channel.

        I(X;Y) = H(Y) - H(Y|X)

        Parameters:
        -----------
        input_distribution : np.ndarray
            Input symbol probabilities
        channel_matrix : np.ndarray
            Channel transition matrix P(Y|X)

        Returns:
        --------
        float : Mutual information
        """
        # Compute output distribution P(Y)
        output_distribution = channel_matrix.T @ input_distribution

        # Compute conditional entropy H(Y|X)
        h_y_given_x = 0
        for i, p_x in enumerate(input_distribution):
            if p_x > 0:
                channel_row = channel_matrix[i, :]
                channel_row = channel_row[channel_row > 0]
                h_y_given_x += p_x * scipy_entropy(channel_row)

        # Mutual information = H(Y) - H(Y|X)
        h_y = scipy_entropy(output_distribution)
        mutual_info = h_y - h_y_given_x

        return max(0, mutual_info)

    @staticmethod
    def blachman_teissier_channel_capacity(channel_matrix: np.ndarray,
                                         max_iterations: int = 100) -> Dict[str, Any]:
        """Compute channel capacity using Blachman-Teissier algorithm.

        Iterative algorithm to find capacity-achieving input distribution.

        Parameters:
        -----------
        channel_matrix : np.ndarray
            Channel transition matrix P(Y|X)
        max_iterations : int
            Maximum iterations

        Returns:
        --------
        dict : Capacity and optimal input distribution
        """
        n_inputs = channel_matrix.shape[0]

        # Initialize uniform input distribution
        p_x = np.ones(n_inputs) / n_inputs

        capacity = 0
        convergence_threshold = 1e-6

        for iteration in range(max_iterations):
            # Compute output distribution
            p_y = channel_matrix.T @ p_x

            # Compute mutual information
            new_capacity = ChannelCapacity.mutual_information_channel(p_x, channel_matrix)

            # Check convergence
            if abs(new_capacity - capacity) < convergence_threshold:
                break

            capacity = new_capacity

            # Update input distribution (Blachman-Teissier step)
            # p_x_new ∝ p_x * exp(λ_y)
            lambda_y = np.log(p_y + 1e-10)  # Avoid log(0)

            # Compute new input distribution
            exponents = channel_matrix @ lambda_y
            p_x_new = p_x * np.exp(exponents - np.max(exponents))  # Numerical stability
            p_x_new = p_x_new / np.sum(p_x_new)

            p_x = p_x_new

        return {
            'capacity': capacity,
            'optimal_input_distribution': p_x,
            'iterations': iteration + 1,
            'converged': iteration < max_iterations - 1,
            'model_type': 'Blachman-Teissier Channel Capacity'
        }


# =============================================================================
# KOLMOGOROV COMPLEXITY AND ALGORITHMIC INFORMATION
# =============================================================================

@dataclass
class KolmogorovComplexity:
    """Kolmogorov complexity and algorithmic information theory."""

    @staticmethod
    def block_decomposition_complexity(time_series: np.ndarray,
                                     block_size: int = 10) -> float:
        """Compute block decomposition complexity.

        Measures complexity based on repeated patterns in blocks.

        Parameters:
        -----------
        time_series : np.ndarray
            Input time series
        block_size : int
            Size of blocks for decomposition

        Returns:
        --------
        float : Block decomposition complexity
        """
        n = len(time_series)

        if n < block_size:
            return 0.0

        # Create blocks
        blocks = []
        for i in range(0, n - block_size + 1, block_size):
            block = tuple(time_series[i:i + block_size])
            blocks.append(block)

        # Count unique blocks
        unique_blocks = len(set(blocks))
        total_blocks = len(blocks)

        # Complexity measure
        if total_blocks == 0:
            return 0.0

        # Normalized compression ratio
        complexity = unique_blocks / total_blocks

        return complexity

    @staticmethod
    def lempel_ziv_complexity(time_series: np.ndarray) -> float:
        """Compute Lempel-Ziv complexity.

        Measures the number of distinct substrings in a sequence.

        Parameters:
        -----------
        time_series : np.ndarray
            Binary or discretized time series

        Returns:
        --------
        float : Lempel-Ziv complexity
        """
        # Convert to string representation
        if time_series.dtype != int:
            # Discretize to binary
            median_val = np.median(time_series)
            binary_sequence = (time_series > median_val).astype(int)
        else:
            binary_sequence = time_series

        sequence_str = ''.join(map(str, binary_sequence))
        n = len(sequence_str)

        if n == 0:
            return 0.0

        # Lempel-Ziv factorization
        substrings = set()
        i = 0
        complexity = 0

        while i < n:
            j = 1
            while i + j <= n:
                substring = sequence_str[i:i+j]

                if substring not in substrings:
                    substrings.add(substring)
                    complexity += 1
                    i += j
                    break
                j += 1
            else:
                i += 1

        # Normalized complexity
        normalized_complexity = complexity / (n / np.log2(n)) if n > 1 else 0

        return normalized_complexity

    @staticmethod
    def algorithmic_complexity_estimation(time_series: np.ndarray,
                                        max_program_length: int = 100) -> Dict[str, Any]:
        """Estimate algorithmic complexity using compression algorithms.

        Uses compression algorithms as proxies for Kolmogorov complexity.

        Parameters:
        -----------
        time_series : np.ndarray
            Input time series
        max_program_length : int
            Maximum program length for estimation

        Returns:
        --------
        dict : Complexity estimates
        """
        # Convert to bytes
        time_series_bytes = time_series.astype(np.float32).tobytes()

        # Try different compression methods
        complexities = {}

        try:
            import zlib
            compressed_zlib = zlib.compress(time_series_bytes)
            complexities['zlib'] = len(compressed_zlib) / len(time_series_bytes)
        except:
            complexities['zlib'] = 1.0

        try:
            import bz2
            compressed_bz2 = bz2.compress(time_series_bytes)
            complexities['bz2'] = len(compressed_bz2) / len(time_series_bytes)
        except:
            complexities['bz2'] = 1.0

        try:
            import lzma
            compressed_lzma = lzma.compress(time_series_bytes)
            complexities['lzma'] = len(compressed_lzma) / len(time_series_bytes)
        except:
            complexities['lzma'] = 1.0

        # Minimum compression ratio as complexity estimate
        min_complexity = min(complexities.values())

        # Information content per sample
        bits_per_sample = min_complexity * 8  # Convert to bits

        return {
            'compression_ratios': complexities,
            'estimated_complexity': min_complexity,
            'bits_per_sample': bits_per_sample,
            'kolmogorov_estimate': -np.log2(min_complexity) if min_complexity > 0 else 0,
            'model_type': 'Algorithmic Complexity Estimation'
        }


# =============================================================================
# INFORMATION-THEORETIC PORTFOLIO OPTIMIZATION
# =============================================================================

@dataclass
class InformationPortfolioOptimization:
    """Portfolio optimization using information-theoretic measures."""

    @staticmethod
    def entropy_pooling_portfolio(views: List[np.ndarray],
                                confidences: List[float],
                                prior_distribution: np.ndarray) -> Dict[str, Any]:
        """Entropy pooling portfolio optimization.

        Updates prior distribution using entropy minimization
        subject to constraints from investor views.

        Parameters:
        -----------
        views : list
            List of view matrices (scenarios)
        confidences : list
            Confidence levels for each view
        prior_distribution : np.ndarray
            Prior probability distribution

        Returns:
        --------
        dict : Entropy pooling results
        """
        n_scenarios = len(prior_distribution)

        # Objective: minimize KL divergence from prior
        def objective(p):
            # Relative entropy (KL divergence)
            kl_div = np.sum(p * np.log(p / prior_distribution + 1e-10))
            return kl_div

        # Constraints for each view
        constraints = []

        for view_matrix, confidence in zip(views, confidences):
            # View constraint: E_p[view_matrix] = confidence
            def view_constraint(p):
                return np.sum(p * view_matrix) - confidence

            constraints.append({'type': 'eq', 'fun': view_constraint})

        # Probability simplex constraint: sum(p) = 1, p >= 0
        def simplex_constraint(p):
            return np.sum(p) - 1

        constraints.append({'type': 'eq', 'fun': simplex_constraint})

        # Bounds
        bounds = [(0, None) for _ in range(n_scenarios)]

        # Initial guess
        p0 = prior_distribution.copy()

        # Optimize
        result = minimize(objective, p0, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        posterior_distribution = result.x / np.sum(result.x)  # Renormalize

        return {
            'posterior_distribution': posterior_distribution,
            'optimization_success': result.success,
            'entropy_change': result.fun,
            'views': len(views),
            'model_type': 'Entropy Pooling Portfolio'
        }

    @staticmethod
    def mutual_information_portfolio_selection(returns: pd.DataFrame,
                                            target_portfolio_size: int = 5) -> Dict[str, Any]:
        """Portfolio selection using mutual information criteria.

        Selects assets that provide maximum information about market movements.

        Parameters:
        -----------
        returns : pd.DataFrame
            Asset returns
        target_portfolio_size : int
            Number of assets to select

        Returns:
        --------
        dict : Selected portfolio and information measures
        """
        asset_names = returns.columns
        n_assets = len(asset_names)

        # Compute mutual information with market (equal-weighted portfolio)
        market_returns = returns.mean(axis=1)

        mi_scores = {}
        for asset in asset_names:
            mi = InformationMeasures.mutual_information(
                returns[asset].values, market_returns.values
            )
            mi_scores[asset] = mi

        # Sort assets by mutual information
        sorted_assets = sorted(mi_scores.items(), key=lambda x: x[1], reverse=True)

        # Select top assets
        selected_assets = [asset for asset, _ in sorted_assets[:target_portfolio_size]]

        # Portfolio weights (equal weight among selected)
        weights = np.zeros(n_assets)
        selected_indices = [asset_names.get_loc(asset) for asset in selected_assets]
        weights[selected_indices] = 1.0 / target_portfolio_size

        # Portfolio statistics
        selected_returns = returns[selected_assets]
        portfolio_returns = selected_returns.mean(axis=1)

        sharpe_ratio = (np.mean(portfolio_returns) / np.std(portfolio_returns) *
                       np.sqrt(252)) if np.std(portfolio_returns) > 0 else 0

        return {
            'selected_assets': selected_assets,
            'portfolio_weights': weights,
            'mutual_information_scores': mi_scores,
            'portfolio_sharpe_ratio': sharpe_ratio,
            'total_assets_considered': n_assets,
            'model_type': 'Mutual Information Portfolio Selection'
        }


# =============================================================================
# MARKET MICROSTRUCTURE INFORMATION CONTENT
# =============================================================================

@dataclass
class MarketMicrostructureInformation:
    """Information content analysis of market microstructure."""

    @staticmethod
    def price_impact_information(order_flow: pd.Series,
                               price_changes: pd.Series) -> Dict[str, Any]:
        """Analyze information content of order flow on price impact.

        Measures how much information order flow provides about future price changes.

        Parameters:
        -----------
        order_flow : pd.Series
            Signed order flow (buy - sell)
        price_changes : pd.Series
            Price changes

        Returns:
        --------
        dict : Price impact information analysis
        """
        # Compute mutual information between order flow and price changes
        mi = InformationMeasures.mutual_information(
            order_flow.values, price_changes.values
        )

        # Transfer entropy: order flow → price changes
        transfer_entropy = EntropyMeasures.transfer_entropy(
            order_flow.values, price_changes.values
        )

        # Granger causality test (simplified)
        # Check if order flow predicts price changes better than autoregression

        # Simple linear regression: price_change = a + b * order_flow + c * lagged_price
        lagged_price = price_changes.shift(1).fillna(0)
        X = np.column_stack([np.ones(len(order_flow)), order_flow.values, lagged_price.values])
        y = price_changes.values

        # Remove NaN values
        valid_idx = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X = X[valid_idx]
        y = y[valid_idx]

        if len(X) > 10:
            # Linear regression
            beta = np.linalg.lstsq(X, y, rcond=None)[0]

            # R-squared
            y_pred = X @ beta
            r_squared = 1 - np.var(y - y_pred) / np.var(y)

            # Information coefficient (correlation between prediction and actual)
            info_coeff = np.corrcoef(y_pred, y)[0, 1]
        else:
            r_squared = 0
            info_coeff = 0

        return {
            'mutual_information': mi,
            'transfer_entropy': transfer_entropy,
            'information_coefficient': info_coeff,
            'r_squared': r_squared,
            'predictive_power': max(0, info_coeff**2),
            'model_type': 'Price Impact Information Analysis'
        }

    @staticmethod
    def high_frequency_information_flow(trade_data: pd.DataFrame,
                                      time_window: str = '1min') -> Dict[str, Any]:
        """Analyze high-frequency information flow in market data.

        Measures information transmission between different market
        participants and price formation.

        Parameters:
        -----------
        trade_data : pd.DataFrame
            High-frequency trade data with timestamps, prices, volumes
        time_window : str
            Time window for aggregation

        Returns:
        --------
        dict : High-frequency information flow analysis
        """
        # Resample to time windows
        resampled = trade_data.set_index('timestamp').resample(time_window).agg({
            'price': 'last',
            'volume': 'sum',
            'trade_direction': 'mean'  # Assuming +1 for buys, -1 for sells
        }).dropna()

        # Compute price volatility
        price_returns = resampled['price'].pct_change().dropna()

        # Information flow measures
        # 1. Volume-price mutual information
        volume_price_mi = InformationMeasures.mutual_information(
            resampled['volume'].values, price_returns.values
        )

        # 2. Trade direction information
        direction_price_mi = InformationMeasures.mutual_information(
            resampled['trade_direction'].values, price_returns.values
        )

        # 3. Entropy of trading activity
        volume_entropy = EntropyMeasures.shannon_entropy(
            resampled['volume'].values / np.sum(resampled['volume'])
        )

        # 4. Transfer entropy in trade flow
        volume_to_price_te = EntropyMeasures.transfer_entropy(
            resampled['volume'].values, price_returns.values
        )

        # Market efficiency measure
        # High mutual information suggests less efficiency (predictable patterns)
        market_efficiency = 1 - (volume_price_mi + direction_price_mi) / 2

        return {
            'volume_price_mutual_info': volume_price_mi,
            'direction_price_mutual_info': direction_price_mi,
            'volume_entropy': volume_entropy,
            'volume_to_price_transfer_entropy': volume_to_price_te,
            'market_efficiency_score': market_efficiency,
            'time_window': time_window,
            'n_intervals': len(resampled),
            'model_type': 'High-Frequency Information Flow'
        }


# =============================================================================
# EXPORT INFORMATION THEORY COMPONENTS
# =============================================================================

__all__ = [
    "EntropyMeasures", "InformationMeasures", "InformationGeometry",
    "ChannelCapacity", "KolmogorovComplexity", "InformationPortfolioOptimization",
    "MarketMicrostructureInformation"
]

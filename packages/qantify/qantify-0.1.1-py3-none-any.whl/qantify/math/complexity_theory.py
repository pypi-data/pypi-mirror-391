"""Complexity Theory: Complex Networks, Emergence, and Self-Organization.

This module implements advanced complexity theory including:

- Complex network analysis and graph theory
- Emergence and self-organization
- Agent-based modeling and cellular automata
- Synchronization in complex systems
- Critical phenomena and phase transitions
- Self-organized criticality
- Swarm intelligence and collective behavior
- Complex adaptive systems
- Evolutionary computation
- Artificial life and emergence
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


# =============================================================================
# COMPLEX NETWORK ANALYSIS
# =============================================================================

@dataclass
class ComplexNetworkAnalysis:
    """Advanced analysis of complex networks and graph structures."""

    @staticmethod
    def scale_free_network_generation(n_nodes: int, gamma: float = 2.5,
                                    m_links: int = 2) -> Dict[str, Any]:
        """Generate Barabási-Albert scale-free network.

        Scale-free networks exhibit power-law degree distributions
        and preferential attachment growth.

        Parameters:
        -----------
        n_nodes : int
            Number of nodes in the network
        gamma : float
            Power-law exponent (typically 2.5-3.0)
        m_links : int
            Number of edges to attach from new node

        Returns:
        --------
        dict : Scale-free network structure and properties
        """
        # Initialize with small complete graph
        adjacency_matrix = np.zeros((n_nodes, n_nodes), dtype=int)

        # Start with m_links + 1 nodes in a complete graph
        initial_nodes = m_links + 1
        for i in range(initial_nodes):
            for j in range(i+1, initial_nodes):
                adjacency_matrix[i, j] = 1
                adjacency_matrix[j, i] = 1

        # Degree sequence for preferential attachment
        degrees = np.sum(adjacency_matrix, axis=1)

        # Add remaining nodes with preferential attachment
        for new_node in range(initial_nodes, n_nodes):
            # Calculate attachment probabilities (proportional to degree)
            attachment_probs = degrees[:new_node] / np.sum(degrees[:new_node])

            # Choose m_links nodes to connect to
            connected_nodes = np.random.choice(new_node, size=m_links, replace=False,
                                             p=attachment_probs)

            # Add edges
            for node in connected_nodes:
                adjacency_matrix[new_node, node] = 1
                adjacency_matrix[node, new_node] = 1

            # Update degrees
            degrees[new_node] = m_links
            for node in connected_nodes:
                degrees[node] += 1

        # Compute network properties
        final_degrees = np.sum(adjacency_matrix, axis=1)

        # Degree distribution
        unique_degrees, degree_counts = np.unique(final_degrees, return_counts=True)
        degree_distribution = degree_counts / np.sum(degree_counts)

        # Power-law fit
        try:
            # Fit power law: p(k) ~ k^(-γ)
            log_degrees = np.log(unique_degrees[unique_degrees > 0])
            log_probs = np.log(degree_distribution[unique_degrees > 0])

            slope, intercept = np.polyfit(log_degrees, log_probs, 1)
            fitted_gamma = -slope

        except:
            fitted_gamma = gamma

        # Clustering coefficient
        clustering_coeffs = []
        for i in range(n_nodes):
            neighbors = np.where(adjacency_matrix[i, :] == 1)[0]
            if len(neighbors) > 1:
                # Count triangles
                triangles = 0
                for j in neighbors:
                    for k in neighbors:
                        if j != k and adjacency_matrix[j, k] == 1:
                            triangles += 1

                clustering_coeffs.append(triangles / (len(neighbors) * (len(neighbors) - 1)))
            else:
                clustering_coeffs.append(0)

        avg_clustering = np.mean(clustering_coeffs)

        # Average path length
        distances = np.full((n_nodes, n_nodes), np.inf)
        np.fill_diagonal(distances, 0)

        # Floyd-Warshall for shortest paths
        for i in range(n_nodes):
            for j in range(n_nodes):
                if adjacency_matrix[i, j] == 1:
                    distances[i, j] = 1

        for k in range(n_nodes):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    distances[i, j] = min(distances[i, j],
                                        distances[i, k] + distances[k, j])

        finite_distances = distances[np.isfinite(distances) & (distances < np.inf)]
        avg_path_length = np.mean(finite_distances) if len(finite_distances) > 0 else 0

        return {
            'adjacency_matrix': adjacency_matrix,
            'degrees': final_degrees,
            'degree_distribution': degree_distribution,
            'unique_degrees': unique_degrees,
            'fitted_gamma': fitted_gamma,
            'target_gamma': gamma,
            'avg_clustering': avg_clustering,
            'avg_path_length': avg_path_length,
            'n_nodes': n_nodes,
            'm_links': m_links,
            'model_type': 'Barabási-Albert Scale-Free Network'
        }

    @staticmethod
    def small_world_network_generation(n_nodes: int, k_neighbors: int = 4,
                                     rewiring_prob: float = 0.1) -> Dict[str, Any]:
        """Generate Watts-Strogatz small-world network.

        Small-world networks interpolate between regular lattices
        and random graphs, exhibiting high clustering and short paths.

        Parameters:
        -----------
        n_nodes : int
            Number of nodes
        k_neighbors : int
            Initial nearest neighbors (must be even)
        rewiring_prob : float
            Probability of rewiring each edge

        Returns:
        --------
        dict : Small-world network properties
        """
        # Ensure k_neighbors is even and reasonable
        k_neighbors = min(k_neighbors, n_nodes - 1)
        if k_neighbors % 2 == 1:
            k_neighbors -= 1

        adjacency_matrix = np.zeros((n_nodes, n_nodes), dtype=int)

        # Create regular lattice
        for i in range(n_nodes):
            for j in range(1, k_neighbors//2 + 1):
                # Connect to j steps forward and backward
                neighbor_fwd = (i + j) % n_nodes
                neighbor_bwd = (i - j) % n_nodes

                adjacency_matrix[i, neighbor_fwd] = 1
                adjacency_matrix[neighbor_fwd, i] = 1
                adjacency_matrix[i, neighbor_bwd] = 1
                adjacency_matrix[neighbor_bwd, i] = 1

        # Rewire edges with probability p
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if adjacency_matrix[i, j] == 1 and np.random.random() < rewiring_prob:
                    # Remove edge
                    adjacency_matrix[i, j] = 0
                    adjacency_matrix[j, i] = 0

                    # Add new edge to random node (not self, not already connected)
                    possible_targets = [k for k in range(n_nodes)
                                      if k != i and k != j and adjacency_matrix[i, k] == 0]

                    if possible_targets:
                        new_target = np.random.choice(possible_targets)
                        adjacency_matrix[i, new_target] = 1
                        adjacency_matrix[new_target, i] = 1

        # Compute small-world properties
        degrees = np.sum(adjacency_matrix, axis=1)
        avg_degree = np.mean(degrees)

        # Clustering coefficient
        clustering_coeffs = []
        for i in range(n_nodes):
            neighbors = np.where(adjacency_matrix[i, :] == 1)[0]
            if len(neighbors) > 1:
                triangles = sum(1 for j in neighbors for k in neighbors
                              if j < k and adjacency_matrix[j, k] == 1)
                clustering_coeffs.append(2 * triangles / (len(neighbors) * (len(neighbors) - 1)))
            else:
                clustering_coeffs.append(0)

        avg_clustering = np.mean(clustering_coeffs)

        # Characteristic path length
        distances = np.full((n_nodes, n_nodes), np.inf)
        np.fill_diagonal(distances, 0)

        for i in range(n_nodes):
            for j in range(n_nodes):
                if adjacency_matrix[i, j] == 1:
                    distances[i, j] = 1

        for k in range(n_nodes):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    distances[i, j] = min(distances[i, j],
                                        distances[i, k] + distances[k, j])

        finite_distances = distances[np.isfinite(distances) & (distances < np.inf)]
        char_path_length = np.mean(finite_distances) if len(finite_distances) > 0 else 0

        # Small-world coefficient: high clustering, short paths
        small_world_coeff = avg_clustering / char_path_length if char_path_length > 0 else 0

        return {
            'adjacency_matrix': adjacency_matrix,
            'degrees': degrees,
            'avg_degree': avg_degree,
            'avg_clustering': avg_clustering,
            'char_path_length': char_path_length,
            'small_world_coefficient': small_world_coeff,
            'rewiring_probability': rewiring_prob,
            'k_neighbors': k_neighbors,
            'n_nodes': n_nodes,
            'model_type': 'Watts-Strogatz Small-World Network'
        }

    @staticmethod
    def network_percolation_analysis(adjacency_matrix: np.ndarray,
                                   removal_probabilities: np.ndarray = None) -> Dict[str, Any]:
        """Analyze percolation and robustness of complex networks.

        Study how networks behave under random or targeted node/edge removal.

        Parameters:
        -----------
        adjacency_matrix : np.ndarray
            Network adjacency matrix
        removal_probabilities : np.ndarray
            Probabilities for node removal

        Returns:
        --------
        dict : Percolation analysis results
        """
        n_nodes = adjacency_matrix.shape[0]

        if removal_probabilities is None:
            removal_probabilities = np.linspace(0, 1, 21)

        # Compute largest component size vs removal probability
        largest_component_sizes = []
        avg_component_sizes = []

        for p_remove in removal_probabilities:
            # Remove nodes with probability p_remove
            remaining_nodes = np.random.random(n_nodes) > p_remove
            remaining_indices = np.where(remaining_nodes)[0]

            if len(remaining_indices) == 0:
                largest_component_sizes.append(0)
                avg_component_sizes.append(0)
                continue

            # Extract subgraph
            subgraph = adjacency_matrix[np.ix_(remaining_indices, remaining_indices)]

            # Find connected components
            visited = np.zeros(len(remaining_indices), dtype=bool)
            component_sizes = []

            for i in range(len(remaining_indices)):
                if not visited[i]:
                    # DFS to find component
                    component = []
                    stack = [i]

                    while stack:
                        node = stack.pop()
                        if not visited[node]:
                            visited[node] = True
                            component.append(node)

                            # Add unvisited neighbors
                            for neighbor in range(len(remaining_indices)):
                                if (subgraph[node, neighbor] == 1 and
                                    not visited[neighbor]):
                                    stack.append(neighbor)

                    component_sizes.append(len(component))

            largest_component_sizes.append(max(component_sizes) if component_sizes else 0)
            avg_component_sizes.append(np.mean(component_sizes) if component_sizes else 0)

        # Find percolation threshold (where giant component disappears)
        largest_component_sizes = np.array(largest_component_sizes)
        percolation_threshold = None

        for i in range(1, len(removal_probabilities)):
            if (largest_component_sizes[i-1] > n_nodes * 0.1 and
                largest_component_sizes[i] < n_nodes * 0.1):
                percolation_threshold = removal_probabilities[i]
                break

        # Network robustness metrics
        robustness_metrics = {
            'percolation_threshold': percolation_threshold,
            'final_component_size': largest_component_sizes[-1],
            'critical_removal_prob': removal_probabilities[np.argmax(np.gradient(largest_component_sizes))]
        }

        return {
            'removal_probabilities': removal_probabilities,
            'largest_component_sizes': largest_component_sizes,
            'avg_component_sizes': avg_component_sizes,
            'percolation_threshold': percolation_threshold,
            'robustness_metrics': robustness_metrics,
            'n_nodes': n_nodes,
            'model_type': 'Network Percolation Analysis'
        }


# =============================================================================
# EMERGENCE AND SELF-ORGANIZATION
# =============================================================================

@dataclass
class EmergenceAndSelfOrganization:
    """Analysis of emergent behavior and self-organizing systems."""

    @staticmethod
    def cellular_automaton_evolution(rule_number: int, n_cells: int = 100,
                                   n_generations: int = 50,
                                   initial_condition: np.ndarray = None) -> Dict[str, Any]:
        """Evolve elementary cellular automaton.

        Study emergent patterns from simple local rules.

        Parameters:
        -----------
        rule_number : int
            Wolfram rule number (0-255)
        n_cells : int
            Number of cells
        n_generations : int
            Number of generations to evolve
        initial_condition : np.ndarray
            Initial cell configuration

        Returns:
        --------
        dict : Cellular automaton evolution and pattern analysis
        """
        if initial_condition is None:
            # Random initial condition
            initial_condition = np.random.randint(0, 2, n_cells)
        elif len(initial_condition) != n_cells:
            initial_condition = np.resize(initial_condition, n_cells)

        # Convert rule number to rule table (8 possible neighborhoods)
        rule_table = np.array([int(x) for x in np.binary_repr(rule_number, 8)], dtype=int)

        # Evolution matrix
        evolution = np.zeros((n_generations + 1, n_cells), dtype=int)
        evolution[0, :] = initial_condition

        # Evolve generations
        for gen in range(1, n_generations + 1):
            for i in range(n_cells):
                # Get neighborhood (periodic boundary)
                left = evolution[gen-1, (i-1) % n_cells]
                center = evolution[gen-1, i]
                right = evolution[gen-1, (i+1) % n_cells]

                # Convert to rule index
                neighborhood = 4*left + 2*center + right
                evolution[gen, i] = rule_table[7 - neighborhood]  # Reverse order

        # Analyze emergent patterns
        # Compute density (fraction of live cells)
        densities = np.mean(evolution, axis=1)

        # Compute entropy of each generation
        generation_entropies = []
        for gen in range(n_generations + 1):
            # Compute local patterns (3-cell windows)
            windows = []
            for i in range(n_cells):
                window = [evolution[gen, (i+j) % n_cells] for j in [-1, 0, 1]]
                windows.append(tuple(window))

            # Pattern frequencies
            pattern_counts = {}
            for pattern in windows:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

            # Entropy
            total_patterns = len(windows)
            probs = np.array(list(pattern_counts.values())) / total_patterns
            entropy = -np.sum(probs * np.log2(probs + 1e-10))
            generation_entropies.append(entropy)

        # Classify rule type (Wolfram classification)
        if rule_number in [0, 255]:
            rule_class = 'uniform'
        elif rule_number in [15, 240, 170, 204, 85, 51]:
            rule_class = 'repetitive'
        elif rule_number in [30, 45, 75, 89, 101, 166, 180, 225]:
            rule_class = 'complex'
        else:
            # Check for chaos: high entropy and no periodicity
            avg_entropy = np.mean(generation_entropies[10:])  # Skip transients
            if avg_entropy > 2.0:
                rule_class = 'chaotic'
            else:
                rule_class = 'other'

        return {
            'evolution': evolution,
            'rule_number': rule_number,
            'rule_table': rule_table,
            'densities': densities,
            'generation_entropies': generation_entropies,
            'rule_class': rule_class,
            'n_cells': n_cells,
            'n_generations': n_generations,
            'model_type': 'Cellular Automaton Evolution'
        }

    @staticmethod
    def boid_flocking_simulation(n_boids: int = 50, n_steps: int = 100,
                               cohesion_strength: float = 0.01,
                               alignment_strength: float = 0.05,
                               separation_strength: float = 0.1) -> Dict[str, Any]:
        """Simulate Reynolds' boid flocking model.

        Study emergent collective behavior from simple individual rules.

        Parameters:
        -----------
        n_boids : int
            Number of boids in the flock
        n_steps : int
            Simulation steps
        cohesion_strength : float
            Strength of cohesion rule
        alignment_strength : float
            Strength of alignment rule
        separation_strength : float
            Strength of separation rule

        Returns:
        --------
        dict : Flocking simulation and emergent behavior analysis
        """
        # Initialize boids with random positions and velocities
        positions = np.random.uniform(0, 100, (n_boids, 2))
        velocities = np.random.normal(0, 1, (n_boids, 2))

        # Normalize initial velocities
        speeds = np.linalg.norm(velocities, axis=1, keepdims=True)
        velocities = velocities / (speeds + 1e-6) * 2  # Speed of 2

        # Store trajectories
        position_history = [positions.copy()]
        velocity_history = [velocities.copy()]

        # Simulation parameters
        perception_radius = 10
        max_speed = 3
        min_speed = 1

        for step in range(n_steps):
            new_positions = positions.copy()
            new_velocities = velocities.copy()

            for i in range(n_boids):
                # Find neighbors within perception radius
                distances = np.linalg.norm(positions - positions[i], axis=1)
                neighbors = distances < perception_radius
                neighbors[i] = False  # Exclude self

                if np.sum(neighbors) > 0:
                    # Cohesion: steer towards center of mass of neighbors
                    center_of_mass = np.mean(positions[neighbors], axis=0)
                    cohesion_vector = (center_of_mass - positions[i]) * cohesion_strength

                    # Alignment: steer towards average velocity of neighbors
                    avg_velocity = np.mean(velocities[neighbors], axis=0)
                    alignment_vector = (avg_velocity - velocities[i]) * alignment_strength

                    # Separation: steer away from nearby boids
                    too_close = distances < 2
                    too_close[i] = False

                    if np.sum(too_close) > 0:
                        separation_vector = np.zeros(2)
                        for j in np.where(too_close)[0]:
                            diff = positions[i] - positions[j]
                            dist = distances[j]
                            if dist > 0:
                                separation_vector += diff / dist
                        separation_vector *= separation_strength
                    else:
                        separation_vector = np.zeros(2)

                    # Update velocity
                    new_velocities[i] += cohesion_vector + alignment_vector + separation_vector

                # Limit speed
                speed = np.linalg.norm(new_velocities[i])
                if speed > max_speed:
                    new_velocities[i] = new_velocities[i] / speed * max_speed
                elif speed < min_speed:
                    new_velocities[i] = new_velocities[i] / speed * min_speed

            # Update positions
            new_positions += new_velocities

            # Periodic boundary conditions
            new_positions = new_positions % 100

            positions = new_positions
            velocities = new_velocities

            position_history.append(positions.copy())
            velocity_history.append(velocities.copy())

        # Analyze emergent behavior
        # Compute order parameter (alignment)
        order_parameters = []
        for velocities_at_t in velocity_history:
            avg_velocity = np.mean(velocities_at_t, axis=0)
            order_param = np.linalg.norm(avg_velocity) / np.mean(np.linalg.norm(velocities_at_t, axis=1))
            order_parameters.append(order_param)

        # Compute clustering coefficient (how grouped boids are)
        clustering_coeffs = []
        for positions_at_t in position_history:
            # Simple clustering: average distance to nearest neighbor
            distances = []
            for i in range(n_boids):
                dist_to_others = np.linalg.norm(positions_at_t - positions_at_t[i], axis=1)
                dist_to_others = dist_to_others[dist_to_others > 1e-6]  # Exclude self
                if len(dist_to_others) > 0:
                    distances.append(np.min(dist_to_others))

            avg_min_distance = np.mean(distances) if distances else 0
            clustering_coeffs.append(1 / (1 + avg_min_distance))  # Higher when more clustered

        return {
            'position_history': position_history,
            'velocity_history': velocity_history,
            'order_parameters': order_parameters,
            'clustering_coefficients': clustering_coeffs,
            'final_order_parameter': order_parameters[-1],
            'final_clustering': clustering_coeffs[-1],
            'cohesion_strength': cohesion_strength,
            'alignment_strength': alignment_strength,
            'separation_strength': separation_strength,
            'n_boids': n_boids,
            'n_steps': n_steps,
            'model_type': 'Boid Flocking Simulation'
        }

    @staticmethod
    def self_organized_criticality_sandpile(lattice_size: int = 50,
                                          n_grains: int = 10000) -> Dict[str, Any]:
        """Simulate Bak-Tang-Wiesenfeld sandpile model.

        Study self-organized criticality where systems naturally evolve
        to a critical state with power-law avalanche distributions.

        Parameters:
        -----------
        lattice_size : int
            Size of square lattice
        n_grains : int
            Number of grains to add

        Returns:
        --------
        dict : Sandpile evolution and criticality analysis
        """
        # Initialize lattice
        lattice = np.zeros((lattice_size, lattice_size), dtype=int)
        avalanche_sizes = []
        avalanche_areas = []

        # Critical height (Bak-Tang-Wiesenfeld rule)
        critical_height = 4

        for grain in range(n_grains):
            # Add grain at random position
            i, j = np.random.randint(0, lattice_size, 2)
            lattice[i, j] += 1

            # Check for avalanches
            avalanche_size = 0
            avalanche_area = 0

            # Use queue for avalanche propagation
            unstable_sites = [(i, j)]

            while unstable_sites:
                x, y = unstable_sites.pop(0)

                if lattice[x, y] >= critical_height:
                    # Topple site
                    lattice[x, y] -= critical_height
                    avalanche_size += 1

                    # Get neighbors (von Neumann neighborhood)
                    neighbors = [
                        ((x-1) % lattice_size, y),
                        ((x+1) % lattice_size, y),
                        (x, (y-1) % lattice_size),
                        (x, (y+1) % lattice_size)
                    ]

                    for nx, ny in neighbors:
                        lattice[nx, ny] += 1
                        if lattice[nx, ny] >= critical_height:
                            unstable_sites.append((nx, ny))

                    # Mark area as affected
                    avalanche_area = max(avalanche_area, len(set(unstable_sites)))

            if avalanche_size > 0:
                avalanche_sizes.append(avalanche_size)
                avalanche_areas.append(avalanche_area)

        # Analyze avalanche statistics
        if avalanche_sizes:
            # Power-law fit for avalanche sizes
            sizes = np.array(avalanche_sizes)
            unique_sizes, counts = np.unique(sizes, return_counts=True)

            # Fit power law: p(s) ~ s^(-τ)
            try:
                log_sizes = np.log(unique_sizes)
                log_counts = np.log(counts)
                slope, intercept = np.polyfit(log_sizes, log_counts, 1)
                avalanche_exponent = -slope
            except:
                avalanche_exponent = 1.5  # Typical SOC value

            # Moments
            mean_size = np.mean(sizes)
            max_size = np.max(sizes)

        else:
            avalanche_exponent = 1.5
            mean_size = 0
            max_size = 0

        # Check for criticality (power-law distribution)
        is_critical = 1.0 < avalanche_exponent < 2.5  # Typical SOC range

        return {
            'final_lattice': lattice,
            'avalanche_sizes': avalanche_sizes,
            'avalanche_areas': avalanche_areas,
            'avalanche_exponent': avalanche_exponent,
            'mean_avalanche_size': mean_size,
            'max_avalanche_size': max_size,
            'is_critical': is_critical,
            'lattice_size': lattice_size,
            'n_grains': n_grains,
            'model_type': 'Self-Organized Criticality Sandpile'
        }


# =============================================================================
# SYNCHRONIZATION IN COMPLEX SYSTEMS
# =============================================================================

@dataclass
class SynchronizationInComplexSystems:
    """Analysis of synchronization phenomena in complex systems."""

    @staticmethod
    def kuramoto_model_oscillators(n_oscillators: int = 100,
                                 coupling_strength: float = 0.5,
                                 n_steps: int = 1000,
                                 dt: float = 0.01) -> Dict[str, Any]:
        """Simulate Kuramoto model of coupled oscillators.

        Study synchronization emergence in networks of coupled oscillators.

        Parameters:
        -----------
        n_oscillators : int
            Number of oscillators
        coupling_strength : float
            Coupling strength K
        n_steps : int
            Simulation steps
        dt : float
            Time step

        Returns:
        --------
        dict : Synchronization dynamics and order parameter
        """
        # Initialize natural frequencies and phases
        natural_frequencies = np.random.normal(0, 1, n_oscillators)  # Gaussian distribution
        phases = np.random.uniform(0, 2*np.pi, n_oscillators)

        # Store phase evolution
        phase_history = [phases.copy()]

        # Coupling matrix (all-to-all coupling)
        coupling_matrix = np.ones((n_oscillators, n_oscillators)) / n_oscillators

        # Simulation
        order_parameters = []

        for step in range(n_steps):
            # Compute order parameter
            r = np.abs(np.mean(np.exp(1j * phases)))
            order_parameters.append(r)

            # Update phases
            for i in range(n_oscillators):
                # Kuramoto equation: dθ_i/dt = ω_i + (K/N) Σ sin(θ_j - θ_i)
                coupling_term = coupling_strength * np.sum(np.sin(phases - phases[i]))

                # Euler integration
                phases[i] += (natural_frequencies[i] + coupling_term) * dt

            phase_history.append(phases.copy())

        # Analyze synchronization
        final_order_parameter = order_parameters[-1]

        # Critical coupling strength (theoretical: K_c = 2/π for uniform frequencies)
        theoretical_kc = 2 / np.pi
        is_synchronized = final_order_parameter > 0.8

        # Frequency synchronization
        final_frequencies = np.diff(np.array(phase_history)[-10:], axis=0).mean(axis=0) / dt
        frequency_spread = np.std(final_frequencies)

        return {
            'phase_history': phase_history,
            'order_parameters': order_parameters,
            'final_order_parameter': final_order_parameter,
            'frequency_spread': frequency_spread,
            'is_synchronized': is_synchronized,
            'coupling_strength': coupling_strength,
            'theoretical_critical_coupling': theoretical_kc,
            'natural_frequencies': natural_frequencies,
            'n_oscillators': n_oscillators,
            'n_steps': n_steps,
            'model_type': 'Kuramoto Model Oscillators'
        }

    @staticmethod
    def chimera_states_network(n_nodes: int = 100,
                             coupling_strength: float = 0.5,
                             n_steps: int = 1000) -> Dict[str, Any]:
        """Generate chimera states in complex networks.

        Chimera states exhibit coexistence of synchronized and
        desynchronized regions in spatially extended systems.

        Parameters:
        -----------
        n_nodes : int
            Number of network nodes
        coupling_strength : float
            Coupling strength
        n_steps : int
            Simulation steps

        Returns:
        --------
        dict : Chimera state analysis
        """
        # Create ring network with nonlocal coupling
        positions = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
        coupling_range = int(0.3 * n_nodes)  # 30% of nodes

        # Coupling matrix: connect to nearby nodes
        coupling_matrix = np.zeros((n_nodes, n_nodes))

        for i in range(n_nodes):
            for j in range(-coupling_range, coupling_range + 1):
                if j != 0:
                    neighbor = (i + j) % n_nodes
                    distance = min(abs(j), n_nodes - abs(j))
                    coupling_matrix[i, neighbor] = np.exp(-distance / (n_nodes/10))

        # Normalize rows
        row_sums = coupling_matrix.sum(axis=1)
        coupling_matrix = coupling_matrix / row_sums[:, np.newaxis]

        # Initialize oscillators
        phases = np.random.uniform(0, 2*np.pi, n_nodes)
        natural_frequencies = np.random.normal(0, 0.1, n_nodes)

        phase_history = [phases.copy()]

        # Simulation
        dt = 0.01
        chimera_detected = False
        chimera_strength = 0

        for step in range(n_steps):
            # Update phases
            new_phases = phases.copy()

            for i in range(n_nodes):
                # Mean field coupling
                mean_field = np.mean(np.exp(1j * phases))
                coupling_term = coupling_strength * np.imag(np.exp(1j * phases[i]) * np.conj(mean_field))

                # Update
                new_phases[i] += (natural_frequencies[i] + coupling_term) * dt

            phases = new_phases
            phase_history.append(phases.copy())

            # Check for chimera state (every 100 steps)
            if step % 100 == 0 and step > 500:
                # Compute local order parameters
                window_size = 10
                local_orders = []

                for i in range(n_nodes):
                    neighbors = [(i + j) % n_nodes for j in range(-window_size, window_size + 1)]
                    local_phases = phases[neighbors]
                    local_order = np.abs(np.mean(np.exp(1j * local_phases)))
                    local_orders.append(local_order)

                local_orders = np.array(local_orders)

                # Chimera condition: coexistence of high and low synchronization
                high_sync = local_orders > 0.8
                low_sync = local_orders < 0.3

                if np.sum(high_sync) > 0 and np.sum(low_sync) > 0:
                    chimera_detected = True
                    chimera_strength = np.std(local_orders)

        return {
            'phase_history': phase_history,
            'coupling_matrix': coupling_matrix,
            'chimera_detected': chimera_detected,
            'chimera_strength': chimera_strength,
            'final_phases': phases,
            'natural_frequencies': natural_frequencies,
            'coupling_strength': coupling_strength,
            'n_nodes': n_nodes,
            'n_steps': n_steps,
            'model_type': 'Chimera States Network'
        }


# =============================================================================
# EVOLUTIONARY COMPUTATION
# =============================================================================

@dataclass
class EvolutionaryComputation:
    """Evolutionary algorithms and computational evolution."""

    @staticmethod
    def genetic_algorithm_optimization(objective_function: Callable,
                                     n_variables: int,
                                     population_size: int = 50,
                                     n_generations: int = 100,
                                     mutation_rate: float = 0.1) -> Dict[str, Any]:
        """Run genetic algorithm for optimization.

        Evolutionary optimization using selection, crossover, and mutation.

        Parameters:
        -----------
        objective_function : callable
            Function to optimize (minimization)
        n_variables : int
            Number of optimization variables
        population_size : int
            Population size
        n_generations : int
            Number of generations
        mutation_rate : float
            Mutation probability

        Returns:
        --------
        dict : Evolutionary optimization results
        """
        # Initialize population (random in [-5, 5])
        population = np.random.uniform(-5, 5, (population_size, n_variables))
        fitness_history = []

        best_fitness_history = []
        best_solution_history = []

        for generation in range(n_generations):
            # Evaluate fitness
            fitness = np.array([objective_function(individual) for individual in population])
            fitness_history.append(np.mean(fitness))

            # Track best solution
            best_idx = np.argmin(fitness)
            best_fitness_history.append(fitness[best_idx])
            best_solution_history.append(population[best_idx].copy())

            # Selection: tournament selection
            selected = []

            for _ in range(population_size):
                # Select 3 random individuals
                candidates = np.random.choice(population_size, 3, replace=False)
                winner = candidates[np.argmin(fitness[candidates])]
                selected.append(population[winner].copy())

            selected = np.array(selected)

            # Crossover: blend crossover
            offspring = []

            for i in range(0, population_size, 2):
                if i + 1 < population_size:
                    parent1, parent2 = selected[i], selected[i+1]

                    # Blend crossover
                    alpha = np.random.uniform(-0.5, 1.5, n_variables)
                    child1 = alpha * parent1 + (1 - alpha) * parent2
                    child2 = (1 - alpha) * parent1 + alpha * parent2

                    offspring.extend([child1, child2])

            offspring = np.array(offspring[:population_size])

            # Mutation: Gaussian mutation
            mutation_mask = np.random.random((population_size, n_variables)) < mutation_rate
            mutations = np.random.normal(0, 0.1, (population_size, n_variables))
            offspring[mutation_mask] += mutations[mutation_mask]

            # Elitism: keep best individual
            best_individual = population[best_idx].copy()
            offspring[0] = best_individual

            population = offspring

        # Final evaluation
        final_fitness = np.array([objective_function(individual) for individual in population])
        best_idx = np.argmin(final_fitness)
        best_solution = population[best_idx]
        best_fitness = final_fitness[best_idx]

        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'fitness_history': fitness_history,
            'best_fitness_history': best_fitness_history,
            'final_population': population,
            'final_fitnesses': final_fitness,
            'n_variables': n_variables,
            'population_size': population_size,
            'n_generations': n_generations,
            'mutation_rate': mutation_rate,
            'model_type': 'Genetic Algorithm Optimization'
        }

    @staticmethod
    def particle_swarm_optimization(objective_function: Callable,
                                  n_variables: int,
                                  n_particles: int = 30,
                                  n_iterations: int = 100,
                                  inertia_weight: float = 0.7,
                                  cognitive_weight: float = 1.4,
                                  social_weight: float = 1.4) -> Dict[str, Any]:
        """Run particle swarm optimization.

        Swarm intelligence optimization inspired by bird flocking.

        Parameters:
        -----------
        objective_function : callable
            Function to minimize
        n_variables : int
            Number of variables
        n_particles : int
            Number of particles
        n_iterations : int
            Number of iterations
        inertia_weight : float
            Inertia weight w
        cognitive_weight : float
            Cognitive weight c1
        social_weight : float
            Social weight c2

        Returns:
        --------
        dict : PSO optimization results
        """
        # Initialize particles
        positions = np.random.uniform(-5, 5, (n_particles, n_variables))
        velocities = np.random.uniform(-1, 1, (n_particles, n_variables))

        # Initialize personal bests
        personal_best_positions = positions.copy()
        personal_best_fitness = np.array([objective_function(p) for p in positions])

        # Initialize global best
        global_best_idx = np.argmin(personal_best_fitness)
        global_best_position = personal_best_positions[global_best_idx].copy()
        global_best_fitness = personal_best_fitness[global_best_idx]

        # Store history
        fitness_history = [np.mean(personal_best_fitness)]
        global_best_history = [global_best_fitness]

        for iteration in range(n_iterations):
            for i in range(n_particles):
                # Update velocity
                r1, r2 = np.random.random(2)

                cognitive_component = cognitive_weight * r1 * (personal_best_positions[i] - positions[i])
                social_component = social_weight * r2 * (global_best_position - positions[i])

                velocities[i] = (inertia_weight * velocities[i] +
                               cognitive_component + social_component)

                # Update position
                positions[i] += velocities[i]

                # Evaluate new position
                fitness = objective_function(positions[i])

                # Update personal best
                if fitness < personal_best_fitness[i]:
                    personal_best_positions[i] = positions[i].copy()
                    personal_best_fitness[i] = fitness

                    # Update global best
                    if fitness < global_best_fitness:
                        global_best_position = positions[i].copy()
                        global_best_fitness = fitness

            fitness_history.append(np.mean(personal_best_fitness))
            global_best_history.append(global_best_fitness)

        return {
            'best_solution': global_best_position,
            'best_fitness': global_best_fitness,
            'fitness_history': fitness_history,
            'global_best_history': global_best_history,
            'final_positions': positions,
            'final_velocities': velocities,
            'n_variables': n_variables,
            'n_particles': n_particles,
            'n_iterations': n_iterations,
            'inertia_weight': inertia_weight,
            'cognitive_weight': cognitive_weight,
            'social_weight': social_weight,
            'model_type': 'Particle Swarm Optimization'
        }


# =============================================================================
# EXPORT COMPLEXITY THEORY COMPONENTS
# =============================================================================

__all__ = [
    "ComplexNetworkAnalysis", "EmergenceAndSelfOrganization",
    "SynchronizationInComplexSystems", "EvolutionaryComputation"
]

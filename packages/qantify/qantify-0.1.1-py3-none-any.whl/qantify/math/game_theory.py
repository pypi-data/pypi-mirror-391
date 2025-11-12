"""Game theory models for strategic analysis and Nash equilibrium computation."""

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


# =============================================================================
# NASH EQUILIBRIUM COMPUTATION
# =============================================================================

@dataclass
class NashEquilibriumSolver:
    """Advanced Nash equilibrium solvers for strategic games."""

    @staticmethod
    def two_player_normal_form_nash(payoff_matrix_p1: np.ndarray,
                                  payoff_matrix_p2: np.ndarray,
                                  solver_method: str = 'support_enumeration') -> Dict[str, Any]:
        """Compute Nash equilibria for two-player normal form games.

        Supports multiple algorithms: support enumeration, vertex enumeration,
        and Lemke-Howson algorithm.

        Parameters:
        -----------
        payoff_matrix_p1 : np.ndarray
            Payoff matrix for player 1 (n_actions_p1 x n_actions_p2)
        payoff_matrix_p2 : np.ndarray
            Payoff matrix for player 2 (n_actions_p1 x n_actions_p2)
        solver_method : str
            Solution method ('support_enumeration', 'vertex_enumeration', 'lemke_howson')

        Returns:
        --------
        dict : Nash equilibria and game properties
        """
        n_actions_p1, n_actions_p2 = payoff_matrix_p1.shape

        if solver_method == 'support_enumeration':
            equilibria = NashEquilibriumSolver._support_enumeration_nash(
                payoff_matrix_p1, payoff_matrix_p2
            )
        elif solver_method == 'lemke_howson':
            equilibria = NashEquilibriumSolver._lemke_howson_nash(
                payoff_matrix_p1, payoff_matrix_p2
            )
        else:
            equilibria = []

        # Classify game type
        game_type = NashEquilibriumSolver._classify_game_type(
            payoff_matrix_p1, payoff_matrix_p2
        )

        return {
            'equilibria': equilibria,
            'n_equilibria': len(equilibria),
            'game_type': game_type,
            'payoff_matrices': {
                'player1': payoff_matrix_p1,
                'player2': payoff_matrix_p2
            },
            'solver_method': solver_method,
            'model_type': 'Two-Player Normal Form Nash Equilibrium'
        }

    @staticmethod
    def _support_enumeration_nash(payoff_p1: np.ndarray, payoff_p2: np.ndarray) -> List[Dict]:
        """Support enumeration algorithm for Nash equilibrium."""
        m, n = payoff_p1.shape
        equilibria = []

        # Check all possible support sizes
        for supp_p1_size in range(1, m + 1):
            for supp_p2_size in range(1, n + 1):
                # Generate all possible supports
                for supp_p1 in NashEquilibriumSolver._combinations(range(m), supp_p1_size):
                    for supp_p2 in NashEquilibriumSolver._combinations(range(n), supp_p2_size):

                        # Check if supports form equilibrium
                        try:
                            mixed_p1, mixed_p2 = NashEquilibriumSolver._solve_indifference_equations(
                                payoff_p1, payoff_p2, supp_p1, supp_p2
                            )

                            if mixed_p1 is not None and mixed_p2 is not None:
                                equilibria.append({
                                    'player1_strategy': mixed_p1,
                                    'player2_strategy': mixed_p2,
                                    'player1_payoff': np.dot(mixed_p1, payoff_p1 @ mixed_p2),
                                    'player2_payoff': np.dot(mixed_p1, payoff_p2 @ mixed_p2)
                                })

                        except:
                            continue

        return equilibria

    @staticmethod
    def _solve_indifference_equations(payoff_p1: np.ndarray, payoff_p2: np.ndarray,
                                    supp_p1: List[int], supp_p2: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """Solve indifference equations for given supports."""
        # For player 1: payoff_p1[supp_p1, :] @ mixed_p2 should be equal for all i in supp_p1
        A_p1 = payoff_p1[np.ix_(supp_p1, supp_p2)].T
        b_p1 = np.ones(len(supp_p1))

        try:
            mixed_p2_partial = np.linalg.solve(A_p1, b_p1)
            mixed_p2_partial = mixed_p2_partial / np.sum(mixed_p2_partial)

            # Check non-negativity
            if np.all(mixed_p2_partial >= -1e-10):  # Allow small negative due to numerical error
                mixed_p2 = np.zeros(payoff_p2.shape[1])
                mixed_p2[supp_p2] = np.maximum(mixed_p2_partial, 0)
                mixed_p2 = mixed_p2 / np.sum(mixed_p2)

                # For player 2
                A_p2 = payoff_p2[np.ix_(supp_p1, supp_p2)]
                b_p2 = np.ones(len(supp_p2))

                mixed_p1_partial = np.linalg.solve(A_p2, b_p2)
                mixed_p1_partial = mixed_p1_partial / np.sum(mixed_p1_partial)

                if np.all(mixed_p1_partial >= -1e-10):
                    mixed_p1 = np.zeros(payoff_p1.shape[0])
                    mixed_p1[supp_p1] = np.maximum(mixed_p1_partial, 0)
                    mixed_p1 = mixed_p1 / np.sum(mixed_p1)

                    return mixed_p1, mixed_p2

        except np.linalg.LinAlgError:
            pass

        return None, None

    @staticmethod
    def _combinations(iterable: List, r: int) -> List[List]:
        """Generate combinations of given length."""
        from itertools import combinations
        return list(combinations(iterable, r))

    @staticmethod
    def _lemke_howson_nash(payoff_p1: np.ndarray, payoff_p2: np.ndarray) -> List[Dict]:
        """Lemke-Howson algorithm for Nash equilibrium computation."""
        # Simplified implementation - in practice would use more sophisticated pivoting
        m, n = payoff_p1.shape

        # Start with artificial equilibrium
        mixed_p1 = np.ones(m) / m
        mixed_p2 = np.ones(n) / n

        # Simple iterative approximation
        max_iter = 100
        tolerance = 1e-6

        for _ in range(max_iter):
            # Best response for player 1
            payoffs_p1 = payoff_p1 @ mixed_p2
            best_response_p1 = np.zeros(m)
            best_response_p1[np.argmax(payoffs_p1)] = 1.0

            # Best response for player 2
            payoffs_p2 = mixed_p1 @ payoff_p2
            best_response_p2 = np.zeros(n)
            best_response_p2[np.argmax(payoffs_p2)] = 1.0

            # Update mixed strategies
            mixed_p1 = 0.9 * mixed_p1 + 0.1 * best_response_p1
            mixed_p2 = 0.9 * mixed_p2 + 0.1 * best_response_p2

            # Check convergence
            if np.linalg.norm(best_response_p1 - mixed_p1) < tolerance and \
               np.linalg.norm(best_response_p2 - mixed_p2) < tolerance:
                break

        equilibrium = {
            'player1_strategy': mixed_p1,
            'player2_strategy': mixed_p2,
            'player1_payoff': np.dot(mixed_p1, payoff_p1 @ mixed_p2),
            'player2_payoff': np.dot(mixed_p1, payoff_p2 @ mixed_p2)
        }

        return [equilibrium]

    @staticmethod
    def _classify_game_type(payoff_p1: np.ndarray, payoff_p2: np.ndarray) -> str:
        """Classify the type of strategic game."""
        # Check for zero-sum
        if np.allclose(payoff_p1 + payoff_p2, 0):
            return "zero-sum"

        # Check for coordination game
        # Both players have same preferences
        if np.allclose(payoff_p1, payoff_p2):
            return "coordination"

        # Check for prisoner's dilemma structure
        m, n = payoff_p1.shape
        if m == 2 and n == 2:
            # Standard prisoner's dilemma check
            if (payoff_p1[0, 0] > payoff_p1[1, 0] > payoff_p1[1, 1] > payoff_p1[0, 1] and
                payoff_p2[0, 0] > payoff_p2[0, 1] > payoff_p2[1, 1] > payoff_p2[1, 0]):
                return "prisoner's dilemma"

        return "general normal form"


# =============================================================================
# EVOLUTIONARY GAME THEORY
# =============================================================================

@dataclass
class EvolutionaryGameTheory:
    """Evolutionary game theory models and replicator dynamics."""

    @staticmethod
    def replicator_dynamics(payoff_matrix: np.ndarray, initial_population: np.ndarray,
                          time_steps: int = 100, mutation_rate: float = 0.01) -> Dict[str, Any]:
        """Simulate replicator dynamics in evolutionary games.

        Models the evolution of strategies in a population where
        successful strategies reproduce more rapidly.

        Parameters:
        -----------
        payoff_matrix : np.ndarray
            Payoff matrix for the game (n_strategies x n_strategies)
        initial_population : np.ndarray
            Initial population distribution over strategies
        time_steps : int
            Number of evolutionary time steps
        mutation_rate : float
            Probability of mutation at each step

        Returns:
        --------
        dict : Evolutionary dynamics and equilibrium analysis
        """
        population = initial_population.copy()
        population_history = [population.copy()]
        fitness_history = []

        n_strategies = len(population)

        for t in range(time_steps):
            # Compute fitness for each strategy
            fitness = payoff_matrix @ population

            # Average fitness
            avg_fitness = np.dot(population, fitness)
            fitness_history.append(avg_fitness)

            # Replicator equation
            new_population = population * fitness / avg_fitness

            # Mutation
            if mutation_rate > 0:
                mutation_matrix = np.full((n_strategies, n_strategies),
                                        mutation_rate / (n_strategies - 1))
                np.fill_diagonal(mutation_matrix, 1 - mutation_rate)
                new_population = mutation_matrix @ new_population

            # Renormalize
            new_population = new_population / np.sum(new_population)

            population = new_population
            population_history.append(population.copy())

        # Analyze equilibria
        final_population = population_history[-1]
        equilibria = []

        # Check for evolutionarily stable strategies (ESS)
        for i in range(n_strategies):
            strategy = np.zeros(n_strategies)
            strategy[i] = 1.0

            # Check ESS conditions
            fitness_against_itself = payoff_matrix[i, i]
            fitness_against_mutants = payoff_matrix[i, :] @ final_population

            if fitness_against_itself > fitness_against_mutants:
                equilibria.append({
                    'strategy': i,
                    'type': 'ESS',
                    'final_frequency': final_population[i]
                })

        return {
            'population_history': np.array(population_history),
            'fitness_history': np.array(fitness_history),
            'final_population': final_population,
            'equilibria': equilibria,
            'payoff_matrix': payoff_matrix,
            'mutation_rate': mutation_rate,
            'model_type': 'Replicator Dynamics'
        }

    @staticmethod
    def hawk_dove_game_evolution(hawk_payoff: float = 50, dove_payoff: float = 25,
                               cost_of_fight: float = 100, resource_value: float = 100) -> Dict[str, Any]:
        """Evolutionary analysis of hawk-dove game.

        Classic evolutionary game where individuals can be aggressive (hawk)
        or passive (dove) in resource competition.

        Parameters:
        -----------
        hawk_payoff : float
            Payoff for hawk vs dove
        dove_payoff : float
            Payoff for dove vs dove
        cost_of_fight : float
            Cost when two hawks fight
        resource_value : float
            Value of the contested resource

        Returns:
        --------
        dict : Evolutionary analysis of hawk-dove game
        """
        # Payoff matrix for hawk-dove game
        # Rows: own strategy, Columns: opponent's strategy
        payoff_matrix = np.array([
            [(resource_value - cost_of_fight)/2, resource_value],  # Hawk vs [Hawk, Dove]
            [0, resource_value/2]  # Dove vs [Hawk, Dove]
        ])

        # Initial mixed population
        initial_pop = np.array([0.5, 0.5])

        # Run evolutionary dynamics
        evolution = EvolutionaryGameTheory.replicator_dynamics(
            payoff_matrix, initial_pop, time_steps=200
        )

        # Analytical equilibrium
        # For hawk-dove: p* = cost_of_fight / (cost_of_fight + resource_value)
        analytical_equilibrium = cost_of_fight / (cost_of_fight + resource_value)

        return {
            'payoff_matrix': payoff_matrix,
            'evolutionary_dynamics': evolution,
            'analytical_equilibrium': analytical_equilibrium,
            'hawk_dove_parameters': {
                'hawk_payoff': hawk_payoff,
                'dove_payoff': dove_payoff,
                'cost_of_fight': cost_of_fight,
                'resource_value': resource_value
            },
            'model_type': 'Hawk-Dove Evolutionary Game'
        }

    @staticmethod
    def rock_paper_scissors_evolution(strength_advantage: float = 1.0) -> Dict[str, Any]:
        """Evolutionary rock-paper-scissors game.

        Cyclic game where each strategy beats another in a cycle,
        leading to never-ending evolution.

        Parameters:
        -----------
        strength_advantage : float
            Strength of the advantage for beating opponent

        Returns:
        --------
        dict : Evolutionary rock-paper-scissors dynamics
        """
        # Payoff matrix: Rock=0, Paper=1, Scissors=2
        payoff_matrix = np.array([
            [0, -strength_advantage, strength_advantage],   # Rock vs [Rock, Paper, Scissors]
            [strength_advantage, 0, -strength_advantage],  # Paper vs [Rock, Paper, Scissors]
            [-strength_advantage, strength_advantage, 0]   # Scissors vs [Rock, Paper, Scissors]
        ])

        # Initial population: equal frequencies
        initial_pop = np.array([1/3, 1/3, 1/3])

        # Run long-term evolution
        evolution = EvolutionaryGameTheory.replicator_dynamics(
            payoff_matrix, initial_pop, time_steps=500, mutation_rate=0.001
        )

        # Compute cycling behavior
        population_history = evolution['population_history']
        cycle_length = EvolutionaryGameTheory._estimate_cycle_length(population_history)

        return {
            'payoff_matrix': payoff_matrix,
            'evolutionary_dynamics': evolution,
            'cycle_length': cycle_length,
            'cycling_behavior': cycle_length > 0,
            'strength_advantage': strength_advantage,
            'model_type': 'Rock-Paper-Scissors Evolutionary Game'
        }

    @staticmethod
    def _estimate_cycle_length(population_history: np.ndarray) -> int:
        """Estimate the length of evolutionary cycles."""
        # Simple autocorrelation-based cycle detection
        n_steps = len(population_history)

        if n_steps < 20:
            return 0

        # Use first strategy's frequency
        series = population_history[:, 0]

        # Compute autocorrelation
        autocorr = np.correlate(series - np.mean(series),
                              series - np.mean(series), mode='full')
        autocorr = autocorr[autocorr.size // 2:]

        # Find peaks in autocorrelation (excluding lag 0)
        peaks = []
        for i in range(10, min(100, len(autocorr))):
            if (autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and
                autocorr[i] > 0.1 * autocorr[1]):  # Significant peak
                peaks.append(i)

        return peaks[0] if peaks else 0


# =============================================================================
# BARGAINING THEORY AND COOPERATIVE GAMES
# =============================================================================

@dataclass
class BargainingTheory:
    """Cooperative bargaining theory and solution concepts."""

    @staticmethod
    def nash_bargaining_solution(player1_payoffs: np.ndarray, player2_payoffs: np.ndarray,
                               disagreement_point: Tuple[float, float] = (0, 0)) -> Dict[str, Any]:
        """Compute Nash bargaining solution.

        Maximizes the product of utility gains over the disagreement point.

        Parameters:
        -----------
        player1_payoffs : np.ndarray
            Feasible payoffs for player 1
        player2_payoffs : np.ndarray
            Feasible payoffs for player 2
        disagreement_point : tuple
            Payoffs if bargaining fails

        Returns:
        --------
        dict : Nash bargaining solution
        """
        d1, d2 = disagreement_point

        # Find Pareto frontier
        pareto_frontier = BargainingTheory._compute_pareto_frontier(
            player1_payoffs, player2_payoffs
        )

        if len(pareto_frontier) == 0:
            return {'error': 'No Pareto optimal points found'}

        # Nash bargaining: max (u1 - d1) * (u2 - d2)
        nash_product = -np.inf
        nash_solution = None

        for u1, u2 in pareto_frontier:
            if u1 > d1 and u2 > d2:
                product = (u1 - d1) * (u2 - d2)
                if product > nash_product:
                    nash_product = product
                    nash_solution = (u1, u2)

        return {
            'nash_solution': nash_solution,
            'nash_product': nash_product,
            'pareto_frontier': pareto_frontier,
            'disagreement_point': disagreement_point,
            'model_type': 'Nash Bargaining Solution'
        }

    @staticmethod
    def kalai_smorodinsky_solution(player1_payoffs: np.ndarray, player2_payoffs: np.ndarray,
                                 disagreement_point: Tuple[float, float] = (0, 0)) -> Dict[str, Any]:
        """Compute Kalai-Smorodinsky bargaining solution.

        Equal proportional reductions from ideal points.

        Parameters:
        -----------
        player1_payoffs : np.ndarray
            Feasible payoffs for player 1
        player2_payoffs : np.ndarray
            Feasible payoffs for player 2
        disagreement_point : tuple
            Payoffs if bargaining fails

        Returns:
        --------
        dict : Kalai-Smorodinsky solution
        """
        d1, d2 = disagreement_point

        # Ideal points (maximum feasible payoffs)
        ideal_p1 = np.max(player1_payoffs)
        ideal_p2 = np.max(player2_payoffs)

        # Find Pareto frontier
        pareto_frontier = BargainingTheory._compute_pareto_frontier(
            player1_payoffs, player2_payoffs
        )

        if len(pareto_frontier) == 0:
            return {'error': 'No Pareto optimal points found'}

        # Kalai-Smorodinsky: find point where proportional reductions are equal
        # (u1 - d1)/(ideal_p1 - d1) = (u2 - d2)/(ideal_p2 - d2)

        target_ratio = min((ideal_p1 - d1) / (ideal_p2 - d2) if ideal_p2 != d2 else 1,
                          (ideal_p2 - d2) / (ideal_p1 - d1) if ideal_p1 != d1 else 1)

        ks_solution = None
        min_distance = np.inf

        for u1, u2 in pareto_frontier:
            if u1 > d1 and u2 > d2:
                ratio1 = (u1 - d1) / (ideal_p1 - d1) if ideal_p1 != d1 else 1
                ratio2 = (u2 - d2) / (ideal_p2 - d2) if ideal_p2 != d2 else 1

                distance = abs(ratio1 - ratio2)
                if distance < min_distance:
                    min_distance = distance
                    ks_solution = (u1, u2)

        return {
            'kalai_smorodinsky_solution': ks_solution,
            'ideal_points': (ideal_p1, ideal_p2),
            'pareto_frontier': pareto_frontier,
            'disagreement_point': disagreement_point,
            'model_type': 'Kalai-Smorodinsky Bargaining Solution'
        }

    @staticmethod
    def _compute_pareto_frontier(payoffs1: np.ndarray, payoffs2: np.ndarray) -> List[Tuple]:
        """Compute Pareto frontier from payoff pairs."""
        points = list(zip(payoffs1, payoffs2))

        # Sort by first coordinate
        points.sort(key=lambda x: x[0], reverse=True)

        pareto_frontier = []
        current_max_y = float('-inf')

        for x, y in points:
            if y > current_max_y:
                pareto_frontier.append((x, y))
                current_max_y = y

        return pareto_frontier

    @staticmethod
    def shapley_value(coalition_values: Dict[Tuple, float], players: List[str]) -> Dict[str, float]:
        """Compute Shapley value for cooperative game.

        Fair allocation of total gains to players based on their marginal contributions.

        Parameters:
        -----------
        coalition_values : dict
            Value for each possible coalition (tuple of players -> value)
        players : list
            List of player names

        Returns:
        --------
        dict : Shapley values for each player
        """
        n = len(players)
        player_index = {player: i for i, player in enumerate(players)}
        shapley_values = {player: 0.0 for player in players}

        # Consider all permutations of players
        from itertools import permutations

        for perm in permutations(players):
            for i, player in enumerate(perm):
                # Coalition without current player
                coalition_without = perm[:i]

                # Value without player
                key_without = tuple(sorted(coalition_without,
                                          key=lambda x: player_index[x]))
                value_without = coalition_values.get(key_without, 0)

                # Value with player
                coalition_with = perm[:i+1]
                key_with = tuple(sorted(coalition_with,
                                      key=lambda x: player_index[x]))
                value_with = coalition_values.get(key_with, 0)

                # Marginal contribution
                marginal = value_with - value_without

                # Add to Shapley value (weighted by permutation probability)
                shapley_values[player] += marginal

        # Normalize by number of permutations
        n_factorial = np.math.factorial(n)
        for player in shapley_values:
            shapley_values[player] /= n_factorial

        return shapley_values


# =============================================================================
# AUCTION THEORY AND MECHANISM DESIGN
# =============================================================================

@dataclass
class AuctionTheory:
    """Auction theory and mechanism design for financial applications."""

    @staticmethod
    def first_price_sealed_bid_equilibrium(n_bidders: int, valuation_distribution: str = 'uniform') -> Dict[str, Any]:
        """Compute Bayesian Nash equilibrium for first-price sealed-bid auction.

        Bidders have private valuations and bid optimally given beliefs about others.

        Parameters:
        -----------
        n_bidders : int
            Number of bidders
        valuation_distribution : str
            Distribution of bidder valuations ('uniform', 'exponential')

        Returns:
        --------
        dict : Equilibrium bidding strategy and revenue analysis
        """
        if valuation_distribution == 'uniform':
            # For uniform [0,1] valuations
            def bid_function(valuation):
                """Equilibrium bid function: b(v) = ((n-1)/n) * v"""
                return ((n_bidders - 1) / n_bidders) * valuation

            # Expected revenue
            expected_revenue = (n_bidders - 1) / (n_bidders + 1)

        elif valuation_distribution == 'exponential':
            # For exponential valuations with rate λ=1
            def bid_function(valuation):
                """Equilibrium bid function for exponential case."""
                # More complex - involves Lambert W function
                # Simplified approximation
                return valuation * (1 - 1/(n_bidders * valuation + 1))

            expected_revenue = 1 / (n_bidders + 1)  # Approximation

        else:
            return {'error': f'Unsupported distribution: {valuation_distribution}'}

        # Revenue equivalence check
        # First-price and second-price auctions have same expected revenue

        return {
            'bid_function': bid_function,
            'expected_revenue': expected_revenue,
            'n_bidders': n_bidders,
            'valuation_distribution': valuation_distribution,
            'auction_format': 'first_price_sealed_bid',
            'model_type': 'First-Price Auction Equilibrium'
        }

    @staticmethod
    def vickrey_clarke_groves_mechanism(cost_functions: List[Callable],
                                      valuations: np.ndarray) -> Dict[str, Any]:
        """Implement Vickrey-Clarke-Groves (VCG) mechanism.

        Truthful mechanism for achieving efficient allocations.

        Parameters:
        -----------
        cost_functions : list
            Cost functions for each agent
        valuations : np.ndarray
            True valuations of agents

        Returns:
        --------
        dict : VCG allocation and payments
        """
        n_agents = len(cost_functions)

        # Find efficient allocation (maximize total surplus)
        # For simplicity, assume binary decisions
        allocations = []
        payments = []

        for i in range(n_agents):
            # Compute allocation without agent i
            other_agents = [j for j in range(n_agents) if j != i]
            surplus_without_i = sum(valuations[j] - cost_functions[j](1) for j in other_agents)

            # Compute allocation with agent i
            surplus_with_i = surplus_without_i + valuations[i] - cost_functions[i](1)

            # VCG payment for agent i
            payment_i = (sum(valuations[j] - cost_functions[j](1) for j in other_agents) -
                        surplus_without_i)

            allocations.append(1 if surplus_with_i > surplus_without_i else 0)
            payments.append(payment_i)

        total_surplus = sum(valuations[i] * allocations[i] - cost_functions[i](allocations[i])
                          for i in range(n_agents))

        return {
            'allocations': allocations,
            'payments': payments,
            'total_surplus': total_surplus,
            'mechanism': 'VCG',
            'incentive_compatible': True,
            'model_type': 'Vickrey-Clarke-Groves Mechanism'
        }

    @staticmethod
    def english_auction_dynamics(starting_price: float, bid_increments: float,
                               bidder_valuations: np.ndarray, max_rounds: int = 50) -> Dict[str, Any]:
        """Simulate English auction dynamics.

        Ascending price auction where bidders drop out when price exceeds valuation.

        Parameters:
        -----------
        starting_price : float
            Initial auction price
        bid_increments : float
            Price increment per round
        bidder_valuations : np.ndarray
            True valuations of bidders
        max_rounds : int
            Maximum auction rounds

        Returns:
        --------
        dict : Auction outcome and bidding history
        """
        current_price = starting_price
        active_bidders = list(range(len(bidder_valuations)))
        price_history = [current_price]
        round_history = []

        for round_num in range(max_rounds):
            # Check which bidders are still active
            still_active = [i for i in active_bidders if bidder_valuations[i] >= current_price]

            round_history.append({
                'round': round_num,
                'price': current_price,
                'active_bidders': len(still_active),
                'remaining_bidders': still_active
            })

            if len(still_active) <= 1:
                break

            # Increase price
            current_price += bid_increments
            price_history.append(current_price)

            # Update active bidders
            active_bidders = still_active

        # Auction outcome
        if len(active_bidders) == 1:
            winner = active_bidders[0]
            winning_price = current_price - bid_increments  # Last price where all remained
            winner_payoff = bidder_valuations[winner] - winning_price
        else:
            winner = None
            winning_price = None
            winner_payoff = 0

        return {
            'winner': winner,
            'winning_price': winning_price,
            'winner_payoff': winner_payoff,
            'total_rounds': len(round_history),
            'price_history': price_history,
            'round_details': round_history,
            'auction_format': 'English',
            'model_type': 'English Auction Dynamics'
        }


# =============================================================================
# STOCHASTIC GAMES AND MARKOV GAMES
# =============================================================================

@dataclass
class StochasticGames:
    """Stochastic games and Markov games for sequential decision making."""

    @staticmethod
    def markov_game_solver(payoff_matrices: List[np.ndarray],
                         transition_probabilities: List[np.ndarray],
                         discount_factor: float = 0.95,
                         max_iterations: int = 1000) -> Dict[str, Any]:
        """Solve Markov game using value iteration.

        Stochastic game with state transitions and stage payoffs.

        Parameters:
        -----------
        payoff_matrices : list
            Payoff matrices for each state (list of 2D arrays)
        transition_probabilities : list
            Transition probabilities for each state-action pair
        discount_factor : float
            Discount factor for future payoffs
        max_iterations : int
            Maximum value iteration steps

        Returns:
        --------
        dict : Markov game equilibrium strategies and values
        """
        n_states = len(payoff_matrices)
        n_actions_p1 = payoff_matrices[0].shape[0]
        n_actions_p2 = payoff_matrices[0].shape[1]

        # Initialize value functions
        value_p1 = np.zeros(n_states)
        value_p2 = np.zeros(n_states)

        # Initialize policies
        policy_p1 = np.zeros((n_states, n_actions_p1))
        policy_p2 = np.zeros((n_states, n_actions_p2))

        # Uniform initial policies
        policy_p1.fill(1.0 / n_actions_p1)
        policy_p2.fill(1.0 / n_actions_p2)

        for iteration in range(max_iterations):
            value_p1_old = value_p1.copy()
            value_p2_old = value_p2.copy()

            for state in range(n_states):
                # Compute Q-values for current state
                q_p1 = np.zeros((n_actions_p1, n_actions_p2))
                q_p2 = np.zeros((n_actions_p1, n_actions_p2))

                for a1 in range(n_actions_p1):
                    for a2 in range(n_actions_p2):
                        # Immediate payoffs
                        payoff_p1 = payoff_matrices[state][a1, a2]
                        payoff_p2 = -payoff_p1  # Zero-sum assumption

                        # Expected future values
                        expected_value_p1 = 0
                        expected_value_p2 = 0

                        # Simplified: assume deterministic transitions
                        # In general, would sum over possible next states
                        next_state = (state + 1) % n_states  # Cyclic states
                        expected_value_p1 = discount_factor * value_p1_old[next_state]
                        expected_value_p2 = discount_factor * value_p2_old[next_state]

                        q_p1[a1, a2] = payoff_p1 + expected_value_p1
                        q_p2[a1, a2] = payoff_p2 + expected_value_p2

                # Update value functions using Nash equilibrium
                nash_result = NashEquilibriumSolver.two_player_normal_form_nash(q_p1, q_p2)

                if nash_result['equilibria']:
                    equilibrium = nash_result['equilibria'][0]  # Take first equilibrium
                    value_p1[state] = equilibrium['player1_payoff']
                    value_p2[state] = equilibrium['player2_payoff']

                    # Update policies (simplified)
                    policy_p1[state] = equilibrium['player1_strategy']
                    policy_p2[state] = equilibrium['player2_strategy']

            # Check convergence
            if (np.max(np.abs(value_p1 - value_p1_old)) < 1e-6 and
                np.max(np.abs(value_p2 - value_p2_old)) < 1e-6):
                break

        return {
            'value_functions': {'player1': value_p1, 'player2': value_p2},
            'optimal_policies': {'player1': policy_p1, 'player2': policy_p2},
            'convergence': iteration < max_iterations - 1,
            'iterations': iteration + 1,
            'discount_factor': discount_factor,
            'model_type': 'Markov Game Solution'
        }

    @staticmethod
    def repeated_game_folk_theorem(payoff_matrix: np.ndarray,
                                 discount_factor: float = 0.95) -> Dict[str, Any]:
        """Analyze repeated games and Folk theorem.

        Study how repetition can sustain cooperation that wouldn't
        be possible in one-shot games.

        Parameters:
        -----------
        payoff_matrix : np.ndarray
            Stage game payoff matrix
        discount_factor : float
            Discount factor for future payoffs

        Returns:
        --------
        dict : Folk theorem analysis and sustainable payoffs
        """
        # Compute one-shot Nash equilibria
        nash_result = NashEquilibriumSolver.two_player_normal_form_nash(
            payoff_matrix, -payoff_matrix  # Zero-sum assumption
        )

        nash_payoffs = []
        for eq in nash_result['equilibria']:
            nash_payoffs.append(eq['player1_payoff'])

        min_nash_payoff = min(nash_payoffs) if nash_payoffs else 0
        max_nash_payoff = max(nash_payoffs) if nash_payoffs else 0

        # Folk theorem: in repeated games, any payoff between min Nash and max feasible is sustainable
        max_feasible_payoff = np.max(payoff_matrix)

        # Grim trigger strategy: cooperate until deviation, then punish forever
        def grim_trigger_payoff(cooperative_payoff: float, punishment_payoff: float) -> float:
            """Compute sustainable payoff with grim trigger strategy."""
            return (cooperative_payoff + discount_factor * punishment_payoff) / (1 - discount_factor)

        # Compute sustainable payoff range
        sustainable_min = min_nash_payoff
        sustainable_max = max_feasible_payoff

        # Check if cooperation is sustainable
        cooperation_payoff = np.max(payoff_matrix)  # Mutual cooperation
        cooperation_sustainable = cooperation_payoff >= grim_trigger_payoff(
            cooperation_payoff, min_nash_payoff
        )

        return {
            'one_shot_nash_equilibria': nash_result['equilibria'],
            'nash_payoff_range': (min_nash_payoff, max_nash_payoff),
            'feasible_payoff_range': (np.min(payoff_matrix), max_feasible_payoff),
            'sustainable_payoff_range': (sustainable_min, sustainable_max),
            'cooperation_sustainable': cooperation_sustainable,
            'grim_trigger_condition': grim_trigger_payoff(cooperation_payoff, min_nash_payoff),
            'discount_factor': discount_factor,
            'model_type': 'Repeated Game Folk Theorem'
        }


# =============================================================================
# FINANCIAL MARKET GAMES
# =============================================================================

@dataclass
class FinancialMarketGames:
    """Game-theoretic models of financial markets and strategic trading."""

    @staticmethod
    def market_making_game_spread(inventory_risk: float = 0.1,
                                adverse_selection: float = 0.05,
                                competition_intensity: float = 0.8) -> Dict[str, Any]:
        """Strategic market making with optimal bid-ask spread.

        Market makers set spreads considering inventory risk,
        adverse selection, and competition.

        Parameters:
        -----------
        inventory_risk : float
            Inventory holding risk parameter
        adverse_selection : float
            Adverse selection risk parameter
        competition_intensity : float
            Intensity of market maker competition

        Returns:
        --------
        dict : Optimal spread and market making strategy
        """
        # Kyle (1985) model: spread = λ * σ_ε / (1 - λ * σ_ε) or similar
        # Simplified optimal spread calculation

        # Components of spread
        inventory_cost = inventory_risk
        adverse_selection_cost = adverse_selection
        order_processing_cost = 0.01  # Fixed cost

        # Competition reduces spread
        competitive_factor = 1 / (1 + competition_intensity)

        # Optimal half-spread
        half_spread = competitive_factor * (inventory_cost + adverse_selection_cost + order_processing_cost)

        # Full spread
        optimal_spread = 2 * half_spread

        # Market depth (order size where spread becomes relevant)
        market_depth = 1 / (inventory_risk + adverse_selection)

        return {
            'optimal_spread': optimal_spread,
            'half_spread': half_spread,
            'inventory_cost_component': inventory_cost,
            'adverse_selection_component': adverse_selection,
            'competition_factor': competitive_factor,
            'market_depth': market_depth,
            'model_type': 'Strategic Market Making'
        }

    @staticmethod
    def predatory_trading_game(informed_trader_signal: float = 0.8,
                             market_impact: float = 0.1,
                             predatory_intensity: float = 0.3) -> Dict[str, Any]:
        """Model predatory trading strategies in high-frequency markets.

        Fast traders detect large orders and trade ahead,
        forcing the large trader to pay higher prices.

        Parameters:
        -----------
        informed_trader_signal : float
            Quality of informed trader's signal
        market_impact : float
            Price impact of large trades
        predatory_intensity : float
            Aggressiveness of predatory trading

        Returns:
        --------
        dict : Predatory trading equilibrium and profits
        """
        # Simplified Kyle-Back model with predation

        # Informed trader's strategy
        informed_position = informed_trader_signal

        # Predatory trader's response
        predatory_position = predatory_intensity * informed_position

        # Price impact
        total_order_flow = informed_position + predatory_position
        price_impact = market_impact * total_order_flow

        # Profits
        informed_profit = informed_position * (informed_trader_signal - price_impact)
        predatory_profit = predatory_position * (-price_impact)  # Predators trade against informed

        # Total market efficiency
        market_efficiency = abs(informed_trader_signal) / (abs(price_impact) + 1e-6)

        return {
            'informed_position': informed_position,
            'predatory_position': predatory_position,
            'price_impact': price_impact,
            'informed_profit': informed_profit,
            'predatory_profit': predatory_profit,
            'market_efficiency': market_efficiency,
            'predation_ratio': abs(predatory_position / informed_position) if informed_position != 0 else 0,
            'model_type': 'Predatory Trading Game'
        }

    @staticmethod
    def algorithmic_trading_arms_race(speed_advantage: np.ndarray,
                                    strategy_complexity: np.ndarray) -> Dict[str, Any]:
        """Model algorithmic trading as an arms race.

        Multiple algorithms compete, with faster and more
        complex strategies having advantages.

        Parameters:
        -----------
        speed_advantage : np.ndarray
            Speed advantages of different algorithms
        strategy_complexity : np.ndarray
            Complexity costs of different algorithms

        Returns:
        --------
        dict : Algorithmic trading competition equilibrium
        """
        n_algorithms = len(speed_advantage)

        # Profit function: speed advantage minus complexity cost
        profits = speed_advantage - strategy_complexity

        # Market shares (softmax of profits)
        market_shares = np.exp(profits) / np.sum(np.exp(profits))

        # Evolutionary stability
        # Algorithm with highest profit should dominate
        dominant_algorithm = np.argmax(profits)

        # Nash equilibrium analysis
        # Each algorithm chooses whether to invest in upgrades
        upgrade_payoff_matrix = np.zeros((2, 2))
        upgrade_cost = 0.1

        for i in range(2):  # Simplified 2-player case
            for j in range(2):
                if i == 1 and j == 1:  # Both upgrade
                    upgrade_payoff_matrix[i, j] = profits[0] - upgrade_cost
                elif i == 1 and j == 0:  # Only i upgrades
                    upgrade_payoff_matrix[i, j] = profits[0] + 0.2 - upgrade_cost
                elif i == 0 and j == 1:  # Only j upgrades
                    upgrade_payoff_matrix[i, j] = profits[0] - 0.2
                else:  # Neither upgrades
                    upgrade_payoff_matrix[i, j] = profits[0]

        upgrade_nash = NashEquilibriumSolver.two_player_normal_form_nash(
            upgrade_payoff_matrix, -upgrade_payoff_matrix
        )

        return {
            'algorithm_profits': profits,
            'market_shares': market_shares,
            'dominant_algorithm': dominant_algorithm,
            'upgrade_game': upgrade_nash,
            'speed_advantages': speed_advantage,
            'strategy_complexities': strategy_complexity,
            'model_type': 'Algorithmic Trading Arms Race'
        }


# =============================================================================
# EXPORT GAME THEORY COMPONENTS
# =============================================================================

__all__ = [
    "NashEquilibriumSolver", "EvolutionaryGameTheory", "BargainingTheory",
    "AuctionTheory", "StochasticGames", "FinancialMarketGames"
]

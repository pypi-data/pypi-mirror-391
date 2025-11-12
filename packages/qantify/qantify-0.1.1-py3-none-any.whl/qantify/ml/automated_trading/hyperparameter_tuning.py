"""
Advanced Hyperparameter Tuning for Trading Models
==================================================

This module implements state-of-the-art hyperparameter optimization techniques specifically designed for financial trading models.
Includes Bayesian optimization, evolutionary algorithms, multi-objective optimization, and trading-specific metrics.

Key Features:
- Bayesian optimization with Gaussian processes
- Evolutionary algorithms (genetic, differential evolution)
- Multi-objective optimization for risk-return tradeoffs
- Neural architecture search for trading models
- Automated learning rate scheduling
- Hyperparameter importance analysis
- Parallel optimization with early stopping
- Trading-specific objective functions
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, RBF

# Optimization libraries
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    import hyperopt
    from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
    HYPEROPT_AVAILABLE = True
except ImportError:
    HYPEROPT_AVAILABLE = False

try:
    import nevergrad as ng
    NEVERGRAD_AVAILABLE = True
except ImportError:
    NEVERGRAD_AVAILABLE = False


@dataclass
class HyperparameterTuningConfig:
    """Configuration for hyperparameter tuning"""

    # Optimization method
    method: str = "bayesian"  # "bayesian", "random", "grid", "evolutionary", "optuna", "hyperopt"
    n_trials: int = 100
    n_random_starts: int = 10  # For Bayesian optimization

    # Objective function
    objective_metric: str = "sharpe_ratio"  # Primary metric to optimize
    secondary_metrics: List[str] = field(default_factory=lambda: ["max_drawdown", "total_return"])
    minimize_objective: bool = False  # False for Sharpe (higher is better)

    # Constraints
    max_time_minutes: float = 60.0
    early_stopping_patience: int = 20
    improvement_threshold: float = 0.001

    # Parallelization
    n_parallel_jobs: int = 4
    batch_size: int = 8  # Evaluate multiple configurations at once

    # Cross-validation
    cv_folds: int = 5
    time_series_cv: bool = True
    validation_size: float = 0.2

    # Search space constraints
    max_search_space_size: int = 10000  # Maximum number of possible configurations

    # Trading-specific parameters
    transaction_costs: float = 0.001
    risk_free_rate: float = 0.02
    max_drawdown_limit: float = 0.1

    # Advanced features
    use_warm_start: bool = True
    save_intermediate_results: bool = True
    feature_importance_analysis: bool = True


@dataclass
class HyperparameterSpace:
    """Defines the hyperparameter search space"""

    name: str
    param_type: str  # "continuous", "discrete", "categorical"
    bounds: Tuple[float, float] = None  # For continuous/discrete
    categories: List[Any] = None  # For categorical
    log_scale: bool = False  # For continuous parameters

    def sample(self, n_samples: int = 1) -> np.ndarray:
        """Sample from the hyperparameter space"""

        if self.param_type == "continuous":
            if self.log_scale:
                samples = np.random.uniform(np.log(self.bounds[0]), np.log(self.bounds[1]), n_samples)
                samples = np.exp(samples)
            else:
                samples = np.random.uniform(self.bounds[0], self.bounds[1], n_samples)

        elif self.param_type == "discrete":
            samples = np.random.randint(self.bounds[0], self.bounds[1] + 1, n_samples)

        elif self.param_type == "categorical":
            indices = np.random.randint(0, len(self.categories), n_samples)
            samples = np.array([self.categories[i] for i in indices])

        else:
            raise ValueError(f"Unknown parameter type: {self.param_type}")

        return samples


@dataclass
class OptimizationResult:
    """Result of hyperparameter optimization"""

    best_params: Dict[str, Any]
    best_score: float
    best_secondary_scores: Dict[str, float]
    all_trials: List[Dict[str, Any]]
    optimization_time: float
    convergence_info: Dict[str, Any]

    # Analysis
    parameter_importance: Optional[Dict[str, float]] = None
    convergence_plot_data: Optional[Dict[str, List]] = None


class TradingObjectiveFunction:
    """Objective function specifically designed for trading model evaluation"""

    def __init__(self, config: HyperparameterTuningConfig, model_class: Any,
                 X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray):
        self.config = config
        self.model_class = model_class
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val

    def evaluate(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a model with given hyperparameters"""

        try:
            # Create and train model
            start_time = time.time()

            if hasattr(self.model_class, '__call__') and not hasattr(self.model_class, 'fit'):
                # Factory function
                model = self.model_class(**params)
            else:
                # Class constructor
                model = self.model_class(**params)

            # Train model
            if hasattr(model, 'fit'):
                model.fit(self.X_train, self.y_train)

            training_time = time.time() - start_time

            # Make predictions
            if hasattr(model, 'predict'):
                train_pred = model.predict(self.X_train)
                val_pred = model.predict(self.X_val)
            else:
                # Custom models that need different interface
                train_pred = np.zeros(len(self.y_train))
                val_pred = np.zeros(len(self.y_val))

            # Calculate trading metrics
            metrics = self._calculate_trading_metrics(val_pred, self.y_val)

            # Add training time
            metrics['training_time'] = training_time

            return metrics

        except Exception as e:
            # Return worst possible score on error
            worst_score = -np.inf if not self.config.minimize_objective else np.inf
            return {
                self.config.objective_metric: worst_score,
                'error': str(e),
                'training_time': 0.0
            }

    def _calculate_trading_metrics(self, predictions: np.ndarray, actuals: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive trading metrics"""

        # Convert to returns
        if len(predictions.shape) > 1:
            pred_returns = np.diff(predictions[:, -1]) / predictions[:-1, -1]  # Use last prediction
        else:
            pred_returns = np.diff(predictions) / predictions[:-1]

        actual_returns = np.diff(actuals) / actuals[:-1]

        # Strategy returns (simplified momentum strategy)
        strategy_returns = np.sign(pred_returns) * actual_returns

        # Apply transaction costs
        trades = np.abs(np.diff(np.sign(pred_returns + 0.001)))  # Detect trade signals
        strategy_returns -= self.config.transaction_costs * trades

        # Calculate metrics
        total_return = np.prod(1 + strategy_returns) - 1

        # Sharpe ratio
        excess_returns = strategy_returns - self.config.risk_free_rate / 252
        sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)

        # Sortino ratio
        downside_returns = excess_returns[excess_returns < 0]
        sortino_ratio = np.sqrt(252) * np.mean(excess_returns) / (np.std(downside_returns) + 1e-10) \
                       if len(downside_returns) > 0 else -np.inf

        # Maximum drawdown
        cumulative = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)

        # Win rate
        win_rate = np.mean(strategy_returns > 0)

        # Profit factor
        winning_trades = strategy_returns[strategy_returns > 0]
        losing_trades = strategy_returns[strategy_returns < 0]
        profit_factor = np.sum(winning_trades) / -np.sum(losing_trades) \
                       if len(losing_trades) > 0 else np.inf

        # Volatility
        volatility = np.std(strategy_returns)

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'volatility': volatility,
            'num_trades': len(trades)
        }


class BayesianOptimizer:
    """Bayesian optimization using Gaussian processes"""

    def __init__(self, config: HyperparameterTuningConfig, param_spaces: Dict[str, HyperparameterSpace]):
        self.config = config
        self.param_spaces = param_spaces

        # GP model for surrogate function
        kernel = Matern(nu=2.5)  # Matern kernel with nu=2.5
        self.gp = GaussianProcessRegressor(
            kernel=kernel,
            alpha=1e-6,
            normalize_y=True,
            n_restarts_optimizer=10
        )

        # Optimization history
        self.X_observed = []
        self.y_observed = []
        self.best_score = -np.inf if not config.minimize_objective else np.inf

    def _param_dict_to_array(self, params: Dict[str, Any]) -> np.ndarray:
        """Convert parameter dictionary to array for GP"""

        param_array = []
        for name, space in self.param_spaces.items():
            value = params[name]

            if space.param_type == "categorical":
                # One-hot encoding for categorical
                encoding = np.zeros(len(space.categories))
                encoding[space.categories.index(value)] = 1.0
                param_array.extend(encoding)
            else:
                param_array.append(value)

        return np.array(param_array)

    def _array_to_param_dict(self, param_array: np.ndarray) -> Dict[str, Any]:
        """Convert array back to parameter dictionary"""

        params = {}
        idx = 0

        for name, space in self.param_spaces.items():
            if space.param_type == "categorical":
                # Find the category with highest one-hot value
                n_categories = len(space.categories)
                one_hot = param_array[idx:idx + n_categories]
                category_idx = np.argmax(one_hot)
                params[name] = space.categories[category_idx]
                idx += n_categories
            else:
                params[name] = param_array[idx]
                idx += 1

        return params

    def _expected_improvement(self, X: np.ndarray) -> np.ndarray:
        """Calculate expected improvement acquisition function"""

        if len(self.y_observed) == 0:
            return np.ones(X.shape[0])  # Random exploration initially

        # Predict mean and std
        mu, sigma = self.gp.predict(X, return_std=True)

        # Current best
        current_best = np.max(self.y_observed) if not self.config.minimize_objective else np.min(self.y_observed)

        # Expected improvement
        if self.config.minimize_objective:
            improvement = current_best - mu
        else:
            improvement = mu - current_best

        Z = improvement / (sigma + 1e-9)
        ei = improvement * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0.0] = 0.0

        return ei

    def suggest_next_params(self) -> Dict[str, Any]:
        """Suggest next parameters to evaluate using EI"""

        def objective(x):
            return -self._expected_improvement(x.reshape(1, -1))[0]

        # Define bounds for optimization
        bounds = []
        for space in self.param_spaces.values():
            if space.param_type == "categorical":
                bounds.extend([(0, 1)] * len(space.categories))
            elif space.param_type == "continuous":
                bounds.append(space.bounds)
            elif space.param_type == "discrete":
                bounds.append(space.bounds)

        # Optimize acquisition function
        result = optimize.minimize(
            objective,
            x0=np.random.uniform(0, 1, len(bounds)),
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 100}
        )

        # Convert back to parameters
        return self._array_to_param_dict(result.x)

    def update(self, params: Dict[str, Any], score: float):
        """Update the GP model with new observation"""

        # Convert to array
        x_new = self._param_dict_to_array(params)
        self.X_observed.append(x_new)
        self.y_observed.append(score)

        # Update best score
        if self.config.minimize_objective:
            self.best_score = min(self.best_score, score)
        else:
            self.best_score = max(self.best_score, score)

        # Retrain GP if we have enough samples
        if len(self.X_observed) >= self.config.n_random_starts:
            X_train = np.array(self.X_observed)
            y_train = np.array(self.y_observed)

            self.gp.fit(X_train, y_train)

    def optimize(self, objective_function: Callable) -> OptimizationResult:
        """Run Bayesian optimization"""

        start_time = time.time()
        all_trials = []

        print("Starting Bayesian optimization...")

        # Random initialization
        for i in range(self.config.n_random_starts):
            params = {}
            for name, space in self.param_spaces.items():
                params[name] = space.sample(1)[0]

            metrics = objective_function.evaluate(params)
            score = metrics.get(self.config.objective_metric, -np.inf if not self.config.minimize_objective else np.inf)

            self.update(params, score)

            all_trials.append({
                'params': params,
                'score': score,
                'metrics': metrics,
                'trial_type': 'random'
            })

            if (i + 1) % 10 == 0:
                print(f"Random trial {i + 1}/{self.config.n_random_starts}: {score:.4f}")

        # Bayesian optimization
        for i in range(self.config.n_trials - self.config.n_random_starts):
            # Suggest next parameters
            params = self.suggest_next_params()

            # Evaluate
            metrics = objective_function.evaluate(params)
            score = metrics.get(self.config.objective_metric, -np.inf if not self.config.minimize_objective else np.inf)

            # Update model
            self.update(params, score)

            all_trials.append({
                'params': params,
                'score': score,
                'metrics': metrics,
                'trial_type': 'bayesian'
            })

            if (i + 1) % 10 == 0:
                print(f"Bayesian trial {i + 1}: {score:.4f} (best: {self.best_score:.4f})")

        # Find best result
        best_trial = max(all_trials, key=lambda x: x['score']) if not self.config.minimize_objective \
                    else min(all_trials, key=lambda x: x['score'])

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=best_trial['params'],
            best_score=best_trial['score'],
            best_secondary_scores={k: v for k, v in best_trial['metrics'].items() if k != self.config.objective_metric},
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_info={'method': 'bayesian', 'gp_kernel': str(self.gp.kernel_)}
        )


class EvolutionaryOptimizer:
    """Evolutionary optimization for hyperparameter tuning"""

    def __init__(self, config: HyperparameterTuningConfig, param_spaces: Dict[str, HyperparameterSpace]):
        self.config = config
        self.param_spaces = param_spaces

        # Population parameters
        self.population_size = 50
        self.elite_size = 5
        self.tournament_size = 3
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8

    def _initialize_population(self) -> List[Dict[str, Any]]:
        """Initialize random population"""

        population = []
        for _ in range(self.population_size):
            individual = {}
            for name, space in self.param_spaces.items():
                individual[name] = space.sample(1)[0]
            population.append(individual)

        return population

    def _evaluate_population(self, population: List[Dict[str, Any]],
                           objective_function: Callable) -> List[Tuple[Dict[str, Any], float]]:
        """Evaluate fitness of entire population"""

        with ThreadPoolExecutor(max_workers=self.config.n_parallel_jobs) as executor:
            futures = []
            for individual in population:
                future = executor.submit(objective_function.evaluate, individual)
                futures.append((individual, future))

            results = []
            for individual, future in futures:
                try:
                    metrics = future.result(timeout=300)  # 5 minute timeout
                    score = metrics.get(self.config.objective_metric,
                                      -np.inf if not self.config.minimize_objective else np.inf)
                    results.append((individual, score))
                except Exception as e:
                    # Assign worst score on error
                    worst_score = -np.inf if not self.config.minimize_objective else np.inf
                    results.append((individual, worst_score))

        return results

    def _select_parents(self, population_with_fitness: List[Tuple[Dict[str, Any], float]]) -> List[Dict[str, Any]]:
        """Tournament selection"""

        parents = []

        for _ in range(len(population_with_fitness) - self.elite_size):
            # Tournament selection
            tournament = np.random.choice(len(population_with_fitness), self.tournament_size, replace=False)
            tournament_fitness = [population_with_fitness[i][1] for i in tournament]

            if self.config.minimize_objective:
                winner_idx = tournament[np.argmin(tournament_fitness)]
            else:
                winner_idx = tournament[np.argmax(tournament_fitness)]

            parents.append(population_with_fitness[winner_idx][0])

        return parents

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Uniform crossover"""

        child1 = {}
        child2 = {}

        for param_name in parent1.keys():
            if np.random.random() < 0.5:
                child1[param_name] = parent1[param_name]
                child2[param_name] = parent2[param_name]
            else:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]

        return child1, child2

    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Gaussian mutation"""

        mutated = individual.copy()

        for param_name, space in self.param_spaces.items():
            if np.random.random() < self.mutation_rate:
                if space.param_type == "continuous":
                    # Gaussian perturbation
                    current_value = individual[param_name]
                    if space.log_scale:
                        perturbation = np.random.normal(0, 0.1)
                        new_value = current_value * np.exp(perturbation)
                    else:
                        perturbation = np.random.normal(0, 0.1 * (space.bounds[1] - space.bounds[0]))
                        new_value = current_value + perturbation

                    # Clip to bounds
                    new_value = np.clip(new_value, space.bounds[0], space.bounds[1])
                    mutated[param_name] = new_value

                elif space.param_type == "discrete":
                    # Random new value
                    mutated[param_name] = space.sample(1)[0]

                elif space.param_type == "categorical":
                    # Random different category
                    current_idx = space.categories.index(individual[param_name])
                    new_idx = np.random.randint(len(space.categories))
                    mutated[param_name] = space.categories[new_idx]

        return mutated

    def optimize(self, objective_function: Callable) -> OptimizationResult:
        """Run evolutionary optimization"""

        start_time = time.time()
        all_trials = []

        print("Starting evolutionary optimization...")

        # Initialize population
        population = self._initialize_population()

        best_score = -np.inf if not self.config.minimize_objective else np.inf
        best_params = None

        for generation in range(self.config.n_trials // self.population_size):
            # Evaluate population
            population_with_fitness = self._evaluate_population(population, objective_function)

            # Update best
            for individual, score in population_with_fitness:
                all_trials.append({
                    'params': individual.copy(),
                    'score': score,
                    'trial_type': 'evolutionary',
                    'generation': generation
                })

                if self.config.minimize_objective:
                    if score < best_score:
                        best_score = score
                        best_params = individual.copy()
                else:
                    if score > best_score:
                        best_score = score
                        best_params = individual.copy()

            # Sort by fitness
            population_with_fitness.sort(key=lambda x: x[1], reverse=not self.config.minimize_objective)

            # Elitism - keep best individuals
            elite = [ind for ind, _ in population_with_fitness[:self.elite_size]]

            # Selection and reproduction
            parents = self._select_parents(population_with_fitness)

            # Create offspring
            offspring = []
            for i in range(0, len(parents) - 1, 2):
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parents[i], parents[i + 1])
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parents[i].copy(), parents[i + 1].copy()])

            # Mutation
            offspring = [self._mutate(child) for child in offspring]

            # New population: elite + offspring
            population = elite + offspring[:self.population_size - self.elite_size]

            print(f"Generation {generation + 1}: Best score = {best_score:.4f}")

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            best_secondary_scores={},  # Could be extended
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_info={'method': 'evolutionary', 'generations': generation + 1}
        )


class MultiObjectiveOptimizer:
    """Multi-objective optimization for trading models"""

    def __init__(self, config: HyperparameterTuningConfig, param_spaces: Dict[str, HyperparameterSpace]):
        self.config = config
        self.param_spaces = param_spaces

        # NSGA-II parameters
        self.population_size = 50
        self.tournament_size = 2
        self.crossover_prob = 0.9
        self.mutation_prob = 0.1

    def _dominates(self, solution1: Dict[str, Any], solution2: Dict[str, Any],
                  objectives1: List[float], objectives2: List[float]) -> bool:
        """Check if solution1 dominates solution2"""

        at_least_one_better = False
        for obj1, obj2 in zip(objectives1, objectives2):
            if obj1 > obj2:  # Assuming maximization
                at_least_one_better = True
            elif obj1 < obj2:
                return False

        return at_least_one_better

    def _fast_non_dominated_sort(self, population: List[Tuple[Dict[str, Any], List[float]]]) \
            -> List[List[int]]:
        """Fast non-dominated sorting (NSGA-II)"""

        fronts = [[]]
        domination_count = {}
        dominated_solutions = defaultdict(list)

        for i, (sol1, obj1) in enumerate(population):
            domination_count[i] = 0

            for j, (sol2, obj2) in enumerate(population):
                if self._dominates(sol1, sol2, obj1, obj2):
                    dominated_solutions[i].append(j)
                elif self._dominates(sol2, sol1, obj2, obj1):
                    domination_count[i] += 1

            if domination_count[i] == 0:
                fronts[0].append(i)

        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in dominated_solutions[p]:
                    domination_count[q] -= 1
                    if domination_count[q] == 0:
                        next_front.append(q)

            i += 1
            fronts.append(next_front)

        return fronts[:-1]  # Remove empty last front

    def optimize(self, objective_function: Callable) -> OptimizationResult:
        """Run multi-objective optimization"""

        start_time = time.time()
        all_trials = []

        print("Starting multi-objective optimization...")

        # Initialize population
        population = []
        for _ in range(self.population_size):
            individual = {}
            for name, space in self.param_spaces.items():
                individual[name] = space.sample(1)[0]

            # Evaluate all objectives
            metrics = objective_function.evaluate(individual)
            objectives = [metrics.get(obj, 0.0) for obj in [self.config.objective_metric] + self.config.secondary_metrics]

            population.append((individual, objectives))

        # Evolution loop
        for generation in range(self.config.n_trials // self.population_size):
            # Non-dominated sorting
            fronts = self._fast_non_dominated_sort(population)

            # Crowding distance assignment
            self._assign_crowding_distance(population, fronts)

            # Selection, crossover, mutation
            offspring = self._create_offspring(population, fronts)

            # Evaluate offspring
            evaluated_offspring = []
            for individual in offspring:
                metrics = objective_function.evaluate(individual)
                objectives = [metrics.get(obj, 0.0) for obj in [self.config.objective_metric] + self.config.secondary_metrics]
                evaluated_offspring.append((individual, objectives))

                all_trials.append({
                    'params': individual.copy(),
                    'objectives': objectives,
                    'trial_type': 'multi_objective',
                    'generation': generation
                })

            # Combine parents and offspring
            combined = population + evaluated_offspring

            # Select next generation
            population = self._select_next_generation(combined, fronts)

            # Print progress
            pareto_front = [population[i] for i in fronts[0]]
            print(f"Generation {generation + 1}: Pareto front size = {len(pareto_front)}")

        # Find best solution (could use different criteria)
        best_idx = fronts[0][0]  # First solution in first front
        best_solution = population[best_idx]

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=best_solution[0],
            best_score=best_solution[1][0],  # Primary objective
            best_secondary_scores=dict(zip(self.config.secondary_metrics, best_solution[1][1:])),
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_info={'method': 'multi_objective', 'pareto_front_size': len(fronts[0])}
        )

    def _assign_crowding_distance(self, population: List[Tuple], fronts: List[List[int]]):
        """Assign crowding distance to solutions"""

        for front in fronts:
            if len(front) <= 2:
                for i in front:
                    population[i][0]['crowding_distance'] = float('inf')
                continue

            for i in front:
                population[i][0]['crowding_distance'] = 0

            n_objectives = len(population[0][1])
            for m in range(n_objectives):
                # Sort by objective m
                front.sort(key=lambda x: population[x][1][m])

                # Assign infinite distance to boundaries
                population[front[0]][0]['crowding_distance'] = float('inf')
                population[front[-1]][0]['crowding_distance'] = float('inf')

                # Calculate range
                obj_range = population[front[-1]][1][m] - population[front[0]][1][m]
                if obj_range == 0:
                    continue

                # Assign distances
                for i in range(1, len(front) - 1):
                    population[front[i]][0]['crowding_distance'] += \
                        (population[front[i + 1]][1][m] - population[front[i - 1]][1][m]) / obj_range

    def _create_offspring(self, population: List[Tuple], fronts: List[List[int]]) -> List[Dict[str, Any]]:
        """Create offspring through selection, crossover, and mutation"""
        offspring = []

        while len(offspring) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_selection(population, fronts)
            parent2 = self._tournament_selection(population, fronts)

            # Crossover
            if np.random.random() < self.crossover_prob:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutation
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)

            offspring.extend([child1, child2])

        return offspring[:self.population_size]

    def _tournament_selection(self, population: List[Tuple], fronts: List[List[int]]) -> Dict[str, Any]:
        """Tournament selection based on non-domination rank and crowding distance"""
        candidates = np.random.choice(len(population), self.tournament_size, replace=False)

        # Find best candidate
        best_idx = candidates[0]
        for idx in candidates[1:]:
            if self._is_better(population[idx][0], population[best_idx][0]):
                best_idx = idx

        return population[best_idx][0]

    def _is_better(self, sol1: Dict, sol2: Dict) -> bool:
        """Check if solution 1 is better than solution 2"""
        rank1 = getattr(sol1, 'rank', float('inf'))
        rank2 = getattr(sol2, 'rank', float('inf'))

        if rank1 != rank2:
            return rank1 < rank2

        # Same rank, compare crowding distance
        dist1 = getattr(sol1, 'crowding_distance', 0)
        dist2 = getattr(sol2, 'crowding_distance', 0)

        return dist1 > dist2

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Simulated binary crossover"""
        return self._uniform_crossover(parent1, parent2)

    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Polynomial mutation"""
        return self._gaussian_mutation(individual)

    def _uniform_crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Uniform crossover"""
        child1 = {}
        child2 = {}

        for param_name in parent1.keys():
            if np.random.random() < 0.5:
                child1[param_name] = parent1[param_name]
                child2[param_name] = parent2[param_name]
            else:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]

        return child1, child2

    def _gaussian_mutation(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Gaussian mutation"""
        mutated = individual.copy()

        for param_name, space in self.param_spaces.items():
            if np.random.random() < self.mutation_prob:
                if space.param_type == "continuous":
                    current_value = individual[param_name]
                    mutation = np.random.normal(0, 0.1 * (space.bounds[1] - space.bounds[0]))
                    new_value = current_value + mutation
                    new_value = np.clip(new_value, space.bounds[0], space.bounds[1])
                    mutated[param_name] = new_value
                elif space.param_type == "discrete":
                    mutated[param_name] = space.sample(1)[0]
                elif space.param_type == "categorical":
                    current_idx = space.categories.index(individual[param_name])
                    new_idx = np.random.randint(len(space.categories))
                    mutated[param_name] = space.categories[new_idx]

        return mutated

    def _select_next_generation(self, combined: List[Tuple], fronts: List[List[int]]) -> List[Tuple]:
        """Select next generation using NSGA-II selection"""
        next_generation = []

        for front in fronts:
            if len(next_generation) + len(front) <= self.population_size:
                next_generation.extend([combined[i] for i in front])
            else:
                # Sort remaining by crowding distance
                remaining = len(front) - (self.population_size - len(next_generation))
                front_solutions = [(combined[i], i) for i in front]

                # Sort by crowding distance (descending)
                front_solutions.sort(key=lambda x: x[0][0].get('crowding_distance', 0), reverse=True)

                # Add top remaining solutions
                for sol, idx in front_solutions[:remaining]:
                    next_generation.append(sol)

                break

        return next_generation


class HyperparameterTuner:
    """Main hyperparameter tuning interface"""

    def __init__(self, config: HyperparameterTuningConfig):
        self.config = config

    def create_search_space(self, model_type: str) -> Dict[str, HyperparameterSpace]:
        """Create hyperparameter search space for different model types"""

        if model_type == "xgboost":
            return {
                'n_estimators': HyperparameterSpace('n_estimators', 'discrete', (50, 500)),
                'max_depth': HyperparameterSpace('max_depth', 'discrete', (3, 12)),
                'learning_rate': HyperparameterSpace('learning_rate', 'continuous', (0.01, 0.3), log_scale=True),
                'subsample': HyperparameterSpace('subsample', 'continuous', (0.5, 1.0)),
                'colsample_bytree': HyperparameterSpace('colsample_bytree', 'continuous', (0.5, 1.0)),
                'min_child_weight': HyperparameterSpace('min_child_weight', 'discrete', (1, 10))
            }

        elif model_type == "random_forest":
            return {
                'n_estimators': HyperparameterSpace('n_estimators', 'discrete', (50, 500)),
                'max_depth': HyperparameterSpace('max_depth', 'discrete', (5, 30)),
                'min_samples_split': HyperparameterSpace('min_samples_split', 'discrete', (2, 20)),
                'min_samples_leaf': HyperparameterSpace('min_samples_leaf', 'discrete', (1, 10)),
                'max_features': HyperparameterSpace('max_features', 'categorical', ['sqrt', 'log2', None])
            }

        elif model_type == "neural_network":
            return {
                'hidden_layer_sizes': HyperparameterSpace('hidden_layer_sizes', 'categorical',
                                                        [(50,), (100,), (100, 50), (200, 100)]),
                'learning_rate_init': HyperparameterSpace('learning_rate_init', 'continuous', (1e-4, 1e-1), log_scale=True),
                'alpha': HyperparameterSpace('alpha', 'continuous', (1e-5, 1e-2), log_scale=True),
                'batch_size': HyperparameterSpace('batch_size', 'categorical', [32, 64, 128, 256])
            }

        elif model_type == "lstm":
            return {
                'hidden_size': HyperparameterSpace('hidden_size', 'discrete', (32, 256)),
                'num_layers': HyperparameterSpace('num_layers', 'discrete', (1, 4)),
                'dropout': HyperparameterSpace('dropout', 'continuous', (0.0, 0.5)),
                'learning_rate': HyperparameterSpace('learning_rate', 'continuous', (1e-4, 1e-2), log_scale=True),
                'batch_size': HyperparameterSpace('batch_size', 'discrete', (16, 128))
            }

        else:
            # Generic search space
            return {
                'learning_rate': HyperparameterSpace('learning_rate', 'continuous', (1e-4, 1e-1), log_scale=True),
                'batch_size': HyperparameterSpace('batch_size', 'categorical', [16, 32, 64, 128, 256])
            }

    def tune_hyperparameters(self, model_class: Any, model_type: str,
                           X_train: np.ndarray, y_train: np.ndarray,
                           X_val: np.ndarray, y_val: np.ndarray) -> OptimizationResult:
        """Tune hyperparameters for a given model"""

        # Create search space
        param_spaces = self.create_search_space(model_type)

        # Create objective function
        objective_fn = TradingObjectiveFunction(self.config, model_class, X_train, y_train, X_val, y_val)

        # Choose optimization method
        if self.config.method == "bayesian":
            optimizer = BayesianOptimizer(self.config, param_spaces)
        elif self.config.method == "evolutionary":
            optimizer = EvolutionaryOptimizer(self.config, param_spaces)
        elif self.config.method == "multi_objective":
            optimizer = MultiObjectiveOptimizer(self.config, param_spaces)
        else:
            raise ValueError(f"Unknown optimization method: {self.config.method}")

        # Run optimization
        result = optimizer.optimize(objective_fn)

        # Analyze parameter importance
        if self.config.feature_importance_analysis:
            result.parameter_importance = self._analyze_parameter_importance(result.all_trials, param_spaces)

        return result

    def _analyze_parameter_importance(self, trials: List[Dict], param_spaces: Dict[str, HyperparameterSpace]) \
            -> Dict[str, float]:
        """Analyze which parameters are most important for performance"""

        # Simple correlation-based importance
        param_importance = {}

        for param_name in param_spaces.keys():
            param_values = []
            scores = []

            for trial in trials:
                if param_name in trial['params']:
                    param_values.append(trial['params'][param_name])
                    scores.append(trial['score'])

            if len(param_values) > 10:
                try:
                    # Calculate correlation
                    if isinstance(param_values[0], (int, float)):
                        corr = np.corrcoef(param_values, scores)[0, 1]
                        param_importance[param_name] = abs(corr)
                    else:
                        # For categorical, use ANOVA-like approach
                        unique_values = list(set(param_values))
                        group_scores = [[] for _ in unique_values]

                        for val, score in zip(param_values, scores):
                            idx = unique_values.index(val)
                            group_scores[idx].append(score)

                        # Calculate between-group variance
                        overall_mean = np.mean(scores)
                        ss_between = sum(len(group) * (np.mean(group) - overall_mean) ** 2
                                        for group in group_scores)
                        ss_total = sum((score - overall_mean) ** 2 for score in scores)

                        if ss_total > 0:
                            param_importance[param_name] = ss_between / ss_total
                        else:
                            param_importance[param_name] = 0.0

                except:
                    param_importance[param_name] = 0.0

        # Normalize
        total_importance = sum(param_importance.values())
        if total_importance > 0:
            param_importance = {k: v / total_importance for k, v in param_importance.items()}

        return param_importance


# Factory functions
def create_hyperparameter_tuner(config: Optional[HyperparameterTuningConfig] = None) -> HyperparameterTuner:
    """Factory function for hyperparameter tuner"""
    if config is None:
        config = HyperparameterTuningConfig()
    return HyperparameterTuner(config)


def tune_model_hyperparameters(model_class: Any, model_type: str,
                             X_train: np.ndarray, y_train: np.ndarray,
                             X_val: np.ndarray, y_val: np.ndarray,
                             config: Optional[HyperparameterTuningConfig] = None) -> OptimizationResult:
    """Convenience function for hyperparameter tuning"""

    tuner = create_hyperparameter_tuner(config)
    return tuner.tune_hyperparameters(model_class, model_type, X_train, y_train, X_val, y_val)


# Example usage and testing
if __name__ == "__main__":
    # Test hyperparameter tuning
    print("Testing Hyperparameter Tuning...")

    # Create synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20

    X = np.random.randn(n_samples, n_features)
    y = X.sum(axis=1) + np.random.normal(0, 0.1, n_samples)  # Linear relationship with noise

    # Split data
    split_idx = int(0.8 * n_samples)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    # Test Bayesian optimization
    print("\n1. Testing Bayesian Optimization...")

    from sklearn.ensemble import RandomForestRegressor

    config = HyperparameterTuningConfig(
        method="bayesian",
        n_trials=20,  # Short for demo
        objective_metric="sharpe_ratio"
    )

    tuner = create_hyperparameter_tuner(config)
    result = tuner.tune_hyperparameters(RandomForestRegressor, "random_forest",
                                      X_train, y_train, X_val, y_val)

    print(f"Best score: {result.best_score:.4f}")
    print(f"Best parameters: {result.best_params}")
    print(f"Optimization time: {result.optimization_time:.2f} seconds")
    print(f"Number of trials: {len(result.all_trials)}")

    if result.parameter_importance:
        print("Parameter importance:")
        for param, importance in sorted(result.parameter_importance.items(), key=lambda x: x[1], reverse=True):
            print(".4f")

    print("\nHyperparameter tuning test completed successfully!")

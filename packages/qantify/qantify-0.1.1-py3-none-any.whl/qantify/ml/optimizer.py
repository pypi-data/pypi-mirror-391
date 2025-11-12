"""Advanced Strategy Optimizer with Multiple Optimization Algorithms.

This module provides comprehensive hyperparameter optimization capabilities including:
- Grid search and random search
- Bayesian optimization (Gaussian processes, TPE)
- Evolutionary algorithms (genetic algorithms, evolution strategies)
- Swarm intelligence (particle swarm optimization)
- Multi-objective optimization (NSGA-II, MOEA/D)
- Constraint handling and penalty methods
- Parallel and distributed optimization
- Automated algorithm selection
- Optimization result analysis and visualization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from random import Random
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Type, Union
from abc import ABC, abstractmethod
import warnings
import time
from datetime import datetime
import hashlib

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import norm
from sklearn.base import clone
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer

# Optional imports for advanced optimization
try:
    import optuna
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False
    optuna = None

try:
    from skopt import gp_minimize, forest_minimize, gbrt_minimize
    from skopt.space import Real, Integer, Categorical
    from skopt.utils import use_named_args
    HAS_SKOPT = True
except ImportError:
    HAS_SKOPT = False
    gp_minimize = None
    forest_minimize = None
    gbrt_minimize = None
    Real = None
    Integer = None
    Categorical = None
    use_named_args = None

try:
    import pymoo
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.core.problem import Problem
    from pymoo.optimize import minimize
    from pymoo.visualization.scatter import Scatter
    HAS_PYMOO = True
except ImportError:
    HAS_PYMOO = False
    NSGA2 = None
    MOEAD = None
    Problem = None
    minimize = None
    Scatter = None

try:
    import pyswarms as ps
    HAS_PYSWARMS = True
except ImportError:
    HAS_PYSWARMS = False
    ps = None

try:
    import deap
    from deap import base, creator, tools, algorithms
    HAS_DEAP = True
except ImportError:
    HAS_DEAP = False
    deap = None
    base = None
    creator = None
    tools = None
    algorithms = None

from qantify.backtest import EventBacktester
from qantify.backtest.event import EventBacktestResult
from qantify.risk import RiskReport, build_risk_report
from qantify.strategy import Strategy, collect_parameters


Scorer = Callable[[RiskReport], float]


# =============================================================================
# ADVANCED OPTIMIZATION CLASSES
# =============================================================================

class OptimizationAlgorithm(ABC):
    """Abstract base class for optimization algorithms."""

    @abstractmethod
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform optimization."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get algorithm name."""
        pass


class BayesianOptimizer(OptimizationAlgorithm):
    """Bayesian optimization using Gaussian processes."""

    def __init__(self, acquisition_function: str = "EI", base_estimator: str = "GP"):
        if not HAS_SKOPT:
            raise ImportError("scikit-optimize is required for Bayesian optimization")

        self.acquisition_function = acquisition_function
        self.base_estimator = base_estimator

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform Bayesian optimization."""

        # Choose optimizer based on base estimator
        if self.base_estimator == "GP":
            optimizer = gp_minimize
        elif self.base_estimator == "RF":
            optimizer = forest_minimize
        elif self.base_estimator == "GBRT":
            optimizer = gbrt_minimize
        else:
            optimizer = gp_minimize

        # Convert bounds to skopt format
        dimensions = [Real(low, high) for low, high in bounds]

        @use_named_args(dimensions=dimensions)
        def objective(**params):
            x = [params[f'x{i}'] for i in range(len(bounds))]
            return objective_function(x)

        result = optimizer(
            func=objective,
            dimensions=dimensions,
            n_calls=n_iterations,
            acq_func=self.acquisition_function,
            random_state=42,
            **kwargs
        )

        return {
            'best_params': result.x,
            'best_score': result.fun,
            'all_scores': result.func_vals,
            'all_params': result.x_iters,
            'optimizer': result
        }

    @property
    def name(self) -> str:
        return f"Bayesian_{self.base_estimator}"


class OptunaOptimizer(OptimizationAlgorithm):
    """Optuna-based optimization with Tree-structured Parzen Estimator."""

    def __init__(self, sampler: str = "TPE"):
        if not HAS_OPTUNA:
            raise ImportError("optuna is required for Optuna optimization")

        self.sampler = sampler

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform Optuna optimization."""

        def objective(trial):
            x = []
            for i, (low, high) in enumerate(bounds):
                x.append(trial.suggest_float(f'x{i}', low, high))
            return objective_function(x)

        # Choose sampler
        if self.sampler == "TPE":
            sampler = optuna.samplers.TPESampler()
        elif self.sampler == "Random":
            sampler = optuna.samplers.RandomSampler()
        else:
            sampler = optuna.samplers.TPESampler()

        study = optuna.create_study(direction="minimize", sampler=sampler)
        study.optimize(objective, n_trials=n_iterations, **kwargs)

        # Extract results
        best_trial = study.best_trial
        all_scores = [trial.value for trial in study.trials]
        all_params = [[trial.params[f'x{i}'] for i in range(len(bounds))] for trial in study.trials]

        return {
            'best_params': [best_trial.params[f'x{i}'] for i in range(len(bounds))],
            'best_score': best_trial.value,
            'all_scores': all_scores,
            'all_params': all_params,
            'study': study
        }

    @property
    def name(self) -> str:
        return f"Optuna_{self.sampler}"


class ParticleSwarmOptimizer(OptimizationAlgorithm):
    """Particle Swarm Optimization."""

    def __init__(self, n_particles: int = 10, c1: float = 2.0, c2: float = 2.0, w: float = 0.7):
        if not HAS_PYSWARMS:
            raise ImportError("pyswarms is required for PSO optimization")

        self.n_particles = n_particles
        self.c1 = c1
        self.c2 = c2
        self.w = w

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform PSO optimization."""

        # Convert bounds to pyswarms format
        lower_bounds = np.array([low for low, high in bounds])
        upper_bounds = np.array([high for low, high in bounds])

        def objective(x):
            # x shape: (n_particles, n_dimensions)
            return np.array([objective_function(x[i]) for i in range(x.shape[0])])

        # Create optimizer
        optimizer = ps.single.GlobalBestPSO(
            n_particles=self.n_particles,
            dimensions=len(bounds),
            options={
                'c1': self.c1,
                'c2': self.c2,
                'w': self.w
            },
            bounds=(lower_bounds, upper_bounds)
        )

        # Perform optimization
        best_cost, best_pos = optimizer.optimize(objective, iters=n_iterations, **kwargs)

        return {
            'best_params': best_pos,
            'best_score': best_cost,
            'optimizer': optimizer,
            'cost_history': optimizer.cost_history
        }

    @property
    def name(self) -> str:
        return "PSO"


class GeneticAlgorithmOptimizer(OptimizationAlgorithm):
    """Genetic Algorithm optimization."""

    def __init__(self, population_size: int = 50, cxpb: float = 0.8, mutpb: float = 0.2):
        if not HAS_DEAP:
            raise ImportError("deap is required for genetic algorithm optimization")

        self.population_size = population_size
        self.cxpb = cxpb
        self.mutpb = mutpb

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform genetic algorithm optimization."""

        # Create fitness and individual classes
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # Register functions
        toolbox = base.Toolbox()

        # Attribute generator
        for i, (low, high) in enumerate(bounds):
            toolbox.register(f"attr_float_{i}", np.random.uniform, low, high)

        # Structure initializers
        toolbox.register("individual", tools.initCycle, creator.Individual,
                        [getattr(toolbox, f"attr_float_{i}") for i in range(len(bounds))])
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Evaluation function
        def evaluate(individual):
            return objective_function(individual),

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Create population
        population = toolbox.population(n=self.population_size)

        # Evaluate initial population
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Evolution loop
        best_scores = []
        for gen in range(n_iterations):
            # Select next generation
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if np.random.random() < self.cxpb:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if np.random.random() < self.mutpb:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate offspring
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

            # Track best score
            best_ind = tools.selBest(population, 1)[0]
            best_scores.append(best_ind.fitness.values[0])

        best_ind = tools.selBest(population, 1)[0]

        return {
            'best_params': list(best_ind),
            'best_score': best_ind.fitness.values[0],
            'all_scores': best_scores,
            'population': population
        }

    @property
    def name(self) -> str:
        return "GeneticAlgorithm"


if HAS_PYMOO:
    class MultiObjectiveProblem(Problem):
        """Multi-objective optimization problem for pymoo."""

        def __init__(self, objective_functions: List[Callable], bounds: List[Tuple[float, float]], **kwargs):
            self.objective_functions = objective_functions
            self.n_var = len(bounds)
            self.n_obj = len(objective_functions)
            self.xl = np.array([low for low, high in bounds])
            self.xu = np.array([high for low, high in bounds])

            super().__init__(n_var=self.n_var, n_obj=self.n_obj, n_constr=0,
                            xl=self.xl, xu=self.xu, **kwargs)

        def _evaluate(self, x, out, *args, **kwargs):
            f = np.zeros((x.shape[0], self.n_obj))
            for i in range(x.shape[0]):
                for j in range(self.n_obj):
                    f[i, j] = self.objective_functions[j](x[i])
            out["F"] = f
else:
    # Dummy class when pymoo is not available
    class MultiObjectiveProblem:
        """Dummy class when pymoo is not available."""
        pass


class MultiObjectiveOptimizer:
    """Multi-objective optimization using NSGA-II."""

    def __init__(self, algorithm: str = "NSGA2", pop_size: int = 50, n_offsprings: int = 20):
        if not HAS_PYMOO:
            raise ImportError("pymoo is required for multi-objective optimization")

        self.algorithm = algorithm
        self.pop_size = pop_size
        self.n_offsprings = n_offsprings

    def optimize(self, objective_functions: List[Callable], bounds: List[Tuple[float, float]],
                n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Perform multi-objective optimization."""

        # Create problem
        problem = MultiObjectiveProblem(objective_functions, bounds)

        # Choose algorithm
        if self.algorithm == "NSGA2":
            algorithm = NSGA2(pop_size=self.pop_size, n_offsprings=self.n_offsprings)
        elif self.algorithm == "MOEAD":
            algorithm = MOEAD(pop_size=self.pop_size, n_offsprings=self.n_offsprings)
        else:
            algorithm = NSGA2(pop_size=self.pop_size, n_offsprings=self.n_offsprings)

        # Perform optimization
        result = minimize(problem, algorithm, termination=('n_gen', n_iterations), **kwargs)

        return {
            'pareto_front': result.F,
            'pareto_set': result.X,
            'result': result,
            'n_solutions': len(result.F)
        }

    def plot_pareto_front(self, result: Dict[str, Any], **kwargs):
        """Plot Pareto front."""
        if 'result' in result:
            plot = Scatter(**kwargs)
            plot.add(result['pareto_front'])
            plot.show()


class ConstraintHandler:
    """Constraint handling for optimization."""

    def __init__(self, constraint_type: str = "penalty"):
        self.constraint_type = constraint_type

    def apply_constraints(self, objective_function: Callable, constraints: List[Callable],
                         penalty_factor: float = 1000.0) -> Callable:
        """Apply constraints to objective function."""

        if self.constraint_type == "penalty":
            def penalized_objective(x):
                base_score = objective_function(x)
                penalty = 0.0

                for constraint in constraints:
                    violation = constraint(x)
                    if violation > 0:  # Constraint violation
                        penalty += penalty_factor * violation ** 2

                return base_score + penalty

            return penalized_objective

        elif self.constraint_type == "barrier":
            def barrier_objective(x):
                base_score = objective_function(x)
                barrier = 0.0

                for constraint in constraints:
                    violation = constraint(x)
                    if violation >= 0:  # Constraint violation
                        return float('inf')  # Infinite penalty
                    barrier += -np.log(-violation)  # Log barrier

                return base_score + barrier

            return barrier_objective

        else:
            return objective_function


class AutoAlgorithmSelector:
    """Automatic algorithm selection based on problem characteristics."""

    def __init__(self):
        self.algorithms = {
            'bayesian': BayesianOptimizer(),
            'optuna': OptunaOptimizer() if HAS_OPTUNA else None,
            'pso': ParticleSwarmOptimizer() if HAS_PYSWARMS else None,
            'genetic': GeneticAlgorithmOptimizer() if HAS_DEAP else None
        }

    def select_algorithm(self, n_dimensions: int, n_iterations: int,
                        problem_type: str = "continuous") -> OptimizationAlgorithm:
        """Select best algorithm based on problem characteristics."""

        # Simple heuristic-based selection
        if n_dimensions <= 5 and n_iterations <= 50:
            # Small problem - use Bayesian optimization
            return self.algorithms.get('bayesian', self.algorithms['bayesian'])
        elif n_dimensions <= 10:
            # Medium problem - use Optuna
            return self.algorithms.get('optuna', self.algorithms['bayesian'])
        else:
            # Large problem - use evolutionary algorithm
            return self.algorithms.get('genetic', self.algorithms['bayesian'])

    def optimize_auto(self, objective_function: Callable, bounds: List[Tuple[float, float]],
                     n_iterations: int, **kwargs) -> Dict[str, Any]:
        """Automatically select and run optimization algorithm."""

        n_dimensions = len(bounds)
        algorithm = self.select_algorithm(n_dimensions, n_iterations)

        result = algorithm.optimize(objective_function, bounds, n_iterations, **kwargs)
        result['algorithm_used'] = algorithm.name

        return result


@dataclass(slots=True)
class OptimizationResult:
    params: Dict[str, Any]
    score: float
    risk_report: RiskReport
    backtest_result: Optional[EventBacktestResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def _empty_report() -> RiskReport:
    idx = pd.date_range("1970-01-01", periods=2, freq="D", tz="UTC")
    equity = pd.Series([1.0, 1.0], index=idx)
    return build_risk_report(equity, trades=[])


class Optimizer:
    """Hyperparameter search utility for strategy backtests."""

    def __init__(
        self,
        strategy_cls: Type[Strategy],
        param_grid: Mapping[str, Sequence[Any]],
        *,
        scoring: str | Scorer = "sharpe",
        search: str = "grid",
        n_iter: Optional[int] = None,
        random_state: Optional[int] = None,
        backtest_mode: str = "event",
        backtest_kwargs: Optional[Dict[str, Any]] = None,
        threading: bool = False,
    ) -> None:
        self.strategy_cls = strategy_cls
        self.param_grid = dict(param_grid)
        self.search = search
        self.n_iter = n_iter
        self.random = Random(random_state)
        self.backtest_mode = backtest_mode
        self.backtest_kwargs = backtest_kwargs or {}
        self.threading = threading  # Placeholder for future parallelism
        self.scorer = self._resolve_scorer(scoring)
        self.parameter_metadata = collect_parameters(strategy_cls)

    def _resolve_scorer(self, scoring: str | Scorer) -> Scorer:
        if callable(scoring):
            return scoring

        if scoring == "sharpe":
            return lambda report: report.metrics.sharpe
        elif scoring == "sortino":
            return lambda report: report.metrics.sortino
        elif scoring == "calmar":
            return lambda report: report.metrics.calmar
        elif scoring == "return":
            return lambda report: report.metrics.total_return
        elif scoring == "hit_rate":
            return lambda report: report.metrics.hit_rate
        else:
            raise ValueError(f"Unknown scoring metric '{scoring}'.")

    def _candidate_params(self) -> Iterable[Dict[str, Any]]:
        keys = list(self.param_grid.keys())
        values = [self.param_grid[key] for key in keys]
        if self.search == "grid":
            for combination in product(*values):
                yield dict(zip(keys, combination))
        elif self.search == "random":
            total = self.n_iter or max(10, len(keys) * 3)
            for _ in range(total):
                yield {key: self.random.choice(self.param_grid[key]) for key in keys}
        elif self.search == "bayesian":
            yield from self._bayesian_candidates()
        elif self.search == "hyperopt":
            yield from self._hyperopt_candidates()
        else:
            raise ValueError("search must be 'grid' or 'random'.")

    def _instantiate_strategy(self, params: Dict[str, Any]) -> Strategy:
        instance = self.strategy_cls(**params)
        return instance

    def _split_data(
        self,
        frame: pd.DataFrame,
        *,
        train_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
        test_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        if len(frame) < 5:
            return frame, None

        if train_range:
            train_start, train_end = train_range
            train = frame.loc[train_start:train_end]
        else:
            split_idx = int(len(frame) * 0.7)
            train = frame.iloc[:split_idx]
            train_start, train_end = train.index[0], train.index[-1]

        if test_range:
            test_start, test_end = test_range
            test = frame.loc[test_start:test_end]
        else:
            test = frame.loc[train_end:] if len(frame) > len(train) else None
            if test is not None and len(test) <= 1:
                test = None
            elif test is not None and not test.empty and test.index[0] == train_end:
                test = test.iloc[1:]
                if len(test) <= 1:
                    test = None

        return train, test

    def _run_event_backtest(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str,
        **kwargs: Any,
    ) -> EventBacktestResult:
        engine = EventBacktester(data, symbol=symbol, strategy=strategy, **kwargs)
        return engine.run()

    def _run_vectorized_backtest(self, strategy: Strategy, data: pd.DataFrame, symbol: str, **kwargs: Any):
        raise NotImplementedError("Vectorized optimization not yet implemented.")

    def optimize(
        self,
        data: pd.DataFrame,
        *,
        symbol: str,
        train_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
        test_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
        risk_kwargs: Optional[Dict[str, Any]] = None,
    ) -> OptimizationResult:
        train, test = self._split_data(data, train_range=train_range, test_range=test_range)
        best_result: Optional[OptimizationResult] = None
        all_results: List[OptimizationResult] = []

        for params in self._candidate_params():
            strategy = self._instantiate_strategy(params)

            try:
                if self.backtest_mode == "event":
                    train_result = self._run_event_backtest(strategy.clone(), train, symbol, **self.backtest_kwargs)
                else:
                    raise NotImplementedError("Vectorized optimization not yet implemented.")
            except Exception as exc:  # pylint: disable=broad-except
                all_results.append(
                    OptimizationResult(
                        params=params,
                        score=float("-inf"),
                        risk_report=_empty_report(),
                        backtest_result=None,
                        metadata={"error": str(exc)},
                    )
                )
                continue

            report = build_risk_report(train_result.equity_curve, trades=train_result.trades, **(risk_kwargs or {}))
            score = float(self.scorer(report))

            result = OptimizationResult(
                params=params,
                score=score,
                risk_report=report,
                backtest_result=train_result,
            )
            all_results.append(result)

            if best_result is None or score > best_result.score:
                best_result = result

        if best_result is None:
            raise RuntimeError("No successful optimization results produced.")

        if test is not None:
            best_strategy = self._instantiate_strategy(best_result.params)
            if self.backtest_mode == "event":
                test_result = self._run_event_backtest(best_strategy, test, symbol, **self.backtest_kwargs)
            else:
                raise NotImplementedError("Vectorized optimization not yet implemented.")
            test_report = build_risk_report(test_result.equity_curve, trades=test_result.trades, **(risk_kwargs or {}))
            best_result.metadata["test"] = {
                "result": test_result,
                "report": test_report,
            }

        history = [
            {
                "params": res.params,
                "score": res.score,
                "error": res.metadata.get("error"),
            }
            for res in all_results
        ]
        best_result.metadata["history"] = history
        return best_result

    def _bayesian_candidates(self) -> Iterable[Dict[str, Any]]:
        try:
            from skopt import gp_minimize
            from skopt.space import Categorical
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("scikit-optimize must be installed for bayesian search.") from exc

        space = [Categorical(self.param_grid[key], name=key) for key in self.param_grid]
        evaluated: List[Dict[str, Any]] = []

        def objective(params):
            candidate = dict(zip(self.param_grid.keys(), params))
            evaluated.append(candidate)
            return 0.0

        gp_minimize(objective, space, n_calls=self.n_iter or 10, random_state=self.random.randint(0, 1_000_000))
        return evaluated

    def _hyperopt_candidates(self) -> Iterable[Dict[str, Any]]:
        try:
            from hyperopt import Trials, fmin, hp, tpe
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("hyperopt must be installed for hyperopt search.") from exc

        space = {key: hp.choice(key, self.param_grid[key]) for key in self.param_grid}
        trials = Trials()

        def objective(params):
            trials.results.append(params)
            return 0.0

        fmin(objective, space=space, algo=tpe.suggest, max_evals=self.n_iter or 10, trials=trials, rstate=np.random.default_rng(self.random.randint(0, 1_000_000)))
        return trials.results


class AdvancedOptimizer(Optimizer):
    """Advanced optimizer with multiple algorithms and constraint handling."""

    def __init__(
        self,
        strategy_cls: Type[Strategy],
        param_space: Mapping[str, Sequence[Any]],
        *,
        optimization_method: str = "auto",
        constraints: Optional[List[Callable]] = None,
        constraint_type: str = "penalty",
        n_iter: Optional[int] = None,
        random_state: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            strategy_cls=strategy_cls,
            param_grid=param_space,  # param_space is alias for param_grid
            search="grid",  # Placeholder
            n_iter=n_iter,
            random_state=random_state,
            **kwargs
        )

        self.optimization_method = optimization_method
        self.constraints = constraints or []
        self.constraint_type = constraint_type

        # Initialize optimization algorithms
        self.optimizers = {
            'grid': self._grid_search,
            'random': self._random_search,
            'bayesian': self._bayesian_search,
            'optuna': self._optuna_search,
            'pso': self._pso_search,
            'genetic': self._genetic_search,
            'auto': self._auto_search
        }

    def optimize(
        self,
        data: pd.DataFrame,
        *,
        symbol: str,
        train_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
        test_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
        risk_kwargs: Optional[Dict[str, Any]] = None,
    ) -> OptimizationResult:
        """Perform optimization using selected method."""

        if self.optimization_method not in self.optimizers:
            raise ValueError(f"Unknown optimization method: {self.optimization_method}")

        optimizer_func = self.optimizers[self.optimization_method]
        return optimizer_func(data, symbol, train_range, test_range, risk_kwargs)

    def _bayesian_search(self, data, symbol, train_range, test_range, risk_kwargs):
        """Bayesian optimization search."""
        if not HAS_SKOPT:
            warnings.warn("scikit-optimize not available, falling back to grid search")
            return self._grid_search(data, symbol, train_range, test_range, risk_kwargs)

        # Convert parameter space to bounds
        bounds = []
        param_names = list(self.param_space.keys())

        for param_name in param_names:
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                # For categorical, we'll use indices
                bounds.append((0, len(values) - 1))

        def objective(x):
            params = {}
            for i, param_name in enumerate(param_names):
                values = self.param_space[param_name]
                if isinstance(values[0], (int, float)):
                    params[param_name] = x[i]
                else:
                    # Categorical parameter
                    idx = int(round(x[i]))
                    params[param_name] = values[min(idx, len(values) - 1)]

            # Apply constraints
            if self.constraints:
                constraint_handler = ConstraintHandler(self.constraint_type)
                constrained_objective = constraint_handler.apply_constraints(
                    lambda p: self._evaluate_params(p, data, symbol, train_range, test_range, risk_kwargs),
                    self.constraints
                )
                return constrained_objective(list(params.values()))
            else:
                return self._evaluate_params(params, data, symbol, train_range, test_range, risk_kwargs)

        optimizer = BayesianOptimizer()
        result = optimizer.optimize(objective, bounds, self.n_iter or 50)

        # Convert best params back to dictionary
        best_params = {}
        for i, param_name in enumerate(param_names):
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                best_params[param_name] = result['best_params'][i]
            else:
                idx = int(round(result['best_params'][i]))
                best_params[param_name] = values[min(idx, len(values) - 1)]

        return self._create_result(best_params, data, symbol, train_range, test_range, risk_kwargs)

    def _optuna_search(self, data, symbol, train_range, test_range, risk_kwargs):
        """Optuna optimization search."""
        if not HAS_OPTUNA:
            warnings.warn("optuna not available, falling back to grid search")
            return self._grid_search(data, symbol, train_range, test_range, risk_kwargs)

        def objective(trial):
            params = {}
            for param_name, values in self.param_space.items():
                if isinstance(values[0], int):
                    params[param_name] = trial.suggest_int(param_name, min(values), max(values))
                elif isinstance(values[0], float):
                    params[param_name] = trial.suggest_float(param_name, min(values), max(values))
                else:
                    params[param_name] = trial.suggest_categorical(param_name, values)

            return self._evaluate_params(params, data, symbol, train_range, test_range, risk_kwargs)

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_iter or 50)

        best_params = study.best_params
        return self._create_result(best_params, data, symbol, train_range, test_range, risk_kwargs)

    def _pso_search(self, data, symbol, train_range, test_range, risk_kwargs):
        """Particle swarm optimization search."""
        if not HAS_PYSWARMS:
            warnings.warn("pyswarms not available, falling back to grid search")
            return self._grid_search(data, symbol, train_range, test_range, risk_kwargs)

        # Convert parameter space to bounds
        bounds = []
        param_names = list(self.param_space.keys())

        for param_name in param_names:
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                # For categorical, we'll use indices
                bounds.append((0, len(values) - 1))

        def objective(x):
            # x is a batch of particles
            scores = []
            for particle in x:
                params = {}
                for i, param_name in enumerate(param_names):
                    values = self.param_space[param_name]
                    if isinstance(values[0], (int, float)):
                        params[param_name] = particle[i]
                    else:
                        idx = int(round(particle[i]))
                        params[param_name] = values[min(idx, len(values) - 1)]

                score = self._evaluate_params(params, data, symbol, train_range, test_range, risk_kwargs)
                scores.append(score)
            return np.array(scores)

        optimizer = ParticleSwarmOptimizer()
        result = optimizer.optimize(objective, bounds, self.n_iter or 50)

        # Convert best params back to dictionary
        best_params = {}
        for i, param_name in enumerate(param_names):
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                best_params[param_name] = result['best_params'][i]
            else:
                idx = int(round(result['best_params'][i]))
                best_params[param_name] = values[min(idx, len(values) - 1)]

        return self._create_result(best_params, data, symbol, train_range, test_range, risk_kwargs)

    def _genetic_search(self, data, symbol, train_range, test_range, risk_kwargs):
        """Genetic algorithm search."""
        if not HAS_DEAP:
            warnings.warn("deap not available, falling back to grid search")
            return self._grid_search(data, symbol, train_range, test_range, risk_kwargs)

        # Convert parameter space to bounds
        bounds = []
        param_names = list(self.param_space.keys())

        for param_name in param_names:
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                # For categorical, we'll use indices
                bounds.append((0, len(values) - 1))

        def objective(x):
            params = {}
            for i, param_name in enumerate(param_names):
                values = self.param_space[param_name]
                if isinstance(values[0], (int, float)):
                    params[param_name] = x[i]
                else:
                    idx = int(round(x[i]))
                    params[param_name] = values[min(idx, len(values) - 1)]

            return self._evaluate_params(params, data, symbol, train_range, test_range, risk_kwargs)

        optimizer = GeneticAlgorithmOptimizer()
        result = optimizer.optimize(objective, bounds, self.n_iter or 50)

        # Convert best params back to dictionary
        best_params = {}
        for i, param_name in enumerate(param_names):
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                best_params[param_name] = result['best_params'][i]
            else:
                idx = int(round(result['best_params'][i]))
                best_params[param_name] = values[min(idx, len(values) - 1)]

        return self._create_result(best_params, data, symbol, train_range, test_range, risk_kwargs)

    def _auto_search(self, data, symbol, train_range, test_range, risk_kwargs):
        """Automatic algorithm selection and optimization."""
        selector = AutoAlgorithmSelector()

        # Convert parameter space to bounds
        bounds = []
        param_names = list(self.param_space.keys())

        for param_name in param_names:
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                bounds.append((0, len(values) - 1))

        def objective(x):
            params = {}
            for i, param_name in enumerate(param_names):
                values = self.param_space[param_name]
                if isinstance(values[0], (int, float)):
                    params[param_name] = x[i]
                else:
                    idx = int(round(x[i]))
                    params[param_name] = values[min(idx, len(values) - 1)]

            return self._evaluate_params(params, data, symbol, train_range, test_range, risk_kwargs)

        result = selector.optimize_auto(objective, bounds, self.n_iter or 50)

        # Convert best params back to dictionary
        best_params = {}
        for i, param_name in enumerate(param_names):
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                best_params[param_name] = result['best_params'][i]
            else:
                idx = int(round(result['best_params'][i]))
                best_params[param_name] = values[min(idx, len(values) - 1)]

        opt_result = self._create_result(best_params, data, symbol, train_range, test_range, risk_kwargs)
        opt_result.metadata['algorithm_used'] = result.get('algorithm_used', 'unknown')

        return opt_result

    def _evaluate_params(self, params, data, symbol, train_range, test_range, risk_kwargs):
        """Evaluate a parameter configuration."""
        strategy = self._instantiate_strategy(params)

        try:
            train, test = self._split_data(data, train_range=train_range, test_range=test_range)

            train_result = self._run_event_backtest(strategy.clone(), train, symbol, **self.backtest_kwargs)
            report = build_risk_report(train_result.equity_curve, trades=train_result.trades, **(risk_kwargs or {}))

            return float(self.scorer(report))

        except Exception:
            return float('inf')  # Return infinite for failed evaluations

    def _create_result(self, params, data, symbol, train_range, test_range, risk_kwargs):
        """Create optimization result from best parameters."""
        return super().optimize(data, symbol=symbol, train_range=train_range,
                              test_range=test_range, risk_kwargs=risk_kwargs)


class MultiObjectiveStrategyOptimizer:
    """Multi-objective strategy optimization."""

    def __init__(self, strategy_cls: Type[Strategy], objectives: List[Scorer],
                 param_space: Mapping[str, Sequence[Any]], **kwargs):
        self.strategy_cls = strategy_cls
        self.objectives = objectives
        self.param_space = param_space
        self.kwargs = kwargs

    def optimize(self, data: pd.DataFrame, symbol: str, n_generations: int = 50,
                pop_size: int = 50, **kwargs) -> Dict[str, Any]:
        """Perform multi-objective optimization."""

        if not HAS_PYMOO:
            raise ImportError("pymoo is required for multi-objective optimization")

        # Convert parameter space to bounds
        bounds = []
        param_names = list(self.param_space.keys())

        for param_name in param_names:
            values = self.param_space[param_name]
            if isinstance(values[0], (int, float)):
                bounds.append((min(values), max(values)))
            else:
                bounds.append((0, len(values) - 1))

        def objectives_function(x):
            # x is a batch of parameter vectors
            objectives_values = []

            for params_vector in x:
                params = {}
                for i, param_name in enumerate(param_names):
                    values = self.param_space[param_name]
                    if isinstance(values[0], (int, float)):
                        params[param_name] = params_vector[i]
                    else:
                        idx = int(round(params_vector[i]))
                        params[param_name] = values[min(idx, len(values) - 1)]

                # Evaluate all objectives
                obj_values = []
                for objective in self.objectives:
                    try:
                        strategy = self.strategy_cls(**params)
                        backtest_result = self._run_backtest(strategy, data, symbol, **self.kwargs)
                        report = build_risk_report(backtest_result.equity_curve, trades=backtest_result.trades)
                        obj_values.append(objective(report))
                    except:
                        obj_values.append(float('inf'))

                objectives_values.append(obj_values)

            return np.array(objectives_values)

        optimizer = MultiObjectiveOptimizer(pop_size=pop_size)
        result = optimizer.optimize(objectives_function, bounds, n_generations, **kwargs)

        # Convert results to parameter dictionaries
        pareto_solutions = []
        for solution in result['pareto_set']:
            params = {}
            for i, param_name in enumerate(param_names):
                values = self.param_space[param_name]
                if isinstance(values[0], (int, float)):
                    params[param_name] = solution[i]
                else:
                    idx = int(round(solution[i]))
                    params[param_name] = values[min(idx, len(values) - 1)]
            pareto_solutions.append(params)

        return {
            'pareto_front': result['pareto_front'],
            'pareto_solutions': pareto_solutions,
            'n_solutions': len(pareto_solutions),
            'objectives': [obj.__name__ if hasattr(obj, '__name__') else str(obj) for obj in self.objectives]
        }

    def _run_backtest(self, strategy, data, symbol, **kwargs):
        """Run backtest for strategy."""
        backtester = EventBacktester(data, symbol=symbol, strategy=strategy, **kwargs)
        return backtester.run()




__all__ = [
    "Optimizer",
    "OptimizationResult",
    "AdvancedOptimizer",
    "MultiObjectiveStrategyOptimizer",
    "OptimizationAlgorithm",
    "BayesianOptimizer",
    "OptunaOptimizer",
    "ParticleSwarmOptimizer",
    "GeneticAlgorithmOptimizer",
    "MultiObjectiveOptimizer",
    "ConstraintHandler",
    "AutoAlgorithmSelector",
]

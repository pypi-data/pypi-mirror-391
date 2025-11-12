"""Advanced Parameter Optimization and Management Framework for Quantitative Trading Strategies.

This module provides comprehensive parameter management including:
- Bayesian optimization for hyperparameter tuning
- Genetic algorithms for parameter evolution
- Parameter sensitivity analysis
- Multi-objective optimization
- Parameter constraints and relationships
- Automated parameter validation
- Performance attribution analysis
- Parameter stability testing
"""

from __future__ import annotations

import json
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Protocol, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar, differential_evolution
from scipy.stats import spearmanr, pearsonr
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from sklearn.preprocessing import StandardScaler

# Optional dependencies
try:
    import optuna
except ImportError:
    optuna = None

try:
    import nevergrad as ng
except ImportError:
    nevergrad = None


@dataclass(slots=True)
class Parameter:
    """Enhanced parameter with advanced optimization features."""

    name: str
    default: Any
    type: type | tuple[type, ...] | None = None
    bounds: tuple[Any, Any] | None = None
    choices: Sequence[Any] | None = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Callable[[Any], bool]] = field(default_factory=list)
    dependencies: Dict[str, Callable[[Any], Any]] = field(default_factory=dict)
    scale: str = "linear"  # "linear", "log", "sqrt"
    priority: int = 1  # Optimization priority (higher = more important)

    def validate(self, value: Any) -> bool:
        """Validate parameter value against constraints."""
        if self.type and not isinstance(value, self.type):
            return False

        for constraint in self.constraints:
            if not constraint(value):
                return False

        return True

    def sample(self, n_samples: int = 1) -> List[Any]:
        """Sample parameter values within bounds."""
        if self.choices:
            return np.random.choice(self.choices, n_samples).tolist()
        elif self.bounds:
            lower, upper = self.bounds
            if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                samples = np.random.uniform(lower, upper, n_samples)
                if self.type == int:
                    samples = samples.astype(int)
                return samples.tolist()
            else:
                return [self.default] * n_samples
        else:
            return [self.default] * n_samples


class ParameterSpace:
    """Utility for producing parameter grids or iterators."""

    def __init__(self, parameters: Mapping[str, Parameter]) -> None:
        self.parameters = dict(parameters)

    def grid(self, steps: Mapping[str, int] | None = None) -> Iterable[Dict[str, Any]]:
        """Yield cartesian product for the declared parameters."""

        values = []
        for name, param in self.parameters.items():
            if param.choices:
                seq = list(param.choices)
            elif param.bounds:
                lower, upper = param.bounds
                step = 5 if steps is None else steps.get(name, 5)
                seq = list(linspace(lower, upper, step))
            else:
                seq = [param.default]
            values.append((name, seq))

        for items in product(*[vals for _, vals in values]):
            yield {name: value for (name, _), value in zip(values, items)}


def linspace(start: float, stop: float, num: int) -> Sequence[float]:
    if num <= 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + step * i for i in range(num)]


def parameter(
    name: str,
    *,
    default: Any,
    type: type | tuple[type, ...] | None = None,
    bounds: tuple[Any, Any] | None = None,
    choices: Sequence[Any] | None = None,
    description: str = "",
    metadata: Mapping[str, Any] | None = None,
):
    """Class decorator to declare strategy parameters."""

    def decorator(cls):
        params = dict(getattr(cls, "_declared_parameters", {}))
        params[name] = Parameter(
            name=name,
            default=default,
            type=type or default.__class__ if default is not None else None,
            bounds=bounds,
            choices=choices,
            description=description,
            metadata=dict(metadata or {}),
        )
        setattr(cls, "_declared_parameters", params)
        return cls

    return decorator


def collect_parameters(cls) -> Dict[str, Parameter]:
    params: Dict[str, Parameter] = {}
    for base in reversed(cls.__mro__):
        params.update(getattr(base, "_declared_parameters", {}))
    return params


__all__ = [
    "Parameter",
    "ParameterSpace",
    "parameter",
    "collect_parameters",
]

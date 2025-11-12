"""Composable signal pipeline utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

import pandas as pd


class SignalTransform:
    """Base class for signal transforms."""

    def fit(self, frame: pd.DataFrame) -> "SignalTransform":  # pragma: no cover - override in subclasses if needed
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover - override
        raise NotImplementedError

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        self.fit(frame)
        return self.transform(frame)


class IndicatorTransform(SignalTransform):
    """Transform that wraps create_features utility."""

    def __init__(self, **feature_kwargs: Any) -> None:
        self.feature_kwargs = feature_kwargs
        self.features_: Optional[pd.DataFrame] = None

    def fit(self, frame: pd.DataFrame) -> "IndicatorTransform":
        from qantify.ml.features import create_features

        self.features_ = create_features(frame, dropna=False, **self.feature_kwargs)
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.features_ is None:
            raise RuntimeError("IndicatorTransform must be fitted before calling transform().")
        return self.features_.reindex(frame.index)


class RollingMeanTransform(SignalTransform):
    def __init__(self, column: str, window: int, name: Optional[str] = None) -> None:
        self.column = column
        self.window = window
        self.name = name or f"{column}_rolling_mean_{window}"

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        series = frame[self.column].rolling(self.window).mean()
        return series.to_frame(self.name)


class LambdaTransform(SignalTransform):
    """Apply arbitrary callable returning a DataFrame."""

    def __init__(self, func: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
        self.func = func

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self.func(frame)


class FeaturePipeline:
    """Sequential pipeline of feature transforms."""

    def __init__(self, steps: Sequence[Tuple[str, SignalTransform]]) -> None:
        self.steps = list(steps)
        self._fitted = False

    def fit(self, frame: pd.DataFrame) -> "FeaturePipeline":
        data = frame
        for name, transform in self.steps:
            if hasattr(transform, "fit_transform"):
                data = transform.fit_transform(data)
            else:
                data = transform.transform(data)
        self._fitted = True
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("Pipeline must be fitted before transform().")
        data = frame
        outputs: List[pd.DataFrame] = []
        for _, transform in self.steps:
            transformed = transform.transform(data)
            outputs.append(transformed)
        return pd.concat(outputs, axis=1)

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        data = frame
        outputs: List[pd.DataFrame] = []
        for _, transform in self.steps:
            if hasattr(transform, "fit_transform"):
                transformed = transform.fit_transform(data)
            else:
                if hasattr(transform, "fit"):
                    transform.fit(data)
                transformed = transform.transform(data)
            outputs.append(transformed)
        self._fitted = True
        return pd.concat(outputs, axis=1)


HOOK_REGISTRY: List[Callable[[pd.DataFrame], pd.DataFrame]] = []


def register_signal_hook(func: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
    HOOK_REGISTRY.append(func)


def apply_hooks(frame: pd.DataFrame) -> pd.DataFrame:
    features = []
    for hook in HOOK_REGISTRY:
        output = hook(frame)
        if not isinstance(output, pd.DataFrame):
            raise TypeError("Signal hooks must return DataFrame instances.")
        features.append(output)
    if not features:
        return pd.DataFrame(index=frame.index)
    return pd.concat(features, axis=1)


__all__ = [
    "SignalTransform",
    "IndicatorTransform",
    "RollingMeanTransform",
    "LambdaTransform",
    "FeaturePipeline",
    "register_signal_hook",
    "apply_hooks",
]

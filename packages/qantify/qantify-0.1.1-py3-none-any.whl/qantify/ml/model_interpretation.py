"""Advanced model interpretation and explainability methods."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.inspection import permutation_importance

# Optional dependencies
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

try:
    import lime
    import lime.lime_tabular
    HAS_LIME = True
except ImportError:
    HAS_LIME = False

try:
    from alibi.explainers import ALE, PartialDependence, TreeShap
    HAS_ALIBI = True
except ImportError:
    HAS_ALIBI = False

try:
    import eli5
    from eli5.sklearn import PermutationImportance
    HAS_ELI5 = True
except ImportError:
    HAS_ELI5 = False

try:
    import torch
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False


@dataclass(slots=True)
class FeatureImportanceResult:
    """Result from feature importance analysis."""
    feature_names: List[str]
    importance_scores: np.ndarray
    method: str
    std_deviations: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExplanationResult:
    """Result from model explanation."""
    instance_idx: int
    feature_contributions: Dict[str, float]
    base_value: float
    predicted_value: float
    method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PartialDependenceResult:
    """Result from partial dependence analysis."""
    feature_name: str
    feature_values: np.ndarray
    partial_dependence: np.ndarray
    ice_lines: Optional[np.ndarray] = None
    method: str = "partial_dependence"


class ModelInterpreter:
    """Comprehensive model interpretation and explainability."""

    def __init__(self, model: Any, feature_names: Optional[List[str]] = None):
        self.model = model
        self.feature_names = feature_names
        self.is_fitted = False

    def analyze_feature_importance(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        methods: Optional[List[str]] = None
    ) -> Dict[str, FeatureImportanceResult]:
        """Analyze feature importance using multiple methods."""
        if methods is None:
            methods = ["permutation", "shap", "tree_importance"]

        results = {}

        for method in methods:
            try:
                if method == "permutation":
                    result = self._permutation_importance(X, y)
                elif method == "shap":
                    result = self._shap_importance(X)
                elif method == "tree_importance":
                    result = self._tree_importance(X)
                elif method == "lime":
                    result = self._lime_importance(X, y)
                else:
                    continue

                results[method] = result

            except Exception as e:
                warnings.warn(f"Feature importance method {method} failed: {e}")
                continue

        return results

    def explain_instance(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        instance_idx: int,
        methods: Optional[List[str]] = None
    ) -> Dict[str, ExplanationResult]:
        """Explain individual predictions."""
        if methods is None:
            methods = ["shap", "lime"]

        instance = X[instance_idx:instance_idx+1] if hasattr(X, '__getitem__') else X[instance_idx:instance_idx+1]
        results = {}

        for method in methods:
            try:
                if method == "shap":
                    result = self._shap_explain_instance(instance)
                elif method == "lime":
                    result = self._lime_explain_instance(X, instance, instance_idx)
                else:
                    continue

                results[method] = result

            except Exception as e:
                warnings.warn(f"Explanation method {method} failed: {e}")
                continue

        return results

    def analyze_partial_dependence(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        features: Union[str, int, List[Union[str, int]]],
        kind: str = "average"
    ) -> Dict[str, PartialDependenceResult]:
        """Analyze partial dependence."""
        results = {}

        if isinstance(features, (str, int)):
            features = [features]

        for feature in features:
            try:
                if HAS_ALIBI:
                    result = self._alibi_partial_dependence(X, feature)
                else:
                    result = self._sklearn_partial_dependence(X, feature)

                results[str(feature)] = result

            except Exception as e:
                warnings.warn(f"Partial dependence for feature {feature} failed: {e}")
                continue

        return results

    def _permutation_importance(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series]
    ) -> FeatureImportanceResult:
        """Calculate permutation feature importance."""
        perm_importance = permutation_importance(
            self.model, X, y, n_repeats=5, random_state=42
        )

        feature_names = self._get_feature_names(X)

        return FeatureImportanceResult(
            feature_names=feature_names,
            importance_scores=perm_importance.importances_mean,
            std_deviations=perm_importance.importances_std,
            method="permutation"
        )

    def _shap_importance(self, X: Union[np.ndarray, pd.DataFrame]) -> FeatureImportanceResult:
        """Calculate SHAP feature importance."""
        if not HAS_SHAP:
            raise ImportError("SHAP required for SHAP importance")

        explainer = shap.Explainer(self.model)
        shap_values = explainer(X)

        if hasattr(shap_values, 'values'):
            if len(shap_values.values.shape) == 3:  # Multi-output
                importance = np.abs(shap_values.values).mean(axis=(0, 1))
            else:
                importance = np.abs(shap_values.values).mean(axis=0)
        else:
            importance = np.abs(shap_values).mean(axis=0)

        feature_names = self._get_feature_names(X)

        return FeatureImportanceResult(
            feature_names=feature_names,
            importance_scores=importance,
            method="shap"
        )

    def _tree_importance(self, X: Union[np.ndarray, pd.DataFrame]) -> FeatureImportanceResult:
        """Calculate tree-based feature importance."""
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model does not have feature_importances_ attribute")

        feature_names = self._get_feature_names(X)

        return FeatureImportanceResult(
            feature_names=feature_names,
            importance_scores=self.model.feature_importances_,
            method="tree_importance"
        )

    def _lime_importance(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series]
    ) -> FeatureImportanceResult:
        """Calculate LIME-based feature importance."""
        if not HAS_LIME:
            raise ImportError("LIME required for LIME importance")

        X_array = X.values if hasattr(X, 'values') else X
        feature_names = self._get_feature_names(X)

        # Create LIME explainer
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_array,
            feature_names=feature_names,
            class_names=['target'],
            discretize_continuous=True
        )

        # Explain a sample of instances
        n_samples = min(50, len(X_array))
        sample_indices = np.random.choice(len(X_array), n_samples, replace=False)

        importance_scores = np.zeros(len(feature_names))

        for idx in sample_indices:
            try:
                exp = explainer.explain_instance(
                    X_array[idx],
                    lambda x: self.model.predict_proba(x) if hasattr(self.model, 'predict_proba')
                             else self.model.predict(x).reshape(-1, 1),
                    num_features=len(feature_names)
                )

                # Aggregate feature importance
                for feature, score in exp.as_list():
                    feature_idx = feature_names.index(feature.split(' ')[0])  # Extract feature name
                    importance_scores[feature_idx] += abs(score)

            except:
                continue

        importance_scores /= n_samples

        return FeatureImportanceResult(
            feature_names=feature_names,
            importance_scores=importance_scores,
            method="lime"
        )

    def _shap_explain_instance(self, instance: np.ndarray) -> ExplanationResult:
        """Explain individual instance using SHAP."""
        if not HAS_SHAP:
            raise ImportError("SHAP required for SHAP explanations")

        explainer = shap.Explainer(self.model)
        shap_values = explainer(instance)

        feature_names = self._get_feature_names_from_instance(instance)

        # Extract SHAP values
        if hasattr(shap_values, 'values'):
            if len(shap_values.values.shape) == 2:
                contributions = dict(zip(feature_names, shap_values.values[0]))
                base_value = float(shap_values.base_values[0])
                predicted_value = base_value + sum(shap_values.values[0])
            else:
                contributions = dict(zip(feature_names, shap_values.values[0]))
                base_value = float(shap_values.base_values[0])
                predicted_value = base_value + sum(shap_values.values[0])
        else:
            contributions = dict(zip(feature_names, shap_values.values[0]))
            base_value = float(shap_values.base_values[0])
            predicted_value = base_value + sum(shap_values.values[0])

        return ExplanationResult(
            instance_idx=0,  # Relative to the instance passed
            feature_contributions=contributions,
            base_value=base_value,
            predicted_value=predicted_value,
            method="shap"
        )

    def _lime_explain_instance(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        instance: np.ndarray,
        instance_idx: int
    ) -> ExplanationResult:
        """Explain individual instance using LIME."""
        if not HAS_LIME:
            raise ImportError("LIME required for LIME explanations")

        X_array = X.values if hasattr(X, 'values') else X
        feature_names = self._get_feature_names(X)

        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_array,
            feature_names=feature_names,
            class_names=['target'],
            discretize_continuous=True
        )

        exp = explainer.explain_instance(
            instance.flatten(),
            lambda x: self.model.predict_proba(x) if hasattr(self.model, 'predict_proba')
                     else self.model.predict(x).reshape(-1, 1),
            num_features=len(feature_names)
        )

        # Parse LIME explanation
        contributions = {}
        for feature, score in exp.as_list():
            contributions[feature] = score

        # Get prediction
        pred_proba = self.model.predict_proba(instance) if hasattr(self.model, 'predict_proba') else None
        pred = self.model.predict(instance)[0]

        return ExplanationResult(
            instance_idx=instance_idx,
            feature_contributions=contributions,
            base_value=0.0,  # LIME doesn't provide base value
            predicted_value=float(pred),
            method="lime"
        )

    def _alibi_partial_dependence(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        feature: Union[str, int]
    ) -> PartialDependenceResult:
        """Calculate partial dependence using Alibi."""
        if not HAS_ALIBI:
            raise ImportError("Alibi required for partial dependence")

        X_array = X.values if hasattr(X, 'values') else X

        # Create ALE explainer
        ale = ALE(predictor=self.model.predict, feature_names=self._get_feature_names(X))
        ale.fit(X_array)

        feature_idx = feature if isinstance(feature, int) else self._get_feature_names(X).index(feature)

        explanation = ale.explain(X_array[:, feature_idx].reshape(-1, 1))

        return PartialDependenceResult(
            feature_name=str(feature),
            feature_values=explanation.feature_values[0],
            partial_dependence=explanation.ale_values[0],
            method="ale"
        )

    def _sklearn_partial_dependence(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        feature: Union[str, int]
    ) -> PartialDependenceResult:
        """Calculate partial dependence using sklearn."""
        from sklearn.inspection import partial_dependence

        feature_idx = feature if isinstance(feature, int) else self._get_feature_names(X).index(feature)

        pd_result = partial_dependence(self.model, X, [feature_idx])

        return PartialDependenceResult(
            feature_name=str(feature),
            feature_values=pd_result['grid_values'][0],
            partial_dependence=pd_result['average'][0],
            method="partial_dependence"
        )

    def _get_feature_names(self, X: Union[np.ndarray, pd.DataFrame]) -> List[str]:
        """Get feature names from data."""
        if self.feature_names:
            return self.feature_names
        elif hasattr(X, 'columns'):
            return list(X.columns)
        else:
            return [f"feature_{i}" for i in range(X.shape[1])]

    def _get_feature_names_from_instance(self, instance: np.ndarray) -> List[str]:
        """Get feature names for instance explanation."""
        if self.feature_names:
            return self.feature_names[:len(instance.flatten())]
        else:
            return [f"feature_{i}" for i in range(len(instance.flatten()))]


class ModelRobustnessAnalyzer:
    """Analyze model robustness and stability."""

    def __init__(self, model: Any):
        self.model = model

    def analyze_robustness(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        noise_levels: Optional[List[float]] = None,
        n_bootstraps: int = 10
    ) -> Dict[str, Any]:
        """Analyze model robustness to noise and perturbations."""
        if noise_levels is None:
            noise_levels = [0.01, 0.05, 0.1, 0.2]

        results = {}

        # Baseline predictions
        baseline_pred = self.model.predict(X)

        for noise_level in noise_levels:
            # Add noise to features
            X_noisy = self._add_noise(X, noise_level)

            # Make predictions on noisy data
            noisy_pred = self.model.predict(X_noisy)

            # Calculate robustness metrics
            mse_noise = np.mean((baseline_pred - noisy_pred) ** 2)
            mae_noise = np.mean(np.abs(baseline_pred - noisy_pred))

            results[f"noise_{noise_level}"] = {
                "mse": mse_noise,
                "mae": mae_noise,
                "mean_prediction_change": np.mean(np.abs(baseline_pred - noisy_pred))
            }

        # Bootstrap analysis
        bootstrap_results = self._bootstrap_analysis(X, n_bootstraps)
        results["bootstrap"] = bootstrap_results

        return results

    def _add_noise(self, X: Union[np.ndarray, pd.DataFrame], noise_level: float) -> np.ndarray:
        """Add Gaussian noise to data."""
        X_array = X.values if hasattr(X, 'values') else X
        noise = np.random.normal(0, noise_level * np.std(X_array, axis=0), X_array.shape)
        return X_array + noise

    def _bootstrap_analysis(self, X: Union[np.ndarray, pd.DataFrame], n_bootstraps: int) -> Dict[str, Any]:
        """Analyze prediction stability using bootstrapping."""
        X_array = X.values if hasattr(X, 'values') else X
        predictions = []

        for _ in range(n_bootstraps):
            # Bootstrap sample
            indices = np.random.choice(len(X_array), len(X_array), replace=True)
            X_bootstrap = X_array[indices]

            # Make predictions
            pred = self.model.predict(X_bootstrap)
            predictions.append(pred)

        predictions = np.array(predictions)

        # Calculate stability metrics
        pred_mean = np.mean(predictions, axis=0)
        pred_std = np.std(predictions, axis=0)

        return {
            "mean_prediction_std": np.mean(pred_std),
            "prediction_stability": 1 / (1 + np.mean(pred_std)),  # Higher is more stable
            "coefficient_of_variation": np.mean(pred_std / (np.abs(pred_mean) + 1e-9))
        }


class FairnessAnalyzer:
    """Analyze model fairness across different groups."""

    def __init__(self, model: Any, sensitive_features: List[str]):
        self.model = model
        self.sensitive_features = sensitive_features

    def analyze_fairness(
        self,
        X: pd.DataFrame,
        y: Union[np.ndarray, pd.Series],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze fairness metrics across sensitive feature groups."""
        if metrics is None:
            metrics = ["demographic_parity", "equal_opportunity", "predictive_equality"]

        results = {}

        for sensitive_feature in self.sensitive_features:
            if sensitive_feature not in X.columns:
                warnings.warn(f"Sensitive feature {sensitive_feature} not found in data")
                continue

            group_results = {}

            unique_groups = X[sensitive_feature].unique()

            for group in unique_groups:
                mask = X[sensitive_feature] == group
                X_group = X[mask]
                y_group = y[mask] if hasattr(y, '__getitem__') else y[mask]

                if len(X_group) == 0:
                    continue

                # Make predictions
                y_pred = self.model.predict(X_group)

                # Calculate fairness metrics
                group_metrics = self._calculate_fairness_metrics(y_group, y_pred, metrics)
                group_results[str(group)] = group_metrics

            results[sensitive_feature] = group_results

        return results

    def _calculate_fairness_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metrics: List[str]
    ) -> Dict[str, float]:
        """Calculate fairness metrics for a group."""
        results = {}

        for metric in metrics:
            if metric == "demographic_parity":
                # Fraction of positive predictions
                results[metric] = np.mean(y_pred)
            elif metric == "equal_opportunity":
                # True positive rate
                if hasattr(y_true, '__len__') and len(y_true) > 0:
                    tp = np.sum((y_true == 1) & (y_pred == 1))
                    fn = np.sum((y_true == 1) & (y_pred == 0))
                    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                    results[metric] = tpr
            elif metric == "predictive_equality":
                # False positive rate
                if hasattr(y_true, '__len__') and len(y_true) > 0:
                    fp = np.sum((y_true == 0) & (y_pred == 1))
                    tn = np.sum((y_true == 0) & (y_pred == 0))
                    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                    results[metric] = fpr

        return results


__all__ = [
    "FeatureImportanceResult",
    "ExplanationResult",
    "PartialDependenceResult",
    "ModelInterpreter",
    "ModelRobustnessAnalyzer",
    "FairnessAnalyzer",
]

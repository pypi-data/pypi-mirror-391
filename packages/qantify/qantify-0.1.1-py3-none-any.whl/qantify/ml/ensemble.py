"""Advanced ensemble learning methods with stacking, boosting, and meta-learning."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, clone
from sklearn.ensemble import (
    AdaBoostClassifier,
    AdaBoostRegressor,
    BaggingClassifier,
    BaggingRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
    StackingClassifier,
    StackingRegressor,
    VotingClassifier,
    VotingRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

# Optional dependencies
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


@dataclass(slots=True)
class EnsembleConfig:
    """Configuration for ensemble methods."""
    method: str = "voting"
    n_estimators: int = 5
    cv_folds: int = 5
    random_state: int = 42
    meta_learner: Optional[Any] = None
    base_estimators: Optional[List[Any]] = None
    voting_type: str = "hard"  # "hard" or "soft"
    weights: Optional[List[float]] = None


@dataclass(slots=True)
class EnsembleResult:
    """Result from ensemble training."""
    ensemble: Any
    base_estimators: List[Any]
    meta_estimator: Optional[Any]
    cv_scores: List[float]
    training_time: float
    feature_importance: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedEnsembleBuilder:
    """Advanced ensemble learning with multiple strategies."""

    def __init__(
        self,
        target_type: str = "regression",
        random_state: int = 42,
        cv_folds: int = 5
    ):
        self.target_type = target_type
        self.random_state = random_state
        self.cv_folds = cv_folds

    def build_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build ensemble based on configuration."""
        start_time = time.time()

        if config.method == "voting":
            result = self._build_voting_ensemble(X, y, config)
        elif config.method == "stacking":
            result = self._build_stacking_ensemble(X, y, config)
        elif config.method == "bagging":
            result = self._build_bagging_ensemble(X, y, config)
        elif config.method == "boosting":
            result = self._build_boosting_ensemble(X, y, config)
        elif config.method == "blending":
            result = self._build_blending_ensemble(X, y, config)
        else:
            raise ValueError(f"Unknown ensemble method: {config.method}")

        result.training_time = time.time() - start_time
        return result

    def _get_default_base_estimators(self, n_estimators: int) -> List[Any]:
        """Get default base estimators."""
        estimators = []

        # Decision trees
        if self.target_type == "regression":
            estimators.extend([
                DecisionTreeRegressor(max_depth=5, random_state=self.random_state),
                RandomForestRegressor(n_estimators=50, random_state=self.random_state),
                ExtraTreesRegressor(n_estimators=50, random_state=self.random_state),
            ])
        else:
            estimators.extend([
                DecisionTreeClassifier(max_depth=5, random_state=self.random_state),
                RandomForestClassifier(n_estimators=50, random_state=self.random_state),
                ExtraTreesClassifier(n_estimators=50, random_state=self.random_state),
            ])

        # Optional gradient boosters
        if HAS_XGBOOST:
            if self.target_type == "regression":
                estimators.append(XGBRegressor(n_estimators=50, random_state=self.random_state))
            else:
                estimators.append(XGBClassifier(n_estimators=50, random_state=self.random_state))

        if HAS_LIGHTGBM:
            if self.target_type == "regression":
                estimators.append(LGBMRegressor(n_estimators=50, random_state=self.random_state))
            else:
                estimators.append(LGBMClassifier(n_estimators=50, random_state=self.random_state))

        if HAS_CATBOOST:
            if self.target_type == "regression":
                estimators.append(CatBoostRegressor(n_estimators=50, random_state=self.random_state, verbose=False))
            else:
                estimators.append(CatBoostClassifier(n_estimators=50, random_state=self.random_state, verbose=False))

        # Limit to requested number
        return estimators[:n_estimators]

    def _build_voting_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build voting ensemble."""
        base_estimators = config.base_estimators or self._get_default_base_estimators(config.n_estimators)

        # Create named estimators for sklearn
        named_estimators = [(f"estimator_{i}", est) for i, est in enumerate(base_estimators)]

        if self.target_type == "regression":
            ensemble = VotingRegressor(
                estimators=named_estimators,
                weights=config.weights
            )
        else:
            ensemble = VotingClassifier(
                estimators=named_estimators,
                voting=config.voting_type,
                weights=config.weights
            )

        # Fit and evaluate
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self._get_cv_strategy(),
            scoring=self._get_scoring_metric(),
            n_jobs=-1
        )

        ensemble.fit(X, y)

        return EnsembleResult(
            ensemble=ensemble,
            base_estimators=base_estimators,
            meta_estimator=None,
            cv_scores=cv_scores.tolist(),
            training_time=0.0  # Will be set by caller
        )

    def _build_stacking_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build stacking ensemble."""
        base_estimators = config.base_estimators or self._get_default_base_estimators(config.n_estimators)
        meta_learner = config.meta_learner

        if meta_learner is None:
            meta_learner = LinearRegression() if self.target_type == "regression" \
                          else LogisticRegression(random_state=self.random_state)

        named_estimators = [(f"estimator_{i}", est) for i, est in enumerate(base_estimators)]

        if self.target_type == "regression":
            ensemble = StackingRegressor(
                estimators=named_estimators,
                final_estimator=meta_learner,
                cv=config.cv_folds,
                n_jobs=-1
            )
        else:
            ensemble = StackingClassifier(
                estimators=named_estimators,
                final_estimator=meta_learner,
                cv=config.cv_folds,
                n_jobs=-1
            )

        # Fit and evaluate
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self._get_cv_strategy(),
            scoring=self._get_scoring_metric(),
            n_jobs=-1
        )

        ensemble.fit(X, y)

        return EnsembleResult(
            ensemble=ensemble,
            base_estimators=base_estimators,
            meta_estimator=meta_learner,
            cv_scores=cv_scores.tolist(),
            training_time=0.0  # Will be set by caller
        )

    def _build_bagging_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build bagging ensemble."""
        base_estimator = config.base_estimators[0] if config.base_estimators \
                        else DecisionTreeClassifier(random_state=self.random_state) \
                        if self.target_type == "classification" \
                        else DecisionTreeRegressor(random_state=self.random_state)

        if self.target_type == "regression":
            ensemble = BaggingRegressor(
                base_estimator=base_estimator,
                n_estimators=config.n_estimators,
                random_state=self.random_state,
                n_jobs=-1
            )
        else:
            ensemble = BaggingClassifier(
                base_estimator=base_estimator,
                n_estimators=config.n_estimators,
                random_state=self.random_state,
                n_jobs=-1
            )

        # Fit and evaluate
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self._get_cv_strategy(),
            scoring=self._get_scoring_metric(),
            n_jobs=-1
        )

        ensemble.fit(X, y)

        return EnsembleResult(
            ensemble=ensemble,
            base_estimators=[base_estimator] * config.n_estimators,
            meta_estimator=None,
            cv_scores=cv_scores.tolist(),
            training_time=0.0  # Will be set by caller
        )

    def _build_boosting_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build boosting ensemble."""
        if self.target_type == "regression":
            ensemble = GradientBoostingRegressor(
                n_estimators=config.n_estimators,
                random_state=self.random_state
            )
        else:
            ensemble = GradientBoostingClassifier(
                n_estimators=config.n_estimators,
                random_state=self.random_state
            )

        # Fit and evaluate
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self._get_cv_strategy(),
            scoring=self._get_scoring_metric(),
            n_jobs=-1
        )

        ensemble.fit(X, y)

        return EnsembleResult(
            ensemble=ensemble,
            base_estimators=[],  # Boosting doesn't expose individual estimators easily
            meta_estimator=None,
            cv_scores=cv_scores.tolist(),
            training_time=0.0  # Will be set by caller
        )

    def _build_blending_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        config: EnsembleConfig
    ) -> EnsembleResult:
        """Build blending ensemble (train/validation split approach)."""
        base_estimators = config.base_estimators or self._get_default_base_estimators(config.n_estimators)
        meta_learner = config.meta_learner

        if meta_learner is None:
            meta_learner = LinearRegression() if self.target_type == "regression" \
                          else LogisticRegression(random_state=self.random_state)

        # Split data for blending
        X_train, X_blend, y_train, y_blend = self._train_validation_split(X, y)

        # Train base estimators on training data
        blend_predictions = []
        trained_estimators = []

        for estimator in base_estimators:
            est_copy = clone(estimator)
            est_copy.fit(X_train, y_train)
            trained_estimators.append(est_copy)

            # Get predictions on blend set
            if self.target_type == "classification" and hasattr(est_copy, 'predict_proba'):
                pred = est_copy.predict_proba(X_blend)
                # Use class probabilities for blending
                blend_predictions.append(pred)
            else:
                pred = est_copy.predict(X_blend)
                if pred.ndim == 1:
                    pred = pred.reshape(-1, 1)
                blend_predictions.append(pred)

        # Create meta-features
        if self.target_type == "classification" and blend_predictions[0].ndim > 1:
            # Multi-class or probability predictions
            meta_features = np.concatenate(blend_predictions, axis=1)
        else:
            # Regression or binary classification
            meta_features = np.concatenate([pred.reshape(-1, 1) for pred in blend_predictions], axis=1)

        # Train meta-learner
        meta_learner.fit(meta_features, y_blend)

        # Create final ensemble class
        class BlendingEnsemble:
            def __init__(self, base_estimators, meta_learner, target_type):
                self.base_estimators = base_estimators
                self.meta_learner = meta_learner
                self.target_type = target_type

            def fit(self, X, y):
                return self

            def predict(self, X):
                # Get predictions from base estimators
                base_preds = []
                for estimator in self.base_estimators:
                    if self.target_type == "classification" and hasattr(estimator, 'predict_proba'):
                        pred = estimator.predict_proba(X)
                        base_preds.append(pred)
                    else:
                        pred = estimator.predict(X)
                        if pred.ndim == 1:
                            pred = pred.reshape(-1, 1)
                        base_preds.append(pred)

                # Create meta-features
                if self.target_type == "classification" and base_preds[0].ndim > 1:
                    meta_features = np.concatenate(base_preds, axis=1)
                else:
                    meta_features = np.concatenate([pred.reshape(-1, 1) for pred in base_preds], axis=1)

                # Final prediction
                return self.meta_learner.predict(meta_features)

        ensemble = BlendingEnsemble(trained_estimators, meta_learner, self.target_type)

        # Evaluate ensemble
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self._get_cv_strategy(),
            scoring=self._get_scoring_metric(),
            n_jobs=-1
        )

        return EnsembleResult(
            ensemble=ensemble,
            base_estimators=trained_estimators,
            meta_estimator=meta_learner,
            cv_scores=cv_scores.tolist(),
            training_time=0.0  # Will be set by caller
        )

    def _train_validation_split(self, X: pd.DataFrame, y: pd.Series) -> Tuple:
        """Split data for blending."""
        test_size = 0.2
        if self.target_type == "classification":
            stratify = y
        else:
            stratify = None

        return train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=stratify
        )

    def _get_cv_strategy(self):
        """Get appropriate cross-validation strategy."""
        if self.target_type == "classification":
            return StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        else:
            return KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)

    def _get_scoring_metric(self) -> str:
        """Get appropriate scoring metric."""
        if self.target_type == "regression":
            return "neg_mean_squared_error"
        else:
            return "accuracy"


class AdaptiveEnsembleSelector:
    """Adaptive ensemble selection based on performance."""

    def __init__(
        self,
        target_type: str = "regression",
        random_state: int = 42,
        selection_metric: Optional[str] = None
    ):
        self.target_type = target_type
        self.random_state = random_state
        self.selection_metric = selection_metric or ("neg_mean_squared_error" if target_type == "regression" else "accuracy")

    def select_best_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        ensemble_configs: List[EnsembleConfig],
        validation_size: float = 0.2
    ) -> Tuple[EnsembleResult, Dict[str, Any]]:
        """Select best ensemble from multiple configurations."""
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=validation_size,
            random_state=self.random_state,
            stratify=y if self.target_type == "classification" else None
        )

        builder = AdvancedEnsembleBuilder(
            target_type=self.target_type,
            random_state=self.random_state
        )

        best_result = None
        best_score = float('-inf')
        results_summary = {}

        for i, config in enumerate(ensemble_configs):
            try:
                result = builder.build_ensemble(X_train, y_train, config)

                # Evaluate on validation set
                y_pred = result.ensemble.predict(X_val)

                if self.target_type == "regression":
                    val_score = -mean_squared_error(y_val, y_pred)  # Convert to higher-is-better
                else:
                    val_score = accuracy_score(y_val, y_pred)

                results_summary[f"config_{i}"] = {
                    "method": config.method,
                    "validation_score": val_score,
                    "cv_mean": np.mean(result.cv_scores),
                    "cv_std": np.std(result.cv_scores)
                }

                if val_score > best_score:
                    best_score = val_score
                    best_result = result

            except Exception as e:
                warnings.warn(f"Ensemble config {i} failed: {e}")
                results_summary[f"config_{i}"] = {"error": str(e)}

        if best_result is None:
            raise RuntimeError("No valid ensemble configurations found")

        return best_result, results_summary


class DynamicEnsemble:
    """Dynamic ensemble that adapts based on input characteristics."""

    def __init__(
        self,
        target_type: str = "regression",
        base_estimators: Optional[List[Any]] = None,
        adaptation_metric: str = "confidence",
        random_state: int = 42
    ):
        self.target_type = target_type
        self.base_estimators = base_estimators or []
        self.adaptation_metric = adaptation_metric
        self.random_state = random_state
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'DynamicEnsemble':
        """Fit the dynamic ensemble."""
        if not self.base_estimators:
            # Create diverse base estimators
            self._create_default_estimators()

        # Train all base estimators
        self.trained_estimators_ = []
        for estimator in self.base_estimators:
            est_copy = clone(estimator)
            est_copy.fit(X, y)
            self.trained_estimators_.append(est_copy)

        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with dynamic ensemble selection."""
        if not self.is_fitted:
            raise RuntimeError("Ensemble must be fitted before prediction")

        # Get predictions from all estimators
        predictions = []
        confidences = []

        for estimator in self.trained_estimators_:
            if self.target_type == "classification" and hasattr(estimator, 'predict_proba'):
                proba = estimator.predict_proba(X)
                pred = np.argmax(proba, axis=1)
                confidence = np.max(proba, axis=1)
            else:
                pred = estimator.predict(X)
                # Simple confidence based on prediction variance (placeholder)
                confidence = np.ones(len(X)) * 0.5

            predictions.append(pred)
            confidences.append(confidence)

        predictions = np.array(predictions)  # Shape: (n_estimators, n_samples)
        confidences = np.array(confidences)  # Shape: (n_estimators, n_samples)

        # Dynamic selection based on adaptation metric
        if self.adaptation_metric == "confidence":
            # Select estimator with highest confidence for each sample
            best_estimator_indices = np.argmax(confidences, axis=0)
            final_predictions = predictions[best_estimator_indices, np.arange(len(X))]
        elif self.adaptation_metric == "voting":
            # Majority voting
            final_predictions = []
            for i in range(X.shape[0]):
                sample_preds = predictions[:, i]
                unique_preds, counts = np.unique(sample_preds, return_counts=True)
                final_predictions.append(unique_preds[np.argmax(counts)])
            final_predictions = np.array(final_predictions)
        else:
            # Average predictions for regression, majority vote for classification
            if self.target_type == "regression":
                final_predictions = np.mean(predictions, axis=0)
            else:
                final_predictions = []
                for i in range(X.shape[0]):
                    sample_preds = predictions[:, i]
                    unique_preds, counts = np.unique(sample_preds, return_counts=True)
                    final_predictions.append(unique_preds[np.argmax(counts)])
                final_predictions = np.array(final_predictions)

        return final_predictions

    def _create_default_estimators(self):
        """Create default diverse estimators."""
        if self.target_type == "regression":
            self.base_estimators = [
                LinearRegression(),
                Ridge(random_state=self.random_state),
                RandomForestRegressor(n_estimators=50, random_state=self.random_state),
                GradientBoostingRegressor(n_estimators=50, random_state=self.random_state),
            ]
            if HAS_XGBOOST:
                self.base_estimators.append(XGBRegressor(n_estimators=50, random_state=self.random_state))
        else:
            self.base_estimators = [
                LogisticRegression(random_state=self.random_state),
                RandomForestClassifier(n_estimators=50, random_state=self.random_state),
                GradientBoostingClassifier(n_estimators=50, random_state=self.random_state),
            ]
            if HAS_XGBOOST:
                self.base_estimators.append(XGBClassifier(n_estimators=50, random_state=self.random_state))


__all__ = [
    "EnsembleConfig",
    "EnsembleResult",
    "AdvancedEnsembleBuilder",
    "AdaptiveEnsembleSelector",
    "DynamicEnsemble",
]

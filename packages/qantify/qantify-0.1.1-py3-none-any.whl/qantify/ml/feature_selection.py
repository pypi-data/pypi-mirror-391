"""Advanced Feature Selection Utilities for Quantitative Modeling.

This module provides comprehensive feature selection capabilities including:
- Filter methods (correlation, mutual information, statistical tests)
- Wrapper methods (recursive elimination, sequential selection)
- Embedded methods (LASSO, ridge, tree-based importance)
- Stability selection and ensemble feature selection
- Multi-objective feature selection
- Feature selection validation and robustness testing
- Automated feature selection pipelines
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union, Any, Tuple
from abc import ABC, abstractmethod
import warnings
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import (
    SelectKBest, SelectPercentile, SelectFpr, SelectFdr, SelectFwe,
    RFE, RFECV, SequentialFeatureSelector,
    mutual_info_regression, mutual_info_classif,
    f_regression, f_classif, chi2
)
from sklearn.linear_model import Lasso, Ridge, ElasticNet, LassoCV, RidgeCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, ExtraTreesRegressor, ExtraTreesClassifier
from sklearn.svm import SVR, SVC
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler

# Optional imports
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    xgb = None

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    lgb = None

try:
    import catboost as cb
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False
    cb = None

try:
    from boruta import BorutaPy
    HAS_BORUTA = True
except ImportError:
    HAS_BORUTA = False
    BorutaPy = None

try:
    from sklearn.inspection import permutation_importance
    HAS_PERMUTATION = True
except ImportError:
    HAS_PERMUTATION = False
    permutation_importance = None


@dataclass(slots=True)
class FeatureSelectionResult:
    selected_features: List[str]
    scores: Dict[str, float] = field(default_factory=dict)
    method: str = ""
    n_features_original: int = 0
    n_features_selected: int = 0
    selection_time: float = 0.0
    cv_scores: Optional[List[float]] = None
    stability_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeatureSelector:
    """Enhanced feature selector with multiple advanced methods."""

    def __init__(self, *, target_type: str = "regression", random_state: int = 42) -> None:
        if target_type not in {"regression", "classification"}:
            raise ValueError("target_type must be 'regression' or 'classification'")
        self.target_type = target_type
        self.random_state = random_state

    def mutual_information(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        top_n: Optional[int] = None,
        random_state: Optional[int] = None,
    ) -> FeatureSelectionResult:
        """Mutual information-based feature selection."""
        start_time = time.time()

        if self.target_type == "regression":
            scores = mutual_info_regression(X.values, y.values, random_state=random_state or self.random_state)
        else:
            scores = mutual_info_classif(X.values, y.values, random_state=random_state or self.random_state)

        ranking = sorted(zip(X.columns, scores), key=lambda item: item[1], reverse=True)
        if top_n is not None:
            ranking = ranking[:top_n]
        selected = [name for name, score in ranking if score > 0]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected,
            scores=dict(ranking),
            method="mutual_information",
            n_features_original=X.shape[1],
            n_features_selected=len(selected),
            selection_time=selection_time
        )

    def univariate_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        k: Union[int, str] = "all",
        score_func: Optional[Callable] = None,
        mode: str = "k_best"
    ) -> FeatureSelectionResult:
        """Univariate feature selection using statistical tests."""
        start_time = time.time()

        if score_func is None:
            if self.target_type == "regression":
                score_func = f_regression
            else:
                score_func = f_classif

        if mode == "k_best":
            if k == "all":
                k = X.shape[1]
            selector = SelectKBest(score_func=score_func, k=k)
        elif mode == "percentile":
            if isinstance(k, str):
                k = 50  # Default 50%
            selector = SelectPercentile(score_func=score_func, percentile=k)
        else:
            raise ValueError("mode must be 'k_best' or 'percentile'")

        X_selected = selector.fit_transform(X, y)
        selected_mask = selector.get_support()
        selected_features = X.columns[selected_mask].tolist()
        scores = dict(zip(X.columns, selector.scores_))

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method=f"univariate_{mode}",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"pvalues": dict(zip(X.columns, selector.pvalues_))}
        )

    def correlation_filter(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        *,
        threshold: float = 0.85,
        method: str = "pearson"
    ) -> FeatureSelectionResult:
        """Filter features based on correlation."""
        start_time = time.time()

        if method == "pearson":
            corr_matrix = X.corr(method='pearson')
        elif method == "spearman":
            corr_matrix = X.corr(method='spearman')
        elif method == "kendall":
            corr_matrix = X.corr(method='kendall')
        else:
            raise ValueError("method must be 'pearson', 'spearman', or 'kendall'")

        # Remove highly correlated features
        corr_matrix = corr_matrix.abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = {column for column in upper.columns if any(upper[column] > threshold)}
        selected = [col for col in X.columns if col not in to_drop]

        # Calculate correlation with target if provided
        scores = {}
        if y is not None:
            for col in X.columns:
                if method == "pearson":
                    corr, _ = pearsonr(X[col], y)
                elif method == "spearman":
                    corr, _ = spearmanr(X[col], y)
                else:
                    corr = X[col].corr(y, method=method)
                scores[col] = abs(corr)
        else:
            scores = {col: 1.0 for col in selected}

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected,
            scores=scores,
            method=f"correlation_filter_{method}",
            n_features_original=X.shape[1],
            n_features_selected=len(selected),
            selection_time=selection_time,
            metadata={"threshold": threshold, "dropped_features": list(to_drop)}
        )

    def recursive_elimination(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        estimator: Optional[Any] = None,
        n_features_to_select: Optional[Union[int, float]] = None,
        step: int = 1,
        cv: int = 5
    ) -> FeatureSelectionResult:
        """Recursive feature elimination."""
        start_time = time.time()

        if estimator is None:
            if self.target_type == "regression":
                estimator = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
            else:
                estimator = RandomForestClassifier(n_estimators=100, random_state=self.random_state)

        if n_features_to_select is None:
            n_features_to_select = max(5, X.shape[1] // 2)

        if isinstance(n_features_to_select, float):
            n_features_to_select = int(X.shape[1] * n_features_to_select)

        selector = RFE(
            estimator=estimator,
            n_features_to_select=n_features_to_select,
            step=step
        )

        selector.fit(X, y)
        selected_mask = selector.get_support()
        selected_features = X.columns[selected_mask].tolist()

        # Get feature rankings
        rankings = selector.ranking_
        scores = dict(zip(X.columns, rankings))

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="recursive_elimination",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"estimator": str(type(estimator).__name__)}
        )

    def sequential_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        estimator: Optional[Any] = None,
        n_features_to_select: Optional[Union[int, float]] = None,
        direction: str = "forward",
        cv: int = 5
    ) -> FeatureSelectionResult:
        """Sequential feature selection."""
        start_time = time.time()

        if estimator is None:
            if self.target_type == "regression":
                estimator = RandomForestRegressor(n_estimators=50, random_state=self.random_state)
            else:
                estimator = RandomForestClassifier(n_estimators=50, random_state=self.random_state)

        if n_features_to_select is None:
            n_features_to_select = max(5, X.shape[1] // 2)

        if isinstance(n_features_to_select, float):
            n_features_to_select = int(X.shape[1] * n_features_to_select)

        selector = SequentialFeatureSelector(
            estimator=estimator,
            n_features_to_select=n_features_to_select,
            direction=direction,
            cv=cv,
            n_jobs=-1
        )

        selector.fit(X, y)
        selected_mask = selector.get_support()
        selected_features = X.columns[selected_mask].tolist()

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores={},  # Sequential selection doesn't provide scores
            method=f"sequential_{direction}",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"estimator": str(type(estimator).__name__), "cv": cv}
        )

    def lasso_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        alpha: Union[float, str] = "auto",
        max_features: Optional[int] = None
    ) -> FeatureSelectionResult:
        """LASSO-based feature selection."""
        start_time = time.time()

        if alpha == "auto":
            lasso = LassoCV(cv=5, random_state=self.random_state)
        else:
            lasso = Lasso(alpha=alpha, random_state=self.random_state)

        lasso.fit(X, y)

        # Get feature importance (absolute coefficients)
        importance = np.abs(lasso.coef_)
        scores = dict(zip(X.columns, importance))

        # Select features with non-zero coefficients
        selected_features = X.columns[importance > 0].tolist()

        # Limit features if specified
        if max_features and len(selected_features) > max_features:
            # Sort by importance and select top features
            sorted_features = sorted(zip(X.columns, importance), key=lambda x: x[1], reverse=True)
            selected_features = [feat for feat, _ in sorted_features[:max_features]]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="lasso_selection",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"alpha": lasso.alpha_ if hasattr(lasso, 'alpha_') else alpha}
        )

    def tree_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        estimator: Optional[Any] = None,
        top_n: Optional[int] = None
    ) -> FeatureSelectionResult:
        """Tree-based feature importance selection."""
        start_time = time.time()

        if estimator is None:
            if self.target_type == "regression":
                if HAS_XGBOOST:
                    estimator = xgb.XGBRegressor(n_estimators=100, random_state=self.random_state)
                elif HAS_LIGHTGBM:
                    estimator = lgb.LGBMRegressor(n_estimators=100, random_state=self.random_state)
                else:
                    estimator = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
            else:
                if HAS_XGBOOST:
                    estimator = xgb.XGBClassifier(n_estimators=100, random_state=self.random_state)
                elif HAS_LIGHTGBM:
                    estimator = lgb.LGBMClassifier(n_estimators=100, random_state=self.random_state)
                else:
                    estimator = RandomForestClassifier(n_estimators=100, random_state=self.random_state)

        estimator.fit(X, y)

        if hasattr(estimator, 'feature_importances_'):
            importance = estimator.feature_importances_
        else:
            # Fallback for estimators without feature_importances_
            importance = np.ones(X.shape[1]) / X.shape[1]

        scores = dict(zip(X.columns, importance))
        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if top_n is not None:
            selected_features = [feat for feat, _ in ranking[:top_n]]
        else:
            # Select features with importance > mean
            mean_importance = np.mean(importance)
            selected_features = [feat for feat, imp in scores.items() if imp > mean_importance]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="tree_importance",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"estimator": str(type(estimator).__name__)}
        )

    def shap_importance(
        self,
        model,
        X: pd.DataFrame,
        *,
        top_n: Optional[int] = None,
        nsamples: Optional[int] = None,
    ) -> FeatureSelectionResult:
        """SHAP-based feature importance."""
        try:
            import shap
        except ImportError:
            raise ImportError("shap package required for shap_importance")

        start_time = time.time()

        explainer = shap.Explainer(model, X)
        shap_values = explainer(X, max_evals=nsamples or (2 * X.shape[1] + 1))

        if hasattr(shap_values, 'values'):
            if len(shap_values.values.shape) == 3:  # Multi-output
                importance = np.abs(shap_values.values).mean(axis=(0, 1))
            else:
                importance = np.abs(shap_values.values).mean(axis=0)
        else:
            importance = np.abs(shap_values).mean(axis=0)

        scores = dict(zip(X.columns, importance))
        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if top_n is not None:
            selected_features = [feat for feat, _ in ranking[:top_n]]
        else:
            # Select features with importance > 0
            selected_features = [feat for feat, imp in scores.items() if imp > 0]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="shap_importance",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time
        )

    def boruta_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        estimator: Optional[Any] = None,
        max_iter: int = 100
    ) -> FeatureSelectionResult:
        """Boruta algorithm for feature selection."""
        if not HAS_BORUTA:
            raise ImportError("boruta package required for boruta_selection")

        start_time = time.time()

        if estimator is None:
            if self.target_type == "regression":
                estimator = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
            else:
                estimator = RandomForestClassifier(n_estimators=100, random_state=self.random_state)

        boruta = BorutaPy(
            estimator=estimator,
            n_estimators='auto',
            max_iter=max_iter,
            random_state=self.random_state
        )

        boruta.fit(X.values, y.values)

        selected_mask = boruta.support_
        selected_features = X.columns[selected_mask].tolist()

        # Get feature rankings
        rankings = boruta.ranking_
        scores = dict(zip(X.columns, rankings))

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="boruta_selection",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"n_iterations": boruta.n_estimators}
        )

    def permutation_importance(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        top_n: Optional[int] = None,
        cv: int = 5
    ) -> FeatureSelectionResult:
        """Permutation importance-based feature selection."""
        if not HAS_PERMUTATION:
            raise ImportError("scikit-learn>=0.24 required for permutation_importance")

        start_time = time.time()

        perm_importance = permutation_importance(model, X, y, cv=cv, random_state=self.random_state)

        scores = dict(zip(X.columns, perm_importance.importances_mean))
        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if top_n is not None:
            selected_features = [feat for feat, _ in ranking[:top_n]]
        else:
            # Select features with positive importance
            selected_features = [feat for feat, imp in scores.items() if imp > 0]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=scores,
            method="permutation_importance",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            metadata={"cv": cv}
        )

    def stability_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        method: str = "lasso",
        n_subsets: int = 50,
        subset_size: float = 0.8,
        threshold: float = 0.6,
        random_state: Optional[int] = None
    ) -> FeatureSelectionResult:
        """Stability selection for robust feature selection."""
        start_time = time.time()
        rng = np.random.RandomState(random_state or self.random_state)

        n_samples = X.shape[0]
        subset_size_int = int(n_samples * subset_size)

        selected_counts = {col: 0 for col in X.columns}

        for _ in range(n_subsets):
            # Create random subset
            subset_indices = rng.choice(n_samples, size=subset_size_int, replace=False)
            X_subset = X.iloc[subset_indices]
            y_subset = y.iloc[subset_indices]

            # Apply feature selection method
            if method == "lasso":
                result = self.lasso_selection(X_subset, y_subset, alpha="auto")
            elif method == "tree":
                result = self.tree_importance(X_subset, y_subset)
            else:
                result = self.univariate_selection(X_subset, y_subset, k="all")

            # Count selected features
            for feature in result.selected_features:
                selected_counts[feature] += 1

        # Calculate stability scores
        stability_scores = {col: count / n_subsets for col, count in selected_counts.items()}

        # Select features above threshold
        selected_features = [col for col, score in stability_scores.items() if score >= threshold]

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=stability_scores,
            method=f"stability_{method}",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            selection_time=selection_time,
            stability_score=np.mean(list(stability_scores.values())),
            metadata={"n_subsets": n_subsets, "threshold": threshold}
        )

    def autocorrelation_filter(
        self,
        X: pd.DataFrame,
        *,
        threshold: float = 0.85,
    ) -> FeatureSelectionResult:
        """Filter features based on autocorrelation (multicollinearity)."""
        start_time = time.time()

        corr = X.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = {column for column in upper.columns if any(upper[column] > threshold)}
        selected = [col for col in X.columns if col not in to_drop]
        scores = {col: 1.0 for col in selected}

        selection_time = time.time() - start_time

        return FeatureSelectionResult(
            selected_features=selected,
            scores=scores,
            method="autocorrelation_filter",
            n_features_original=X.shape[1],
            n_features_selected=len(selected),
            selection_time=selection_time,
            metadata={"threshold": threshold, "dropped_features": list(to_drop)}
        )


# =============================================================================
# ADVANCED FEATURE SELECTION CLASSES
# =============================================================================

class EnsembleFeatureSelector:
    """Ensemble feature selection combining multiple methods."""

    def __init__(self, selectors: List[FeatureSelector], voting_threshold: float = 0.5):
        self.selectors = selectors
        self.voting_threshold = voting_threshold

    def select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        methods: List[str] = None
    ) -> FeatureSelectionResult:
        """Ensemble feature selection using voting."""
        if methods is None:
            methods = ['mutual_information', 'tree_importance', 'lasso_selection']

        all_results = []
        vote_counts = {col: 0 for col in X.columns}

        for selector in self.selectors:
            for method in methods:
                try:
                    if method == 'mutual_information':
                        result = selector.mutual_information(X, y)
                    elif method == 'tree_importance':
                        result = selector.tree_importance(X, y)
                    elif method == 'lasso_selection':
                        result = selector.lasso_selection(X, y)
                    elif method == 'correlation_filter':
                        result = selector.correlation_filter(X, y)
                    else:
                        continue

                    all_results.append(result)

                    # Count votes
                    for feature in result.selected_features:
                        vote_counts[feature] += 1

                except Exception as e:
                    warnings.warn(f"Feature selection method {method} failed: {e}")
                    continue

        # Select features based on voting
        n_methods = len(all_results)
        threshold = int(n_methods * self.voting_threshold)

        selected_features = [col for col, votes in vote_counts.items() if votes >= threshold]

        # Combine scores from all methods
        combined_scores = {}
        for col in X.columns:
            scores = [result.scores.get(col, 0) for result in all_results if col in result.scores]
            combined_scores[col] = np.mean(scores) if scores else 0

        return FeatureSelectionResult(
            selected_features=selected_features,
            scores=combined_scores,
            method="ensemble_selection",
            n_features_original=X.shape[1],
            n_features_selected=len(selected_features),
            metadata={"n_methods": n_methods, "threshold": threshold}
        )


class MultiObjectiveFeatureSelector:
    """Multi-objective feature selection optimizing multiple criteria."""

    def __init__(self, objectives: List[Callable] = None):
        self.objectives = objectives or [
            lambda result: len(result.selected_features),  # Minimize number of features
            lambda result: -np.mean(list(result.scores.values())),  # Maximize average score
            lambda result: result.stability_score or 0  # Maximize stability
        ]

    def optimize_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        methods: List[str] = None,
        n_generations: int = 50
    ) -> FeatureSelectionResult:
        """Multi-objective optimization of feature selection."""
        try:
            import pymoo
        except ImportError:
            raise ImportError("pymoo required for multi-objective feature selection")

        if methods is None:
            methods = ['lasso_selection', 'tree_importance', 'stability_selection']

        # Generate candidate solutions
        candidates = []
        selector = FeatureSelector()

        for method in methods:
            try:
                if method == 'lasso_selection':
                    result = selector.lasso_selection(X, y)
                elif method == 'tree_importance':
                    result = selector.tree_importance(X, y)
                elif method == 'stability_selection':
                    result = selector.stability_selection(X, y)
                else:
                    continue

                candidates.append(result)
            except:
                continue

        if not candidates:
            raise RuntimeError("No valid feature selection results generated")

        # For simplicity, return the best candidate based on combined score
        best_result = max(candidates, key=lambda r: np.mean(list(r.scores.values())))

        return best_result


class AutomatedFeatureSelector:
    """Automated feature selection with model validation."""

    def __init__(self, cv_folds: int = 5, scoring: str = None):
        self.cv_folds = cv_folds
        self.scoring = scoring
        self.selector = FeatureSelector()

    def select_with_validation(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        methods: List[str] = None,
        base_estimator = None
    ) -> FeatureSelectionResult:
        """Select features with cross-validation performance validation."""
        from sklearn.model_selection import cross_val_score

        if methods is None:
            methods = ['mutual_information', 'tree_importance', 'lasso_selection']

        if base_estimator is None:
            from sklearn.ensemble import RandomForestRegressor
            base_estimator = RandomForestRegressor(n_estimators=50, random_state=42)

        if self.scoring is None:
            self.scoring = 'neg_mean_squared_error'

        best_result = None
        best_cv_score = float('-inf')

        for method in methods:
            try:
                # Apply feature selection
                if method == 'mutual_information':
                    result = self.selector.mutual_information(X, y)
                elif method == 'tree_importance':
                    result = self.selector.tree_importance(X, y)
                elif method == 'lasso_selection':
                    result = self.selector.lasso_selection(X, y)
                else:
                    continue

                if not result.selected_features:
                    continue

                # Validate with cross-validation
                X_selected = X[result.selected_features]
                cv_scores = cross_val_score(
                    base_estimator, X_selected, y,
                    cv=self.cv_folds, scoring=self.scoring
                )

                mean_cv_score = np.mean(cv_scores)

                if mean_cv_score > best_cv_score:
                    best_cv_score = mean_cv_score
                    best_result = result
                    best_result.cv_scores = cv_scores.tolist()

            except Exception as e:
                warnings.warn(f"Feature selection method {method} failed validation: {e}")
                continue

        if best_result is None:
            # Fallback to simple selection
            best_result = self.selector.mutual_information(X, y)

        return best_result


class FeatureSelectionPipeline(BaseEstimator, TransformerMixin):
    """Scikit-learn compatible feature selection pipeline."""

    def __init__(
        self,
        method: str = "mutual_information",
        target_type: str = "regression",
        **kwargs
    ):
        self.method = method
        self.target_type = target_type
        self.kwargs = kwargs
        self.selector = FeatureSelector(target_type=target_type)
        self.selected_features_ = []

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit the feature selector."""
        if y is None:
            raise ValueError("y cannot be None for feature selection")

        # Apply feature selection
        if self.method == "mutual_information":
            result = self.selector.mutual_information(X, y, **self.kwargs)
        elif self.method == "tree_importance":
            result = self.selector.tree_importance(X, y, **self.kwargs)
        elif self.method == "lasso_selection":
            result = self.selector.lasso_selection(X, y, **self.kwargs)
        elif self.method == "correlation_filter":
            result = self.selector.correlation_filter(X, y, **self.kwargs)
        else:
            raise ValueError(f"Unknown method: {self.method}")

        self.selected_features_ = result.selected_features
        self.scores_ = result.scores

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data by selecting features."""
        if not self.selected_features_:
            raise RuntimeError("Pipeline must be fitted before transform")

        available_features = [col for col in self.selected_features_ if col in X.columns]
        if not available_features:
            warnings.warn("No selected features available in input data")
            return X.iloc[:, :0]  # Return empty DataFrame with same index

        return X[available_features]

    def get_feature_names_out(self, input_features=None):
        """Get output feature names."""
        return self.selected_features_


__all__ = [
    "FeatureSelector",
    "FeatureSelectionResult",
    "EnsembleFeatureSelector",
    "MultiObjectiveFeatureSelector",
    "AutomatedFeatureSelector",
    "FeatureSelectionPipeline",
]

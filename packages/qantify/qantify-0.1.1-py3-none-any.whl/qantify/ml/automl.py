"""Advanced AutoML runner with neural architecture search, automated preprocessing, and model stacking."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import (
    GradientBoostingRegressor,
    GradientBoostingClassifier,
    RandomForestRegressor,
    RandomForestClassifier,
    ExtraTreesRegressor,
    ExtraTreesClassifier,
    AdaBoostRegressor,
    AdaBoostClassifier,
    StackingRegressor,
    StackingClassifier,
    VotingRegressor,
    VotingClassifier,
)
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression,
    Ridge,
    Lasso,
    ElasticNet,
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
    KFold,
    TimeSeriesSplit,
)
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    MaxAbsScaler,
    Normalizer,
    PowerTransformer,
    QuantileTransformer,
)
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_selection import (
    SelectKBest,
    SelectPercentile,
    RFE,
    SelectFromModel,
)
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    f1_score,
    roc_auc_score,
    precision_score,
    recall_score,
)
from math import sqrt

# Optional dependencies
try:
    from xgboost import XGBRegressor, XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from lightgbm import LGBMRegressor, LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    from catboost import CatBoostRegressor, CatBoostClassifier  # type: ignore
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

try:
    import optuna  # type: ignore
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False

try:
    from ray import tune  # type: ignore
    HAS_RAY = True
except ImportError:
    HAS_RAY = False

try:
    from boruta import BorutaPy  # type: ignore
    HAS_BORUTA = True
except ImportError:
    HAS_BORUTA = False


@dataclass(slots=True)
class ModelConfig:
    """Configuration for a single model in AutoML."""
    name: str
    estimator: Any
    param_grid: Dict[str, Sequence[Any]]
    preprocessor: Optional[Any] = None
    feature_selector: Optional[Any] = None
    target_type: str = "regression"  # "regression" or "classification"


@dataclass(slots=True)
class AutoMLResult:
    """Result from AutoML training."""
    model_name: str
    params: Dict[str, Any]
    score: float
    fitted_estimator: Any
    cv_scores: Optional[List[float]] = None
    training_time: float = 0.0
    feature_importance: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineConfig:
    """Configuration for preprocessing pipeline."""
    scaler: str = "standard"
    feature_selection: Optional[str] = None
    feature_selection_k: Optional[int] = None
    polynomial_features: Optional[int] = None
    custom_transformers: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class NeuralArchitectureResult:
    """Result from neural architecture search."""
    architecture: Dict[str, Any]
    score: float
    model: Any
    training_history: Dict[str, List[float]]
    search_time: float


@dataclass(slots=True)
class StackingResult:
    """Result from model stacking."""
    final_estimator: Any
    base_estimators: List[Any]
    score: float
    cv_scores: List[float]
    feature_importance: Optional[Dict[str, float]] = None


class AutoMLRunner:
    """Advanced AutoML runner with automated preprocessing and feature selection."""

    def __init__(
        self,
        *,
        models: Optional[Iterable[ModelConfig]] = None,
        scoring: Optional[Callable] = None,
        random_state: Optional[int] = None,
        test_size: float = 0.2,
        cv_folds: int = 5,
        target_type: str = "regression",
        preprocessing_configs: Optional[List[PipelineConfig]] = None,
    ) -> None:
        self.target_type = target_type
        self.scoring = scoring or self._get_default_scorer()
        self.random_state = random_state or 42
        self.test_size = test_size
        self.cv_folds = cv_folds
        self.models = list(models or self._default_models())
        self.preprocessing_configs = preprocessing_configs or [PipelineConfig()]

    def _get_default_scorer(self) -> Callable:
        """Get default scoring function based on target type."""
        if self.target_type == "regression":
            return lambda y_true, y_pred: -sqrt(mean_squared_error(y_true, y_pred))
        else:
            return lambda y_true, y_pred: accuracy_score(y_true, y_pred)

    def _default_models(self) -> List[ModelConfig]:
        """Generate default model configurations."""
        configs = []

        # Tree-based models
        configs.extend([
            ModelConfig(
                name="random_forest",
                estimator=RandomForestRegressor(random_state=self.random_state) if self.target_type == "regression"
                         else RandomForestClassifier(random_state=self.random_state),
                param_grid={
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 5, 10, 20],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                },
                target_type=self.target_type,
            ),
            ModelConfig(
                name="extra_trees",
                estimator=ExtraTreesRegressor(random_state=self.random_state) if self.target_type == "regression"
                         else ExtraTreesClassifier(random_state=self.random_state),
                param_grid={
                    "n_estimators": [50, 100, 200],
                    "max_depth": [None, 5, 10, 20],
                    "min_samples_split": [2, 5, 10],
                },
                target_type=self.target_type,
            ),
                ModelConfig(
                name="gradient_boosting",
                estimator=GradientBoostingRegressor(random_state=self.random_state) if self.target_type == "regression"
                         else GradientBoostingClassifier(random_state=self.random_state),
                param_grid={
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200],
                    "max_depth": [3, 5, 7],
                    "subsample": [0.8, 0.9, 1.0],
                },
                target_type=self.target_type,
            ),
        ])

        # Optional boosting libraries
        if HAS_XGBOOST:
            configs.append(ModelConfig(
                    name="xgboost",
                estimator=XGBRegressor(random_state=self.random_state, eval_metric="rmse") if self.target_type == "regression"
                         else XGBClassifier(random_state=self.random_state, eval_metric="logloss"),
                param_grid={
                    "max_depth": [3, 5, 7],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200],
                    "subsample": [0.8, 0.9, 1.0],
                    "colsample_bytree": [0.8, 0.9, 1.0],
                },
                target_type=self.target_type,
            ))

        if HAS_LIGHTGBM:
            configs.append(ModelConfig(
                name="lightgbm",
                estimator=LGBMRegressor(random_state=self.random_state) if self.target_type == "regression"
                         else LGBMClassifier(random_state=self.random_state),
                param_grid={
                    "max_depth": [3, 5, 7, -1],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200],
                    "subsample": [0.8, 0.9, 1.0],
                    "colsample_bytree": [0.8, 0.9, 1.0],
                },
                target_type=self.target_type,
            ))

        if HAS_CATBOOST:
            configs.append(ModelConfig(
                name="catboost",
                estimator=CatBoostRegressor(random_state=self.random_state, verbose=False) if self.target_type == "regression"
                         else CatBoostClassifier(random_state=self.random_state, verbose=False),
                param_grid={
                    "depth": [3, 5, 7],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "iterations": [50, 100, 200],
                    "l2_leaf_reg": [1, 3, 5, 10],
                },
                target_type=self.target_type,
            ))

        # Linear models
        if self.target_type == "regression":
            configs.extend([
                ModelConfig(
                    name="linear_regression",
                    estimator=LinearRegression(),
                    param_grid={},
                    target_type=self.target_type,
                ),
                ModelConfig(
                    name="ridge",
                    estimator=Ridge(random_state=self.random_state),
                    param_grid={"alpha": [0.1, 1.0, 10.0, 100.0]},
                    target_type=self.target_type,
                ),
                ModelConfig(
                    name="lasso",
                    estimator=Lasso(random_state=self.random_state),
                    param_grid={"alpha": [0.001, 0.01, 0.1, 1.0]},
                    target_type=self.target_type,
                ),
                ModelConfig(
                    name="elastic_net",
                    estimator=ElasticNet(random_state=self.random_state),
                    param_grid={
                        "alpha": [0.001, 0.01, 0.1, 1.0],
                        "l1_ratio": [0.1, 0.5, 0.9],
                    },
                    target_type=self.target_type,
                ),
            ])
        else:
            configs.extend([
                ModelConfig(
                    name="logistic_regression",
                    estimator=LogisticRegression(random_state=self.random_state, max_iter=1000),
                    param_grid={"C": [0.1, 1.0, 10.0, 100.0]},
                    target_type=self.target_type,
                ),
                ModelConfig(
                    name="naive_bayes",
                    estimator=GaussianNB(),
                    param_grid={},
                    target_type=self.target_type,
                ),
            ])

        # Other models
        configs.extend([
            ModelConfig(
                name="svm",
                estimator=SVR() if self.target_type == "regression" else SVC(random_state=self.random_state),
                param_grid={
                    "C": [0.1, 1.0, 10.0],
                    "kernel": ["linear", "rbf", "poly"],
                    "gamma": ["scale", "auto", 0.001, 0.01, 0.1],
                },
                target_type=self.target_type,
            ),
            ModelConfig(
                name="knn",
                estimator=KNeighborsRegressor() if self.target_type == "regression" else KNeighborsClassifier(),
                param_grid={
                    "n_neighbors": [3, 5, 7, 9, 11],
                    "weights": ["uniform", "distance"],
                    "p": [1, 2],
                },
                target_type=self.target_type,
            ),
        ])

        return configs

    def run(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        search: str = "random",
        n_iter: Optional[int] = None,
        optimize_preprocessing: bool = True,
    ) -> AutoMLResult:
        """Run AutoML with automated preprocessing optimization."""
        start_time = time.time()

        # Determine target type from data if not specified
        if self.target_type == "auto":
            unique_values = y.nunique()
            self.target_type = "classification" if unique_values <= 20 else "regression"

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size,
            random_state=self.random_state,
            stratify=y if self.target_type == "classification" else None
        )

        results: List[AutoMLResult] = []
        best_score = float("-inf")
        best_result = None

        # Try different preprocessing configurations
        for prep_config in self.preprocessing_configs if optimize_preprocessing else [PipelineConfig()]:
            for config in self.models:
                if config.target_type != self.target_type:
                    continue

                try:
                    result = self._optimize_model(
                        config, prep_config, X_train, X_test, y_train, y_test,
                        search=search, n_iter=n_iter
                    )

                    if result.score > best_score:
                        best_score = result.score
                        best_result = result

                    results.append(result)

                except Exception as e:
                    warnings.warn(f"Model {config.name} failed: {e}")
                    continue

        if best_result is None:
            raise RuntimeError("AutoML did not produce any valid results.")

        best_result.training_time = time.time() - start_time
        return best_result

    def _optimize_model(
        self,
        config: ModelConfig,
        prep_config: PipelineConfig,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        search: str,
        n_iter: Optional[int]
    ) -> AutoMLResult:
        """Optimize a single model with preprocessing."""
        # Build preprocessing pipeline
        preprocessor = self._build_preprocessor(prep_config)

        # Generate parameter combinations
        rng = np.random.default_rng(self.random_state)
        param_list = list(self._generate_params(
            config.param_grid, search=search, rng=rng, n_iter=n_iter
        ))

        best_score = float("-inf")
        best_estimator = None
        best_params = {}
        best_cv_scores = []

        for params in param_list:
            try:
                # Build full pipeline
                pipeline = self._build_full_pipeline(
                    preprocessor, config.estimator, params, config.feature_selector
                )

                # Fit and evaluate
                pipeline.fit(X_train, y_train)
                preds = pipeline.predict(X_test)
                score = self.scoring(y_test, preds)

                # Cross-validation for stability
                cv_scores = cross_val_score(
                    pipeline, X_train, y_train,
                    cv=self._get_cv_strategy(),
                    scoring=self._get_cv_scorer(),
                    n_jobs=-1
                )

                cv_mean = np.mean(cv_scores)

                if cv_mean > best_score:
                    best_score = cv_mean
                    best_estimator = pipeline
                    best_params = params
                    best_cv_scores = cv_scores.tolist()

            except Exception as e:
                warnings.warn(f"Parameter combination failed: {e}")
                continue

        if best_estimator is None:
            raise RuntimeError(f"No valid parameter combinations for {config.name}")

        # Extract feature importance if available
        feature_importance = self._extract_feature_importance(best_estimator, X_train.columns)

        return AutoMLResult(
                    model_name=config.name,
                    params=best_params,
                    score=best_score,
                    fitted_estimator=best_estimator,
            cv_scores=best_cv_scores,
            feature_importance=feature_importance,
            metadata={"preprocessing": prep_config.__dict__}
        )

    def _build_preprocessor(self, config: PipelineConfig) -> Pipeline:
        """Build preprocessing pipeline."""
        steps = []

        # Scaling
        if config.scaler == "standard":
            steps.append(("scaler", StandardScaler()))
        elif config.scaler == "robust":
            steps.append(("scaler", RobustScaler()))
        elif config.scaler == "minmax":
            steps.append(("scaler", MinMaxScaler()))
        elif config.scaler == "maxabs":
            steps.append(("scaler", MaxAbsScaler()))
        elif config.scaler == "normalizer":
            steps.append(("scaler", Normalizer()))
        elif config.scaler == "power":
            steps.append(("scaler", PowerTransformer()))
        elif config.scaler == "quantile":
            steps.append(("scaler", QuantileTransformer(output_distribution='normal')))

        # Feature selection
        if config.feature_selection:
            if config.feature_selection == "kbest":
                k = config.feature_selection_k or 10
                if self.target_type == "regression":
                    from sklearn.feature_selection import f_regression
                    steps.append(("feature_selection", SelectKBest(f_regression, k=k)))
                else:
                    from sklearn.feature_selection import f_classif
                    steps.append(("feature_selection", SelectKBest(f_classif, k=k)))
            elif config.feature_selection == "percentile":
                percentile = min(config.feature_selection_k or 50, 100)
                if self.target_type == "regression":
                    from sklearn.feature_selection import f_regression
                    steps.append(("feature_selection", SelectPercentile(f_regression, percentile=percentile)))
                else:
                    from sklearn.feature_selection import f_classif
                    steps.append(("feature_selection", SelectPercentile(f_classif, percentile=percentile)))

        # Custom transformers
        for i, transformer in enumerate(config.custom_transformers):
            steps.append((f"custom_{i}", transformer))

        return Pipeline(steps)

    def _build_full_pipeline(
        self,
        preprocessor: Pipeline,
        estimator: Any,
        params: Dict[str, Any],
        feature_selector: Optional[Any] = None
    ) -> Pipeline:
        """Build complete pipeline with model."""
        # Clone and update estimator with params
        base_estimator = estimator.__class__(**{**estimator.get_params(), **params})

        steps = [("preprocessor", preprocessor), ("model", base_estimator)]

        if feature_selector:
            steps.insert(1, ("feature_selector", feature_selector))

        return Pipeline(steps)

    def _generate_params(
        self,
        grid: Dict[str, Sequence[Any]],
        *,
        search: str,
        rng: np.random.Generator,
        n_iter: Optional[int],
    ) -> Iterable[Dict[str, Any]]:
        """Generate parameter combinations."""
        keys = list(grid.keys())
        values = [list(grid[key]) for key in keys]

        if search == "grid":
            from itertools import product
            for combination in product(*values):
                yield dict(zip(keys, combination))
        elif search == "random":
            total = n_iter or min(len(keys) * 5, 50)
            for _ in range(total):
                yield {key: rng.choice(grid[key]) for key in keys}
        else:
            raise ValueError("search must be 'grid' or 'random'")

    def _get_cv_strategy(self):
        """Get appropriate cross-validation strategy."""
        if hasattr(self, '_is_time_series') and self._is_time_series:
            return TimeSeriesSplit(n_splits=self.cv_folds)
        elif self.target_type == "classification":
            return StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        else:
            return KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)

    def _get_cv_scorer(self) -> str:
        """Get appropriate cross-validation scorer."""
        if self.target_type == "regression":
            return "neg_mean_squared_error"
        else:
            return "accuracy"

    def _extract_feature_importance(self, pipeline: Pipeline, feature_names: pd.Index) -> Optional[Dict[str, float]]:
        """Extract feature importance from trained pipeline."""
        try:
            model = pipeline.named_steps.get('model')
            if hasattr(model, 'feature_importances_'):
                return dict(zip(feature_names, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                # For linear models
                importance = np.abs(model.coef_)
                if importance.ndim > 1:
                    importance = importance.mean(axis=0)
                return dict(zip(feature_names, importance))
        except:
            pass
        return None


# =============================================================================
# NEURAL ARCHITECTURE SEARCH
# =============================================================================

class NeuralNetwork(nn.Module):
    """Flexible neural network architecture for NAS."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        architecture: Dict[str, Any],
        task_type: str = "regression"
    ):
        super().__init__()
        self.task_type = task_type

        layers = []
        prev_dim = input_dim

        # Hidden layers
        for i, layer_config in enumerate(architecture.get('layers', [])):
            layer_type = layer_config.get('type', 'linear')
            units = layer_config.get('units', 64)
            activation = layer_config.get('activation', 'relu')
            dropout = layer_config.get('dropout', 0.0)
            batch_norm = layer_config.get('batch_norm', False)

            # Linear layer
            layers.append(nn.Linear(prev_dim, units))

            # Batch normalization
            if batch_norm:
                layers.append(nn.BatchNorm1d(units))

            # Activation
            if activation == 'relu':
                layers.append(nn.ReLU())
            elif activation == 'tanh':
                layers.append(nn.Tanh())
            elif activation == 'sigmoid':
                layers.append(nn.Sigmoid())
            elif activation == 'leaky_relu':
                layers.append(nn.LeakyReLU(0.1))

            # Dropout
            if dropout > 0:
                layers.append(nn.Dropout(dropout))

            prev_dim = units

        # Output layer
        self.hidden = nn.Sequential(*layers)
        self.output = nn.Linear(prev_dim, output_dim)

        # Output activation
        if task_type == "classification":
            self.output_activation = nn.Softmax(dim=1)
        else:
            self.output_activation = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.hidden(x)
        x = self.output(x)
        if self.output_activation:
            x = self.output_activation(x)
        return x


class NeuralArchitectureSearch:
    """Neural Architecture Search for automated neural network design."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        task_type: str = "regression",
        max_layers: int = 5,
        max_units: int = 512,
        random_state: int = 42
    ):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.task_type = task_type
        self.max_layers = max_layers
        self.max_units = max_units
        self.random_state = random_state

    def search(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        n_trials: int = 50,
        epochs: int = 100,
        batch_size: int = 32,
        patience: int = 10,
        optimizer_name: str = "optuna" if HAS_OPTUNA else "random"
    ) -> NeuralArchitectureResult:
        """Perform neural architecture search."""
        if not HAS_PYTORCH:
            raise ImportError("PyTorch required for neural architecture search")

        start_time = time.time()

        if optimizer_name == "optuna" and HAS_OPTUNA:
            best_architecture, best_score, best_model, history = self._optuna_search(
                X, y, n_trials, epochs, batch_size, patience
            )
        else:
            best_architecture, best_score, best_model, history = self._random_search(
                X, y, n_trials, epochs, batch_size, patience
            )

        search_time = time.time() - start_time

        return NeuralArchitectureResult(
            architecture=best_architecture,
            score=best_score,
            model=best_model,
            training_history=history,
            search_time=search_time
        )

    def _random_search(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials: int,
        epochs: int,
        batch_size: int,
        patience: int
    ) -> Tuple[Dict[str, Any], float, Any, Dict[str, List[float]]]:
        """Random neural architecture search."""
        best_score = float('-inf')
        best_architecture = None
        best_model = None
        best_history = {}

        rng = np.random.RandomState(self.random_state)

        for trial in range(n_trials):
            # Generate random architecture
            architecture = self._generate_random_architecture(rng)

            # Train and evaluate
            try:
                score, model, history = self._train_evaluate_architecture(
                    architecture, X, y, epochs, batch_size, patience
                )

                if score > best_score:
                    best_score = score
                    best_architecture = architecture
                    best_model = model
                    best_history = history

            except Exception as e:
                warnings.warn(f"Trial {trial} failed: {e}")
                continue

        return best_architecture, best_score, best_model, best_history

    def _optuna_search(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials: int,
        epochs: int,
        batch_size: int,
        patience: int
    ) -> Tuple[Dict[str, Any], float, Any, Dict[str, List[float]]]:
        """Optuna-based neural architecture search."""
        def objective(trial):
            # Generate architecture from trial
            architecture = self._generate_optuna_architecture(trial)

            try:
                score, _, _ = self._train_evaluate_architecture(
                    architecture, X, y, epochs, batch_size, patience
                )
                return score
            except:
                return float('-inf')

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        # Get best architecture and retrain for history
        best_architecture = self._generate_optuna_architecture(study.best_trial)
        best_score, best_model, best_history = self._train_evaluate_architecture(
            best_architecture, X, y, epochs, batch_size, patience
        )

        return best_architecture, best_score, best_model, best_history

    def _generate_random_architecture(self, rng: np.random.RandomState) -> Dict[str, Any]:
        """Generate random neural architecture."""
        n_layers = rng.randint(1, self.max_layers + 1)
        layers = []

        for i in range(n_layers):
            layer = {
                'type': 'linear',
                'units': rng.randint(16, self.max_units + 1),
                'activation': rng.choice(['relu', 'tanh', 'sigmoid', 'leaky_relu']),
                'dropout': rng.uniform(0, 0.5),
                'batch_norm': rng.choice([True, False])
            }
            layers.append(layer)

        return {'layers': layers}

    def _generate_optuna_architecture(self, trial: 'optuna.Trial') -> Dict[str, Any]:
        """Generate architecture using Optuna."""
        n_layers = trial.suggest_int('n_layers', 1, self.max_layers)
        layers = []

        for i in range(n_layers):
            layer = {
                'type': 'linear',
                'units': trial.suggest_int(f'units_{i}', 16, self.max_units),
                'activation': trial.suggest_categorical(f'activation_{i}', ['relu', 'tanh', 'sigmoid', 'leaky_relu']),
                'dropout': trial.suggest_float(f'dropout_{i}', 0.0, 0.5),
                'batch_norm': trial.suggest_categorical(f'batch_norm_{i}', [True, False])
            }
            layers.append(layer)

        return {'layers': layers}

    def _train_evaluate_architecture(
        self,
        architecture: Dict[str, Any],
        X: pd.DataFrame,
        y: pd.Series,
        epochs: int,
        batch_size: int,
        patience: int
    ) -> Tuple[float, Any, Dict[str, List[float]]]:
        """Train and evaluate a neural architecture."""
        # Convert to tensors
        X_tensor = torch.FloatTensor(X.values)
        if self.task_type == "classification":
            y_tensor = torch.LongTensor(y.values)
        else:
            y_tensor = torch.FloatTensor(y.values).unsqueeze(1)

        # Create data loader
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Create model
        model = NeuralNetwork(
            self.input_dim, self.output_dim,
            architecture, self.task_type
        )

        # Loss and optimizer
        if self.task_type == "regression":
            criterion = nn.MSELoss()
        else:
            criterion = nn.CrossEntropyLoss()

        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        # Training loop
        history = {'loss': [], 'val_loss': []}
        best_loss = float('inf')
        patience_counter = 0
        best_model_state = None

        # Split for validation
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        for epoch in range(epochs):
            # Training
            model.train()
            train_loss = 0.0
            for inputs, targets in train_loader:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            train_loss /= len(train_loader)

            # Validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for inputs, targets in val_loader:
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)
                    val_loss += loss.item()

            val_loss /= len(val_loader)

            history['loss'].append(train_loss)
            history['val_loss'].append(val_loss)

            # Early stopping
            if val_loss < best_loss:
                best_loss = val_loss
                patience_counter = 0
                best_model_state = model.state_dict()
            else:
                patience_counter += 1

            if patience_counter >= patience:
                break

        # Load best model
        if best_model_state:
            model.load_state_dict(best_model_state)

        # Calculate score
        model.eval()
        with torch.no_grad():
            preds = model(X_tensor)
            if self.task_type == "regression":
                score = -mean_squared_error(y.values, preds.numpy().flatten())
            else:
                score = accuracy_score(y.values, preds.argmax(dim=1).numpy())

        return score, model, history


# =============================================================================
# AUTOMATED PIPELINE OPTIMIZATION
# =============================================================================

class AutomatedPipelineOptimizer:
    """Automated pipeline optimization with preprocessing and feature engineering."""

    def __init__(
        self,
        target_type: str = "regression",
        random_state: int = 42,
        cv_folds: int = 5
    ):
        self.target_type = target_type
        self.random_state = random_state
        self.cv_folds = cv_folds

    def optimize_pipeline(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        include_feature_engineering: bool = True,
        include_feature_selection: bool = True,
        max_pipeline_complexity: int = 3,
        n_trials: int = 50
    ) -> Dict[str, Any]:
        """Optimize complete ML pipeline."""
        best_pipeline = None
        best_score = float('-inf')
        best_config = {}

        for trial in range(n_trials):
            try:
                # Generate pipeline configuration
                config = self._generate_pipeline_config(
                    X,
                    include_feature_engineering,
                    include_feature_selection,
                    max_pipeline_complexity
                )

                # Build and evaluate pipeline
                pipeline = self._build_optimized_pipeline(config, X)
                score = self._evaluate_pipeline(pipeline, X, y)

                if score > best_score:
                    best_score = score
                    best_pipeline = pipeline
                    best_config = config

            except Exception as e:
                warnings.warn(f"Pipeline trial {trial} failed: {e}")
                continue

        return {
            'pipeline': best_pipeline,
            'config': best_config,
            'score': best_score
        }

    def _generate_pipeline_config(
        self,
        X: pd.DataFrame,
        include_fe: bool,
        include_fs: bool,
        max_complexity: int
    ) -> Dict[str, Any]:
        """Generate random pipeline configuration."""
        config = {}

        # Preprocessing
        config['scaler'] = np.random.choice([
            'standard', 'robust', 'minmax', 'power', 'quantile', None
        ])

        # Feature engineering
        if include_fe and np.random.random() < 0.7:
            config['feature_engineering'] = np.random.choice([
                'polynomial', 'interaction', 'binning', None
            ], p=[0.3, 0.3, 0.2, 0.2])

        # Feature selection
        if include_fs and np.random.random() < 0.8:
            config['feature_selection'] = np.random.choice([
                'kbest', 'percentile', 'rfe', 'lasso', None
            ])
            if config['feature_selection']:
                config['k_features'] = np.random.randint(5, min(50, len(X.columns)))

        # Model selection
        config['model'] = np.random.choice([
            'random_forest', 'xgboost', 'lightgbm', 'linear', 'svm'
        ])

        return config

    def _build_optimized_pipeline(self, config: Dict[str, Any], X: pd.DataFrame) -> Pipeline:
        """Build pipeline from configuration."""
        steps = []

        # Scaling
        if config.get('scaler'):
            if config['scaler'] == 'standard':
                steps.append(('scaler', StandardScaler()))
            elif config['scaler'] == 'robust':
                steps.append(('scaler', RobustScaler()))
            elif config['scaler'] == 'minmax':
                steps.append(('scaler', MinMaxScaler()))
            elif config['scaler'] == 'power':
                steps.append(('scaler', PowerTransformer()))
            elif config['scaler'] == 'quantile':
                steps.append(('scaler', QuantileTransformer()))

        # Feature engineering
        if config.get('feature_engineering') == 'polynomial':
            from sklearn.preprocessing import PolynomialFeatures
            steps.append(('poly', PolynomialFeatures(degree=2, include_bias=False)))
        elif config.get('feature_engineering') == 'interaction':
            from sklearn.preprocessing import PolynomialFeatures
            steps.append(('interaction', PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)))

        # Feature selection
        if config.get('feature_selection'):
            k = config.get('k_features', 10)
            if config['feature_selection'] == 'kbest':
                if self.target_type == 'regression':
                    from sklearn.feature_selection import f_regression
                    steps.append(('feature_selection', SelectKBest(f_regression, k=k)))
                else:
                    from sklearn.feature_selection import f_classif
                    steps.append(('feature_selection', SelectKBest(f_classif, k=k)))
            elif config['feature_selection'] == 'percentile':
                percentile = min(k * 100 // len(X.columns), 100)
                if self.target_type == 'regression':
                    from sklearn.feature_selection import f_regression
                    steps.append(('feature_selection', SelectPercentile(f_regression, percentile=percentile)))
                else:
                    from sklearn.feature_selection import f_classif
                    steps.append(('feature_selection', SelectPercentile(f_classif, percentile=percentile)))
            elif config['feature_selection'] == 'rfe':
                if config['model'] in ['linear', 'svm']:
                    steps.append(('feature_selection', RFE(estimator=LinearRegression(), n_features_to_select=k)))
            elif config['feature_selection'] == 'lasso':
                if self.target_type == 'regression':
                    steps.append(('feature_selection', SelectFromModel(Lasso(alpha=0.01))))

        # Model
        if config['model'] == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, random_state=self.random_state) \
                if self.target_type == 'regression' else \
                RandomForestClassifier(n_estimators=100, random_state=self.random_state)
        elif config['model'] == 'xgboost' and HAS_XGBOOST:
            model = XGBRegressor(n_estimators=100, random_state=self.random_state) \
                if self.target_type == 'regression' else \
                XGBClassifier(n_estimators=100, random_state=self.random_state)
        elif config['model'] == 'lightgbm' and HAS_LIGHTGBM:
            model = LGBMRegressor(n_estimators=100, random_state=self.random_state) \
                if self.target_type == 'regression' else \
                LGBMClassifier(n_estimators=100, random_state=self.random_state)
        elif config['model'] == 'linear':
            model = LinearRegression() if self.target_type == 'regression' else LogisticRegression()
        elif config['model'] == 'svm':
            model = SVR() if self.target_type == 'regression' else SVC()
        else:
            # Fallback
            model = RandomForestRegressor(n_estimators=100, random_state=self.random_state) \
                if self.target_type == 'regression' else \
                RandomForestClassifier(n_estimators=100, random_state=self.random_state)

        steps.append(('model', model))
        return Pipeline(steps)

    def _evaluate_pipeline(self, pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> float:
        """Evaluate pipeline using cross-validation."""
        scorer = self._get_cv_scorer()
        cv_scores = cross_val_score(
            pipeline, X, y,
            cv=self.cv_folds,
            scoring=scorer,
            n_jobs=-1
        )
        return np.mean(cv_scores)

    def _get_cv_scorer(self) -> str:
        """Get appropriate cross-validation scorer."""
        if self.target_type == "regression":
            return "neg_mean_squared_error"
        else:
            return "accuracy"


# =============================================================================
# MODEL STACKING AND ENSEMBLE METHODS
# =============================================================================

class AdvancedModelStacking:
    """Advanced model stacking with multiple layers and meta-learners."""

    def __init__(
        self,
        target_type: str = "regression",
        random_state: int = 42,
        cv_folds: int = 5
    ):
        self.target_type = target_type
        self.random_state = random_state
        self.cv_folds = cv_folds

    def create_stacking_ensemble(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        *,
        base_models: Optional[List[Any]] = None,
        meta_learner: Optional[Any] = None,
        n_layers: int = 2,
        use_blending: bool = False
    ) -> StackingResult:
        """Create advanced stacking ensemble."""
        start_time = time.time()

        if base_models is None:
            base_models = self._get_default_base_models()

        if meta_learner is None:
            meta_learner = LinearRegression() if self.target_type == "regression" \
                         else LogisticRegression(random_state=self.random_state)

        # Create stacking ensemble
        if use_blending:
            final_estimator, cv_scores = self._create_blending_ensemble(
                base_models, meta_learner, X, y
            )
        else:
            final_estimator, cv_scores = self._create_stacking_ensemble(
                base_models, meta_learner, X, y, n_layers
            )

        # Evaluate final ensemble
        if self.target_type == "regression":
            stacking_reg = StackingRegressor(
                estimators=[(f"base_{i}", model) for i, model in enumerate(base_models)],
                final_estimator=meta_learner,
                cv=self.cv_folds,
                passthrough=True
            )
            stacking_reg.fit(X, y)
            final_cv_scores = cross_val_score(
                stacking_reg, X, y, cv=self.cv_folds,
                scoring="neg_mean_squared_error", n_jobs=-1
            )
            score = np.mean(final_cv_scores)
        else:
            stacking_clf = StackingClassifier(
                estimators=[(f"base_{i}", model) for i, model in enumerate(base_models)],
                final_estimator=meta_learner,
                cv=self.cv_folds,
                passthrough=True
            )
            stacking_clf.fit(X, y)
            final_cv_scores = cross_val_score(
                stacking_clf, X, y, cv=self.cv_folds,
                scoring="accuracy", n_jobs=-1
            )
            score = np.mean(final_cv_scores)

        training_time = time.time() - start_time

        return StackingResult(
            final_estimator=final_estimator,
            base_estimators=base_models,
            score=score,
            cv_scores=final_cv_scores.tolist()
        )

    def _get_default_base_models(self) -> List[Any]:
        """Get default base models for stacking."""
        models = [
            RandomForestRegressor(n_estimators=100, random_state=self.random_state)
            if self.target_type == "regression" else
            RandomForestClassifier(n_estimators=100, random_state=self.random_state),

            GradientBoostingRegressor(n_estimators=100, random_state=self.random_state)
            if self.target_type == "regression" else
            GradientBoostingClassifier(n_estimators=100, random_state=self.random_state),
        ]

        if HAS_XGBOOST:
            models.append(
                XGBRegressor(n_estimators=100, random_state=self.random_state)
                if self.target_type == "regression" else
                XGBClassifier(n_estimators=100, random_state=self.random_state)
            )

        if HAS_LIGHTGBM:
            models.append(
                LGBMRegressor(n_estimators=100, random_state=self.random_state)
                if self.target_type == "regression" else
                LGBMClassifier(n_estimators=100, random_state=self.random_state)
            )

        models.extend([
            LinearRegression() if self.target_type == "regression" else
            LogisticRegression(random_state=self.random_state),

            SVR() if self.target_type == "regression" else
            SVC(random_state=self.random_state, probability=True)
        ])

        return models

    def _create_stacking_ensemble(
        self,
        base_models: List[Any],
        meta_learner: Any,
        X: pd.DataFrame,
        y: pd.Series,
        n_layers: int
    ) -> Tuple[Any, List[float]]:
        """Create multi-layer stacking ensemble."""
        current_X = X.copy()

        for layer in range(n_layers - 1):
            # Train base models on current features
            layer_predictions = []

            for model in base_models:
                cv_scores = cross_val_score(
                    model, current_X, y,
                    cv=self.cv_folds, n_jobs=-1
                )
                layer_predictions.append(cv_scores)

            # Use average predictions as new features
            new_features = np.column_stack([pred for pred in layer_predictions])
            current_X = pd.DataFrame(new_features, index=X.index)

        # Final stacking layer
        if self.target_type == "regression":
            final_stacking = StackingRegressor(
                estimators=[(f"base_{i}", model) for i, model in enumerate(base_models)],
                final_estimator=meta_learner,
                cv=self.cv_folds
            )
        else:
            final_stacking = StackingClassifier(
                estimators=[(f"base_{i}", model) for i, model in enumerate(base_models)],
                final_estimator=meta_learner,
                cv=self.cv_folds
            )

        cv_scores = cross_val_score(
            final_stacking, X, y,
            cv=self.cv_folds,
            scoring="neg_mean_squared_error" if self.target_type == "regression" else "accuracy",
            n_jobs=-1
        )

        return final_stacking, cv_scores.tolist()

    def _create_blending_ensemble(
        self,
        base_models: List[Any],
        meta_learner: Any,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[Any, List[float]]:
        """Create blending ensemble."""
        # Split data for blending
        X_blend_train, X_blend_val, y_blend_train, y_blend_val = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state,
            stratify=y if self.target_type == "classification" else None
        )

        # Train base models on blend_train
        blend_predictions = []
        for model in base_models:
            model.fit(X_blend_train, y_blend_train)
            if self.target_type == "classification" and hasattr(model, 'predict_proba'):
                preds = model.predict_proba(X_blend_val)
            else:
                preds = model.predict(X_blend_val).reshape(-1, 1)
            blend_predictions.append(preds)

        # Create meta-features
        if self.target_type == "classification":
            meta_features = np.column_stack([
                pred[:, 1] if pred.ndim > 1 else pred.flatten()
                for pred in blend_predictions
            ])
        else:
            meta_features = np.column_stack([pred.flatten() for pred in blend_predictions])

        # Train meta-learner
        meta_learner.fit(meta_features, y_blend_val)

        # Create final ensemble class
        class BlendingEnsemble:
            def __init__(self, base_models, meta_learner, target_type):
                self.base_models = base_models
                self.meta_learner = meta_learner
                self.target_type = target_type

            def fit(self, X, y):
                # Train all base models
                for model in self.base_models:
                    model.fit(X, y)
                return self

            def predict(self, X):
                # Get predictions from base models
                base_preds = []
                for model in self.base_models:
                    if self.target_type == "classification" and hasattr(model, 'predict_proba'):
                        pred = model.predict_proba(X)[:, 1]
                    else:
                        pred = model.predict(X)
                    base_preds.append(pred)

                # Create meta-features and predict
                meta_features = np.column_stack(base_preds)
                return self.meta_learner.predict(meta_features)

        ensemble = BlendingEnsemble(base_models, meta_learner, self.target_type)

        # Evaluate ensemble
        cv_scores = cross_val_score(
            ensemble, X, y,
            cv=self.cv_folds,
            scoring="neg_mean_squared_error" if self.target_type == "regression" else "accuracy",
            n_jobs=-1
        )

        return ensemble, cv_scores.tolist()


# =============================================================================
# AUTOMATED FEATURE PREPROCESSING
# =============================================================================

class AutomatedFeaturePreprocessor(BaseEstimator, TransformerMixin):
    """Automated feature preprocessing with intelligent transformation selection."""

    def __init__(
        self,
        target_type: str = "regression",
        handle_missing: bool = True,
        handle_outliers: bool = True,
        handle_categorical: bool = True,
        handle_scaling: bool = True,
        random_state: int = 42
    ):
        self.target_type = target_type
        self.handle_missing = handle_missing
        self.handle_outliers = handle_outliers
        self.handle_categorical = handle_categorical
        self.handle_scaling = handle_scaling
        self.random_state = random_state
        self.transformers_ = {}

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit automated preprocessing transformers."""
        X_processed = X.copy()

        # Handle missing values
        if self.handle_missing:
            self.transformers_['missing'] = self._fit_missing_handler(X_processed)

        # Handle categorical features
        if self.handle_categorical:
            self.transformers_['categorical'] = self._fit_categorical_handler(X_processed)

        # Handle outliers
        if self.handle_outliers:
            self.transformers_['outliers'] = self._fit_outlier_handler(X_processed)

        # Handle scaling
        if self.handle_scaling:
            self.transformers_['scaling'] = self._fit_scaling_handler(X_processed)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted preprocessing transformations."""
        X_processed = X.copy()

        # Apply transformations in order
        for transformer_name in ['missing', 'categorical', 'outliers', 'scaling']:
            if transformer_name in self.transformers_:
                transformer = self.transformers_[transformer_name]
                if hasattr(transformer, 'transform'):
                    X_processed = transformer.transform(X_processed)
                elif callable(transformer):
                    X_processed = transformer(X_processed)

        return X_processed

    def _fit_missing_handler(self, X: pd.DataFrame):
        """Fit missing value handler."""
        from sklearn.impute import SimpleImputer

        # Check for missing values
        missing_cols = X.columns[X.isnull().any()].tolist()

        if not missing_cols:
            return lambda x: x  # No-op

        # Choose imputation strategy based on data types
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        categorical_cols = X.select_dtypes(exclude=[np.number]).columns

        transformers = []

        if numeric_cols.any():
            numeric_imputer = SimpleImputer(strategy='median')
            numeric_imputer.fit(X[numeric_cols])
            transformers.append(('numeric', numeric_imputer, numeric_cols))

        if categorical_cols.any():
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            categorical_imputer.fit(X[categorical_cols])
            transformers.append(('categorical', categorical_imputer, categorical_cols))

        class MissingValueImputer:
            def __init__(self, transformers):
                self.transformers = transformers

            def transform(self, X):
                X_copy = X.copy()
                for name, imputer, cols in self.transformers:
                    X_copy[cols] = imputer.transform(X_copy[cols])
                return X_copy

        return MissingValueImputer(transformers)

    def _fit_categorical_handler(self, X: pd.DataFrame):
        """Fit categorical feature handler."""
        from sklearn.preprocessing import LabelEncoder, OneHotEncoder

        categorical_cols = X.select_dtypes(exclude=[np.number]).columns

        if not categorical_cols.any():
            return lambda x: x  # No-op

        # Check cardinality
        low_cardinality = []
        high_cardinality = []

        for col in categorical_cols:
            n_unique = X[col].nunique()
            if n_unique <= 10:
                low_cardinality.append(col)
            else:
                high_cardinality.append(col)

        transformers = []

        if low_cardinality:
            # One-hot encoding for low cardinality
            ohe = OneHotEncoder(sparse=False, drop='first', handle_unknown='ignore')
            ohe.fit(X[low_cardinality])
            transformers.append(('ohe', ohe, low_cardinality))

        if high_cardinality:
            # Label encoding for high cardinality
            label_encoders = {}
            for col in high_cardinality:
                le = LabelEncoder()
                le.fit(X[col].astype(str))
                label_encoders[col] = le
            transformers.append(('label', label_encoders, high_cardinality))

        class CategoricalTransformer:
            def __init__(self, transformers):
                self.transformers = transformers

            def transform(self, X):
                X_copy = X.copy()

                for name, transformer, cols in self.transformers:
                    if name == 'ohe':
                        encoded = transformer.transform(X_copy[cols])
                        # Remove original columns and add encoded
                        X_copy = X_copy.drop(cols, axis=1)
                        encoded_df = pd.DataFrame(
                            encoded,
                            columns=transformer.get_feature_names_out(cols),
                            index=X_copy.index
                        )
                        X_copy = pd.concat([X_copy, encoded_df], axis=1)

                    elif name == 'label':
                        for col in cols:
                            if col in X_copy.columns:
                                X_copy[col] = transformer[col].transform(X_copy[col].astype(str))

                return X_copy

        return CategoricalTransformer(transformers)

    def _fit_outlier_handler(self, X: pd.DataFrame):
        """Fit outlier handler."""
        from sklearn.preprocessing import RobustScaler

        numeric_cols = X.select_dtypes(include=[np.number]).columns

        if not numeric_cols.any():
            return lambda x: x  # No-op

        # Use robust scaling to handle outliers
        scaler = RobustScaler()
        scaler.fit(X[numeric_cols])

        return scaler

    def _fit_scaling_handler(self, X: pd.DataFrame):
        """Fit feature scaling handler."""
        numeric_cols = X.select_dtypes(include=[np.number]).columns

        if not numeric_cols.any():
            return lambda x: x  # No-op

        # Choose scaling method based on data distribution
        # Check for normality
        from scipy.stats import shapiro

        normal_cols = []
        skewed_cols = []

        for col in numeric_cols:
            try:
                _, p_value = shapiro(X[col].dropna().sample(min(5000, len(X[col]))))
                if p_value > 0.05:
                    normal_cols.append(col)
                else:
                    skewed_cols.append(col)
            except:
                skewed_cols.append(col)  # Assume skewed if test fails

        transformers = []

        if normal_cols:
            standard_scaler = StandardScaler()
            standard_scaler.fit(X[normal_cols])
            transformers.append(('standard', standard_scaler, normal_cols))

        if skewed_cols:
            power_scaler = PowerTransformer(method='yeo-johnson')
            power_scaler.fit(X[skewed_cols])
            transformers.append(('power', power_scaler, skewed_cols))

        class ScalingTransformer:
            def __init__(self, transformers):
                self.transformers = transformers

            def transform(self, X):
                X_copy = X.copy()
                for name, scaler, cols in self.transformers:
                    X_copy[cols] = scaler.transform(X_copy[cols])
                return X_copy

        return ScalingTransformer(transformers)


__all__ = [
    "AutoMLRunner",
    "AutoMLResult",
    "ModelConfig",
    "PipelineConfig",
    "NeuralArchitectureResult",
    "StackingResult",
    "NeuralArchitectureSearch",
    "AutomatedPipelineOptimizer",
    "AdvancedModelStacking",
    "AutomatedFeaturePreprocessor",
]

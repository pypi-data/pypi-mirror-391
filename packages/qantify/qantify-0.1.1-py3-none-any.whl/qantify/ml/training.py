"""Advanced Model Training and Validation Workflows.

This module provides comprehensive machine learning training capabilities including:
- Advanced cross-validation techniques (time series, grouped, stratified)
- Ensemble learning methods (bagging, boosting, stacking)
- Neural network training with custom architectures
- Hyperparameter optimization with multiple algorithms
- Distributed training support
- Model validation and performance monitoring
- Automated model selection and comparison
- Transfer learning capabilities
- Online learning and incremental training
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union, Callable, Protocol
from abc import ABC, abstractmethod
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import warnings
import hashlib
import json
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import (
    TimeSeriesSplit, KFold, StratifiedKFold, GroupKFold,
    cross_val_score, cross_validate, learning_curve, validation_curve
)
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    AdaBoostRegressor, AdaBoostClassifier,
    ExtraTreesRegressor, ExtraTreesClassifier,
    VotingRegressor, VotingClassifier,
    StackingRegressor, StackingClassifier
)
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso, ElasticNet,
    LogisticRegression, SGDRegressor, SGDClassifier
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    make_scorer
)
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin, clone

# Optional imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader, TensorDataset
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False
    torch = None
    nn = None
    optim = None
    Dataset = None
    DataLoader = None
    TensorDataset = None

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
    from ray import tune
    from ray.tune.schedulers import ASHAScheduler
    HAS_RAY = True
except ImportError:
    HAS_RAY = False
    tune = None
    ASHAScheduler = None

try:
    import optuna
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False
    optuna = None

try:
    import dask
    import dask_ml
    from dask_ml.model_selection import HyperbandSearchCV
    HAS_DASK = True
except ImportError:
    HAS_DASK = False
    dask = None
    dask_ml = None
    HyperbandSearchCV = None

from qantify.ml.features import create_features
from qantify.risk import RiskReport, build_risk_report

try:  # Optional imports
    import mlflow
except Exception:  # pragma: no cover - optional dependency
    mlflow = None  # type: ignore

try:  # Optional imports
    import wandb
except Exception:  # pragma: no cover - optional dependency
    wandb = None  # type: ignore


# =============================================================================
# ADVANCED CROSS-VALIDATION TECHNIQUES
# =============================================================================

class AdvancedCrossValidator:
    """Advanced cross-validation techniques for time series and financial data."""

    def __init__(self, cv_method: str = "time_series", n_splits: int = 5, **kwargs):
        self.cv_method = cv_method
        self.n_splits = n_splits
        self.kwargs = kwargs
        self.cv = self._create_cv()

    def _create_cv(self):
        """Create cross-validation splitter based on method."""
        if self.cv_method == "time_series":
            return TimeSeriesSplit(n_splits=self.n_splits, **self.kwargs)
        elif self.cv_method == "kfold":
            return KFold(n_splits=self.n_splits, shuffle=True, random_state=42, **self.kwargs)
        elif self.cv_method == "stratified":
            return StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=42, **self.kwargs)
        elif self.cv_method == "group":
            return GroupKFold(n_splits=self.n_splits)
        elif self.cv_method == "blocked":
            # Custom blocked CV for time series with gaps
            return self._create_blocked_cv()
        else:
            raise ValueError(f"Unknown CV method: {self.cv_method}")

    def _create_blocked_cv(self):
        """Create blocked cross-validation for time series."""
        class BlockedTimeSeriesSplit:
            def __init__(self, n_splits=5, gap=0, test_size=None):
                self.n_splits = n_splits
                self.gap = gap
                self.test_size = test_size or max(1, n_splits // 2)

            def split(self, X, y=None, groups=None):
                n_samples = len(X)
                indices = np.arange(n_samples)

                for i in range(self.n_splits):
                    # Calculate test start index
                    test_start = n_samples - (self.n_splits - i) * self.test_size
                    test_end = min(n_samples, test_start + self.test_size)

                    # Calculate train end index (with gap)
                    train_end = test_start - self.gap

                    if train_end <= 0:
                        continue

                    train_indices = indices[:train_end]
                    test_indices = indices[test_start:test_end]

                    if len(train_indices) > 0 and len(test_indices) > 0:
                        yield train_indices, test_indices

        return BlockedTimeSeriesSplit(n_splits=self.n_splits, **self.kwargs)

    def get_splits(self, X: pd.DataFrame, y: Optional[pd.Series] = None, groups: Optional[np.ndarray] = None):
        """Get train/test splits."""
        return list(self.cv.split(X, y, groups))

    def cross_validate(self, estimator, X: pd.DataFrame, y: pd.Series,
                      scoring: Union[str, Callable] = None, verbose: bool = False) -> Dict[str, Any]:
        """Perform cross-validation with detailed metrics."""
        if scoring is None:
            scoring = 'neg_mean_squared_error' if self._is_regression(y) else 'accuracy'

        # Basic cross-validation
        scores = cross_val_score(estimator, X, y, cv=self.cv, scoring=scoring)

        # Detailed cross-validation
        cv_results = cross_validate(
            estimator, X, y, cv=self.cv,
            scoring=self._get_scoring_dict(y),
            return_train_score=True,
            return_estimator=True
        )

        results = {
            'scores': scores,
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'cv_results': cv_results,
            'best_estimator': cv_results['estimator'][np.argmax(cv_results['test_score'])]
            if 'test_score' in cv_results else None
        }

        if verbose:
            print(f"CV Results: {results['mean_score']:.4f} (+/- {results['std_score']*2:.4f})")

        return results

    def _is_regression(self, y: pd.Series) -> bool:
        """Check if target is regression or classification."""
        return y.dtype in ['float64', 'float32'] or y.nunique() > 20

    def _get_scoring_dict(self, y: pd.Series) -> Dict[str, str]:
        """Get appropriate scoring metrics based on target type."""
        if self._is_regression(y):
            return {
                'neg_mean_squared_error': 'neg_mean_squared_error',
                'neg_mean_absolute_error': 'neg_mean_absolute_error',
                'r2': 'r2'
            }
        else:
            return {
                'accuracy': 'accuracy',
                'precision': 'precision_macro',
                'recall': 'recall_macro',
                'f1': 'f1_macro'
            }


class PurgedWalkForwardValidator:
    """Purged walk-forward validation for financial time series."""

    def __init__(self, n_splits: int = 5, embargo_pct: float = 0.01, purge_pct: float = 0.02):
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct
        self.purge_pct = purge_pct

    def split(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Generate purged train/test splits."""
        n_samples = len(X)
        indices = np.arange(n_samples)

        test_size = n_samples // (self.n_splits + 1)
        embargo_size = int(n_samples * self.embargo_pct)
        purge_size = int(n_samples * self.purge_pct)

        for i in range(self.n_splits):
            # Test set
            test_start = n_samples - (self.n_splits - i) * test_size
            test_end = min(n_samples, test_start + test_size)
            test_indices = indices[test_start:test_end]

            # Training set (with purging and embargo)
            train_end = test_start - embargo_size
            if purge_size > 0:
                # Remove samples close to test set start
                train_end = min(train_end, test_start - purge_size)

            train_indices = indices[:train_end]

            if len(train_indices) > 0 and len(test_indices) > 0:
                yield train_indices, test_indices

    def cross_validate(self, estimator, X: pd.DataFrame, y: pd.Series, **kwargs) -> Dict[str, Any]:
        """Perform purged cross-validation."""
        cv = AdvancedCrossValidator()
        cv.cv = self
        return cv.cross_validate(estimator, X, y, **kwargs)


# =============================================================================
# ENSEMBLE LEARNING METHODS
# =============================================================================

class AdvancedEnsembleTrainer:
    """Advanced ensemble training with multiple techniques."""

    def __init__(self, ensemble_type: str = "voting", **kwargs):
        self.ensemble_type = ensemble_type
        self.kwargs = kwargs
        self.base_estimators = []
        self.ensemble = None
        self.feature_importance = {}

    def create_base_estimators(self, task_type: str = "regression") -> List[Tuple[str, Any]]:
        """Create diverse base estimators."""
        estimators = []

        if task_type == "regression":
            # Tree-based models
            estimators.extend([
                ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
                ('et', ExtraTreesRegressor(n_estimators=100, random_state=42)),
            ])

            # Linear models
            estimators.extend([
                ('ridge', Ridge(alpha=1.0, random_state=42)),
                ('lasso', Lasso(alpha=0.1, random_state=42)),
                ('svr', SVR(kernel='rbf', C=1.0)),
            ])

            # Boosting models (if available)
            if HAS_XGBOOST:
                estimators.append(('xgb', xgb.XGBRegressor(n_estimators=100, random_state=42)))
            if HAS_LIGHTGBM:
                estimators.append(('lgb', lgb.LGBMRegressor(n_estimators=100, random_state=42)))
            if HAS_CATBOOST:
                estimators.append(('cb', cb.CatBoostRegressor(iterations=100, random_state=42, verbose=False)))

        else:  # classification
            estimators.extend([
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
                ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
                ('et', ExtraTreesClassifier(n_estimators=100, random_state=42)),
                ('lr', LogisticRegression(random_state=42, max_iter=1000)),
                ('svm', SVC(kernel='rbf', probability=True, random_state=42)),
            ])

            if HAS_XGBOOST:
                estimators.append(('xgb', xgb.XGBClassifier(n_estimators=100, random_state=42)))
            if HAS_LIGHTGBM:
                estimators.append(('lgb', lgb.LGBMClassifier(n_estimators=100, random_state=42)))
            if HAS_CATBOOST:
                estimators.append(('cb', cb.CatBoostClassifier(iterations=100, random_state=42, verbose=False)))

        return estimators

    def fit(self, X: pd.DataFrame, y: pd.Series, base_estimators: Optional[List[Tuple[str, Any]]] = None) -> 'AdvancedEnsembleTrainer':
        """Fit ensemble model."""
        task_type = "regression" if self._is_regression(y) else "classification"

        if base_estimators is None:
            base_estimators = self.create_base_estimators(task_type)

        self.base_estimators = base_estimators

        if self.ensemble_type == "voting":
            if task_type == "regression":
                self.ensemble = VotingRegressor(estimators=base_estimators, **self.kwargs)
            else:
                self.ensemble = VotingClassifier(estimators=base_estimators, **self.kwargs)

        elif self.ensemble_type == "stacking":
            if task_type == "regression":
                self.ensemble = StackingRegressor(
                    estimators=base_estimators,
                    final_estimator=Ridge(alpha=1.0),
                    **self.kwargs
                )
            else:
                self.ensemble = StackingClassifier(
                    estimators=base_estimators,
                    final_estimator=LogisticRegression(),
                    **self.kwargs
                )

        elif self.ensemble_type == "weighted":
            self.ensemble = self._create_weighted_ensemble(base_estimators, X, y)

        else:
            raise ValueError(f"Unknown ensemble type: {self.ensemble_type}")

        self.ensemble.fit(X, y)

        # Calculate feature importance if available
        self._calculate_feature_importance(X, y)

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.ensemble is None:
            raise RuntimeError("Ensemble must be fitted before prediction")
        return self.ensemble.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Predict probabilities for classification."""
        if hasattr(self.ensemble, 'predict_proba'):
            return self.ensemble.predict_proba(X)
        return None

    def _create_weighted_ensemble(self, estimators, X, y):
        """Create weighted ensemble based on individual performance."""
        from sklearn.model_selection import cross_val_score

        weights = []
        for name, estimator in estimators:
            try:
                scores = cross_val_score(estimator, X, y, cv=3, scoring='neg_mean_squared_error')
                weight = np.mean(scores)
                weights.append(max(0.1, weight))  # Minimum weight
            except:
                weights.append(1.0)  # Default weight

        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()

        # Create weighted ensemble
        class WeightedEnsemble:
            def __init__(self, estimators, weights):
                self.estimators = estimators
                self.weights = weights

            def fit(self, X, y):
                for name, estimator in self.estimators:
                    estimator.fit(X, y)
                return self

            def predict(self, X):
                predictions = np.array([est.predict(X) for name, est in self.estimators])
                return np.average(predictions, axis=0, weights=self.weights)

        return WeightedEnsemble(estimators, weights)

    def _calculate_feature_importance(self, X: pd.DataFrame, y: pd.Series):
        """Calculate feature importance across ensemble members."""
        importance_dict = {}

        for name, estimator in self.base_estimators:
            if hasattr(estimator, 'feature_importances_'):
                importance_dict[name] = estimator.feature_importances_
            elif hasattr(estimator, 'coef_'):
                # For linear models
                importance_dict[name] = np.abs(estimator.coef_)

        if importance_dict:
            # Average importance across models
            all_importance = np.array(list(importance_dict.values()))
            self.feature_importance = np.mean(all_importance, axis=0)

            # Create feature name mapping
            feature_names = X.columns.tolist()
            self.feature_importance = dict(zip(feature_names, self.feature_importance))

    def _is_regression(self, y: pd.Series) -> bool:
        """Check if task is regression."""
        return y.dtype in ['float64', 'float32'] or y.nunique() > 20


# =============================================================================
# NEURAL NETWORK TRAINING
# =============================================================================

class NeuralNetworkTrainer:
    """Advanced neural network training with PyTorch."""

    def __init__(self, architecture: Dict[str, Any] = None, training_config: Dict[str, Any] = None):
        if not HAS_PYTORCH:
            raise ImportError("PyTorch is required for neural network training")

        self.architecture = architecture or self._default_architecture()
        self.training_config = training_config or self._default_training_config()
        self.model = None
        self.scaler = StandardScaler()
        self.training_history = []

    def _default_architecture(self) -> Dict[str, Any]:
        """Default neural network architecture."""
        return {
            'input_dim': None,  # To be set during fit
            'hidden_dims': [128, 64, 32],
            'output_dim': 1,
            'activation': 'relu',
            'dropout': 0.2,
            'batch_norm': True
        }

    def _default_training_config(self) -> Dict[str, Any]:
        """Default training configuration."""
        return {
            'lr': 0.001,
            'batch_size': 32,
            'epochs': 100,
            'patience': 10,
            'optimizer': 'adam',
            'loss': 'mse',  # or 'bce' for binary classification
            'device': 'cpu',
            'validation_split': 0.2
        }

    def fit(self, X: pd.DataFrame, y: pd.Series, validation_data: Optional[Tuple[pd.DataFrame, pd.Series]] = None) -> 'NeuralNetworkTrainer':
        """Train neural network."""
        # Prepare data
        X_scaled = self.scaler.fit_transform(X.values)
        y_array = y.values.reshape(-1, 1) if len(y.shape) == 1 else y.values

        # Update architecture
        self.architecture['input_dim'] = X.shape[1]
        if self._is_classification(y):
            self.architecture['output_dim'] = len(np.unique(y))
            self.training_config['loss'] = 'ce'  # Cross-entropy

        # Create datasets
        if validation_data is not None:
            X_val_scaled = self.scaler.transform(validation_data[0].values)
            y_val_array = validation_data[1].values.reshape(-1, 1) if len(validation_data[1].shape) == 1 else validation_data[1].values

            train_dataset = TensorDataset(torch.FloatTensor(X_scaled), torch.FloatTensor(y_array))
            val_dataset = TensorDataset(torch.FloatTensor(X_val_scaled), torch.FloatTensor(y_val_array))
        else:
            # Split training data
            val_size = int(len(X_scaled) * self.training_config['validation_split'])
            train_size = len(X_scaled) - val_size

            train_dataset = TensorDataset(
                torch.FloatTensor(X_scaled[:train_size]),
                torch.FloatTensor(y_array[:train_size])
            )
            val_dataset = TensorDataset(
                torch.FloatTensor(X_scaled[train_size:]),
                torch.FloatTensor(y_array[train_size:])
            )

        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.training_config['batch_size'], shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.training_config['batch_size'])

        # Create model
        self.model = self._create_model()
        self.model.to(self.training_config['device'])

        # Training loop
        self._train_model(train_loader, val_loader)

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise RuntimeError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled).to(self.training_config['device'])

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor)

            if self._is_regression_task():
                return outputs.cpu().numpy().flatten()
            else:
                return torch.softmax(outputs, dim=1).cpu().numpy()

    def _create_model(self) -> nn.Module:
        """Create neural network model."""
        class FlexibleNet(nn.Module):
            def __init__(self, architecture):
                super(FlexibleNet, self).__init__()
                self.architecture = architecture

                layers = []
                prev_dim = architecture['input_dim']

                for hidden_dim in architecture['hidden_dims']:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        self._get_activation(architecture['activation']),
                    ])

                    if architecture.get('batch_norm', False):
                        layers.append(nn.BatchNorm1d(hidden_dim))

                    if architecture.get('dropout', 0) > 0:
                        layers.append(nn.Dropout(architecture['dropout']))

                    prev_dim = hidden_dim

                # Output layer
                layers.append(nn.Linear(prev_dim, architecture['output_dim']))

                self.network = nn.Sequential(*layers)

            def forward(self, x):
                return self.network(x)

            def _get_activation(self, activation_name):
                activations = {
                    'relu': nn.ReLU(),
                    'tanh': nn.Tanh(),
                    'sigmoid': nn.Sigmoid(),
                    'leaky_relu': nn.LeakyReLU(0.1)
                }
                return activations.get(activation_name, nn.ReLU())

        return FlexibleNet(self.architecture)

    def _train_model(self, train_loader: DataLoader, val_loader: DataLoader):
        """Train the neural network."""
        # Loss function
        if self.training_config['loss'] == 'mse':
            criterion = nn.MSELoss()
        elif self.training_config['loss'] == 'bce':
            criterion = nn.BCELoss()
        elif self.training_config['loss'] == 'ce':
            criterion = nn.CrossEntropyLoss()
        else:
            criterion = nn.MSELoss()

        # Optimizer
        if self.training_config['optimizer'] == 'adam':
            optimizer = optim.Adam(self.model.parameters(), lr=self.training_config['lr'])
        elif self.training_config['optimizer'] == 'sgd':
            optimizer = optim.SGD(self.model.parameters(), lr=self.training_config['lr'])
        else:
            optimizer = optim.Adam(self.model.parameters(), lr=self.training_config['lr'])

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(self.training_config['epochs']):
            # Training
            self.model.train()
            train_loss = 0.0

            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.training_config['device'])
                batch_y = batch_y.to(self.training_config['device'])

                optimizer.zero_grad()
                outputs = self.model(batch_X)

                if self.training_config['loss'] == 'ce':
                    # For classification, batch_y should be long type
                    batch_y = batch_y.squeeze().long()
                    loss = criterion(outputs, batch_y)
                else:
                    loss = criterion(outputs, batch_y)

                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Validation
            self.model.eval()
            val_loss = 0.0

            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.training_config['device'])
                    batch_y = batch_y.to(self.training_config['device'])

                    outputs = self.model(batch_X)

                    if self.training_config['loss'] == 'ce':
                        batch_y = batch_y.squeeze().long()
                        loss = criterion(outputs, batch_y)
                    else:
                        loss = criterion(outputs, batch_y)

                    val_loss += loss.item()

            train_loss /= len(train_loader)
            val_loss /= len(val_loader)

            self.training_history.append({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss
            })

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= self.training_config['patience']:
                break

    def _is_classification(self, y: pd.Series) -> bool:
        """Check if task is classification."""
        return y.dtype == 'object' or y.nunique() <= 20

    def _is_regression_task(self) -> bool:
        """Check if current task is regression."""
        return self.training_config['loss'] in ['mse']


class AutoEncoderTrainer:
    """Autoencoder for unsupervised feature learning."""

    def __init__(self, encoding_dim: int = 32, architecture: Dict[str, Any] = None):
        if not HAS_PYTORCH:
            raise ImportError("PyTorch is required for autoencoder training")

        self.encoding_dim = encoding_dim
        self.architecture = architecture or self._default_architecture()
        self.encoder = None
        self.decoder = None
        self.autoencoder = None
        self.scaler = StandardScaler()

    def _default_architecture(self) -> Dict[str, Any]:
        """Default autoencoder architecture."""
        return {
            'hidden_dims': [128, 64],
            'activation': 'relu',
            'dropout': 0.2
        }

    def fit(self, X: pd.DataFrame, epochs: int = 50, batch_size: int = 32) -> 'AutoEncoderTrainer':
        """Train autoencoder."""
        X_scaled = self.scaler.fit_transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled)

        dataset = TensorDataset(X_tensor, X_tensor)  # Input and target are the same
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Create autoencoder
        self._create_autoencoder(X.shape[1])

        # Training
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.autoencoder.parameters(), lr=0.001)

        for epoch in range(epochs):
            self.autoencoder.train()
            total_loss = 0

            for batch_X, _ in dataloader:
                optimizer.zero_grad()
                outputs = self.autoencoder(batch_X)
                loss = criterion(outputs, batch_X)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data to encoded representation."""
        X_scaled = self.scaler.transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled)

        self.encoder.eval()
        with torch.no_grad():
            encoded = self.encoder(X_tensor)

        return pd.DataFrame(
            encoded.cpu().numpy(),
            index=X.index,
            columns=[f'encoded_{i}' for i in range(self.encoding_dim)]
        )

    def _create_autoencoder(self, input_dim: int):
        """Create autoencoder architecture."""
        class AutoEncoder(nn.Module):
            def __init__(self, input_dim, encoding_dim, architecture):
                super(AutoEncoder, self).__init__()

                # Encoder
                encoder_layers = []
                prev_dim = input_dim

                for hidden_dim in architecture['hidden_dims']:
                    encoder_layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Dropout(architecture['dropout'])
                    ])
                    prev_dim = hidden_dim

                encoder_layers.append(nn.Linear(prev_dim, encoding_dim))
                self.encoder = nn.Sequential(*encoder_layers)

                # Decoder
                decoder_layers = []
                prev_dim = encoding_dim

                for hidden_dim in reversed(architecture['hidden_dims']):
                    decoder_layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Dropout(architecture['dropout'])
                    ])
                    prev_dim = hidden_dim

                decoder_layers.append(nn.Linear(prev_dim, input_dim))
                self.decoder = nn.Sequential(*decoder_layers)

            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded

            def encode(self, x):
                return self.encoder(x)

        self.autoencoder = AutoEncoder(input_dim, self.encoding_dim, self.architecture)
        self.encoder = self.autoencoder.encoder
        self.decoder = self.autoencoder.decoder


# =============================================================================
# HYPERPARAMETER OPTIMIZATION
# =============================================================================

class HyperparameterOptimizer:
    """Advanced hyperparameter optimization with multiple algorithms."""

    def __init__(self, optimization_method: str = "grid", **kwargs):
        self.optimization_method = optimization_method
        self.kwargs = kwargs

    def optimize(self, estimator, param_space: Dict[str, List[Any]],
                X: pd.DataFrame, y: pd.Series, cv: Any = None,
                scoring: str = None, n_iter: int = 50) -> Dict[str, Any]:
        """Perform hyperparameter optimization."""

        if self.optimization_method == "grid":
            return self._grid_search(estimator, param_space, X, y, cv, scoring)
        elif self.optimization_method == "random":
            return self._random_search(estimator, param_space, X, y, cv, scoring, n_iter)
        elif self.optimization_method == "bayesian" and HAS_OPTUNA:
            return self._optuna_optimize(estimator, param_space, X, y, cv, scoring, n_iter)
        elif self.optimization_method == "ray" and HAS_RAY:
            return self._ray_optimize(estimator, param_space, X, y, cv, scoring, n_iter)
        else:
            # Fallback to grid search
            return self._grid_search(estimator, param_space, X, y, cv, scoring)

    def _grid_search(self, estimator, param_space, X, y, cv, scoring):
        """Grid search optimization."""
        from sklearn.model_selection import GridSearchCV

        if cv is None:
            cv = TimeSeriesSplit(n_splits=5)

        if scoring is None:
            scoring = 'neg_mean_squared_error' if self._is_regression(y) else 'accuracy'

        grid_search = GridSearchCV(
            estimator, param_space, cv=cv, scoring=scoring,
            n_jobs=-1, verbose=1, **self.kwargs
        )

        grid_search.fit(X, y)

        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_,
            'best_estimator': grid_search.best_estimator_
        }

    def _random_search(self, estimator, param_space, X, y, cv, scoring, n_iter):
        """Random search optimization."""
        from sklearn.model_selection import RandomizedSearchCV

        if cv is None:
            cv = TimeSeriesSplit(n_splits=5)

        if scoring is None:
            scoring = 'neg_mean_squared_error' if self._is_regression(y) else 'accuracy'

        random_search = RandomizedSearchCV(
            estimator, param_space, n_iter=n_iter, cv=cv, scoring=scoring,
            n_jobs=-1, random_state=42, verbose=1, **self.kwargs
        )

        random_search.fit(X, y)

        return {
            'best_params': random_search.best_params_,
            'best_score': random_search.best_score_,
            'cv_results': random_search.cv_results_,
            'best_estimator': random_search.best_estimator_
        }

    def _optuna_optimize(self, estimator, param_space, X, y, cv, scoring, n_iter):
        """Optuna-based optimization."""
        def objective(trial):
            params = {}
            for param_name, param_values in param_space.items():
                if isinstance(param_values[0], int):
                    params[param_name] = trial.suggest_int(param_name, min(param_values), max(param_values))
                elif isinstance(param_values[0], float):
                    params[param_name] = trial.suggest_float(param_name, min(param_values), max(param_values))
                else:
                    params[param_name] = trial.suggest_categorical(param_name, param_values)

            # Clone estimator with new params
            est = clone(estimator)
            est.set_params(**params)

            # Cross-validation score
            scores = cross_val_score(est, X, y, cv=cv or TimeSeriesSplit(n_splits=5), scoring=scoring)
            return scores.mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_iter)

        # Fit best estimator
        best_estimator = clone(estimator)
        best_estimator.set_params(**study.best_params)
        best_estimator.fit(X, y)

        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'best_estimator': best_estimator,
            'study': study
        }

    def _ray_optimize(self, estimator, param_space, X, y, cv, scoring, n_iter):
        """Ray Tune-based optimization."""
        def objective(config):
            # Clone estimator with config params
            est = clone(estimator)
            est.set_params(**config)

            # Cross-validation score
            scores = cross_val_score(est, X, y, cv=cv or TimeSeriesSplit(n_splits=5), scoring=scoring)
            tune.report(score=scores.mean())

        analysis = tune.run(
            objective,
            config=param_space,
            num_samples=n_iter,
            scheduler=ASHAScheduler(metric="score", mode="max"),
            **self.kwargs
        )

        best_config = analysis.best_config
        best_estimator = clone(estimator)
        best_estimator.set_params(**best_config)
        best_estimator.fit(X, y)

        return {
            'best_params': best_config,
            'best_score': analysis.best_result["score"],
            'best_estimator': best_estimator,
            'analysis': analysis
        }

    def _is_regression(self, y: pd.Series) -> bool:
        """Check if task is regression."""
        return y.dtype in ['float64', 'float32'] or y.nunique() > 20


# =============================================================================
# DISTRIBUTED TRAINING
# =============================================================================

class DistributedTrainer:
    """Distributed training support using multiple backends."""

    def __init__(self, backend: str = "thread", n_workers: int = 4):
        self.backend = backend
        self.n_workers = n_workers

    def parallel_cross_validate(self, estimator, X: pd.DataFrame, y: pd.Series,
                              cv_splits: List[Tuple[np.ndarray, np.ndarray]],
                              scoring: Callable) -> List[float]:
        """Parallel cross-validation across splits."""

        def evaluate_fold(train_idx, test_idx):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            est = clone(estimator)
            est.fit(X_train, y_train)
            y_pred = est.predict(X_test)

            return scoring(y_test, y_pred)

        if self.backend == "thread":
            with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [executor.submit(evaluate_fold, train_idx, test_idx)
                          for train_idx, test_idx in cv_splits]
                scores = [future.result() for future in futures]

        elif self.backend == "process":
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [executor.submit(evaluate_fold, train_idx, test_idx)
                          for train_idx, test_idx in cv_splits]
                scores = [future.result() for future in futures]

        elif self.backend == "dask" and HAS_DASK:
            # Dask-based distributed computation
            import dask
            futures = [dask.delayed(evaluate_fold)(train_idx, test_idx)
                      for train_idx, test_idx in cv_splits]
            scores = dask.compute(*futures)

        else:
            # Sequential fallback
            scores = [evaluate_fold(train_idx, test_idx) for train_idx, test_idx in cv_splits]

        return scores

    def parallel_hyperopt(self, param_combinations: List[Dict[str, Any]],
                         estimator_factory: Callable, X: pd.DataFrame, y: pd.Series,
                         cv: Any = None) -> List[Dict[str, Any]]:
        """Parallel hyperparameter optimization."""

        def evaluate_params(params):
            est = estimator_factory(**params)
            scores = cross_val_score(est, X, y, cv=cv or TimeSeriesSplit(n_splits=3))
            return {
                'params': params,
                'mean_score': scores.mean(),
                'std_score': scores.std()
            }

        if self.backend == "thread":
            with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [executor.submit(evaluate_params, params) for params in param_combinations]
                results = [future.result() for future in futures]

        elif self.backend == "dask" and HAS_DASK:
            import dask
            futures = [dask.delayed(evaluate_params)(params) for params in param_combinations]
            results = dask.compute(*futures)

        else:
            results = [evaluate_params(params) for params in param_combinations]

        return results


# =============================================================================
# MODEL VALIDATION AND MONITORING
# =============================================================================

class ModelValidator:
    """Comprehensive model validation and performance monitoring."""

    def __init__(self, validation_metrics: List[str] = None):
        self.validation_metrics = validation_metrics or [
            'mse', 'mae', 'r2', 'accuracy', 'precision', 'recall', 'f1'
        ]

    def validate_model(self, y_true: pd.Series, y_pred: pd.Series,
                      model_type: str = "auto") -> Dict[str, Any]:
        """Comprehensive model validation."""

        if model_type == "auto":
            model_type = "regression" if y_true.dtype in ['float64', 'float32'] else "classification"

        results = {}

        if model_type == "regression":
            results.update(self._regression_metrics(y_true, y_pred))
        else:
            results.update(self._classification_metrics(y_true, y_pred))

        # Common metrics
        results.update(self._common_metrics(y_true, y_pred))

        return results

    def _regression_metrics(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """Calculate regression metrics."""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            'explained_variance': 1 - np.var(y_true - y_pred) / np.var(y_true)
        }

    def _classification_metrics(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """Calculate classification metrics."""
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='macro', zero_division=0),
            'f1': f1_score(y_true, y_pred, average='macro', zero_division=0),
            'balanced_accuracy': (precision_score(y_true, y_pred, average='macro', zero_division=0) +
                                recall_score(y_true, y_pred, average='macro', zero_division=0)) / 2
        }

    def _common_metrics(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, Any]:
        """Calculate common metrics for both regression and classification."""
        residuals = y_true - y_pred if y_true.dtype in ['float64', 'float32'] else None

        metrics = {
            'n_samples': len(y_true),
            'prediction_std': y_pred.std(),
            'target_std': y_true.std()
        }

        if residuals is not None:
            metrics.update({
                'residual_mean': residuals.mean(),
                'residual_std': residuals.std(),
                'max_residual': residuals.abs().max(),
                'residual_skew': residuals.skew(),
                'residual_kurtosis': residuals.kurtosis()
            })

        return metrics

    def learning_curves(self, estimator, X: pd.DataFrame, y: pd.Series,
                        cv: Any = None, train_sizes: np.ndarray = None) -> Dict[str, Any]:
        """Generate learning curves."""
        if train_sizes is None:
            train_sizes = np.linspace(0.1, 1.0, 10)

        if cv is None:
            cv = TimeSeriesSplit(n_splits=5)

        train_sizes, train_scores, val_scores = learning_curve(
            estimator, X, y, cv=cv, train_sizes=train_sizes,
            scoring='neg_mean_squared_error' if self._is_regression(y) else 'accuracy',
            n_jobs=-1
        )

        return {
            'train_sizes': train_sizes,
            'train_scores': train_scores,
            'val_scores': val_scores,
            'train_scores_mean': np.mean(train_scores, axis=1),
            'train_scores_std': np.std(train_scores, axis=1),
            'val_scores_mean': np.mean(val_scores, axis=1),
            'val_scores_std': np.std(val_scores, axis=1)
        }

    def validation_curves(self, estimator, X: pd.DataFrame, y: pd.Series,
                         param_name: str, param_range: List[Any],
                         cv: Any = None) -> Dict[str, Any]:
        """Generate validation curves for hyperparameter tuning."""
        if cv is None:
            cv = TimeSeriesSplit(n_splits=5)

        train_scores, val_scores = validation_curve(
            estimator, X, y, param_name=param_name, param_range=param_range,
            cv=cv, scoring='neg_mean_squared_error' if self._is_regression(y) else 'accuracy',
            n_jobs=-1
        )

        return {
            'param_range': param_range,
            'train_scores_mean': np.mean(train_scores, axis=1),
            'train_scores_std': np.std(train_scores, axis=1),
            'val_scores_mean': np.mean(val_scores, axis=1),
            'val_scores_std': np.std(val_scores, axis=1)
        }

    def _is_regression(self, y: pd.Series) -> bool:
        """Check if task is regression."""
        return y.dtype in ['float64', 'float32'] or y.nunique() > 20


# =============================================================================
# AUTOMATED MODEL SELECTION
# =============================================================================

class AutomatedModelSelector:
    """Automated model selection and comparison."""

    def __init__(self, models: List[Tuple[str, Any]] = None, cv_method: str = "time_series"):
        self.models = models or self._default_models()
        self.cv_method = cv_method
        self.cv = AdvancedCrossValidator(cv_method)
        self.results = {}

    def _default_models(self) -> List[Tuple[str, Any]]:
        """Default model candidates."""
        models = [
            ('linear', Ridge(alpha=1.0)),
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
            ('svm', SVR(kernel='rbf')),
        ]

        # Add optional models
        if HAS_XGBOOST:
            models.append(('xgb', xgb.XGBRegressor(n_estimators=100, random_state=42)))
        if HAS_LIGHTGBM:
            models.append(('lgb', lgb.LGBMRegressor(n_estimators=100, random_state=42)))
        if HAS_CATBOOST:
            models.append(('cb', cb.CatBoostRegressor(iterations=100, random_state=42, verbose=False)))

        return models

    def compare_models(self, X: pd.DataFrame, y: pd.Series,
                      scoring: str = None) -> pd.DataFrame:
        """Compare multiple models using cross-validation."""
        if scoring is None:
            scoring = 'neg_mean_squared_error' if self._is_regression(y) else 'accuracy'

        results = []

        for name, model in self.models:
            try:
                cv_results = self.cv.cross_validate(model, X, y, scoring=scoring)

                result = {
                    'model': name,
                    'mean_score': cv_results['mean_score'],
                    'std_score': cv_results['std_score'],
                    'best_estimator': cv_results['best_estimator']
                }

                # Add detailed metrics if available
                if 'cv_results' in cv_results:
                    cv_res = cv_results['cv_results']
                    if 'test_r2' in cv_res:
                        result['r2_mean'] = np.mean(cv_res['test_r2'])
                        result['r2_std'] = np.std(cv_res['test_r2'])

                results.append(result)

            except Exception as e:
                results.append({
                    'model': name,
                    'error': str(e),
                    'mean_score': float('-inf')
                })

        # Convert to DataFrame and sort
        df = pd.DataFrame(results)
        if not df.empty and 'mean_score' in df.columns:
            df = df.sort_values('mean_score', ascending=False)

        self.results = df
        return df

    def get_best_model(self) -> Tuple[str, Any]:
        """Get the best performing model."""
        if self.results.empty:
            raise RuntimeError("No model comparison results available. Run compare_models first.")

        best_row = self.results.iloc[0]
        return best_row['model'], best_row['best_estimator']

    def ensemble_selection(self, X: pd.DataFrame, y: pd.Series,
                          n_models: int = 3) -> AdvancedEnsembleTrainer:
        """Create ensemble from top performing models."""
        if self.results.empty:
            self.compare_models(X, y)

        # Get top N models
        top_models = self.results.head(n_models)
        estimators = [(row['model'], row['best_estimator']) for _, row in top_models.iterrows()]

        # Create ensemble
        ensemble = AdvancedEnsembleTrainer(ensemble_type='voting')
        ensemble.fit(X, y, base_estimators=estimators)

        return ensemble

    def _is_regression(self, y: pd.Series) -> bool:
        """Check if task is regression."""
        return y.dtype in ['float64', 'float32'] or y.nunique() > 20


# Update existing Dataset class with more functionality
@dataclass(slots=True)
class Dataset:
    features: pd.DataFrame
    target: pd.Series

    def __post_init__(self):
        """Validate dataset consistency."""
        if len(self.features) != len(self.target):
            raise ValueError("Features and target must have the same length")

        # Align indices
        common_index = self.features.index.intersection(self.target.index)
        if len(common_index) != len(self.features):
            warnings.warn(f"Index mismatch detected. Using {len(common_index)} common samples.")

        self.features = self.features.loc[common_index]
        self.target = self.target.loc[common_index]

    @property
    def shape(self) -> Tuple[int, int]:
        """Get dataset shape."""
        return self.features.shape

    @property
    def n_features(self) -> int:
        """Get number of features."""
        return self.features.shape[1]

    @property
    def n_samples(self) -> int:
        """Get number of samples."""
        return self.features.shape[0]

    @property
    def feature_names(self) -> List[str]:
        """Get feature names."""
        return self.features.columns.tolist()

    @property
    def is_regression(self) -> bool:
        """Check if dataset is for regression."""
        return self.target.dtype in ['float64', 'float32'] or self.target.nunique() > 20

    @property
    def is_classification(self) -> bool:
        """Check if dataset is for classification."""
        return not self.is_regression

    def get_splits(self, test_size: float = 0.2, random_state: int = 42) -> Tuple['Dataset', 'Dataset']:
        """Split dataset into train and test sets."""
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.target, test_size=test_size,
            random_state=random_state, shuffle=not isinstance(self.features.index, pd.DatetimeIndex)
        )

        train_dataset = Dataset(features=X_train, target=y_train)
        test_dataset = Dataset(features=X_test, target=y_test)

        return train_dataset, test_dataset

    def get_cv_splits(self, cv_method: str = "time_series", n_splits: int = 5) -> List[Tuple['Dataset', 'Dataset']]:
        """Get cross-validation splits."""
        cv = AdvancedCrossValidator(cv_method, n_splits)
        splits = cv.get_splits(self.features, self.target)

        cv_datasets = []
        for train_idx, test_idx in splits:
            train_dataset = Dataset(
                features=self.features.iloc[train_idx],
                target=self.target.iloc[train_idx]
            )
            test_dataset = Dataset(
                features=self.features.iloc[test_idx],
                target=self.target.iloc[test_idx]
            )
            cv_datasets.append((train_dataset, test_dataset))

        return cv_datasets

    def describe(self) -> Dict[str, Any]:
        """Get comprehensive dataset description."""
        return {
            'shape': self.shape,
            'n_features': self.n_features,
            'n_samples': self.n_samples,
            'feature_names': self.feature_names,
            'target_type': 'regression' if self.is_regression else 'classification',
            'target_unique_values': self.target.nunique(),
            'features_dtypes': self.features.dtypes.value_counts().to_dict(),
            'missing_values_features': self.features.isnull().sum().sum(),
            'missing_values_target': self.target.isnull().sum(),
            'features_stats': self.features.describe().to_dict(),
            'target_stats': self.target.describe().to_dict()
        }


@dataclass(slots=True)
class WalkForwardFold:
    params: Dict[str, Any]
    train_range: Tuple[pd.Timestamp, pd.Timestamp]
    test_range: Tuple[pd.Timestamp, pd.Timestamp]
    risk_report: RiskReport
    predictions: pd.Series
    realized_returns: pd.Series


@dataclass(slots=True)
class WalkForwardResult:
    folds: List[WalkForwardFold]

    def summary(self) -> pd.DataFrame:
        data = []
        for idx, fold in enumerate(self.folds, start=1):
            metrics = fold.risk_report.metrics
            row = {
                "fold": idx,
                "train_start": fold.train_range[0],
                "train_end": fold.train_range[1],
                "test_start": fold.test_range[0],
                "test_end": fold.test_range[1],
                "sharpe": metrics.sharpe,
                "sortino": metrics.sortino,
                "return": metrics.total_return,
                "max_drawdown": metrics.max_drawdown,
            }
            data.append(row)
        return pd.DataFrame(data)


@dataclass(slots=True)
class TrackerConfig:
    enable_mlflow: bool = False
    mlflow_experiment: Optional[str] = None
    enable_wandb: bool = False
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


class ExperimentTracker:
    """Unified wrapper for MLflow and Weights & Biases logging."""

    def __init__(self, config: TrackerConfig, *, context: str = "training") -> None:
        self.config = config
        self.context = context
        self._mlflow_active = False
        self._wandb_run = None

    def __enter__(self) -> "ExperimentTracker":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.finish()

    def start(self) -> None:
        if self.config.enable_mlflow and mlflow is not None:
            if self.config.mlflow_experiment:
                mlflow.set_experiment(self.config.mlflow_experiment)
            mlflow.start_run()
            mlflow.set_tags(self.config.tags | {"context": self.context})
            self._mlflow_active = True
        if self.config.enable_wandb and wandb is not None:
            run = wandb.init(
                project=self.config.wandb_project,
                entity=self.config.wandb_entity,
                config=self.config.tags,
                reinit=True,
            )
            self._wandb_run = run

    def log_params(self, params: Mapping[str, Any]) -> None:
        if self._mlflow_active and mlflow is not None:
            mlflow.log_params(dict(params))
        if self._wandb_run is not None:
            wandb.log({f"param/{k}": v for k, v in params.items()})

    def log_metrics(self, metrics: Mapping[str, float], *, step: Optional[int] = None) -> None:
        if self._mlflow_active and mlflow is not None:
            mlflow.log_metrics(metrics, step=step)
        if self._wandb_run is not None:
            wandb.log({f"metric/{k}": v for k, v in metrics.items()}, step=step)

    def log_artifact(self, path: str) -> None:
        if self._mlflow_active and mlflow is not None:
            mlflow.log_artifact(path)
        if self._wandb_run is not None and wandb is not None:
            wandb.save(path)

    def finish(self) -> None:
        if self._mlflow_active and mlflow is not None:
            mlflow.end_run()
            self._mlflow_active = False
        if self._wandb_run is not None:
            wandb.finish()
            self._wandb_run = None


def compute_future_return(series: pd.Series, *, horizon: int = 1, log: bool = False) -> pd.Series:
    if log:
        target = np.log(series.shift(-horizon) / series)
    else:
        target = series.shift(-horizon) / series - 1
    target.name = f"future_return_{horizon}{'_log' if log else ''}"
    return target


def prepare_dataset(
    frame: pd.DataFrame,
    *,
    target_column: str = "close",
    feature_kwargs: Optional[Dict[str, Any]] = None,
    target_kwargs: Optional[Dict[str, Any]] = None,
    dropna: bool = True,
) -> Dataset:
    feature_kwargs = feature_kwargs or {}
    target_kwargs = target_kwargs or {}

    features = create_features(frame, **feature_kwargs)
    target = compute_future_return(frame[target_column], **target_kwargs)
    target = target.reindex(features.index)

    if dropna:
        mask = features.notna().all(axis=1) & target.notna()
        features = features.loc[mask]
        target = target.loc[mask]

    return Dataset(features=features, target=target)


class ModelTrainer:
    """Utility class for fitting estimators on generated features."""

    def __init__(
        self,
        estimator: Any,
        *,
        threshold: float = 0.0,
        tracker: Optional[ExperimentTracker] = None,
    ) -> None:
        if not all(hasattr(estimator, attr) for attr in ("fit", "predict")):
            raise TypeError("Estimator must implement fit and predict methods.")
        self.estimator = estimator
        self.threshold = threshold
        self.feature_columns: Optional[List[str]] = None
        self.tracker = tracker

    def fit(self, dataset: Dataset) -> "ModelTrainer":
        X = dataset.features.values
        y = dataset.target.values
        if self.tracker is not None:
            self.tracker.log_params({"n_features": X.shape[1], "n_samples": X.shape[0]})
        self.estimator.fit(X, y)
        self.feature_columns = list(dataset.features.columns)
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        if self.feature_columns is None:
            raise RuntimeError("ModelTrainer must be fitted before predicting.")
        missing = [col for col in self.feature_columns if col not in features.columns]
        if missing:
            raise KeyError(f"Missing feature columns: {missing}")
        X = features[self.feature_columns].values
        preds = self.estimator.predict(X)
        return pd.Series(preds, index=features.index, name="prediction")

    def walk_forward(
        self,
        frame: pd.DataFrame,
        *,
        splits: int = 4,
        target_column: str = "close",
        feature_kwargs: Optional[Dict[str, Any]] = None,
        target_kwargs: Optional[Dict[str, Any]] = None,
        risk_kwargs: Optional[Dict[str, Any]] = None,
        min_train_size: int = 50,
    ) -> WalkForwardResult:
        feature_kwargs = feature_kwargs or {}
        target_kwargs = target_kwargs or {}
        risk_kwargs = risk_kwargs or {}

        if len(frame) < min_train_size + splits:
            raise ValueError("Not enough data for requested number of splits.")

        fold_size = (len(frame) - min_train_size) // splits
        folds: List[WalkForwardFold] = []

        for idx in range(splits):
            train_end = frame.index[min_train_size + idx * fold_size]
            test_end_idx = min(len(frame) - 1, min_train_size + (idx + 1) * fold_size)
            test_end = frame.index[test_end_idx]

            train = frame.loc[:train_end]
            test = frame.loc[train_end:test_end]
            if len(test) <= 5:
                continue
            dataset = prepare_dataset(
                train,
                target_column=target_column,
                feature_kwargs=feature_kwargs,
                target_kwargs=target_kwargs,
            )

            self.fit(dataset)
            test_dataset = prepare_dataset(
                test,
                target_column=target_column,
                feature_kwargs=feature_kwargs,
                target_kwargs=target_kwargs,
                dropna=False,
            )

            preds = self.predict(test_dataset.features)
            actual = test_dataset.target.reindex(preds.index)
            signals = np.where(preds > self.threshold, 1.0, np.where(preds < -self.threshold, -1.0, 0.0))
            aligned_returns = actual.fillna(0.0)
            equity = pd.Series(1.0, index=aligned_returns.index)
            equity = (1 + aligned_returns * signals).cumprod()

            report = build_risk_report(equity, trades=[], **risk_kwargs)
            if self.tracker is not None:
                metrics = report.metrics
                self.tracker.log_metrics(
                    {
                        f"fold_{idx}_sharpe": metrics.sharpe,
                        f"fold_{idx}_return": metrics.total_return,
                        f"fold_{idx}_max_drawdown": metrics.max_drawdown,
                    },
                    step=idx,
                )
            folds.append(
                WalkForwardFold(
                    params={"fold": idx, "threshold": self.threshold},
                    train_range=(train.index[0], train.index[-1]),
                    test_range=(test.index[0], test.index[-1]),
                    risk_report=report,
                    predictions=preds,
                    realized_returns=aligned_returns,
                )
            )

        return WalkForwardResult(folds=folds)


__all__ = [
    "Dataset",
    "WalkForwardResult",
    "WalkForwardFold",
    "ModelTrainer",
    "prepare_dataset",
    "compute_future_return",
    "ExperimentTracker",
    "TrackerConfig",
    "AdvancedCrossValidator",
    "PurgedWalkForwardValidator",
    "AdvancedEnsembleTrainer",
    "NeuralNetworkTrainer",
    "AutoEncoderTrainer",
    "HyperparameterOptimizer",
    "DistributedTrainer",
    "ModelValidator",
    "AutomatedModelSelector",
]

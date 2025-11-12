"""Advanced anomaly detection methods and utilities."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.stats import zscore, chi2
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor

# Optional dependencies
try:
    import torch
    import torch.nn as nn
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

try:
    from pyod.models import (
        IForest, LOF, OCSVM, AutoEncoder as PyODAutoEncoder,
        DeepSVDD, ECOD, COPOD, MAD, SOS, LODA
    )
    HAS_PYOD = True
except ImportError:
    HAS_PYOD = False


@dataclass(slots=True)
class AnomalyDetectionConfig:
    """Configuration for anomaly detection methods."""
    method: str = "isolation_forest"
    contamination: float = 0.1
    n_estimators: int = 100
    random_state: int = 42
    scaling: str = "standard"  # "standard", "robust", "none"


@dataclass(slots=True)
class AnomalyResult:
    """Result from anomaly detection."""
    predictions: np.ndarray
    scores: np.ndarray
    threshold: float
    contamination_rate: float
    method: str
    training_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AnomalyEvaluationMetrics:
    """Comprehensive evaluation metrics for anomaly detection."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float]
    confusion_matrix: np.ndarray
    classification_report: str
    contamination_rate: float


class AdvancedAnomalyDetector:
    """Advanced anomaly detection with multiple algorithms."""

    def __init__(self, config: AnomalyDetectionConfig):
        self.config = config
        self.detector = None
        self.scaler = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'AdvancedAnomalyDetector':
        """Fit the anomaly detector."""
        start_time = time.time()

        # Prepare data
        X_processed = self._preprocess_data(X, fit=True)

        # Initialize detector based on method
        if self.config.method == "isolation_forest":
            self.detector = IsolationForest(
                n_estimators=self.config.n_estimators,
                contamination=self.config.contamination,
                random_state=self.config.random_state
            )
        elif self.config.method == "one_class_svm":
            self.detector = OneClassSVM(
                nu=self.config.contamination,
                kernel="rbf"
            )
        elif self.config.method == "local_outlier_factor":
            self.detector = LocalOutlierFactor(
                n_neighbors=20,
                contamination=self.config.contamination,
                novelty=True
            )
        elif self.config.method == "pyod_iforest" and HAS_PYOD:
            self.detector = IForest(
                n_estimators=self.config.n_estimators,
                contamination=self.config.contamination,
                random_state=self.config.random_state
            )
        elif self.config.method == "pyod_lof" and HAS_PYOD:
            self.detector = LOF(
                contamination=self.config.contamination
            )
        elif self.config.method == "pyod_autoencoder" and HAS_PYOD:
            self.detector = PyODAutoEncoder(
                contamination=self.config.contamination,
                hidden_neurons=[64, 32, 32, 64],
                epochs=50,
                batch_size=32,
                random_state=self.config.random_state
            )
        else:
            raise ValueError(f"Unknown anomaly detection method: {self.config.method}")

        # Fit detector
        self.detector.fit(X_processed)

        self.training_time = time.time() - start_time
        self.is_fitted = True

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> AnomalyResult:
        """Predict anomalies."""
        if not self.is_fitted:
            raise RuntimeError("Detector must be fitted before prediction")

        X_processed = self._preprocess_data(X, fit=False)

        # Get predictions
        if hasattr(self.detector, 'predict'):
            predictions = self.detector.predict(X_processed)
        else:
            # For sklearn-like detectors that return -1/1
            raw_predictions = self.detector.predict(X_processed)
            predictions = (raw_predictions == -1).astype(int)

        # Get anomaly scores
        if hasattr(self.detector, 'score_samples'):
            scores = -self.detector.score_samples(X_processed)  # Higher scores = more anomalous
        elif hasattr(self.detector, 'decision_function'):
            scores = -self.detector.decision_function(X_processed)
        else:
            # Fallback: use predictions as scores
            scores = predictions.astype(float)

        # Determine threshold
        threshold = self._determine_threshold(scores, predictions)

        contamination_rate = np.mean(predictions)

        return AnomalyResult(
            predictions=predictions,
            scores=scores,
            threshold=threshold,
            contamination_rate=contamination_rate,
            method=self.config.method,
            training_time=self.training_time
        )

    def _preprocess_data(self, X: Union[np.ndarray, pd.DataFrame], fit: bool = False) -> np.ndarray:
        """Preprocess input data."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        if self.config.scaling == "standard":
            if fit:
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)
            else:
                if self.scaler is None:
                    raise RuntimeError("Scaler not fitted")
                X_scaled = self.scaler.transform(X)
        elif self.config.scaling == "robust":
            if fit:
                self.scaler = RobustScaler()
                X_scaled = self.scaler.fit_transform(X)
            else:
                if self.scaler is None:
                    raise RuntimeError("Scaler not fitted")
                X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X

        return X_scaled

    def _determine_threshold(self, scores: np.ndarray, predictions: np.ndarray) -> float:
        """Determine anomaly threshold."""
        # Use the score at the contamination boundary
        sorted_scores = np.sort(scores)
        threshold_idx = int(len(sorted_scores) * (1 - self.config.contamination))
        return sorted_scores[threshold_idx] if threshold_idx < len(sorted_scores) else sorted_scores[-1]


class StatisticalAnomalyDetector:
    """Statistical anomaly detection methods."""

    def __init__(self, method: str = "zscore", threshold: float = 3.0):
        self.method = method
        self.threshold = threshold
        self.baseline_stats = {}

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'StatisticalAnomalyDetector':
        """Fit statistical baseline."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        if self.method == "zscore":
            self.baseline_stats['mean'] = np.mean(X, axis=0)
            self.baseline_stats['std'] = np.std(X, axis=0)
        elif self.method == "mad":
            # Median Absolute Deviation
            self.baseline_stats['median'] = np.median(X, axis=0)
            self.baseline_stats['mad'] = np.median(np.abs(X - self.baseline_stats['median']), axis=0)
        elif self.method == "iqr":
            # Interquartile Range
            q75, q25 = np.percentile(X, [75, 25], axis=0)
            self.baseline_stats['iqr'] = q75 - q25
            self.baseline_stats['q25'] = q25

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> AnomalyResult:
        """Detect anomalies using statistical methods."""
        if isinstance(X, pd.DataFrame):
            X = X.values

        scores = np.zeros(len(X))

        if self.method == "zscore":
            for i, x in enumerate(X):
                z_scores = np.abs((x - self.baseline_stats['mean']) / self.baseline_stats['std'])
                scores[i] = np.max(z_scores)
        elif self.method == "mad":
            for i, x in enumerate(X):
                mad_scores = np.abs(x - self.baseline_stats['median']) / self.baseline_stats['mad']
                scores[i] = np.max(mad_scores)
        elif self.method == "iqr":
            for i, x in enumerate(X):
                outlier_scores = (x - self.baseline_stats['q25']) / self.baseline_stats['iqr']
                scores[i] = np.max(np.abs(outlier_scores))

        predictions = (scores > self.threshold).astype(int)

        return AnomalyResult(
            predictions=predictions,
            scores=scores,
            threshold=self.threshold,
            contamination_rate=np.mean(predictions),
            method=f"statistical_{self.method}",
            training_time=0.0
        )


class EnsembleAnomalyDetector:
    """Ensemble of multiple anomaly detection methods."""

    def __init__(self, detectors: List[AdvancedAnomalyDetector], voting: str = "majority"):
        self.detectors = detectors
        self.voting = voting  # "majority", "average", "weighted"
        self.weights = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'EnsembleAnomalyDetector':
        """Fit all detectors in the ensemble."""
        for detector in self.detectors:
            detector.fit(X)
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> AnomalyResult:
        """Make ensemble predictions."""
        results = [detector.predict(X) for detector in self.detectors]

        if self.voting == "majority":
            # Majority voting
            all_predictions = np.array([result.predictions for result in results])
            ensemble_predictions = (np.mean(all_predictions, axis=0) > 0.5).astype(int)
            ensemble_scores = np.mean([result.scores for result in results], axis=0)
        elif self.voting == "average":
            # Average scores
            ensemble_scores = np.mean([result.scores for result in results], axis=0)
            ensemble_predictions = (ensemble_scores > np.mean([r.threshold for r in results])).astype(int)
        else:
            # Weighted voting (if weights provided)
            if self.weights is None:
                self.weights = np.ones(len(self.detectors)) / len(self.detectors)

            all_predictions = np.array([result.predictions for result in results])
            ensemble_predictions = np.average(all_predictions, axis=0, weights=self.weights)
            ensemble_predictions = (ensemble_predictions > 0.5).astype(int)
            ensemble_scores = np.average([result.scores for result in results], axis=0, weights=self.weights)

        return AnomalyResult(
            predictions=ensemble_predictions,
            scores=ensemble_scores,
            threshold=np.mean([r.threshold for r in results]),
            contamination_rate=np.mean(ensemble_predictions),
            method="ensemble",
            training_time=sum(r.training_time for r in results),
            metadata={"individual_results": results}
        )


class TimeSeriesAnomalyDetector:
    """Anomaly detection for time series data."""

    def __init__(
        self,
        window_size: int = 50,
        method: str = "arima",
        threshold: float = 3.0
    ):
        self.window_size = window_size
        self.method = method
        self.threshold = threshold

    def fit(self, X: Union[np.ndarray, pd.Series]) -> 'TimeSeriesAnomalyDetector':
        """Fit time series anomaly detector."""
        if isinstance(X, pd.Series):
            X = X.values

        self.baseline_data = X[-self.window_size:]  # Use recent data as baseline

        if self.method == "arima":
            try:
                from statsmodels.tsa.arima.model import ARIMA
                self.model = ARIMA(self.baseline_data, order=(1, 0, 1))
                self.model_fit = self.model.fit()
            except ImportError:
                warnings.warn("statsmodels not available, falling back to statistical method")
                self.method = "statistical"

        return self

    def predict(self, X: Union[np.ndarray, pd.Series]) -> AnomalyResult:
        """Detect anomalies in time series."""
        if isinstance(X, pd.Series):
            X = X.values

        scores = np.zeros(len(X))

        if self.method == "arima" and hasattr(self, 'model_fit'):
            # Forecast and calculate residuals
            predictions = []
            for i in range(len(X)):
                if i < self.window_size:
                    pred = np.mean(self.baseline_data)
                else:
                    # Refit model with new data
                    try:
                        temp_data = np.concatenate([self.baseline_data, X[:i]])
                        model = ARIMA(temp_data[-self.window_size:], order=(1, 0, 1))
                        pred = model.fit().forecast(steps=1)[0]
                    except:
                        pred = np.mean(self.baseline_data)

                predictions.append(pred)

            predictions = np.array(predictions)
            residuals = np.abs(X - predictions)
            scores = residuals / (np.std(residuals) + 1e-9)

        else:
            # Statistical method: rolling z-score
            for i in range(len(X)):
                if i < self.window_size:
                    window_data = np.concatenate([self.baseline_data, X[:i+1]])
                else:
                    window_data = X[i-self.window_size:i+1]

                mean_val = np.mean(window_data[:-1])  # Exclude current point
                std_val = np.std(window_data[:-1]) + 1e-9
                scores[i] = abs(X[i] - mean_val) / std_val

        predictions = (scores > self.threshold).astype(int)

        return AnomalyResult(
            predictions=predictions,
            scores=scores,
            threshold=self.threshold,
            contamination_rate=np.mean(predictions),
            method=f"timeseries_{self.method}",
            training_time=0.0
        )


class AutoEncoderAnomalyDetector(nn.Module):
    """Autoencoder-based anomaly detection."""

    def __init__(self, input_dim: int, encoding_dim: int, hidden_dims: List[int] = None):
        super().__init__()
        if not HAS_PYTORCH:
            raise ImportError("PyTorch required for autoencoder anomaly detection")

        self.input_dim = input_dim
        self.encoding_dim = encoding_dim

        # Encoder
        encoder_layers = []
        prev_dim = input_dim

        if hidden_dims:
            for hidden_dim in hidden_dims:
                encoder_layers.extend([
                    nn.Linear(prev_dim, hidden_dim),
                    nn.ReLU()
                ])
                prev_dim = hidden_dim

        encoder_layers.append(nn.Linear(prev_dim, encoding_dim))
        self.encoder = nn.Sequential(*encoder_layers)

        # Decoder
        decoder_layers = []
        prev_dim = encoding_dim

        if hidden_dims:
            for hidden_dim in reversed(hidden_dims):
                decoder_layers.extend([
                    nn.Linear(prev_dim, hidden_dim),
                    nn.ReLU()
                ])
                prev_dim = hidden_dim

        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def fit(self, X: np.ndarray, epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001):
        """Train the autoencoder."""
        import torch.optim as optim
        from torch.utils.data import DataLoader, TensorDataset

        self.train()

        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()

        dataset = TensorDataset(torch.FloatTensor(X), torch.FloatTensor(X))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            total_loss = 0
            for batch_X, _ in dataloader:
                optimizer.zero_grad()
                outputs = self(batch_X)
                loss = criterion(outputs, batch_X)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

    def detect_anomalies(self, X: np.ndarray, threshold_percentile: float = 95) -> AnomalyResult:
        """Detect anomalies using reconstruction error."""
        self.eval()

        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            reconstructed = self(X_tensor)
            reconstruction_errors = torch.mean((X_tensor - reconstructed) ** 2, dim=1).numpy()

        # Determine threshold
        threshold = np.percentile(reconstruction_errors, threshold_percentile)
        predictions = (reconstruction_errors > threshold).astype(int)

        return AnomalyResult(
            predictions=predictions,
            scores=reconstruction_errors,
            threshold=threshold,
            contamination_rate=np.mean(predictions),
            method="autoencoder",
            training_time=0.0
        )


class AnomalyDetectionEvaluator:
    """Comprehensive evaluation of anomaly detection methods."""

    def __init__(self, contamination: float = None):
        self.contamination = contamination

    def evaluate(
        self,
        y_true: Union[np.ndarray, pd.Series],
        y_pred: Union[np.ndarray, pd.Series],
        scores: Optional[np.ndarray] = None
    ) -> AnomalyEvaluationMetrics:
        """Evaluate anomaly detection performance."""
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        # ROC AUC (if scores available)
        roc_auc = None
        if scores is not None:
            try:
                roc_auc = roc_auc_score(y_true, scores)
            except:
                pass

        # Confusion matrix and report
        cm = confusion_matrix(y_true, y_pred)
        report = classification_report(y_true, y_pred, zero_division=0)

        # Contamination rate
        contamination_rate = np.mean(y_pred)

        return AnomalyEvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            confusion_matrix=cm,
            classification_report=report,
            contamination_rate=contamination_rate
        )

    def compare_methods(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y_true: Union[np.ndarray, pd.Series],
        methods: List[str] = None
    ) -> Dict[str, AnomalyEvaluationMetrics]:
        """Compare multiple anomaly detection methods."""
        if methods is None:
            methods = ["isolation_forest", "one_class_svm", "local_outlier_factor"]

        results = {}

        for method in methods:
            try:
                config = AnomalyDetectionConfig(method=method, contamination=self.contamination)
                detector = AdvancedAnomalyDetector(config)
                detector.fit(X)
                predictions = detector.predict(X)

                metrics = self.evaluate(y_true, predictions.predictions, predictions.scores)
                results[method] = metrics

            except Exception as e:
                warnings.warn(f"Method {method} failed: {e}")
                continue

        return results


__all__ = [
    "AnomalyDetectionConfig",
    "AnomalyResult",
    "AnomalyEvaluationMetrics",
    "AdvancedAnomalyDetector",
    "StatisticalAnomalyDetector",
    "EnsembleAnomalyDetector",
    "TimeSeriesAnomalyDetector",
    "AutoEncoderAnomalyDetector",
    "AnomalyDetectionEvaluator",
]

"""Advanced time series forecasting methods and utilities."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Optional dependencies
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.seasonal import seasonal_decompose
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


@dataclass(slots=True)
class TimeSeriesConfig:
    """Configuration for time series forecasting."""
    method: str = "arima"
    seasonal: bool = False
    seasonal_periods: int = 7
    trend: str = "add"
    damped_trend: bool = False
    use_box_cox: bool = False
    remove_outliers: bool = False
    outlier_threshold: float = 3.0


@dataclass(slots=True)
class ForecastingResult:
    """Result from time series forecasting."""
    predictions: np.ndarray
    confidence_intervals: Optional[np.ndarray] = None
    model: Any = None
    method: str = ""
    training_time: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TimeSeriesForecaster:
    """Advanced time series forecasting with multiple methods."""

    def __init__(self, config: TimeSeriesConfig):
        self.config = config
        self.model = None
        self.scaler = None
        self.is_fitted = False

    def fit(self, y: Union[np.ndarray, pd.Series], X: Optional[pd.DataFrame] = None) -> 'TimeSeriesForecaster':
        """Fit the forecasting model."""
        start_time = time.time()

        # Prepare data
        if isinstance(y, pd.Series):
            y = y.values

        y_processed = self._preprocess_series(y)

        # Fit model based on method
        if self.config.method == "arima":
            self._fit_arima(y_processed)
        elif self.config.method == "sarima":
            self._fit_sarima(y_processed)
        elif self.config.method == "exponential_smoothing":
            self._fit_exponential_smoothing(y_processed)
        elif self.config.method == "prophet":
            self._fit_prophet(y_processed)
        elif self.config.method == "lstm":
            self._fit_lstm(y_processed, X)
        else:
            raise ValueError(f"Unknown forecasting method: {self.config.method}")

        self.training_time = time.time() - start_time
        self.is_fitted = True

        return self

    def predict(
        self,
        steps: int,
        X_future: Optional[pd.DataFrame] = None,
        return_confidence: bool = True
    ) -> ForecastingResult:
        """Make predictions."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")

        if self.config.method in ["arima", "sarima"]:
            predictions, conf_int = self._predict_arima_sarima(steps, return_confidence)
        elif self.config.method == "exponential_smoothing":
            predictions, conf_int = self._predict_exponential_smoothing(steps, return_confidence)
        elif self.config.method == "prophet":
            predictions, conf_int = self._predict_prophet(steps, return_confidence)
        elif self.config.method == "lstm":
            predictions, conf_int = self._predict_lstm(steps, X_future, return_confidence)
        else:
            raise ValueError(f"Unknown forecasting method: {self.config.method}")

        # Post-process predictions
        predictions = self._postprocess_predictions(predictions)

        return ForecastingResult(
            predictions=predictions,
            confidence_intervals=conf_int,
            model=self.model,
            method=self.config.method,
            training_time=self.training_time
        )

    def _preprocess_series(self, y: np.ndarray) -> np.ndarray:
        """Preprocess time series data."""
        y_processed = y.copy()

        # Remove outliers if requested
        if self.config.remove_outliers:
            z_scores = np.abs((y_processed - np.mean(y_processed)) / np.std(y_processed))
            outlier_mask = z_scores > self.config.outlier_threshold
            y_processed[outlier_mask] = np.median(y_processed[~outlier_mask])

        # Scale data
        self.scaler = StandardScaler()
        y_processed = self.scaler.fit_transform(y_processed.reshape(-1, 1)).flatten()

        return y_processed

    def _postprocess_predictions(self, predictions: np.ndarray) -> np.ndarray:
        """Post-process predictions (inverse transform)."""
        if self.scaler is not None:
            predictions = self.scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
        return predictions

    def _fit_arima(self, y: np.ndarray):
        """Fit ARIMA model."""
        if not HAS_STATSMODELS:
            raise ImportError("statsmodels required for ARIMA")

        # Auto-select order (simplified)
        self.model = ARIMA(y, order=(1, 1, 1))
        self.model_fit = self.model.fit()

    def _fit_sarima(self, y: np.ndarray):
        """Fit SARIMA model."""
        if not HAS_STATSMODELS:
            raise ImportError("statsmodels required for SARIMA")

        self.model = SARIMAX(
            y,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, self.config.seasonal_periods)
        )
        self.model_fit = self.model.fit(disp=False)

    def _fit_exponential_smoothing(self, y: np.ndarray):
        """Fit Exponential Smoothing model."""
        if not HAS_STATSMODELS:
            raise ImportError("statsmodels required for Exponential Smoothing")

        self.model = ExponentialSmoothing(
            y,
            seasonal=self.config.seasonal,
            seasonal_periods=self.config.seasonal_periods if self.config.seasonal else None,
            trend=self.config.trend,
            damped_trend=self.config.damped_trend
        )
        self.model_fit = self.model.fit()

    def _fit_prophet(self, y: np.ndarray):
        """Fit Facebook Prophet model."""
        if not HAS_PROPHET:
            raise ImportError("prophet required for Prophet forecasting")

        # Create dataframe for Prophet
        dates = pd.date_range(start='2020-01-01', periods=len(y), freq='D')
        df = pd.DataFrame({'ds': dates, 'y': y})

        self.model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=self.config.seasonal,
            daily_seasonality=False
        )
        self.model.fit(df)

    def _fit_lstm(self, y: np.ndarray, X: Optional[pd.DataFrame]):
        """Fit LSTM model."""
        if not HAS_PYTORCH:
            raise ImportError("PyTorch required for LSTM")

        # Create sequences
        sequence_length = 10  # Default
        X_seq, y_seq = self._create_sequences(y, sequence_length)

        # Create LSTM model
        self.model = LSTMForecaster(
            input_size=1,
            hidden_size=50,
            num_layers=2,
            output_size=1,
            sequence_length=sequence_length
        )

        # Train model
        self.model.fit(X_seq, y_seq, epochs=50, batch_size=32)

    def _predict_arima_sarima(self, steps: int, return_confidence: bool) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Make predictions with ARIMA/SARIMA."""
        forecast = self.model_fit.forecast(steps=steps)

        conf_int = None
        if return_confidence:
            try:
                conf_int_result = self.model_fit.get_forecast(steps=steps).conf_int()
                conf_int = conf_int_result.values
            except:
                pass

        return forecast, conf_int

    def _predict_exponential_smoothing(self, steps: int, return_confidence: bool) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Make predictions with Exponential Smoothing."""
        forecast = self.model_fit.forecast(steps=steps)

        conf_int = None
        # Exponential smoothing doesn't provide confidence intervals by default

        return forecast, conf_int

    def _predict_prophet(self, steps: int, return_confidence: bool) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Make predictions with Prophet."""
        future_dates = self.model.make_future_dataframe(periods=steps)
        forecast = self.model.predict(future_dates)

        predictions = forecast['yhat'].values[-steps:]

        conf_int = None
        if return_confidence:
            lower = forecast['yhat_lower'].values[-steps:]
            upper = forecast['yhat_upper'].values[-steps:]
            conf_int = np.column_stack([lower, upper])

        return predictions, conf_int

    def _predict_lstm(self, steps: int, X_future: Optional[pd.DataFrame], return_confidence: bool) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Make predictions with LSTM."""
        predictions = self.model.predict(steps=steps)

        conf_int = None
        # LSTM doesn't provide confidence intervals by default

        return predictions, conf_int

    def _create_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:i+sequence_length])
            y.append(data[i+sequence_length])
        return np.array(X), np.array(y)


class LSTMForecaster(nn.Module):
    """LSTM-based time series forecaster."""

    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int, sequence_length: int):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.sequence_length = sequence_length

        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, batch_size: int = 32):
        """Train the LSTM model."""
        X_tensor = torch.FloatTensor(X).unsqueeze(-1)  # Add feature dimension
        y_tensor = torch.FloatTensor(y).unsqueeze(-1)

        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.parameters())

        self.train()
        for epoch in range(epochs):
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

    def predict(self, steps: int) -> np.ndarray:
        """Make multi-step predictions."""
        self.eval()

        # Start with the last sequence from training
        # This is a simplified implementation
        predictions = []

        with torch.no_grad():
            # Initialize with zeros (simplified)
            current_input = torch.zeros(1, self.sequence_length, 1)

            for _ in range(steps):
                output = self(current_input)
                pred = output.item()
                predictions.append(pred)

                # Update input sequence (simplified rolling)
                current_input = torch.roll(current_input, -1, dims=1)
                current_input[0, -1, 0] = pred

        return np.array(predictions)


class EnsembleTimeSeriesForecaster:
    """Ensemble of multiple time series forecasting methods."""

    def __init__(self, configs: List[TimeSeriesConfig], weights: Optional[List[float]] = None):
        self.configs = configs
        self.weights = weights or [1.0 / len(configs)] * len(configs)
        self.models = []

    def fit(self, y: Union[np.ndarray, pd.Series], X: Optional[pd.DataFrame] = None) -> 'EnsembleTimeSeriesForecaster':
        """Fit all models in the ensemble."""
        self.models = []

        for config in self.configs:
            try:
                forecaster = TimeSeriesForecaster(config)
                forecaster.fit(y, X)
                self.models.append(forecaster)
            except Exception as e:
                warnings.warn(f"Failed to fit {config.method}: {e}")
                continue

        return self

    def predict(self, steps: int, X_future: Optional[pd.DataFrame] = None) -> ForecastingResult:
        """Make ensemble predictions."""
        if not self.models:
            raise RuntimeError("No models fitted")

        predictions_list = []
        confidence_intervals_list = []

        for model in self.models:
            try:
                result = model.predict(steps, X_future)
                predictions_list.append(result.predictions)

                if result.confidence_intervals is not None:
                    confidence_intervals_list.append(result.confidence_intervals)
            except Exception as e:
                warnings.warn(f"Model prediction failed: {e}")
                continue

        if not predictions_list:
            raise RuntimeError("All model predictions failed")

        # Ensemble predictions (weighted average)
        predictions = np.average(predictions_list, axis=0, weights=self.weights[:len(predictions_list)])

        # Ensemble confidence intervals (simplified)
        conf_int = None
        if confidence_intervals_list:
            # Take the average of confidence intervals
            avg_lower = np.average([ci[:, 0] for ci in confidence_intervals_list], axis=0, weights=self.weights[:len(confidence_intervals_list)])
            avg_upper = np.average([ci[:, 1] for ci in confidence_intervals_list], axis=0, weights=self.weights[:len(confidence_intervals_list)])
            conf_int = np.column_stack([avg_lower, avg_upper])

        return ForecastingResult(
            predictions=predictions,
            confidence_intervals=conf_int,
            method="ensemble",
            training_time=sum(model.training_time for model in self.models)
        )


class SklearnCompatibleTimeSeriesForecaster(BaseEstimator, RegressorMixin):
    """Scikit-learn compatible time series forecaster."""

    def __init__(
        self,
        method: str = "arima",
        sequence_length: int = 10,
        forecast_horizon: int = 1,
        **kwargs
    ):
        self.method = method
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.kwargs = kwargs
        self.forecaster = None

    def fit(self, X, y):
        """Fit the forecaster."""
        # Convert to supervised learning problem
        X_supervised, y_supervised = self._create_supervised_data(y)

        if self.method == "lightgbm":
            if not HAS_LIGHTGBM:
                raise ImportError("lightgbm required for LightGBM forecasting")

            self.model = lgb.LGBMRegressor(**self.kwargs)
            self.model.fit(X_supervised, y_supervised)
        else:
            # Use time series forecaster
            config = TimeSeriesConfig(method=self.method, **self.kwargs)
            self.forecaster = TimeSeriesForecaster(config)
            self.forecaster.fit(y)

        return self

    def predict(self, X):
        """Make predictions."""
        if self.forecaster is not None:
            # Time series forecasting
            steps = len(X) if hasattr(X, '__len__') else 1
            result = self.forecaster.predict(steps)
            return result.predictions
        else:
            # Supervised learning approach
            return self.model.predict(X)

    def _create_supervised_data(self, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create supervised learning dataset from time series."""
        X, y_supervised = [], []

        for i in range(len(y) - self.sequence_length - self.forecast_horizon + 1):
            X.append(y[i:i+self.sequence_length])
            y_supervised.append(y[i+self.sequence_length:i+self.sequence_length+self.forecast_horizon])

        return np.array(X), np.array(y_supervised)


class TimeSeriesEvaluator:
    """Comprehensive evaluation of time series forecasting methods."""

    def __init__(self, metrics: Optional[List[str]] = None):
        self.metrics = metrics or ["mse", "mae", "rmse", "mape", "smape", "r2"]

    def evaluate(
        self,
        y_true: Union[np.ndarray, pd.Series],
        y_pred: Union[np.ndarray, pd.Series]
    ) -> Dict[str, float]:
        """Evaluate forecasting performance."""
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        results = {}

        # Basic metrics
        if "mse" in self.metrics:
            results["mse"] = mean_squared_error(y_true, y_pred)

        if "mae" in self.metrics:
            results["mae"] = mean_absolute_error(y_true, y_pred)

        if "rmse" in self.metrics:
            results["rmse"] = np.sqrt(mean_squared_error(y_true, y_pred))

        if "mape" in self.metrics:
            # Mean Absolute Percentage Error
            results["mape"] = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-9))) * 100

        if "smape" in self.metrics:
            # Symmetric Mean Absolute Percentage Error
            numerator = 2 * np.abs(y_true - y_pred)
            denominator = np.abs(y_true) + np.abs(y_pred) + 1e-9
            results["smape"] = np.mean(numerator / denominator) * 100

        if "r2" in self.metrics:
            results["r2"] = r2_score(y_true, y_pred)

        return results

    def cross_validate(
        self,
        forecaster_class: type,
        y: Union[np.ndarray, pd.Series],
        config: TimeSeriesConfig,
        cv_splits: int = 5
    ) -> Dict[str, List[float]]:
        """Cross-validate time series forecasting."""
        y = np.asarray(y)

        tscv = TimeSeriesSplit(n_splits=cv_splits)
        cv_results = {metric: [] for metric in self.metrics}

        for train_idx, test_idx in tscv.split(y):
            try:
                y_train, y_test = y[train_idx], y[test_idx]

                forecaster = forecaster_class(config)
                forecaster.fit(y_train)

                predictions = forecaster.predict(len(y_test))
                y_pred = predictions.predictions

                fold_metrics = self.evaluate(y_test, y_pred)

                for metric in self.metrics:
                    cv_results[metric].append(fold_metrics.get(metric, np.nan))

            except Exception as e:
                warnings.warn(f"Cross-validation fold failed: {e}")
                for metric in self.metrics:
                    cv_results[metric].append(np.nan)

        return cv_results


__all__ = [
    "TimeSeriesConfig",
    "ForecastingResult",
    "TimeSeriesForecaster",
    "LSTMForecaster",
    "EnsembleTimeSeriesForecaster",
    "SklearnCompatibleTimeSeriesForecaster",
    "TimeSeriesEvaluator",
]

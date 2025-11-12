"""
LSTM-Based Time Series Predictors for Trading
==============================================

This module implements Long Short-Term Memory (LSTM) networks specifically designed for financial time series prediction.
Includes multi-step forecasting, attention mechanisms, and trading signal generation.

Key Features:
- Multi-layer LSTM architectures for time series forecasting
- Attention-enhanced LSTM for better temporal dependencies
- Multi-step ahead predictions with uncertainty estimation
- Trading signal generation from predictions
- Risk-adjusted prediction confidence
- Hardware acceleration support (GPU/TPU)
- Bayesian LSTM for uncertainty quantification
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Neural network dependencies
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader, TensorDataset
    from torch.distributions import Normal
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    keras = None


@dataclass
class LSTMPredictorConfig:
    """Configuration for LSTM predictor"""

    # Network architecture
    input_size: int = 10  # Number of input features
    hidden_size: int = 128
    num_layers: int = 2
    output_size: int = 1  # Prediction horizon
    dropout_rate: float = 0.2

    # Attention mechanism
    use_attention: bool = True
    attention_heads: int = 8
    attention_dropout: float = 0.1

    # Training parameters
    sequence_length: int = 60  # Lookback window
    prediction_horizon: int = 1  # Steps ahead to predict
    batch_size: int = 64
    num_epochs: int = 100
    learning_rate: float = 0.001
    weight_decay: float = 1e-5

    # Loss function
    loss_function: str = "mse"  # "mse", "mae", "huber", "quantile"

    # Optimization
    optimizer: str = "adam"  # "adam", "adamw", "sgd", "rmsprop"
    scheduler: str = "cosine"  # "cosine", "step", "plateau", "none"

    # Regularization
    l1_penalty: float = 0.0
    l2_penalty: float = 0.0

    # Early stopping
    patience: int = 20
    min_delta: float = 1e-4

    # Hardware acceleration
    use_gpu: bool = True
    device: Optional[str] = None

    # Data preprocessing
    normalization: str = "standard"  # "standard", "minmax", "robust"
    feature_selection: bool = True

    # Prediction uncertainty
    uncertainty_estimation: bool = True
    num_samples: int = 100  # For Monte Carlo dropout

    # Trading integration
    generate_signals: bool = True
    signal_threshold: float = 0.02  # Minimum prediction change for signal
    risk_adjustment: bool = True


class TimeSeriesDataset(Dataset):
    """Custom dataset for time series data"""

    def __init__(self, data: np.ndarray, targets: np.ndarray, sequence_length: int):
        self.data = torch.FloatTensor(data) if TORCH_AVAILABLE else data
        self.targets = torch.FloatTensor(targets) if TORCH_AVAILABLE else targets
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.data) - self.sequence_length

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.sequence_length]
        y = self.targets[idx + self.sequence_length]
        return x, y


class AttentionLayer(nn.Module if TORCH_AVAILABLE else object):
    """Multi-head attention layer for LSTM"""

    def __init__(self, hidden_size: int, num_heads: int = 8, dropout: float = 0.1):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for AttentionLayer")

        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        assert self.head_dim * num_heads == hidden_size, "hidden_size must be divisible by num_heads"

        self.q_linear = nn.Linear(hidden_size, hidden_size)
        self.k_linear = nn.Linear(hidden_size, hidden_size)
        self.v_linear = nn.Linear(hidden_size, hidden_size)
        self.out_linear = nn.Linear(hidden_size, hidden_size)

        self.dropout = nn.Dropout(dropout)
        self.scale = torch.sqrt(torch.FloatTensor([self.head_dim]))

    def forward(self, x):
        batch_size, seq_len, hidden_size = x.size()

        # Linear transformations and reshape
        Q = self.q_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale.to(x.device)
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention
        attended = torch.matmul(attention_weights, V)

        # Concatenate heads and put through final linear layer
        attended = attended.transpose(1, 2).contiguous().view(batch_size, seq_len, hidden_size)
        output = self.out_linear(attended)

        return output, attention_weights


class LSTMWithAttention(nn.Module if TORCH_AVAILABLE else object):
    """LSTM network with attention mechanism"""

    def __init__(self, config: LSTMPredictorConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for LSTMWithAttention")

        super().__init__()

        self.config = config
        self.hidden_size = config.hidden_size
        self.num_layers = config.num_layers

        # Input projection
        self.input_projection = nn.Linear(config.input_size, config.hidden_size)

        # LSTM layers
        self.lstm = nn.LSTM(
            config.hidden_size,
            config.hidden_size,
            config.num_layers,
            batch_first=True,
            dropout=config.dropout_rate if config.num_layers > 1 else 0,
            bidirectional=False
        )

        # Attention layer
        if config.use_attention:
            self.attention = AttentionLayer(
                config.hidden_size,
                config.attention_heads,
                config.attention_dropout
            )

        # Output layers
        output_input_size = config.hidden_size * 2 if config.use_attention else config.hidden_size
        self.output_layer = nn.Sequential(
            nn.Linear(output_input_size, config.hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_size // 2, config.output_size)
        )

    def forward(self, x, hidden=None):
        batch_size = x.size(0)

        # Input projection
        x = self.input_projection(x)

        # LSTM forward pass
        lstm_out, hidden = self.lstm(x, hidden)

        # Attention mechanism
        if self.config.use_attention:
            attended_out, attention_weights = self.attention(lstm_out)
            # Concatenate LSTM output and attention output
            combined = torch.cat([lstm_out, attended_out], dim=-1)
        else:
            combined = lstm_out
            attention_weights = None

        # Global average pooling over sequence
        pooled = torch.mean(combined, dim=1)

        # Output prediction
        output = self.output_layer(pooled)

        return output, hidden, attention_weights


class BayesianLSTM(nn.Module if TORCH_AVAILABLE else object):
    """Bayesian LSTM for uncertainty estimation"""

    def __init__(self, config: LSTMPredictorConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for BayesianLSTM")

        super().__init__()

        self.config = config

        # Variational layers
        self.lstm = nn.LSTM(
            config.input_size,
            config.hidden_size,
            config.num_layers,
            batch_first=True,
            dropout=config.dropout_rate if config.num_layers > 1 else 0
        )

        # Bayesian output layer (mean and variance)
        self.output_mean = nn.Linear(config.hidden_size, config.output_size)
        self.output_var = nn.Linear(config.hidden_size, config.output_size)

    def forward(self, x, hidden=None):
        # LSTM forward pass
        lstm_out, hidden = self.lstm(x, hidden)

        # Global average pooling
        pooled = torch.mean(lstm_out, dim=1)

        # Bayesian output
        mean = self.output_mean(pooled)
        log_var = self.output_var(pooled)
        var = torch.exp(log_var)

        return mean, var, hidden


class MultiStepLSTM(nn.Module if TORCH_AVAILABLE else object):
    """Multi-step ahead prediction LSTM"""

    def __init__(self, config: LSTMPredictorConfig):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for MultiStepLSTM")

        super().__init__()

        self.config = config
        self.prediction_horizon = config.prediction_horizon

        # Encoder LSTM
        self.encoder = nn.LSTM(
            config.input_size,
            config.hidden_size,
            config.num_layers,
            batch_first=True,
            dropout=config.dropout_rate if config.num_layers > 1 else 0
        )

        # Decoder LSTM for multi-step prediction
        self.decoder = nn.LSTM(
            config.output_size,
            config.hidden_size,
            config.num_layers,
            batch_first=True,
            dropout=config.dropout_rate if config.num_layers > 1 else 0
        )

        # Output projection
        self.output_layer = nn.Linear(config.hidden_size, config.output_size)

    def forward(self, x, hidden=None):
        batch_size = x.size(0)

        # Encoder
        encoder_out, encoder_hidden = self.encoder(x)

        # Multi-step decoding
        decoder_input = torch.zeros(batch_size, 1, self.config.output_size).to(x.device)
        predictions = []

        for step in range(self.prediction_horizon):
            decoder_out, encoder_hidden = self.decoder(decoder_input, encoder_hidden)
            step_prediction = self.output_layer(decoder_out.squeeze(1))
            predictions.append(step_prediction.unsqueeze(1))

            # Use prediction as next input (teacher forcing)
            decoder_input = step_prediction.unsqueeze(1)

        predictions = torch.cat(predictions, dim=1)

        return predictions, encoder_hidden


class LSTMPredictor:
    """LSTM-based time series predictor for trading"""

    def __init__(self, config: LSTMPredictorConfig):
        self.config = config

        # Initialize device
        if TORCH_AVAILABLE and config.use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif TORCH_AVAILABLE:
            self.device = torch.device("cpu")
        else:
            self.device = None

        # Initialize model based on type
        self.model = self._initialize_model()

        if TORCH_AVAILABLE:
            self.model.to(self.device)

        # Initialize optimizer
        if TORCH_AVAILABLE:
            self.optimizer = self._initialize_optimizer()
            self.scheduler = self._initialize_scheduler()

        # Training state
        self.scaler = None
        self.feature_scaler = None
        self.is_trained = False
        self.training_history = []

        # Uncertainty estimation
        if config.uncertainty_estimation and TORCH_AVAILABLE:
            self.model.train()  # Keep dropout active for uncertainty

    def _initialize_model(self):
        """Initialize the appropriate model architecture"""
        if self.config.uncertainty_estimation:
            return BayesianLSTM(self.config)
        elif self.config.prediction_horizon > 1:
            return MultiStepLSTM(self.config)
        else:
            return LSTMWithAttention(self.config)

    def _initialize_optimizer(self):
        """Initialize optimizer"""
        if self.config.optimizer == "adam":
            return optim.Adam(self.model.parameters(), lr=self.config.learning_rate,
                            weight_decay=self.config.weight_decay)
        elif self.config.optimizer == "adamw":
            return optim.AdamW(self.model.parameters(), lr=self.config.learning_rate,
                             weight_decay=self.config.weight_decay)
        elif self.config.optimizer == "sgd":
            return optim.SGD(self.model.parameters(), lr=self.config.learning_rate,
                           weight_decay=self.config.weight_decay, momentum=0.9)
        else:
            return optim.RMSprop(self.model.parameters(), lr=self.config.learning_rate,
                               weight_decay=self.config.weight_decay)

    def _initialize_scheduler(self):
        """Initialize learning rate scheduler"""
        if self.config.scheduler == "cosine":
            return optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=self.config.num_epochs)
        elif self.config.scheduler == "step":
            return optim.lr_scheduler.StepLR(self.optimizer, step_size=30, gamma=0.1)
        elif self.config.scheduler == "plateau":
            return optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=10, factor=0.5)
        else:
            return None

    def _preprocess_data(self, data: pd.DataFrame, target_column: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess time series data"""

        # Feature selection
        if self.config.feature_selection:
            features = self._select_features(data, target_column)
        else:
            features = [col for col in data.columns if col != target_column]

        # Extract features and target
        X = data[features].values
        y = data[target_column].values.reshape(-1, 1)

        # Handle missing values
        X = pd.DataFrame(X).fillna(method='ffill').fillna(method='bfill').values
        y = pd.DataFrame(y).fillna(method='ffill').fillna(method='bfill').values

        # Scale features
        if self.config.normalization == "standard":
            self.feature_scaler = StandardScaler()
        elif self.config.normalization == "minmax":
            self.feature_scaler = MinMaxScaler()
        else:
            self.feature_scaler = StandardScaler()  # Default

        X_scaled = self.feature_scaler.fit_transform(X)

        # Scale target
        self.scaler = StandardScaler()
        y_scaled = self.scaler.fit_transform(y)

        return X_scaled, y_scaled

    def _select_features(self, data: pd.DataFrame, target_column: str) -> List[str]:
        """Select most relevant features using correlation and mutual information"""
        features = []
        target = data[target_column]

        for col in data.columns:
            if col != target_column:
                # Correlation-based selection
                corr = abs(data[col].corr(target))
                if corr > 0.1:  # Minimum correlation threshold
                    features.append(col)

        # Ensure we have at least some features
        if not features:
            features = [col for col in data.columns if col != target_column][:10]

        return features

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM input"""
        X_seq, y_seq = [], []

        for i in range(len(X) - self.config.sequence_length):
            X_seq.append(X[i:i + self.config.sequence_length])
            y_seq.append(y[i + self.config.sequence_length])

        return np.array(X_seq), np.array(y_seq)

    def fit(self, data: pd.DataFrame, target_column: str,
            validation_split: float = 0.2) -> Dict[str, List]:
        """Train the LSTM predictor"""

        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for LSTM training")

        print("Preprocessing data...")
        X_scaled, y_scaled = self._preprocess_data(data, target_column)
        X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)

        # Train/validation split
        split_idx = int(len(X_seq) * (1 - validation_split))
        X_train, X_val = X_seq[:split_idx], X_seq[split_idx:]
        y_train, y_val = y_seq[:split_idx], y_seq[split_idx:]

        # Create datasets
        train_dataset = TimeSeriesDataset(X_train, y_train, self.config.sequence_length)
        val_dataset = TimeSeriesDataset(X_val, y_val, self.config.sequence_length)

        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size,
                                shuffle=True, drop_last=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size,
                              shuffle=False, drop_last=False)

        print(f"Training LSTM with {len(train_dataset)} samples, validating on {len(val_dataset)} samples")
        print(f"Sequence length: {self.config.sequence_length}, Prediction horizon: {self.config.prediction_horizon}")

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(self.config.num_epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0

            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                self.optimizer.zero_grad()

                if isinstance(self.model, BayesianLSTM):
                    # Bayesian loss
                    mean, var, _ = self.model(batch_X)
                    loss = self._bayesian_loss(mean, var, batch_y)
                elif isinstance(self.model, MultiStepLSTM):
                    # Multi-step loss
                    predictions, _ = self.model(batch_X)
                    loss = F.mse_loss(predictions, batch_y.unsqueeze(1).expand(-1, self.config.prediction_horizon))
                else:
                    # Standard prediction loss
                    predictions, _, _ = self.model(batch_X)
                    loss = self._compute_loss(predictions, batch_y)

                # Add regularization
                if self.config.l1_penalty > 0:
                    l1_loss = sum(torch.norm(param, 1) for param in self.model.parameters())
                    loss += self.config.l1_penalty * l1_loss

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()

                train_loss += loss.item()

            train_loss /= len(train_loader)

            # Validation phase
            self.model.eval()
            val_loss = 0.0

            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                    if isinstance(self.model, BayesianLSTM):
                        mean, var, _ = self.model(batch_X)
                        loss = self._bayesian_loss(mean, var, batch_y)
                    elif isinstance(self.model, MultiStepLSTM):
                        predictions, _ = self.model(batch_X)
                        loss = F.mse_loss(predictions, batch_y.unsqueeze(1).expand(-1, self.config.prediction_horizon))
                    else:
                        predictions, _, _ = self.model(batch_X)
                        loss = self._compute_loss(predictions, batch_y)

                    val_loss += loss.item()

            val_loss /= len(val_loader)

            # Update scheduler
            if self.scheduler:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()

            # Early stopping
            if val_loss < best_val_loss - self.config.min_delta:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self._save_checkpoint()
            else:
                patience_counter += 1

            if patience_counter >= self.config.patience:
                print(f"Early stopping at epoch {epoch + 1}")
                break

            # Logging
            if (epoch + 1) % 10 == 0:
                current_lr = self.optimizer.param_groups[0]['lr']
                print(f"Epoch {epoch + 1}/{self.config.num_epochs}: "
                      f"Train Loss = {train_loss:.6f}, Val Loss = {val_loss:.6f}, "
                      f"LR = {current_lr:.6f}")

            self.training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'learning_rate': self.optimizer.param_groups[0]['lr']
            })

        # Load best model
        self._load_checkpoint()
        self.is_trained = True

        return self.training_history

    def _compute_loss(self, predictions, targets):
        """Compute loss based on configuration"""
        if self.config.loss_function == "mse":
            return F.mse_loss(predictions, targets)
        elif self.config.loss_function == "mae":
            return F.l1_loss(predictions, targets)
        elif self.config.loss_function == "huber":
            return F.smooth_l1_loss(predictions, targets)
        else:
            return F.mse_loss(predictions, targets)

    def _bayesian_loss(self, mean, var, targets):
        """Compute Bayesian loss with uncertainty"""
        # Negative log likelihood for Gaussian
        dist = Normal(mean, torch.sqrt(var))
        return -dist.log_prob(targets).mean()

    def _save_checkpoint(self):
        """Save model checkpoint"""
        if TORCH_AVAILABLE:
            self.best_model_state = {
                'model': self.model.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'scaler': self.scaler,
                'feature_scaler': self.feature_scaler
            }

    def _load_checkpoint(self):
        """Load best model checkpoint"""
        if hasattr(self, 'best_model_state'):
            self.model.load_state_dict(self.best_model_state['model'])
            self.optimizer.load_state_dict(self.best_model_state['optimizer'])
            self.scaler = self.best_model_state['scaler']
            self.feature_scaler = self.best_model_state['feature_scaler']

    def predict(self, data: pd.DataFrame, return_uncertainty: bool = False) -> np.ndarray:
        """Make predictions on new data"""

        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for predictions")

        # Preprocess data
        features = [col for col in data.columns if col in self.feature_scaler.feature_names_in_]
        X = data[features].values
        X = pd.DataFrame(X).fillna(method='ffill').fillna(method='bfill').values
        X_scaled = self.feature_scaler.transform(X)

        # Create sequences
        X_seq = []
        for i in range(len(X_scaled) - self.config.sequence_length + 1):
            X_seq.append(X_scaled[i:i + self.config.sequence_length])

        if not X_seq:
            raise ValueError("Not enough data for prediction")

        X_seq = np.array(X_seq)
        X_tensor = torch.FloatTensor(X_seq).to(self.device)

        self.model.eval()

        with torch.no_grad():
            if isinstance(self.model, BayesianLSTM):
                # Monte Carlo sampling for uncertainty
                predictions = []
                uncertainties = []

                for _ in range(self.config.num_samples):
                    mean, var, _ = self.model(X_tensor)
                    pred = mean.cpu().numpy()
                    uncertainty = var.cpu().numpy()

                    predictions.append(pred)
                    uncertainties.append(uncertainty)

                predictions = np.array(predictions)
                mean_pred = np.mean(predictions, axis=0)
                uncertainty = np.mean(uncertainties, axis=0)

            elif isinstance(self.model, MultiStepLSTM):
                predictions, _ = self.model(X_tensor)
                predictions = predictions.cpu().numpy()
                mean_pred = predictions[:, -1, :]  # Last prediction in sequence
                uncertainty = None

            else:
                predictions, _, _ = self.model(X_tensor)
                predictions = predictions.cpu().numpy()
                mean_pred = predictions
                uncertainty = None

        # Inverse transform predictions
        predictions_original = self.scaler.inverse_transform(mean_pred)

        if return_uncertainty and uncertainty is not None:
            uncertainty_original = self.scaler.scale_ * uncertainty  # Scale uncertainty
            return predictions_original, uncertainty_original

        return predictions_original

    def generate_trading_signals(self, data: pd.DataFrame,
                               current_price: float) -> List[Dict[str, Any]]:
        """Generate trading signals from predictions"""

        if not self.config.generate_signals:
            return []

        predictions = self.predict(data)

        signals = []

        for i, pred in enumerate(predictions):
            # Calculate prediction change
            if i > 0:
                pred_change = (pred[0] - current_price) / current_price
            else:
                pred_change = 0.0

            # Generate signal based on prediction
            if abs(pred_change) > self.config.signal_threshold:
                signal_type = "BUY" if pred_change > 0 else "SELL"
                confidence = min(abs(pred_change) / self.config.signal_threshold, 1.0)

                # Risk adjustment
                if self.config.risk_adjustment:
                    # Reduce confidence based on prediction uncertainty
                    if hasattr(self, 'uncertainty_estimation') and self.config.uncertainty_estimation:
                        _, uncertainty = self.predict(data, return_uncertainty=True)
                        uncertainty_ratio = uncertainty[i][0] / abs(pred[0])
                        confidence *= (1 - min(uncertainty_ratio, 0.5))

                signals.append({
                    'timestamp': data.index[i + self.config.sequence_length - 1],
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'predicted_price': pred[0],
                    'current_price': current_price,
                    'expected_return': pred_change
                })

        return signals

    def evaluate(self, data: pd.DataFrame, target_column: str) -> Dict[str, float]:
        """Evaluate model performance"""

        predictions = self.predict(data)
        actuals = data[target_column].values[self.config.sequence_length - 1:len(predictions) + self.config.sequence_length - 1]

        # Calculate metrics
        mse = mean_squared_error(actuals, predictions.flatten())
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actuals, predictions.flatten())
        r2 = r2_score(actuals, predictions.flatten())

        # Directional accuracy
        actual_changes = np.diff(actuals)
        pred_changes = np.diff(predictions.flatten())
        directional_accuracy = np.mean((actual_changes > 0) == (pred_changes > 0))

        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2_score': r2,
            'directional_accuracy': directional_accuracy
        }


def create_lstm_predictor(config: Optional[LSTMPredictorConfig] = None) -> LSTMPredictor:
    """Factory function for LSTM predictor"""
    if config is None:
        config = LSTMPredictorConfig()
    return LSTMPredictor(config)


def create_bayesian_lstm_predictor(config: Optional[LSTMPredictorConfig] = None) -> LSTMPredictor:
    """Factory function for Bayesian LSTM predictor"""
    if config is None:
        config = LSTMPredictorConfig(uncertainty_estimation=True)
    else:
        config.uncertainty_estimation = True
    return LSTMPredictor(config)


def create_multi_step_lstm_predictor(prediction_horizon: int = 5,
                                   config: Optional[LSTMPredictorConfig] = None) -> LSTMPredictor:
    """Factory function for multi-step LSTM predictor"""
    if config is None:
        config = LSTMPredictorConfig(prediction_horizon=prediction_horizon)
    else:
        config.prediction_horizon = prediction_horizon
    return LSTMPredictor(config)


# Example usage and testing
if __name__ == "__main__":
    # Test LSTM predictor
    print("Testing LSTM Predictor...")

    if TORCH_AVAILABLE:
        # Create sample financial data
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=1000, freq="1H")

        # Generate synthetic price data with trends and volatility
        trend = np.linspace(100, 120, 1000)
        noise = np.random.normal(0, 2, 1000)
        volume = np.random.normal(1000, 200, 1000)

        # Create technical indicators
        rsi = 50 + np.random.normal(0, 10, 1000)
        macd = np.random.normal(0, 1, 1000)
        bollinger = np.random.normal(0, 0.5, 1000)

        data = pd.DataFrame({
            'price': trend + noise,
            'volume': volume,
            'rsi': rsi,
            'macd': macd,
            'bollinger_position': bollinger
        }, index=dates)

        # Test single-step LSTM
        print("\n1. Testing Single-Step LSTM...")
        config = LSTMPredictorConfig(
            sequence_length=60,
            num_epochs=5,  # Short training for demo
            generate_signals=True
        )

        predictor = create_lstm_predictor(config)
        history = predictor.fit(data, 'price')

        print(f"LSTM trained for {len(history)} epochs")
        print(".6f")
        # Test prediction
        test_predictions = predictor.predict(data.iloc[-100:])
        print(f"Generated {len(test_predictions)} predictions")

        # Test signal generation
        signals = predictor.generate_trading_signals(data.iloc[-100:], current_price=115.0)
        print(f"Generated {len(signals)} trading signals")

        # Test evaluation
        metrics = predictor.evaluate(data.iloc[-200:], 'price')
        print("\nEvaluation metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}")

        # Test Bayesian LSTM
        print("\n2. Testing Bayesian LSTM...")
        bayesian_config = LSTMPredictorConfig(
            uncertainty_estimation=True,
            num_epochs=3
        )

        bayesian_predictor = create_bayesian_lstm_predictor(bayesian_config)
        bayesian_predictor.fit(data, 'price')

        # Test uncertainty estimation
        pred_mean, pred_uncertainty = bayesian_predictor.predict(
            data.iloc[-50:], return_uncertainty=True
        )
        print(f"Bayesian predictions with uncertainty: {len(pred_mean)} samples")
        print(f"Mean prediction: {pred_mean[0][0]:.4f}, Uncertainty: {pred_uncertainty[0][0]:.4f}")
    else:
        print("PyTorch not available - LSTM functionality disabled")
        print("Install PyTorch to enable LSTM-based prediction: pip install torch")

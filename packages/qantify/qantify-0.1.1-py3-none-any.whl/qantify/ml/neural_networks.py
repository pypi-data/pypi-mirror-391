"""Advanced neural network architectures and training utilities."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# PyTorch dependencies
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset, TensorDataset, WeightedRandomSampler
    from torch.optim import Adam, SGD, AdamW, RMSprop
    from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, ReduceLROnPlateau
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False
    torch = None
    nn = None
    F = None

try:
    from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
    from sklearn.metrics import accuracy_score, mean_squared_error, log_loss
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
except ImportError:
    pass


@dataclass(slots=True)
class NeuralNetworkConfig:
    """Configuration for neural network architecture."""
    input_dim: int
    output_dim: int
    hidden_dims: List[int] = field(default_factory=lambda: [64, 32])
    activation: str = "relu"
    dropout_rate: float = 0.1
    batch_norm: bool = True
    task_type: str = "regression"  # "regression", "classification", "multiclass"


@dataclass(slots=True)
class TrainingConfig:
    """Configuration for neural network training."""
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "adam"
    loss_function: str = "mse"
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    use_scheduler: bool = True
    scheduler_type: str = "reduce_on_plateau"
    weight_decay: float = 1e-4
    gradient_clip_value: Optional[float] = 1.0


@dataclass(slots=True)
class TrainingResult:
    """Result from neural network training."""
    model: Any
    history: Dict[str, List[float]]
    best_epoch: int
    training_time: float
    final_metrics: Dict[str, float]
    config: NeuralNetworkConfig


class FlexibleNeuralNetwork(nn.Module):
    """Flexible neural network with configurable architecture."""

    def __init__(self, config: NeuralNetworkConfig):
        super().__init__()
        self.config = config

        # Build layers
        layers = []
        prev_dim = config.input_dim

        for i, hidden_dim in enumerate(config.hidden_dims):
            # Linear layer
            layers.append(nn.Linear(prev_dim, hidden_dim))

            # Batch normalization
            if config.batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))

            # Activation
            if config.activation == "relu":
                layers.append(nn.ReLU())
            elif config.activation == "tanh":
                layers.append(nn.Tanh())
            elif config.activation == "sigmoid":
                layers.append(nn.Sigmoid())
            elif config.activation == "leaky_relu":
                layers.append(nn.LeakyReLU(0.1))
            elif config.activation == "elu":
                layers.append(nn.ELU())

            # Dropout
            if config.dropout_rate > 0:
                layers.append(nn.Dropout(config.dropout_rate))

            prev_dim = hidden_dim

        # Output layer
        self.hidden_layers = nn.Sequential(*layers)
        self.output_layer = nn.Linear(prev_dim, config.output_dim)

        # Output activation
        if config.task_type == "classification":
            self.output_activation = nn.Sigmoid()
        elif config.task_type == "multiclass":
            self.output_activation = nn.Softmax(dim=1)
        else:
            self.output_activation = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.hidden_layers(x)
        x = self.output_layer(x)
        if self.output_activation:
            x = self.output_activation(x)
        return x


class AdvancedNeuralTrainer:
    """Advanced neural network trainer with comprehensive features."""

    def __init__(self, device: Optional[str] = None):
        if not HAS_PYTORCH:
            raise ImportError("PyTorch required for neural network training")

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def train(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        network_config: NeuralNetworkConfig,
        training_config: TrainingConfig,
        verbose: bool = True
    ) -> TrainingResult:
        """Train neural network with advanced features."""
        start_time = time.time()

        # Prepare data
        X_tensor, y_tensor = self._prepare_data(X, y, network_config)

        # Create datasets
        dataset = TensorDataset(X_tensor, y_tensor)

        # Train/validation split
        val_size = int(len(dataset) * training_config.validation_split)
        train_size = len(dataset) - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=training_config.batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=training_config.batch_size,
            shuffle=False
        )

        # Create model
        model = FlexibleNeuralNetwork(network_config).to(self.device)

        # Loss function
        criterion = self._get_loss_function(training_config.loss_function, network_config)

        # Optimizer
        optimizer = self._get_optimizer(
            model, training_config.optimizer,
            training_config.learning_rate, training_config.weight_decay
        )

        # Learning rate scheduler
        scheduler = None
        if training_config.use_scheduler:
            scheduler = self._get_scheduler(optimizer, training_config)

        # Training loop
        history = {
            'train_loss': [], 'val_loss': [],
            'train_metric': [], 'val_metric': []
        }

        best_val_loss = float('inf')
        best_model_state = None
        patience_counter = 0
        best_epoch = 0

        for epoch in range(training_config.epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            train_metric = 0.0

            for inputs, targets in train_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()

                # Gradient clipping
                if training_config.gradient_clip_value:
                    torch.nn.utils.clip_grad_norm_(
                        model.parameters(), training_config.gradient_clip_value
                    )

                optimizer.step()

                train_loss += loss.item()

                # Calculate metric
                batch_metric = self._calculate_metric(outputs, targets, network_config)
                train_metric += batch_metric

            train_loss /= len(train_loader)
            train_metric /= len(train_loader)

            # Validation phase
            model.eval()
            val_loss = 0.0
            val_metric = 0.0

            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)
                    val_loss += loss.item()
                    val_metric += self._calculate_metric(outputs, targets, network_config)

            val_loss /= len(val_loader)
            val_metric /= len(val_loader)

            # Update history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_metric'].append(train_metric)
            history['val_metric'].append(val_metric)

            # Learning rate scheduling
            if scheduler:
                if isinstance(scheduler, ReduceLROnPlateau):
                    scheduler.step(val_loss)
                else:
                    scheduler.step()

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = model.state_dict()
                patience_counter = 0
                best_epoch = epoch
            else:
                patience_counter += 1

            if patience_counter >= training_config.early_stopping_patience:
                if verbose:
                    print(f"Early stopping at epoch {epoch}")
                break

            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{training_config.epochs}, "
                      f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        # Load best model
        if best_model_state:
            model.load_state_dict(best_model_state)

        # Calculate final metrics
        final_metrics = self._calculate_final_metrics(model, val_loader, network_config)

        training_time = time.time() - start_time

        return TrainingResult(
            model=model,
            history=history,
            best_epoch=best_epoch,
            training_time=training_time,
            final_metrics=final_metrics,
            config=network_config
        )

    def _prepare_data(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        config: NeuralNetworkConfig
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepare data for training."""
        # Convert to numpy
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        # Convert to tensors
        X_tensor = torch.FloatTensor(X)

        if config.task_type == "regression":
            y_tensor = torch.FloatTensor(y).unsqueeze(1)
        elif config.task_type == "classification":
            y_tensor = torch.FloatTensor(y).unsqueeze(1)
        else:  # multiclass
            y_tensor = torch.LongTensor(y)

        return X_tensor, y_tensor

    def _get_loss_function(self, loss_name: str, config: NeuralNetworkConfig) -> nn.Module:
        """Get appropriate loss function."""
        if loss_name == "mse":
            return nn.MSELoss()
        elif loss_name == "mae":
            return nn.L1Loss()
        elif loss_name == "bce":
            return nn.BCELoss()
        elif loss_name == "cross_entropy":
            return nn.CrossEntropyLoss()
        elif loss_name == "huber":
            return nn.HuberLoss()
        else:
            # Auto-select based on task
            if config.task_type == "regression":
                return nn.MSELoss()
            elif config.task_type == "classification":
                return nn.BCELoss()
            else:
                return nn.CrossEntropyLoss()

    def _get_optimizer(self, model: nn.Module, optimizer_name: str, lr: float, weight_decay: float):
        """Get optimizer."""
        if optimizer_name == "adam":
            return Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == "adamw":
            return AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == "sgd":
            return SGD(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == "rmsprop":
            return RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
        else:
            return Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    def _get_scheduler(self, optimizer, config: TrainingConfig):
        """Get learning rate scheduler."""
        if config.scheduler_type == "step":
            return StepLR(optimizer, step_size=30, gamma=0.1)
        elif config.scheduler_type == "cosine":
            return CosineAnnealingLR(optimizer, T_max=config.epochs)
        elif config.scheduler_type == "reduce_on_plateau":
            return ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
        else:
            return None

    def _calculate_metric(self, outputs: torch.Tensor, targets: torch.Tensor, config: NeuralNetworkConfig) -> float:
        """Calculate training metric."""
        if config.task_type == "regression":
            return F.mse_loss(outputs, targets).item()
        elif config.task_type == "classification":
            preds = (outputs > 0.5).float()
            return (preds == targets).float().mean().item()
        else:  # multiclass
            preds = torch.argmax(outputs, dim=1)
            return (preds == targets).float().mean().item()

    def _calculate_final_metrics(self, model: nn.Module, val_loader: DataLoader, config: NeuralNetworkConfig) -> Dict[str, float]:
        """Calculate final validation metrics."""
        model.eval()
        all_outputs = []
        all_targets = []

        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = model(inputs)
                all_outputs.append(outputs.cpu())
                all_targets.append(targets.cpu())

        all_outputs = torch.cat(all_outputs)
        all_targets = torch.cat(all_targets)

        metrics = {}

        if config.task_type == "regression":
            mse = F.mse_loss(all_outputs, all_targets).item()
            mae = F.l1_loss(all_outputs, all_targets).item()
            metrics.update({"mse": mse, "mae": mae, "rmse": np.sqrt(mse)})
        elif config.task_type == "classification":
            preds = (all_outputs > 0.5).float()
            accuracy = (preds == all_targets).float().mean().item()
            try:
                auc = self._calculate_auc(all_outputs.numpy(), all_targets.numpy())
                metrics.update({"accuracy": accuracy, "auc": auc})
            except:
                metrics.update({"accuracy": accuracy})
        else:  # multiclass
            preds = torch.argmax(all_outputs, dim=1)
            accuracy = (preds == all_targets).float().mean().item()
            metrics.update({"accuracy": accuracy})

        return metrics

    def _calculate_auc(self, y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Calculate AUC for binary classification."""
        try:
            from sklearn.metrics import roc_auc_score
            return roc_auc_score(y_true, y_pred)
        except:
            return 0.0


class SklearnCompatibleNeuralNetwork(BaseEstimator, ClassifierMixin, RegressorMixin):
    """Scikit-learn compatible neural network wrapper."""

    def __init__(
        self,
        hidden_dims: List[int] = None,
        activation: str = "relu",
        dropout_rate: float = 0.1,
        batch_norm: bool = True,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        early_stopping_patience: int = 10,
        random_state: int = 42
    ):
        self.hidden_dims = hidden_dims or [64, 32]
        self.activation = activation
        self.dropout_rate = dropout_rate
        self.batch_norm = batch_norm
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.early_stopping_patience = early_stopping_patience
        self.random_state = random_state

        self.model_ = None
        self.scaler_ = None
        self.label_encoder_ = None
        self.is_fitted_ = False

    def fit(self, X, y):
        """Fit the neural network."""
        if not HAS_PYTORCH:
            raise ImportError("PyTorch required for neural network training")

        # Prepare data
        X = self._validate_input(X)

        # Scale features
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X)

        # Determine task type
        unique_values = len(np.unique(y))
        if isinstance(y, pd.Series) and y.dtype == 'object':
            task_type = "multiclass"
            self.label_encoder_ = LabelEncoder()
            y_encoded = self.label_encoder_.fit_transform(y)
        elif unique_values <= 20:
            task_type = "multiclass"
            y_encoded = y
        else:
            task_type = "regression"
            y_encoded = y

        # Create network config
        network_config = NeuralNetworkConfig(
            input_dim=X.shape[1],
            output_dim=unique_values if task_type == "multiclass" else 1,
            hidden_dims=self.hidden_dims,
            activation=self.activation,
            dropout_rate=self.dropout_rate,
            batch_norm=self.batch_norm,
            task_type=task_type
        )

        # Create training config
        training_config = TrainingConfig(
            epochs=self.epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            early_stopping_patience=self.early_stopping_patience
        )

        # Train model
        trainer = AdvancedNeuralTrainer()
        result = trainer.train(X_scaled, y_encoded, network_config, training_config, verbose=False)

        self.model_ = result.model
        self.is_fitted_ = True

        return self

    def predict(self, X):
        """Make predictions."""
        if not self.is_fitted_:
            raise RuntimeError("Model must be fitted before prediction")

        X = self._validate_input(X)
        X_scaled = self.scaler_.transform(X)

        self.model_.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_scaled)
            outputs = self.model_(X_tensor)

            if self._is_multiclass():
                preds = torch.argmax(outputs, dim=1).numpy()
                if self.label_encoder_:
                    preds = self.label_encoder_.inverse_transform(preds)
                return preds
            else:
                return outputs.numpy().flatten()

    def predict_proba(self, X):
        """Predict class probabilities."""
        if not self.is_fitted_:
            raise RuntimeError("Model must be fitted before prediction")

        if self._is_multiclass():
            X = self._validate_input(X)
            X_scaled = self.scaler_.transform(X)

            self.model_.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X_scaled)
                outputs = self.model_(X_tensor)
                return torch.softmax(outputs, dim=1).numpy()
        else:
            raise AttributeError("predict_proba only available for classification tasks")

    def _validate_input(self, X):
        """Validate input data."""
        if isinstance(X, pd.DataFrame):
            return X.values
        return np.asarray(X)

    def _is_multiclass(self):
        """Check if this is a multiclass problem."""
        return hasattr(self.model_.config, 'task_type') and self.model_.config.task_type == "multiclass"


class AutoEncoder(nn.Module):
    """Autoencoder for dimensionality reduction and feature learning."""

    def __init__(self, input_dim: int, encoding_dim: int, hidden_dims: List[int] = None):
        super().__init__()
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

    def encode(self, x):
        """Get encoded representation."""
        return self.encoder(x)

    def decode(self, x):
        """Decode from encoded representation."""
        return self.decoder(x)


class VariationalAutoEncoder(nn.Module):
    """Variational Autoencoder for generative modeling."""

    def __init__(self, input_dim: int, latent_dim: int, hidden_dims: List[int] = None):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

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

        self.encoder = nn.Sequential(*encoder_layers)
        self.fc_mu = nn.Linear(prev_dim, latent_dim)
        self.fc_var = nn.Linear(prev_dim, latent_dim)

        # Decoder
        decoder_layers = []
        prev_dim = latent_dim

        if hidden_dims:
            for hidden_dim in reversed(hidden_dims):
                decoder_layers.extend([
                    nn.Linear(prev_dim, hidden_dim),
                    nn.ReLU()
                ])
                prev_dim = hidden_dim

        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        decoder_layers.append(nn.Sigmoid())  # Assuming normalized input
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_var(h)

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        return self.decode(z), mu, log_var

    def loss_function(self, recon_x, x, mu, log_var):
        """VAE loss: reconstruction + KL divergence."""
        BCE = F.binary_cross_entropy(recon_x, x, reduction='sum')
        KLD = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        return BCE + KLD


__all__ = [
    "NeuralNetworkConfig",
    "TrainingConfig",
    "TrainingResult",
    "FlexibleNeuralNetwork",
    "AdvancedNeuralTrainer",
    "SklearnCompatibleNeuralNetwork",
    "AutoEncoder",
    "VariationalAutoEncoder",
]

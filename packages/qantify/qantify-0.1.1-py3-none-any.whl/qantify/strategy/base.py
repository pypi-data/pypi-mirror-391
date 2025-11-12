"""Advanced ML-Enhanced Strategy Framework with AutoML, Multi-Agent Systems, and Production Capabilities."""

from __future__ import annotations

import asyncio
import warnings
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from os import PathLike
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import uuid
import json
import hashlib
import inspect
from functools import partial, wraps
import time
import logging as python_logging

import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# Optional ML library imports
try:
    import xgboost as xgb
except ImportError:
    xgb = None

try:
    import lightgbm as lgb
except ImportError:
    lgb = None
from scipy.optimize import minimize_scalar
from scipy.stats import norm, t

# Optional PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
except ImportError:
    torch = None
    nn = None
    optim = None
    Dataset = None
    DataLoader = None

from qantify.backtest.errors import ExecutionError
from qantify.backtest.types import Order, OrderSide, TimeInForce
from qantify.math.volatility import realized_volatility, parkinson_volatility

# Import stat_arb if available
try:
    from qantify.math.stat_arb import cointegration_test, johansen_test
except ImportError:
    cointegration_test = None
    johansen_test = None

from .logging import logs_to_dataframe, write_csv, write_jsonl, write_parquet
from .monitor import InMemoryMonitor, NullMonitor, StrategyMonitor
from .persistence import StateSnapshot, StateStore
from .dsl import Rule
from .parameters import Parameter, ParameterSpace, collect_parameters

IndicatorInput = Union[pd.Series, pd.DataFrame, Sequence[float], np.ndarray]


# Utility functions for technical indicators
def simple_moving_average(data: pd.Series, period: int) -> pd.Series:
    """Calculate simple moving average."""
    return data.rolling(window=period).mean()


def exponential_moving_average(data: pd.Series, period: int) -> pd.Series:
    """Calculate exponential moving average."""
    return data.ewm(span=period).mean()


# =============================================================================
# ADVANCED ML-ENHANCED STRATEGY FRAMEWORK
# =============================================================================

class StrategyExecutionMode:
    """Execution modes for strategies."""
    BACKTEST = "backtest"
    LIVE = "live"
    PAPER = "paper"
    SIMULATION = "simulation"


class StrategyPerformanceMetrics:
    """Comprehensive performance metrics for strategies."""

    def __init__(self):
        self.sharpe_ratio = 0.0
        self.sortino_ratio = 0.0
        self.calmar_ratio = 0.0
        self.max_drawdown = 0.0
        self.win_rate = 0.0
        self.profit_factor = 0.0
        self.avg_win = 0.0
        self.avg_loss = 0.0
        self.total_trades = 0
        self.total_return = 0.0
        self.annual_return = 0.0
        self.volatility = 0.0
        self.alpha = 0.0
        self.beta = 0.0
        self.information_ratio = 0.0
        self.kelly_criterion = 0.0
        self.optimal_f = 0.0
        self.recovery_factor = 0.0
        self.payoff_ratio = 0.0
        self.r_squared = 0.0
        self.adjusted_r_squared = 0.0

    def calculate_from_trades(self, trades: List[Dict], benchmark_returns: Optional[pd.Series] = None):
        """Calculate all metrics from trade data."""
        if not trades:
            return

        # Basic trade metrics
        profits = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        losses = [abs(t.get('pnl', 0)) for t in trades if t.get('pnl', 0) < 0]

        self.total_trades = len(trades)
        self.win_rate = len(profits) / self.total_trades if self.total_trades > 0 else 0
        self.avg_win = np.mean(profits) if profits else 0
        self.avg_loss = np.mean(losses) if losses else 0
        self.profit_factor = (sum(profits) / sum(losses)) if losses and sum(losses) > 0 else float('inf')

        # Kelly Criterion
        if self.win_rate > 0 and self.avg_loss > 0:
            win_prob = self.win_rate
            loss_prob = 1 - win_prob
            avg_win = self.avg_win
            avg_loss = self.avg_loss
            kelly = (win_prob / avg_loss) - (loss_prob / avg_win) if avg_win > 0 else 0
            self.kelly_criterion = max(0, kelly)
            self.optimal_f = min(0.5, self.kelly_criterion * 0.5)  # Fractional Kelly

    def calculate_from_returns(self, returns: pd.Series, risk_free_rate: float = 0.02):
        """Calculate risk-adjusted metrics from return series."""
        if returns.empty:
            return

        # Basic statistics
        ann_return = returns.mean() * 252
        ann_vol = returns.std() * np.sqrt(252)
        excess_returns = returns - risk_free_rate/252

        # Risk-adjusted ratios
        self.sharpe_ratio = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0
        downside_returns = returns[returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(252) if not downside_returns.empty else 0
        self.sortino_ratio = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else 0

        # Drawdown analysis
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        self.max_drawdown = abs(drawdown.min())

        self.calmar_ratio = ann_return / abs(self.max_drawdown) if self.max_drawdown != 0 else 0
        self.recovery_factor = ann_return / abs(self.max_drawdown) if self.max_drawdown != 0 else 0

        # Additional metrics
        self.total_return = (cumulative.iloc[-1] - 1) * 100
        self.annual_return = ann_return * 100
        self.volatility = ann_vol * 100


@runtime_checkable
class MLModelProtocol(Protocol):
    """Protocol for ML models used in strategies."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        ...


class FeatureEngineer:
    """Advanced feature engineering for ML-enhanced strategies."""

    def __init__(self):
        self.feature_functions = {}
        self._register_default_features()

    def _register_default_features(self):
        """Register default feature engineering functions."""
        self.register_feature('sma', self._sma_features)
        self.register_feature('ema', self._ema_features)
        self.register_feature('rsi', self._rsi_features)
        self.register_feature('macd', self._macd_features)
        self.register_feature('bollinger', self._bollinger_features)
        self.register_feature('volume', self._volume_features)
        self.register_feature('momentum', self._momentum_features)
        self.register_feature('volatility', self._volatility_features)
        self.register_feature('trend', self._trend_features)

    def register_feature(self, name: str, func: Callable):
        """Register a custom feature engineering function."""
        self.feature_functions[name] = func

    def create_features(self, data: pd.DataFrame, feature_config: Dict[str, Any]) -> pd.DataFrame:
        """Create features from market data."""
        features = pd.DataFrame(index=data.index)

        for feature_name, config in feature_config.items():
            if feature_name in self.feature_functions:
                try:
                    feature_data = self.feature_functions[feature_name](data, **config)
                    if isinstance(feature_data, pd.DataFrame):
                        features = pd.concat([features, feature_data], axis=1)
                    elif isinstance(feature_data, pd.Series):
                        features[feature_name] = feature_data
                except Exception as e:
                    warnings.warn(f"Failed to create feature {feature_name}: {e}")

        return features.dropna()

    def _sma_features(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """Simple moving average features."""
        if periods is None:
            periods = [5, 10, 20, 50]

        features = pd.DataFrame(index=data.index)
        for period in periods:
            features[f'sma_{period}'] = simple_moving_average(data['close'], period)

        return features

    def _ema_features(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """Exponential moving average features."""
        if periods is None:
            periods = [5, 10, 20, 50]

        features = pd.DataFrame(index=data.index)
        for period in periods:
            features[f'ema_{period}'] = exponential_moving_average(data['close'], period)

        return features

    def _rsi_features(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """RSI features."""
        if periods is None:
            periods = [14, 21]

        features = pd.DataFrame(index=data.index)
        for period in periods:
            features[f'rsi_{period}'] = self._calculate_rsi(data['close'], period)

        return features

    def _macd_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """MACD features."""
        features = pd.DataFrame(index=data.index)

        ema12 = exponential_moving_average(data['close'], 12)
        ema26 = exponential_moving_average(data['close'], 26)
        macd = ema12 - ema26
        signal = exponential_moving_average(macd, 9)

        features['macd'] = macd
        features['macd_signal'] = signal
        features['macd_histogram'] = macd - signal

        return features

    def _bollinger_features(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Bollinger Band features."""
        features = pd.DataFrame(index=data.index)

        sma = simple_moving_average(data['close'], period)
        std = data['close'].rolling(period).std()

        features['bb_upper'] = sma + 2 * std
        features['bb_lower'] = sma - 2 * std
        features['bb_middle'] = sma
        features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / features['bb_middle']
        features['bb_position'] = (data['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])

        return features

    def _volume_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Volume-based features."""
        features = pd.DataFrame(index=data.index)

        if 'volume' not in data.columns:
            return features

        features['volume_sma_20'] = simple_moving_average(data['volume'], 20)
        features['volume_ratio'] = data['volume'] / features['volume_sma_20']
        features['volume_price_trend'] = data['volume'] * (data['close'].pct_change() > 0).astype(int)

        return features

    def _momentum_features(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """Momentum features."""
        if periods is None:
            periods = [1, 5, 10, 20]

        features = pd.DataFrame(index=data.index)
        for period in periods:
            features[f'momentum_{period}'] = data['close'] / data['close'].shift(period) - 1

        return features

    def _volatility_features(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """Volatility features."""
        if periods is None:
            periods = [5, 10, 20, 30]

        features = pd.DataFrame(index=data.index)
        returns = data['close'].pct_change()

        for period in periods:
            features[f'volatility_{period}'] = returns.rolling(period).std()
            # Realized volatility calculation
            if 'high' in data.columns and 'low' in data.columns and 'close' in data.columns:
                try:
                    high_arr = data['high'].values
                    low_arr = data['low'].values
                    close_arr = data['close'].values
                    realized_vol = realized_volatility(high_arr, low_arr, close_arr, window=period)
                    features[f'realized_vol_{period}'] = pd.Series(realized_vol, index=data.index)
                except Exception:
                    features[f'realized_vol_{period}'] = returns.rolling(period).std()  # Fallback
            else:
                features[f'realized_vol_{period}'] = returns.rolling(period).std()  # Fallback

        return features

    def _trend_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Trend analysis features."""
        features = pd.DataFrame(index=data.index)

        # Linear regression slope
        def linreg_slope(series, window):
            slopes = []
            for i in range(len(series)):
                if i < window - 1:
                    slopes.append(0)
                else:
                    y = series.iloc[i-window+1:i+1].values
                    x = np.arange(window)
                    slope = np.polyfit(x, y, 1)[0]
                    slopes.append(slope)
            return pd.Series(slopes, index=series.index)

        features['trend_slope_20'] = linreg_slope(data['close'], 20)
        features['trend_slope_50'] = linreg_slope(data['close'], 50)

        # Trend strength
        features['trend_strength'] = abs(features['trend_slope_20']) / data['close'].rolling(20).std()

        return features

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))


class AutoMLTrainer:
    """Automated Machine Learning trainer for strategy signals."""

    def __init__(self, models: Optional[List[str]] = None, cv_folds: int = 5):
        self.models = models or ['rf', 'gb', 'xgb', 'lgb', 'mlp']
        self.cv_folds = cv_folds
        self.best_model = None
        self.best_score = 0.0
        self.feature_importance = {}
        self.model_configs = self._get_default_configs()

    def _get_default_configs(self) -> Dict[str, Dict]:
        """Get default model configurations."""
        return {
            'rf': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42),
                'params': {'n_estimators': [50, 100, 200], 'max_depth': [5, 10, None]}
            },
            'gb': {
                'model': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'params': {'n_estimators': [50, 100], 'learning_rate': [0.01, 0.1, 0.2]}
            },
            'xgb': {
                'model': xgb.XGBClassifier(objective='binary:logistic', random_state=42) if xgb else None,
                'params': {'n_estimators': [50, 100], 'learning_rate': [0.01, 0.1], 'max_depth': [3, 6]}
            } if xgb else None,
            'lgb': {
                'model': lgb.LGBMClassifier(objective='binary', random_state=42) if lgb else None,
                'params': {'n_estimators': [50, 100], 'learning_rate': [0.01, 0.1], 'num_leaves': [31, 63]}
            } if lgb else None,
            'mlp': {
                'model': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42),
                'params': {'hidden_layer_sizes': [(32,), (64, 32), (128, 64, 32)]}
            }
        }

    def train(self, X: pd.DataFrame, y: pd.Series, optimize: bool = True) -> MLModelProtocol:
        """Train the best model using AutoML."""
        print(f"Training AutoML on {len(X)} samples with {len(X.columns)} features...")

        # Feature selection
        selector = SelectKBest(score_func=f_classif, k=min(50, len(X.columns)))
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()].tolist()

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_selected)

        best_model = None
        best_score = 0.0

        # Train and evaluate each model
        for model_name in self.models:
            if model_name not in self.model_configs or self.model_configs[model_name] is None:
                continue

            config = self.model_configs[model_name]
            model = config['model']

            try:
                # Cross-validation scoring
                cv_scores = cross_val_score(
                    model, X_scaled, y,
                    cv=TimeSeriesSplit(n_splits=min(self.cv_folds, len(y)-1)),
                    scoring='f1'
                )

                mean_score = np.mean(cv_scores)
                std_score = np.std(cv_scores)

                print(".3f")
                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    self.feature_importance = dict(zip(selected_features,
                                                      selector.scores_[selector.get_support()]))

                # Hyperparameter optimization if requested
                if optimize:
                    best_model = self._optimize_hyperparameters(
                        model, config['params'], X_scaled, y
                    )
            except Exception as e:
                print(f"Failed to train {model_name}: {e}")
                continue

        if best_model is None:
            raise ValueError("No models could be trained successfully")

        # Final training on full dataset
        best_model.fit(X_scaled, y)
        self.best_model = best_model
        self.best_score = best_score

        print(f"Best model: {type(best_model).__name__} with score {best_score:.3f}")
        return Pipeline([
            ('selector', selector),
            ('scaler', scaler),
            ('classifier', best_model)
        ])

    def _optimize_hyperparameters(self, model, param_grid: Dict, X: np.ndarray, y: np.ndarray):
        """Simple hyperparameter optimization."""
        best_score = 0
        best_params = {}

        # Grid search (simplified)
        from sklearn.model_selection import ParameterGrid
        for params in ParameterGrid(param_grid):
            try:
                model_copy = model.__class__(**{**model.get_params(), **params})
                scores = cross_val_score(model_copy, X, y, cv=3, scoring='f1')
                mean_score = np.mean(scores)

                if mean_score > best_score:
                    best_score = mean_score
                    best_params = params
            except:
                continue

        return model.__class__(**{**model.get_params(), **best_params})

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with the best model."""
        if self.best_model is None:
            raise ValueError("No trained model available")
        return self.best_model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities."""
        if self.best_model is None:
            raise ValueError("No trained model available")
        return self.best_model.predict_proba(X)


class NeuralSignalPredictor:
    """Neural network for signal prediction."""

    def __init__(self, input_dim: int, hidden_dims: List[int] = None, dropout: float = 0.2):
        if nn is None:
            raise RuntimeError("PyTorch is required for NeuralSignalPredictor")

        self.model = nn.Module()

        if hidden_dims is None:
            hidden_dims = [128, 64, 32]

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 2))  # Binary classification
        self.model.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.model.network(x)


class DeepLearningTrainer:
    """Deep learning trainer for advanced signal prediction."""

    def __init__(self, input_dim: int, epochs: int = 100, batch_size: int = 64, learning_rate: float = 0.001):
        if torch is None or nn is None or optim is None or Dataset is None or DataLoader is None:
            raise RuntimeError("PyTorch is required for DeepLearningTrainer")

        self.input_dim = input_dim
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.model = None
        self.scaler = StandardScaler()

    def train(self, X: pd.DataFrame, y: pd.Series, validation_split: float = 0.2) -> NeuralSignalPredictor:
        """Train the neural network."""
        print(f"Training neural network on {len(X)} samples...")

        # Prepare data
        X_scaled = self.scaler.fit_transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.LongTensor(y.values)

        # Create datasets
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        val_size = int(len(dataset) * validation_split)
        train_size = len(dataset) - val_size

        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size)

        # Initialize model
        self.model = NeuralSignalPredictor(self.input_dim)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # Training loop
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0

        for epoch in range(self.epochs):
            # Training
            self.model.train()
            train_loss = 0.0

            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Validation
            self.model.eval()
            val_loss = 0.0
            correct = 0
            total = 0

            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()

            val_accuracy = correct / total

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{self.epochs}, Train Loss: {train_loss/len(train_loader):.4f}, "
                      f"Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_accuracy:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

        return self.model

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("No trained model available")

        self.model.eval()
        X_scaled = self.scaler.transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            _, predicted = torch.max(outputs, 1)

        return predicted.numpy()

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities."""
        if self.model is None:
            raise ValueError("No trained model available")

        self.model.eval()
        X_scaled = self.scaler.transform(X.values)
        X_tensor = torch.FloatTensor(X_scaled)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            probabilities = torch.softmax(outputs, dim=1)

        return probabilities.numpy()


class StrategyEnsemble:
    """Ensemble of multiple strategies for improved performance."""

    def __init__(self, strategies: List['MLStrategy'], weights: Optional[List[float]] = None):
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)
        self.normalize_weights()

    def normalize_weights(self):
        """Normalize weights to sum to 1."""
        total = sum(self.weights)
        self.weights = [w / total for w in self.weights]

    def get_signal(self, data: pd.DataFrame) -> float:
        """Get ensemble signal."""
        signals = []
        for strategy in self.strategies:
            try:
                signal = strategy.predict_signal(data)
                signals.append(signal)
            except Exception as e:
                warnings.warn(f"Strategy failed: {e}")
                signals.append(0.0)

        # Weighted average
        return sum(s * w for s, w in zip(signals, self.weights))

    def update_weights(self, performance_data: pd.DataFrame):
        """Update ensemble weights based on recent performance."""
        # Simple performance-based weighting
        recent_returns = performance_data.tail(30)['returns']

        for i, strategy in enumerate(self.strategies):
            try:
                strategy_returns = performance_data.tail(30)[f'strategy_{i}_returns']
                correlation = strategy_returns.corr(recent_returns)
                # Adjust weight based on correlation with overall performance
                self.weights[i] *= (1 + correlation * 0.1)
            except:
                pass

        self.normalize_weights()


class MultiAgentStrategySystem:
    """Multi-agent strategy system with communication and coordination."""

    def __init__(self, agents: List['MLStrategy']):
        self.agents = agents
        self.communication_network = {}
        self.agent_states = {}
        self.coordination_protocol = "consensus"

    def initialize_agents(self, initial_data: pd.DataFrame):
        """Initialize all agents with data."""
        for i, agent in enumerate(self.agents):
            agent.initialize(initial_data)
            self.agent_states[i] = {
                'confidence': 0.5,
                'last_signal': 0.0,
                'performance': 0.0
            }

    def coordinate_signals(self, data: pd.DataFrame) -> float:
        """Coordinate signals from multiple agents."""
        agent_signals = []
        agent_confidences = []

        for i, agent in enumerate(self.agents):
            try:
                signal = agent.predict_signal(data)
                confidence = self.agent_states[i]['confidence']
                agent_signals.append(signal * confidence)
                agent_confidences.append(confidence)
            except Exception as e:
                warnings.warn(f"Agent {i} failed: {e}")
                agent_signals.append(0.0)
                agent_confidences.append(0.0)

        # Consensus-based coordination
        if self.coordination_protocol == "consensus":
            total_confidence = sum(agent_confidences)
            if total_confidence > 0:
                return sum(s * c for s, c in zip(agent_signals, agent_confidences)) / total_confidence
            else:
                return np.mean(agent_signals)

        elif self.coordination_protocol == "majority_vote":
            binary_signals = [1 if s > 0 else -1 for s in agent_signals]
            return np.sign(sum(binary_signals))

        else:
            return np.mean(agent_signals)

    def update_agent_states(self, actual_return: float):
        """Update agent states based on performance."""
        for i, agent in enumerate(self.agents):
            predicted_signal = self.agent_states[i]['last_signal']
            # Simple reinforcement learning update
            reward = predicted_signal * actual_return
            self.agent_states[i]['performance'] = 0.9 * self.agent_states[i]['performance'] + 0.1 * reward

            # Update confidence based on recent performance
            self.agent_states[i]['confidence'] = min(1.0, max(0.1, self.agent_states[i]['confidence'] + reward * 0.01))


class AdaptiveStrategyManager:
    """Adaptive strategy manager with online learning."""

    def __init__(self, base_strategy: 'MLStrategy', adaptation_rate: float = 0.01):
        self.base_strategy = base_strategy
        self.adaptation_rate = adaptation_rate
        self.performance_history = []
        self.market_regime = "normal"
        self.regime_detector = self._initialize_regime_detector()

    def _initialize_regime_detector(self):
        """Initialize market regime detection."""
        # Simple regime detection based on volatility and trend
        return {
            'volatility_threshold': 0.02,
            'trend_threshold': 0.001
        }

    def detect_market_regime(self, data: pd.DataFrame) -> str:
        """Detect current market regime."""
        recent_data = data.tail(20)

        # Calculate volatility
        returns = recent_data['close'].pct_change().dropna()
        volatility = returns.std()

        # Calculate trend
        trend = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]

        if volatility > self.regime_detector['volatility_threshold'] * 2:
            return "high_volatility"
        elif abs(trend) > self.regime_detector['trend_threshold'] * 2:
            return "trending"
        else:
            return "normal"

    def adapt_strategy(self, data: pd.DataFrame, current_performance: float):
        """Adapt strategy parameters based on market conditions and performance."""
        self.market_regime = self.detect_market_regime(data)
        self.performance_history.append(current_performance)

        # Adapt based on regime
        if self.market_regime == "high_volatility":
            # Reduce position sizes, increase stop losses
            self.base_strategy.risk_multiplier *= (1 - self.adaptation_rate)
            self.base_strategy.stop_loss_multiplier *= (1 + self.adaptation_rate)

        elif self.market_regime == "trending":
            # Increase trend-following parameters
            self.base_strategy.trend_weight *= (1 + self.adaptation_rate)

        # Performance-based adaptation
        recent_performance = np.mean(self.performance_history[-10:])
        if recent_performance < -0.02:  # Poor performance
            self.base_strategy.conservatism *= (1 + self.adaptation_rate)
        elif recent_performance > 0.02:  # Good performance
            self.base_strategy.conservatism *= (1 - self.adaptation_rate)


@dataclass(slots=True)
class IndicatorSeries:
    """Wrapper around ``pd.Series`` providing convenience helpers."""

    series: pd.Series
    strategy: "Strategy"
    symbol: Optional[str] = None

    @property
    def current(self) -> float:
        idx = self.strategy.index
        if idx < 0:
            return float("nan")
        return float(self.series.iloc[idx])

    @property
    def prev(self) -> float:
        return self.shift(1)

    def shift(self, periods: int) -> float:
        idx = self.strategy.index - periods
        if idx < 0:
            return float("nan")
        return float(self.series.iloc[idx])

    def value(self, offset: int = 0) -> float:
        idx = self.strategy.index - offset
        if idx < 0:
            return float("nan")
        return float(self.series.iloc[idx])

    def rolling_max(self, window: int) -> float:
        idx = self.strategy.index
        if idx < 0:
            return float("nan")
        rolled = self.series.rolling(window=window, min_periods=1).max()
        return float(rolled.iloc[idx])

    def rolling_min(self, window: int) -> float:
        idx = self.strategy.index
        if idx < 0:
            return float("nan")
        rolled = self.series.rolling(window=window, min_periods=1).min()
        return float(rolled.iloc[idx])

    def rolling_mean(self, window: int) -> float:
        idx = self.strategy.index
        if idx < 0:
            return float("nan")
        rolled = self.series.rolling(window=window, min_periods=1).mean()
        return float(rolled.iloc[idx])

    def percentile(self, window: int, q: float) -> float:
        if not 0 <= q <= 1:
            raise ValueError("Percentile q must be between 0 and 1.")
        idx = self.strategy.index
        if idx < 0:
            return float("nan")
        rolled = self.series.rolling(window=window, min_periods=1).quantile(q)
        return float(rolled.iloc[idx])

    def log(self, message: str, **fields: Any) -> None:
        self.strategy.log(message, indicator=self.series.name, symbol=self.symbol, **fields)

    def cross_above(self, other: Union["IndicatorSeries", pd.Series, float, int]) -> bool:
        return _cross(self, other, direction="above")

    def cross_below(self, other: Union["IndicatorSeries", pd.Series, float, int]) -> bool:
        return _cross(self, other, direction="below")

    def above(self, other: Union["IndicatorSeries", pd.Series, float, int]) -> bool:
        return _compare(self, other, op="gt")

    def below(self, other: Union["IndicatorSeries", pd.Series, float, int]) -> bool:
        return _compare(self, other, op="lt")

    def to_series(self) -> pd.Series:
        return self.series


@dataclass(slots=True)
class IndicatorFrame:
    frame: pd.DataFrame
    strategy: "Strategy"
    symbol: Optional[str] = None

    def __getattr__(self, item: str) -> IndicatorSeries:
        if item in self.frame.columns:
            return IndicatorSeries(self.frame[item], self.strategy, symbol=self.symbol)
        raise AttributeError(item)

    def __getitem__(self, item: str) -> IndicatorSeries:
        return self.__getattr__(item)

    def to_frame(self) -> pd.DataFrame:
        return self.frame


@dataclass(slots=True)
class ScheduledEvent:
    name: str
    callback: Callable[["Strategy", Any], None]
    frequency: Optional[pd.DateOffset]
    next_run: Optional[pd.Timestamp]
    once: bool
    symbol: Optional[str]
    run_immediately: bool
    kwargs: Dict[str, Any] = field(default_factory=dict)


def _resolve_indicator_output(data: IndicatorInput, index: pd.Index) -> IndicatorInput:
    if isinstance(data, pd.Series):
        return data.reindex(index)
    if isinstance(data, pd.DataFrame):
        return data.reindex(index)
    array = np.asarray(data)
    if len(array) != len(index):
        raise ValueError("Indicator output length does not match data index length.")
    return pd.Series(array, index=index)


def _value_at(source: Union[IndicatorSeries, pd.Series, float, int], idx: int) -> float:
    if isinstance(source, IndicatorSeries):
        series = source.series
        if idx < 0:
            return float("nan")
        return float(series.iloc[idx])
    if isinstance(source, pd.Series):
        if idx < 0 or idx >= len(source):
            return float("nan")
        return float(source.iloc[idx])
    return float(source)


def _cross(base: IndicatorSeries, other: Union[IndicatorSeries, pd.Series, float, int], *, direction: str) -> bool:
    idx = base.strategy.index
    if idx <= 0:
        return False

    curr_self = base.value(0)
    prev_self = base.value(1)
    curr_other = _value_at(other, idx)
    prev_other = _value_at(other, idx - 1)

    if any(np.isnan(val) for val in (curr_self, prev_self, curr_other, prev_other)):
        return False

    if direction == "above":
        return prev_self <= prev_other and curr_self > curr_other
    return prev_self >= prev_other and curr_self < curr_other


def _compare(base: IndicatorSeries, other: Union[IndicatorSeries, pd.Series, float, int], *, op: str) -> bool:
    idx = base.strategy.index
    if idx < 0:
        return False

    left = base.value(0)
    right = _value_at(other, idx)

    if np.isnan(left) or np.isnan(right):
        return False

    if op == "gt":
        return left > right
    if op == "lt":
        return left < right
    raise ValueError(f"Unsupported comparison op '{op}'.")


class Strategy:
    """Base class for event-driven strategies with advanced utilities."""

    def __init__(self, **params: Any) -> None:
        strategy_id = params.pop("strategy_id", None)
        state_store = params.pop("state_store", None)
        monitor = params.pop("monitor", None)
        self.data: Optional[pd.DataFrame] = None
        self.symbol: Optional[str] = None
        self.price_column: str = "close"
        self.broker: Any = None
        self.portfolio: Any = None
        self._data_sources: Dict[str, pd.DataFrame] = {}
        self._indicator_cache: Dict[Tuple[str, Tuple[Any, ...], Tuple[Tuple[str, Any], ...]], Union[IndicatorSeries, IndicatorFrame]] = {}
        self._indicator_cache_meta: Dict[str, Any] = {}
        self._schedule: List[ScheduledEvent] = []
        self._schedule_index: Dict[str, ScheduledEvent] = {}
        self._journal: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}
        self._context: Any = None
        self._current_index: int = -1
        self._current_timestamp: Optional[pd.Timestamp] = None
        self._current_row: Optional[pd.Series] = None
        self._initialized: bool = False
        self.strategy_id = strategy_id
        self.state_store: Optional[StateStore] = state_store
        self.monitor: StrategyMonitor = monitor or NullMonitor()
        self._state_loaded = False
        self._rules: List[Rule] = []
        self._parameters_meta: Dict[str, Parameter] = collect_parameters(self.__class__)
        self._parameters: Dict[str, Any] = {name: meta.default for name, meta in self._parameters_meta.items()}
        if params:
            self.configure(**params)

    # ------------------------------------------------------------------
    # Parameter management
    # ------------------------------------------------------------------
    @classmethod
    def parameter_space(cls) -> ParameterSpace:
        return ParameterSpace(collect_parameters(cls))

    @property
    def parameters(self) -> Dict[str, Any]:
        return dict(self._parameters)

    def configure(self, **params: Any) -> None:
        for name, value in params.items():
            if name not in self._parameters_meta:
                raise KeyError(f"Unknown parameter '{name}'.")
            self._parameters[name] = value

    def get_parameter(self, name: str, default: Any = None) -> Any:
        if name in self._parameters:
            return self._parameters[name]
        if default is not None:
            return default
        raise KeyError(name)

    def clone(self, **override: Any) -> "Strategy":
        config = self.parameters
        config.update(override)
        return self.__class__(**config)

    @classmethod
    def register(cls, name: str | None = None, overwrite: bool = False) -> None:
        from .registry import register_strategy

        register_strategy(cls, name=name, overwrite=overwrite)

    # ------------------------------------------------------------------
    # Binding & lifecycle
    # ------------------------------------------------------------------
    def _bind(
        self,
        *,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        symbol: str,
        broker: Any,
        portfolio: Any,
        price_column: str = "close",
    ) -> None:
        self.price_column = price_column
        self.broker = broker
        self.portfolio = portfolio

        if isinstance(data, dict):
            self._data_sources = {sym: df for sym, df in data.items()}
            self.symbol = symbol if symbol in data else next(iter(data))
            self.data = self._data_sources[self.symbol]
        else:
            self._data_sources = {symbol: data}
            self.symbol = symbol
            self.data = data
        self.symbols = tuple(self._data_sources.keys())
        self._load_persistent_state()

    def on_start(self, context: Any) -> None:
        self._update_context(context)
        self.before_start(context)
        self.init()
        self._initialized = True
        self.after_start(context)
        self.persist_state()

    def on_bar(self, context: Any) -> None:
        self._ensure_initialized()
        self._update_context(context)
        self.before_bar(context)
        self._run_scheduled(context)
        self.next()
        self._execute_rules()
        self.after_bar(context)
        self.persist_state()

    def on_finish(self, context: Any) -> None:
        self._ensure_initialized()
        self._update_context(context)
        self.before_finish(context)
        self.finish()
        self.after_finish(context)
        self.persist_state()

    def before_start(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def after_start(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def before_bar(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def after_bar(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def before_finish(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def after_finish(self, context: Any) -> None:  # pragma: no cover - hook
        pass

    def init(self) -> None:  # pragma: no cover - to be overridden
        """Hook for pre-run initialization."""

    def next(self) -> None:  # pragma: no cover - to be overridden
        """Hook invoked for every bar."""

    def finish(self) -> None:  # pragma: no cover - to be overridden
        """Hook executed after the backtest completes."""

    def on_fill(self, fill: Any) -> None:  # pragma: no cover - optional
        self.log("order_filled", category="fill", order_id=getattr(fill.order, "id", None), price=fill.price, quantity=fill.quantity)

    def on_cancel(self, order: Order) -> None:  # pragma: no cover - optional
        self.log("order_cancelled", category="cancel", order_id=order.id)

    # ------------------------------------------------------------------
    # Scheduling utilities
    # ------------------------------------------------------------------
    def schedule_every(
        self,
        frequency: Union[str, pd.DateOffset],
        callback: Callable[["Strategy", Any], None],
        *,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        run_immediately: bool = False,
        **kwargs: Any,
    ) -> str:
        offset = to_offset(frequency)
        event_name = name or callback.__name__
        event = ScheduledEvent(
            name=event_name,
            callback=callback,
            frequency=offset,
            next_run=None,
            once=False,
            symbol=symbol,
            run_immediately=run_immediately,
            kwargs=dict(kwargs),
        )
        self._register_event(event)
        return event.name

    def schedule_once(
        self,
        when: Union[str, pd.Timestamp],
        callback: Callable[["Strategy", Any], None],
        *,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        timestamp = pd.Timestamp(when)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        else:
            timestamp = timestamp.tz_convert("UTC")
        event_name = name or callback.__name__
        event = ScheduledEvent(
            name=event_name,
            callback=callback,
            frequency=None,
            next_run=timestamp,
            once=True,
            symbol=symbol,
            run_immediately=False,
            kwargs=dict(kwargs),
        )
        self._register_event(event)
        return event.name

    def unschedule(self, name: str) -> bool:
        event = self._schedule_index.pop(name, None)
        if not event:
            return False
        self._schedule = [evt for evt in self._schedule if evt.name != name]
        return True

    def scheduled_events(self) -> List[ScheduledEvent]:
        return list(self._schedule)

    def _register_event(self, event: ScheduledEvent) -> None:
        if event.name in self._schedule_index:
            raise ValueError(f"Scheduled event '{event.name}' already exists.")
        if self.now is not None and event.next_run is None:
            event.next_run = self.now if event.run_immediately else event.frequency.rollforward(self.now) if event.frequency else self.now
        self._schedule.append(event)
        self._schedule_index[event.name] = event

    def _run_scheduled(self, context: Any) -> None:
        if not self._schedule:
            return
        now = context.timestamp
        for event in list(self._schedule):
            if event.next_run is None:
                event.next_run = now if event.run_immediately else (now if event.frequency is None else event.frequency.rollforward(now))
            if now < event.next_run:
                continue
            event.callback(self, context, **event.kwargs)
            if event.once:
                self.unschedule(event.name)
            else:
                event.next_run = event.next_run + event.frequency

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def data_for(self, symbol: Optional[str] = None) -> pd.DataFrame:
        symbol = symbol or self.symbol
        if symbol not in self._data_sources:
            raise KeyError(f"Unknown symbol '{symbol}'.")
        return self._data_sources[symbol]

    def price(self, column: str = "close", *, symbol: Optional[str] = None, offset: int = 0) -> float:
        frame = self.data_for(symbol)
        idx = self.index - offset
        if idx < 0:
            return float("nan")
        return float(frame.iloc[idx][column])

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def snapshot_state(self) -> Dict[str, Any]:
        return dict(self.state)

    # ------------------------------------------------------------------
    # Logging & journaling
    # ------------------------------------------------------------------
    def log(self, message: str, *, category: str | None = None, **fields: Any) -> None:
        entry: Dict[str, Any] = {
            "index": self.index,
            "timestamp": self.now,
            "symbol": self.symbol,
            "message": message,
            "category": category,
        }
        entry.update(fields)
        self.logs.append(entry)
        tags = {"category": category or "general"}
        self.monitor.log_event(message, level=category or "info", tags=tags)
        self.monitor.record_metric("strategy_logs_total", 1.0, tags=tags)

    def logs_dataframe(self, *, sort: bool = True) -> pd.DataFrame:
        frame = logs_to_dataframe(self.logs, sort=sort)
        return frame

    def export_logs_jsonl(self, path: str | PathLike) -> None:
        write_jsonl(self.logs, path)

    def export_logs_csv(self, path: str | PathLike, **csv_kwargs: Any) -> None:
        write_csv(self.logs, path, **csv_kwargs)

    def export_logs_parquet(self, path: str | PathLike, **parquet_kwargs: Any) -> None:
        write_parquet(self.logs, path, **parquet_kwargs)

    def clear_logs(self) -> None:
        self.logs.clear()

    def record(self, category: str, **fields: Any) -> None:
        entry = {
            "timestamp": self.now,
            "symbol": fields.pop("symbol", self.symbol),
            "category": category,
            "fields": dict(fields),
        }
        self._journal.append(entry)
        self.monitor.log_event(f"journal:{category}", level="info", tags=fields)
        if self.state_store and self.strategy_id:
            self.state_store.append_event(self.strategy_id, entry)

    def journal_entries(self) -> List[Dict[str, Any]]:
        return list(self._journal)

    def journal_dataframe(self) -> pd.DataFrame:
        if not self._journal:
            return pd.DataFrame(columns=["timestamp", "symbol", "category", "fields"])
        frame = pd.DataFrame(self._journal)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame

    def clear_journal(self) -> None:
        self._journal.clear()

    def record_metric(self, name: str, value: float, *, tags: Optional[Dict[str, str]] = None) -> None:
        self.monitor.record_metric(name, value, tags=tags)

    def health_check(self, status: str, message: str = "", *, tags: Optional[Dict[str, str]] = None) -> None:
        self.monitor.log_event(f"health:{status}", level=status, tags=tags or {})
        if message:
            self.log(message, category=status, **(tags or {}))

    # ------------------------------------------------------------------
    # Indicator helpers
    # ------------------------------------------------------------------
    def I(
        self,
        func: Callable[..., IndicatorInput],
        *args: Any,
        name: Optional[str] = None,
        cache: bool = True,
        symbol: Optional[str] = None,
        data: Optional[pd.Series | pd.DataFrame] = None,
        **kwargs: Any,
    ) -> Union[IndicatorSeries, IndicatorFrame]:
        if self.data is None:
            raise RuntimeError("Strategy must be bound before creating indicators.")

        if data is not None:
            source = data
        elif args:
            source = None
        else:
            source = self.data_for(symbol)
            args = (source,)

        params_key = tuple(sorted(kwargs.items()))
        cache_key = (name or func.__name__, args, params_key, symbol)

        if cache and cache_key in self._indicator_cache:
            return self._indicator_cache[cache_key]

        output = func(*args, **kwargs)
        normalized = _resolve_indicator_output(output, self.data.index)

        if isinstance(normalized, pd.Series):
            handle = IndicatorSeries(normalized, self, symbol=symbol)
        elif isinstance(normalized, pd.DataFrame):
            handle = IndicatorFrame(normalized, self, symbol=symbol)
        else:  # pragma: no cover - guard rail
            raise TypeError("Indicator function must return pandas Series or DataFrame compatible output.")

        if cache:
            self._indicator_cache[cache_key] = handle
            if name:
                self._indicator_cache_meta[name] = handle

        return handle

    def indicator_names(self) -> List[str]:
        return list(self._indicator_cache_meta.keys())

    def refresh_indicator(self, name: str) -> None:
        meta = self._indicator_cache_meta.get(name)
        if meta is None:
            raise KeyError(name)
        for key, value in list(self._indicator_cache.items()):
            if value is meta:
                self._indicator_cache.pop(key, None)
        self._indicator_cache_meta.pop(name, None)

    # ------------------------------------------------------------------
    # Order API
    # ------------------------------------------------------------------
    def order(
        self,
        side: Union[str, OrderSide],
        *,
        size: Optional[float] = None,
        symbol: Optional[str] = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
    ) -> Any:
        self._ensure_initialized()
        if self.data is None:
            raise RuntimeError("Strategy is not bound to data.")

        side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
        if side_value not in {"buy", "sell"}:
            raise ValueError("Order side must be 'buy' or 'sell'.")

        symbol = symbol or self.symbol
        tif = TimeInForce(time_in_force) if isinstance(time_in_force, str) else time_in_force

        quantity = self._resolve_quantity(side=side_value, size=size, symbol=symbol)
        if quantity <= 0:
            return None

        if side_value == "buy":
            result = self.broker.buy(quantity)
        else:
            result = self.broker.sell(quantity)

        self.log("market_order", category="order", side=side_value, size=quantity, symbol=symbol, tif=tif.value)
        return result

    def buy(self, *, size: Optional[float] = None, symbol: Optional[str] = None) -> Any:
        return self.order("buy", size=size, symbol=symbol)

    def sell(self, *, size: Optional[float] = None, symbol: Optional[str] = None) -> Any:
        return self.order("sell", size=size, symbol=symbol)

    def close(self, symbol: Optional[str] = None) -> Any:
        symbol = symbol or self.symbol
        position = self.portfolio.state.positions.get(symbol) if self.portfolio else None
        if not position:
            return None
        return self.sell(size=position.quantity, symbol=symbol)

    def limit(
        self,
        price: float,
        *,
        side: Union[str, OrderSide] = "buy",
        size: Optional[float] = None,
        symbol: Optional[str] = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        fill_ratio: float = 1.0,
    ) -> Any:
        self._ensure_initialized()
        side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
        if side_value not in {"buy", "sell"}:
            raise ValueError("Limit orders support 'buy' or 'sell' sides.")

        symbol = symbol or self.symbol
        quantity = self._resolve_quantity(side=side_value, size=size, symbol=symbol)
        if quantity <= 0:
            return None

        tif = TimeInForce(time_in_force) if isinstance(time_in_force, str) else time_in_force
        result = self.broker.limit(OrderSide(side_value), price, quantity, time_in_force=tif, fill_ratio=fill_ratio)
        if isinstance(result, Order):
            self.log("limit_order", category="order", order_id=result.id, side=side_value, price=price, size=quantity, symbol=symbol, tif=tif.value)
        return result

    def stop(
        self,
        price: float,
        *,
        side: Union[str, OrderSide] = "sell",
        size: Optional[float] = None,
        symbol: Optional[str] = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        fill_ratio: float = 1.0,
    ) -> Any:
        self._ensure_initialized()
        side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
        if side_value not in {"buy", "sell"}:
            raise ValueError("Stop orders support 'buy' or 'sell' sides.")

        symbol = symbol or self.symbol
        quantity = self._resolve_quantity(side=side_value, size=size, symbol=symbol)
        if quantity <= 0:
            return None

        tif = TimeInForce(time_in_force) if isinstance(time_in_force, str) else time_in_force
        result = self.broker.stop(OrderSide(side_value), price, quantity, time_in_force=tif, fill_ratio=fill_ratio)
        if isinstance(result, Order):
            self.log("stop_order", category="order", order_id=result.id, side=side_value, stop_price=price, size=quantity, symbol=symbol, tif=tif.value)
        return result

    def stop_limit(
        self,
        stop_price: float,
        limit_price: float,
        *,
        side: Union[str, OrderSide] = "sell",
        size: Optional[float] = None,
        symbol: Optional[str] = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
    ) -> Any:
        self._ensure_initialized()
        side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
        if side_value not in {"buy", "sell"}:
            raise ValueError("Stop-limit orders support 'buy' or 'sell' sides.")

        symbol = symbol or self.symbol
        quantity = self._resolve_quantity(side=side_value, size=size, symbol=symbol)
        if quantity <= 0:
            return None

        tif = TimeInForce(time_in_force) if isinstance(time_in_force, str) else time_in_force
        result = self.broker.stop_limit(OrderSide(side_value), stop_price, limit_price, quantity, time_in_force=tif)
        if isinstance(result, Order):
            self.log(
                "stop_limit_order",
                category="order",
                order_id=result.id,
                side=side_value,
                stop_price=stop_price,
                limit_price=limit_price,
                size=quantity,
                symbol=symbol,
                tif=tif.value,
            )
        return result

    def trailing_stop(
        self,
        *,
        side: Union[str, OrderSide] = "sell",
        size: Optional[float] = None,
        trail_amount: Optional[float] = None,
        trail_percent: Optional[float] = None,
        symbol: Optional[str] = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
    ) -> Any:
        self._ensure_initialized()
        side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
        if side_value not in {"buy", "sell"}:
            raise ValueError("Trailing stops support 'buy' or 'sell' sides.")

        symbol = symbol or self.symbol
        quantity = self._resolve_quantity(side=side_value, size=size, symbol=symbol)
        if quantity <= 0:
            return None

        tif = TimeInForce(time_in_force) if isinstance(time_in_force, str) else time_in_force
        result = self.broker.trailing_stop(
            OrderSide(side_value),
            quantity,
            trail_amount=trail_amount,
            trail_percent=trail_percent,
            time_in_force=tif,
        )
        if isinstance(result, Order):
            self.log(
                "trailing_stop",
                category="order",
                order_id=result.id,
                side=side_value,
                trail_amount=trail_amount,
                trail_percent=trail_percent,
                size=quantity,
                symbol=symbol,
                tif=tif.value,
            )
        return result

    def cancel(self, order: Union[Order, str, None]) -> bool:
        self._ensure_initialized()
        if order is None:
            return False
        if not hasattr(self.broker, "cancel"):
            raise RuntimeError("Bound broker does not support order cancellation.")
        if isinstance(order, Order):
            order_id = order.id
        elif hasattr(order, "id"):
            order_id = str(getattr(order, "id"))
        else:
            order_id = str(order)
        success = bool(self.broker.cancel(order_id))
        if success:
            self.log("order_cancelled", category="cancel", order_id=order_id)
        return success

    def cancel_all_orders(self, *, side: Union[str, OrderSide, None] = None) -> int:
        self._ensure_initialized()
        if not hasattr(self.broker, "pending_orders"):
            raise RuntimeError("Bound broker does not expose pending order list.")

        pending: List[Order] = list(getattr(self.broker, "pending_orders", []))
        cancelled = 0
        for order in pending:
            if side is not None:
                side_value = side.value if isinstance(side, OrderSide) else str(side).lower()
                if order.side.value != side_value:
                    continue
            if self.cancel(order):
                cancelled += 1
        return cancelled

    @property
    def open_orders(self) -> List[Order]:
        if not hasattr(self.broker, "pending_orders"):
            return []
        return list(getattr(self.broker, "pending_orders"))

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    @property
    def index(self) -> int:
        return self._current_index

    @property
    def now(self) -> Optional[pd.Timestamp]:
        return self._current_timestamp

    @property
    def row(self) -> Optional[pd.Series]:
        return self._current_row

    @property
    def context(self) -> Any:
        return self._context

    @property
    def cash(self) -> float:
        if self.portfolio is None:
            return 0.0
        state = self.portfolio.state
        balances = getattr(state, "cash_balances", None)
        if isinstance(balances, dict):
            base_currency = getattr(self.portfolio, "base_currency", None)
            if base_currency and base_currency in balances:
                return float(balances[base_currency])
            if balances:
                first_key = next(iter(balances))
                return float(balances[first_key])
        return float(getattr(state, "cash", 0.0))

    @property
    def equity(self) -> float:
        if self.portfolio is None or self.symbol is None or self.now is None:
            return self.cash
        price = self.price()
        snapshot = self.portfolio.snapshot(self.now.to_pydatetime(), {self.symbol: price})
        return float(snapshot.equity)

    @property
    def position_quantity(self) -> float:
        if self.portfolio is None or self.symbol is None:
            return 0.0
        position = self.portfolio.state.positions.get(self.symbol)
        return float(position.quantity) if position else 0.0

    @property
    def has_position(self) -> bool:
        return self.position_quantity > 0

    @property
    def risk_manager(self) -> Any:
        return getattr(self.broker, "risk_manager", None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("Strategy.init has not been executed yet.")

    def _update_context(self, context: Any) -> None:
        self._context = context
        self._current_index = int(context.index)
        self._current_timestamp = context.timestamp
        self._current_row = context.row

    def _execute_rules(self) -> None:
        for rule in self._rules:
            try:
                if rule.condition(self):
                    rule.action(self)
            except Exception as exc:  # pragma: no cover - defensive
                self.log(f"Rule '{rule.name}' failed: {exc}", category="error")

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def _load_persistent_state(self) -> None:
        if not self.state_store or not self.strategy_id or self._state_loaded:
            return
        snapshot = self.state_store.load_state(self.strategy_id)
        if snapshot:
            self.state.update(snapshot.state)
            self.logs = snapshot.logs
            self._journal = snapshot.journal
        self._state_loaded = True

    def persist_state(self) -> None:
        if not self.state_store or not self.strategy_id:
            return
        snapshot = StateSnapshot(
            state=dict(self.state),
            logs=list(self.logs),
            journal=list(self._journal),
            timestamp=datetime.utcnow(),
        )
        self.state_store.save_state(self.strategy_id, snapshot)

    def replay_events(self) -> List[Dict[str, Any]]:
        if not self.state_store or not self.strategy_id:
            return []
        return list(self.state_store.replay_events(self.strategy_id))

    def _resolve_quantity(self, *, side: str, size: Optional[float], symbol: str) -> float:
        if self.portfolio is None:
            raise RuntimeError("Portfolio not bound to strategy.")

        price = self.price(symbol=symbol)
        if not np.isfinite(price) or price <= 0:
            raise ExecutionError("Invalid current price for position sizing.")

        portfolio_state = self.portfolio.state
        position = portfolio_state.positions.get(symbol)

        if side == "buy":
            balances = getattr(portfolio_state, "cash_balances", None)
            if isinstance(balances, dict):
                base_currency = getattr(self.portfolio, "base_currency", None)
                if base_currency and base_currency in balances:
                    cash = float(balances[base_currency])
                else:
                    cash = float(next(iter(balances.values()), 0.0))
            else:
                cash = float(getattr(portfolio_state, "cash", 0.0))
            if cash <= 0:
                return 0.0
            if size is None:
                quantity = cash / price
            elif 0 < size <= 1:
                quantity = (cash * size) / price
            else:
                quantity = float(size)
                if quantity * price > cash + 1e-9:
                    raise ExecutionError("Insufficient cash for requested order size.")
            return max(0.0, quantity)

        # sell side
        if position is None:
            return 0.0

        if size is None:
            return float(position.quantity)
        if 0 < size <= 1:
            return float(position.quantity * size)
        if float(size) > float(position.quantity) + 1e-9:
            raise ExecutionError("Cannot sell more than current position size.")
        return float(size)


class MLStrategy(Strategy):
    """ML-Enhanced Strategy with AutoML and Deep Learning capabilities."""

    def __init__(self, **params):
        super().__init__(**params)

        # ML Components
        self.feature_engineer = FeatureEngineer()
        self.automl_trainer = AutoMLTrainer()
        self.dl_trainer = None
        self.ensemble = None

        # Strategy Parameters
        self.model_type = params.get('model_type', 'automl')
        self.feature_config = params.get('feature_config', self._default_feature_config())
        self.lookback_window = params.get('lookback_window', 50)
        self.prediction_horizon = params.get('prediction_horizon', 5)
        self.confidence_threshold = params.get('confidence_threshold', 0.6)

        # Risk Management
        self.risk_multiplier = params.get('risk_multiplier', 1.0)
        self.stop_loss_multiplier = params.get('stop_loss_multiplier', 1.0)
        self.take_profit_multiplier = params.get('take_profit_multiplier', 1.0)

        # Learning Parameters
        self.retrain_frequency = params.get('retrain_frequency', 100)
        self.min_samples_for_training = params.get('min_samples_for_training', 200)

        # State
        self.signal_history = []
        self.feature_history = []
        self.model_trained = False
        self.last_training_step = -self.retrain_frequency

    def _default_feature_config(self) -> Dict[str, Any]:
        """Default feature configuration."""
        return {
            'sma': {'periods': [5, 10, 20]},
            'ema': {'periods': [5, 10, 20]},
            'rsi': {'periods': [14]},
            'macd': {},
            'bollinger': {'period': 20},
            'volume': {},
            'momentum': {'periods': [1, 5, 10]},
            'volatility': {'periods': [10, 20]},
            'trend': {}
        }

    def initialize(self, data: pd.DataFrame):
        """Initialize the ML strategy."""
        super().init()

        # Create initial features
        self.features = self.feature_engineer.create_features(data, self.feature_config)

        # Initialize target variable (future returns)
        returns = data['close'].pct_change(self.prediction_horizon).shift(-self.prediction_horizon)
        self.target = (returns > 0).astype(int)  # Binary classification

        # Align features and target
        common_index = self.features.index.intersection(self.target.index)
        self.features = self.features.loc[common_index]
        self.target = self.target.loc[common_index]

        self.log("ML Strategy initialized with {} features and {} samples".format(
            len(self.features.columns), len(self.features)))

    def next(self):
        """Main strategy logic with ML predictions."""
        if not self.model_trained:
            self._train_model_if_needed()
            return

        # Generate features for current bar
        current_features = self._get_current_features()
        if current_features is None:
            return

        # Get ML prediction
        signal = self.predict_signal(current_features)

        # Apply confidence threshold
        confidence = self._calculate_prediction_confidence(signal)
        if confidence < self.confidence_threshold:
            signal = 0.0

        # Risk adjustment
        signal *= self.risk_multiplier

        # Execute signal
        self._execute_signal(signal)

        # Store for learning
        self.signal_history.append({
            'timestamp': self.now,
            'signal': signal,
            'confidence': confidence,
            'features': current_features.to_dict()
        })

    def predict_signal(self, features: pd.DataFrame) -> float:
        """Predict trading signal using ML model."""
        if not self.model_trained:
            return 0.0

        try:
            if self.model_type == 'automl':
                prediction = self.automl_trainer.predict(features)[0]
                probability = self.automl_trainer.predict_proba(features)[0]
                return (prediction * 2 - 1) * probability.max()  # Convert to [-1, 1] range

            elif self.model_type == 'deep_learning' and self.dl_trainer:
                prediction = self.dl_trainer.predict(features)[0]
                probability = self.dl_trainer.predict_proba(features)[0]
                return (prediction * 2 - 1) * probability.max()

            else:
                return 0.0

        except Exception as e:
            self.log(f"ML prediction failed: {e}", category="error")
            return 0.0

    def _execute_signal(self, signal: float):
        """Execute trading signal with risk management."""
        if abs(signal) < 0.1:  # Minimum signal threshold
            return

        current_position = self.position_quantity
        target_position = signal * self._calculate_position_size()

        # Position change
        position_change = target_position - current_position

        if position_change > 0.01:  # Buy signal
            size = min(position_change, self._calculate_position_size())
            self.buy(size=size)
        elif position_change < -0.01:  # Sell signal
            size = min(abs(position_change), abs(current_position))
            self.sell(size=size)

    def _calculate_position_size(self) -> float:
        """Calculate position size based on risk management."""
        portfolio_value = self.equity
        risk_per_trade = 0.01  # 1% risk per trade

        # Volatility-adjusted position sizing
        volatility = self.I(lambda x: x['close'].pct_change().rolling(20).std(),
                           name='volatility_20').current or 0.02

        # Kelly criterion adjustment
        win_rate = 0.55  # Assume 55% win rate
        avg_win_loss_ratio = 1.5  # Assume 1.5:1 win/loss ratio

        kelly_fraction = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
        kelly_fraction = max(0.01, min(0.1, kelly_fraction))  # Bound between 1% and 10%

        position_size = (portfolio_value * risk_per_trade * kelly_fraction) / volatility

        return position_size / self.price()  # Convert to shares

    def _get_current_features(self) -> Optional[pd.DataFrame]:
        """Get features for current bar."""
        if self.data is None or len(self.data) < self.lookback_window:
            return None

        # Use recent data to create features
        recent_data = self.data.tail(self.lookback_window)
        features = self.feature_engineer.create_features(recent_data, self.feature_config)

        if features.empty:
            return None

        return features.iloc[-1:].copy()  # Latest features

    def _calculate_prediction_confidence(self, signal: float) -> float:
        """Calculate confidence in the prediction."""
        # Simple confidence based on signal strength and recent accuracy
        signal_strength = abs(signal)

        # Recent accuracy (simplified)
        recent_signals = self.signal_history[-20:]
        if len(recent_signals) > 5:
            recent_confidences = [s['confidence'] for s in recent_signals]
            avg_recent_confidence = np.mean(recent_confidences)
            return min(1.0, signal_strength * avg_recent_confidence)
        else:
            return signal_strength

    def _train_model_if_needed(self):
        """Train ML model if conditions are met."""
        if (len(self.features) >= self.min_samples_for_training and
            self.index - self.last_training_step >= self.retrain_frequency):

            try:
                self._train_model()
                self.model_trained = True
                self.last_training_step = self.index
                self.log("ML model trained/retrained", category="ml")

            except Exception as e:
                self.log(f"Model training failed: {e}", category="error")

    def _train_model(self):
        """Train the ML model."""
        if len(self.features) < self.min_samples_for_training:
            return

        # Prepare training data
        X = self.features
        y = self.target

        if self.model_type == 'automl':
            self.automl_trainer.train(X, y)

        elif self.model_type == 'deep_learning':
            if self.dl_trainer is None:
                self.dl_trainer = DeepLearningTrainer(input_dim=len(X.columns))
            self.dl_trainer.train(X, y)

        self.log(f"Trained {self.model_type} model with {len(X)} samples")

    def on_fill(self, fill):
        """Enhanced fill handling with ML learning."""
        super().on_fill(fill)

        # Store outcome for reinforcement learning
        if self.signal_history:
            last_signal = self.signal_history[-1]
            # Could implement reinforcement learning updates here

    def get_model_performance(self) -> Dict[str, Any]:
        """Get ML model performance metrics."""
        if not self.model_trained:
            return {}

        return {
            'model_type': self.model_type,
            'feature_count': len(self.features.columns) if hasattr(self, 'features') else 0,
            'training_samples': len(self.target) if hasattr(self, 'target') else 0,
            'last_trained_at': self.last_training_step,
            'feature_importance': self.automl_trainer.feature_importance if self.model_type == 'automl' else {}
        }


__all__ = ["Strategy", "MLStrategy", "IndicatorSeries", "IndicatorFrame"]

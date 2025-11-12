"""Automated machine learning pipeline for trading strategies."""

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
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin

# ML libraries
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.svm import SVR
    from sklearn.neural_network import MLPRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Import existing Qantify modules
try:
    from ..reinforcement_learning.dqn_trading import LSTMPredictor
    from ..neural_networks.transformer_models import TransformerPredictor
except ImportError:
    LSTMPredictor = None
    TransformerPredictor = None


@dataclass
class AutoMLConfig:
    """Configuration for AutoML pipeline"""

    # Data preprocessing
    feature_engineering: bool = True
    feature_selection: bool = True
    max_features: int = 50
    handle_missing: str = "auto"  # "auto", "drop", "fill"

    # Model selection
    model_families: List[str] = field(default_factory=lambda: [
        "linear", "tree", "ensemble", "neural", "svm"
    ])
    max_models_per_family: int = 3
    include_custom_models: bool = True

    # Hyperparameter tuning
    tuning_method: str = "bayesian"  # "grid", "random", "bayesian"
    max_tuning_iterations: int = 50
    cv_folds: int = 5
    time_series_cv: bool = True

    # Ensemble building
    use_ensemble: bool = True
    ensemble_method: str = "stacking"  # "stacking", "blending", "voting"
    max_ensemble_models: int = 5

    # Evaluation metrics
    primary_metric: str = "sharpe_ratio"  # "sharpe_ratio", "sortino", "max_drawdown", "profit_factor"
    secondary_metrics: List[str] = field(default_factory=lambda: [
        "total_return", "volatility", "win_rate"
    ])

    # Risk management
    risk_free_rate: float = 0.02
    max_drawdown_limit: float = 0.1
    position_sizing: str = "kelly"  # "equal", "kelly", "optimal_f"

    # Computational resources
    max_parallel_jobs: int = 4
    time_limit_minutes: int = 60
    memory_limit_gb: float = 8.0

    # Trading specific
    prediction_horizon: int = 1
    transaction_costs: float = 0.001
    slippage_model: str = "percentage"


@dataclass
class ModelCandidate:
    """Represents a candidate model in the AutoML pipeline"""

    name: str
    model_family: str
    estimator: Any
    hyperparameters: Dict[str, Any]
    feature_importance: Optional[np.ndarray] = None

    # Performance metrics
    cv_scores: List[float] = field(default_factory=list)
    validation_score: float = 0.0
    training_time: float = 0.0

    # Trading metrics
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_return: float = 0.0
    win_rate: float = 0.0


class AutomatedFeatureEngineer:
    """Automated feature engineering for financial time series"""

    def __init__(self, config: AutoMLConfig):
        self.config = config

    def create_features(self, data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Create comprehensive feature set from raw financial data"""

        df = data.copy()

        # Basic price features
        df = self._add_price_features(df)

        # Technical indicators
        df = self._add_technical_indicators(df)

        # Statistical features
        df = self._add_statistical_features(df)

        # Time-based features
        df = self._add_temporal_features(df)

        # Cross-sectional features
        if len(data.columns) > 1:
            df = self._add_cross_sectional_features(df)

        # Handle missing values
        df = self._handle_missing_values(df)

        # Remove target column if present
        if target_column in df.columns:
            df = df.drop(columns=[target_column])

        return df

    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-based features"""

        if 'close' in df.columns.lower():
            close_col = [col for col in df.columns if col.lower() == 'close'][0]

            # Returns
            df['return_1d'] = df[close_col].pct_change()
            df['return_5d'] = df[close_col].pct_change(5)
            df['return_20d'] = df[close_col].pct_change(20)

            # Log returns
            df['log_return_1d'] = np.log(df[close_col] / df[close_col].shift(1))

            # Price momentum
            df['momentum_1d'] = df[close_col] / df[close_col].shift(1) - 1
            df['momentum_5d'] = df[close_col] / df[close_col].shift(5) - 1

            # Price acceleration
            df['acceleration'] = df['momentum_1d'] - df['momentum_1d'].shift(1)

        return df

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""

        if 'close' not in [col.lower() for col in df.columns]:
            return df

        close_col = [col for col in df.columns if col.lower() == 'close'][0]

        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df[close_col].rolling(period).mean()
            df[f'ema_{period}'] = df[close_col].ewm(span=period).mean()

        # RSI
        delta = df[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df[close_col].ewm(span=12).mean()
        ema26 = df[close_col].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()

        # Bollinger Bands
        sma20 = df[close_col].rolling(window=20).mean()
        std20 = df[close_col].rolling(window=20).std()
        df['bb_upper'] = sma20 + 2 * std20
        df['bb_lower'] = sma20 - 2 * std20
        df['bb_position'] = (df[close_col] - sma20) / (2 * std20)

        # Volatility
        df['volatility_20d'] = df[close_col].pct_change().rolling(20).std()
        df['volatility_60d'] = df[close_col].pct_change().rolling(60).std()

        return df

    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Rolling statistics
            for window in [5, 10, 20]:
                df[f'{col}_mean_{window}'] = df[col].rolling(window).mean()
                df[f'{col}_std_{window}'] = df[col].rolling(window).std()
                df[f'{col}_skew_{window}'] = df[col].rolling(window).skew()
                df[f'{col}_kurt_{window}'] = df[col].rolling(window).kurt()

            # Lagged features
            for lag in [1, 2, 3, 5]:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)

        return df

    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""

        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['is_month_start'] = df.index.is_month_start.astype(int)
            df['is_month_end'] = df.index.is_month_end.astype(int)

            # Cyclical encoding
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

        return df

    def _add_cross_sectional_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add cross-sectional features for multiple assets"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Rank within cross-section
            df[f'{col}_rank'] = df[col].rank(pct=True)

            # Z-score within cross-section
            df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values"""

        if self.config.handle_missing == "drop":
            df = df.dropna()
        elif self.config.handle_missing == "fill":
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        else:  # "auto"
            # Forward fill, then backward fill, then zeros
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)

        return df

    def select_features(self, X: pd.DataFrame, y: pd.Series,
                       max_features: int = 50) -> List[str]:
        """Select most important features"""

        if not self.config.feature_selection:
            return list(X.columns)[:max_features]

        # Correlation-based selection
        correlations = {}
        for col in X.columns:
            if X[col].dtype in ['int64', 'float64']:
                corr = abs(X[col].corr(y))
                if not np.isnan(corr):
                    correlations[col] = corr

        # Sort by correlation
        sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)

        # Select top features
        selected_features = [feature for feature, _ in sorted_features[:max_features]]

        return selected_features


class ModelFactory:
    """Factory for creating and configuring ML models"""

    def __init__(self, config: AutoMLConfig):
        self.config = config

    def create_model_candidates(self) -> List[ModelCandidate]:
        """Create candidate models for each family"""

        candidates = []

        # Linear models
        if "linear" in self.config.model_families and SKLEARN_AVAILABLE:
            candidates.extend(self._create_linear_models())

        # Tree models
        if "tree" in self.config.model_families and SKLEARN_AVAILABLE:
            candidates.extend(self._create_tree_models())

        # Ensemble models
        if "ensemble" in self.config.model_families:
            candidates.extend(self._create_ensemble_models())

        # Neural network models
        if "neural" in self.config.model_families:
            candidates.extend(self._create_neural_models())

        # SVM models
        if "svm" in self.config.model_families and SKLEARN_AVAILABLE:
            candidates.extend(self._create_svm_models())

        return candidates

    def _create_linear_models(self) -> List[ModelCandidate]:
        """Create linear regression models"""

        models = []

        # Linear Regression
        models.append(ModelCandidate(
            name="linear_regression",
            model_family="linear",
            estimator=LinearRegression(),
            hyperparameters={}
        ))

        # Ridge Regression
        for alpha in [0.1, 1.0, 10.0]:
            models.append(ModelCandidate(
                name=f"ridge_{alpha}",
                model_family="linear",
                estimator=Ridge(alpha=alpha),
                hyperparameters={"alpha": alpha}
            ))

        # Lasso Regression
        for alpha in [0.001, 0.01, 0.1]:
            models.append(ModelCandidate(
                name=f"lasso_{alpha}",
                model_family="linear",
                estimator=Lasso(alpha=alpha),
                hyperparameters={"alpha": alpha}
            ))

        return models

    def _create_tree_models(self) -> List[ModelCandidate]:
        """Create tree-based models"""

        models = []

        # Random Forest
        for n_estimators in [100, 200]:
            for max_depth in [10, 20, None]:
                models.append(ModelCandidate(
                    name=f"rf_{n_estimators}_{max_depth}",
                    model_family="tree",
                    estimator=RandomForestRegressor(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        random_state=42
                    ),
                    hyperparameters={
                        "n_estimators": n_estimators,
                        "max_depth": max_depth
                    }
                ))

        return models

    def _create_ensemble_models(self) -> List[ModelCandidate]:
        """Create ensemble models"""

        models = []

        # Gradient Boosting
        if SKLEARN_AVAILABLE:
            models.append(ModelCandidate(
                name="gradient_boosting",
                model_family="ensemble",
                estimator=GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    random_state=42
                ),
                hyperparameters={
                    "n_estimators": 100,
                    "learning_rate": 0.1
                }
            ))

        # XGBoost
        if XGB_AVAILABLE:
            models.append(ModelCandidate(
                name="xgboost",
                model_family="ensemble",
                estimator=xgb.XGBRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    random_state=42
                ),
                hyperparameters={
                    "n_estimators": 100,
                    "learning_rate": 0.1
                }
            ))

        # LightGBM
        if LGBM_AVAILABLE:
            models.append(ModelCandidate(
                name="lightgbm",
                model_family="ensemble",
                estimator=lgb.LGBMRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    random_state=42
                ),
                hyperparameters={
                    "n_estimators": 100,
                    "learning_rate": 0.1
                }
            ))

        # CatBoost
        if CATBOOST_AVAILABLE:
            models.append(ModelCandidate(
                name="catboost",
                model_family="ensemble",
                estimator=cb.CatBoostRegressor(
                    iterations=100,
                    learning_rate=0.1,
                    random_state=42,
                    verbose=False
                ),
                hyperparameters={
                    "iterations": 100,
                    "learning_rate": 0.1
                }
            ))

        return models

    def _create_neural_models(self) -> List[ModelCandidate]:
        """Create neural network models"""

        models = []

        # MLP Regressor
        if SKLEARN_AVAILABLE:
            models.append(ModelCandidate(
                name="mlp_regressor",
                model_family="neural",
                estimator=MLPRegressor(
                    hidden_layer_sizes=(100, 50),
                    max_iter=200,
                    random_state=42
                ),
                hyperparameters={
                    "hidden_layer_sizes": (100, 50),
                    "max_iter": 200
                }
            ))

        # Custom models (LSTM, Transformer)
        if LSTMPredictor is not None:
            models.append(ModelCandidate(
                name="lstm_predictor",
                model_family="neural",
                estimator=LSTMPredictor,
                hyperparameters={}
            ))

        if TransformerPredictor is not None:
            models.append(ModelCandidate(
                name="transformer_predictor",
                model_family="neural",
                estimator=TransformerPredictor,
                hyperparameters={}
            ))

        return models

    def _create_svm_models(self) -> List[ModelCandidate]:
        """Create SVM models"""

        models = []

        # SVR with different kernels
        for kernel in ['rbf', 'linear']:
            for C in [0.1, 1.0, 10.0]:
                models.append(ModelCandidate(
                    name=f"svr_{kernel}_{C}",
                    model_family="svm",
                    estimator=SVR(kernel=kernel, C=C),
                    hyperparameters={"kernel": kernel, "C": C}
                ))

        return models


class TradingMetrics:
    """Trading-specific performance metrics"""

    def __init__(self, config: AutoMLConfig):
        self.config = config

    def calculate_trading_metrics(self, predictions: np.ndarray,
                                actuals: np.ndarray,
                                transaction_costs: float = 0.001) -> Dict[str, float]:
        """Calculate comprehensive trading metrics"""

        # Convert to returns
        pred_returns = np.diff(predictions.flatten()) / predictions[:-1].flatten()
        actual_returns = np.diff(actuals.flatten()) / actuals[:-1].flatten()

        # Strategy returns (simplified)
        strategy_returns = np.sign(pred_returns) * actual_returns

        # Apply transaction costs
        trades = np.abs(np.diff(np.sign(pred_returns + 0.001)))  # Detect trade signals
        strategy_returns -= transaction_costs * trades

        # Calculate metrics
        total_return = np.prod(1 + strategy_returns) - 1

        # Sharpe ratio
        excess_returns = strategy_returns - self.config.risk_free_rate / 252  # Daily risk-free rate
        sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)

        # Sortino ratio
        downside_returns = excess_returns[excess_returns < 0]
        sortino_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(downside_returns)

        # Maximum drawdown
        cumulative = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)

        # Win rate
        win_rate = np.mean(strategy_returns > 0)

        # Profit factor
        winning_trades = strategy_returns[strategy_returns > 0]
        losing_trades = strategy_returns[strategy_returns < 0]
        profit_factor = (np.sum(winning_trades) / -np.sum(losing_trades)) if len(losing_trades) > 0 else np.inf

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'volatility': np.std(strategy_returns),
            'num_trades': len(trades)
        }

    def get_primary_metric_value(self, metrics: Dict[str, float]) -> float:
        """Get the primary metric value for model comparison"""

        if self.config.primary_metric == "sharpe_ratio":
            return metrics.get('sharpe_ratio', -np.inf)
        elif self.config.primary_metric == "sortino_ratio":
            return metrics.get('sortino_ratio', -np.inf)
        elif self.config.primary_metric == "max_drawdown":
            return -metrics.get('max_drawdown', np.inf)  # Negative because lower is better
        elif self.config.primary_metric == "profit_factor":
            return metrics.get('profit_factor', -np.inf)
        else:
            return metrics.get('total_return', -np.inf)


class AutomatedMLPipeline:
    """Complete AutoML pipeline for trading strategies"""

    def __init__(self, config: AutoMLConfig):
        self.config = config

        # Initialize components
        self.feature_engineer = AutomatedFeatureEngineer(config)
        self.model_factory = ModelFactory(config)
        self.metrics_calculator = TradingMetrics(config)

        # Pipeline state
        self.feature_columns = []
        self.selected_models = []
        self.best_model = None
        self.ensemble_model = None

    def fit(self, data: pd.DataFrame, target_column: str,
            validation_split: float = 0.2) -> Dict[str, Any]:
        """Execute the complete AutoML pipeline"""

        print("Starting AutoML pipeline for trading strategies...")
        print(f"Data shape: {data.shape}")
        print(f"Target column: {target_column}")

        start_time = time.time()

        # Step 1: Feature Engineering
        print("\n1. Feature Engineering...")
        X = self.feature_engineer.create_features(data, target_column)
        y = data[target_column].values

        print(f"Created {X.shape[1]} features")

        # Step 2: Feature Selection
        if self.config.feature_selection:
            print("\n2. Feature Selection...")
            self.feature_columns = self.feature_engineer.select_features(
                X, pd.Series(y), self.config.max_features
            )
            X = X[self.feature_columns]
            print(f"Selected {len(self.feature_columns)} features")

        # Step 3: Data Preparation
        print("\n3. Data Preparation...")
        X_train, X_val, y_train, y_val = self._prepare_data(X, y, validation_split)

        # Step 4: Model Selection and Training
        print("\n4. Model Selection and Training...")
        candidates = self.model_factory.create_model_candidates()
        print(f"Created {len(candidates)} model candidates")

        # Evaluate models
        evaluated_models = self._evaluate_models(candidates, X_train, y_train, X_val, y_val)

        # Select best models
        self.selected_models = self._select_best_models(evaluated_models)

        # Step 5: Ensemble Building
        if self.config.use_ensemble and len(self.selected_models) > 1:
            print("\n5. Ensemble Building...")
            self.ensemble_model = self._build_ensemble(self.selected_models, X_train, y_train)

        # Step 6: Final Evaluation
        print("\n6. Final Evaluation...")
        self.best_model = self._select_final_model()

        pipeline_time = time.time() - start_time
        print(".2f"
        return {
            'best_model': self.best_model,
            'selected_models': self.selected_models,
            'ensemble_model': self.ensemble_model,
            'feature_columns': self.feature_columns,
            'pipeline_time': pipeline_time,
            'model_performance': evaluated_models
        }

    def _prepare_data(self, X: pd.DataFrame, y: np.ndarray, validation_split: float):
        """Prepare training and validation data"""

        # Handle NaN values
        X = X.fillna(method='ffill').fillna(method='bfill').fillna(0)

        # Split data (time-aware split)
        split_idx = int(len(X) * (1 - validation_split))
        X_train = X.iloc[:split_idx]
        X_val = X.iloc[split_idx:]
        y_train = y[:split_idx]
        y_val = y[split_idx:]

        return X_train, X_val, y_train, y_val

    def _evaluate_models(self, candidates: List[ModelCandidate],
                        X_train: pd.DataFrame, y_train: np.ndarray,
                        X_val: pd.DataFrame, y_val: np.ndarray) -> List[ModelCandidate]:
        """Evaluate all model candidates"""

        evaluated_models = []

        for i, candidate in enumerate(candidates):
            if (i + 1) % 10 == 0:
                print(f"Evaluating model {i + 1}/{len(candidates)}: {candidate.name}")

            try:
                start_time = time.time()

                # Train model
                if hasattr(candidate.estimator, 'fit'):
                    candidate.estimator.fit(X_train.values, y_train)

                training_time = time.time() - start_time

                # Make predictions
                if hasattr(candidate.estimator, 'predict'):
                    train_pred = candidate.estimator.predict(X_train.values)
                    val_pred = candidate.estimator.predict(X_val.values)
                else:
                    # Custom models
                    train_pred = np.zeros(len(y_train))
                    val_pred = np.zeros(len(y_val))

                # Calculate metrics
                train_metrics = self.metrics_calculator.calculate_trading_metrics(
                    train_pred, y_train
                )
                val_metrics = self.metrics_calculator.calculate_trading_metrics(
                    val_pred, y_val
                )

                # Update candidate
                candidate.training_time = training_time
                candidate.sharpe_ratio = val_metrics['sharpe_ratio']
                candidate.max_drawdown = val_metrics['max_drawdown']
                candidate.total_return = val_metrics['total_return']
                candidate.win_rate = val_metrics['win_rate']
                candidate.validation_score = self.metrics_calculator.get_primary_metric_value(val_metrics)

                evaluated_models.append(candidate)

            except Exception as e:
                print(f"Error evaluating {candidate.name}: {e}")
                continue

        return evaluated_models

    def _select_best_models(self, evaluated_models: List[ModelCandidate],
                           top_k: int = 5) -> List[ModelCandidate]:
        """Select the best performing models"""

        # Sort by primary metric
        sorted_models = sorted(evaluated_models,
                             key=lambda x: x.validation_score,
                             reverse=True)

        return sorted_models[:top_k]

    def _build_ensemble(self, models: List[ModelCandidate],
                       X_train: pd.DataFrame, y_train: np.ndarray) -> Any:
        """Build ensemble model"""

        if self.config.ensemble_method == "stacking":
            # Simple averaging for now
            return self._build_averaging_ensemble(models)

        return None

    def _build_averaging_ensemble(self, models: List[ModelCandidate]) -> Any:
        """Build simple averaging ensemble"""

        class AveragingEnsemble:
            def __init__(self, models):
                self.models = models

            def predict(self, X):
                predictions = []
                for model in self.models:
                    if hasattr(model.estimator, 'predict'):
                        pred = model.estimator.predict(X)
                        predictions.append(pred)

                if predictions:
                    return np.mean(predictions, axis=0)
                else:
                    return np.zeros(X.shape[0])

        return AveragingEnsemble(models)

    def _select_final_model(self) -> ModelCandidate:
        """Select the final best model"""

        if self.ensemble_model is not None:
            # Return a dummy candidate for ensemble
            return ModelCandidate(
                name="ensemble_model",
                model_family="ensemble",
                estimator=self.ensemble_model,
                hyperparameters={}
            )
        elif self.selected_models:
            return self.selected_models[0]
        else:
            return None

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Make predictions using the best model"""

        if self.best_model is None:
            raise ValueError("Pipeline must be fitted before making predictions")

        # Feature engineering
        X = self.feature_engineer.create_features(data, "dummy_target")
        X = X[self.feature_columns] if self.feature_columns else X

        # Handle missing values
        X = X.fillna(method='ffill').fillna(method='bfill').fillna(0)

        # Make predictions
        if hasattr(self.best_model.estimator, 'predict'):
            return self.best_model.estimator.predict(X.values)
        else:
            return np.zeros(len(X))

    def generate_trading_signals(self, data: pd.DataFrame,
                               current_price: float) -> List[Dict[str, Any]]:
        """Generate trading signals"""

        predictions = self.predict(data)

        signals = []
        for i, pred in enumerate(predictions):
            pred_change = (pred - current_price) / current_price

            if abs(pred_change) > self.config.signal_threshold:
                signal_type = "BUY" if pred_change > 0 else "SELL"
                confidence = min(abs(pred_change) / self.config.signal_threshold, 1.0)

                signals.append({
                    'timestamp': data.index[i],
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'predicted_price': pred,
                    'current_price': current_price,
                    'expected_return': pred_change,
                    'model': self.best_model.name if self.best_model else "unknown"
                })

        return signals


# Factory functions
def create_automl_pipeline(config: Optional[AutoMLConfig] = None) -> AutomatedMLPipeline:
    """Factory function for AutoML pipeline"""
    if config is None:
        config = AutoMLConfig()
    return AutomatedMLPipeline(config)


def run_automl_trading(data: pd.DataFrame, target_column: str,
                      config: Optional[AutoMLConfig] = None) -> Dict[str, Any]:
    """Run complete AutoML pipeline for trading"""

    pipeline = create_automl_pipeline(config)
    results = pipeline.fit(data, target_column)

    return {
        'pipeline': pipeline,
        'results': results,
        'best_model_name': results['best_model'].name if results['best_model'] else None,
        'num_features': len(results['feature_columns']),
        'training_time': results['pipeline_time']
    }


# Example usage and testing
if __name__ == "__main__":
    # Test AutoML pipeline
    print("Testing AutoML Pipeline...")

    # Create synthetic financial data
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=500, freq="1H")

    # Generate price data with trend and noise
    trend = np.linspace(100, 120, 500)
    noise = np.random.normal(0, 2, 500)
    prices = trend + noise

    # Create features
    data = pd.DataFrame({
        'close': prices,
        'volume': np.random.normal(1000, 200, 500),
        'open': prices * np.random.normal(1, 0.01, 500),
        'high': prices * np.random.normal(1.01, 0.005, 500),
        'low': prices * np.random.normal(0.99, 0.005, 500)
    }, index=dates)

    # Add target (next period return)
    data['target'] = data['close'].shift(-1).pct_change()
    data = data.dropna()

    # Test AutoML pipeline
    config = AutoMLConfig(
        max_features=20,
        max_models_per_family=2,
        use_ensemble=False  # Disable for faster testing
    )

    print(f"Testing on data with shape: {data.shape}")

    pipeline = create_automl_pipeline(config)
    results = pipeline.fit(data, 'target')

    print("
AutoML Results:")
    print(f"Best model: {results['best_model'].name if results['best_model'] else 'None'}")
    print(f"Number of features: {len(results['feature_columns'])}")
    print(".2f"
    # Test predictions
    test_predictions = pipeline.predict(data.iloc[-50:])
    print(f"Generated {len(test_predictions)} predictions")

    # Test signal generation
    signals = pipeline.generate_trading_signals(data.iloc[-50:], current_price=115.0)
    print(f"Generated {len(signals)} trading signals")

    print("\nAutoML pipeline test completed successfully!")

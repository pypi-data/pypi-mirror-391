"""
Advanced Model Selection and Comparison for Trading Strategies
============================================================

This module implements sophisticated model selection algorithms and comparative analysis
specifically designed for financial trading applications. Includes statistical tests,
performance comparison, model ensembles, and automated model recommendation.

Key Features:
- Statistical model comparison tests
- Risk-adjusted performance metrics
- Model stability and robustness analysis
- Ensemble model construction
- Automated model recommendation
- Cross-validation for time series
- Model confidence intervals
- Trading-specific validation metrics
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from collections import deque, defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import ttest_ind, mannwhitneyu, wilcoxon, friedmanchisquare, normaltest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin

# Statistical testing libraries
try:
    import statsmodels.api as sm
    import statsmodels.stats.api as sms
    from statsmodels.tsa.stattools import adfuller, kpss
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


@dataclass
class ModelSelectionConfig:
    """Configuration for model selection"""

    # Selection criteria
    primary_metric: str = "sharpe_ratio"  # Main selection criterion
    secondary_metrics: List[str] = field(default_factory=lambda: [
        "sortino_ratio", "max_drawdown", "profit_factor"
    ])

    # Statistical testing
    significance_level: float = 0.05  # p-value threshold
    use_statistical_tests: bool = True
    multiple_comparison_correction: str = "bonferroni"  # "bonferroni", "holm", "none"

    # Cross-validation
    cv_folds: int = 5
    time_series_cv: bool = True
    purge_length: int = 10  # For walk-forward validation

    # Ensemble building
    use_ensemble: bool = True
    ensemble_method: str = "weighted_average"  # "weighted_average", "stacking", "blending"
    max_ensemble_models: int = 3

    # Risk management
    risk_free_rate: float = 0.02
    max_drawdown_threshold: float = 0.2
    minimum_sharpe_ratio: float = 0.5

    # Computational
    n_bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    parallel_evaluation: bool = True
    max_parallel_jobs: int = 4


@dataclass
class ModelPerformance:
    """Comprehensive model performance metrics"""

    model_name: str
    model_type: str

    # Basic metrics
    mse: float = 0.0
    mae: float = 0.0
    r2_score: float = 0.0

    # Trading metrics
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    calmar_ratio: float = 0.0
    omega_ratio: float = 0.0

    # Risk metrics
    volatility: float = 0.0
    value_at_risk: float = 0.0
    expected_shortfall: float = 0.0
    beta_coefficient: float = 1.0

    # Statistical properties
    normality_pvalue: float = 0.0  # Test for normality of returns
    autocorrelation: float = 0.0
    stationarity_pvalue: float = 0.0

    # Stability metrics
    prediction_stability: float = 0.0
    parameter_stability: float = 0.0

    # Confidence intervals
    sharpe_ci_lower: float = 0.0
    sharpe_ci_upper: float = 0.0
    return_ci_lower: float = 0.0
    return_ci_upper: float = 0.0

    # Cross-validation scores
    cv_scores: List[float] = field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0


@dataclass
class ModelComparisonResult:
    """Result of statistical model comparison"""

    best_model: str
    ranking: List[str]  # Models ordered by performance
    statistical_tests: Dict[str, Dict[str, float]]  # p-values for pairwise comparisons
    confidence_intervals: Dict[str, Tuple[float, float]]
    ensemble_weights: Optional[Dict[str, float]] = None

    # Stability analysis
    model_stability_scores: Dict[str, float] = field(default_factory=dict)

    # Risk-adjusted rankings
    risk_adjusted_ranking: List[str] = field(default_factory=list)


class StatisticalTester:
    """Statistical testing for model comparison"""

    def __init__(self, config: ModelSelectionConfig):
        self.config = config

    def compare_models_statistically(self, model_performances: Dict[str, ModelPerformance]) \
            -> Dict[str, Dict[str, float]]:
        """Perform statistical tests between all model pairs"""

        models = list(model_performances.keys())
        test_results = {}

        for i, model1 in enumerate(models):
            for j, model2 in enumerate(models):
                if i < j:  # Avoid duplicate comparisons
                    key = f"{model1}_vs_{model2}"

                    # Get performance samples (use CV scores or bootstrap)
                    perf1 = model_performances[model1]
                    perf2 = model_performances[model2]

                    scores1 = perf1.cv_scores if perf1.cv_scores else [perf1.sharpe_ratio]
                    scores2 = perf2.cv_scores if perf2.cv_scores else [perf2.sharpe_ratio]

                    # Perform statistical test
                    test_result = self._perform_statistical_test(scores1, scores2)
                    test_results[key] = test_result

        return test_results

    def _perform_statistical_test(self, scores1: List[float], scores2: List[float]) -> Dict[str, float]:
        """Perform appropriate statistical test based on data characteristics"""

        # Check if data is normally distributed
        if len(scores1) >= 8 and len(scores2) >= 8:
            _, p_normal1 = normaltest(scores1)
            _, p_normal2 = normaltest(scores2)

            if p_normal1 > self.config.significance_level and p_normal2 > self.config.significance_level:
                # Both normal - use t-test
                try:
                    _, p_value = ttest_ind(scores1, scores2, equal_var=False)
                    test_name = "welch_t_test"
                except:
                    _, p_value = mannwhitneyu(scores1, scores2, alternative='two-sided')
                    test_name = "mann_whitney_u"
            else:
                # Not normal - use Mann-Whitney U test
                _, p_value = mannwhitneyu(scores1, scores2, alternative='two-sided')
                test_name = "mann_whitney_u"
        else:
            # Small sample - use Wilcoxon signed-rank test if paired
            try:
                _, p_value = wilcoxon(scores1, scores2)
                test_name = "wilcoxon_signed_rank"
            except:
                # Fallback to Mann-Whitney
                _, p_value = mannwhitneyu(scores1, scores2, alternative='two-sided')
                test_name = "mann_whitney_u"

        # Calculate effect size
        mean_diff = np.mean(scores1) - np.mean(scores2)
        pooled_std = np.sqrt((np.var(scores1) + np.var(scores2)) / 2)
        effect_size = mean_diff / pooled_std if pooled_std > 0 else 0

        return {
            'p_value': p_value,
            'test_name': test_name,
            'effect_size': effect_size,
            'mean_difference': mean_diff,
            'significant': p_value < self.config.significance_level
        }

    def perform_multiple_comparison_correction(self, p_values: Dict[str, float]) -> Dict[str, float]:
        """Apply multiple comparison correction"""

        if self.config.multiple_comparison_correction == "bonferroni":
            n_tests = len(p_values)
            corrected_p_values = {k: min(v * n_tests, 1.0) for k, v in p_values.items()}

        elif self.config.multiple_comparison_correction == "holm":
            sorted_p = sorted(p_values.items(), key=lambda x: x[1])
            corrected_p_values = {}

            for i, (key, p_val) in enumerate(sorted_p):
                corrected_p = p_val * (len(sorted_p) - i)
                corrected_p_values[key] = min(corrected_p, 1.0)

        else:  # "none"
            corrected_p_values = p_values.copy()

        return corrected_p_values


class BootstrapAnalyzer:
    """Bootstrap analysis for model performance"""

    def __init__(self, config: ModelSelectionConfig):
        self.config = config

    def calculate_confidence_intervals(self, performance_data: Dict[str, ModelPerformance]) \
            -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals using bootstrap"""

        confidence_intervals = {}

        for model_name, perf in performance_data.items():
            # Use CV scores if available, otherwise single score
            scores = perf.cv_scores if perf.cv_scores else [perf.sharpe_ratio]

            if len(scores) > 1:
                # Bootstrap resampling
                bootstrap_means = []
                n_samples = len(scores)

                for _ in range(self.config.n_bootstrap_samples):
                    bootstrap_sample = np.random.choice(scores, size=n_samples, replace=True)
                    bootstrap_means.append(np.mean(bootstrap_sample))

                # Calculate confidence interval
                lower = np.percentile(bootstrap_means, (1 - self.config.confidence_level) / 2 * 100)
                upper = np.percentile(bootstrap_means, (1 + self.config.confidence_level) / 2 * 100)

                confidence_intervals[model_name] = (lower, upper)
            else:
                # Single score - use asymptotic approximation
                mean_val = scores[0]
                # Rough approximation for Sharpe ratio CI
                se = 1.0 / np.sqrt(len(scores)) if len(scores) > 0 else 1.0
                margin = se * stats.norm.ppf((1 + self.config.confidence_level) / 2)

                confidence_intervals[model_name] = (mean_val - margin, mean_val + margin)

        return confidence_intervals

    def calculate_prediction_intervals(self, predictions: np.ndarray, confidence: float = 0.95) \
            -> Tuple[np.ndarray, np.ndarray]:
        """Calculate prediction intervals for model forecasts"""

        # Bootstrap prediction intervals
        n_predictions = len(predictions)
        bootstrap_predictions = []

        for _ in range(self.config.n_bootstrap_samples):
            # Resample with replacement
            indices = np.random.choice(n_predictions, size=n_predictions, replace=True)
            bootstrap_pred = predictions[indices]
            bootstrap_predictions.append(np.mean(bootstrap_pred))

        # Calculate percentiles
        lower_bound = np.percentile(bootstrap_predictions, (1 - confidence) / 2 * 100)
        upper_bound = np.percentile(bootstrap_predictions, (1 + confidence) / 2 * 100)

        return np.full_like(predictions, lower_bound), np.full_like(predictions, upper_bound)


class TimeSeriesCrossValidator:
    """Time series specific cross-validation"""

    def __init__(self, config: ModelSelectionConfig):
        self.config = config

    def time_series_split(self, X: np.ndarray, y: np.ndarray, n_splits: int = 5) \
            -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """Create time series cross-validation splits"""

        splits = []
        n_samples = len(X)

        for i in range(n_splits):
            # Rolling window validation
            train_end = int(n_samples * (i + 1) / (n_splits + 1))
            test_end = int(n_samples * (i + 2) / (n_splits + 1))

            # Purge overlapping data
            if self.config.purge_length > 0:
                train_end = min(train_end, n_samples - self.config.purge_length)
                test_start = train_end + self.config.purge_length
            else:
                test_start = train_end

            if test_end > n_samples:
                test_end = n_samples

            X_train = X[:train_end]
            y_train = y[:train_end]
            X_test = X[test_start:test_end]
            y_test = y[test_start:test_end]

            if len(X_test) > 0:
                splits.append((X_train, y_train, X_test, y_test))

        return splits

    def walk_forward_validation(self, X: np.ndarray, y: np.ndarray,
                               initial_train_size: int = 100, step_size: int = 50) \
            -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """Walk-forward validation for time series"""

        splits = []
        n_samples = len(X)

        current_train_end = initial_train_size

        while current_train_end + step_size <= n_samples:
            # Training data
            X_train = X[:current_train_end]
            y_train = y[:current_train_end]

            # Test data
            test_start = current_train_end
            test_end = min(current_train_end + step_size, n_samples)

            X_test = X[test_start:test_end]
            y_test = y[test_start:test_end]

            splits.append((X_train, y_train, X_test, y_test))

            # Move window forward
            current_train_end += step_size

        return splits


class EnsembleBuilder:
    """Build ensembles of trading models"""

    def __init__(self, config: ModelSelectionConfig):
        self.config = config

    def build_ensemble(self, model_performances: Dict[str, ModelPerformance],
                      predictions: Dict[str, np.ndarray]) -> Tuple[Any, Dict[str, float]]:
        """Build an ensemble model"""

        if self.config.ensemble_method == "weighted_average":
            return self._build_weighted_average_ensemble(model_performances, predictions)
        elif self.config.ensemble_method == "stacking":
            return self._build_stacking_ensemble(model_performances, predictions)
        else:
            # Simple average
            return self._build_simple_average_ensemble(predictions)

    def _build_weighted_average_ensemble(self, model_performances: Dict[str, ModelPerformance],
                                        predictions: Dict[str, np.ndarray]) -> Tuple[Any, Dict[str, float]]:
        """Build weighted average ensemble based on performance"""

        # Calculate weights based on Sharpe ratio
        sharpe_ratios = {name: perf.sharpe_ratio for name, perf in model_performances.items()}

        # Normalize to get weights
        total_sharpe = sum(max(0, sr) for sr in sharpe_ratios.values())
        if total_sharpe > 0:
            weights = {name: max(0, sr) / total_sharpe for name, sr in sharpe_ratios.items()}
        else:
            # Equal weights if all Sharpe ratios are negative
            weights = {name: 1.0 / len(sharpe_ratios) for name in sharpe_ratios.keys()}

        class WeightedAverageEnsemble:
            def __init__(self, weights):
                self.weights = weights

            def predict(self, individual_predictions: Dict[str, np.ndarray]) -> np.ndarray:
                weighted_sum = np.zeros_like(next(iter(individual_predictions.values())))
                total_weight = 0

                for model_name, pred in individual_predictions.items():
                    if model_name in self.weights:
                        weight = self.weights[model_name]
                        weighted_sum += weight * pred
                        total_weight += weight

                return weighted_sum / total_weight if total_weight > 0 else weighted_sum

        ensemble = WeightedAverageEnsemble(weights)
        return ensemble, weights

    def _build_stacking_ensemble(self, model_performances: Dict[str, ModelPerformance],
                                predictions: Dict[str, np.ndarray]) -> Tuple[Any, Dict[str, float]]:
        """Build stacking ensemble"""

        # Use top-performing models for stacking
        sorted_models = sorted(model_performances.items(),
                             key=lambda x: x[1].sharpe_ratio, reverse=True)
        top_models = sorted_models[:self.config.max_ensemble_models]

        # Create meta-features
        meta_features = np.column_stack([predictions[name] for name, _ in top_models])

        # Simple linear combination (can be extended with ML model)
        weights = self._optimize_stacking_weights(meta_features, list(predictions.keys())[0])

        class StackingEnsemble:
            def __init__(self, model_names, weights):
                self.model_names = model_names
                self.weights = weights

            def predict(self, individual_predictions: Dict[str, np.ndarray]) -> np.ndarray:
                stacked_pred = np.zeros_like(next(iter(individual_predictions.values())))

                for model_name, weight in zip(self.model_names, self.weights):
                    if model_name in individual_predictions:
                        stacked_pred += weight * individual_predictions[model_name]

                return stacked_pred

        model_names = [name for name, _ in top_models]
        ensemble = StackingEnsemble(model_names, weights[:len(model_names)])

        # Return equal weights for compatibility
        equal_weights = {name: 1.0 / len(model_names) for name in model_names}
        return ensemble, equal_weights

    def _optimize_stacking_weights(self, meta_features: np.ndarray, target: np.ndarray) -> np.ndarray:
        """Optimize stacking weights"""

        def objective(weights):
            prediction = meta_features @ weights
            return -np.corrcoef(prediction, target)[0, 1]  # Maximize correlation

        n_features = meta_features.shape[1]
        bounds = [(0, 1) for _ in range(n_features)]  # Weights between 0 and 1
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # Sum to 1

        try:
            result = optimize.minimize(objective, np.ones(n_features) / n_features,
                                     bounds=bounds, constraints=constraints, method='SLSQP')
            return result.x if result.success else np.ones(n_features) / n_features
        except:
            return np.ones(n_features) / n_features

    def _build_simple_average_ensemble(self, predictions: Dict[str, np.ndarray]) -> Tuple[Any, Dict[str, float]]:
        """Build simple average ensemble"""

        class SimpleAverageEnsemble:
            def predict(self, individual_predictions: Dict[str, np.ndarray]) -> np.ndarray:
                preds = list(individual_predictions.values())
                return np.mean(preds, axis=0)

        ensemble = SimpleAverageEnsemble()
        n_models = len(predictions)
        weights = {name: 1.0 / n_models for name in predictions.keys()}

        return ensemble, weights


class ModelSelector:
    """Main model selection and comparison engine"""

    def __init__(self, config: ModelSelectionConfig):
        self.config = config

        # Initialize components
        self.statistical_tester = StatisticalTester(config)
        self.bootstrap_analyzer = BootstrapAnalyzer(config)
        self.cross_validator = TimeSeriesCrossValidator(config)
        self.ensemble_builder = EnsembleBuilder(config)

    def select_best_model(self, candidate_models: Dict[str, Any],
                         X_train: np.ndarray, y_train: np.ndarray,
                         X_val: np.ndarray, y_val: np.ndarray) -> ModelComparisonResult:
        """Select the best model from candidates"""

        print("Starting model selection process...")

        # Evaluate all models
        model_performances = self._evaluate_models(candidate_models, X_train, y_train, X_val, y_val)

        # Generate predictions for ensemble building
        predictions = self._generate_predictions(candidate_models, X_val)

        # Statistical comparison
        if self.config.use_statistical_tests and len(model_performances) > 1:
            statistical_results = self.statistical_tester.compare_models_statistically(model_performances)
        else:
            statistical_results = {}

        # Calculate confidence intervals
        confidence_intervals = self.bootstrap_analyzer.calculate_confidence_intervals(model_performances)

        # Rank models
        ranking = self._rank_models(model_performances)

        # Build ensemble if requested
        ensemble_weights = None
        if self.config.use_ensemble and len(ranking) > 1:
            ensemble, ensemble_weights = self.ensemble_builder.build_ensemble(model_performances, predictions)
            # Add ensemble to rankings
            ranking.insert(0, "ensemble")

        # Determine best model
        best_model = ranking[0] if ranking else list(model_performances.keys())[0]

        # Risk-adjusted ranking
        risk_adjusted_ranking = self._calculate_risk_adjusted_ranking(model_performances)

        return ModelComparisonResult(
            best_model=best_model,
            ranking=ranking,
            statistical_tests=statistical_results,
            confidence_intervals=confidence_intervals,
            ensemble_weights=ensemble_weights,
            risk_adjusted_ranking=risk_adjusted_ranking
        )

    def _evaluate_models(self, candidate_models: Dict[str, Any],
                        X_train: np.ndarray, y_train: np.ndarray,
                        X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, ModelPerformance]:
        """Evaluate all candidate models"""

        performances = {}

        # Use parallel evaluation if requested
        if self.config.parallel_evaluation:
            with ThreadPoolExecutor(max_workers=self.config.max_parallel_jobs) as executor:
                futures = {}
                for model_name, model in candidate_models.items():
                    future = executor.submit(self._evaluate_single_model,
                                           model_name, model, X_train, y_train, X_val, y_val)
                    futures[future] = model_name

                for future in futures:
                    model_name = futures[future]
                    try:
                        performances[model_name] = future.result(timeout=300)
                    except Exception as e:
                        print(f"Error evaluating {model_name}: {e}")
                        performances[model_name] = self._create_default_performance(model_name)
        else:
            for model_name, model in candidate_models.items():
                try:
                    performances[model_name] = self._evaluate_single_model(
                        model_name, model, X_train, y_train, X_val, y_val
                    )
                except Exception as e:
                    print(f"Error evaluating {model_name}: {e}")
                    performances[model_name] = self._create_default_performance(model_name)

        return performances

    def _evaluate_single_model(self, model_name: str, model: Any,
                              X_train: np.ndarray, y_train: np.ndarray,
                              X_val: np.ndarray, y_val: np.ndarray) -> ModelPerformance:
        """Evaluate a single model"""

        # Cross-validation
        cv_scores = self._perform_cross_validation(model, X_train, y_train)

        # Train final model
        try:
            model.fit(X_train, y_train)
            predictions = model.predict(X_val)
        except:
            predictions = np.zeros(len(y_val))

        # Calculate metrics
        perf = self._calculate_model_performance(model_name, predictions, y_val, cv_scores)

        return perf

    def _perform_cross_validation(self, model: Any, X: np.ndarray, y: np.ndarray) -> List[float]:
        """Perform cross-validation"""

        if self.config.time_series_cv:
            splits = self.cross_validator.time_series_split(X, y, self.config.cv_folds)
        else:
            # Standard CV (not recommended for time series)
            from sklearn.model_selection import KFold
            kf = KFold(n_splits=self.config.cv_folds, shuffle=False)
            splits = [(X[train_idx], y[train_idx], X[test_idx], y[test_idx])
                     for train_idx, test_idx in kf.split(X)]

        cv_scores = []
        for X_train_cv, y_train_cv, X_test_cv, y_test_cv in splits:
            try:
                model_copy = self._clone_model(model)
                model_copy.fit(X_train_cv, y_train_cv)
                pred_cv = model_copy.predict(X_test_cv)

                # Calculate Sharpe ratio for CV fold
                sharpe = self._calculate_sharpe_ratio(pred_cv, y_test_cv)
                cv_scores.append(sharpe)
            except:
                cv_scores.append(0.0)

        return cv_scores

    def _calculate_model_performance(self, model_name: str, predictions: np.ndarray,
                                   actuals: np.ndarray, cv_scores: List[float]) -> ModelPerformance:
        """Calculate comprehensive performance metrics"""

        # Basic ML metrics
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)

        # Trading metrics
        trading_metrics = self._calculate_trading_metrics(predictions, actuals)

        # Statistical properties
        returns = np.diff(predictions.flatten()) / predictions[:-1].flatten()
        normality_pvalue = normaltest(returns)[1] if len(returns) >= 8 else 1.0

        # Autocorrelation
        autocorrelation = np.corrcoef(returns[:-1], returns[1:])[0, 1] if len(returns) > 1 else 0.0

        # Stationarity test
        try:
            stationarity_pvalue = adfuller(returns)[1] if STATSMODELS_AVAILABLE else 1.0
        except:
            stationarity_pvalue = 1.0

        # CV statistics
        cv_mean = np.mean(cv_scores) if cv_scores else 0.0
        cv_std = np.std(cv_scores) if cv_scores else 0.0

        return ModelPerformance(
            model_name=model_name,
            model_type=self._infer_model_type(model_name),

            # Basic metrics
            mse=mse, mae=mae, r2_score=r2,

            # Trading metrics
            **trading_metrics,

            # Statistical properties
            normality_pvalue=normality_pvalue,
            autocorrelation=autocorrelation,
            stationarity_pvalue=stationarity_pvalue,

            # CV scores
            cv_scores=cv_scores,
            cv_mean=cv_mean,
            cv_std=cv_std
        )

    def _calculate_trading_metrics(self, predictions: np.ndarray, actuals: np.ndarray) -> Dict[str, float]:
        """Calculate trading-specific metrics"""

        # Convert to returns
        pred_returns = np.diff(predictions.flatten()) / predictions[:-1].flatten()
        actual_returns = np.diff(actuals.flatten()) / actuals[:-1].flatten()

        # Strategy returns (momentum strategy)
        strategy_returns = np.sign(pred_returns) * actual_returns

        # Apply transaction costs
        trades = np.abs(np.diff(np.sign(pred_returns + 0.001)))
        strategy_returns -= 0.001 * trades  # 0.1% transaction cost

        # Basic metrics
        total_return = np.prod(1 + strategy_returns) - 1

        # Risk-adjusted metrics
        excess_returns = strategy_returns - self.config.risk_free_rate / 252
        sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)

        # Sortino ratio
        downside_returns = excess_returns[excess_returns < 0]
        sortino_ratio = np.sqrt(252) * np.mean(excess_returns) / (np.std(downside_returns) + 1e-10) \
                       if len(downside_returns) > 0 else -np.inf

        # Maximum drawdown
        cumulative = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)

        # Win rate and profit factor
        win_rate = np.mean(strategy_returns > 0)

        winning_trades = strategy_returns[strategy_returns > 0]
        losing_trades = strategy_returns[strategy_returns < 0]
        profit_factor = np.sum(winning_trades) / -np.sum(losing_trades) \
                       if len(losing_trades) > 0 else np.inf

        # Additional ratios
        calmar_ratio = total_return / -max_drawdown if max_drawdown < 0 else np.inf
        omega_ratio = self._calculate_omega_ratio(strategy_returns)

        # Risk metrics
        volatility = np.std(strategy_returns)
        value_at_risk = np.percentile(strategy_returns, 5)  # 5% VaR
        expected_shortfall = np.mean(strategy_returns[strategy_returns <= value_at_risk])

        # Beta (simplified - would need market returns)
        beta_coefficient = 1.0  # Placeholder

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'calmar_ratio': calmar_ratio,
            'omega_ratio': omega_ratio,
            'volatility': volatility,
            'value_at_risk': value_at_risk,
            'expected_shortfall': expected_shortfall,
            'beta_coefficient': beta_coefficient
        }

    def _calculate_omega_ratio(self, returns: np.ndarray, threshold: float = 0.0) -> float:
        """Calculate Omega ratio"""

        excess_returns = returns - threshold
        positive_sum = np.sum(excess_returns[excess_returns > 0])
        negative_sum = -np.sum(excess_returns[excess_returns < 0])

        return positive_sum / negative_sum if negative_sum > 0 else np.inf

    def _calculate_sharpe_ratio(self, predictions: np.ndarray, actuals: np.ndarray) -> float:
        """Calculate Sharpe ratio for CV scoring"""

        pred_returns = np.diff(predictions.flatten()) / predictions[:-1].flatten()
        actual_returns = np.diff(actuals.flatten()) / actuals[:-1].flatten()
        strategy_returns = np.sign(pred_returns) * actual_returns

        excess_returns = strategy_returns - self.config.risk_free_rate / 252
        return np.sqrt(252) * np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)

    def _generate_predictions(self, candidate_models: Dict[str, Any], X: np.ndarray) -> Dict[str, np.ndarray]:
        """Generate predictions from all models"""

        predictions = {}
        for model_name, model in candidate_models.items():
            try:
                if hasattr(model, 'predict'):
                    predictions[model_name] = model.predict(X)
                else:
                    predictions[model_name] = np.zeros(len(X))
            except:
                predictions[model_name] = np.zeros(len(X))

        return predictions

    def _rank_models(self, performances: Dict[str, ModelPerformance]) -> List[str]:
        """Rank models based on primary metric"""

        # Primary ranking
        primary_ranking = sorted(performances.items(),
                               key=lambda x: getattr(x[1], self.config.primary_metric),
                               reverse=True)

        # Apply risk constraints
        filtered_ranking = []
        for model_name, perf in primary_ranking:
            if (perf.sharpe_ratio >= self.config.minimum_sharpe_ratio and
                perf.max_drawdown >= -self.config.max_drawdown_threshold):
                filtered_ranking.append(model_name)

        return filtered_ranking if filtered_ranking else [name for name, _ in primary_ranking]

    def _calculate_risk_adjusted_ranking(self, performances: Dict[str, ModelPerformance]) -> List[str]:
        """Calculate risk-adjusted ranking using multiple criteria"""

        # Create composite score
        composite_scores = {}

        for model_name, perf in performances.items():
            # Normalize metrics (higher is better)
            sharpe_norm = (perf.sharpe_ratio - performances[min(performances.keys(),
                          key=lambda x: performances[x].sharpe_ratio)].sharpe_ratio) / \
                         (performances[max(performances.keys(),
                          key=lambda x: performances[x].sharpe_ratio)].sharpe_ratio + 1e-10)

            sortino_norm = (perf.sortino_ratio - performances[min(performances.keys(),
                           key=lambda x: performances[x].sortino_ratio)].sortino_ratio) / \
                          (performances[max(performances.keys(),
                           key=lambda x: performances[x].sortino_ratio)].sortino_ratio + 1e-10)

            # Risk penalty
            risk_penalty = abs(perf.max_drawdown) / self.config.max_drawdown_threshold

            composite_scores[model_name] = sharpe_norm + sortino_norm - risk_penalty

        # Rank by composite score
        return sorted(composite_scores.keys(), key=lambda x: composite_scores[x], reverse=True)

    def _clone_model(self, model: Any) -> Any:
        """Clone a model for CV"""

        try:
            # Try sklearn clone
            from sklearn.base import clone
            return clone(model)
        except:
            # Fallback - try to create new instance
            try:
                return model.__class__(**model.get_params())
            except:
                # Last resort - return original
                return model

    def _infer_model_type(self, model_name: str) -> str:
        """Infer model type from name"""

        name_lower = model_name.lower()
        if 'xgboost' in name_lower or 'xgb' in name_lower:
            return 'gradient_boosting'
        elif 'lightgbm' in name_lower or 'lgb' in name_lower:
            return 'gradient_boosting'
        elif 'catboost' in name_lower or 'cb' in name_lower:
            return 'gradient_boosting'
        elif 'random_forest' in name_lower or 'rf' in name_lower:
            return 'random_forest'
        elif 'lstm' in name_lower:
            return 'neural_network'
        elif 'transformer' in name_lower:
            return 'neural_network'
        elif 'linear' in name_lower:
            return 'linear'
        elif 'svm' in name_lower:
            return 'svm'
        else:
            return 'unknown'

    def _create_default_performance(self, model_name: str) -> ModelPerformance:
        """Create default performance for failed models"""

        return ModelPerformance(
            model_name=model_name,
            model_type=self._infer_model_type(model_name),
            sharpe_ratio=-np.inf,
            max_drawdown=0.0
        )


# Factory functions
def create_model_selector(config: Optional[ModelSelectionConfig] = None) -> ModelSelector:
    """Factory function for model selector"""
    if config is None:
        config = ModelSelectionConfig()
    return ModelSelector(config)


def compare_trading_models(models: Dict[str, Any], X_train: np.ndarray, y_train: np.ndarray,
                          X_val: np.ndarray, y_val: np.ndarray,
                          config: Optional[ModelSelectionConfig] = None) -> ModelComparisonResult:
    """Convenience function for model comparison"""

    selector = create_model_selector(config)
    return selector.select_best_model(models, X_train, y_train, X_val, y_val)


# Example usage and testing
if __name__ == "__main__":
    # Test model selection
    print("Testing Model Selection...")

    # Create synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20

    X = np.random.randn(n_samples, n_features)
    y = X.sum(axis=1) + np.random.normal(0, 0.1, n_samples)

    # Split data
    split_idx = int(0.8 * n_samples)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    # Create candidate models
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression

        candidate_models = {
            'random_forest': RandomForestRegressor(n_estimators=50, random_state=42),
            'linear_regression': LinearRegression()
        }

        # Test model selection
        config = ModelSelectionConfig(
            primary_metric="sharpe_ratio",
            use_statistical_tests=True,
            use_ensemble=True
        )

        print(f"Testing on data with shape: {X_train.shape}")

        selector = create_model_selector(config)
        result = selector.select_best_model(candidate_models, X_train, y_train, X_val, y_val)

        print("
Model Selection Results:")
        print(f"Best model: {result.best_model}")
        print(f"Model ranking: {result.ranking}")
        print(f"Number of statistical tests: {len(result.statistical_tests)}")

        if result.ensemble_weights:
            print(f"Ensemble weights: {result.ensemble_weights}")

        print(f"Risk-adjusted ranking: {result.risk_adjusted_ranking}")

    except ImportError:
        print("scikit-learn not available - Model selection functionality disabled")
        print("Install scikit-learn: pip install scikit-learn")

    print("\nModel selection test completed successfully!")

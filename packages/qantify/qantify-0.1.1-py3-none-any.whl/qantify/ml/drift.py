"""Advanced model drift detection, concept drift, monitoring, and adaptive retraining."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency, entropy, wasserstein_distance
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.ensemble import IsolationForest, VotingClassifier, VotingRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    roc_auc_score, log_loss
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import itertools

# Optional dependencies
try:
    from alibi_detect.cd import MMDDrift, LSDDDrift, ChiSquareDrift, FETDrift  # type: ignore
    HAS_ALIBI = True
except ImportError:
    HAS_ALIBI = False

try:
    from frouros.detectors.concept_drift import DDM, EDDM, ADWIN, HDDM_A, HDDM_W  # type: ignore
    HAS_FROUROS = True
except ImportError:
    HAS_FROUROS = False

try:
    from river.drift import ADWIN as RiverADWIN, DDM as RiverDDM, EDDM as RiverEDDM  # type: ignore
    HAS_RIVER = True
except ImportError:
    HAS_RIVER = False


@dataclass(slots=True)
class DriftMetrics:
    """Comprehensive drift detection metrics."""
    ks_stat: float
    ks_pvalue: float
    psi: float
    wasserstein_distance: Optional[float] = None
    jensen_shannon_divergence: Optional[float] = None
    hellinger_distance: Optional[float] = None
    total_variation_distance: Optional[float] = None
    chi_square_stat: Optional[float] = None
    chi_square_pvalue: Optional[float] = None
    mmd_stat: Optional[float] = None
    mmd_pvalue: Optional[float] = None
    lsdd_stat: Optional[float] = None
    lsdd_pvalue: Optional[float] = None
    drift_detected: bool = False
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DriftDetector:
    """Advanced drift detector with multiple statistical tests."""

    def __init__(
        self,
        *,
        bins: int = 10,
        alpha: float = 0.05,
        methods: Optional[List[str]] = None
    ) -> None:
        self.bins = bins
        self.alpha = alpha
        self.methods = methods or ['ks', 'psi', 'wasserstein']

    def compute(self, baseline: pd.Series, current: pd.Series) -> DriftMetrics:
        """Compute comprehensive drift metrics."""
        baseline = baseline.dropna()
        current = current.dropna()

        if baseline.empty or current.empty:
            return DriftMetrics(
                ks_stat=0.0, ks_pvalue=1.0, psi=0.0,
                drift_detected=False, confidence=0.0
            )

        metrics = {}

        # Kolmogorov-Smirnov test
        if 'ks' in self.methods:
            ks_result = ks_2samp(baseline, current)
            metrics.update({
                'ks_stat': float(ks_result.statistic),
                'ks_pvalue': float(ks_result.pvalue)
            })

        # Population Stability Index
        if 'psi' in self.methods:
            metrics['psi'] = self._population_stability_index(baseline, current)

        # Wasserstein distance
        if 'wasserstein' in self.methods:
            metrics['wasserstein_distance'] = wasserstein_distance(baseline, current)

        # Jensen-Shannon divergence
        if 'js_divergence' in self.methods:
            metrics['jensen_shannon_divergence'] = self._jensen_shannon_divergence(baseline, current)

        # Hellinger distance
        if 'hellinger' in self.methods:
            metrics['hellinger_distance'] = self._hellinger_distance(baseline, current)

        # Total variation distance
        if 'total_variation' in self.methods:
            metrics['total_variation_distance'] = self._total_variation_distance(baseline, current)

        # Chi-square test (for binned data)
        if 'chi_square' in self.methods:
            chi_stat, chi_pval = self._chi_square_test(baseline, current)
            metrics.update({
                'chi_square_stat': chi_stat,
                'chi_square_pvalue': chi_pval
            })

        # Determine if drift is detected
        drift_detected, confidence = self._assess_drift(metrics)

        return DriftMetrics(
            **metrics,
            drift_detected=drift_detected,
            confidence=confidence
        )

    def _population_stability_index(self, baseline: pd.Series, current: pd.Series) -> float:
        """Calculate Population Stability Index."""
        bins = np.linspace(min(baseline.min(), current.min()),
                          max(baseline.max(), current.max()), self.bins + 1)
        hist_base, _ = np.histogram(baseline, bins=bins)
        hist_curr, _ = np.histogram(current, bins=bins)

        base_pct = hist_base / max(hist_base.sum(), 1e-9)
        curr_pct = hist_curr / max(hist_curr.sum(), 1e-9)

        psi = np.sum((curr_pct - base_pct) * np.log((curr_pct + 1e-9) / (base_pct + 1e-9)))
        return float(psi)

    def _jensen_shannon_divergence(self, baseline: pd.Series, current: pd.Series) -> float:
        """Calculate Jensen-Shannon divergence."""
        bins = np.linspace(min(baseline.min(), current.min()),
                          max(baseline.max(), current.max()), self.bins + 1)
        hist_base, _ = np.histogram(baseline, bins=bins)
        hist_curr, _ = np.histogram(current, bins=bins)

        base_pct = hist_base / max(hist_base.sum(), 1e-9)
        curr_pct = hist_curr / max(hist_curr.sum(), 1e-9)

        # Jensen-Shannon divergence
        m = (base_pct + curr_pct) / 2
        js_div = (entropy(base_pct, m) + entropy(curr_pct, m)) / 2
        return float(js_div)

    def _hellinger_distance(self, baseline: pd.Series, current: pd.Series) -> float:
        """Calculate Hellinger distance."""
        bins = np.linspace(min(baseline.min(), current.min()),
                          max(baseline.max(), current.max()), self.bins + 1)
        hist_base, _ = np.histogram(baseline, bins=bins)
        hist_curr, _ = np.histogram(current, bins=bins)

        base_pct = hist_base / max(hist_base.sum(), 1e-9)
        curr_pct = hist_curr / max(hist_curr.sum(), 1e-9)

        hellinger = np.sqrt(np.sum((np.sqrt(base_pct) - np.sqrt(curr_pct))**2)) / np.sqrt(2)
        return float(hellinger)

    def _total_variation_distance(self, baseline: pd.Series, current: pd.Series) -> float:
        """Calculate Total Variation Distance."""
        bins = np.linspace(min(baseline.min(), current.min()),
                          max(baseline.max(), current.max()), self.bins + 1)
        hist_base, _ = np.histogram(baseline, bins=bins)
        hist_curr, _ = np.histogram(current, bins=bins)

        base_pct = hist_base / max(hist_base.sum(), 1e-9)
        curr_pct = hist_curr / max(hist_curr.sum(), 1e-9)

        tv_distance = np.sum(np.abs(base_pct - curr_pct)) / 2
        return float(tv_distance)

    def _chi_square_test(self, baseline: pd.Series, current: pd.Series) -> Tuple[float, float]:
        """Perform Chi-square test for binned distributions."""
        bins = np.linspace(min(baseline.min(), current.min()),
                          max(baseline.max(), current.max()), self.bins + 1)
        hist_base, _ = np.histogram(baseline, bins=bins)
        hist_curr, _ = np.histogram(current, bins=bins)

        # Create contingency table
        contingency = np.array([hist_base, hist_curr])

        try:
            chi2_stat, p_value, _, _ = chi2_contingency(contingency)
            return float(chi2_stat), float(p_value)
        except ValueError:
            return 0.0, 1.0

    def _assess_drift(self, metrics: Dict[str, float]) -> Tuple[bool, float]:
        """Assess if drift is detected based on multiple metrics."""
        drift_indicators = []

        # KS test
        if 'ks_pvalue' in metrics and metrics['ks_pvalue'] < self.alpha:
            drift_indicators.append(1)

        # PSI threshold (typically > 0.25 indicates significant drift)
        if 'psi' in metrics and metrics['psi'] > 0.25:
            drift_indicators.append(1)

        # Wasserstein distance (higher values indicate more drift)
        if 'wasserstein_distance' in metrics and metrics['wasserstein_distance'] > 0.1:
            drift_indicators.append(1)

        # Chi-square test
        if 'chi_square_pvalue' in metrics and metrics['chi_square_pvalue'] < self.alpha:
            drift_indicators.append(1)

        drift_detected = len(drift_indicators) >= 2  # Require at least 2 indicators
        confidence = len(drift_indicators) / len([k for k in metrics.keys() if k in self.methods])

        return drift_detected, confidence


@dataclass(slots=True)
class RetrainingSchedule:
    """Advanced retraining schedule with multiple triggering conditions."""
    interval: timedelta
    last_run: Optional[datetime] = None
    drift_threshold: float = 0.2
    performance_drop_threshold: float = 0.1
    min_samples_since_last_retrain: int = 1000
    max_samples_without_check: int = 10000
    adaptive: bool = True

    def due(
        self,
        current_time: datetime,
        drift_metrics: Optional[DriftMetrics] = None,
        performance_drop: Optional[float] = None,
        samples_since_last_retrain: int = 0
    ) -> bool:
        """Check if retraining is due based on multiple conditions."""
        # Always retrain if never run before
        if self.last_run is None:
            return True

        conditions = []

        # Time-based condition
        time_condition = current_time - self.last_run >= self.interval
        conditions.append(time_condition)

        # Drift-based condition
        if drift_metrics and drift_metrics.drift_detected:
            drift_condition = drift_metrics.confidence >= self.drift_threshold
            conditions.append(drift_condition)

        # Performance-based condition
        if performance_drop is not None:
            perf_condition = performance_drop >= self.performance_drop_threshold
            conditions.append(perf_condition)

        # Sample-based condition
        sample_condition = samples_since_last_retrain >= self.min_samples_since_last_retrain
        conditions.append(sample_condition)

        # Adaptive adjustment
        if self.adaptive and len(conditions) > 1:
            # Require at least 2 conditions to be met for adaptive scheduling
            return sum(conditions) >= 2
        else:
            # Standard behavior: any condition triggers retraining
            return any(conditions)

    def update_last_run(self, timestamp: datetime) -> None:
        """Update the last run timestamp."""
        self.last_run = timestamp

    def get_next_scheduled_time(self) -> datetime:
        """Get the next scheduled retraining time."""
        if self.last_run is None:
            return datetime.utcnow()
        return self.last_run + self.interval


class DriftMonitor:
    """Advanced drift monitoring system with comprehensive tracking."""

    def __init__(
        self,
        *,
        detector: Optional[DriftDetector] = None,
        schedule: Optional[RetrainingSchedule] = None,
        threshold: float = 0.2,
        retrain_callback: Optional[Callable[[datetime], None]] = None,
        enable_logging: bool = True,
        alert_callback: Optional[Callable[[DriftMetrics, datetime], None]] = None,
    ) -> None:
        self.detector = detector or DriftDetector()
        self.schedule = schedule or RetrainingSchedule(interval=timedelta(days=1))
        self.threshold = threshold
        self.retrain_callback = retrain_callback
        self.alert_callback = alert_callback
        self.enable_logging = enable_logging
        self.baseline: Optional[pd.Series] = None
        self.baseline_timestamp: Optional[datetime] = None
        self.drift_history: List[Tuple[datetime, DriftMetrics]] = []
        self.performance_history: List[Tuple[datetime, Dict[str, float]]] = []
        self.samples_processed = 0

    def update_baseline(self, baseline: pd.Series, timestamp: Optional[datetime] = None) -> None:
        """Update the baseline distribution."""
        self.baseline = baseline.copy()
        self.baseline_timestamp = timestamp or datetime.utcnow()
        if self.enable_logging:
            print(f"Baseline updated at {self.baseline_timestamp}")

    def check(
        self,
        current: pd.Series,
        timestamp: Optional[datetime] = None,
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> DriftMetrics:
        """Check for drift and update monitoring state."""
        if self.baseline is None:
            raise RuntimeError("Baseline must be set before checking drift.")

        current_time = timestamp or datetime.utcnow()
        metrics = self.detector.compute(self.baseline, current)

        # Update sample counter
        self.samples_processed += len(current)

        # Store drift history
        self.drift_history.append((current_time, metrics))

        # Store performance history if provided
        if performance_metrics:
            self.performance_history.append((current_time, performance_metrics))

        # Check retraining conditions
        retrain_due = self.schedule.due(
            current_time=current_time,
            drift_metrics=metrics,
            performance_drop=self._calculate_performance_drop() if performance_metrics else None,
            samples_since_last_retrain=self.samples_processed
        )

        # Trigger alerts if drift detected
        if metrics.drift_detected and self.alert_callback:
            self.alert_callback(metrics, current_time)

        # Trigger retraining if due
        if retrain_due:
            if self.retrain_callback:
                self.retrain_callback(current_time)
            self.schedule.update_last_run(current_time)
            if self.enable_logging:
                print(f"Retraining triggered at {current_time}")

        return metrics

    def get_drift_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of drift detection over recent period."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_history = [(t, m) for t, m in self.drift_history if t >= cutoff]

        if not recent_history:
            return {"drift_incidents": 0, "avg_confidence": 0.0}

        drift_incidents = sum(1 for _, m in recent_history if m.drift_detected)
        avg_confidence = np.mean([m.confidence for _, m in recent_history])

        return {
            "drift_incidents": drift_incidents,
            "total_checks": len(recent_history),
            "drift_rate": drift_incidents / len(recent_history),
            "avg_confidence": avg_confidence,
            "most_recent_drift": max((t for t, m in recent_history if m.drift_detected), default=None)
        }

    def _calculate_performance_drop(self) -> Optional[float]:
        """Calculate recent performance drop."""
        if len(self.performance_history) < 2:
            return None

        # Simple implementation: compare most recent to baseline performance
        # This could be made more sophisticated
        recent_perf = self.performance_history[-1][1]
        baseline_perf = self.performance_history[0][1]

        # Assume higher values are better (customize based on metric)
        if 'accuracy' in recent_perf and 'accuracy' in baseline_perf:
            return baseline_perf['accuracy'] - recent_perf['accuracy']

        return None


# =============================================================================
# CONCEPT DRIFT DETECTORS
# =============================================================================

class ConceptDriftDetector:
    """Concept drift detection using various algorithms."""

    def __init__(self, method: str = "ddm", **kwargs):
        self.method = method
        self.detector = None
        self._initialize_detector(**kwargs)

    def _initialize_detector(self, **kwargs):
        """Initialize the concept drift detector."""
        if self.method == "ddm":
            if HAS_FROUROS:
                self.detector = DDM(**kwargs)
            elif HAS_RIVER:
                self.detector = RiverDDM(**kwargs)
            else:
                raise ImportError("DDM requires frouros or river-ml")
        elif self.method == "eddm":
            if HAS_FROUROS:
                self.detector = EDDM(**kwargs)
            elif HAS_RIVER:
                self.detector = RiverEDDM(**kwargs)
            else:
                raise ImportError("EDDM requires frouros or river-ml")
        elif self.method == "adwin":
            if HAS_FROUROS:
                self.detector = ADWIN(**kwargs)
            elif HAS_RIVER:
                self.detector = RiverADWIN(**kwargs)
            else:
                raise ImportError("ADWIN requires frouros or river-ml")
        elif self.method == "hddm_a":
            if HAS_FROUROS:
                self.detector = HDDM_A(**kwargs)
            else:
                raise ImportError("HDDM_A requires frouros")
        elif self.method == "hddm_w":
            if HAS_FROUROS:
                self.detector = HDDM_W(**kwargs)
            else:
                raise ImportError("HDDM_W requires frouros")
        else:
            raise ValueError(f"Unknown concept drift method: {self.method}")

    def update(self, y_true: float, y_pred: float) -> Dict[str, Any]:
        """Update detector with new prediction and return drift status."""
        if hasattr(self.detector, 'update'):
            # Frouros interface
            result = self.detector.update(y_true=y_true, y_pred=y_pred)
            return {
                "drift_detected": result.drift,
                "warning_detected": getattr(result, 'warning', False),
                "confidence": getattr(result, 'confidence', 0.0)
            }
        elif hasattr(self.detector, 'update'):
            # River interface
            drift_detected = self.detector.update(y_true - y_pred)  # Error-based
            return {
                "drift_detected": drift_detected,
                "warning_detected": False,
                "confidence": 1.0 if drift_detected else 0.0
            }
        else:
            raise RuntimeError("Detector does not have update method")


class AlibiDriftDetector:
    """Drift detection using Alibi Detect library."""

    def __init__(self, method: str = "mmd", **kwargs):
        if not HAS_ALIBI:
            raise ImportError("Alibi Detect required for advanced drift detection")

        self.method = method
        self.detector = None
        self.fitted = False
        self._initialize_detector(**kwargs)

    def _initialize_detector(self, **kwargs):
        """Initialize Alibi Detect drift detector."""
        if self.method == "mmd":
            self.detector = MMDDrift(**kwargs)
        elif self.method == "lsdd":
            self.detector = LSDDDrift(**kwargs)
        elif self.method == "chi_square":
            self.detector = ChiSquareDrift(**kwargs)
        elif self.method == "fet":
            self.detector = FETDrift(**kwargs)
        else:
            raise ValueError(f"Unknown Alibi Detect method: {self.method}")

    def fit(self, X: np.ndarray):
        """Fit the drift detector on reference data."""
        self.detector.fit(X)
        self.fitted = True

    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Predict drift on new data."""
        if not self.fitted:
            raise RuntimeError("Detector must be fitted before prediction")

        result = self.detector.predict(X)

        return {
            "drift_detected": bool(result['data']['is_drift']),
            "p_value": float(result['data']['p_val']) if 'p_val' in result['data'] else None,
            "distance": float(result['data']['distance']) if 'distance' in result['data'] else None,
            "threshold": float(result['data']['threshold']) if 'threshold' in result['data'] else None,
            "confidence": 1.0 - (result['data'].get('p_val', 1.0))
        }


# =============================================================================
# MODEL PERFORMANCE MONITORING
# =============================================================================

@dataclass(slots=True)
class PerformanceMetrics:
    """Comprehensive model performance metrics."""
    timestamp: datetime
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    log_loss: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class ModelPerformanceMonitor:
    """Monitor model performance over time."""

    def __init__(
        self,
        target_type: str = "regression",
        baseline_metrics: Optional[Dict[str, float]] = None,
        alert_threshold: float = 0.1
    ):
        self.target_type = target_type
        self.baseline_metrics = baseline_metrics or {}
        self.alert_threshold = alert_threshold
        self.performance_history: List[PerformanceMetrics] = []
        self.alerts_triggered: List[Tuple[datetime, str, float]] = []

    def update(
        self,
        y_true: Union[np.ndarray, pd.Series],
        y_pred: Union[np.ndarray, pd.Series],
        timestamp: Optional[datetime] = None,
        custom_metrics: Optional[Dict[str, float]] = None
    ) -> PerformanceMetrics:
        """Update performance metrics."""
        current_time = timestamp or datetime.utcnow()

        # Convert to numpy arrays
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        metrics = PerformanceMetrics(timestamp=current_time)

        if self.target_type == "classification":
            # Classification metrics
            try:
                metrics.accuracy = accuracy_score(y_true, y_pred)
                metrics.precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
                metrics.recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
                metrics.f1_score = f1_score(y_true, y_pred, average='weighted', zero_division=0)

                # ROC AUC (for binary classification)
                if len(np.unique(y_true)) == 2:
                    try:
                        if hasattr(y_pred, 'shape') and len(y_pred.shape) > 1:
                            y_pred_proba = y_pred[:, 1]
                        else:
                            y_pred_proba = y_pred
                        metrics.roc_auc = roc_auc_score(y_true, y_pred_proba)
                    except:
                        pass

                # Log loss
                try:
                    if hasattr(y_pred, 'shape') and len(y_pred.shape) > 1:
                        metrics.log_loss = log_loss(y_true, y_pred)
                    else:
                        # Assume binary with single probability
                        y_pred_proba = np.column_stack([1 - y_pred, y_pred])
                        metrics.log_loss = log_loss(y_true, y_pred_proba)
                except:
                    pass

            except Exception as e:
                warnings.warn(f"Error calculating classification metrics: {e}")

        else:
            # Regression metrics
            try:
                metrics.mse = mean_squared_error(y_true, y_pred)
                metrics.mae = mean_absolute_error(y_true, y_pred)
                metrics.r2_score = r2_score(y_true, y_pred)
            except Exception as e:
                warnings.warn(f"Error calculating regression metrics: {e}")

        # Custom metrics
        if custom_metrics:
            metrics.custom_metrics.update(custom_metrics)

        # Store history
        self.performance_history.append(metrics)

        # Check for alerts
        self._check_alerts(metrics)

        return metrics

    def _check_alerts(self, current_metrics: PerformanceMetrics):
        """Check if performance degradation triggers alerts."""
        if not self.baseline_metrics:
            # Set baseline if not provided
            self.baseline_metrics.update({
                k: v for k, v in current_metrics.__dict__.items()
                if k not in ['timestamp', 'custom_metrics'] and v is not None
            })
            return

        for metric_name, baseline_value in self.baseline_metrics.items():
            current_value = getattr(current_metrics, metric_name)
            if current_value is None:
                continue

            # Calculate degradation (assuming higher values are better)
            if metric_name in ['mse', 'mae', 'log_loss']:
                # Lower is better for these metrics
                degradation = (current_value - baseline_value) / max(abs(baseline_value), 1e-9)
            else:
                # Higher is better for other metrics
                degradation = (baseline_value - current_value) / max(abs(baseline_value), 1e-9)

            if abs(degradation) >= self.alert_threshold:
                alert = (current_metrics.timestamp, metric_name, degradation)
                self.alerts_triggered.append(alert)
                warnings.warn(
                    f"Performance alert: {metric_name} degraded by {degradation:.3f} "
                    f"at {current_metrics.timestamp}"
                )

    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary over recent period."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_history = [m for m in self.performance_history if m.timestamp >= cutoff]

        if not recent_history:
            return {}

        summary = {}
        metric_names = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc',
                       'log_loss', 'mse', 'mae', 'r2_score']

        for metric_name in metric_names:
            values = [getattr(m, metric_name) for m in recent_history if getattr(m, metric_name) is not None]
            if values:
                summary[f"{metric_name}_mean"] = np.mean(values)
                summary[f"{metric_name}_std"] = np.std(values)
                summary[f"{metric_name}_trend"] = np.polyfit(range(len(values)), values, 1)[0] if len(values) > 1 else 0

        summary["alerts_count"] = len([a for a in self.alerts_triggered if a[0] >= cutoff])

        return summary


# =============================================================================
# ADAPTIVE RETRAINING SYSTEM
# =============================================================================

class AdaptiveRetrainingManager:
    """Adaptive retraining system with multiple strategies."""

    def __init__(
        self,
        base_model: Any,
        retraining_strategies: Optional[List[str]] = None,
        performance_monitor: Optional[ModelPerformanceMonitor] = None,
        drift_monitor: Optional[DriftMonitor] = None
    ):
        self.base_model = base_model
        self.retraining_strategies = retraining_strategies or ["incremental", "full", "ensemble"]
        self.performance_monitor = performance_monitor
        self.drift_monitor = drift_monitor

        self.retraining_history: List[Dict[str, Any]] = []
        self.current_model_version = 0
        self.model_versions: Dict[int, Any] = {}

    def should_retrain(
        self,
        drift_metrics: Optional[DriftMetrics] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        sample_size: int = 0
    ) -> Tuple[bool, str]:
        """Determine if retraining is needed and which strategy to use."""
        retrain_needed = False
        strategy = "none"
        reasons = []

        # Check drift
        if drift_metrics and drift_metrics.drift_detected:
            retrain_needed = True
            reasons.append("drift_detected")

        # Check performance degradation
        if performance_metrics and self.performance_monitor:
            recent_perf = self.performance_monitor.get_performance_summary(days=7)
            for key, value in recent_perf.items():
                if key.endswith("_trend") and value < -0.01:  # Significant downward trend
                    retrain_needed = True
                    reasons.append("performance_degradation")
                    break

        # Check sample size for incremental learning
        if sample_size > 1000 and "incremental" in self.retraining_strategies:
            strategy = "incremental"
        elif retrain_needed:
            # Choose strategy based on available data and model type
            if hasattr(self.base_model, 'partial_fit') and "incremental" in self.retraining_strategies:
                strategy = "incremental"
            elif "full" in self.retraining_strategies:
                strategy = "full"
            elif "ensemble" in self.retraining_strategies:
                strategy = "ensemble"

        return retrain_needed, strategy

    def retrain(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        strategy: str,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute retraining with specified strategy."""
        start_time = time.time()
        self.current_model_version += 1

        result = {
            "version": self.current_model_version,
            "strategy": strategy,
            "start_time": datetime.utcnow(),
            "training_samples": len(X_train)
        }

        if strategy == "incremental":
            new_model = self._incremental_retrain(X_train, y_train, **kwargs)
        elif strategy == "full":
            new_model = self._full_retrain(X_train, y_train, X_val, y_val, **kwargs)
        elif strategy == "ensemble":
            new_model = self._ensemble_retrain(X_train, y_train, X_val, y_val, **kwargs)
        else:
            raise ValueError(f"Unknown retraining strategy: {strategy}")

        # Store model version
        self.model_versions[self.current_model_version] = new_model

        # Evaluate new model
        if X_val is not None and y_val is not None:
            val_metrics = self._evaluate_model(new_model, X_val, y_val)
            result["validation_metrics"] = val_metrics

        result["training_time"] = time.time() - start_time
        self.retraining_history.append(result)

        return result

    def _incremental_retrain(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> Any:
        """Incremental retraining using partial_fit."""
        if not hasattr(self.base_model, 'partial_fit'):
            # Fallback to full retrain
            return self._full_retrain(X_train, y_train, None, None, **kwargs)

        model_copy = self._clone_model(self.base_model)

        # Incremental learning
        batch_size = kwargs.get('batch_size', 1000)
        for i in range(0, len(X_train), batch_size):
            X_batch = X_train.iloc[i:i+batch_size]
            y_batch = y_train.iloc[i:i+batch_size]
            model_copy.partial_fit(X_batch, y_batch)

        return model_copy

    def _full_retrain(self, X_train: pd.DataFrame, y_train: pd.Series,
                     X_val: Optional[pd.DataFrame], y_val: Optional[pd.Series], **kwargs) -> Any:
        """Full retraining from scratch."""
        model_copy = self._clone_model(self.base_model)
        model_copy.fit(X_train, y_train)
        return model_copy

    def _ensemble_retrain(self, X_train: pd.DataFrame, y_train: pd.Series,
                         X_val: Optional[pd.DataFrame], y_val: Optional[pd.Series], **kwargs) -> Any:
        """Ensemble retraining combining old and new models."""
        # Train new model
        new_model = self._full_retrain(X_train, y_train, X_val, y_val, **kwargs)

        # Create ensemble with previous models
        recent_versions = list(self.model_versions.keys())[-3:]  # Use last 3 versions
        models = [self.model_versions[v] for v in recent_versions] + [new_model]

        if hasattr(self.base_model, 'predict_proba'):
            ensemble = VotingClassifier(models, voting='soft')
        else:
            ensemble = VotingRegressor(models)

        return ensemble

    def _clone_model(self, model: Any) -> Any:
        """Clone a model for retraining."""
        try:
            return model.__class__(**model.get_params())
        except:
            # Fallback for models without get_params
            import copy
            return copy.deepcopy(model)

    def _evaluate_model(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Evaluate model performance."""
        try:
            y_pred = model.predict(X)

            if hasattr(model, 'predict_proba'):
                # Classification
                return {
                    'accuracy': accuracy_score(y, y_pred),
                    'f1_score': f1_score(y, y_pred, average='weighted')
                }
            else:
                # Regression
                return {
                    'mse': mean_squared_error(y, y_pred),
                    'mae': mean_absolute_error(y, y_pred),
                    'r2': r2_score(y, y_pred)
                }
        except Exception as e:
            warnings.warn(f"Model evaluation failed: {e}")
            return {}

    def get_best_model(self) -> Any:
        """Get the best performing model version."""
        if not self.model_versions:
            return self.base_model

        # Simple heuristic: return most recent model
        # Could be enhanced with proper model selection
        return self.model_versions[self.current_model_version]

    def get_retraining_summary(self) -> Dict[str, Any]:
        """Get summary of retraining history."""
        if not self.retraining_history:
            return {}

        strategies_used = [r['strategy'] for r in self.retraining_history]
        avg_training_time = np.mean([r['training_time'] for r in self.retraining_history])

        return {
            "total_retrains": len(self.retraining_history),
            "strategies_used": strategies_used,
            "avg_training_time": avg_training_time,
            "most_recent_version": self.current_model_version
        }


# =============================================================================
# COMPREHENSIVE MONITORING DASHBOARD
# =============================================================================

class ModelMonitoringDashboard:
    """Comprehensive model monitoring dashboard."""

    def __init__(
        self,
        model: Any,
        target_type: str = "regression",
        drift_detector: Optional[DriftDetector] = None,
        performance_monitor: Optional[ModelPerformanceMonitor] = None,
        retraining_manager: Optional[AdaptiveRetrainingManager] = None
    ):
        self.model = model
        self.target_type = target_type
        self.drift_detector = drift_detector or DriftDetector()
        self.performance_monitor = performance_monitor or ModelPerformanceMonitor(target_type=target_type)
        self.retraining_manager = retraining_manager

        self.monitoring_history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []

    def monitor_prediction(
        self,
        X: pd.DataFrame,
        y_true: Optional[Union[np.ndarray, pd.Series]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Monitor a prediction and update all monitoring components."""
        current_time = timestamp or datetime.utcnow()

        # Make prediction
        y_pred = self.model.predict(X)

        result = {
            "timestamp": current_time,
            "input_shape": X.shape,
            "prediction_shape": y_pred.shape if hasattr(y_pred, 'shape') else len(y_pred)
        }

        # Performance monitoring (if ground truth available)
        if y_true is not None:
            perf_metrics = self.performance_monitor.update(y_true, y_pred, current_time)
            result["performance"] = {
                k: v for k, v in perf_metrics.__dict__.items()
                if k != 'timestamp' and v is not None
            }

        # Drift detection (using prediction features as proxy)
        # This is a simplified approach - real drift detection would need reference data
        if hasattr(self, 'reference_predictions') and self.reference_predictions is not None:
            # Compare current predictions to reference
            drift_metrics = self.drift_detector.compute(
                pd.Series(self.reference_predictions),
                pd.Series(y_pred.flatten() if hasattr(y_pred, 'flatten') else y_pred)
            )
            result["drift"] = {
                k: v for k, v in drift_metrics.__dict__.items()
                if k != 'metadata' and v is not None
            }

        # Check for retraining needs
        if self.retraining_manager:
            retrain_needed, strategy = self.retraining_manager.should_retrain(
                drift_metrics=drift_metrics if 'drift_metrics' in locals() else None,
                performance_metrics=result.get("performance"),
                sample_size=len(X)
            )
            result["retraining_needed"] = retrain_needed
            result["retraining_strategy"] = strategy

            if retrain_needed:
                alert = {
                    "timestamp": current_time,
                    "type": "retraining_triggered",
                    "strategy": strategy,
                    "reason": "drift" if 'drift_metrics' in locals() and drift_metrics.drift_detected else "performance"
                }
                self.alerts.append(alert)

        # Store monitoring result
        self.monitoring_history.append(result)

        return result

    def get_dashboard_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive dashboard summary."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_history = [h for h in self.monitoring_history if h['timestamp'] >= cutoff]

        summary = {
            "monitoring_period_days": days,
            "total_predictions": len(recent_history),
            "alerts_count": len([a for a in self.alerts if a['timestamp'] >= cutoff])
        }

        # Performance summary
        if self.performance_monitor:
            perf_summary = self.performance_monitor.get_performance_summary(days)
            summary["performance"] = perf_summary

        # Drift summary
        if hasattr(self, 'drift_detector') and self.monitoring_history:
            drift_events = sum(1 for h in recent_history if h.get('drift', {}).get('drift_detected', False))
            summary["drift"] = {
                "drift_events": drift_events,
                "drift_rate": drift_events / max(len(recent_history), 1)
            }

        # Retraining summary
        if self.retraining_manager:
            retrain_summary = self.retraining_manager.get_retraining_summary()
            summary["retraining"] = retrain_summary

        return summary

    def generate_alert_report(self) -> List[Dict[str, Any]]:
        """Generate detailed alert report."""
        return self.alerts.copy()


__all__ = [
    "DriftDetector",
    "DriftMetrics",
    "DriftMonitor",
    "RetrainingSchedule",
    "ConceptDriftDetector",
    "AlibiDriftDetector",
    "PerformanceMetrics",
    "ModelPerformanceMonitor",
    "AdaptiveRetrainingManager",
    "ModelMonitoringDashboard",
]

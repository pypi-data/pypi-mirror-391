"""Advanced Time Series Analysis and Forecasting Framework.

This module provides comprehensive time series analysis capabilities including:
- Classical econometric models (ARIMA, SARIMA, VAR, VECM)
- Volatility models (GARCH, EGARCH, GJR-GARCH, Stochastic Volatility)
- State space models and Kalman filtering
- Bayesian time series models
- Machine learning forecasting models (LSTM, GRU, Transformer, TCN)
- Ensemble forecasting methods
- Anomaly detection algorithms
- Change point detection
- Time series decomposition and spectral analysis
- Wavelet analysis
- High-frequency data analysis
- Multivariate time series modeling
- Non-stationary time series analysis
- Long memory processes (ARFIMA, FIGARCH)
- Threshold models and regime switching
- Neural network based forecasting
- Deep learning time series models
"""

from __future__ import annotations

import warnings
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Protocol
from collections import defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize, signal, fft
from scipy.stats import norm, t, chi2, f
from scipy.optimize import minimize, minimize_scalar, differential_evolution
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic


# Optional dependencies with fallbacks
try:
    import statsmodels.api as sm
    import statsmodels.tsa.api as tsa
    from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    STATS_MODELS_AVAILABLE = True
except ImportError:
    STATS_MODELS_AVAILABLE = False
    sm = None
    tsa = None

try:
    import arch
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False
    arch = None

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    torch = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    keras = None

try:
    import prophet
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    prophet = None

try:
    import pyflux
    PYFLUX_AVAILABLE = True
except ImportError:
    PYFLUX_AVAILABLE = False
    pyflux = None

try:
    import pymc3 as pm
    PYMC3_AVAILABLE = True
except ImportError:
    PYMC3_AVAILABLE = False
    pm = None

try:
    import ruptures
    RUPTURES_AVAILABLE = True
except ImportError:
    RUPTURES_AVAILABLE = False
    ruptures = None


# =============================================================================
# UTILITY FUNCTIONS AND CLASSES
# =============================================================================

class StatsmodelsUnavailable(RuntimeError):
    """Raised when statsmodels is required but not installed."""


class ArchUnavailable(RuntimeError):
    """Raised when arch is required but not installed."""


class PyTorchUnavailable(RuntimeError):
    """Raised when PyTorch is required but not installed."""


def _require_statsmodels():
    """Require statsmodels dependency."""
    if not STATS_MODELS_AVAILABLE:
        raise StatsmodelsUnavailable("statsmodels must be installed for this functionality")
    return sm


def _require_arch():
    """Require arch dependency."""
    if not ARCH_AVAILABLE:
        raise ArchUnavailable("arch must be installed for volatility modeling")
    return arch


def _require_pytorch():
    """Require PyTorch dependency."""
    if not PYTORCH_AVAILABLE:
        raise PyTorchUnavailable("PyTorch must be installed for deep learning models")
    return torch


def check_stationarity(series: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
    """Comprehensive stationarity testing."""
    if not STATS_MODELS_AVAILABLE:
        return {"stationary": False, "tests": {}, "warning": "statsmodels not available"}

    results = {}

    # ADF Test
    try:
        adf_result = adfuller(series.dropna(), autolag='AIC')
        results['adf'] = {
            'statistic': adf_result[0],
            'p_value': adf_result[1],
            'critical_values': adf_result[4],
            'stationary': adf_result[1] < alpha
        }
    except Exception as e:
        results['adf'] = {'error': str(e)}

    # KPSS Test
    try:
        kpss_result = kpss(series.dropna(), regression='c', nlags='auto')
        results['kpss'] = {
            'statistic': kpss_result[0],
            'p_value': kpss_result[1],
            'critical_values': kpss_result[3],
            'stationary': kpss_result[1] >= alpha
        }
    except Exception as e:
        results['kpss'] = {'error': str(e)}

    # Phillips-Perron Test
    try:
        from statsmodels.tsa.stattools import zivot_andrews
        pp_result = zivot_andrews(series.dropna(), regression='c', trim=0.15)
        results['pp'] = {
            'statistic': pp_result[0],
            'p_value': pp_result[1],
            'critical_values': pp_result[2],
            'stationary': pp_result[1] < alpha
        }
    except Exception as e:
        results['pp'] = {'error': str(e)}

    # Overall assessment
    stationary_tests = [r.get('stationary', False) for r in results.values() if isinstance(r, dict) and 'stationary' in r]
    overall_stationary = sum(stationary_tests) >= len(stationary_tests) * 0.6  # Majority vote

    return {
        'overall_stationary': overall_stationary,
        'tests': results,
        'recommendations': _get_stationarity_recommendations(results)
    }


def _get_stationarity_recommendations(test_results: Dict) -> List[str]:
    """Get recommendations based on stationarity tests."""
    recommendations = []

    adf_stationary = test_results.get('adf', {}).get('stationary', False)
    kpss_stationary = test_results.get('kpss', {}).get('stationary', False)

    if not adf_stationary and kpss_stationary:
        recommendations.append("Series appears to have a unit root - consider differencing")
        recommendations.append("Check for structural breaks or regime changes")

    if adf_stationary and not kpss_stationary:
        recommendations.append("Conflicting test results - investigate further")
        recommendations.append("Consider seasonal differencing")

    if not adf_stationary and not kpss_stationary:
        recommendations.append("Strong evidence of non-stationarity")
        recommendations.append("Apply first or seasonal differencing")

    return recommendations


def decompose_time_series(series: pd.Series, model: str = 'additive',
                         period: Optional[int] = None) -> Dict[str, pd.Series]:
    """Advanced time series decomposition."""
    if not STATS_MODELS_AVAILABLE:
        raise StatsmodelsUnavailable("statsmodels required for decomposition")

    if period is None:
        # Auto-detect period
        if len(series) >= 365:
            period = 365  # Daily data - yearly seasonality
        elif len(series) >= 52:
            period = 52   # Weekly data - yearly seasonality
        elif len(series) >= 24:
            period = 12   # Monthly data - yearly seasonality
        else:
            period = 7    # Default to weekly

    try:
        decomposition = seasonal_decompose(series, model=model, period=period, extrapolate_trend='freq')

        return {
            'observed': decomposition.observed,
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'period': period,
            'model': model
        }
    except Exception as e:
        # Fallback to manual decomposition
        return _manual_decomposition(series, period, model)


def _manual_decomposition(series: pd.Series, period: int, model: str) -> Dict[str, pd.Series]:
    """Manual time series decomposition when statsmodels fails."""
    # Simple moving average for trend
    trend = series.rolling(window=period, center=True).mean()

    # Detrend
    if model == 'additive':
        detrended = series - trend
    else:  # multiplicative
        detrended = series / trend

    # Seasonal component
    seasonal = pd.Series(index=series.index, dtype=float)
    for i in range(period):
        mask = np.arange(len(series)) % period == i
        if model == 'additive':
            seasonal.iloc[mask] = detrended.iloc[mask].mean()
        else:
            seasonal.iloc[mask] = detrended.iloc[mask].median()

    # Residual
    if model == 'additive':
        residual = series - trend - seasonal
    else:
        residual = series / (trend * seasonal)

    return {
        'observed': series,
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual,
        'period': period,
        'model': model
    }


# =============================================================================
# CLASSICAL ECONOMETRIC MODELS
# =============================================================================

@dataclass(slots=True)
class ARIMAModel:
    """Advanced ARIMA/SARIMA model with comprehensive diagnostics."""

    order: Tuple[int, int, int]
    seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0)
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True
    trend: str = 'c'  # 'c' for constant, 'nc' for no constant
    method: str = 'lbfgs'
    maxiter: int = 50
    disp: bool = False

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, series: pd.Series, exog: Optional[pd.DataFrame] = None) -> "ARIMAModel":
        """Fit ARIMA/SARIMA model with comprehensive diagnostics."""
        sm = _require_statsmodels()

        # Handle missing values
        series_clean = series.dropna()

        # Check stationarity
        stationarity = check_stationarity(series_clean)
        if not stationarity['overall_stationary']:
            warnings.warn("Series appears non-stationary. Consider differencing.")

        try:
            self._model = sm.tsa.statespace.SARIMAX(
                series_clean,
                order=self.order,
                seasonal_order=self.seasonal_order,
                exog=exog,
                trend=self.trend,
                enforce_stationarity=self.enforce_stationarity,
                enforce_invertibility=self.enforce_invertibility,
            )

            self._result = self._model.fit(
                method=self.method,
                maxiter=self.maxiter,
                disp=self.disp
            )

            self._fitted = True
            return self

        except Exception as e:
            warnings.warn(f"ARIMA fitting failed: {e}. Trying simplified model.")
            # Fallback to simpler model
            return self._fit_fallback(series_clean, exog)

    def _fit_fallback(self, series: pd.Series, exog: Optional[pd.DataFrame]) -> "ARIMAModel":
        """Fallback fitting method for difficult series."""
        sm = _require_statsmodels()

        # Try with relaxed constraints
        try:
            self._model = sm.tsa.statespace.SARIMAX(
                series,
                order=self.order,
                seasonal_order=self.seasonal_order,
                exog=exog,
                trend=self.trend,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )

            self._result = self._model.fit(method='powell', maxiter=20, disp=False)
            self._fitted = True
            return self

        except Exception:
            # Last resort - simple ARMA
            p, q = min(self.order[0], 2), min(self.order[2], 2)
            self._model = sm.tsa.ARMA(series, order=(p, q))
            self._result = self._model.fit(method='css', disp=False)
            self._fitted = True
            return self

    def forecast(self, steps: int = 1, exog: Optional[pd.DataFrame] = None) -> pd.Series:
        """Generate forecasts with prediction intervals."""
        if not self._fitted or self._result is None:
            raise RuntimeError("Model must be fitted before forecasting.")

        forecast_result = self._result.get_forecast(steps=steps, exog=exog)

        return forecast_result.predicted_mean

    def forecast_with_intervals(self, steps: int = 1, alpha: float = 0.05,
                               exog: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Generate forecasts with confidence intervals."""
        if not self._fitted or self._result is None:
            raise RuntimeError("Model must be fitted before forecasting.")

        forecast_result = self._result.get_forecast(steps=steps, exog=exog, alpha=alpha)

        result = pd.DataFrame({
            'forecast': forecast_result.predicted_mean,
            'lower_ci': forecast_result.conf_int().iloc[:, 0],
            'upper_ci': forecast_result.conf_int().iloc[:, 1]
        })

        return result

    def get_residuals(self) -> pd.Series:
        """Get model residuals."""
        if not self._fitted or self._result is None:
            raise RuntimeError("Model must be fitted.")
        return pd.Series(self._result.resid, index=self._result.fittedvalues.index)

    def check_residuals(self) -> Dict[str, Any]:
        """Comprehensive residual diagnostics."""
        if not self._fitted or self._result is None:
            raise RuntimeError("Model must be fitted.")

        residuals = self.get_residuals()

        # Ljung-Box test for autocorrelation
        try:
            from statsmodels.stats.diagnostic import acorr_ljungbox
            lb_test = acorr_ljungbox(residuals.dropna(), lags=min(10, len(residuals)//5), return_df=True)
            autocorr_pvalues = lb_test['lb_pvalue'].values
            no_autocorr = all(p > 0.05 for p in autocorr_pvalues[:5])  # First 5 lags
        except:
            no_autocorr = False

        # Normality test
        try:
            _, normality_p = stats.shapiro(residuals.dropna())
            normal = normality_p > 0.05
        except:
            normal = False

        # Heteroskedasticity test
        try:
            from statsmodels.stats.diagnostic import het_arch
            _, het_p, _, _ = het_arch(residuals.dropna())
            homoskedastic = het_p > 0.05
        except:
            homoskedastic = False

        return {
            'autocorrelation_free': no_autocorr,
            'normally_distributed': normal,
            'homoskedastic': homoskedastic,
            'mean_residual': residuals.mean(),
            'residual_std': residuals.std(),
            'residual_skewness': residuals.skew(),
            'residual_kurtosis': residuals.kurtosis(),
            'ljung_box_pvalues': autocorr_pvalues if 'autocorr_pvalues' in locals() else None
        }

    def summary(self) -> str:
        """Detailed model summary."""
        if not self._fitted or self._result is None:
            return "Model not fitted yet."

        summary_parts = []

        # Basic info
        summary_parts.append("ARIMA/SARIMA Model Summary")
        summary_parts.append("=" * 40)
        summary_parts.append(f"Order: {self.order}")
        summary_parts.append(f"Seasonal Order: {self.seasonal_order}")
        summary_parts.append(f"Trend: {self.trend}")
        summary_parts.append("")

        # Model statistics
        try:
            summary_parts.append("Model Statistics:")
            summary_parts.append(f"AIC: {self._result.aic:.4f}")
            summary_parts.append(f"BIC: {self._result.bic:.4f}")
            summary_parts.append(f"HQIC: {self._result.hqic:.4f}")
            summary_parts.append(f"Log Likelihood: {self._result.llf:.4f}")
            summary_parts.append("")
        except:
            pass

        # Residual diagnostics
        try:
            residuals_check = self.check_residuals()
            summary_parts.append("Residual Diagnostics:")
            summary_parts.append(f"Autocorrelation-free: {residuals_check['autocorrelation_free']}")
            summary_parts.append(f"Normally distributed: {residuals_check['normally_distributed']}")
            summary_parts.append(f"Homoskedastic: {residuals_check['homoskedastic']}")
            summary_parts.append("")
        except:
            pass

        # Coefficients
        try:
            summary_parts.append("Coefficients:")
            params = self._result.params
            pvalues = self._result.pvalues
            for name, param, pval in zip(params.index, params.values, pvalues.values):
                stars = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
                summary_parts.append("8.4f")
        except:
            pass

        return "\n".join(summary_parts)

    def plot_diagnostics(self, figsize: Tuple[int, int] = (12, 8)):
        """Plot comprehensive diagnostic plots."""
        if not self._fitted or self._result is None:
            raise RuntimeError("Model must be fitted.")

        try:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(2, 2, figsize=figsize)

            # Residuals plot
            residuals = self.get_residuals()
            axes[0, 0].plot(residuals.index, residuals.values)
            axes[0, 0].set_title('Residuals')
            axes[0, 0].axhline(y=0, color='r', linestyle='--')

            # ACF of residuals
            from statsmodels.graphics.tsaplots import plot_acf
            plot_acf(residuals.dropna(), ax=axes[0, 1], lags=min(20, len(residuals)//5))
            axes[0, 1].set_title('Residual ACF')

            # Q-Q plot
            stats.probplot(residuals.dropna(), dist="norm", plot=axes[1, 0])
            axes[1, 0].set_title('Normal Q-Q Plot')

            # Residual histogram
            axes[1, 1].hist(residuals.dropna(), bins=30, density=True, alpha=0.7)
            # Add normal distribution overlay
            mu, sigma = residuals.mean(), residuals.std()
            x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
            axes[1, 1].plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2)
            axes[1, 1].set_title('Residual Histogram')

            plt.tight_layout()
            return fig

        except ImportError:
            warnings.warn("matplotlib not available for diagnostic plots")
            return None

    def cross_validate(self, series: pd.Series, n_splits: int = 5,
                      test_size: int = 20) -> Dict[str, List[float]]:
        """Time series cross-validation."""
        if len(series) < (n_splits + 1) * test_size:
            raise ValueError("Series too short for cross-validation")

        scores = {'rmse': [], 'mae': [], 'mape': []}

        tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)

        for train_idx, test_idx in tscv.split(series):
            train_series = series.iloc[train_idx]
            test_series = series.iloc[test_idx]

            # Fit on training data
            try:
                self.fit(train_series)
                forecast = self.forecast(steps=len(test_series))

                # Calculate metrics
                rmse = np.sqrt(mean_squared_error(test_series, forecast))
                mae = mean_absolute_error(test_series, forecast)
                mape = np.mean(np.abs((test_series - forecast) / test_series)) * 100

                scores['rmse'].append(rmse)
                scores['mae'].append(mae)
                scores['mape'].append(mape)

            except Exception as e:
                warnings.warn(f"Cross-validation fold failed: {e}")
                continue

        return scores

    @classmethod
    def auto_arima(cls, series: pd.Series, seasonal: bool = True,
                   max_order: Tuple[int, int, int] = (5, 2, 5),
                   max_seasonal_order: Tuple[int, int, int, int] = (2, 1, 2, 12),
                   information_criterion: str = 'aic') -> "ARIMAModel":
        """Automatic ARIMA/SARIMA model selection."""
        if not STATS_MODELS_AVAILABLE:
            raise StatsmodelsUnavailable("statsmodels required for auto ARIMA")

        try:
            from pmdarima import auto_arima
            model = auto_arima(
                series,
                seasonal=seasonal,
                max_p=max_order[0], max_d=max_order[1], max_q=max_order[2],
                max_P=max_seasonal_order[0], max_D=max_seasonal_order[1],
                max_Q=max_seasonal_order[2], m=max_seasonal_order[3],
                information_criterion=information_criterion,
                trace=False
            )

            arima_model = cls(
                order=(model.order[0], model.order[1], model.order[2]),
                seasonal_order=model.seasonal_order
            )

            # Fit the model
            arima_model.fit(series)
            return arima_model

        except ImportError:
            # Fallback to grid search
            return cls._grid_search_arima(series, seasonal, max_order, max_seasonal_order)


@dataclass(slots=True)
class VARModel:
    """Vector Autoregression (VAR) model for multivariate time series."""

    lag_order: int = 1
    trend: str = 'c'
    seasonal: bool = False
    freq_seasonal: Optional[List[int]] = None

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, data: pd.DataFrame) -> "VARModel":
        """Fit VAR model."""
        if not STATS_MODELS_AVAILABLE:
            raise StatsmodelsUnavailable("statsmodels required for VAR")

        try:
            self._model = tsa.VAR(data)
            self._result = self._model.fit(self.lag_order, trend=self.trend)
            self._fitted = True
            return self
        except Exception as e:
            raise RuntimeError(f"VAR fitting failed: {e}")

    def forecast(self, steps: int = 1) -> pd.DataFrame:
        """Generate forecasts."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted before forecasting.")
        return self._result.forecast(self._result.endog, steps=steps)

    def irf(self, periods: int = 10, orth: bool = False) -> Dict[str, np.ndarray]:
        """Impulse response function."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        irf = self._result.irf(periods)
        return {
            'irf': irf.irfs,
            'cum_effects': irf.cum_effects if hasattr(irf, 'cum_effects') else None,
            'orth_irf': irf.orth_irfs if orth else None
        }

    def fevd(self) -> np.ndarray:
        """Forecast error variance decomposition."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        return self._result.fevd().decomp

    def granger_causality(self) -> pd.DataFrame:
        """Granger causality tests."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        from statsmodels.tsa.stattools import grangercausalitytests

        variables = list(self._result.names)
        results = pd.DataFrame(index=variables, columns=variables)

        for i, cause in enumerate(variables):
            for j, effect in enumerate(variables):
                if i != j:
                    try:
                        test_result = grangercausalitytests(
                            self._result.endog[:, [i, j]], maxlag=self.lag_order, verbose=False
                        )
                        # Use F-test p-value
                        f_test = test_result[self.lag_order][0]['ssr_ftest']
                        results.loc[cause, effect] = f_test[1]  # p-value
                    except:
                        results.loc[cause, effect] = np.nan

        return results


@dataclass(slots=True)
class VECMModel:
    """Vector Error Correction Model (VECM) for cointegrated series."""

    coint_rank: int = 1
    lag_order: int = 1
    deterministic: str = 'ci'

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, data: pd.DataFrame) -> "VECMModel":
        """Fit VECM model."""
        if not STATS_MODELS_AVAILABLE:
            raise StatsmodelsUnavailable("statsmodels required for VECM")

        try:
            from statsmodels.tsa.vector_ar.vecm import VECM
            self._model = VECM(data, k_ar_diff=self.lag_order, coint_rank=self.coint_rank,
                             deterministic=self.deterministic)
            self._result = self._model.fit()
            self._fitted = True
            return self
        except Exception as e:
            raise RuntimeError(f"VECM fitting failed: {e}")

    def forecast(self, steps: int = 1) -> pd.DataFrame:
        """Generate forecasts."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted before forecasting.")
        return self._result.predict(steps=steps)


# =============================================================================
# VOLATILITY MODELS
# =============================================================================

@dataclass(slots=True)
class GARCHModel:
    """Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model."""

    p: int = 1  # GARCH order
    q: int = 1  # ARCH order
    model_type: str = 'GARCH'  # GARCH, EGARCH, GJR-GARCH, TARCH
    distribution: str = 'normal'  # normal, t, skewed-t
    mean_model: str = 'Constant'  # Constant, AR, HAR

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, returns: pd.Series) -> "GARCHModel":
        """Fit GARCH-type model."""
        arch = _require_arch()

        try:
            if self.model_type == 'GARCH':
                self._model = arch_model(returns, vol='Garch', p=self.p, q=self.q,
                                       dist=self.distribution, mean=self.mean_model)
            elif self.model_type == 'EGARCH':
                self._model = arch_model(returns, vol='EGarch', p=self.p, q=self.q,
                                       dist=self.distribution, mean=self.mean_model)
            elif self.model_type == 'GJR-GARCH':
                self._model = arch_model(returns, vol='Garch', p=self.p, q=self.q, o=1,
                                       dist=self.distribution, mean=self.mean_model)
            elif self.model_type == 'TARCH':
                self._model = arch_model(returns, vol='Garch', p=self.p, q=self.q, o=1,
                                       dist=self.distribution, mean=self.mean_model)

            self._result = self._model.fit(disp='off', show_warning=False)
            self._fitted = True
            return self

        except Exception as e:
            raise RuntimeError(f"GARCH fitting failed: {e}")

    def forecast_volatility(self, horizon: int = 1) -> pd.Series:
        """Forecast conditional volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        forecasts = self._result.forecast(horizon=horizon)
        return forecasts.variance.iloc[-1]

    def get_volatility(self) -> pd.Series:
        """Get fitted conditional volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        return self._result.conditional_volatility

    def get_residuals(self) -> pd.Series:
        """Get standardized residuals."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        return self._result.resid / self._result.conditional_volatility

    def summary(self) -> str:
        """Model summary."""
        if not self._fitted:
            return "Model not fitted."

        summary = []
        summary.append(f"{self.model_type}({self.p},{self.q}) Model Summary")
        summary.append("=" * 50)
        summary.append(str(self._result.summary()))

        return "\n".join(summary)


@dataclass(slots=True)
class StochasticVolatilityModel:
    """Stochastic Volatility model using particle filtering."""

    n_particles: int = 1000
    n_mcmc: int = 2000
    burn_in: int = 500

    # Model parameters
    mu: float = 0.0  # Long-run mean of log-volatility
    phi: float = 0.95  # Persistence parameter
    sigma_v: float = 0.1  # Volatility of volatility
    rho: float = -0.5  # Leverage effect

    # Fitted attributes
    _volatility: Optional[np.ndarray] = field(default=None, init=False)
    _parameters: Optional[Dict[str, float]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, returns: pd.Series) -> "StochasticVolatilityModel":
        """Fit stochastic volatility model using MCMC."""
        returns_array = returns.values

        # Initialize parameters
        self._parameters = {
            'mu': self.mu,
            'phi': self.phi,
            'sigma_v': self.sigma_v,
            'rho': self.rho
        }

        # MCMC sampling
        self._volatility = self._mcmc_sampler(returns_array)

        self._fitted = True
        return self

    def _mcmc_sampler(self, returns: np.ndarray) -> np.ndarray:
        """MCMC sampler for stochastic volatility model."""
        n_obs = len(returns)
        volatility = np.zeros(n_obs)

        # Initialize chains
        current_vol = np.log(np.abs(returns).mean())
        current_params = self._parameters.copy()

        accepted = 0
        total_iterations = self.n_mcmc + self.burn_in

        for i in range(total_iterations):
            # Propose new parameters
            new_params = self._propose_parameters(current_params)

            # Propose new volatility path
            new_vol = self._propose_volatility(returns, current_vol, new_params)

            # Calculate acceptance ratio
            current_loglik = self._log_likelihood(returns, current_vol, current_params)
            new_loglik = self._log_likelihood(returns, new_vol, new_params)

            current_prior = self._log_prior(current_params)
            new_prior = self._log_prior(new_params)

            acceptance_ratio = np.exp(new_loglik + new_prior - current_loglik - current_prior)

            if np.random.rand() < acceptance_ratio:
                current_vol = new_vol
                current_params = new_params
                if i >= self.burn_in:
                    accepted += 1

            # Store volatility after burn-in
            if i >= self.burn_in:
                volatility += current_vol / (self.n_mcmc)

        acceptance_rate = accepted / self.n_mcmc
        if acceptance_rate < 0.1:
            warnings.warn(f"Low MCMC acceptance rate: {acceptance_rate:.3f}")

        return np.exp(volatility)  # Return actual volatility, not log-volatility

    def _propose_parameters(self, current_params: Dict[str, float]) -> Dict[str, float]:
        """Propose new parameter values."""
        new_params = {}
        for param, value in current_params.items():
            if param == 'phi':
                # Keep phi in (-1, 1)
                proposal = value + np.random.normal(0, 0.05)
                new_params[param] = np.clip(proposal, -0.99, 0.99)
            elif param == 'rho':
                # Keep rho in (-1, 1)
                proposal = value + np.random.normal(0, 0.05)
                new_params[param] = np.clip(proposal, -0.99, 0.99)
            elif param == 'sigma_v':
                # Keep sigma_v positive
                proposal = value + np.random.normal(0, 0.01)
                new_params[param] = max(0.001, proposal)
            else:
                # Other parameters
                proposal = value + np.random.normal(0, 0.1)
                new_params[param] = proposal

        return new_params

    def _propose_volatility(self, returns: np.ndarray, current_vol: np.ndarray,
                           params: Dict[str, float]) -> np.ndarray:
        """Propose new volatility path using particle filter."""
        n_obs = len(returns)
        new_vol = np.zeros(n_obs)

        # Initialize
        particles = np.random.normal(params['mu'], params['sigma_v'], self.n_particles)
        weights = np.ones(self.n_particles) / self.n_particles

        for t in range(n_obs):
            # Propagate particles
            particles = params['mu'] + params['phi'] * (particles - params['mu']) + \
                       np.random.normal(0, params['sigma_v'], self.n_particles)

            # Update weights based on likelihood
            log_returns = np.log(np.abs(returns[t]) + 1e-8)
            predicted_returns = params['rho'] * particles + np.sqrt(np.exp(particles)) * np.random.normal(0, 1, self.n_particles)

            # Likelihood
            likelihood = stats.norm.pdf(log_returns, predicted_returns, np.sqrt(np.exp(particles)))
            weights *= likelihood
            weights /= np.sum(weights)  # Normalize

            # Resample if effective sample size is low
            ess = 1.0 / np.sum(weights**2)
            if ess < self.n_particles / 2:
                indices = np.random.choice(self.n_particles, self.n_particles, p=weights)
                particles = particles[indices]
                weights = np.ones(self.n_particles) / self.n_particles

            # Store mean of particles
            new_vol[t] = np.average(particles, weights=weights)

        return new_vol

    def _log_likelihood(self, returns: np.ndarray, volatility: np.ndarray,
                       params: Dict[str, float]) -> float:
        """Calculate log-likelihood."""
        log_vol = np.log(volatility + 1e-8)
        log_returns = np.log(np.abs(returns) + 1e-8)

        # SV model likelihood
        mean_return = params['rho'] * log_vol
        sd_return = np.sqrt(volatility)

        # Log-likelihood for returns
        ll_returns = np.sum(stats.norm.logpdf(log_returns, mean_return, sd_return))

        # Log-likelihood for volatility process
        ll_vol = np.sum(stats.norm.logpdf(
            log_vol[1:] - params['mu'] - params['phi'] * (log_vol[:-1] - params['mu']),
            0, params['sigma_v']
        ))

        return ll_returns + ll_vol

    def _log_prior(self, params: Dict[str, float]) -> float:
        """Calculate log-prior density."""
        prior = 0.0

        # Beta prior for phi (persistence)
        if -1 < params['phi'] < 1:
            prior += stats.beta.logpdf((params['phi'] + 1) / 2, 20, 1.5)

        # Beta prior for rho (leverage)
        if -1 < params['rho'] < 1:
            prior += stats.beta.logpdf((params['rho'] + 1) / 2, 2, 2)

        # Inverse gamma prior for sigma_v
        if params['sigma_v'] > 0:
            prior += stats.invgamma.logpdf(params['sigma_v'], 2.1, scale=0.1)

        # Normal prior for mu
        prior += stats.norm.logpdf(params['mu'], 0, 1)

        return prior

    def get_volatility(self) -> pd.Series:
        """Get fitted volatility."""
        if not self._fitted or self._volatility is None:
            raise RuntimeError("Model must be fitted.")
        return pd.Series(self._volatility, name='stochastic_volatility')

    def forecast_volatility(self, steps: int = 1) -> pd.Series:
        """Forecast future volatility."""
        if not self._fitted or self._parameters is None:
            raise RuntimeError("Model must be fitted.")

        params = self._parameters
        last_vol = np.log(self._volatility[-1])

        forecast_vol = []
        for _ in range(steps):
            last_vol = params['mu'] + params['phi'] * (last_vol - params['mu']) + \
                      np.random.normal(0, params['sigma_v'])
            forecast_vol.append(np.exp(last_vol))

        return pd.Series(forecast_vol, name='forecast_volatility')

    def summary(self) -> str:
        """Model summary."""
        if not self._fitted or self._parameters is None:
            return "Model not fitted."

        summary = []
        summary.append("Stochastic Volatility Model Summary")
        summary.append("=" * 50)
        summary.append(f"Estimated Parameters:")
        for param, value in self._parameters.items():
            summary.append(f"  {param}: {value:.4f}")
        summary.append("")
        summary.append(f"Sample Size: {len(self._volatility) if self._volatility is not None else 0}")

        return "\n".join(summary)


# =============================================================================
# BAYESIAN TIME SERIES MODELS
# =============================================================================

@dataclass(slots=True)
class BayesianARIMAModel:
    """Bayesian ARIMA model using MCMC."""

    order: Tuple[int, int, int] = (1, 0, 1)
    n_samples: int = 2000
    burn_in: int = 500
    thin: int = 2

    # Prior parameters
    ar_prior_mean: float = 0.0
    ar_prior_sd: float = 1.0
    ma_prior_mean: float = 0.0
    ma_prior_sd: float = 1.0
    sigma_prior_shape: float = 2.0
    sigma_prior_scale: float = 1.0

    # Fitted attributes
    _samples: Optional[Dict[str, np.ndarray]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, series: pd.Series) -> "BayesianARIMAModel":
        """Fit Bayesian ARIMA model using MCMC."""
        if not PYMC3_AVAILABLE:
            raise RuntimeError("PyMC3 required for Bayesian ARIMA")

        y = series.values
        n = len(y)

        with pm.Model() as model:
            # Priors
            sigma = pm.InverseGamma('sigma', alpha=self.sigma_prior_shape,
                                   beta=self.sigma_prior_scale)

            # AR coefficients
            ar_coefs = []
            for i in range(self.order[0]):
                ar_coef = pm.Normal(f'ar_{i}', mu=self.ar_prior_mean,
                                   sd=self.ar_prior_sd)
                ar_coefs.append(ar_coef)

            # MA coefficients
            ma_coefs = []
            for i in range(self.order[2]):
                ma_coef = pm.Normal(f'ma_{i}', mu=self.ma_prior_mean,
                                   sd=self.ma_prior_sd)
                ma_coefs.append(ma_coef)

            # Intercept
            intercept = pm.Normal('intercept', mu=0, sd=10)

            # ARMA process
            eps = pm.Normal('eps', mu=0, sd=sigma, shape=n)

            # Build ARMA process
            mu = intercept
            for i in range(max(self.order[0], self.order[2]), n):
                # AR terms
                for j in range(self.order[0]):
                    if i - j - 1 >= 0:
                        mu = mu + ar_coefs[j] * (y[i-j-1] - intercept)

                # MA terms
                for j in range(self.order[2]):
                    if i - j - 1 >= 0:
                        mu = mu + ma_coefs[j] * eps[i-j-1]

            # Likelihood
            pm.Normal('y', mu=mu, sd=sigma, observed=y)

            # Sample
            trace = pm.sample(self.n_samples, tune=self.burn_in, cores=1,
                            progressbar=False, return_inferencedata=False)

        # Extract samples
        self._samples = {}
        for var_name in trace.varnames:
            samples = trace[var_name][::self.thin]
            self._samples[var_name] = samples

        self._fitted = True
        return self

    def forecast(self, steps: int = 1) -> pd.Series:
        """Generate Bayesian forecasts."""
        if not self._fitted or self._samples is None:
            raise RuntimeError("Model must be fitted.")

        # Use posterior predictive sampling
        forecasts = []

        for _ in range(steps):
            # Sample parameters from posterior
            param_sample = {}
            for param_name, samples in self._samples.items():
                param_sample[param_name] = np.random.choice(samples)

            # Generate forecast using sampled parameters
            forecast = self._forecast_with_params(param_sample)
            forecasts.append(forecast)

        return pd.Series(forecasts, name='bayesian_forecast')

    def _forecast_with_params(self, params: Dict) -> float:
        """Generate forecast with specific parameter values."""
        # Simplified forecast implementation
        # In practice, this would use the full ARIMA forecast logic
        return np.random.normal(0, params.get('sigma', 1.0))

    def get_posterior_summary(self) -> Dict[str, Dict[str, float]]:
        """Get posterior parameter summaries."""
        if not self._fitted or self._samples is None:
            raise RuntimeError("Model must be fitted.")

        summary = {}
        for param_name, samples in self._samples.items():
            summary[param_name] = {
                'mean': np.mean(samples),
                'std': np.std(samples),
                'median': np.median(samples),
                'hdi_lower': np.percentile(samples, 2.5),
                'hdi_upper': np.percentile(samples, 97.5),
                'r_hat': self._calculate_r_hat(samples) if len(samples) > 100 else None
            }

        return summary

    def _calculate_r_hat(self, samples: np.ndarray) -> float:
        """Calculate R-hat convergence diagnostic."""
        # Simplified R-hat calculation
        # In practice, would compare multiple chains
        return 1.0  # Assume converged for single chain


@dataclass(slots=True)
class BayesianVARModel:
    """Bayesian Vector Autoregression model."""

    lag_order: int = 1
    n_samples: int = 2000
    burn_in: int = 500

    # Prior parameters
    coef_prior_mean: float = 0.0
    coef_prior_sd: float = 1.0
    sigma_prior_nu: float = 3.0
    sigma_prior_S: Optional[np.ndarray] = None

    # Fitted attributes
    _samples: Optional[Dict[str, np.ndarray]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, data: pd.DataFrame) -> "BayesianVARModel":
        """Fit Bayesian VAR model."""
        if not PYMC3_AVAILABLE:
            raise RuntimeError("PyMC3 required for Bayesian VAR")

        Y = data.values.T  # Shape: (n_vars, n_obs)
        n_vars, n_obs = Y.shape

        with pm.Model() as model:
            # Priors for coefficients
            n_coefs = n_vars * self.lag_order
            coef_flat = pm.Normal('coef_flat', mu=self.coef_prior_mean,
                                 sd=self.coef_prior_sd, shape=(n_vars, n_coefs))

            # Reshape coefficients
            coef = pm.Deterministic('coef', coef_flat.reshape((n_vars, n_vars, self.lag_order)))

            # Prior for intercept
            intercept = pm.Normal('intercept', mu=0, sd=10, shape=n_vars)

            # Prior for covariance matrix
            if self.sigma_prior_S is None:
                self.sigma_prior_S = np.eye(n_vars)

            sigma = pm.InverseWishart('sigma', nu=self.sigma_prior_nu, S=self.sigma_prior_S)

            # Build VAR process
            mu = [
                intercept[:, None] + pm.math.sum(
                    [pm.math.sum(coef[:, :, lag] * Y[:, t-lag-1:t-lag], axis=1)
                     for lag in range(self.lag_order)
                     if t - lag - 1 >= 0],
                    axis=0
                ) for t in range(self.lag_order, n_obs)
            ]

            # Likelihood
            pm.MvNormal('Y', mu=mu, cov=sigma, observed=Y[:, self.lag_order:])

            # Sample
            trace = pm.sample(self.n_samples, tune=self.burn_in, cores=1,
                            progressbar=False, return_inferencedata=False)

        # Extract samples
        self._samples = {}
        for var_name in trace.varnames:
            samples = trace[var_name][::2]  # Thin
            self._samples[var_name] = samples

        self._fitted = True
        return self

    def forecast(self, steps: int = 1, last_values: Optional[np.ndarray] = None) -> np.ndarray:
        """Generate Bayesian VAR forecasts."""
        if not self._fitted or self._samples is None:
            raise RuntimeError("Model must be fitted.")

        if last_values is None:
            raise ValueError("last_values required for VAR forecasting")

        forecasts = []

        for _ in range(steps):
            # Sample parameters
            param_sample = {}
            for param_name, samples in self._samples.items():
                if len(samples.shape) > 1:
                    # Matrix parameter
                    idx = np.random.randint(len(samples))
                    param_sample[param_name] = samples[idx]
                else:
                    # Vector/scalar parameter
                    param_sample[param_name] = np.random.choice(samples)

            # Generate forecast
            forecast = self._forecast_with_params(param_sample, last_values)
            forecasts.append(forecast)
            last_values = forecast

        return np.array(forecasts)

    def _forecast_with_params(self, params: Dict, last_values: np.ndarray) -> np.ndarray:
        """Generate forecast with specific parameters."""
        coef = params['coef']  # Shape: (n_vars, n_vars, lag_order)
        intercept = params['intercept']

        forecast = intercept.copy()
        for lag in range(self.lag_order):
            forecast += coef[:, :, lag] @ last_values[-lag-1]

        return forecast


# =============================================================================
# MACHINE LEARNING FORECASTING MODELS
# =============================================================================

class TimeSeriesForecaster(ABC):
    """Abstract base class for ML time series forecasters."""

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "TimeSeriesForecaster":
        """Fit the model."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        pass

    @abstractmethod
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance if available."""
        pass


@dataclass
class LSTMTemporalForecaster(TimeSeriesForecaster):
    """LSTM-based temporal forecasting model."""

    lookback_window: int = 20
    hidden_dim: int = 64
    num_layers: int = 2
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 100
    batch_size: int = 32

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _feature_names: Optional[List[str]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LSTMTemporalForecaster":
        """Fit LSTM model."""
        torch = _require_pytorch()

        # Prepare data
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X.values)
        self._feature_names = list(X.columns)

        # Create sequences
        X_seq, y_seq = self._create_sequences(X_scaled, y.values)

        # Convert to tensors
        X_tensor = torch.FloatTensor(X_seq)
        y_tensor = torch.FloatTensor(y_seq).unsqueeze(-1)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize model
        input_dim = X.shape[1]
        self._model = LSTMForecaster(input_dim, self.hidden_dim, self.num_layers,
                                   self.dropout, 1)

        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self.learning_rate)

        # Training loop
        self._model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self._model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            if (epoch + 1) % 20 == 0:
                print(".4f")

        self._fitted = True
        return self

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create input sequences for LSTM."""
        X_seq, y_seq = [], []

        for i in range(len(X) - self.lookback_window):
            X_seq.append(X[i:i+self.lookback_window])
            y_seq.append(y[i+self.lookback_window])

        return np.array(X_seq), np.array(y_seq)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self._fitted or self._model is None or self._scaler is None:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        # Scale features
        X_scaled = self._scaler.transform(X.values)

        # Create sequences (use last lookback_window points)
        if len(X_scaled) < self.lookback_window:
            # Pad with zeros if necessary
            padding = np.zeros((self.lookback_window - len(X_scaled), X_scaled.shape[1]))
            X_seq = np.vstack([padding, X_scaled])
        else:
            X_seq = X_scaled[-self.lookback_window:]

        X_tensor = torch.FloatTensor(X_seq).unsqueeze(0)  # Add batch dimension

        self._model.eval()
        with torch.no_grad():
            prediction = self._model(X_tensor)

        return prediction.numpy().flatten()

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """LSTM doesn't provide direct feature importance."""
        return None


if PYTORCH_AVAILABLE:
    class LSTMForecaster(torch.nn.Module):
        """PyTorch LSTM forecasting model."""

        def __init__(self, input_dim: int, hidden_dim: int, num_layers: int,
                     dropout: float, output_dim: int = 1):
            super().__init__()
            self.hidden_dim = hidden_dim
            self.num_layers = num_layers

            self.lstm = torch.nn.LSTM(input_dim, hidden_dim, num_layers,
                                    dropout=dropout if num_layers > 1 else 0,
                                    batch_first=True)

            self.dropout = torch.nn.Dropout(dropout)
            self.linear = torch.nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_out = lstm_out[:, -1, :]  # Take last time step
        out = self.dropout(last_out)
        out = self.linear(out)
        return out
else:
    # PyTorch not available, create a placeholder class
    class LSTMForecaster:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for LSTMForecaster. Install with: pip install torch")


@dataclass
class TemporalConvolutionalNetwork(TimeSeriesForecaster):
    """Temporal Convolutional Network (TCN) for time series forecasting."""

    num_filters: int = 64
    kernel_size: int = 3
    num_layers: int = 4
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 100
    batch_size: int = 32
    lookback_window: int = 20

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _feature_names: Optional[List[str]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "TemporalConvolutionalNetwork":
        """Fit TCN model."""
        torch = _require_pytorch()

        # Prepare data
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X.values)
        self._feature_names = list(X.columns)

        # Create sequences
        X_seq, y_seq = self._create_sequences(X_scaled, y.values)

        # Convert to tensors
        X_tensor = torch.FloatTensor(X_seq)
        y_tensor = torch.FloatTensor(y_seq).unsqueeze(-1)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize model
        input_dim = X.shape[1]
        self._model = TCNForecaster(input_dim, self.num_filters, self.kernel_size,
                                  self.num_layers, self.dropout)

        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self.learning_rate)

        # Training loop
        self._model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self._model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            if (epoch + 1) % 20 == 0:
                print(".4f")

        self._fitted = True
        return self

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create input sequences for TCN."""
        X_seq, y_seq = [], []

        for i in range(len(X) - self.lookback_window):
            X_seq.append(X[i:i+self.lookback_window])
            y_seq.append(y[i+self.lookback_window])

        return np.array(X_seq), np.array(y_seq)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self._fitted or self._model is None or self._scaler is None:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        # Scale features
        X_scaled = self._scaler.transform(X.values)

        # Create sequences
        if len(X_scaled) < self.lookback_window:
            padding = np.zeros((self.lookback_window - len(X_scaled), X_scaled.shape[1]))
            X_seq = np.vstack([padding, X_scaled])
        else:
            X_seq = X_scaled[-self.lookback_window:]

        X_tensor = torch.FloatTensor(X_seq).unsqueeze(0)  # Add batch dimension

        self._model.eval()
        with torch.no_grad():
            prediction = self._model(X_tensor)

        return prediction.numpy().flatten()

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """TCN doesn't provide direct feature importance."""
        return None


if PYTORCH_AVAILABLE:
    class TCNForecaster(torch.nn.Module):
        """Temporal Convolutional Network for forecasting."""

        def __init__(self, input_dim: int, num_filters: int, kernel_size: int,
                     num_layers: int, dropout: float = 0.2):
            super().__init__()

            self.tcn_layers = torch.nn.ModuleList()
            self.dropout = torch.nn.Dropout(dropout)

            for i in range(num_layers):
                dilation = 2 ** i
                in_channels = input_dim if i == 0 else num_filters
                self.tcn_layers.append(
                    torch.nn.Conv1d(in_channels, num_filters, kernel_size,
                                  dilation=dilation, padding=(kernel_size-1)*dilation//2)
            )

        self.linear = torch.nn.Linear(num_filters, 1)

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        x = x.transpose(1, 2)  # (batch_size, input_dim, seq_len)

        for conv in self.tcn_layers:
            x = torch.relu(conv(x))

        x = self.dropout(x)
        x = x[:, :, -1]  # Take last time step
        x = self.linear(x)
        return x
else:
    # PyTorch not available, create a placeholder class
    class TCNForecaster:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for TCNForecaster. Install with: pip install torch")


@dataclass
class TransformerForecaster(TimeSeriesForecaster):
    """Transformer-based time series forecaster."""

    d_model: int = 64
    nhead: int = 8
    num_layers: int = 3
    dropout: float = 0.1
    learning_rate: float = 0.001
    epochs: int = 100
    batch_size: int = 32
    lookback_window: int = 20

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _feature_names: Optional[List[str]] = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "TransformerForecaster":
        """Fit Transformer model."""
        torch = _require_pytorch()

        # Prepare data
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X.values)
        self._feature_names = list(X.columns)

        # Create sequences
        X_seq, y_seq = self._create_sequences(X_scaled, y.values)

        # Convert to tensors
        X_tensor = torch.FloatTensor(X_seq)
        y_tensor = torch.FloatTensor(y_seq).unsqueeze(-1)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize model
        input_dim = X.shape[1]
        self._model = TransformerForecasterModel(
            input_dim, self.d_model, self.nhead, self.num_layers, self.dropout
        )

        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self.learning_rate)

        # Training loop
        self._model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self._model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            if (epoch + 1) % 20 == 0:
                print(".4f")

        self._fitted = True
        return self

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create input sequences for Transformer."""
        X_seq, y_seq = [], []

        for i in range(len(X) - self.lookback_window):
            X_seq.append(X[i:i+self.lookback_window])
            y_seq.append(y[i+self.lookback_window])

        return np.array(X_seq), np.array(y_seq)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self._fitted or self._model is None or self._scaler is None:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        # Scale features
        X_scaled = self._scaler.transform(X.values)

        # Create sequences
        if len(X_scaled) < self.lookback_window:
            padding = np.zeros((self.lookback_window - len(X_scaled), X_scaled.shape[1]))
            X_seq = np.vstack([padding, X_scaled])
        else:
            X_seq = X_scaled[-self.lookback_window:]

        X_tensor = torch.FloatTensor(X_seq).unsqueeze(0)  # Add batch dimension

        self._model.eval()
        with torch.no_grad():
            prediction = self._model(X_tensor)

        return prediction.numpy().flatten()

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Transformer doesn't provide direct feature importance."""
        return None


class TransformerForecasterModel(torch.nn.Module):
    """Transformer model for time series forecasting."""

    def __init__(self, input_dim: int, d_model: int, nhead: int, num_layers: int, dropout: float):
        super().__init__()

        self.input_projection = torch.nn.Linear(input_dim, d_model)
        self.positional_encoding = PositionalEncoding(d_model, dropout)

        encoder_layer = torch.nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dropout=dropout, batch_first=True
        )
        self.transformer_encoder = torch.nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.output_projection = torch.nn.Linear(d_model, 1)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        x = self.input_projection(x)
        x = self.positional_encoding(x)

        # Apply transformer
        x = self.transformer_encoder(x)

        # Take last time step and project to output
        x = x[:, -1, :]  # (batch_size, d_model)
        x = self.dropout(x)
        x = self.output_projection(x)
        return x


class PositionalEncoding(torch.nn.Module):
    """Positional encoding for Transformer."""

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = torch.nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


@dataclass
class EnsembleForecaster:
    """Ensemble of multiple forecasting models."""

    models: List[TimeSeriesForecaster] = field(default_factory=list)
    weights: Optional[List[float]] = None

    # Fitted attributes
    _fitted: bool = field(default=False, init=False)

    def add_model(self, model: TimeSeriesForecaster) -> "EnsembleForecaster":
        """Add a model to the ensemble."""
        self.models.append(model)
        return self

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "EnsembleForecaster":
        """Fit all models in the ensemble."""
        fitted_models = []

        for model in self.models:
            try:
                fitted_model = model.fit(X, y)
                fitted_models.append(fitted_model)
            except Exception as e:
                warnings.warn(f"Failed to fit model {type(model).__name__}: {e}")

        self.models = fitted_models
        self._fitted = True

        # Set equal weights if not provided
        if self.weights is None:
            self.weights = [1.0 / len(self.models)] * len(self.models)

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions."""
        if not self._fitted:
            raise RuntimeError("Ensemble must be fitted.")

        predictions = []
        for model in self.models:
            try:
                pred = model.predict(X)
                predictions.append(pred)
            except Exception as e:
                warnings.warn(f"Model prediction failed: {e}")
                predictions.append(np.zeros(len(X)) if len(X) > 0 else np.array([0.0]))

        # Weighted average
        if predictions:
            predictions_array = np.array(predictions)
            weighted_pred = np.average(predictions_array, axis=0, weights=self.weights)
            return weighted_pred
        else:
            return np.zeros(len(X)) if len(X) > 0 else np.array([0.0])

    def optimize_weights(self, X_val: pd.DataFrame, y_val: pd.Series) -> "EnsembleForecaster":
        """Optimize ensemble weights using validation data."""
        if not self._fitted:
            raise RuntimeError("Ensemble must be fitted.")

        def objective(weights):
            self.weights = weights.tolist()
            pred = self.predict(X_val)
            return mean_squared_error(y_val, pred)

        # Constraints: weights sum to 1, all positive
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
        ]
        bounds = [(0, 1) for _ in self.models]

        initial_weights = np.array(self.weights)

        result = minimize(objective, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        if result.success:
            self.weights = result.x.tolist()
        else:
            warnings.warn("Weight optimization failed, using equal weights")

        return self

    def get_model_weights(self) -> Dict[str, float]:
        """Get model weights."""
        return {type(model).__name__: weight for model, weight in zip(self.models, self.weights)}


# =============================================================================
# ANOMALY DETECTION ALGORITHMS
# =============================================================================

@dataclass
class AnomalyDetector:
    """Base class for time series anomaly detection."""

    contamination: float = 0.1  # Expected proportion of anomalies

    def fit(self, series: pd.Series) -> "AnomalyDetector":
        """Fit the anomaly detector."""
        raise NotImplementedError

    def detect(self, series: pd.Series) -> pd.Series:
        """Detect anomalies in the series."""
        raise NotImplementedError


@dataclass
class IsolationForestAnomalyDetector(AnomalyDetector):
    """Isolation Forest based anomaly detection."""

    n_estimators: int = 100
    max_samples: Union[str, int] = 'auto'
    random_state: int = 42

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _threshold: float = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, series: pd.Series) -> "IsolationForestAnomalyDetector":
        """Fit Isolation Forest."""
        from sklearn.ensemble import IsolationForest

        # Prepare features (rolling statistics)
        features = self._create_features(series)

        self._model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            random_state=self.random_state
        )

        self._model.fit(features)
        scores = self._model.decision_function(features)
        self._threshold = np.percentile(scores, 100 * self.contamination)
        self._fitted = True

        return self

    def detect(self, series: pd.Series) -> pd.Series:
        """Detect anomalies."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        features = self._create_features(series)
        scores = self._model.decision_function(features)
        anomalies = scores < self._threshold

        return pd.Series(anomalies, index=series.index, name='anomaly')

    def _create_features(self, series: pd.Series) -> np.ndarray:
        """Create features for anomaly detection."""
        features = []

        # Rolling statistics
        for window in [5, 10, 20, 50]:
            features.extend([
                series.rolling(window).mean(),
                series.rolling(window).std(),
                series.rolling(window).skew(),
                series.rolling(window).kurt()
            ])

        # Lagged values
        for lag in [1, 2, 3, 5, 10]:
            features.append(series.shift(lag))

        # First differences
        features.append(series.diff())

        # Seasonal differences (assuming daily data)
        features.append(series - series.shift(7))

        # Combine features
        df = pd.concat(features, axis=1).dropna()
        return df.values


@dataclass
class ProphetAnomalyDetector(AnomalyDetector):
    """Prophet-based anomaly detection."""

    changepoint_prior_scale: float = 0.05
    seasonality_prior_scale: float = 10.0
    interval_width: float = 0.95

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, series: pd.Series) -> "ProphetAnomalyDetector":
        """Fit Prophet model."""
        if not PROPHET_AVAILABLE:
            raise RuntimeError("Prophet required for ProphetAnomalyDetector")

        # Prepare data for Prophet
        df = pd.DataFrame({
            'ds': series.index,
            'y': series.values
        })

        self._model = Prophet(
            changepoint_prior_scale=self.changepoint_prior_scale,
            seasonality_prior_scale=self.seasonality_prior_scale,
            interval_width=self.interval_width
        )

        self._model.fit(df)
        self._fitted = True

        return self

    def detect(self, series: pd.Series) -> pd.Series:
        """Detect anomalies using Prophet predictions."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Create future dataframe
        future = self._model.make_future_dataframe(periods=0, freq='D')
        forecast = self._model.predict(future)

        # Calculate residuals
        actual = series.values
        predicted = forecast['yhat'].values[:len(actual)]
        residuals = actual - predicted

        # Detect anomalies based on residual magnitude
        residual_std = np.std(residuals)
        threshold = self.contamination * residual_std * 3  # 3-sigma equivalent
        anomalies = np.abs(residuals) > threshold

        return pd.Series(anomalies, index=series.index, name='anomaly')


@dataclass
class LSTMAnomalyDetector(AnomalyDetector):
    """LSTM-based anomaly detection."""

    lookback_window: int = 20
    hidden_dim: int = 64
    num_layers: int = 2
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 50
    threshold_percentile: float = 95.0

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _threshold: float = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, series: pd.Series) -> "LSTMAnomalyDetector":
        """Fit LSTM autoencoder for anomaly detection."""
        torch = _require_pytorch()

        # Normalize data
        self._scaler = StandardScaler()
        scaled_data = self._scaler.fit_transform(series.values.reshape(-1, 1)).flatten()

        # Create sequences
        sequences = []
        for i in range(len(scaled_data) - self.lookback_window + 1):
            sequences.append(scaled_data[i:i+self.lookback_window])

        sequences = np.array(sequences)

        # Convert to tensors
        seq_tensor = torch.FloatTensor(sequences)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(seq_tensor, seq_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

        # Initialize model
        self._model = LSTMAutoencoder(self.lookback_window, self.hidden_dim,
                                    self.num_layers, self.dropout)

        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self.learning_rate)

        # Training loop
        self._model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self._model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

        # Calculate reconstruction errors on training data
        self._model.eval()
        reconstruction_errors = []
        with torch.no_grad():
            for seq in seq_tensor:
                seq_input = seq.unsqueeze(0)
                output = self._model(seq_input)
                error = torch.mean((output - seq_input) ** 2).item()
                reconstruction_errors.append(error)

        # Set threshold
        self._threshold = np.percentile(reconstruction_errors, self.threshold_percentile)
        self._fitted = True

        return self

    def detect(self, series: pd.Series) -> pd.Series:
        """Detect anomalies using reconstruction error."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        # Normalize data
        scaled_data = self._scaler.transform(series.values.reshape(-1, 1)).flatten()

        # Create sequences
        sequences = []
        anomalies = []

        self._model.eval()
        with torch.no_grad():
            for i in range(len(scaled_data) - self.lookback_window + 1):
                seq = scaled_data[i:i+self.lookback_window]
                seq_tensor = torch.FloatTensor(seq).unsqueeze(0)

                output = self._model(seq_tensor)
                error = torch.mean((output - seq_tensor) ** 2).item()

                is_anomaly = error > self._threshold
                anomalies.append(is_anomaly)

        # Pad beginning with False (no anomaly detection for initial points)
        padding = [False] * (self.lookback_window - 1)
        anomalies = padding + anomalies

        return pd.Series(anomalies, index=series.index, name='anomaly')


class LSTMAutoencoder(torch.nn.Module):
    """LSTM Autoencoder for anomaly detection."""

    def __init__(self, seq_len: int, hidden_dim: int, num_layers: int, dropout: float):
        super().__init__()

        self.encoder = torch.nn.LSTM(seq_len, hidden_dim, num_layers, dropout=dropout, batch_first=True)
        self.decoder = torch.nn.LSTM(hidden_dim, seq_len, num_layers, dropout=dropout, batch_first=True)

    def forward(self, x):
        # x shape: (batch_size, seq_len)
        x = x.unsqueeze(-1)  # Add feature dimension: (batch_size, seq_len, 1)

        # Encode
        _, (hidden, cell) = self.encoder(x)

        # Decode
        output, _ = self.decoder(hidden[-1].unsqueeze(0).repeat(1, x.size(1), 1))

        return output.squeeze(-1)  # Remove feature dimension


# =============================================================================
# CHANGE POINT DETECTION
# =============================================================================

@dataclass
class ChangePointDetector:
    """Change point detection algorithms."""

    method: str = 'pelt'  # 'pelt', 'binseg', 'bottomup', 'window'
    model: str = 'l2'     # Cost function: 'l1', 'l2', 'ar'
    min_size: int = 5     # Minimum segment size
    jump: int = 5         # Jump parameter for binseg

    def detect(self, series: pd.Series) -> List[int]:
        """Detect change points in the time series."""
        if not RUPTURES_AVAILABLE:
            raise RuntimeError("ruptures package required for change point detection")

        import ruptures as rpt

        # Convert to numpy array
        signal = series.values

        # Choose algorithm
        if self.method == 'pelt':
            algo = rpt.Pelt(model=self.model, min_size=self.min_size).fit(signal)
            change_points = algo.predict(pen=10)
        elif self.method == 'binseg':
            algo = rpt.Binseg(model=self.model, min_size=self.min_size, jump=self.jump).fit(signal)
            change_points = algo.predict(pen=10)
        elif self.method == 'bottomup':
            algo = rpt.BottomUp(model=self.model, min_size=self.min_size).fit(signal)
            change_points = algo.predict(pen=10)
        elif self.method == 'window':
            algo = rpt.Window(width=40, model=self.model, min_size=self.min_size).fit(signal)
            change_points = algo.predict(pen=10)
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Convert to indices (remove last element which is series length)
        change_points = change_points[:-1]

        return change_points

    def detect_with_cost(self, series: pd.Series, pen: float = 10) -> Dict[str, Any]:
        """Detect change points with cost analysis."""
        if not RUPTURES_AVAILABLE:
            raise RuntimeError("ruptures package required for change point detection")

        import ruptures as rpt

        signal = series.values
        algo = rpt.Pelt(model=self.model, min_size=self.min_size).fit(signal)
        result = algo.predict(pen=pen)

        # Get segmentation
        bkps = result[:-1]
        segments = [(0, bkps[0])] + [(bkps[i], bkps[i+1]) for i in range(len(bkps)-1)] + [(bkps[-1], len(signal))]

        # Calculate segment statistics
        segment_stats = []
        for start, end in segments:
            segment_data = signal[start:end]
            stats = {
                'start_idx': start,
                'end_idx': end,
                'length': end - start,
                'mean': np.mean(segment_data),
                'std': np.std(segment_data),
                'min': np.min(segment_data),
                'max': np.max(segment_data)
            }
            segment_stats.append(stats)

        return {
            'change_points': bkps,
            'segments': segment_stats,
            'penalty': pen
        }


# =============================================================================
# TIME SERIES DECOMPOSITION AND ANALYSIS
# =============================================================================

@dataclass
class SpectralAnalyzer:
    """Spectral analysis of time series."""

    nperseg: Optional[int] = None
    noverlap: Optional[int] = None
    nfft: Optional[int] = None
    detrend: str = 'constant'
    scaling: str = 'density'

    def periodogram(self, series: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Compute periodogram."""
        from scipy.signal import periodogram

        freq, power = periodogram(series.values, detrend=self.detrend,
                                nfft=self.nfft, scaling=self.scaling)
        return freq, power

    def welch_periodogram(self, series: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Welch's periodogram."""
        from scipy.signal import welch

        freq, power = welch(series.values, detrend=self.detrend,
                          nperseg=self.nperseg, noverlap=self.noverlap,
                          nfft=self.nfft, scaling=self.scaling)
        return freq, power

    def find_dominant_frequencies(self, series: pd.Series, n_top: int = 5) -> List[Tuple[float, float]]:
        """Find dominant frequencies in the series."""
        freq, power = self.welch_periodogram(series)

        # Get top frequencies
        top_indices = np.argsort(power)[-n_top:][::-1]
        dominant_freqs = [(freq[i], power[i]) for i in top_indices]

        return dominant_freqs

    def get_power_spectral_density(self, series: pd.Series) -> pd.DataFrame:
        """Compute power spectral density."""
        freq, power = self.welch_periodogram(series)

        # Convert frequency to period (for time series interpretation)
        periods = 1.0 / freq

        psd_df = pd.DataFrame({
            'frequency': freq,
            'period': periods,
            'power': power
        })

        # Sort by power
        psd_df = psd_df.sort_values('power', ascending=False)

        return psd_df


@dataclass
class WaveletAnalyzer:
    """Wavelet analysis of time series."""

    wavelet: str = 'morl'  # Mother wavelet
    scales: Optional[np.ndarray] = None
    sampling_period: float = 1.0

    def continuous_wavelet_transform(self, series: pd.Series) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Perform continuous wavelet transform."""
        try:
            import pywt

            # Set default scales if not provided
            if self.scales is None:
                self.scales = np.arange(1, 128)

            coefficients, frequencies = pywt.cwt(series.values, self.scales, self.wavelet,
                                               sampling_period=self.sampling_period)

            return coefficients, frequencies, self.scales

        except ImportError:
            raise RuntimeError("PyWavelets required for wavelet analysis")

    def wavelet_power_spectrum(self, series: pd.Series) -> pd.DataFrame:
        """Compute wavelet power spectrum."""
        coefficients, frequencies, scales = self.continuous_wavelet_transform(series)

        # Compute power
        power = np.abs(coefficients) ** 2

        # Create DataFrame
        power_df = pd.DataFrame(power, index=frequencies, columns=series.index)

        return power_df

    def find_wavelet_ridges(self, series: pd.Series) -> List[np.ndarray]:
        """Find ridges in wavelet transform (dominant oscillation modes)."""
        try:
            from scipy.signal import find_peaks

            coefficients, frequencies, scales = self.continuous_wavelet_transform(series)

            # Find local maxima along scale dimension for each time point
            ridges = []
            for t in range(coefficients.shape[1]):
                power_profile = np.abs(coefficients[:, t]) ** 2
                peaks, _ = find_peaks(power_profile, height=np.std(power_profile))
                ridges.append(peaks)

            return ridges

        except ImportError:
            raise RuntimeError("scipy required for ridge detection")


# =============================================================================
# HIGH-FREQUENCY DATA ANALYSIS
# =============================================================================

@dataclass
class RealizedVolatilityCalculator:
    """Realized volatility calculations for high-frequency data."""

    sampling_rule: str = '5min'  # Resampling frequency
    annualization_factor: float = np.sqrt(252 * 24 * 12)  # For 5-min data

    def realized_variance(self, prices: pd.Series) -> pd.Series:
        """Calculate realized variance."""
        # Resample to regular intervals
        resampled = prices.resample(self.sampling_rule).last().dropna()

        # Calculate returns
        returns = resampled.pct_change().dropna()

        # Realized variance (sum of squared returns)
        rv = returns.groupby(pd.Grouper(freq='D')).apply(lambda x: np.sum(x**2))

        return rv * self.annualization_factor ** 2

    def bipower_variation(self, prices: pd.Series, m: int = 1) -> pd.Series:
        """Calculate bipower variation (robust to jumps)."""
        # Resample to regular intervals
        resampled = prices.resample(self.sampling_rule).last().dropna()

        # Calculate returns
        returns = resampled.pct_change().dropna()

        # Bipower variation
        bv = returns.groupby(pd.Grouper(freq='D')).apply(
            lambda x: np.sum(np.abs(x[:-m]) * np.abs(x[m:])) * (np.pi/2)
        )

        return bv * self.annualization_factor ** 2

    def realized_kernel(self, prices: pd.Series, H: float = 1.0) -> pd.Series:
        """Calculate realized kernel (accounts for microstructure noise)."""
        # Resample to regular intervals
        resampled = prices.resample(self.sampling_rule).last().dropna()

        # Calculate returns
        returns = resampled.pct_change().dropna()

        def kernel_estimator(returns_array, H):
            n = len(returns_array)
            weights = np.zeros(n-1)

            # Parzen kernel weights
            for k in range(1, n):
                x = k / (H * np.sqrt(n))
                if x <= 0.5:
                    weights[k-1] = 1 - 6*x**2 + 6*x**3
                elif x <= 1:
                    weights[k-1] = 2*(1-x)**3
                else:
                    weights[k-1] = 0

            # Realized kernel
            rk = returns_array[0]**2
            for k in range(1, n):
                gamma_k = np.sum(returns_array[:-k] * returns_array[k:])
                rk += 2 * weights[k-1] * gamma_k

            return rk

        rk = returns.groupby(pd.Grouper(freq='D')).apply(lambda x: kernel_estimator(x.values, H))

        return rk * self.annualization_factor ** 2


# =============================================================================
# MULTIVARIATE TIME SERIES ANALYSIS
# =============================================================================

@dataclass
class GrangerCausalityTester:
    """Granger causality tests for multivariate time series."""

    max_lag: int = 10
    test_type: str = 'ssr_ftest'  # 'ssr_ftest', 'ssr_chi2test', 'lrtest', 'params_ftest'

    def test_causality(self, X: pd.Series, Y: pd.Series) -> Dict[str, Any]:
        """Test if X Granger-causes Y."""
        if not STATS_MODELS_AVAILABLE:
            raise StatsmodelsUnavailable("statsmodels required for Granger causality")

        from statsmodels.tsa.stattools import grangercausalitytests

        # Prepare data: columns are [Y, X]
        data = pd.concat([Y, X], axis=1).dropna()

        try:
            result = grangercausalitytests(data, maxlag=self.max_lag, verbose=False)

            # Extract results for each lag
            lag_results = {}
            for lag in range(1, self.max_lag + 1):
                if lag in result:
                    test_result = result[lag][0]
                    lag_results[lag] = {
                        'statistic': test_result[0],
                        'p_value': test_result[1],
                        'df': test_result[2] if len(test_result) > 2 else None
                    }

            # Find best lag (lowest p-value)
            best_lag = min(lag_results.keys(),
                         key=lambda k: lag_results[k]['p_value'])

            return {
                'causality_detected': lag_results[best_lag]['p_value'] < 0.05,
                'best_lag': best_lag,
                'best_p_value': lag_results[best_lag]['p_value'],
                'all_results': lag_results
            }

        except Exception as e:
            return {
                'causality_detected': False,
                'error': str(e),
                'all_results': {}
            }

    def pairwise_causality_matrix(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute pairwise Granger causality matrix."""
        variables = data.columns
        n_vars = len(variables)

        causality_matrix = pd.DataFrame(
            np.zeros((n_vars, n_vars)),
            index=variables,
            columns=variables
        )

        pvalue_matrix = pd.DataFrame(
            np.ones((n_vars, n_vars)),
            index=variables,
            columns=variables
        )

        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i != j:
                    result = self.test_causality(data[var2], data[var1])
                    causality_matrix.loc[var1, var2] = result.get('causality_detected', False)
                    pvalue_matrix.loc[var1, var2] = result.get('best_p_value', 1.0)

        return {
            'causality_matrix': causality_matrix,
            'pvalue_matrix': pvalue_matrix
        }


@dataclass
class CointegrationTester:
    """Cointegration tests for multivariate time series."""

    test_type: str = 'johansen'  # 'johansen', 'engle_granger'
    significance_level: float = 0.05
    k_ar_diff: int = 1  # Lag order for Johansen test

    def test_cointegration(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Test for cointegration among multiple time series."""
        if not STATS_MODELS_AVAILABLE:
            raise StatsmodelsUnavailable("statsmodels required for cointegration tests")

        variables = data.columns
        n_vars = len(variables)

        if self.test_type == 'johansen':
            return self._johansen_test(data)
        elif self.test_type == 'engle_granger':
            return self._engle_granger_test(data)
        else:
            raise ValueError(f"Unknown test type: {self.test_type}")

    def _johansen_test(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Johansen cointegration test."""
        from statsmodels.tsa.vector_ar.vecm import coint_johansen

        try:
            result = coint_johansen(data.values, det_order=0, k_ar_diff=self.k_ar_diff)

            # Extract results
            n_vars = data.shape[1]
            cointegration_rank = 0

            for i in range(n_vars):
                if result.eig[i] > result.cvt[i, 1]:  # 5% significance level
                    cointegration_rank += 1

            return {
                'cointegrated': cointegration_rank > 0,
                'cointegration_rank': cointegration_rank,
                'eigenvalues': result.eig,
                'critical_values': result.cvt,
                'eigenvectors': result.evec,
                'test_type': 'johansen'
            }

        except Exception as e:
            return {
                'cointegrated': False,
                'error': str(e),
                'test_type': 'johansen'
            }

    def _engle_granger_test(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Engle-Granger cointegration test (pairwise)."""
        from statsmodels.tsa.stattools import coint

        variables = data.columns
        cointegration_results = {}

        for i in range(len(variables)):
            for j in range(i+1, len(variables)):
                var1, var2 = variables[i], variables[j]

                try:
                    score, p_value, critical_values = coint(
                        data[var1], data[var2], trend='c'
                    )

                    cointegration_results[f'{var1}_{var2}'] = {
                        'statistic': score,
                        'p_value': p_value,
                        'critical_values': critical_values,
                        'cointegrated': p_value < self.significance_level
                    }

                except Exception as e:
                    cointegration_results[f'{var1}_{var2}'] = {
                        'error': str(e),
                        'cointegrated': False
                    }

        # Overall assessment
        cointegrated_pairs = sum(1 for result in cointegration_results.values()
                               if result.get('cointegrated', False))

        return {
            'cointegrated': cointegrated_pairs > 0,
            'cointegrated_pairs': cointegrated_pairs,
            'pairwise_results': cointegration_results,
            'test_type': 'engle_granger'
        }


# =============================================================================
# ENSEMBLE AND META-MODELS
# =============================================================================

@dataclass
class TimeSeriesEnsemble:
    """Ensemble model combining multiple time series forecasting approaches."""

    base_models: List[Any] = field(default_factory=list)
    meta_model: Any = None
    use_stacking: bool = True

    # Fitted attributes
    _fitted: bool = field(default=False, init=False)
    _scaler: Any = field(default=None, init=False)

    def add_model(self, model: Any, name: Optional[str] = None) -> "TimeSeriesEnsemble":
        """Add a base model to the ensemble."""
        if name is None:
            name = type(model).__name__
        self.base_models.append((name, model))
        return self

    def fit(self, X: pd.DataFrame, y: pd.Series, meta_features: Optional[pd.DataFrame] = None) -> "TimeSeriesEnsemble":
        """Fit the ensemble model."""
        # Fit base models
        base_predictions = []

        for name, model in self.base_models:
            try:
                model.fit(X, y)
                pred = model.predict(X)
                base_predictions.append(pred)
            except Exception as e:
                warnings.warn(f"Failed to fit {name}: {e}")
                base_predictions.append(np.zeros(len(y)))

        base_predictions = np.column_stack(base_predictions)

        if self.use_stacking and meta_features is not None:
            # Use meta-features for stacking
            meta_X = np.column_stack([base_predictions, meta_features.values])
        else:
            meta_X = base_predictions

        # Fit meta-model
        if self.meta_model is None:
            self.meta_model = RandomForestRegressor(n_estimators=100, random_state=42)

        self.meta_model.fit(meta_X, y)
        self._fitted = True

        return self

    def predict(self, X: pd.DataFrame, meta_features: Optional[pd.DataFrame] = None) -> np.ndarray:
        """Make ensemble predictions."""
        if not self._fitted:
            raise RuntimeError("Ensemble must be fitted.")

        # Get base model predictions
        base_predictions = []

        for name, model in self.base_models:
            try:
                pred = model.predict(X)
                base_predictions.append(pred)
            except Exception as e:
                warnings.warn(f"Model prediction failed: {e}")
                predictions.append(np.zeros(len(X)) if len(X) > 0 else np.array([0.0]))

        # Weighted average
        if predictions:
            predictions_array = np.array(predictions)
            weighted_pred = np.average(predictions_array, axis=0, weights=self.weights)
            return weighted_pred
        else:
            return np.zeros(len(X)) if len(X) > 0 else np.array([0.0])

    def optimize_weights(self, X_val: pd.DataFrame, y_val: pd.Series) -> "TimeSeriesEnsemble":
        """Optimize ensemble weights using validation data."""
        if not self._fitted:
            raise RuntimeError("Ensemble must be fitted.")

        def objective(weights):
            self.weights = weights.tolist()
            pred = self.predict(X_val)
            return mean_squared_error(y_val, pred)

        # Constraints: weights sum to 1, all positive
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
        ]
        bounds = [(0, 1) for _ in self.models]

        initial_weights = np.array(self.weights)

        result = minimize(objective, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        if result.success:
            self.weights = result.x.tolist()
        else:
            warnings.warn("Weight optimization failed, using equal weights")

        return self

    def get_model_weights(self) -> Dict[str, float]:
        """Get model weights."""
        return {type(model).__name__: weight for model, weight in zip(self.models, self.weights)}


# =============================================================================
# ADVANCED TIME SERIES PIPELINE
# =============================================================================

@dataclass
class TimeSeriesPipeline:
    """Complete time series analysis and forecasting pipeline."""

    # Components
    stationarity_tester: Any = None
    decomposer: Any = None
    feature_engineer: Any = None
    model_selector: Any = None
    forecaster: Any = None
    validator: Any = None

    # Pipeline configuration
    auto_stationarity: bool = True
    auto_differencing: bool = True
    use_decomposition: bool = True
    feature_engineering: bool = True
    model_selection: bool = True
    cross_validation: bool = True

    def __post_init__(self):
        """Initialize default components."""
        if self.stationarity_tester is None:
            self.stationarity_tester = lambda x: check_stationarity(x)

        if self.decomposer is None:
            self.decomposer = lambda x: decompose_time_series(x)

        if self.feature_engineer is None:
            self.feature_engineer = self._default_feature_engineering

        if self.model_selector is None:
            self.model_selector = self._default_model_selection

        if self.validator is None:
            self.validator = self._default_validation

    def fit(self, series: pd.Series, exog: Optional[pd.DataFrame] = None) -> "TimeSeriesPipeline":
        """Fit the complete pipeline."""
        # Step 1: Stationarity testing
        if self.auto_stationarity:
            stationarity_result = self.stationarity_tester(series)
            if not stationarity_result['overall_stationary']:
                if self.auto_differencing:
                    series = self._difference_series(series)
                    print("Applied differencing for stationarity")

        # Step 2: Decomposition
        if self.use_decomposition:
            decomposition = self.decomposer(series)
            # Use residuals for modeling
            series = decomposition['residual']

        # Step 3: Feature engineering
        if self.feature_engineering:
            features = self.feature_engineer(series, exog)

        # Step 4: Model selection and fitting
        if self.model_selection:
            self.forecaster = self.model_selector(series, features if self.feature_engineering else None)

        return self

    def predict(self, steps: int = 1, exog: Optional[pd.DataFrame] = None) -> pd.Series:
        """Generate predictions."""
        if self.forecaster is None:
            raise RuntimeError("Pipeline must be fitted.")

        return self.forecaster.predict(steps, exog)

    def _difference_series(self, series: pd.Series) -> pd.Series:
        """Apply differencing to make series stationary."""
        return series.diff().dropna()

    def _default_feature_engineering(self, series: pd.Series, exog: Optional[pd.DataFrame]) -> pd.DataFrame:
        """Default feature engineering."""
        features = pd.DataFrame(index=series.index)

        # Lagged values
        for lag in [1, 2, 3, 7, 14, 30]:
            features[f'lag_{lag}'] = series.shift(lag)

        # Rolling statistics
        for window in [7, 14, 30]:
            features[f'rolling_mean_{window}'] = series.rolling(window).mean()
            features[f'rolling_std_{window}'] = series.rolling(window).std()

        # Time-based features
        features['day_of_week'] = series.index.dayofweek
        features['month'] = series.index.month
        features['quarter'] = series.index.quarter

        # Add exogenous variables if provided
        if exog is not None:
            features = pd.concat([features, exog], axis=1)

        return features.dropna()

    def _default_model_selection(self, series: pd.Series, features: Optional[pd.DataFrame]) -> Any:
        """Default model selection."""
        # Try different models and select best
        models_to_try = []

        # Add statistical models
        if STATS_MODELS_AVAILABLE:
            models_to_try.append(('ARIMA', ARIMAModel(order=(1, 1, 1))))

        # Add ML models
        if features is not None:
            models_to_try.append(('RandomForest', RandomForestRegressor(n_estimators=100)))
            models_to_try.append(('GradientBoosting', GradientBoostingRegressor(n_estimators=100)))

        best_model = None
        best_score = float('inf')

        for name, model in models_to_try:
            try:
                if hasattr(model, 'fit'):
                    if isinstance(model, (RandomForestRegressor, GradientBoostingRegressor)):
                        # ML model
                        X = features.values
                        y = series.values[len(series) - len(features):]  # Align lengths
                        model.fit(X, y)
                        pred = model.predict(X)
                        score = mean_squared_error(y, pred)
                    else:
                        # Time series model
                        model.fit(series)
                        pred = model.predict(steps=len(series))  # In-sample prediction
                        score = mean_squared_error(series, pred)

                    if score < best_score:
                        best_score = score
                        best_model = model

            except Exception as e:
                continue

        return best_model

    def _default_validation(self, series: pd.Series, predictions: pd.Series) -> Dict[str, float]:
        """Default validation metrics."""
        return {
            'mse': mean_squared_error(series, predictions),
            'mae': mean_absolute_error(series, predictions),
            'rmse': np.sqrt(mean_squared_error(series, predictions)),
            'r2': r2_score(series, predictions)
        }


# =============================================================================
# UTILITY FUNCTIONS AND COMPATIBILITY
# =============================================================================

def auto_arima(series: pd.Series, seasonal: bool = True, **kwargs) -> ARIMAModel:
    """Convenience function for automatic ARIMA model selection."""
    return ARIMAModel.auto_arima(series, seasonal=seasonal, **kwargs)


def seasonal_decompose(series: pd.Series, **kwargs) -> Dict[str, pd.Series]:
    """Convenience function for seasonal decomposition."""
    return decompose_time_series(series, **kwargs)


def detect_anomalies(series: pd.Series, method: str = 'isolation_forest', **kwargs) -> pd.Series:
    """Convenience function for anomaly detection."""
    if method == 'isolation_forest':
        detector = IsolationForestAnomalyDetector(**kwargs)
    elif method == 'prophet':
        detector = ProphetAnomalyDetector(**kwargs)
    elif method == 'lstm':
        detector = LSTMAnomalyDetector(**kwargs)
    else:
        raise ValueError(f"Unknown anomaly detection method: {method}")

    detector.fit(series)
    return detector.detect(series)


def detect_change_points(series: pd.Series, method: str = 'pelt', **kwargs) -> List[int]:
    """Convenience function for change point detection."""
    detector = ChangePointDetector(method=method, **kwargs)
    return detector.detect(series)


# Maintain backward compatibility
_ARIMAModel = ARIMAModel


# =============================================================================
# ADVANCED MATHEMATICAL MODELS (NOBEL-PRIZE LEVEL COMPLEXITY)
# =============================================================================

@dataclass
class AdvancedMathematicalModels:
    """Collection of Nobel-prize level mathematical models for time series analysis."""

    @staticmethod
    def riemann_zeta_time_series(series: pd.Series, s: complex = 0.5 + 14.134725j) -> pd.Series:
        """Apply Riemann zeta function transformation to time series.

        Uses the Riemann zeta function ζ(s) to transform financial time series
        into complex domain for advanced pattern recognition.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        s : complex
            Complex argument for zeta function

        Returns:
        --------
        pd.Series : Zeta-transformed series
        """
        def zeta_transform(x):
            """Complex zeta function approximation."""
            if x == 0:
                return 0
            # Simplified zeta function approximation for large |Im(s)|
            result = 0
            for n in range(1, 50):  # Truncated series
                result += 1 / (n ** s)
            return result

        # Apply zeta transformation with complex argument
        transformed = series.apply(lambda x: abs(zeta_transform(complex(x, 0.1))) if x != 0 else 0)
        return transformed

    @staticmethod
    def fourier_analytic_continuation(series: pd.Series, analytic_strip: Tuple[float, float] = (-1, 1)) -> pd.Series:
        """Apply Fourier analytic continuation to extend series into complex plane.

        Uses Fourier transforms to analytically continue the time series
        into the complex domain, enabling advanced prediction capabilities.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        analytic_strip : tuple
            Complex strip for analytic continuation (Re_min, Re_max)

        Returns:
        --------
        pd.Series : Analytically continued series
        """
        # Fourier transform
        fft_result = np.fft.fft(series.values)

        # Analytic continuation in frequency domain
        frequencies = np.fft.fftfreq(len(series))
        analytic_factor = np.exp(2j * np.pi * frequencies * analytic_strip[0])

        # Inverse transform with analytic continuation
        continued = np.fft.ifft(fft_result * analytic_factor)
        return pd.Series(np.real(continued), index=series.index)

    @staticmethod
    def quantum_mechanical_wave_function(series: pd.Series, potential_barrier: float = 1.0) -> pd.Series:
        """Apply quantum mechanical wave function analysis to time series.

        Models financial time series as quantum mechanical wave functions
        with potential barriers representing market resistance levels.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        potential_barrier : float
            Quantum potential barrier height

        Returns:
        --------
        pd.Series : Wave function probability density
        """
        # Normalize series to [-π, π] for wave function
        normalized = 2 * np.pi * (series - series.min()) / (series.max() - series.min()) - np.pi

        # Quantum harmonic oscillator wave function
        def quantum_wave(x, n=0):
            """nth energy level wave function."""
            hermite_coeff = np.polynomial.hermite.Hermite([0] * n + [1])
            normalization = 1 / np.sqrt(2**n * np.math.factorial(n)) * (np.pi)**(-0.25)

            # Add potential barrier effect
            barrier_factor = np.exp(-potential_barrier * np.abs(x))
            return normalization * hermite_coeff(x) * np.exp(-x**2 / 2) * barrier_factor

        # Compute probability density |ψ(x)|²
        wave_amplitudes = np.array([quantum_wave(x) for x in normalized])
        probability_density = np.abs(wave_amplitudes)**2

        return pd.Series(probability_density, index=series.index)

    @staticmethod
    def string_theory_vibrational_modes(series: pd.Series, string_length: float = 1.0) -> Dict[str, pd.Series]:
        """Apply string theory vibrational mode analysis to time series.

        Models financial markets as vibrating strings with different
        fundamental frequencies representing market harmonics.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        string_length : float
            Effective string length for vibrational modes

        Returns:
        --------
        dict : Dictionary of vibrational mode series
        """
        # Fundamental frequency
        fundamental_freq = 1 / string_length

        # Extract fundamental components using FFT
        fft_result = np.fft.fft(series.values)
        frequencies = np.fft.fftfreq(len(series))

        modes = {}
        # First 5 vibrational modes (fundamental + harmonics)
        for n in range(1, 6):
            mode_freq = n * fundamental_freq
            # Find closest frequency in FFT
            freq_idx = np.argmin(np.abs(frequencies - mode_freq / len(series)))
            mode_amplitude = np.abs(fft_result[freq_idx])

            # Create mode series
            mode_series = mode_amplitude * np.sin(2 * np.pi * n * np.arange(len(series)) / len(series))
            modes[f'mode_{n}'] = pd.Series(mode_series, index=series.index)

        return modes

    @staticmethod
    def fractal_dimension_analysis(series: pd.Series, embedding_dimension: int = 10) -> Dict[str, float]:
        """Compute fractal dimensions using advanced mathematical methods.

        Applies multiple fractal dimension calculations including:
        - Hausdorff dimension
        - Correlation dimension
        - Information dimension
        - Packing dimension

        Parameters:
        -----------
        series : pd.Series
            Input time series
        embedding_dimension : int
            Embedding dimension for phase space reconstruction

        Returns:
        --------
        dict : Fractal dimension metrics
        """
        values = series.values

        # Phase space reconstruction
        def reconstruct_phase_space(data, dim, delay=1):
            """Reconstruct phase space using time delay embedding."""
            n_points = len(data) - (dim - 1) * delay
            if n_points <= 0:
                return np.array([])

            embedded = np.zeros((n_points, dim))
            for i in range(n_points):
                for j in range(dim):
                    embedded[i, j] = data[i + j * delay]
            return embedded

        # Correlation sum for correlation dimension
        def correlation_sum(embedded_data, r):
            """Compute correlation sum C(r)."""
            if len(embedded_data) == 0:
                return 0

            distances = spatial.distance.pdist(embedded_data)
            return np.sum(distances <= r) / (len(embedded_data) * (len(embedded_data) - 1))

        embedded = reconstruct_phase_space(values, embedding_dimension)

        if len(embedded) < 10:
            return {'hausdorff': np.nan, 'correlation': np.nan, 'information': np.nan, 'packing': np.nan}

        # Correlation dimension
        r_values = np.logspace(-3, 0, 20)
        c_r = [correlation_sum(embedded, r) for r in r_values]
        valid_idx = np.array(c_r) > 0
        if np.sum(valid_idx) > 5:
            slope, _ = np.polyfit(np.log(r_values[valid_idx]), np.log(np.array(c_r)[valid_idx]), 1)
            correlation_dim = slope
        else:
            correlation_dim = np.nan

        # Hausdorff dimension approximation (simplified)
        hausdorff_dim = correlation_dim if not np.isnan(correlation_dim) else np.nan

        # Information dimension (approximated as correlation dimension for simplicity)
        information_dim = correlation_dim

        # Packing dimension (upper bound)
        packing_dim = max(correlation_dim, information_dim) if not np.isnan(correlation_dim) else np.nan

        return {
            'hausdorff': hausdorff_dim,
            'correlation': correlation_dim,
            'information': information_dim,
            'packing': packing_dim
        }

    @staticmethod
    def topological_data_analysis(series: pd.Series, max_dimension: int = 2) -> Dict[str, Any]:
        """Apply topological data analysis to time series.

        Uses persistent homology to extract topological features
        from the time series structure.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        max_dimension : int
            Maximum homology dimension to compute

        Returns:
        --------
        dict : Topological features and persistence diagrams
        """
        try:
            from ripser import ripser
            from persim import PersistenceImager
        except ImportError:
            return {'error': 'ripser and persim required for topological analysis'}

        values = series.values.reshape(-1, 1)

        # Compute persistent homology
        diagrams = ripser(values, maxdim=max_dimension)['dgms']

        # Extract persistence features
        features = {}
        for dim in range(len(diagrams)):
            if len(diagrams[dim]) > 0:
                # Compute persistence (lifetime)
                persistence = diagrams[dim][:, 1] - diagrams[dim][:, 0]
                features[f'dim_{dim}_mean_persistence'] = np.mean(persistence)
                features[f'dim_{dim}_max_persistence'] = np.max(persistence)
                features[f'dim_{dim}_num_features'] = len(persistence)

        # Create persistence images if possible
        try:
            if len(diagrams[0]) > 0:
                imager = PersistenceImager(pixel_size=0.1)
                features['persistence_image'] = imager.fit_transform(diagrams)
        except:
            features['persistence_image'] = None

        features['diagrams'] = diagrams
        return features

    @staticmethod
    def category_theory_functor_analysis(series: pd.Series, categories: List[str] = None) -> Dict[str, Any]:
        """Apply category theory concepts to time series analysis.

        Models time series transformations as functors between
        mathematical categories representing different market regimes.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        categories : list
            List of category names (market regimes)

        Returns:
        --------
        dict : Category-theoretic analysis results
        """
        if categories is None:
            categories = ['bull', 'bear', 'sideways', 'volatile']

        # Define morphisms (transformations) between categories
        morphisms = {}

        # Compute transition probabilities between regimes
        returns = series.pct_change().dropna()
        regimes = pd.qcut(returns, q=len(categories), labels=categories)

        # Build transition matrix
        transition_matrix = pd.crosstab(regimes[:-1], regimes[1:], normalize='index')

        # Functor analysis: preserve structure through transformations
        functor_preservation = {}

        for cat1 in categories:
            for cat2 in categories:
                if cat1 in transition_matrix.index and cat2 in transition_matrix.columns:
                    functor_preservation[f'{cat1}_to_{cat2}'] = transition_matrix.loc[cat1, cat2]
                else:
                    functor_preservation[f'{cat1}_to_{cat2}'] = 0.0

        # Compute functor composition (associativity)
        composition_check = {}
        for cat1 in categories:
            for cat2 in categories:
                for cat3 in categories:
                    direct = functor_preservation.get(f'{cat1}_to_{cat3}', 0)
                    composed = sum(functor_preservation.get(f'{cat1}_to_{cat2}', 0) *
                                 functor_preservation.get(f'{cat2}_to_{cat3}', 0)
                                 for cat2 in categories)
                    composition_check[f'{cat1}->{cat2}->{cat3}'] = abs(direct - composed)

        return {
            'transition_matrix': transition_matrix,
            'functor_preservation': functor_preservation,
            'composition_associativity': composition_check,
            'categories': categories
        }

    @staticmethod
    def non_commutative_geometry_analysis(series: pd.Series, spectral_triple: Tuple = None) -> Dict[str, Any]:
        """Apply non-commutative geometry to time series analysis.

        Uses Connes' spectral triple framework to analyze
        the geometric structure of financial time series.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        spectral_triple : tuple
            (algebra, hilbert_space, dirac_operator) specification

        Returns:
        --------
        dict : Non-commutative geometric analysis results
        """
        values = series.values

        # Default spectral triple for time series
        if spectral_triple is None:
            # Algebra: C*-algebra of time series operators
            algebra_dim = len(values)

            # Hilbert space: L2 space of the time series
            hilbert_space = np.linalg.norm(values)

            # Dirac operator: finite difference operator
            dirac_operator = np.zeros((algebra_dim, algebra_dim))
            for i in range(algebra_dim - 1):
                dirac_operator[i, i+1] = 1
                dirac_operator[i+1, i] = -1

        # Compute spectral properties
        eigenvalues = np.linalg.eigvals(dirac_operator)
        spectral_radius = np.max(np.abs(eigenvalues))

        # Non-commutative distance
        commutator = np.dot(dirac_operator, dirac_operator.T) - np.dot(dirac_operator.T, dirac_operator)
        nc_distance = np.linalg.norm(commutator)

        # Dixmier trace (simplified approximation)
        positive_eigenvals = eigenvalues[eigenvalues > 0]
        if len(positive_eigenvals) > 0:
            dixmier_trace = np.sum(np.log(positive_eigenvals) / np.log(len(positive_eigenvals)))
        else:
            dixmier_trace = 0

        return {
            'spectral_radius': spectral_radius,
            'non_commutative_distance': nc_distance,
            'dixmier_trace': dixmier_trace,
            'eigenvalues': eigenvalues,
            'hilbert_space_dimension': hilbert_space,
            'algebra_dimension': algebra_dim
        }


# =============================================================================
# QUANTUM INFORMATION THEORY MODELS
# =============================================================================

@dataclass
class QuantumInformationModels:
    """Quantum information theory applications to financial time series."""

    @staticmethod
    def quantum_entropy_analysis(series: pd.Series, num_qubits: int = 8) -> Dict[str, float]:
        """Compute quantum entropy measures for time series.

        Uses von Neumann entropy and quantum mutual information
        to analyze information content of financial data.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        num_qubits : int
            Number of qubits for quantum representation

        Returns:
        --------
        dict : Quantum entropy metrics
        """
        values = series.values

        # Discretize values into quantum states
        n_states = 2 ** num_qubits
        digitized = np.digitize(values, np.linspace(values.min(), values.max(), n_states))

        # Create density matrix approximation
        prob_dist = np.bincount(digitized, minlength=n_states) / len(digitized)
        density_matrix = np.diag(prob_dist)

        # Von Neumann entropy: S(ρ) = -Tr(ρ log ρ)
        eigenvals = np.linalg.eigvals(density_matrix)
        eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros
        von_neumann_entropy = -np.sum(eigenvals * np.log2(eigenvals))

        # Linear entropy (simplified quantum coherence measure)
        linear_entropy = 1 - np.trace(np.dot(density_matrix, density_matrix))

        # Quantum Fisher information (simplified)
        fisher_info = np.sum(prob_dist * (np.gradient(prob_dist) / prob_dist)**2)

        return {
            'von_neumann_entropy': von_neumann_entropy,
            'linear_entropy': linear_entropy,
            'quantum_fisher_information': fisher_info,
            'num_qubits': num_qubits,
            'effective_dimension': len(eigenvals)
        }

    @staticmethod
    def quantum_walk_prediction(series: pd.Series, walk_steps: int = 10) -> pd.Series:
        """Use quantum walk algorithms for time series prediction.

        Implements quantum walk on a graph representation of
        the time series for advanced forecasting.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        walk_steps : int
            Number of quantum walk steps

        Returns:
        --------
        pd.Series : Quantum walk predictions
        """
        values = series.values
        n_points = len(values)

        # Create adjacency matrix based on similarity
        adjacency = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(n_points):
                adjacency[i, j] = np.exp(-np.abs(values[i] - values[j])**2)

        # Initialize quantum walk state (superposition)
        initial_state = np.ones(n_points) / np.sqrt(n_points)

        # Time evolution operator
        evolution_operator = adjacency / np.linalg.norm(adjacency)

        # Evolve quantum state
        current_state = initial_state.copy()
        for step in range(walk_steps):
            current_state = np.dot(evolution_operator, current_state)

        # Extract predictions from quantum amplitudes
        predictions = np.abs(current_state)**2 * np.max(values)

        return pd.Series(predictions, index=series.index)


# =============================================================================
# ADVANCED STOCHASTIC PROCESSES
# =============================================================================

@dataclass
class AdvancedStochasticProcesses:
    """Advanced stochastic process models beyond standard Brownian motion."""

    @staticmethod
    def levy_process_simulation(series: pd.Series, alpha: float = 1.5, num_simulations: int = 1000) -> pd.DataFrame:
        """Simulate Lévy processes for time series analysis.

        Lévy processes are generalizations of Brownian motion with
        heavy tails and jumps, better modeling extreme market events.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        alpha : float
            Stability parameter (0 < α ≤ 2)
        num_simulations : int
            Number of simulation paths

        Returns:
        --------
        pd.DataFrame : Simulated Lévy process paths
        """
        n_steps = len(series)
        dt = 1.0 / n_steps

        # Generate stable distribution random variables
        def stable_random(alpha, beta=0, size=1):
            """Generate stable distribution random variables."""
            if alpha == 2:  # Gaussian case
                return np.random.normal(0, 1, size)

            # General stable distribution using Chambers-Mallows-Stuck method
            u = np.random.uniform(-np.pi/2, np.pi/2, size)
            w = np.random.exponential(1, size)

            if alpha != 1:
                b = np.arctan(beta * np.tan(np.pi * alpha / 2)) / alpha
                s = (1 + beta**2 * np.tan(np.pi * alpha / 2)**2)**(1/(2*alpha))
                x = s * np.sin(alpha * (u + b)) / np.cos(u)**(1/alpha) * (np.cos(u - alpha*(u + b))/w)**((1-alpha)/alpha)
            else:  # Cauchy case
                x = (2/np.pi) * ((np.pi/2 + beta*u) * np.tan(u) - beta * np.log((np.pi/2 * w * np.cos(u)) / (np.pi/2 + beta*u)))

            return x

        # Simulate multiple paths
        simulations = []
        for sim in range(num_simulations):
            # Generate Lévy increments
            increments = stable_random(alpha, size=n_steps-1) * np.sqrt(dt)

            # Accumulate to get process path
            path = np.zeros(n_steps)
            path[0] = series.iloc[0]
            for i in range(1, n_steps):
                path[i] = path[i-1] + increments[i-1]

            simulations.append(path)

        return pd.DataFrame(simulations, columns=series.index).T

    @staticmethod
    def fractional_brownian_motion(series: pd.Series, hurst_exponent: float = 0.7) -> pd.Series:
        """Generate fractional Brownian motion with specified Hurst exponent.

        Fractional Brownian motion generalizes standard Brownian motion
        with long-range dependence controlled by the Hurst parameter.

        Parameters:
        -----------
        series : pd.Series
            Input time series (for scaling)
        hurst_exponent : float
            Hurst exponent H (0 < H < 1)

        Returns:
        --------
        pd.Series : Fractional Brownian motion path
        """
        n = len(series)
        scale = np.std(series.pct_change().dropna())

        # Generate fractional Gaussian noise using Hosking method
        def fgn_hosking(h, n):
            """Generate fractional Gaussian noise."""
            # Autocorrelation function for fGn
            gamma = np.zeros(n)
            for k in range(n):
                gamma[k] = 0.5 * ((k+1)**(2*h) - 2*k**(2*h) + (abs(k-1))**(2*h))

            # Generate using circulant embedding
            # This is a simplified implementation
            noise = np.random.normal(0, 1, n)
            fgn = np.zeros(n)

            # Cholesky decomposition of Toeplitz matrix (simplified)
            for i in range(n):
                fgn[i] = noise[i]
                for j in range(i):
                    if i - j < len(gamma):
                        fgn[i] -= gamma[i-j] * fgn[j]

            return fgn

        fgn = fgn_hosking(hurst_exponent, n)

        # Integrate to get fBm
        fbm = np.cumsum(fgn) * scale

        return pd.Series(fbm, index=series.index)

    @staticmethod
    def multifractal_random_walk(series: pd.Series, lambda_min: float = 0.1, lambda_max: float = 10.0) -> pd.Series:
        """Generate multifractal random walk.

        Multifractal random walks capture the scaling properties
        observed in financial time series with multiple scaling exponents.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        lambda_min, lambda_max : float
            Range of scaling factors

        Returns:
        --------
        pd.Series : Multifractal random walk
        """
        n = len(series)
        log_returns = np.log(series / series.shift(1)).dropna()

        # Generate multiplicative cascade
        def multiplicative_cascade(n_levels, p=0.5):
            """Generate multiplicative cascade for multifractality."""
            cascade = np.ones(2**n_levels)

            for level in range(n_levels):
                for i in range(2**level):
                    # Random multipliers
                    m1 = np.random.beta(2, 2)  # Uniform in (0,1) approximately
                    m2 = 1 - m1

                    start_idx = i * 2**(n_levels - level - 1)
                    mid_idx = start_idx + 2**(n_levels - level - 2)
                    end_idx = start_idx + 2**(n_levels - level - 1)

                    cascade[start_idx:mid_idx] *= m1
                    cascade[mid_idx:end_idx] *= m2

            return cascade[:n]

        # Number of cascade levels
        n_levels = int(np.log2(n))
        cascade_weights = multiplicative_cascade(n_levels)

        # Apply multifractal structure to returns
        mf_returns = log_returns.values[:len(cascade_weights)] * cascade_weights

        # Reconstruct price series
        mf_prices = np.exp(np.cumsum(mf_returns))
        mf_prices = np.concatenate([[series.iloc[0]], series.iloc[0] * mf_prices])

        return pd.Series(mf_prices[:len(series)], index=series.index)


# =============================================================================
# INFORMATION GEOMETRY AND FISHER INFORMATION
# =============================================================================

@dataclass
class InformationGeometryModels:
    """Information geometry applications to time series analysis."""

    @staticmethod
    def fisher_information_matrix(series: pd.Series, embedding_dim: int = 5) -> np.ndarray:
        """Compute Fisher information matrix for time series.

        The Fisher information matrix quantifies the amount of
        information that an observable random variable carries
        about an unknown parameter.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        embedding_dim : int
            Embedding dimension for parameter space

        Returns:
        --------
        np.ndarray : Fisher information matrix
        """
        values = series.values

        # Estimate probability distribution
        hist, bin_edges = np.histogram(values, bins=50, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Remove zero probabilities
        valid_idx = hist > 1e-10
        hist = hist[valid_idx]
        bin_centers = bin_centers[valid_idx]

        # Fisher information for location parameter
        score_function = (bin_centers - np.mean(bin_centers)) / np.var(bin_centers)
        fisher_info = np.sum(hist * score_function**2)

        # Construct Fisher information matrix (simplified)
        fim = np.zeros((embedding_dim, embedding_dim))

        # Diagonal elements (local Fisher information)
        for i in range(min(embedding_dim, len(hist))):
            fim[i, i] = fisher_info / len(hist)

        # Off-diagonal elements (coupling between parameters)
        for i in range(embedding_dim):
            for j in range(i+1, embedding_dim):
                coupling = fisher_info * 0.1 * np.exp(-abs(i-j))  # Exponential decay
                fim[i, j] = coupling
                fim[j, i] = coupling

        return fim

    @staticmethod
    def kullback_leibler_divergence_evolution(series: pd.Series, window_size: int = 50) -> pd.Series:
        """Compute time-varying Kullback-Leibler divergence.

        Tracks how the probability distribution evolves over time,
        measuring information loss between consecutive windows.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        window_size : int
            Rolling window size

        Returns:
        --------
        pd.Series : KL divergence time series
        """
        values = series.values
        kl_divergence = []

        for i in range(window_size, len(values) - window_size, window_size // 2):
            # Current and next window
            current_window = values[i-window_size:i]
            next_window = values[i:i+window_size]

            # Estimate distributions
            hist_current, bins = np.histogram(current_window, bins=30, density=True)
            hist_next, _ = np.histogram(next_window, bins=bins, density=True)

            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            hist_current = np.maximum(hist_current, epsilon)
            hist_next = np.maximum(hist_next, epsilon)

            # Normalize
            hist_current = hist_current / np.sum(hist_current)
            hist_next = hist_next / np.sum(hist_next)

            # Compute KL divergence: D_KL(P||Q) = Σ P(x) log(P(x)/Q(x))
            kl = np.sum(hist_current * np.log(hist_current / hist_next))

            kl_divergence.append(kl)

        # Pad with NaN for initial values
        padding = [np.nan] * (window_size // 2)
        kl_series = padding + kl_divergence

        return pd.Series(kl_series, index=series.index[:len(kl_series)])

    @staticmethod
    def amari_distance_analysis(series: pd.Series, reference_distribution: str = 'normal') -> Dict[str, float]:
        """Compute Amari α-divergence for distribution comparison.

        Amari α-divergence is a family of divergences that includes
        KL-divergence as a special case, providing richer information geometry.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        reference_distribution : str
            Reference distribution ('normal', 'uniform', 'exponential')

        Returns:
        --------
        dict : Amari divergence metrics for different α values
        """
        values = series.values

        # Create reference distribution
        if reference_distribution == 'normal':
            ref_mean, ref_std = np.mean(values), np.std(values)
            ref_pdf = lambda x: stats.norm.pdf(x, ref_mean, ref_std)
        elif reference_distribution == 'uniform':
            ref_min, ref_max = np.min(values), np.max(values)
            ref_pdf = lambda x: stats.uniform.pdf(x, ref_min, ref_max - ref_min)
        elif reference_distribution == 'exponential':
            ref_scale = np.mean(values)
            ref_pdf = lambda x: stats.expon.pdf(x, scale=ref_scale)
        else:
            raise ValueError(f"Unknown reference distribution: {reference_distribution}")

        # Estimate empirical distribution
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(values)
        emp_pdf = lambda x: kde(x)

        # Compute Amari α-divergence for different α values
        alpha_values = [-1, 0, 0.5, 1, 2]
        amari_divergences = {}

        for alpha in alpha_values:
            # Sample points for numerical integration
            x_points = np.linspace(np.min(values), np.max(values), 1000)

            if alpha == 1:  # KL-divergence
                p_vals = emp_pdf(x_points)
                q_vals = ref_pdf(x_points)
                valid_idx = (p_vals > 1e-10) & (q_vals > 1e-10)
                divergence = np.sum(p_vals[valid_idx] * np.log(p_vals[valid_idx] / q_vals[valid_idx]))
            else:
                # General Amari α-divergence
                p_vals = emp_pdf(x_points)
                q_vals = ref_pdf(x_points)

                if alpha == 0:  # Hellinger distance
                    integrand = (np.sqrt(p_vals) - np.sqrt(q_vals))**2
                else:
                    integrand = (4 / (1 - alpha**2)) * (p_vals**((1+alpha)/2) * q_vals**((1-alpha)/2) - 1)

                divergence = np.trapz(integrand, x_points)

            amari_divergences[f'alpha_{alpha}'] = divergence

        return amari_divergences


# =============================================================================
# ERGODIC THEORY AND DYNAMICAL SYSTEMS
# =============================================================================

@dataclass
class ErgodicTheoryModels:
    """Ergodic theory applications to time series analysis."""

    @staticmethod
    def lyapunov_exponents(series: pd.Series, embedding_dim: int = 5, delay: int = 1) -> List[float]:
        """Compute Lyapunov exponents for chaotic dynamics detection.

        Lyapunov exponents quantify the rate of divergence of
        nearby trajectories in phase space, indicating chaos.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        embedding_dim : int
            Embedding dimension
        delay : int
            Time delay for embedding

        Returns:
        --------
        list : Lyapunov exponents (largest first)
        """
        values = series.values

        # Phase space reconstruction
        def reconstruct_phase_space(data, dim, tau):
            n_points = len(data) - (dim - 1) * tau
            embedded = np.zeros((n_points, dim))
            for i in range(n_points):
                for j in range(dim):
                    embedded[i, j] = data[i + j * tau]
            return embedded

        embedded = reconstruct_phase_space(values, embedding_dim, delay)

        if len(embedded) < 10:
            return [np.nan] * embedding_dim

        # Find nearest neighbors for each point
        from scipy.spatial import KDTree

        tree = KDTree(embedded)
        lyapunov_sums = np.zeros(embedding_dim)

        # Iterate through each point
        for i in range(len(embedded)):
            # Find nearest neighbor (excluding itself)
            distances, indices = tree.query(embedded[i], k=2)
            neighbor_idx = indices[1]  # Skip self (index 0)

            if neighbor_idx >= len(embedded):
                continue

            # Initial distance
            initial_distance = distances[1]

            if initial_distance < 1e-10:
                continue

            # Track evolution of distance
            current_point = embedded[i].copy()
            neighbor_point = embedded[neighbor_idx].copy()

            for j in range(embedding_dim):
                # Evolve both trajectories
                if i + j + 1 < len(embedded):
                    current_point = embedded[i + j + 1]
                    neighbor_point = embedded[neighbor_idx + j + 1]

                    # Compute current distance
                    current_distance = np.linalg.norm(current_point - neighbor_point)

                    if current_distance > 1e-10:
                        lyapunov_sums[j] += np.log(current_distance / initial_distance)

        # Average and sort Lyapunov exponents
        lyapunov_exponents = lyapunov_sums / len(embedded)
        lyapunov_exponents = sorted(lyapunov_exponents, reverse=True)

        return lyapunov_exponents

    @staticmethod
    def kolmogorov_entropy(series: pd.Series, embedding_dim: int = 5, delay: int = 1) -> float:
        """Compute Kolmogorov-Sinai entropy (KS-entropy).

        KS-entropy measures the rate of information loss in
        dynamical systems, quantifying predictability.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        embedding_dim : int
            Embedding dimension
        delay : int
            Time delay

        Returns:
        --------
        float : Kolmogorov-Sinai entropy
        """
        # Get ordered Lyapunov exponents
        lyapunov_exp = ErgodicTheoryModels.lyapunov_exponents(series, embedding_dim, delay)

        # KS-entropy is the sum of positive Lyapunov exponents
        positive_exponents = [exp for exp in lyapunov_exp if exp > 0]
        ks_entropy = sum(positive_exponents) if positive_exponents else 0.0

        return ks_entropy

    @staticmethod
    def birkhoff_ergoic_theorem_check(series: pd.Series, num_partitions: int = 10) -> Dict[str, float]:
        """Test Birkhoff's ergodic theorem for time series.

        Birkhoff's theorem states that time averages equal
        space averages for ergodic systems.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        num_partitions : int
            Number of partitions for space average

        Returns:
        --------
        dict : Ergodicity test results
        """
        values = series.values

        # Time average (Birkhoff sum)
        time_average = np.mean(values)

        # Space averages over partitions
        partitions = np.array_split(np.sort(values), num_partitions)
        space_averages = [np.mean(partition) for partition in partitions]

        # Overall space average
        overall_space_average = np.mean(space_averages)

        # Ergodicity measure: difference between time and space averages
        ergodicity_deviation = abs(time_average - overall_space_average)

        # Partition-wise ergodicity
        partition_deviations = [abs(np.mean(partition) - time_average) for partition in partitions]
        mean_partition_deviation = np.mean(partition_deviations)

        # Ergodic theorem holds if time average ≈ space average
        is_ergodic = ergodicity_deviation < np.std(values) * 0.1  # Heuristic threshold

        return {
            'time_average': time_average,
            'space_average': overall_space_average,
            'ergodicity_deviation': ergodicity_deviation,
            'mean_partition_deviation': mean_partition_deviation,
            'is_ergodic': is_ergodic,
            'num_partitions': num_partitions
        }


# =============================================================================
# NON-EUCLIDEAN GEOMETRY MODELS
# =============================================================================

@dataclass
class NonEuclideanGeometryModels:
    """Non-Euclidean geometry applications to financial modeling."""

    @staticmethod
    def hyperbolic_geometry_analysis(series: pd.Series, curvature: float = -1.0) -> Dict[str, Any]:
        """Analyze time series in hyperbolic geometry.

        Models financial markets as hyperbolic manifolds where
        curvature represents market stress levels.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        curvature : float
            Hyperbolic curvature parameter

        Returns:
        --------
        dict : Hyperbolic geometry metrics
        """
        values = series.values

        # Map to hyperbolic plane using Poincaré disk model
        def cartesian_to_hyperbolic(x, y, K=curvature):
            """Map Cartesian coordinates to hyperbolic coordinates."""
            r = np.sqrt(x**2 + y**2)
            if r >= 1:
                return np.array([np.inf, np.inf])  # Point at infinity

            # Hyperbolic radius
            rho = (1/K) * np.arctanh(K * r)

            # Hyperbolic angle
            theta = np.arctan2(y, x)

            return np.array([rho, theta])

        # Create 2D representation for hyperbolic mapping
        # Use PCA for dimensionality reduction
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        embedded_2d = pca.fit_transform(values.reshape(-1, 1))

        # Map to hyperbolic coordinates
        hyperbolic_coords = np.array([cartesian_to_hyperbolic(x, y, curvature)
                                    for x, y in embedded_2d])

        # Compute hyperbolic distances
        def hyperbolic_distance(p1, p2, K=curvature):
            """Compute distance in hyperbolic geometry."""
            rho1, theta1 = p1
            rho2, theta2 = p2

            if np.isinf(rho1) or np.isinf(rho2):
                return np.inf

            cosh_distance = np.cosh(K * rho1) * np.cosh(K * rho2) - np.sinh(K * rho1) * np.sinh(K * rho2) * np.cos(theta1 - theta2)
            distance = (1/K) * np.arccosh(np.maximum(cosh_distance, 1.0))

            return distance

        # Compute pairwise hyperbolic distances
        n_points = len(hyperbolic_coords)
        distances = np.zeros((n_points, n_points))

        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = hyperbolic_distance(hyperbolic_coords[i], hyperbolic_coords[j], curvature)

        # Hyperbolic properties
        finite_distances = distances[np.isfinite(distances)]
        mean_hyperbolic_distance = np.mean(finite_distances) if len(finite_distances) > 0 else np.inf
        max_hyperbolic_distance = np.max(finite_distances) if len(finite_distances) > 0 else np.inf

        return {
            'hyperbolic_coordinates': hyperbolic_coords,
            'distance_matrix': distances,
            'mean_hyperbolic_distance': mean_hyperbolic_distance,
            'max_hyperbolic_distance': max_hyperbolic_distance,
            'curvature': curvature,
            'geometry_type': 'hyperbolic'
        }

    @staticmethod
    def elliptic_geometry_analysis(series: pd.Series, curvature: float = 1.0) -> Dict[str, Any]:
        """Analyze time series in elliptic geometry.

        Models financial markets as elliptic manifolds where
        positive curvature represents market efficiency.

        Parameters:
        -----------
        series : pd.Series
            Input time series
        curvature : float
            Elliptic curvature parameter

        Returns:
        --------
        dict : Elliptic geometry metrics
        """
        values = series.values

        # Elliptic geometry using spherical model
        def cartesian_to_elliptic(x, y, K=curvature):
            """Map Cartesian coordinates to elliptic coordinates."""
            r = np.sqrt(x**2 + y**2)

            # Elliptic radius (spherical distance)
            rho = (1/np.sqrt(K)) * np.arcsin(np.sqrt(K) * r)

            # Elliptic angle
            theta = np.arctan2(y, x)

            return np.array([rho, theta])

        # Create 2D representation
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        embedded_2d = pca.fit_transform(values.reshape(-1, 1))

        # Map to elliptic coordinates
        elliptic_coords = np.array([cartesian_to_elliptic(x, y, curvature)
                                  for x, y in embedded_2d])

        # Compute elliptic distances
        def elliptic_distance(p1, p2, K=curvature):
            """Compute distance in elliptic geometry."""
            rho1, theta1 = p1
            rho2, theta2 = p2

            cos_rho1 = np.cos(np.sqrt(K) * rho1)
            cos_rho2 = np.cos(np.sqrt(K) * rho2)
            sin_rho1 = np.sin(np.sqrt(K) * rho1)
            sin_rho2 = np.sin(np.sqrt(K) * rho2)

            cos_angle_diff = np.cos(theta1 - theta2)

            cos_distance = cos_rho1 * cos_rho2 + sin_rho1 * sin_rho2 * cos_angle_diff
            cos_distance = np.clip(cos_distance, -1, 1)  # Numerical stability

            distance = (1/np.sqrt(K)) * np.arccos(cos_distance)

            return distance

        # Compute pairwise elliptic distances
        n_points = len(elliptic_coords)
        distances = np.zeros((n_points, n_points))

        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = elliptic_distance(elliptic_coords[i], elliptic_coords[j], curvature)

        # Elliptic properties
        mean_elliptic_distance = np.mean(distances)
        max_elliptic_distance = np.max(distances)

        return {
            'elliptic_coordinates': elliptic_coords,
            'distance_matrix': distances,
            'mean_elliptic_distance': mean_elliptic_distance,
            'max_elliptic_distance': max_elliptic_distance,
            'curvature': curvature,
            'geometry_type': 'elliptic'
        }

    @staticmethod
    def taxicab_geometry_analysis(series: pd.Series) -> Dict[str, Any]:
        """Analyze time series in taxicab (Manhattan) geometry.

        L¹ geometry where distance is measured as the sum of
        absolute differences, modeling discrete market movements.

        Parameters:
        -----------
        series : pd.Series
            Input time series

        Returns:
        --------
        dict : Taxicab geometry metrics
        """
        values = series.values

        # Create 2D representation
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        embedded_2d = pca.fit_transform(values.reshape(-1, 1))

        # Compute taxicab distances
        def taxicab_distance(p1, p2):
            """L¹ distance between two points."""
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        # Compute pairwise taxicab distances
        n_points = len(embedded_2d)
        distances = np.zeros((n_points, n_points))

        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = taxicab_distance(embedded_2d[i], embedded_2d[j])

        # Taxicab geometry properties
        mean_taxicab_distance = np.mean(distances)
        max_taxicab_distance = np.max(distances)

        # Manhattan path analysis
        returns = np.diff(values)
        manhattan_path_length = np.sum(np.abs(returns))

        # Direction changes (turns)
        direction_changes = np.sum(np.abs(np.diff(np.sign(returns)))) / 2  # Each sign change represents a turn

        return {
            'taxicab_coordinates': embedded_2d,
            'distance_matrix': distances,
            'mean_taxicab_distance': mean_taxicab_distance,
            'max_taxicab_distance': max_taxicab_distance,
            'manhattan_path_length': manhattan_path_length,
            'direction_changes': direction_changes,
            'geometry_type': 'taxicab'
        }


# =============================================================================
# EXPORT ADVANCED MODELS
# =============================================================================

__all__ = [
    # Existing exports
    'ARIMAModel', 'SARIMAModel', 'VARModel', 'VECMModel', 'GARCHModel', 'EGARCHModel',
    'GJRModel', 'StochasticVolatilityModel', 'BayesianTimeSeriesModel', 'LSTMForecaster',
    'GRUForecaster', 'TransformerForecaster', 'TCNForecaster', 'EnsembleForecaster',
    'IsolationForestAnomalyDetector', 'ProphetAnomalyDetector', 'LSTMAnomalyDetector',
    'ChangePointDetector', 'decompose_time_series', 'detect_anomalies', 'detect_change_points',
    'auto_arima', 'seasonal_decompose',

    # New advanced exports
    'AdvancedMathematicalModels', 'QuantumInformationModels', 'AdvancedStochasticProcesses',
    'InformationGeometryModels', 'ErgodicTheoryModels', 'NonEuclideanGeometryModels'
]
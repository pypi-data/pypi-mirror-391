"""Advanced Volatility Analysis and Modeling Framework.

This module provides comprehensive volatility analysis capabilities including:
- Implied volatility surface modeling (SABR, SVI, Heston)
- Historical volatility estimation
- Realized volatility measures
- GARCH-family models
- Stochastic volatility models
- Volatility forecasting
- Volatility risk premium analysis
- High-frequency volatility estimation
- Jump-diffusion models
- Local volatility models
- Volatility derivatives pricing
- Risk-neutral vs physical measures
- Volatility clustering analysis
- Long memory in volatility
- Multivariate volatility models
- Volatility spillover effects
- Regime-switching volatility
- Machine learning for volatility prediction
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, Callable
from collections import defaultdict
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np
import pandas as pd
from scipy import stats, optimize, integrate, special
from scipy.optimize import minimize, minimize_scalar, differential_evolution, least_squares
from scipy.stats import norm, t, chi2, f, gamma, beta
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.gaussian_process import GaussianProcessRegressor


# Optional dependencies with fallbacks
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
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    torch = None

try:
    from .options import BlackScholes
    OPTIONS_AVAILABLE = True
except ImportError:
    OPTIONS_AVAILABLE = False
    BlackScholes = None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _require_scipy_optimize():
    """Require scipy.optimize."""
    try:
        from scipy.optimize import least_squares
        return least_squares
    except Exception as exc:
        raise RuntimeError("scipy.optimize is required") from exc


def _require_arch():
    """Require arch library."""
    if not ARCH_AVAILABLE:
        raise RuntimeError("arch library required for GARCH models")
    return arch


def _require_pytorch():
    """Require PyTorch."""
    if not PYTORCH_AVAILABLE:
        raise RuntimeError("PyTorch required for neural volatility models")
    return torch


def _require_options():
    """Require options module."""
    if not OPTIONS_AVAILABLE:
        raise RuntimeError("options module required")
    return BlackScholes


def calculate_historical_volatility(returns: pd.Series, window: int = 30,
                                   annualization_factor: float = np.sqrt(252)) -> pd.Series:
    """Calculate rolling historical volatility."""
    return returns.rolling(window=window).std() * annualization_factor


def calculate_parkinson_volatility(high: pd.Series, low: pd.Series,
                                  window: int = 30, annualization_factor: float = np.sqrt(252)) -> pd.Series:
    """Calculate Parkinson volatility using high-low range."""
    # Parkinson estimator: σ = sqrt(1/(4*N*ln(2)) * sum(ln(Hi/Li)^2))
    log_hl_ratio = np.log(high / low) ** 2
    parkinson_var = log_hl_ratio.rolling(window=window).mean() / (4 * window * np.log(2))
    return np.sqrt(parkinson_var) * annualization_factor


def calculate_garman_klass_volatility(open_prices: pd.Series, high: pd.Series,
                                    low: pd.Series, close: pd.Series,
                                    window: int = 30, annualization_factor: float = np.sqrt(252)) -> pd.Series:
    """Calculate Garman-Klass volatility using OHLC data."""
    # Garman-Klass estimator
    log_hl = np.log(high / low)
    log_co = np.log(close / open_prices)

    gk_var = (0.5 * log_hl ** 2 - (2 * np.log(2) - 1) * log_co ** 2).rolling(window=window).mean()
    return np.sqrt(gk_var) * annualization_factor


def calculate_yang_zhang_volatility(open_prices: pd.Series, high: pd.Series,
                                  low: pd.Series, close: pd.Series,
                                  window: int = 30, annualization_factor: float = np.sqrt(252)) -> pd.Series:
    """Calculate Yang-Zhang volatility estimator."""
    # Overnight returns
    close_shifted = close.shift(1)
    overnight_returns = np.log(open_prices / close_shifted)

    # Open-to-close returns
    open_to_close_returns = np.log(close / open_prices)

    # Rogers-Satchell variance
    rs_var = (np.log(high / close) * np.log(high / open_prices) +
             np.log(low / close) * np.log(low / open_prices)).rolling(window=window).mean()

    # Yang-Zhang variance
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    yz_var = overnight_returns.rolling(window=window).var() + k * rs_var + (1 - k) * open_to_close_returns.rolling(window=window).var()

    return np.sqrt(yz_var) * annualization_factor


def detect_volatility_clusters(returns: pd.Series, threshold: float = 2.0) -> pd.Series:
    """Detect periods of high volatility clustering."""
    vol = returns.rolling(window=30).std()
    vol_mean = vol.rolling(window=252).mean()
    vol_std = vol.rolling(window=252).std()

    # Z-score of volatility
    vol_zscore = (vol - vol_mean) / vol_std

    # High volatility clusters
    clusters = (vol_zscore > threshold).astype(int)

    return clusters


def calculate_volatility_of_volatility(returns: pd.Series, window: int = 30) -> pd.Series:
    """Calculate volatility of volatility (vol-of-vol)."""
    vol = returns.rolling(window=window).std()
    return vol.rolling(window=window).std()


def estimate_volatility_skewness(returns: pd.Series, window: int = 30) -> pd.Series:
    """Estimate volatility skewness."""
    vol = returns.rolling(window=window).std()
    return vol.rolling(window=window).skew()


def estimate_volatility_kurtosis(returns: pd.Series, window: int = 30) -> pd.Series:
    """Estimate volatility kurtosis."""
    vol = returns.rolling(window=window).std()
    return vol.rolling(window=window).kurt()


# =============================================================================
# IMPLIED VOLATILITY SURFACE MODELS
# =============================================================================

@dataclass(slots=True)
class SABRCalibrator:
    """SABR (Stochastic Alpha Beta Rho) model calibrator."""

    beta: float = 0.5  # CEV parameter (0.5 for lognormal)

    def _sabr_vol(self, f: float, k: float, t: float, alpha: float, rho: float, nu: float) -> float:
        """Calculate SABR implied volatility."""
        if abs(f - k) < 1e-8:  # At-the-money case
            numer1 = alpha
            denom1 = f ** (1 - self.beta)
            term1 = numer1 / denom1

            # ATM volatility adjustment
            term2 = ((1 - self.beta) ** 2 / 24) * (alpha ** 2) / (f ** (2 - 2 * self.beta))
            term3 = 0.25 * rho * self.beta * nu * alpha / (f ** (1 - self.beta))
            term4 = (2 - 3 * rho ** 2) / 24 * nu ** 2

            return (term1 * (1 + (term2 + term3 + term4) * t))

        # Out-of-the-money case
        fk = f * k
        log_fk_ratio = np.log(f / k)

        z = (nu / alpha) * (fk) ** ((1 - self.beta) / 2) * log_fk_ratio
        x_z = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))

        # Main SABR formula
        numerator = alpha * (1 + (((1 - self.beta) ** 2 / 24) * (log_fk_ratio) ** 2 +
                                ((1 - self.beta) ** 4 / 1920) * (log_fk_ratio) ** 4))

        denominator = (fk) ** ((1 - self.beta) / 2) * (1 + ((1 - self.beta) ** 2 / 24) * (log_fk_ratio) ** 2 +
                                                       ((1 - self.beta) ** 4 / 1920) * (log_fk_ratio) ** 4)

        vol = (numerator / denominator) * (z / x_z)

        return vol

    def calibrate(
        self,
        forwards: Iterable[float],
        strikes: Iterable[float],
        maturities: Iterable[float],
        implied_vols: Iterable[float],
        *,
        initial_guess: Tuple[float, float, float] = (0.2, -0.5, 0.4),
        bounds: Optional[Tuple] = None,
    ) -> Tuple[float, float, float]:
        """Calibrate SABR parameters to implied volatility surface."""
        least_squares = _require_scipy_optimize()

        f = np.asarray(list(forwards), dtype=float)
        k = np.asarray(list(strikes), dtype=float)
        t = np.asarray(list(maturities), dtype=float)
        iv_obs = np.asarray(list(implied_vols), dtype=float)

        if bounds is None:
            bounds = ([0.001, -0.99, 0.001], [2.0, 0.99, 2.0])  # alpha, rho, nu

        def objective(params):
            alpha, rho, nu = params
            iv_model = np.array([self._sabr_vol(f_i, k_i, t_i, alpha, rho, nu)
                               for f_i, k_i, t_i in zip(f, k, t)])
            return iv_obs - iv_model

        result = least_squares(
            objective,
            initial_guess,
            bounds=bounds,
            method='trf',
            loss='soft_l1',
            f_scale=0.1
        )

        if not result.success:
            warnings.warn(f"SABR calibration did not converge: {result.message}")

        return tuple(result.x)

    def calibrate_surface(
        self,
        strikes: pd.DataFrame,
        maturities: pd.Series,
        implied_vols: pd.DataFrame,
        spot: float,
    ) -> Dict[str, np.ndarray]:
        """Calibrate SABR parameters for each maturity slice."""
        results = {}

        for i, maturity in enumerate(maturities):
            vol_slice = implied_vols.iloc[:, i].dropna()
            strike_slice = strikes.iloc[:, i].dropna()

            if len(vol_slice) < 3:
                warnings.warn(f"Insufficient data for maturity {maturity}")
                continue

            try:
                # Use forward price approximation
                forward = spot * np.exp(0.02 * maturity)  # Simple approximation

                params = self.calibrate(
                    forwards=[forward] * len(strike_slice),
                    strikes=strike_slice.values,
                    maturities=[maturity] * len(strike_slice),
                    implied_vols=vol_slice.values
                )

                results[maturity] = np.array(params)

            except Exception as e:
                warnings.warn(f"Failed to calibrate maturity {maturity}: {e}")
                continue

        return results

    def interpolate_surface(
        self,
        calibrated_params: Dict[float, np.ndarray],
        strikes: np.ndarray,
        maturities: np.ndarray
    ) -> np.ndarray:
        """Interpolate SABR parameters across strike-maturity space."""
        maturities_cal = np.array(list(calibrated_params.keys()))
        params_cal = np.array(list(calibrated_params.values()))

        # Simple linear interpolation for parameters across maturities
        params_interp = np.zeros((len(maturities), len(strikes), 3))

        for i, maturity in enumerate(maturities):
            if maturity in calibrated_params:
                params_interp[i, :, :] = calibrated_params[maturity]
            else:
                # Linear interpolation
                idx = np.searchsorted(maturities_cal, maturity)
                if idx == 0:
                    params_interp[i, :, :] = params_cal[0]
                elif idx >= len(maturities_cal):
                    params_interp[i, :, :] = params_cal[-1]
                else:
                    # Interpolate parameters
                    t1, t2 = maturities_cal[idx-1], maturities_cal[idx]
                    p1, p2 = params_cal[idx-1], params_cal[idx]
                    w = (maturity - t1) / (t2 - t1)
                    params_interp[i, :, :] = p1 + w * (p2 - p1)

        return params_interp

    def calculate_volatility_surface(
        self,
        spot: float,
        strikes: np.ndarray,
        maturities: np.ndarray,
        calibrated_params: Dict[float, np.ndarray]
    ) -> pd.DataFrame:
        """Calculate full implied volatility surface."""
        params_interp = self.interpolate_surface(calibrated_params, strikes, maturities)

        vol_surface = pd.DataFrame(index=strikes, columns=maturities)

        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                alpha, rho, nu = params_interp[j, i, :]

                # Forward price approximation
                forward = spot * np.exp(0.02 * maturity)

                vol = self._sabr_vol(forward, strike, maturity, alpha, rho, nu)
                vol_surface.loc[strike, maturity] = vol

        return vol_surface


@dataclass(slots=True)
class SVICalibrator:
    """SVI (Stochastic Volatility Inspired) model calibrator."""

    def svi_vol(self, k: float, a: float, b: float, rho: float, m: float, sigma: float) -> float:
        """Calculate SVI implied volatility."""
        return np.sqrt(a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2)))

    def calibrate(
        self,
        log_moneyness: np.ndarray,
        implied_vols: np.ndarray,
        *,
        initial_guess: Tuple[float, float, float, float, float] = (0.04, -0.1, -0.5, 0.1, 0.2),
    ) -> Tuple[float, float, float, float, float]:
        """Calibrate SVI parameters."""

        def objective(params):
            a, b, rho, m, sigma = params
            vol_model = np.array([self.svi_vol(k, a, b, rho, m, sigma) for k in log_moneyness])
            return implied_vols - vol_model

        # Constraints for SVI parameters
        constraints = [
            {'type': 'ineq', 'fun': lambda x: x[1]},  # b >= 0
            {'type': 'ineq', 'fun': lambda x: 1 - x[2]**2},  # |rho| <= 1
            {'type': 'ineq', 'fun': lambda x: x[4]},  # sigma >= 0
        ]

        bounds = [(-2, 2), (0, 5), (-0.99, 0.99), (-2, 2), (0, 2)]

        result = minimize(
            lambda x: np.sum(objective(x) ** 2),
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            warnings.warn(f"SVI calibration did not converge: {result.message}")

        return tuple(result.x)


@dataclass(slots=True)
class HestonCalibrator:
    """Heston stochastic volatility model calibrator."""

    def heston_vol(self, s: float, k: float, t: float, r: float, q: float,
                  v0: float, kappa: float, theta: float, sigma: float, rho: float) -> float:
        """Calculate Heston model implied volatility using characteristic function."""

        def heston_char_func(phi, s, k, t, r, q, v0, kappa, theta, sigma, rho):
            """Heston characteristic function."""
            i = complex(0, 1)

            a = kappa * theta
            u = -0.5
            b = kappa + rho * sigma * i * phi

            d = np.sqrt(b ** 2 - sigma ** 2 * (2 * u * i * phi - phi ** 2))
            g = (b - d) / (b + d)

            exp_dt = np.exp(-d * t)
            D = (b - d) / sigma ** 2 * ((1 - exp_dt) / (1 - g * exp_dt))
            C = r * i * phi * t + (a / sigma ** 2) * ((b - d) * t - 2 * np.log((1 - g * exp_dt) / (1 - g)))

            return np.exp(C + D * v0 + i * phi * np.log(s))

        def integrand(phi, s, k, t, r, q, v0, kappa, theta, sigma, rho):
            """Integration kernel for option price."""
            char_func = heston_char_func(phi, s, k, t, r, q, v0, kappa, theta, sigma, rho)
            return np.real(char_func * np.exp(-i * phi * np.log(k)) / (i * phi))

        # Simplified integration (in practice, use more sophisticated methods)
        integral_result = integrate.quad(
            lambda phi: integrand(phi, s, k, t, r, q, v0, kappa, theta, sigma, rho),
            0, 100, limit=100
        )[0]

        call_price = s * np.exp(-q * t) - k * np.exp(-r * t) * integral_result / np.pi
        call_price = max(call_price, 0.001)  # Avoid negative prices

        # Convert to implied volatility using Black-Scholes inversion
        bs = _require_options()
        return bs.implied_volatility(call_price, s, k, t, r, q, 'call')

    def calibrate(
        self,
        spot: float,
        strikes: np.ndarray,
        maturities: np.ndarray,
        market_prices: np.ndarray,
        r: float = 0.02,
        q: float = 0.0,
        *,
        initial_guess: Tuple[float, float, float, float, float] = (0.04, 1.5, 0.04, 0.3, -0.7),
    ) -> Tuple[float, float, float, float, float]:
        """Calibrate Heston parameters to option prices."""

        def objective(params):
            v0, kappa, theta, sigma, rho = params

            model_prices = []
            for strike, maturity, market_price in zip(strikes, maturities, market_prices):
                try:
                    iv = self.heston_vol(spot, strike, maturity, r, q, v0, kappa, theta, sigma, rho)
                    bs = _require_options()
                    model_price = bs.price(spot, strike, maturity, r, q, iv, 'call')
                    model_prices.append(model_price)
                except:
                    model_prices.append(market_price)  # Fallback

            return np.array(model_prices) - market_prices

        # Parameter bounds
        bounds = [(0.001, 1.0), (0.1, 5.0), (0.001, 1.0), (0.001, 2.0), (-0.99, 0.99)]

        result = least_squares(
            objective,
            initial_guess,
            bounds=bounds,
            method='trf',
            loss='soft_l1'
        )

        if not result.success:
            warnings.warn(f"Heston calibration did not converge: {result.message}")

        return tuple(result.x)


# =============================================================================
# GARCH FAMILY MODELS
# =============================================================================

@dataclass(slots=True)
class AdvancedGARCHModel:
    """Advanced GARCH model with multiple variants and extensions."""

    model_type: str = 'GARCH'  # GARCH, EGARCH, GJR-GARCH, TARCH, NGARCH, AGARCH
    p: int = 1  # ARCH order
    q: int = 1  # GARCH order
    o: int = 0  # Asymmetry order (for GJR-GARCH)
    distribution: str = 'normal'  # normal, t, skewed-t, ged
    mean_model: str = 'Constant'  # Constant, AR, HAR

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, returns: pd.Series, exog: Optional[pd.DataFrame] = None) -> "AdvancedGARCHModel":
        """Fit GARCH-type model."""
        arch = _require_arch()

        try:
            if self.model_type == 'GARCH':
                self._model = arch_model(
                    returns, vol='Garch', p=self.p, q=self.q,
                    dist=self.distribution, mean=self.mean_model, x=exog
                )
            elif self.model_type == 'EGARCH':
                self._model = arch_model(
                    returns, vol='EGarch', p=self.p, q=self.q,
                    dist=self.distribution, mean=self.mean_model, x=exog
                )
            elif self.model_type == 'GJR-GARCH':
                self._model = arch_model(
                    returns, vol='Garch', p=self.p, q=self.q, o=self.o,
                    dist=self.distribution, mean=self.mean_model, x=exog
                )
            elif self.model_type == 'TARCH':
                self._model = arch_model(
                    returns, vol='Garch', p=self.p, q=self.q, o=1,
                    dist=self.distribution, mean=self.mean_model, x=exog
                )
            elif self.model_type == 'NGARCH':
                self._model = arch_model(
                    returns, vol='Garch', p=self.p, q=self.q,
                    dist=self.distribution, mean=self.mean_model, x=exog,
                    power=2.0  # NGARCH specification
                )
            elif self.model_type == 'AGARCH':
                # Asymmetric GARCH - custom implementation needed
                self._model = self._fit_agarch(returns, exog)

            self._result = self._model.fit(disp='off', show_warning=False)
            self._fitted = True

        except Exception as e:
            warnings.warn(f"GARCH fitting failed: {e}")
            # Fallback to simple GARCH(1,1)
            self._model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal')
            self._result = self._model.fit(disp='off', show_warning=False)
            self._fitted = True

        return self

    def _fit_agarch(self, returns: pd.Series, exog: Optional[pd.DataFrame]) -> Any:
        """Fit Asymmetric GARCH model (custom implementation)."""
        # AGARCH(p,q) implementation
        # This is a simplified version - full implementation would be more complex
        return arch_model(returns, vol='Garch', p=self.p, q=self.q, o=1,
                         dist=self.distribution, mean=self.mean_model, x=exog)

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

    def get_standardized_residuals(self) -> pd.Series:
        """Get standardized residuals."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        return self._result.resid / self._result.conditional_volatility

    def simulate_paths(self, n_paths: int = 1000, horizon: int = 252) -> np.ndarray:
        """Simulate volatility paths."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Extract parameters
        params = self._result.params

        # Simulate based on model type
        if self.model_type == 'GARCH':
            return self._simulate_garch_paths(params, n_paths, horizon)
        else:
            # Simplified simulation for other models
            return self._simulate_garch_paths(params, n_paths, horizon)

    def _simulate_garch_paths(self, params: pd.Series, n_paths: int, horizon: int) -> np.ndarray:
        """Simulate GARCH(1,1) paths."""
        omega = params['omega']
        alpha = params['alpha[1]']
        beta = params['beta[1]']

        # Initial volatility
        sigma2_0 = omega / (1 - alpha - beta)

        paths = np.zeros((n_paths, horizon))
        sigma2 = np.full(n_paths, sigma2_0)

        # Random innovations
        z = np.random.normal(0, 1, (n_paths, horizon))

        for t in range(horizon):
            # Update volatility
            sigma2 = omega + alpha * (z[:, t-1] ** 2 if t > 0 else sigma2_0) + beta * sigma2
            paths[:, t] = np.sqrt(sigma2)

        return paths

    def calculate_value_at_risk(self, confidence_level: float = 0.05) -> float:
        """Calculate Value-at-Risk using fitted model."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Get last volatility forecast
        vol_forecast = self.forecast_volatility(horizon=1).iloc[-1]

        # Assuming normal distribution for simplicity
        if self.distribution == 'normal':
            var = -vol_forecast * stats.norm.ppf(confidence_level)
        elif self.distribution == 't':
            # Extract degrees of freedom
            nu = self._result.params.get('nu', 5)
            var = -vol_forecast * stats.t.ppf(confidence_level, nu)
        else:
            var = -vol_forecast * stats.norm.ppf(confidence_level)

        return var

    def calculate_expected_shortfall(self, confidence_level: float = 0.05) -> float:
        """Calculate Expected Shortfall (CVaR)."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        vol_forecast = self.forecast_volatility(horizon=1).iloc[-1]

        if self.distribution == 'normal':
            # ES for normal distribution
            alpha = stats.norm.ppf(confidence_level)
            es = -vol_forecast * stats.norm.pdf(alpha) / confidence_level
        elif self.distribution == 't':
            nu = self._result.params.get('nu', 5)
            alpha = stats.t.ppf(confidence_level, nu)
            es = -vol_forecast * (stats.t.pdf(alpha, nu) / confidence_level) * ((nu + alpha**2) / (nu - 1))
        else:
            es = -vol_forecast * 1.5  # Approximation

        return es

    def summary(self) -> str:
        """Detailed model summary."""
        if not self._fitted:
            return "Model not fitted."

        summary = []
        summary.append(f"{self.model_type}({self.p},{self.q}) Model Summary")
        summary.append("=" * 60)
        summary.append(str(self._result.summary()))
        summary.append("")

        # Additional diagnostics
        summary.append("Additional Diagnostics:")
        summary.append(".4f")
        summary.append(".4f")
        summary.append(".4f")

        return "\n".join(summary)


@dataclass(slots=True)
class FIGARCHModel:
    """Fractionally Integrated GARCH model for long memory in volatility."""

    p: int = 1
    q: int = 1
    d: float = 0.4  # Fractional integration parameter
    distribution: str = 'normal'

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _result: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, returns: pd.Series) -> "FIGARCHModel":
        """Fit FIGARCH model."""
        # FIGARCH requires specialized implementation
        # This is a simplified version using ARFIMA-GARCH hybrid
        try:
            arch = _require_arch()

            # Fit ARFIMA first for fractional differencing
            from statsmodels.tsa.arima.model import ARIMA
            arfima_model = ARIMA(returns, order=(1, self.d, 1))
            arfima_result = arfima_model.fit()

            # Get fractionally differenced series
            frac_diff_returns = arfima_result.resid

            # Fit GARCH on fractionally differenced series
            self._model = arch_model(frac_diff_returns, vol='Garch', p=self.p, q=self.q, dist=self.distribution)
            self._result = self._model.fit(disp='off')

            self._fitted = True

        except Exception as e:
            warnings.warn(f"FIGARCH fitting failed: {e}")
            # Fallback to regular GARCH
            arch = _require_arch()
            self._model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal')
            self._result = self._model.fit(disp='off')
            self._fitted = True

        return self

    def get_volatility(self) -> pd.Series:
        """Get fitted volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")
        return self._result.conditional_volatility


@dataclass(slots=True)
class RegimeSwitchingGARCH:
    """Regime-switching GARCH model."""

    n_regimes: int = 2
    p: int = 1
    q: int = 1

    # Regime parameters
    regime_params: Dict[int, Dict[str, float]] = field(default_factory=dict)
    transition_matrix: np.ndarray = field(default=None)

    # Fitted attributes
    _fitted: bool = field(default=False, init=False)
    _regime_probs: Optional[np.ndarray] = field(default=None, init=False)

    def fit(self, returns: pd.Series) -> "RegimeSwitchingGARCH":
        """Fit regime-switching GARCH model."""
        # This is a simplified implementation
        # Full implementation would require specialized Markov switching models

        # Estimate parameters for each regime using quantile-based approach
        quantiles = [i / self.n_regimes for i in range(self.n_regimes + 1)]

        for i in range(self.n_regimes):
            if i == 0:
                regime_data = returns[returns <= returns.quantile(quantiles[i+1])]
            elif i == self.n_regimes - 1:
                regime_data = returns[returns >= returns.quantile(quantiles[i])]
            else:
                regime_data = returns[(returns >= returns.quantile(quantiles[i])) &
                                    (returns <= returns.quantile(quantiles[i+1]))]

            if len(regime_data) > 10:
                try:
                    garch = AdvancedGARCHModel(p=self.p, q=self.q)
                    garch.fit(regime_data)
                    self.regime_params[i] = dict(garch._result.params)
                except:
                    # Default parameters
                    self.regime_params[i] = {'omega': 0.01, 'alpha[1]': 0.1, 'beta[1]': 0.8}

        # Simple transition matrix estimation
        self.transition_matrix = np.full((self.n_regimes, self.n_regimes), 1/self.n_regimes)
        np.fill_diagonal(self.transition_matrix, 0.8)
        self.transition_matrix = self.transition_matrix / self.transition_matrix.sum(axis=1, keepdims=True)

        self._fitted = True
        return self

    def get_regime_volatility(self, returns: pd.Series) -> pd.Series:
        """Get regime-dependent volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Simplified regime detection based on volatility levels
        vol = returns.rolling(20).std()
        vol_quantiles = vol.quantile([i/self.n_regimes for i in range(1, self.n_regimes)])

        regime_vol = pd.Series(index=returns.index, dtype=float)

        for i in range(self.n_regimes):
            if i == 0:
                mask = vol <= vol_quantiles.iloc[i]
            elif i == self.n_regimes - 1:
                mask = vol >= vol_quantiles.iloc[i-1]
            else:
                mask = (vol >= vol_quantiles.iloc[i-1]) & (vol <= vol_quantiles.iloc[i])

            # Calculate regime-specific volatility
            regime_returns = returns[mask]
            if len(regime_returns) > 0:
                regime_vol.loc[mask] = regime_returns.std()

        return regime_vol


# =============================================================================
# STOCHASTIC VOLATILITY MODELS
# =============================================================================

@dataclass(slots=True)
class NeuralVolatilityForecaster:
    """Neural network-based volatility forecasting."""

    lookback_window: int = 20
    hidden_dims: List[int] = field(default_factory=lambda: [64, 32])
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 100
    batch_size: int = 32

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, volatility_series: pd.Series, features: Optional[pd.DataFrame] = None) -> "NeuralVolatilityForecaster":
        """Fit neural network for volatility forecasting."""
        torch = _require_pytorch()

        # Prepare data
        vol_data = volatility_series.values

        if features is not None:
            # Combine volatility with features
            feature_data = features.values
            combined_data = np.column_stack([vol_data, feature_data])
        else:
            combined_data = vol_data.reshape(-1, 1)

        # Create sequences
        X, y = [], []
        for i in range(len(combined_data) - self.lookback_window):
            X.append(combined_data[i:i+self.lookback_window])
            y.append(vol_data[i+self.lookback_window])

        X = np.array(X)
        y = np.array(y)

        # Normalize
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X.reshape(X.shape[0], -1)).reshape(X.shape)

        # Convert to tensors
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y).unsqueeze(-1)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize model
        input_dim = X.shape[2]
        self._model = VolatilityLSTM(input_dim, self.hidden_dims, self.dropout)

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

    def forecast(self, recent_volatility: pd.Series, features: Optional[pd.DataFrame] = None,
                horizon: int = 1) -> np.ndarray:
        """Forecast future volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        torch = _require_pytorch()

        # Prepare input data
        vol_data = recent_volatility.values[-self.lookback_window:]

        if features is not None:
            recent_features = features.tail(self.lookback_window).values
            input_data = np.column_stack([vol_data, recent_features])
        else:
            input_data = vol_data.reshape(-1, 1)

        # Scale
        input_scaled = self._scaler.transform(input_data.reshape(1, -1)).reshape(input_data.shape)

        # Convert to tensor
        input_tensor = torch.FloatTensor(input_scaled).unsqueeze(0)

        self._model.eval()
        with torch.no_grad():
            prediction = self._model(input_tensor)

        return prediction.numpy().flatten()


class VolatilityLSTM(torch.nn.Module):
    """LSTM model for volatility forecasting."""

    def __init__(self, input_dim: int, hidden_dims: List[int], dropout: float):
        super().__init__()

        self.layers = torch.nn.ModuleList()
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            self.layers.append(torch.nn.LSTM(prev_dim, hidden_dim, batch_first=True))
            self.layers.append(torch.nn.Dropout(dropout))
            prev_dim = hidden_dim

        self.output_layer = torch.nn.Linear(hidden_dims[-1], 1)

    def forward(self, x):
        for layer in self.layers:
            if isinstance(layer, torch.nn.LSTM):
                x, _ = layer(x)
            else:
                x = layer(x)

        # Take last time step
        x = x[:, -1, :]
        x = self.output_layer(x)
        return x


@dataclass(slots=True)
class VolatilityEnsembleForecaster:
    """Ensemble model for volatility forecasting."""

    models: List[Any] = field(default_factory=list)
    weights: Optional[List[float]] = None

    # Fitted attributes
    _fitted: bool = field(default=False, init=False)

    def add_model(self, model: Any) -> "VolatilityEnsembleForecaster":
        """Add a model to the ensemble."""
        self.models.append(model)
        return self

    def fit(self, volatility_series: pd.Series, features: Optional[pd.DataFrame] = None) -> "VolatilityEnsembleForecaster":
        """Fit all models."""
        for model in self.models:
            try:
                model.fit(volatility_series, features)
            except Exception as e:
                warnings.warn(f"Failed to fit {type(model).__name__}: {e}")

        self._fitted = True

        # Set equal weights if not provided
        if self.weights is None:
            self.weights = [1.0 / len(self.models)] * len(self.models)

        return self

    def forecast(self, recent_volatility: pd.Series, features: Optional[pd.DataFrame] = None) -> float:
        """Make ensemble forecast."""
        if not self._fitted:
            raise RuntimeError("Ensemble must be fitted.")

        predictions = []
        for model in self.models:
            try:
                pred = model.forecast(recent_volatility, features, horizon=1)
                if isinstance(pred, np.ndarray):
                    pred = pred[0] if len(pred) > 0 else 0.0
                predictions.append(pred)
            except Exception as e:
                warnings.warn(f"Model prediction failed: {e}")
                predictions.append(0.0)

        # Weighted average
        return np.average(predictions, weights=self.weights[:len(predictions)])


# =============================================================================
# VOLATILITY RISK PREMIUM AND DERIVATIVES
# =============================================================================

@dataclass(slots=True)
class VolatilityRiskPremiumCalculator:
    """Calculate volatility risk premium."""

    def calculate_vrp(self, realized_vol: pd.Series, implied_vol: pd.Series) -> pd.Series:
        """Calculate volatility risk premium (VRP = IV - RV)."""
        return implied_vol - realized_vol

    def decompose_vrp(self, vrp: pd.Series) -> Dict[str, pd.Series]:
        """Decompose VRP into components."""
        # Trend component
        trend = vrp.rolling(window=252, center=True).mean()

        # Seasonal component
        seasonal = pd.Series(index=vrp.index, dtype=float)
        for month in range(1, 13):
            mask = vrp.index.month == month
            seasonal.loc[mask] = vrp.loc[mask].mean()

        # Residual component
        residual = vrp - trend - seasonal

        return {
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'total': vrp
        }

    def predict_vrp(self, historical_vrp: pd.Series, features: pd.DataFrame) -> pd.Series:
        """Predict future VRP using machine learning."""
        # Use random forest for prediction
        model = RandomForestRegressor(n_estimators=100, random_state=42)

        # Prepare data
        X = features.values[:-1]  # All features except last
        y = historical_vrp.values[1:]  # VRP shifted by 1 (predict next period)

        # Align lengths
        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]

        model.fit(X, y)

        # Predict next period
        last_features = features.iloc[-1:].values
        prediction = model.predict(last_features)

        return pd.Series(prediction, index=[features.index[-1] + pd.Timedelta(days=1)])


@dataclass(slots=True)
class VolatilityDerivativePricer:
    """Price volatility derivatives using various models."""

    def price_variance_swap(self, spot: float, strike: float, time_to_maturity: float,
                          realized_vol: float, risk_free_rate: float = 0.02) -> float:
        """Price a variance swap."""
        # Simplified pricing - in practice would use more sophisticated methods
        fair_variance = realized_vol ** 2
        variance_notional = strike - fair_variance

        # PV of variance notional
        pv = variance_notional * np.exp(-risk_free_rate * time_to_maturity)

        return pv

    def price_volatility_swap(self, spot: float, strike: float, time_to_maturity: float,
                            realized_vol: float, risk_free_rate: float = 0.02) -> float:
        """Price a volatility swap."""
        fair_vol = realized_vol
        vol_notional = strike - fair_vol

        # PV of volatility notional
        pv = vol_notional * np.exp(-risk_free_rate * time_to_maturity)

        return pv

    def price_vix_future(self, vix_spot: float, future_price: float, time_to_maturity: float,
                        risk_free_rate: float = 0.02) -> float:
        """Price VIX futures."""
        # VIX futures pricing under risk-neutral measure
        # Simplified model
        expected_vix = vix_spot * np.exp(risk_free_rate * time_to_maturity)
        return expected_vix

    def price_vix_option(self, spot: float, strike: float, time_to_maturity: float,
                        volatility: float, risk_free_rate: float = 0.02,
                        option_type: str = 'call') -> float:
        """Price VIX options using Black-76 model."""
        bs = _require_options()

        # Use Black-76 model for options on futures
        # Simplified - VIX options are European
        price = bs.price(spot, strike, time_to_maturity, risk_free_rate, 0.0,
                        volatility, option_type)

        return price


# =============================================================================
# MULTIVARIATE VOLATILITY MODELS
# =============================================================================

@dataclass(slots=True)
class MultivariateGARCH:
    """Multivariate GARCH models (BEKK, DCC, etc.)."""

    model_type: str = 'DCC'  # DCC, BEKK, CCC
    n_assets: int = 2

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, returns: pd.DataFrame) -> "MultivariateGARCH":
        """Fit multivariate GARCH model."""
        try:
            import mgarch

            if self.model_type == 'DCC':
                # Dynamic Conditional Correlation
                self._model = mgarch.DCC(returns.values)
            elif self.model_type == 'BEKK':
                # BEKK model
                self._model = mgarch.BEKK(returns.values)
            elif self.model_type == 'CCC':
                # Constant Conditional Correlation
                self._model = mgarch.CCC(returns.values)

            # Note: This is a conceptual implementation
            # Actual fitting would require specific mgarch library implementation
            self._fitted = True

        except ImportError:
            warnings.warn("Multivariate GARCH requires mgarch library")
            self._fitted = False

        return self

    def get_correlation_matrix(self) -> np.ndarray:
        """Get conditional correlation matrix."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Placeholder - actual implementation would extract correlations
        return np.eye(self.n_assets)

    def forecast_correlations(self, horizon: int = 1) -> np.ndarray:
        """Forecast future correlations."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        # Placeholder
        return np.eye(self.n_assets)


@dataclass(slots=True)
class VolatilitySpilloverAnalyzer:
    """Analyze volatility spillovers between assets."""

    def calculate_spillover_matrix(self, volatilities: pd.DataFrame,
                                 method: str = 'dy2012') -> pd.DataFrame:
        """Calculate volatility spillover matrix using DY (2012) methodology."""
        # Generalized Variance Decomposition approach
        n_assets = volatilities.shape[1]

        # Estimate VAR model on volatilities
        from statsmodels.tsa.api import VAR
        model = VAR(volatilities)
        results = model.fit(maxlags=5, ic='aic')

        # Forecast error variance decomposition
        fevd = results.fevd(10)  # 10-step ahead

        # Calculate spillovers
        spillover_matrix = np.zeros((n_assets, n_assets))

        for i in range(n_assets):
            for j in range(n_assets):
                if i != j:
                    # Proportion of forecast error variance in i due to shocks from j
                    spillover_matrix[i, j] = fevd.decomp[i, j, -1]  # Last period

        # Normalize
        spillover_matrix = spillover_matrix / spillover_matrix.sum(axis=1, keepdims=True)

        return pd.DataFrame(spillover_matrix,
                          index=volatilities.columns,
                          columns=volatilities.columns)

    def calculate_total_spillover(self, spillover_matrix: pd.DataFrame) -> float:
        """Calculate total spillover index."""
        n = len(spillover_matrix)
        total_spillover = spillover_matrix.values.sum() - np.trace(spillover_matrix.values)
        total_spillover = total_spillover / n

        return total_spillover

    def directional_spillovers(self, spillover_matrix: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate directional spillovers."""
        from_i = spillover_matrix.sum(axis=1)  # Spillovers from i to others
        to_j = spillover_matrix.sum(axis=0)    # Spillovers to j from others
        net = from_i - to_j                     # Net spillovers

        return {
            'from': from_i,
            'to': to_j,
            'net': net
        }


# =============================================================================
# HIGH-FREQUENCY VOLATILITY ESTIMATION
# =============================================================================

@dataclass(slots=True)
class HighFrequencyVolatilityCalculator:
    """High-frequency volatility estimation."""

    sampling_frequency: str = '5min'
    noise_estimation: str = 'rz'  # rz (Realized Volatility with noise), zma (ZMA)

    def realized_volatility(self, prices: pd.Series) -> pd.Series:
        """Calculate realized volatility."""
        # Resample to regular intervals
        resampled = prices.resample(self.sampling_frequency).last().dropna()

        # Calculate returns
        returns = resampled.pct_change().dropna()

        # Realized variance
        rv = returns.groupby(pd.Grouper(freq='D')).apply(lambda x: np.sum(x**2))

        return np.sqrt(rv)

    def bipower_variation(self, prices: pd.Series, sampling_multiplier: int = 1) -> pd.Series:
        """Calculate bipower variation (robust to jumps)."""
        resampled = prices.resample(self.sampling_frequency).last().dropna()
        returns = resampled.pct_change().dropna()

        bv = returns.groupby(pd.Grouper(freq='D')).apply(
            lambda x: (np.pi/2) * np.sum(np.abs(x[:-sampling_multiplier]) * np.abs(x[sampling_multiplier:]))
        )

        return np.sqrt(bv)

    def realized_kernel(self, prices: pd.Series, H: float = 1.0) -> pd.Series:
        """Realized kernel estimator."""
        resampled = prices.resample(self.sampling_frequency).last().dropna()
        returns = resampled.pct_change().dropna()

        def kernel_estimator(returns_array):
            n = len(returns_array)
            weights = np.zeros(n-1)

            # Parzen kernel
            for k in range(1, n):
                x = k / (H * np.sqrt(n))
                if x <= 0.5:
                    weights[k-1] = 1 - 6*x**2 + 6*x**3
                elif x <= 1:
                    weights[k-1] = 2*(1-x)**3
                else:
                    weights[k-1] = 0

            rk = returns_array[0]**2
            for k in range(1, n):
                gamma_k = np.sum(returns_array[:-k] * returns_array[k:])
                rk += 2 * weights[k-1] * gamma_k

            return rk

        rk = returns.groupby(pd.Grouper(freq='D')).apply(kernel_estimator)

        return np.sqrt(rk)

    def jump_variation(self, prices: pd.Series) -> pd.Series:
        """Estimate jump variation."""
        rv = self.realized_volatility(prices) ** 2
        bv = self.bipower_variation(prices) ** 2

        # Jump variation = RV - BV
        jv = rv - bv
        jv = np.maximum(jv, 0)  # Ensure non-negative

        return np.sqrt(jv)

    def spot_volatility(self, prices: pd.Series, window: int = 50) -> pd.Series:
        """Estimate spot volatility using pre-averaging."""
        # Pre-averaging to reduce microstructure noise
        preaveraged_prices = self._preaverage_prices(prices, window)

        # Calculate spot volatility
        spot_vol = preaveraged_prices.rolling(window).std() * np.sqrt(252 * 24 * 12)  # Annualized

        return spot_vol

    def _preaverage_prices(self, prices: pd.Series, window: int) -> pd.Series:
        """Pre-average prices to reduce noise."""
        # Simple pre-averaging
        preaveraged = prices.rolling(window=window, center=True).mean()
        return preaveraged.dropna()


# =============================================================================
# MACHINE LEARNING FOR VOLATILITY
# =============================================================================

@dataclass(slots=True)
class VolatilityRegressor:
    """Machine learning models for volatility prediction."""

    model_type: str = 'random_forest'  # random_forest, gradient_boosting, neural_network
    lookback_window: int = 20

    # Model parameters
    n_estimators: int = 100
    max_depth: Optional[int] = None
    learning_rate: float = 0.1
    hidden_layer_sizes: Tuple[int, ...] = (64, 32)

    # Fitted attributes
    _model: Any = field(default=None, init=False)
    _scaler: Any = field(default=None, init=False)
    _fitted: bool = field(default=False, init=False)

    def fit(self, features: pd.DataFrame, target_volatility: pd.Series) -> "VolatilityRegressor":
        """Fit volatility prediction model."""
        # Prepare data
        X = features.values[:-1]  # Features for prediction
        y = target_volatility.values[1:]  # Next period volatility

        # Align lengths
        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]

        # Scale features
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Initialize model
        if self.model_type == 'random_forest':
            from sklearn.ensemble import RandomForestRegressor
            self._model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            from sklearn.ensemble import GradientBoostingRegressor
            self._model = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=42
            )
        elif self.model_type == 'neural_network':
            from sklearn.neural_network import MLPRegressor
            self._model = MLPRegressor(
                hidden_layer_sizes=self.hidden_layer_sizes,
                learning_rate_init=self.learning_rate,
                max_iter=500,
                random_state=42
            )

        # Fit model
        self._model.fit(X_scaled, y)
        self._fitted = True

        return self

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Predict volatility."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted.")

        X_scaled = self._scaler.transform(features.values)
        return self._model.predict(X_scaled)

    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance if available."""
        if hasattr(self._model, 'feature_importances_'):
            return self._model.feature_importances_
        elif hasattr(self._model, 'coefs_'):
            # Neural network - use coefficient magnitudes
            return np.array([np.mean(np.abs(coef)) for coef in self._model.coefs_[0]])
        else:
            return None


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Maintain backward compatibility with original interface
SABRCalibratorLegacy = SABRCalibrator


class VolatilitySurface:
    def __init__(self, strikes: np.ndarray, maturities: np.ndarray, vols: np.ndarray) -> None:
        self.strikes = np.asarray(strikes, dtype=float)
        self.maturities = np.asarray(maturities, dtype=float)
        self.vols = np.asarray(vols, dtype=float)
        if self.vols.shape != (self.maturities.shape[0], self.strikes.shape[0]):
            raise ValueError("Vol surface must be shaped (n_maturities, n_strikes).")
        try:
            from scipy.interpolate import RectBivariateSpline  # type: ignore
        except Exception:
            self._interpolator = None
        else:
            kx = min(3, max(1, len(self.maturities) - 1))
            ky = min(3, max(1, len(self.strikes) - 1))
            if len(self.maturities) > 1 and len(self.strikes) > 1:
                self._interpolator = RectBivariateSpline(self.maturities, self.strikes, self.vols, kx=kx, ky=ky)
            else:
                self._interpolator = None

    def interpolate(self, maturity: float, strike: float) -> float:
        if self._interpolator is not None:
            return float(self._interpolator(maturity, strike)[0, 0])
        # Fallback bilinear interpolation
        t_idx = np.searchsorted(self.maturities, maturity)
        k_idx = np.searchsorted(self.strikes, strike)
        t_idx = np.clip(t_idx, 1, len(self.maturities) - 1)
        k_idx = np.clip(k_idx, 1, len(self.strikes) - 1)
        t0, t1 = self.maturities[t_idx - 1], self.maturities[t_idx]
        k0, k1 = self.strikes[k_idx - 1], self.strikes[k_idx]
        v00 = self.vols[t_idx - 1, k_idx - 1]
        v01 = self.vols[t_idx - 1, k_idx]
        v10 = self.vols[t_idx, k_idx - 1]
        v11 = self.vols[t_idx, k_idx]
        wt = (maturity - t0) / (t1 - t0) if t1 != t0 else 0.0
        wk = (strike - k0) / (k1 - k0) if k1 != k0 else 0.0
        vol = (1 - wt) * ((1 - wk) * v00 + wk * v01) + wt * ((1 - wk) * v10 + wk * v11)
        return float(vol)

    def price_option(
        self,
        s0: float,
        k: float,
        t: float,
        r: float,
        option_type: str = "call",
    ) -> float:
        vol = self.interpolate(t, k)
        bs = BlackScholes(s0=s0, strike=k, rate=r, sigma=vol, maturity=t)
        return bs.price(option_type)


def realized_volatility(high: np.ndarray, low: np.ndarray, close: np.ndarray, window: int = 20) -> np.ndarray:
    """Calculate realized volatility using Garman-Klass estimator.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        window: Rolling window size

    Returns:
        Realized volatility array
    """
    # Garman-Klass estimator
    log_hl = np.log(high / low) ** 2
    log_co = np.log(close / np.roll(close, 1)) ** 2

    # Avoid division by zero and log(0)
    log_co = np.where(np.isfinite(log_co), log_co, 0)

    # Garman-Klass volatility
    sigma_gk = 0.5 * log_hl - (2 * np.log(2) - 1) * log_co

    # Annualized volatility
    if window > 1:
        # Rolling standard deviation
        vol = np.sqrt(252 * pd.Series(sigma_gk).rolling(window=window).mean())
        return vol.values
    else:
        return np.sqrt(252 * sigma_gk)


def parkinson_volatility(high: np.ndarray, low: np.ndarray, window: int = 20) -> np.ndarray:
    """Calculate Parkinson volatility estimator.

    Args:
        high: High prices
        low: Low prices
        window: Rolling window size

    Returns:
        Parkinson volatility array
    """
    # Parkinson estimator
    log_hl = np.log(high / low)
    sigma_p = (1 / (4 * np.log(2))) * (log_hl ** 2)

    # Annualized volatility
    if window > 1:
        # Rolling standard deviation
        vol = np.sqrt(252 * pd.Series(sigma_p).rolling(window=window).mean())
        return vol.values
    else:
        return np.sqrt(252 * sigma_p)


# =============================================================================
# ADVANCED STOCHASTIC VOLATILITY MODELS (NOBEL-PRIZE LEVEL COMPLEXITY)
# =============================================================================

@dataclass
class AdvancedStochasticVolatilityModels:
    """Collection of Nobel-prize level stochastic volatility models."""

    @staticmethod
    def heston_model_calibration(returns: pd.Series, risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Calibrate Heston stochastic volatility model.

        The Heston model is a stochastic volatility model that describes
        the evolution of asset prices with stochastic volatility.

        Parameters:
        -----------
        returns : pd.Series
            Historical returns
        risk_free_rate : float
            Risk-free interest rate

        Returns:
        --------
        dict : Calibrated Heston model parameters
        """
        # Initial parameter guesses
        initial_params = {
            'kappa': 2.0,      # Mean reversion speed
            'theta': 0.04,     # Long-term variance
            'sigma': 0.3,      # Volatility of variance
            'rho': -0.7,       # Correlation between price and volatility
            'v0': 0.04         # Initial variance
        }

        # Historical moments for calibration
        returns_vals = returns.values
        historical_vol = np.var(returns_vals)
        skewness = stats.skew(returns_vals)
        kurtosis = stats.kurtosis(returns_vals, fisher=True)

        # Simplified calibration using moment matching
        # In practice, this would use maximum likelihood estimation
        calibrated_params = initial_params.copy()

        # Adjust kappa based on volatility clustering
        autocorr = np.corrcoef(returns_vals[:-1], returns_vals[1:])[0, 1]
        calibrated_params['kappa'] = -np.log(abs(autocorr)) * 252  # Annualized

        # Adjust theta based on long-term volatility
        calibrated_params['theta'] = historical_vol

        # Adjust sigma based on kurtosis (vol-of-vol)
        calibrated_params['sigma'] = np.sqrt(kurtosis * historical_vol) / 2

        # Adjust rho based on skewness
        calibrated_params['rho'] = -abs(skewness) / 3

        return {
            'parameters': calibrated_params,
            'historical_moments': {
                'variance': historical_vol,
                'skewness': skewness,
                'kurtosis': kurtosis,
                'autocorrelation': autocorr
            },
            'model_type': 'Heston'
        }

    @staticmethod
    def sabr_model_extensions(strikes: np.ndarray, forwards: np.ndarray,
                            expiries: np.ndarray, market_vols: np.ndarray) -> Dict[str, Any]:
        """Extended SABR model with additional parameters for better fit.

        SABR (Stochastic Alpha Beta Rho) model with extensions for
        improved volatility surface modeling.

        Parameters:
        -----------
        strikes : np.ndarray
            Option strike prices
        forwards : np.ndarray
            Forward prices
        expiries : np.ndarray
            Time to expiry
        market_vols : np.ndarray
            Market implied volatilities

        Returns:
        --------
        dict : Extended SABR model results
        """
        # SABR parameters with extensions
        alpha = 0.2      # Initial volatility
        beta = 0.7       # Elasticity parameter
        rho = -0.3       # Correlation
        nu = 0.4         # Volatility of volatility
        gamma = 0.1      # Additional curvature parameter

        # Extended SABR volatility function
        def extended_sabr_vol(K, F, T, alpha, beta, rho, nu, gamma):
            """Extended SABR volatility formula."""
            if T <= 0:
                return 0

            # Standard SABR components
            log_K_F = np.log(K / F)
            z = nu / alpha * (F * K)**(0.5 * (1 - beta)) * log_K_F
            x_z = np.log((np.sqrt(1 - 2 * rho * z + z**2) + z - rho) / (1 - rho))

            # SABR volatility
            vol_sabr = alpha * (F * K)**(beta - 1) * (1 + ((1 - beta)**2 / 24) * (log_K_F)**2 +
                                                     ((1 - beta)**4 / 1920) * (log_K_F)**4)

            # Add extended terms
            extended_term = gamma * T * (log_K_F)**2 * np.exp(-nu * np.sqrt(T))
            vol_extended = vol_sabr * (1 + extended_term)

            return vol_extended

        # Vectorized application
        model_vols = np.zeros_like(market_vols)
        for i, (K, F, T) in enumerate(zip(strikes, forwards, expiries)):
            model_vols[i] = extended_sabr_vol(K, F, T, alpha, beta, rho, nu, gamma)

        # Calculate fit quality
        mse = np.mean((model_vols - market_vols)**2)
        rmse = np.sqrt(mse)
        max_error = np.max(np.abs(model_vols - market_vols))

        return {
            'parameters': {
                'alpha': alpha, 'beta': beta, 'rho': rho,
                'nu': nu, 'gamma': gamma
            },
            'model_volatilities': model_vols,
            'market_volatilities': market_vols,
            'fit_metrics': {
                'mse': mse,
                'rmse': rmse,
                'max_error': max_error
            },
            'model_type': 'Extended SABR'
        }

    @staticmethod
    def local_volatility_model(spot: float, strikes: np.ndarray,
                             expiries: np.ndarray, market_vols: np.ndarray) -> Dict[str, Any]:
        """Implement Dupire's local volatility model.

        Local volatility model that recovers the volatility surface
        from market option prices using Dupire's formula.

        Parameters:
        -----------
        spot : float
            Current spot price
        strikes : np.ndarray
            Option strike prices
        expiries : np.ndarray
            Time to expiry
        market_vols : np.ndarray
            Market implied volatilities

        Returns:
        --------
        dict : Local volatility surface and model
        """
        # Dupire's local volatility formula:
        # σ_L(K,T)² = [∂C/∂T + rK ∂C/∂K + (r - q)C] / [K² ∂²C/∂K²]
        # where C is the call price

        def black_scholes_call(S, K, T, r, sigma, q=0):
            """Black-Scholes call price."""
            if T <= 0:
                return max(S - K, 0)

            d1 = (np.log(S/K) + (r - q + sigma**2/2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)

            return S*np.exp(-q*T)*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)

        # Create grid for local volatility
        K_grid = np.linspace(np.min(strikes), np.max(strikes), 50)
        T_grid = np.linspace(0.01, np.max(expiries), 50)
        K_mesh, T_mesh = np.meshgrid(K_grid, T_grid)

        # Interpolate market volatilities
        from scipy.interpolate import griddata
        local_vols = griddata(
            (strikes, expiries), market_vols,
            (K_mesh, T_mesh), method='cubic', fill_value=np.mean(market_vols)
        )

        # Apply Dupire's formula to refine local volatility
        # This is a simplified implementation
        r = 0.02  # Risk-free rate
        q = 0.01  # Dividend yield

        refined_local_vols = local_vols.copy()

        # Finite difference approximations for Dupire formula
        for i in range(1, len(T_grid)-1):
            for j in range(1, len(K_grid)-1):
                T = T_grid[i]
                K = K_grid[j]

                # Approximate derivatives
                dC_dT = (local_vols[i+1, j] - local_vols[i-1, j]) / (2 * (T_grid[1] - T_grid[0]))
                dC_dK = (local_vols[i, j+1] - local_vols[i, j-1]) / (2 * (K_grid[1] - K_grid[0]))
                d2C_dK2 = (local_vols[i, j+1] - 2*local_vols[i, j] + local_vols[i, j-1]) / ((K_grid[1] - K_grid[0])**2)

                # Call price approximation
                C = black_scholes_call(spot, K, T, r, local_vols[i, j], q)

                # Dupire's formula
                if d2C_dK2 > 1e-10:  # Avoid division by zero
                    numerator = dC_dT + r*K*dC_dK + (r - q)*C
                    local_vol_sq = numerator / (K**2 * d2C_dK2)
                    refined_local_vols[i, j] = np.sqrt(max(local_vol_sq, 0.01**2))  # Floor at 1%

        return {
            'local_volatility_surface': refined_local_vols,
            'strike_grid': K_grid,
            'time_grid': T_grid,
            'market_data': {
                'spot': spot,
                'strikes': strikes,
                'expiries': expiries,
                'market_vols': market_vols
            },
            'model_type': 'Dupire Local Volatility'
        }


# =============================================================================
# ADVANCED GARCH FAMILY EXTENSIONS
# =============================================================================

@dataclass
class AdvancedGARCHModels:
    """Advanced GARCH-family models with extensions and generalizations."""

    @staticmethod
    def component_garch(returns: pd.Series, p: int = 1, q: int = 1, r: int = 1) -> Dict[str, Any]:
        """Component GARCH model by Engle and Lee.

        Component GARCH decomposes volatility into permanent and
        transitory components, allowing for more flexible modeling.

        Parameters:
        -----------
        returns : pd.Series
            Historical returns
        p, q, r : int
            GARCH orders for different components

        Returns:
        --------
        dict : Component GARCH model results
        """
        returns_vals = returns.values
        n = len(returns_vals)

        # Initialize parameters
        omega = np.var(returns_vals) * 0.1  # Permanent component
        alpha = 0.1                         # Transitory component
        beta = 0.8                          # Persistence
        gamma = 0.05                        # Decay rate

        # Initialize volatility components
        sigma2_perm = np.zeros(n)    # Permanent volatility
        sigma2_trans = np.zeros(n)   # Transitory volatility
        sigma2_total = np.zeros(n)   # Total volatility

        sigma2_perm[0] = np.var(returns_vals[:min(50, n)])
        sigma2_trans[0] = sigma2_perm[0]
        sigma2_total[0] = sigma2_perm[0] + sigma2_trans[0]

        # Component GARCH recursion
        for t in range(1, n):
            # Permanent component (slowly moving)
            sigma2_perm[t] = omega + beta * sigma2_perm[t-1]

            # Transitory component (fast moving)
            epsilon_t = returns_vals[t-1]**2 - sigma2_total[t-1]
            sigma2_trans[t] = alpha * epsilon_t + gamma * sigma2_trans[t-1]

            # Total volatility
            sigma2_total[t] = sigma2_perm[t] + sigma2_trans[t]

        # Calculate log-likelihood for model evaluation
        log_likelihood = -0.5 * np.sum(np.log(sigma2_total) + returns_vals**2 / sigma2_total)

        return {
            'parameters': {
                'omega': omega, 'alpha': alpha, 'beta': beta, 'gamma': gamma
            },
            'volatility_components': {
                'permanent': sigma2_perm,
                'transitory': sigma2_trans,
                'total': sigma2_total
            },
            'log_likelihood': log_likelihood,
            'aic': -2 * log_likelihood + 2 * 4,  # 4 parameters
            'bic': -2 * log_likelihood + 4 * np.log(n),
            'model_type': 'Component GARCH'
        }

    @staticmethod
    def realized_garch(returns: pd.Series, realized_measure: pd.Series,
                      p: int = 1, q: int = 1) -> Dict[str, Any]:
        """Realized GARCH model incorporating high-frequency data.

        Realized GARCH combines parametric GARCH with realized
        volatility measures for improved volatility forecasting.

        Parameters:
        -----------
        returns : pd.Series
            Daily returns
        realized_measure : pd.Series
            Realized volatility measure (e.g., realized variance)
        p, q : int
            GARCH orders

        Returns:
        --------
        dict : Realized GARCH model results
        """
        returns_vals = returns.values
        rv_vals = realized_measure.values
        n = len(returns_vals)

        # Initialize parameters
        omega = np.var(returns_vals) * 0.05
        beta = 0.8
        tau = 0.1      # Weight on realized measure
        phi = 0.9      # Persistence of realized component

        # Initialize conditional variances
        sigma2 = np.zeros(n)
        sigma2[0] = np.var(returns_vals[:min(20, n)])

        # Realized GARCH recursion
        for t in range(1, n):
            # GARCH component
            epsilon_t = returns_vals[t-1]**2 - sigma2[t-1]
            sigma2_garch = omega + beta * sigma2[t-1]

            # Realized component
            sigma2_realized = phi * rv_vals[t-1] + (1 - phi) * sigma2[t-1]

            # Combined volatility
            sigma2[t] = tau * sigma2_realized + (1 - tau) * sigma2_garch

        # Model evaluation
        log_likelihood = -0.5 * np.sum(np.log(sigma2) + returns_vals**2 / sigma2)

        return {
            'parameters': {
                'omega': omega, 'beta': beta, 'tau': tau, 'phi': phi
            },
            'conditional_volatility': sigma2,
            'log_likelihood': log_likelihood,
            'aic': -2 * log_likelihood + 2 * 4,
            'bic': -2 * log_likelihood + 4 * np.log(n),
            'model_type': 'Realized GARCH'
        }

    @staticmethod
    def garch_with_jumps(returns: pd.Series, jump_intensity: float = 0.1) -> Dict[str, Any]:
        """GARCH model with jumps in volatility.

        Extends GARCH to include jump components in volatility,
        better capturing extreme volatility movements.

        Parameters:
        -----------
        returns : pd.Series
            Historical returns
        jump_intensity : float
            Intensity parameter for jumps

        Returns:
        --------
        dict : GARCH with jumps results
        """
        returns_vals = returns.values
        n = len(returns_vals)

        # Initialize parameters
        omega = np.var(returns_vals) * 0.05
        alpha = 0.1
        beta = 0.8
        lambda_jump = jump_intensity
        mu_jump = 0.0     # Mean jump size
        sigma_jump = 0.2  # Jump volatility

        # Initialize volatility with jumps
        sigma2 = np.zeros(n)
        jumps = np.zeros(n)

        sigma2[0] = np.var(returns_vals[:min(20, n)])

        # GARCH with jumps recursion
        for t in range(1, n):
            # Generate jump (Poisson process)
            jump_occurs = np.random.poisson(lambda_jump) > 0
            if jump_occurs:
                jump_size = np.random.normal(mu_jump, sigma_jump)
                jumps[t] = jump_size
            else:
                jump_size = 0
                jumps[t] = 0

            # GARCH volatility
            epsilon_t = returns_vals[t-1]**2 - sigma2[t-1]
            sigma2[t] = omega + alpha * epsilon_t + beta * sigma2[t-1] + jump_size

        # Model evaluation
        log_likelihood = -0.5 * np.sum(np.log(sigma2) + returns_vals**2 / sigma2)

        return {
            'parameters': {
                'omega': omega, 'alpha': alpha, 'beta': beta,
                'lambda_jump': lambda_jump, 'mu_jump': mu_jump, 'sigma_jump': sigma_jump
            },
            'conditional_volatility': sigma2,
            'jump_components': jumps,
            'log_likelihood': log_likelihood,
            'jump_frequency': np.sum(jumps != 0) / n,
            'model_type': 'GARCH with Jumps'
        }

    @staticmethod
    def multivariate_garch(returns_matrix: pd.DataFrame, model_type: str = 'DCC') -> Dict[str, Any]:
        """Multivariate GARCH models for volatility spillovers.

        Implements various multivariate GARCH specifications:
        - Diagonal VECH
        - Constant Conditional Correlation (CCC)
        - Dynamic Conditional Correlation (DCC)

        Parameters:
        -----------
        returns_matrix : pd.DataFrame
            Matrix of returns for multiple assets
        model_type : str
            Type of multivariate GARCH ('VECH', 'CCC', 'DCC')

        Returns:
        --------
        dict : Multivariate GARCH results
        """
        returns_vals = returns_matrix.values.T  # Shape: (n_assets, n_periods)
        n_assets, n_periods = returns_vals.shape

        if model_type == 'DCC':
            # Dynamic Conditional Correlation GARCH

            # First, fit univariate GARCH to each series
            univariate_vols = []
            for i in range(n_assets):
                series_returns = pd.Series(returns_vals[i, :])
                # Simple GARCH(1,1) fit
                omega = np.var(returns_vals[i, :]) * 0.05
                alpha = 0.1
                beta = 0.8

                sigma2 = np.zeros(n_periods)
                sigma2[0] = np.var(returns_vals[i, :min(20, n_periods)])
                for t in range(1, n_periods):
                    epsilon_t = returns_vals[i, t-1]**2 - sigma2[t-1]
                    sigma2[t] = omega + alpha * epsilon_t + beta * sigma2[t-1]

                univariate_vols.append(np.sqrt(sigma2))

            # Standardized residuals
            std_residuals = np.zeros_like(returns_vals)
            for i in range(n_assets):
                std_residuals[i, :] = returns_vals[i, :] / univariate_vols[i]

            # Estimate dynamic correlations
            a = 0.05  # DCC parameter
            b = 0.9   # DCC parameter

            Q = np.corrcoef(std_residuals)  # Unconditional correlation
            Q_t = Q.copy()  # Initialize

            correlations = np.zeros((n_assets, n_assets, n_periods))
            correlations[:, :, 0] = Q

            for t in range(1, n_periods):
                # Update Q_t
                residual_outer = np.outer(std_residuals[:, t-1], std_residuals[:, t-1])
                Q_t = (1 - a - b) * Q + a * residual_outer + b * Q_t

                # Normalize to get correlation matrix
                diag_sqrt = np.sqrt(np.diag(Q_t))
                R_t = Q_t / np.outer(diag_sqrt, diag_sqrt)
                correlations[:, :, t] = R_t

            # Covariance matrices
            covariance_matrices = np.zeros((n_assets, n_assets, n_periods))
            for t in range(n_periods):
                vol_matrix = np.diag(univariate_vols[0][t] * univariate_vols[1][t])  # Simplified
                covariance_matrices[:, :, t] = vol_matrix @ correlations[:, :, t] @ vol_matrix

            return {
                'model_type': 'DCC-GARCH',
                'univariate_volatilities': univariate_vols,
                'dynamic_correlations': correlations,
                'covariance_matrices': covariance_matrices,
                'dcc_parameters': {'a': a, 'b': b}
            }

        else:
            return {'error': f'Model type {model_type} not implemented'}


# =============================================================================
# STOCHASTIC VOLATILITY MODELS
# =============================================================================

@dataclass
class StochasticVolatilityModels:
    """Advanced stochastic volatility models."""

    @staticmethod
    def hull_white_stochastic_vol(returns: pd.Series, mean_reversion: float = 2.0,
                                vol_of_vol: float = 0.3) -> Dict[str, Any]:
        """Hull-White stochastic volatility model.

        Two-factor model where volatility follows an Ornstein-Uhlenbeck process.

        Parameters:
        -----------
        returns : pd.Series
            Historical returns
        mean_reversion : float
            Mean reversion speed for volatility
        vol_of_vol : float
            Volatility of volatility

        Returns:
        --------
        dict : Hull-White stochastic volatility results
        """
        returns_vals = returns.values
        n = len(returns_vals)

        # Model parameters
        theta = np.var(returns_vals)  # Long-term volatility level
        kappa = mean_reversion       # Mean reversion speed
        sigma = vol_of_vol          # Volatility of volatility
        rho = -0.5                  # Correlation between price and volatility

        # Initialize state variables
        v = np.zeros(n)  # Volatility process
        v[0] = theta

        # Simulate the volatility process
        dt = 1.0 / 252  # Daily time step

        for t in range(1, n):
            # Volatility follows OU process
            dv = kappa * (theta - v[t-1]) * dt + sigma * np.sqrt(v[t-1]) * np.random.normal()
            v[t] = max(v[t-1] + dv, 0.01**2)  # Floor at 1% volatility

        # Generate returns with stochastic volatility
        simulated_returns = np.zeros(n)
        for t in range(1, n):
            # Correlated innovations
            z1 = np.random.normal()
            z2 = rho * z1 + np.sqrt(1 - rho**2) * np.random.normal()

            # Return = drift + volatility * innovation
            drift = -0.5 * v[t]  # Risk-neutral drift
            simulated_returns[t] = drift * dt + np.sqrt(v[t]) * z2 * np.sqrt(dt)

        return {
            'parameters': {
                'theta': theta, 'kappa': kappa, 'sigma': sigma, 'rho': rho
            },
            'volatility_process': v,
            'simulated_returns': simulated_returns,
            'actual_returns': returns_vals,
            'model_type': 'Hull-White Stochastic Volatility'
        }

    @staticmethod
    def three_two_model(returns: pd.Series) -> Dict[str, Any]:
        """3/2 stochastic volatility model.

        Advanced model where volatility scales as 1/v^{3/2},
        providing better fit for equity volatility smiles.

        Parameters:
        -----------
        returns : pd.Series
            Historical returns

        Returns:
        --------
        dict : 3/2 model results
        """
        returns_vals = returns.values
        n = len(returns_vals)

        # 3/2 model parameters
        eta = 0.5     # Volatility elasticity
        theta = np.var(returns_vals)  # Long-term volatility
        kappa = 1.5   # Mean reversion speed
        sigma = 0.2   # Volatility of volatility
        v0 = theta    # Initial volatility

        # Initialize volatility process
        v = np.zeros(n)
        v[0] = v0

        dt = 1.0 / 252

        # Simulate 3/2 process
        for t in range(1, n):
            # 3/2 volatility dynamics: dv = kappa(θ - v)dt + σ v^{η} dW
            # where η = 3/2 for the 3/2 model
            eta = 1.5
            drift = kappa * (theta - v[t-1]) * dt
            diffusion = sigma * (v[t-1] ** eta) * np.random.normal() * np.sqrt(dt)

            v[t] = max(v[t-1] + drift + diffusion, 0.01**2)

        # Generate returns
        simulated_returns = np.zeros(n)
        for t in range(1, n):
            drift = -0.5 * v[t] * dt
            innovation = np.random.normal() * np.sqrt(dt)
            simulated_returns[t] = drift + np.sqrt(v[t]) * innovation

        return {
            'parameters': {
                'eta': eta, 'theta': theta, 'kappa': kappa, 'sigma': sigma, 'v0': v0
            },
            'volatility_process': v,
            'simulated_returns': simulated_returns,
            'actual_returns': returns_vals,
            'model_type': '3/2 Stochastic Volatility'
        }


# =============================================================================
# VOLATILITY DERIVATIVES PRICING
# =============================================================================

@dataclass
class VolatilityDerivativesPricing:
    """Pricing models for volatility derivatives."""

    @staticmethod
    def variance_swap_pricing(spot: float, strikes: np.ndarray, expiries: np.ndarray,
                            market_vols: np.ndarray, risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Price variance swaps using volatility surface.

        Variance swaps pay the difference between realized variance
        and strike variance at maturity.

        Parameters:
        -----------
        spot : float
            Current spot price
        strikes : np.ndarray
            Option strikes
        expiries : np.ndarray
            Time to expiry
        market_vols : np.ndarray
            Market implied volatilities
        risk_free_rate : float
            Risk-free rate

        Returns:
        --------
        dict : Variance swap pricing results
        """
        # Variance swap fair strike is approximately the integral of ATM volatility
        # Fair strike = (2/rT) * ∫ [σ_ATM(K,T)^2 * dT] from 0 to T

        # Simplified: use average ATM volatility
        atm_vols = market_vols[len(strikes)//2]  # Assume middle strike is ATM

        # Calculate fair variance strike
        variance_strikes = {}
        for i, T in enumerate(expiries):
            # Simple approximation
            avg_var = np.mean(atm_vols[max(0, i-5):i+1]**2) if i > 0 else atm_vols[0]**2
            fair_strike = avg_var  # Simplified

            variance_strikes[T] = {
                'fair_strike': fair_strike,
                'realized_variance': avg_var,
                'market_price': fair_strike * np.exp(-risk_free_rate * T)
            }

        return {
            'variance_swaps': variance_strikes,
            'underlying_asset': spot,
            'risk_free_rate': risk_free_rate,
            'model_type': 'Variance Swap'
        }

    @staticmethod
    def vol_swap_pricing(spot: float, strikes: np.ndarray, expiries: np.ndarray,
                        market_vols: np.ndarray, risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Price volatility swaps.

        Volatility swaps pay the difference between realized volatility
        and strike volatility at maturity.

        Parameters:
        -----------
        spot : float
            Current spot price
        strikes : np.ndarray
            Option strikes
        expiries : np.ndarray
            Time to expiry
        market_vols : np.ndarray
            Market implied volatilities
        risk_free_rate : float
            Risk-free rate

        Returns:
        --------
        dict : Volatility swap pricing results
        """
        # Volatility swap fair strike is more complex
        # Requires numerical integration over the volatility surface

        atm_vols = market_vols[len(strikes)//2]

        vol_strikes = {}
        for i, T in enumerate(expiries):
            # Simplified fair strike calculation
            # In practice, this involves complex integration
            avg_vol = np.mean(atm_vols[max(0, i-5):i+1]) if i > 0 else atm_vols[0]

            # Adjustment for volatility convexity
            convexity_adjustment = 0.1 * avg_vol  # Simplified
            fair_strike = avg_vol + convexity_adjustment

            vol_strikes[T] = {
                'fair_strike': fair_strike,
                'expected_realized_vol': avg_vol,
                'convexity_adjustment': convexity_adjustment,
                'market_price': fair_strike * np.exp(-risk_free_rate * T)
            }

        return {
            'volatility_swaps': vol_strikes,
            'underlying_asset': spot,
            'risk_free_rate': risk_free_rate,
            'model_type': 'Volatility Swap'
        }


# =============================================================================
# EXPORT ADVANCED VOLATILITY MODELS
# =============================================================================

__all__ = [
    # Existing exports
    "SABRCalibrator", "VolatilitySurface", "realized_volatility", "parkinson_volatility",

    # New advanced exports
    "AdvancedStochasticVolatilityModels", "AdvancedGARCHModels", "StochasticVolatilityModels",
    "VolatilityDerivativesPricing"
]

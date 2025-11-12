"""Advanced risk management utilities for backtesting engines with portfolio optimization and ML integration."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field, asdict
from typing import Iterable, List, Optional, Protocol, Dict, Any, Callable, Union
from abc import ABC, abstractmethod
import numpy as np

import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from .types import Order, OrderSide, PortfolioSnapshot


@dataclass(slots=True)
class RiskEvent:
    timestamp: pd.Timestamp
    rule: str
    message: str
    severity: str = "warning"


@dataclass(slots=True)
class RiskContext:
    symbol: str
    price: float
    snapshot: PortfolioSnapshot
    timestamp: pd.Timestamp


class RiskRule(Protocol):
    name: str

    def reset(self) -> None:  # pragma: no cover - default protocol method
        ...

    def on_context(self, context: RiskContext) -> None:  # pragma: no cover - default protocol method
        ...

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:  # pragma: no cover
        ...

    def on_fill(self, order: Order, context: RiskContext) -> None:  # pragma: no cover
        ...


class BaseRiskRule:
    name = "base"

    def reset(self) -> None:
        pass

    def on_context(self, context: RiskContext) -> None:
        pass

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        return None

    def on_fill(self, order: Order, context: RiskContext) -> None:
        pass


class MaxDrawdownRule(BaseRiskRule):
    name = "max_drawdown"

    def __init__(self, threshold: float) -> None:
        if threshold <= 0 or threshold >= 1:
            raise ValueError("Drawdown threshold must be between 0 and 1.")
        self.threshold = threshold
        self.peak_equity: float = 0.0
        self.tripped: bool = False

    def reset(self) -> None:
        self.peak_equity = 0.0
        self.tripped = False

    def on_context(self, context: RiskContext) -> None:
        equity = context.snapshot.equity
        if self.peak_equity == 0:
            self.peak_equity = equity
        self.peak_equity = max(self.peak_equity, equity)
        if self.peak_equity <= 0:
            return
        drawdown = 1 - equity / self.peak_equity
        if drawdown >= self.threshold:
            self.tripped = True

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if self.tripped:
            return f"Drawdown threshold {self.threshold:.0%} exceeded."
        return None


class MaxPositionRule(BaseRiskRule):
    name = "max_position"

    def __init__(self, max_units: float) -> None:
        if max_units <= 0:
            raise ValueError("max_units must be positive")
        self.max_units = max_units

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        positions = context.snapshot.positions
        current_quantity = 0.0
        for position in positions:
            if position.symbol == context.symbol:
                current_quantity = position.quantity
                break

        if order.side == OrderSide.BUY:
            projected = current_quantity + order.remaining
            if projected > self.max_units + 1e-9:
                return f"Order exceeds max long units {self.max_units}."
        else:
            projected = current_quantity - order.remaining
            if projected < -self.max_units - 1e-9:
                return f"Order exceeds max short units {self.max_units}."
        return None


class DailyLossRule(BaseRiskRule):
    name = "daily_loss"

    def __init__(self, loss_limit: float) -> None:
        if loss_limit <= 0 or loss_limit >= 1:
            raise ValueError("loss_limit must be between 0 and 1.")
        self.loss_limit = loss_limit
        self.day_start_equity: float = 0.0
        self.current_day: Optional[pd.Timestamp] = None
        self.halted: bool = False

    def reset(self) -> None:
        self.day_start_equity = 0.0
        self.current_day = None
        self.halted = False

    def on_context(self, context: RiskContext) -> None:
        day = context.timestamp.normalize()
        if self.current_day is None or day != self.current_day:
            self.current_day = day
            self.day_start_equity = context.snapshot.equity
            self.halted = False
            return

        if self.day_start_equity <= 0:
            return
        loss_pct = 1 - context.snapshot.equity / self.day_start_equity
        if loss_pct >= self.loss_limit:
            self.halted = True

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if self.halted:
            return f"Daily loss limit {self.loss_limit:.0%} reached."
        return None


class NetExposureLimitRule(BaseRiskRule):
    name = "net_exposure_limit"

    def __init__(self, max_exposure: float) -> None:
        if max_exposure <= 0:
            raise ValueError("max_exposure must be positive.")
        self.max_exposure = max_exposure

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        snapshot = context.snapshot
        price = context.price
        current = snapshot.gross_exposure or 0.0
        delta = price * order.remaining
        projected = current + delta
        if projected > self.max_exposure + 1e-9:
            return f"Projected exposure {projected:,.2f} exceeds limit {self.max_exposure:,.2f}."
        return None


class LeverageLimitRule(BaseRiskRule):
    name = "leverage_limit"

    def __init__(self, max_leverage: float) -> None:
        if max_leverage <= 0:
            raise ValueError("max_leverage must be positive.")
        self.max_leverage = max_leverage

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        equity = context.snapshot.equity or 1.0
        exposure = context.snapshot.gross_exposure or 0.0
        price = context.price
        projected = exposure + price * order.remaining
        leverage = projected / max(equity, 1e-9)
        if leverage > self.max_leverage + 1e-9:
            return f"Projected leverage {leverage:.2f} exceeds limit {self.max_leverage:.2f}."
        return None


class ValueAtRiskRule(BaseRiskRule):
    """VaR-based position sizing with historical simulation."""

    name = "value_at_risk"

    def __init__(self, confidence_level: float = 0.95, lookback_periods: int = 252, max_var_loss: float = 0.02) -> None:
        if not 0 < confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1.")
        if lookback_periods < 30:
            raise ValueError("Lookback periods must be at least 30.")
        if max_var_loss <= 0:
            raise ValueError("Max VaR loss must be positive.")

        self.confidence_level = confidence_level
        self.lookback_periods = lookback_periods
        self.max_var_loss = max_var_loss
        self.return_history: List[float] = []

    def reset(self) -> None:
        self.return_history.clear()

    def on_context(self, context: RiskContext) -> None:
        # Track portfolio returns for VaR calculation
        if len(self.return_history) >= 2:
            ret = (context.snapshot.equity - self.return_history[-1]) / max(self.return_history[-1], 1e-9)
            self.return_history.append(context.snapshot.equity)
            if len(self.return_history) > self.lookback_periods:
                self.return_history.pop(0)
        else:
            self.return_history.append(context.snapshot.equity)

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if len(self.return_history) < 30:
            return None  # Not enough data for VaR calculation

        # Calculate historical VaR
        returns = np.diff(self.return_history) / np.array(self.return_history[:-1])
        returns = returns[~np.isnan(returns) & ~np.isinf(returns)]

        if len(returns) < 10:
            return None

        var_threshold = np.percentile(returns, (1 - self.confidence_level) * 100)
        projected_loss = abs(var_threshold) * context.snapshot.equity

        if projected_loss > self.max_var_loss * context.snapshot.equity:
            return f"VaR breach: potential loss {projected_loss:.2f} exceeds limit {self.max_var_loss * context.snapshot.equity:.2f}."
        return None


class ExpectedShortfallRule(BaseRiskRule):
    """Expected Shortfall (CVaR) risk control."""

    name = "expected_shortfall"

    def __init__(self, confidence_level: float = 0.95, max_es_loss: float = 0.05, window: int = 252) -> None:
        if not 0 < confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1.")
        self.confidence_level = confidence_level
        self.max_es_loss = max_es_loss
        self.window = window
        self.return_series: List[float] = []

    def reset(self) -> None:
        self.return_series.clear()

    def on_context(self, context: RiskContext) -> None:
        if len(self.return_series) >= 2:
            ret = (context.snapshot.equity - self.return_series[-1]) / max(self.return_series[-1], 1e-9)
            self.return_series.append(context.snapshot.equity)
            if len(self.return_series) > self.window:
                self.return_series.pop(0)
        else:
            self.return_series.append(context.snapshot.equity)

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if len(self.return_series) < 50:
            return None

        returns = np.diff(self.return_series) / np.array(self.return_series[:-1])
        returns = returns[~np.isnan(returns) & ~np.isinf(returns)]

        if len(returns) < 20:
            return None

        # Calculate Expected Shortfall (CVaR)
        var_threshold = np.percentile(returns, (1 - self.confidence_level) * 100)
        tail_losses = returns[returns <= var_threshold]
        es = -np.mean(tail_losses) if len(tail_losses) > 0 else 0

        if es > self.max_es_loss:
            return f"ES breach: expected shortfall {es:.3f} exceeds limit {self.max_es_loss:.3f}."
        return None


class CorrelationRiskRule(BaseRiskRule):
    """Monitor portfolio correlation and diversification."""

    name = "correlation_risk"

    def __init__(self, max_correlation: float = 0.8, min_assets: int = 5) -> None:
        if not 0 <= max_correlation <= 1:
            raise ValueError("Max correlation must be between 0 and 1.")
        self.max_correlation = max_correlation
        self.min_assets = min_assets
        self.asset_returns: Dict[str, List[float]] = {}

    def reset(self) -> None:
        self.asset_returns.clear()

    def on_context(self, context: RiskContext) -> None:
        # Track returns for each asset
        symbol = context.symbol
        if symbol not in self.asset_returns:
            self.asset_returns[symbol] = []

        if len(self.asset_returns[symbol]) >= 2:
            ret = (context.price - self.asset_returns[symbol][-1]) / max(self.asset_returns[symbol][-1], 1e-9)
            self.asset_returns[symbol].append(context.price)
        else:
            self.asset_returns[symbol].append(context.price)

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if len(self.asset_returns) < self.min_assets:
            return None  # Need minimum assets for correlation analysis

        # Calculate average correlation
        symbols = list(self.asset_returns.keys())
        if len(symbols) < 2:
            return None

        correlations = []
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                returns_i = np.diff(self.asset_returns[symbols[i]]) / np.array(self.asset_returns[symbols[i]][:-1])
                returns_j = np.diff(self.asset_returns[symbols[j]]) / np.array(self.asset_returns[symbols[j]][:-1])

                if len(returns_i) > 10 and len(returns_j) > 10:
                    corr = np.corrcoef(returns_i[-min(len(returns_i), len(returns_j)):],
                                      returns_j[-min(len(returns_i), len(returns_j)):])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(abs(corr))

        if correlations and np.mean(correlations) > self.max_correlation:
            return f"Portfolio correlation {np.mean(correlations):.3f} exceeds limit {self.max_correlation:.3f}."
        return None


class LiquidityRiskRule(BaseRiskRule):
    """Monitor position liquidity and trading volume."""

    name = "liquidity_risk"

    def __init__(self, min_volume_ratio: float = 0.01, max_position_ratio: float = 0.1) -> None:
        self.min_volume_ratio = min_volume_ratio
        self.max_position_ratio = max_position_ratio
        self.symbol_volumes: Dict[str, float] = {}

    def reset(self) -> None:
        self.symbol_volumes.clear()

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        # This would need volume data integration
        # For now, implement basic position size limits
        positions = context.snapshot.positions
        for position in positions:
            if position.symbol == context.symbol:
                position_ratio = abs(position.quantity) / max(context.snapshot.equity, 1e-9)
                if position_ratio > self.max_position_ratio:
                    return f"Position size {position_ratio:.3f} exceeds liquidity limit {self.max_position_ratio:.3f}."
        return None


class MLVolatilityRule(BaseRiskRule):
    """Machine learning-based volatility prediction for dynamic risk control."""

    name = "ml_volatility"

    def __init__(self, volatility_threshold: float = 0.03, retrain_period: int = 100) -> None:
        self.volatility_threshold = volatility_threshold
        self.retrain_period = retrain_period
        self.price_history: List[float] = []
        self.volatility_model = None
        self.last_train_step = 0

    def reset(self) -> None:
        self.price_history.clear()
        self.volatility_model = None
        self.last_train_step = 0

    def _train_volatility_model(self) -> None:
        """Train ML model to predict volatility."""
        if len(self.price_history) < 50:
            return

        # Create features from price history
        prices = np.array(self.price_history)
        returns = np.diff(prices) / prices[:-1]

        # Rolling volatility features
        features = []
        targets = []

        window_sizes = [5, 10, 20, 50]
        for i in range(max(window_sizes), len(returns)):
            feature_row = []
            for window in window_sizes:
                vol = np.std(returns[i-window:i])
                feature_row.extend([vol, np.mean(returns[i-window:i]), np.max(returns[i-window:i])])

            # Target: future volatility
            future_vol = np.std(returns[i:i+10]) if i+10 < len(returns) else np.std(returns[i:])
            targets.append(future_vol)
            features.append(feature_row)

        if len(features) > 20:
            X = np.array(features)
            y = np.array(targets)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.volatility_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.volatility_model.fit(X_train, y_train)

    def on_context(self, context: RiskContext) -> None:
        self.price_history.append(context.price)

        # Retrain model periodically
        if len(self.price_history) - self.last_train_step >= self.retrain_period:
            self._train_volatility_model()
            self.last_train_step = len(self.price_history)

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        if self.volatility_model is None or len(self.price_history) < 50:
            return None

        # Predict current volatility
        prices = np.array(self.price_history[-50:])
        returns = np.diff(prices) / prices[:-1]

        features = []
        window_sizes = [5, 10, 20, 50]
        for window in window_sizes:
            if len(returns) >= window:
                vol = np.std(returns[-window:])
                mean_ret = np.mean(returns[-window:])
                max_ret = np.max(returns[-window:])
                features.extend([vol, mean_ret, max_ret])
            else:
                features.extend([0, 0, 0])

        predicted_volatility = self.volatility_model.predict([features])[0]

        if predicted_volatility > self.volatility_threshold:
            return f"Predicted volatility {predicted_volatility:.4f} exceeds threshold {self.volatility_threshold:.4f}."
        return None


class KellyCriterionRule(BaseRiskRule):
    """Kelly Criterion-based position sizing for optimal growth."""

    name = "kelly_criterion"

    def __init__(self, fraction: float = 1.0, min_edge: float = 0.01) -> None:
        if not 0 < fraction <= 1:
            raise ValueError("Kelly fraction must be between 0 and 1.")
        self.fraction = fraction
        self.min_edge = min_edge
        self.win_rate_history: List[bool] = []
        self.avg_win_history: List[float] = []
        self.avg_loss_history: List[float] = []

    def reset(self) -> None:
        self.win_rate_history.clear()
        self.avg_win_history.clear()
        self.avg_loss_history.clear()

    def on_fill(self, order: Order, context: RiskContext) -> None:
        # Track trade outcomes for Kelly calculation
        # This would need integration with trade results
        pass

    def should_block_order(self, order: Order, context: RiskContext) -> Optional[str]:
        # Simplified Kelly calculation - would need historical trade data
        if len(self.win_rate_history) < 10:
            return None

        win_rate = np.mean(self.win_rate_history)
        avg_win = np.mean(self.avg_win_history) if self.avg_win_history else 0.01
        avg_loss = np.mean(self.avg_loss_history) if self.avg_loss_history else 0.01

        if win_rate <= 0 or avg_win <= 0 or avg_loss <= 0:
            return None

        # Kelly formula: f = (bp - q) / b
        # where b = odds (avg_win/avg_loss), p = win_rate, q = loss_rate
        b = avg_win / avg_loss
        kelly_fraction = (b * win_rate - (1 - win_rate)) / b

        if kelly_fraction < self.min_edge:
            return f"Kelly fraction {kelly_fraction:.4f} below minimum edge {self.min_edge:.4f}."

        # Apply fractional Kelly
        optimal_fraction = kelly_fraction * self.fraction
        max_position_value = context.snapshot.equity * optimal_fraction

        order_value = context.price * order.remaining
        if order_value > max_position_value:
            return f"Order size {order_value:.2f} exceeds Kelly optimal {max_position_value:.2f}."
        return None


class PortfolioOptimizer:
    """Advanced portfolio optimization for risk management."""

    def __init__(self, method: str = "mean_variance", risk_aversion: float = 2.0):
        self.method = method
        self.risk_aversion = risk_aversion
        self.asset_returns: Dict[str, List[float]] = {}
        self.covariance_matrix: Optional[pd.DataFrame] = None

    def update_asset_returns(self, symbol: str, price: float) -> None:
        """Update price history for an asset."""
        if symbol not in self.asset_returns:
            self.asset_returns[symbol] = []

        self.asset_returns[symbol].append(price)
        if len(self.asset_returns[symbol]) > 1000:  # Keep reasonable history
            self.asset_returns[symbol].pop(0)

    def _calculate_covariance_matrix(self) -> pd.DataFrame:
        """Calculate covariance matrix from asset returns."""
        symbols = list(self.asset_returns.keys())
        if len(symbols) < 2:
            return pd.DataFrame()

        # Calculate returns for each asset
        returns_dict = {}
        for symbol in symbols:
            prices = np.array(self.asset_returns[symbol])
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]
                returns_dict[symbol] = returns

        # Create returns DataFrame
        returns_df = pd.DataFrame(returns_dict).dropna()
        if returns_df.empty or len(returns_df.columns) < 2:
            return pd.DataFrame()

        self.covariance_matrix = returns_df.cov()
        return self.covariance_matrix

    def optimize_portfolio(self, target_return: Optional[float] = None) -> Dict[str, float]:
        """Optimize portfolio weights using specified method."""
        if len(self.asset_returns) < 2:
            return {symbol: 1.0 / len(self.asset_returns) for symbol in self.asset_returns.keys()}

        cov_matrix = self._calculate_covariance_matrix()
        if cov_matrix.empty:
            return {symbol: 1.0 / len(self.asset_returns) for symbol in self.asset_returns.keys()}

        symbols = list(cov_matrix.columns)
        n_assets = len(symbols)

        if self.method == "mean_variance":
            return self._mean_variance_optimization(cov_matrix, symbols, target_return)
        elif self.method == "risk_parity":
            return self._risk_parity_optimization(cov_matrix, symbols)
        elif self.method == "minimum_variance":
            return self._minimum_variance_optimization(cov_matrix, symbols)
        else:
            # Equal weight fallback
            return {symbol: 1.0 / n_assets for symbol in symbols}

    def _mean_variance_optimization(self, cov_matrix: pd.DataFrame, symbols: List[str],
                                  target_return: Optional[float]) -> Dict[str, float]:
        """Markowitz mean-variance optimization."""
        n_assets = len(symbols)

        # Calculate expected returns (simplified: use historical averages)
        expected_returns = []
        for symbol in symbols:
            prices = np.array(self.asset_returns[symbol])
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]
                expected_returns.append(np.mean(returns))
            else:
                expected_returns.append(0.0)

        expected_returns = np.array(expected_returns)

        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))

            if target_return is not None:
                return portfolio_volatility + self.risk_aversion * abs(portfolio_return - target_return)
            else:
                return portfolio_volatility - self.risk_aversion * portfolio_return  # Maximize Sharpe-like ratio

        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        ]
        bounds = [(0, 1) for _ in range(n_assets)]  # Long only

        try:
            result = minimize_scalar(lambda x: objective(x), bounds=bounds, constraints=constraints,
                                   method='SLSQP')
            if hasattr(result, 'x'):
                return dict(zip(symbols, result.x))
            else:
                return {symbol: 1.0 / n_assets for symbol in symbols}
        except:
            return {symbol: 1.0 / n_assets for symbol in symbols}

    def _risk_parity_optimization(self, cov_matrix: pd.DataFrame, symbols: List[str]) -> Dict[str, float]:
        """Risk parity optimization - equal risk contribution."""
        n_assets = len(symbols)

        def objective(weights):
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            marginal_risk = np.dot(cov_matrix.values, weights) / portfolio_volatility
            risk_contributions = weights * marginal_risk

            # Minimize variance of risk contributions
            return np.var(risk_contributions)

        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        ]
        bounds = [(0.01, 1) for _ in range(n_assets)]  # Small minimum weight to avoid zero

        try:
            result = minimize_scalar(objective, bounds=bounds, constraints=constraints, method='SLSQP')
            if hasattr(result, 'x'):
                weights = result.x / np.sum(result.x)  # Renormalize
                return dict(zip(symbols, weights))
            else:
                return {symbol: 1.0 / n_assets for symbol in symbols}
        except:
            return {symbol: 1.0 / n_assets for symbol in symbols}

    def _minimum_variance_optimization(self, cov_matrix: pd.DataFrame, symbols: List[str]) -> Dict[str, float]:
        """Minimum variance portfolio optimization."""
        n_assets = len(symbols)

        def objective(weights):
            return np.dot(weights.T, np.dot(cov_matrix.values, weights))

        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        ]
        bounds = [(0, 1) for _ in range(n_assets)]

        try:
            result = minimize_scalar(objective, bounds=bounds, constraints=constraints, method='SLSQP')
            if hasattr(result, 'x'):
                return dict(zip(symbols, result.x))
            else:
                return {symbol: 1.0 / n_assets for symbol in symbols}
        except:
            return {symbol: 1.0 / n_assets for symbol in symbols}


@dataclass(slots=True)
class RiskManager:
    rules: List[RiskRule] = field(default_factory=list)
    events: List[RiskEvent] = field(default_factory=list)
    context: Optional[RiskContext] = None
    portfolio_optimizer: Optional[PortfolioOptimizer] = None

    def __post_init__(self) -> None:
        if self.portfolio_optimizer is None:
            self.portfolio_optimizer = PortfolioOptimizer()

    def reset(self) -> None:
        for rule in self.rules:
            rule.reset()
        self.events.clear()
        self.context = None
        if self.portfolio_optimizer:
            self.portfolio_optimizer.asset_returns.clear()

    def update_context(self, context: RiskContext) -> None:
        self.context = context

        # Update portfolio optimizer with current prices
        if self.portfolio_optimizer:
            self.portfolio_optimizer.update_asset_returns(context.symbol, context.price)

        for rule in self.rules:
            rule.on_context(context)

    def approve(self, order: Order) -> bool:
        if self.context is None:
            return True
        allowed = True
        for rule in self.rules:
            message = rule.should_block_order(order, self.context)
            if message:
                allowed = False
                self.events.append(
                    RiskEvent(timestamp=self.context.timestamp, rule=rule.name, message=message, severity="block"),
                )
        return allowed

    def on_fill(self, order: Order) -> None:
        if self.context is None:
            return
        for rule in self.rules:
            rule.on_fill(order, self.context)

    def get_optimal_weights(self, symbols: List[str]) -> Dict[str, float]:
        """Get optimal portfolio weights from the optimizer."""
        if self.portfolio_optimizer:
            return self.portfolio_optimizer.optimize_portfolio()
        return {symbol: 1.0 / len(symbols) for symbol in symbols}

    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive portfolio risk metrics."""
        if not self.portfolio_optimizer or not self.portfolio_optimizer.covariance_matrix:
            return {}

        cov_matrix = self.portfolio_optimizer.covariance_matrix
        if cov_matrix.empty:
            return {}

        # Equal weight assumption for metrics
        n_assets = len(cov_matrix.columns)
        weights = np.array([1.0 / n_assets] * n_assets)

        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))

        # Calculate expected returns (simplified)
        expected_returns = []
        for symbol in cov_matrix.columns:
            prices = np.array(self.portfolio_optimizer.asset_returns.get(symbol, []))
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]
                expected_returns.append(np.mean(returns))
            else:
                expected_returns.append(0.0)

        expected_returns = np.array(expected_returns)
        portfolio_return = np.dot(weights, expected_returns)

        # Sharpe ratio (assuming risk-free rate of 0.02)
        risk_free_rate = 0.02
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

        # Maximum drawdown calculation would require equity curve
        # This is a simplified version

        return {
            "portfolio_volatility": portfolio_volatility,
            "portfolio_return": portfolio_return,
            "sharpe_ratio": sharpe_ratio,
            "diversification_ratio": np.sqrt(np.sum(weights**2))  # Inverse concentration
        }

    def summary(self) -> pd.DataFrame:
        if not self.events:
            return pd.DataFrame(columns=["timestamp", "rule", "message", "severity"])
        frame = pd.DataFrame([asdict(event) for event in self.events])
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame

    def get_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report."""
        report = {
            "active_rules": [rule.name for rule in self.rules],
            "total_events": len(self.events),
            "events_by_severity": {},
            "portfolio_metrics": self.calculate_portfolio_metrics(),
        }

        # Events by severity
        for event in self.events:
            severity = event.severity
            if severity not in report["events_by_severity"]:
                report["events_by_severity"][severity] = 0
            report["events_by_severity"][severity] += 1

        return report


__all__ = [
    "RiskManager",
    "RiskRule",
    "RiskContext",
    "RiskEvent",
    "BaseRiskRule",
    "MaxDrawdownRule",
    "MaxPositionRule",
    "DailyLossRule",
    "NetExposureLimitRule",
    "LeverageLimitRule",
    "ValueAtRiskRule",
    "ExpectedShortfallRule",
    "CorrelationRiskRule",
    "LiquidityRiskRule",
    "MLVolatilityRule",
    "KellyCriterionRule",
    "PortfolioOptimizer",
]

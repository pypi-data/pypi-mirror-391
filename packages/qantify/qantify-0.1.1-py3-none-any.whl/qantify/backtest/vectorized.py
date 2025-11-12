"""Advanced vectorized backtesting engine with ML integration and multi-timeframe support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, List, Callable, Union, Any
from abc import ABC, abstractmethod
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import warnings

import pandas as pd

from qantify.core.utils import validate_ohlcv_frame

from .costs import CommissionModel, NoCommission, NoSlippage, SlippageModel
from .errors import ConfigurationError
from .types import Fill, Order, OrderSide, OrderType, Trade


@dataclass(slots=True)
class VectorizedBacktestResult:
    equity_curve: pd.Series
    long_positions: pd.Series
    short_positions: pd.Series
    trades: list[Trade]
    orders: list[Order]
    returns: pd.Series
    gross_exposure: pd.Series
    # Enhanced metrics
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    calmar_ratio: float = 0.0
    sortino_ratio: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    information_ratio: float = 0.0
    # Risk metrics
    value_at_risk: float = 0.0
    expected_shortfall: float = 0.0
    tail_ratio: float = 0.0
    # Performance attribution
    benchmark_returns: Optional[pd.Series] = None
    tracking_error: float = 0.0
    # Multi-timeframe data
    timeframe_returns: Dict[str, pd.Series] = field(default_factory=dict)
    # ML predictions (if used)
    ml_predictions: Optional[pd.Series] = None
    feature_importance: Dict[str, float] = field(default_factory=dict)

    def calculate_metrics(self, risk_free_rate: float = 0.02, benchmark_returns: Optional[pd.Series] = None) -> None:
        """Calculate comprehensive performance metrics."""
        returns = self.returns.dropna()

        if len(returns) == 0:
            return

        # Basic metrics
        self.sharpe_ratio = self._calculate_sharpe_ratio(returns, risk_free_rate)
        self.max_drawdown = self._calculate_max_drawdown(self.equity_curve)
        self.win_rate = self._calculate_win_rate()
        self.profit_factor = self._calculate_profit_factor()
        self.calmar_ratio = self._calculate_calmar_ratio(returns, risk_free_rate)
        self.sortino_ratio = self._calculate_sortino_ratio(returns, risk_free_rate)

        # Risk metrics
        self.value_at_risk = self._calculate_var(returns)
        self.expected_shortfall = self._calculate_es(returns)
        self.tail_ratio = self._calculate_tail_ratio(returns)

        # Benchmark-relative metrics
        if benchmark_returns is not None:
            self.benchmark_returns = benchmark_returns
            self.alpha, self.beta = self._calculate_alpha_beta(returns, benchmark_returns, risk_free_rate)
            self.information_ratio = self._calculate_information_ratio(returns, benchmark_returns, risk_free_rate)

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """Calculate Sharpe ratio."""
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return abs(drawdown.min())

    def _calculate_win_rate(self) -> float:
        """Calculate win rate from trades."""
        if not self.trades:
            return 0.0

        winning_trades = sum(1 for trade in self.trades if trade.pnl > 0)
        return winning_trades / len(self.trades)

    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor."""
        if not self.trades:
            return 1.0

        gross_profit = sum(trade.pnl for trade in self.trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in self.trades if trade.pnl < 0))

        return gross_profit / gross_loss if gross_loss > 0 else float('inf')

    def _calculate_calmar_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """Calculate Calmar ratio."""
        if self.max_drawdown == 0:
            return 0.0
        ann_return = (1 + returns.mean()) ** 252 - 1
        return (ann_return - risk_free_rate) / self.max_drawdown

    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """Calculate Sortino ratio."""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    def _calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk."""
        return -np.percentile(returns, (1 - confidence) * 100)

    def _calculate_es(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Expected Shortfall."""
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        tail_losses = returns[returns <= var_threshold]
        return -np.mean(tail_losses) if len(tail_losses) > 0 else 0.0

    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate tail ratio (upside capture / downside capture)."""
        returns_95 = np.percentile(returns, 95)
        returns_5 = np.percentile(returns, 5)

        if returns_5 >= 0:  # No downside
            return float('inf')

        return returns_95 / abs(returns_5)

    def _calculate_alpha_beta(self, returns: pd.Series, benchmark_returns: pd.Series,
                            risk_free_rate: float) -> tuple[float, float]:
        """Calculate alpha and beta."""
        # Align the series
        common_index = returns.index.intersection(benchmark_returns.index)
        if len(common_index) < 2:
            return 0.0, 1.0

        aligned_returns = returns.loc[common_index]
        aligned_benchmark = benchmark_returns.loc[common_index]

        # Calculate beta
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0

        # Calculate alpha
        portfolio_excess = aligned_returns - risk_free_rate / 252
        benchmark_excess = aligned_benchmark - risk_free_rate / 252
        alpha = portfolio_excess.mean() - beta * benchmark_excess.mean()

        return alpha * 252, beta  # Annualize alpha

    def _calculate_information_ratio(self, returns: pd.Series, benchmark_returns: pd.Series,
                                   risk_free_rate: float) -> float:
        """Calculate information ratio."""
        alpha, _ = self._calculate_alpha_beta(returns, benchmark_returns, risk_free_rate)
        tracking_error = returns.std() * np.sqrt(252)
        return alpha / tracking_error if tracking_error > 0 else 0.0


class PositionSizer(ABC):
    """Abstract base class for position sizing strategies."""

    @abstractmethod
    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        """Calculate position size for a given signal."""
        pass


class FixedPositionSizer(PositionSizer):
    """Fixed position sizing."""

    def __init__(self, size: float):
        self.size = size

    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        return self.size if signal else 0.0


class PercentagePositionSizer(PositionSizer):
    """Percentage of capital position sizing."""

    def __init__(self, percentage: float = 0.1):
        self.percentage = percentage

    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        if not signal:
            return 0.0
        return (available_capital * self.percentage) / price


class KellyPositionSizer(PositionSizer):
    """Kelly Criterion-based position sizing."""

    def __init__(self, win_rate: float, win_loss_ratio: float, fraction: float = 1.0):
        self.win_rate = win_rate
        self.win_loss_ratio = win_loss_ratio
        self.fraction = fraction

    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        if not signal:
            return 0.0

        # Kelly formula: f = (bp - q) / b
        b = self.win_loss_ratio
        kelly_fraction = (b * self.win_rate - (1 - self.win_rate)) / b
        kelly_fraction = max(0, kelly_fraction * self.fraction)  # Apply fractional Kelly

        return (available_capital * kelly_fraction) / price


class VolatilityAdjustedSizer(PositionSizer):
    """Volatility-adjusted position sizing."""

    def __init__(self, base_percentage: float = 0.1, volatility_window: int = 20, target_volatility: float = 0.02):
        self.base_percentage = base_percentage
        self.volatility_window = volatility_window
        self.target_volatility = target_volatility

    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        if not signal:
            return 0.0

        # Calculate current volatility
        returns = data['close'].pct_change().dropna()
        if len(returns) < self.volatility_window:
            current_volatility = returns.std()
        else:
            current_volatility = returns.iloc[-self.volatility_window:].std()

        # Adjust position size based on volatility
        if current_volatility > 0:
            adjustment_factor = self.target_volatility / current_volatility
            adjusted_percentage = self.base_percentage * adjustment_factor
            adjusted_percentage = np.clip(adjusted_percentage, 0.01, 0.5)  # Reasonable bounds
        else:
            adjusted_percentage = self.base_percentage

        return (available_capital * adjusted_percentage) / price


class MLPositionSizer(PositionSizer):
    """Machine learning-based position sizing."""

    def __init__(self, model_type: str = "random_forest", max_position: float = 0.2):
        self.model_type = model_type
        self.max_position = max_position
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, historical_data: pd.DataFrame, target_returns: pd.Series) -> None:
        """Train the ML model for position sizing."""
        # Create features
        features = self._create_features(historical_data)

        # Prepare target (optimal position sizes based on subsequent returns)
        # This is a simplified approach - in practice, you'd need more sophisticated labeling
        optimal_sizes = np.where(target_returns > 0, 0.1, 0.05)  # Simple rule-based optimal sizes

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            features, optimal_sizes, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        predictions = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, predictions)
        print(f"ML Position Sizer trained. MSE: {mse:.4f}")

        self.is_trained = True

    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML model."""
        features = pd.DataFrame(index=data.index)

        # Price-based features
        features['returns'] = data['close'].pct_change()
        features['volatility'] = features['returns'].rolling(20).std()
        features['trend'] = data['close'].rolling(50).mean() / data['close'].rolling(200).mean() - 1

        # Volume features (if available)
        if 'volume' in data.columns:
            features['volume_ma'] = data['volume'].rolling(20).mean()
            features['volume_ratio'] = data['volume'] / features['volume_ma']

        # Technical indicators
        features['rsi'] = self._calculate_rsi(data['close'])
        features['macd'] = self._calculate_macd(data['close'])

        return features.dropna()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD."""
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        return ema12 - ema26

    def calculate_size(self, data: pd.DataFrame, signal: pd.Series, current_position: float,
                      available_capital: float, price: float) -> float:
        if not signal or not self.is_trained:
            return 0.0

        # Get latest features
        features = self._create_features(data)
        if features.empty:
            return 0.0

        latest_features = features.iloc[-1:].values
        scaled_features = self.scaler.transform(latest_features)

        # Predict optimal position size
        predicted_size_pct = self.model.predict(scaled_features)[0]
        predicted_size_pct = np.clip(predicted_size_pct, 0, self.max_position)

        return (available_capital * predicted_size_pct) / price


class MultiTimeframeEngine:
    """Multi-timeframe analysis engine."""

    def __init__(self, base_timeframe: str = "1D"):
        self.base_timeframe = base_timeframe
        self.timeframes = {
            "1H": 1/24,  # Assuming base is daily
            "4H": 4/24,
            "1D": 1,
            "1W": 7,
            "1M": 30
        }

    def resample_data(self, data: pd.DataFrame, target_timeframe: str) -> pd.DataFrame:
        """Resample data to target timeframe."""
        if target_timeframe not in self.timeframes:
            raise ValueError(f"Unsupported timeframe: {target_timeframe}")

        # This is a simplified resampling - in practice you'd use proper OHLCV resampling
        resampled = data.resample(target_timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum' if 'volume' in data.columns else 'count'
        }).dropna()

        return resampled

    def generate_multi_timeframe_signals(self, data: pd.DataFrame,
                                       signal_generator: Callable) -> Dict[str, pd.Series]:
        """Generate signals across multiple timeframes."""
        signals = {}

        for tf in self.timeframes.keys():
            try:
                tf_data = self.resample_data(data, tf)
                signals[tf] = signal_generator(tf_data)
            except Exception as e:
                warnings.warn(f"Failed to generate signals for {tf}: {e}")
                signals[tf] = pd.Series(False, index=data.index)

        return signals

    def combine_timeframe_signals(self, signals: Dict[str, pd.Series],
                                combination_method: str = "vote") -> pd.Series:
        """Combine signals from multiple timeframes."""
        if not signals:
            return pd.Series()

        # Align all signals to base timeframe
        aligned_signals = {}
        base_index = None

        for tf, signal in signals.items():
            if base_index is None:
                base_index = signal.index
                aligned_signals[tf] = signal
            else:
                # Simple alignment - in practice you'd need proper reindexing
                aligned_signals[tf] = signal.reindex(base_index, method='ffill').fillna(False)

        # Combine signals
        signal_df = pd.DataFrame(aligned_signals)

        if combination_method == "vote":
            # Majority vote
            return signal_df.sum(axis=1) > len(signal_df.columns) / 2
        elif combination_method == "weighted":
            # Weight higher timeframes more
            weights = {'1H': 1, '4H': 2, '1D': 3, '1W': 4, '1M': 5}
            weighted_sum = sum(signal_df[tf] * weights.get(tf, 1) for tf in signal_df.columns)
            return weighted_sum > sum(weights.values()) / 2
        else:
            # Default to daily signal
            return signal_df.get('1D', signal_df.iloc[:, 0])


def run(
    data: pd.DataFrame,
    *,
    symbol: str,
    entry_signal: pd.Series,
    exit_signal: Optional[pd.Series] = None,
    short_entry_signal: Optional[pd.Series] = None,
    short_exit_signal: Optional[pd.Series] = None,
    initial_capital: float = 100_000.0,
    allocation: float = 1.0,
    leverage: float = 1.0,
    allow_short: bool = False,
    commission_model: CommissionModel | None = None,
    slippage_model: SlippageModel | None = None,
    price_column: str = "close",
    position_mode: Literal["full", "capital", "fixed"] = "capital",
    fixed_size: float = 1.0,
    position_sizer: Optional[PositionSizer] = None,
    use_multi_timeframe: bool = False,
    benchmark_data: Optional[pd.DataFrame] = None,
) -> VectorizedBacktestResult:
    """Execute an advanced vectorized backtest with ML integration and multi-timeframe support."""

    if initial_capital <= 0:
        raise ConfigurationError("Initial capital must be positive.")
    if allocation <= 0 or allocation > 1:
        raise ConfigurationError("Allocation must be within 0-1 range.")
    if leverage <= 0:
        raise ConfigurationError("Leverage must be positive.")

    validate_ohlcv_frame(data)

    if price_column not in data.columns:
        raise ConfigurationError(f"Data must contain price column '{price_column}'.")

    commission_model = commission_model or NoCommission()
    slippage_model = slippage_model or NoSlippage()

    price = data[price_column]
    if not isinstance(price.index, pd.DatetimeIndex):
        raise ConfigurationError("Price series must be indexed by DatetimeIndex.")

    # Enhanced signal processing
    entry_signal = entry_signal.reindex(price.index).fillna(False).astype(bool)
    exit_signal = exit_signal.reindex(price.index).fillna(False).astype(bool) if exit_signal is not None else pd.Series(False, index=price.index)
    short_entry_signal = short_entry_signal.reindex(price.index).fillna(False).astype(bool) if short_entry_signal is not None else pd.Series(False, index=price.index)
    short_exit_signal = short_exit_signal.reindex(price.index).fillna(False).astype(bool) if short_exit_signal is not None else pd.Series(False, index=price.index)

    # Multi-timeframe processing
    if use_multi_timeframe:
        mtf_engine = MultiTimeframeEngine()

        def signal_gen(df):
            # Simple moving average crossover for demo
            short_ma = df['close'].rolling(10).mean()
            long_ma = df['close'].rolling(30).mean()
            return short_ma > long_ma

        mtf_signals = mtf_engine.generate_multi_timeframe_signals(data, signal_gen)
        combined_signal = mtf_engine.combine_timeframe_signals(mtf_signals)
        entry_signal = entry_signal | combined_signal  # Combine with original signal

    position_long = _generate_position(entry_signal, exit_signal)
    position_short = _generate_position(short_entry_signal, short_exit_signal) if allow_short else pd.Series(0, index=price.index)

    position_long = position_long.clip(0, 1)
    position_short = position_short.clip(0, 1)

    returns = price.pct_change().fillna(0.0)

    # Advanced position sizing
    if position_sizer is not None:
        long_size = _advanced_size_calculation(position_long, price, initial_capital, allocation, leverage, position_sizer, data)
        short_size = _advanced_size_calculation(position_short, price, initial_capital, allocation, leverage, position_sizer, data) if allow_short else pd.Series(0, index=price.index)
    else:
        long_size = _determine_size(position_long, price, initial_capital, allocation, leverage, position_mode, fixed_size)
        short_size = _determine_size(position_short, price, initial_capital, allocation, leverage, position_mode, fixed_size)

    long_weights = long_size.shift(1, fill_value=0)
    short_weights = short_size.shift(1, fill_value=0)

    long_returns = returns * position_long.shift(1, fill_value=0) * long_weights
    short_returns = -returns * position_short.shift(1, fill_value=0) * short_weights
    strategy_returns = long_returns + short_returns

    equity_curve = initial_capital * (1 + strategy_returns).cumprod()
    gross_exposure = (position_long.abs() * long_size.abs()) + (position_short.abs() * short_size.abs())

    orders: list[Order] = []
    trades: list[Trade] = []

    _vector_extract_trades(
        trades,
        orders,
        symbol=symbol,
        position_series=position_long,
        price=price,
        equity_curve=equity_curve,
        commission_model=commission_model,
        slippage_model=slippage_model,
        side=OrderSide.BUY,
    )

    if allow_short:
        _vector_extract_trades(
            trades,
            orders,
            symbol=symbol,
            position_series=position_short,
            price=price,
            equity_curve=equity_curve,
            commission_model=commission_model,
            slippage_model=slippage_model,
            side=OrderSide.SELL,
        )

    trades.sort(key=lambda trade: trade.entry.timestamp)

    # Create result with enhanced metrics
    result = VectorizedBacktestResult(
        equity_curve=equity_curve,
        long_positions=position_long,
        short_positions=position_short,
        trades=trades,
        orders=orders,
        returns=strategy_returns,
        gross_exposure=gross_exposure,
    )

    # Calculate comprehensive metrics
    benchmark_returns = None
    if benchmark_data is not None and 'close' in benchmark_data.columns:
        benchmark_returns = benchmark_data['close'].pct_change().reindex(price.index).fillna(0)

    result.calculate_metrics(benchmark_returns=benchmark_returns)

    # Add multi-timeframe returns if requested
    if use_multi_timeframe:
        result.timeframe_returns = mtf_engine.generate_multi_timeframe_signals(data, lambda x: x['close'].pct_change())

    # Add ML feature importance if position sizer was ML-based
    if isinstance(position_sizer, MLPositionSizer) and position_sizer.is_trained and hasattr(position_sizer.model, 'feature_importances_'):
        feature_names = ['returns', 'volatility', 'trend', 'volume_ma', 'volume_ratio', 'rsi', 'macd']
        result.feature_importance = dict(zip(feature_names, position_sizer.model.feature_importances_))

    return result


def _advanced_size_calculation(
    position: pd.Series,
    price: pd.Series,
    initial_capital: float,
    allocation: float,
    leverage: float,
    position_sizer: PositionSizer,
    data: pd.DataFrame,
) -> pd.Series:
    """Calculate position sizes using advanced position sizer."""
    sizes = []

    for i, (pos, prc) in enumerate(zip(position, price)):
        current_data = data.iloc[:i+1] if i > 0 else data.iloc[:1]
        available_capital = initial_capital * allocation * leverage

        size = position_sizer.calculate_size(
            data=current_data,
            signal=pos > 0,
            current_position=0.0,  # Simplified
            available_capital=available_capital,
            price=prc
        )
        sizes.append(size)

    return pd.Series(sizes, index=position.index)


def _generate_position(entry_signal: pd.Series, exit_signal: pd.Series) -> pd.Series:
    entry_flag = entry_signal.astype(int).cumsum()
    exit_flag = exit_signal.astype(int).cumsum()
    raw_position = entry_flag - exit_flag
    position = (raw_position > 0).astype(int)
    return position


def _determine_size(
    position: pd.Series,
    price: pd.Series,
    initial_capital: float,
    allocation: float,
    leverage: float,
    position_mode: str,
    fixed_size: float,
) -> pd.Series:
    if position_mode == "fixed":
        weight = (price * fixed_size) / initial_capital
    elif position_mode == "full":
        weight = pd.Series(leverage, index=position.index)
    else:  # capital mode
        weight = pd.Series(allocation * leverage, index=position.index)

    if not isinstance(weight, pd.Series):
        weight = pd.Series(weight, index=position.index)

    return weight.clip(lower=0)


def _vector_extract_trades(
    trades: list[Trade],
    orders: list[Order],
    *,
    symbol: str,
    position_series: pd.Series,
    price: pd.Series,
    equity_curve: pd.Series,
    commission_model: CommissionModel,
    slippage_model: SlippageModel,
    side: OrderSide,
) -> None:
    changes = position_series.diff().fillna(position_series.iloc[0])
    in_trade = False
    entry_idx: Optional[pd.Timestamp] = None
    entry_price: Optional[float] = None
    entry_equity: Optional[float] = None
    entry_base_price: Optional[float] = None

    for idx, change in changes.items():
        if change > 0 and not in_trade:
            base_price = price.loc[idx]
            order = Order(timestamp=idx, symbol=symbol, side=side, quantity=1.0, type=OrderType.MARKET)
            adjusted_price = slippage_model.apply(order, base_price, 1.0)
            commission = commission_model.compute(order, adjusted_price, 1.0)
            order.mark_filled()
            orders.append(order)
            entry_idx = idx
            entry_price = adjusted_price
            entry_equity = equity_curve.loc[idx]
            entry_base_price = base_price
            in_trade = True

        elif change < 0 and in_trade:
            base_price = price.loc[idx]
            exit_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
            order = Order(timestamp=idx, symbol=symbol, side=exit_side, quantity=1.0, type=OrderType.MARKET)
            adjusted_price = slippage_model.apply(order, base_price, 1.0)
            commission = commission_model.compute(order, adjusted_price, 1.0)
            order.mark_filled()
            orders.append(order)
            if entry_idx and entry_price is not None and entry_equity is not None:
                exit_equity = equity_curve.loc[idx]
                pnl = exit_equity - entry_equity - commission
                return_pct = (exit_equity - entry_equity) / entry_equity if entry_equity else 0.0
                entry_slippage = 0.0
                if entry_base_price is not None and entry_price is not None:
                    entry_slippage = entry_price - entry_base_price

                if side == OrderSide.BUY:
                    entry_fill = Fill(entry_idx, symbol, OrderSide.BUY, entry_price, 1.0, commission=0.0, slippage=entry_slippage)
                    exit_fill = Fill(idx, symbol, OrderSide.SELL, adjusted_price, 1.0, commission=commission, slippage=adjusted_price - base_price)
                    direction = OrderSide.BUY
                else:
                    entry_fill = Fill(entry_idx, symbol, OrderSide.SELL, entry_price, 1.0, commission=0.0, slippage=entry_slippage)
                    exit_fill = Fill(idx, symbol, OrderSide.BUY, adjusted_price, 1.0, commission=commission, slippage=adjusted_price - base_price)
                    direction = OrderSide.SELL

                trade = Trade(
                    entry=entry_fill,
                    exit=exit_fill,
                    quantity=1.0,
                    pnl=pnl,
                    return_pct=return_pct,
                    max_drawdown=0.0,
                    direction=direction,
                )
                trades.append(trade)
            in_trade = False
            entry_idx = None
            entry_base_price = None


__all__ = [
    "VectorizedBacktestResult",
    "run",
    "PositionSizer",
    "FixedPositionSizer",
    "PercentagePositionSizer",
    "KellyPositionSizer",
    "VolatilityAdjustedSizer",
    "MLPositionSizer",
    "MultiTimeframeEngine",
]

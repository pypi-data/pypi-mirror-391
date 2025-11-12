"""Advanced bot templates and trading strategies built on qantify framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from qantify.backtest import EventBacktester
from qantify.strategy import IndicatorSeries, Strategy, when
from qantify.signals import (
    rsi,
    macd,
    bollinger_bands,
    supertrend,
    stochastic,
    atr,
    adx,
    cci,
    mfi,
    keltner_channels,
    ichimoku,
    williams_r,
    ultimate_oscillator,
    chaikin_money_flow,
    aroon,
    elder_ray,
    force_index,
    ease_of_movement,
    volume_price_trend,
    accumulation_distribution,
    chaikin_oscillator,
    chande_momentum_oscillator,
    psychological_line,
    vertical_horizontal_filter,
    trend_intensity_index,
    trix,
    vidya,
    alma,
    frama,
    gma,
    jma,
    lsma,
    mcginley_dynamic,
    head_shoulders_patterns,
    double_top_bottom,
    wedge_patterns,
    triangle_patterns,
    flag_patterns,
    cup_handle_patterns,
    clustering_market_regime_signals,
    reinforcement_learning_signals,
    neural_network_regime_classifier,
    ensemble_ml_signals,
    feature_importance_signals,
    value_at_risk_signals,
    drawdown_risk_signals,
    volatility_adjusted_signals,
    kelly_criterion_signals,
    multi_timeframe_momentum_signals,
    timeframe_synchronization_signals,
)


@dataclass(slots=True)
class BotResult:
    equity_curve: pd.Series
    trades: int
    logs: pd.DataFrame
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_trade_return: float = 0.0
    volatility: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    calmar_ratio: float = 0.0
    sortino_ratio: float = 0.0

    def calculate_metrics(self, benchmark_returns: Optional[pd.Series] = None) -> None:
        """Calculate comprehensive performance metrics."""
        if len(self.equity_curve) < 2:
            return

        # Basic returns
        returns = self.equity_curve.pct_change().fillna(0)
        cumulative_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) - 1
        self.total_return = cumulative_return

        # Risk metrics
        self.volatility = returns.std() * np.sqrt(252)  # Annualized
        self.max_drawdown = ((self.equity_curve - self.equity_curve.expanding().max()) / self.equity_curve.expanding().max()).min()

        # Sharpe ratio
        risk_free_rate = 0.02  # 2% annual risk-free rate
        daily_rf = risk_free_rate / 252
        excess_returns = returns - daily_rf
        if excess_returns.std() > 0:
            self.sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            self.sortino_ratio = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)

        # Calmar ratio
        if abs(self.max_drawdown) > 0:
            self.calmar_ratio = cumulative_return / abs(self.max_drawdown)

        # Trading metrics
        if hasattr(self, 'trades') and self.trades > 0:
            winning_trades = len([log for log in self.logs if 'profit' in str(log).lower() and float(str(log).split()[-1]) > 0])
            self.win_rate = winning_trades / self.trades if self.trades > 0 else 0

            # Profit factor
            gross_profit = sum(max(0, float(str(log).split()[-1])) for log in self.logs if 'profit' in str(log).lower())
            gross_loss = abs(sum(min(0, float(str(log).split()[-1])) for log in self.logs if 'profit' in str(log).lower()))
            self.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

            # Average trade return
            trade_returns = [float(str(log).split()[-1]) for log in self.logs if 'profit' in str(log).lower()]
            self.avg_trade_return = np.mean(trade_returns) if trade_returns else 0

        # Alpha/Beta vs benchmark
        if benchmark_returns is not None:
            aligned_returns = returns.align(benchmark_returns, join='inner')[0]
            aligned_benchmark = benchmark_returns.align(returns, join='inner')[1]

            if len(aligned_returns) > 1 and aligned_benchmark.std() > 0:
                covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
                benchmark_var = aligned_benchmark.var()
                self.beta = covariance / benchmark_var
                self.alpha = (aligned_returns.mean() - self.beta * aligned_benchmark.mean()) * 252

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "total_return": self.total_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "avg_trade_return": self.avg_trade_return,
            "volatility": self.volatility,
            "alpha": self.alpha,
            "beta": self.beta,
            "calmar_ratio": self.calmar_ratio,
            "sortino_ratio": self.sortino_ratio,
            "trades": self.trades,
        }

    def generate_report(self) -> str:
        """Generate a comprehensive performance report."""
        report_lines = []
        report_lines.append("🤖 Bot Performance Report")
        report_lines.append("=" * 50)
        report_lines.append("")

        report_lines.append("📊 Performance Metrics:")
        report_lines.append(f"   • Total Return: {self.total_return:.2%}")
        report_lines.append(f"   • Sharpe Ratio: {self.sharpe_ratio:.2f}")
        report_lines.append(f"   • Sortino Ratio: {self.sortino_ratio:.2f}")
        report_lines.append(f"   • Calmar Ratio: {self.calmar_ratio:.2f}")
        report_lines.append(f"   • Max Drawdown: {self.max_drawdown:.2%}")
        report_lines.append(f"   • Volatility: {self.volatility:.2%}")
        report_lines.append("")

        report_lines.append("💼 Trading Metrics:")
        report_lines.append(f"   • Total Trades: {self.trades}")
        report_lines.append(f"   • Win Rate: {self.win_rate:.1%}")
        report_lines.append(f"   • Profit Factor: {self.profit_factor:.2f}")
        report_lines.append(f"   • Avg Trade Return: {self.avg_trade_return:.2%}")
        report_lines.append("")

        if hasattr(self, 'alpha') and hasattr(self, 'beta'):
            report_lines.append("📈 Risk-Adjusted Metrics:")
            report_lines.append(f"   • Alpha: {self.alpha:.2%}")
            report_lines.append(f"   • Beta: {self.beta:.2f}")
            report_lines.append("")

        return "\n".join(report_lines)


@dataclass(slots=True)
class MeanReversionConfig:
    rsi_period: int = 14
    oversold: float = 30.0
    overbought: float = 70.0
    position_size: float = 0.5


class _MeanReversionStrategy(Strategy):
    def __init__(self, config: MeanReversionConfig) -> None:
        super().__init__()
        self.cfg = config
        self.data = None  # Will be set by backtester

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        if self.data is None:
            raise ValueError("Data not set for strategy")

        cfg = self.cfg
        close_series = self.data["close"]
        rsi_result = rsi(close_series, period=cfg.rsi_period)
        if isinstance(rsi_result, pd.DataFrame):
            rsi_series = rsi_result.iloc[:, 0]
        else:
            rsi_series = rsi_result
        rsi_series = rsi_series.rename("bot_rsi").fillna(50)  # Fill NaN with neutral value
        self.rsi_series = IndicatorSeries(rsi_series, self)

        self.add_rule(
            when(lambda strat: strat.rsi_series.cross_below(strat.cfg.oversold), name="bot_enter_long").then(
                lambda strat: strat.buy(size=strat.cfg.position_size)
            )
        )
        self.add_rule(
            when(lambda strat: strat.rsi_series.cross_above(strat.cfg.overbought), name="bot_exit_long").then(
                lambda strat: strat.sell(size=strat.cfg.position_size)
            )
        )

    def next(self) -> None:
        pass


def run_mean_reversion_bot(
    data: pd.DataFrame,
    *,
    config: Optional[MeanReversionConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    cfg = config or MeanReversionConfig()
    strategy = _MeanReversionStrategy(cfg)
    strategy.set_data(data)  # Set data for strategy
    engine = EventBacktester(data, symbol="BOT", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()
    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class BreakoutConfig:
    ema_fast: int = 10
    ema_slow: int = 40
    supertrend_period: int = 10
    supertrend_multiplier: float = 3.0
    position_size: float = 0.4


class _BreakoutStrategy(Strategy):
    def __init__(self, config: BreakoutConfig) -> None:
        super().__init__()
        self.cfg = config
        self.data = None  # Will be set by backtester

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        if self.data is None:
            raise ValueError("Data not set for strategy")
        cfg = self.cfg
        close = self.data["close"]
        fast_series = close.ewm(span=cfg.ema_fast, adjust=False).mean().rename("bot_ema_fast")
        slow_series = close.ewm(span=cfg.ema_slow, adjust=False).mean().rename("bot_ema_slow")
        st_frame = supertrend(
            self.data,
            period=cfg.supertrend_period,
            multiplier=cfg.supertrend_multiplier,
            name="bot_supertrend",
        )
        st_series = st_frame["bot_supertrend"]

        self.fast = IndicatorSeries(fast_series, self)
        self.slow = IndicatorSeries(slow_series, self)
        self.supertrend = IndicatorSeries(st_series, self)

        self.add_rule(
            when(
                lambda strat: strat.fast.cross_above(strat.slow)
                and strat.price() > strat.supertrend.value(0),
                name="bot_breakout_long",
            ).then(lambda strat: strat.buy(size=strat.cfg.position_size))
        )
        self.add_rule(
            when(
                lambda strat: strat.fast.cross_below(strat.slow)
                or strat.price() < strat.supertrend.value(0),
                name="bot_breakout_exit",
            ).then(lambda strat: strat.sell(size=strat.cfg.position_size))
        )

    def next(self) -> None:
        pass


def run_breakout_bot(
    data: pd.DataFrame,
    *,
    config: Optional[BreakoutConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    cfg = config or BreakoutConfig()
    strategy = _BreakoutStrategy(cfg)
    strategy.set_data(data)  # Set data for strategy
    engine = EventBacktester(data, symbol="BOT", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()
    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


# =============================================================================
# ADVANCED BOT TEMPLATES
# =============================================================================

@dataclass(slots=True)
class PairsTradingConfig:
    entry_threshold: float = 2.0
    exit_threshold: float = 0.5
    lookback_window: int = 100
    max_holding_period: int = 50
    position_size: float = 0.3
    stop_loss: float = 0.05
    take_profit: float = 0.03

    def __post_init__(self):
        if self.entry_threshold <= self.exit_threshold:
            raise ValueError("Entry threshold must be greater than exit threshold")


class _PairsTradingStrategy(Strategy):
    def __init__(self, config: PairsTradingConfig, asset1_data: pd.DataFrame, asset2_data: pd.DataFrame):
        super().__init__()
        self.cfg = config
        self.asset1_data = asset1_data
        self.asset2_data = asset2_data
        self.position = 0  # 1 for long asset1/short asset2, -1 for short asset1/long asset2
        self.entry_bar = None
        self.data = asset1_data  # Primary data for strategy

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        # Calculate spread and z-score
        asset1_prices = self.asset1_data["close"]
        asset2_prices = self.asset2_data["close"]

        # Simple spread (can be enhanced with cointegration)
        spread = asset1_prices - asset2_prices

        # Rolling mean and std for z-score
        spread_mean = spread.rolling(window=self.cfg.lookback_window).mean()
        spread_std = spread.rolling(window=self.cfg.lookback_window).std()

        zscore = (spread - spread_mean) / spread_std
        zscore = zscore.fillna(0)

        self.spread_series = IndicatorSeries(zscore, self)

        # Entry rules
        self.add_rule(
            when(lambda strat: strat.spread_series.value(0) > strat.cfg.entry_threshold and strat.position == 0)
            .then(lambda strat: strat._enter_short_spread())
            .name("pairs_enter_short_spread")
        )

        self.add_rule(
            when(lambda strat: strat.spread_series.value(0) < -strat.cfg.entry_threshold and strat.position == 0)
            .then(lambda strat: strat._enter_long_spread())
            .name("pairs_enter_long_spread")
        )

        # Exit rules
        self.add_rule(
            when(lambda strat: abs(strat.spread_series.value(0)) < strat.cfg.exit_threshold and strat.position != 0)
            .then(lambda strat: strat._exit_spread())
            .name("pairs_exit_on_reversion")
        )

        # Stop loss and take profit
        self.add_rule(
            when(lambda strat: strat.position != 0 and strat._check_stop_loss())
            .then(lambda strat: strat._exit_spread())
            .name("pairs_stop_loss")
        )

        self.add_rule(
            when(lambda strat: strat.position != 0 and strat._check_take_profit())
            .then(lambda strat: strat._exit_spread())
            .name("pairs_take_profit")
        )

        # Max holding period
        self.add_rule(
            when(lambda strat: strat.position != 0 and strat._check_max_holding())
            .then(lambda strat: strat._exit_spread())
            .name("pairs_max_holding")
        )

    def _enter_short_spread(self) -> None:
        """Enter short spread: short asset1, long asset2."""
        self.position = -1
        self.entry_bar = len(self.data)
        self.buy(size=self.cfg.position_size, name="pairs_long_asset2")
        # Note: In real implementation, you'd need to short asset1

    def _enter_long_spread(self) -> None:
        """Enter long spread: long asset1, short asset2."""
        self.position = 1
        self.entry_bar = len(self.data)
        self.sell(size=self.cfg.position_size, name="pairs_short_asset2")
        # Note: In real implementation, you'd need to long asset1

    def _exit_spread(self) -> None:
        """Exit the spread position."""
        if self.position == 1:
            self.buy(size=self.cfg.position_size, name="pairs_cover_asset2")
        elif self.position == -1:
            self.sell(size=self.cfg.position_size, name="pairs_cover_asset2")

        self.position = 0
        self.entry_bar = None

    def _check_stop_loss(self) -> bool:
        """Check if stop loss is hit."""
        if self.entry_bar is None:
            return False

        entry_spread = self.spread_series.value_at(self.entry_bar)
        current_spread = self.spread_series.value(0)

        if self.position == 1:  # Long spread
            return current_spread < entry_spread * (1 - self.cfg.stop_loss)
        elif self.position == -1:  # Short spread
            return current_spread > entry_spread * (1 + self.cfg.stop_loss)

        return False

    def _check_take_profit(self) -> bool:
        """Check if take profit is hit."""
        if self.entry_bar is None:
            return False

        entry_spread = self.spread_series.value_at(self.entry_bar)
        current_spread = self.spread_series.value(0)

        if self.position == 1:  # Long spread
            return current_spread > entry_spread * (1 + self.cfg.take_profit)
        elif self.position == -1:  # Short spread
            return current_spread < entry_spread * (1 - self.cfg.take_profit)

        return False

    def _check_max_holding(self) -> bool:
        """Check if max holding period is reached."""
        if self.entry_bar is None:
            return False

        return (len(self.data) - self.entry_bar) >= self.cfg.max_holding_period

    def next(self) -> None:
        pass


def run_pairs_trading_bot(
    asset1_data: pd.DataFrame,
    asset2_data: pd.DataFrame,
    *,
    config: Optional[PairsTradingConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run a pairs trading bot between two assets."""

    cfg = config or PairsTradingConfig()
    strategy = _PairsTradingStrategy(cfg, asset1_data, asset2_data)

    # Use asset1 as the primary data for backtesting
    engine = EventBacktester(asset1_data, symbol="PAIRS", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class ArbitrageConfig:
    price_threshold: float = 0.005  # 0.5% price difference
    volume_threshold: int = 1000
    max_holding_time: int = 10  # bars
    position_size: float = 0.5
    arbitrage_type: str = "statistical"  # "statistical" or "triangular"


class _ArbitrageStrategy(Strategy):
    def __init__(self, config: ArbitrageConfig, exchange_data: Dict[str, pd.DataFrame]):
        super().__init__()
        self.cfg = config
        self.exchange_data = exchange_data
        self.position = 0
        self.data = list(exchange_data.values())[0]  # Primary exchange data

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        # For statistical arbitrage between exchanges
        if self.cfg.arbitrage_type == "statistical":
            self._setup_statistical_arbitrage()

    def _setup_statistical_arbitrage(self) -> None:
        """Setup statistical arbitrage between exchanges."""
        if len(self.exchange_data) < 2:
            return

        # Calculate price differences between exchanges
        exchanges = list(self.exchange_data.keys())
        exchange1_prices = self.exchange_data[exchanges[0]]["close"]
        exchange2_prices = self.exchange_data[exchanges[1]]["close"]

        # Price difference ratio
        price_ratio = exchange1_prices / exchange2_prices
        price_ratio_mean = price_ratio.rolling(window=50).mean()
        price_ratio_std = price_ratio.rolling(window=50).std()

        zscore = (price_ratio - price_ratio_mean) / price_ratio_std
        zscore = zscore.fillna(0)

        self.price_ratio_series = IndicatorSeries(zscore, self)

        # Arbitrage entry rules
        self.add_rule(
            when(lambda strat: strat.price_ratio_series.value(0) > 2.0 and strat.position == 0)
            .then(lambda strat: strat._enter_arbitrage_buy())
            .name("arb_enter_buy_exchange1")
        )

        self.add_rule(
            when(lambda strat: strat.price_ratio_series.value(0) < -2.0 and strat.position == 0)
            .then(lambda strat: strat._enter_arbitrage_sell())
            .name("arb_enter_sell_exchange1")
        )

        # Exit rules
        self.add_rule(
            when(lambda strat: abs(strat.price_ratio_series.value(0)) < 0.5 and strat.position != 0)
            .then(lambda strat: strat._exit_arbitrage())
            .name("arb_exit_reversion")
        )

    def _enter_arbitrage_buy(self) -> None:
        """Buy on cheaper exchange, sell on expensive."""
        self.position = 1
        self.buy(size=self.cfg.position_size, name="arb_buy_cheap")

    def _enter_arbitrage_sell(self) -> None:
        """Sell on expensive exchange, buy on cheap."""
        self.position = -1
        self.sell(size=self.cfg.position_size, name="arb_sell_expensive")

    def _exit_arbitrage(self) -> None:
        """Exit arbitrage position."""
        if self.position == 1:
            self.sell(size=self.cfg.position_size, name="arb_exit_buy")
        elif self.position == -1:
            self.buy(size=self.cfg.position_size, name="arb_exit_sell")

        self.position = 0

    def next(self) -> None:
        pass


def run_arbitrage_bot(
    exchange_data: Dict[str, pd.DataFrame],
    *,
    config: Optional[ArbitrageConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run an arbitrage bot across multiple exchanges."""

    cfg = config or ArbitrageConfig()
    strategy = _ArbitrageStrategy(cfg, exchange_data)

    # Use first exchange as primary data
    primary_exchange = list(exchange_data.keys())[0]
    engine = EventBacktester(
        exchange_data[primary_exchange],
        symbol="ARB",
        strategy=strategy,
        initial_cash=initial_cash
    )
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class TrendFollowingConfig:
    fast_ma: int = 20
    slow_ma: int = 50
    trend_strength_threshold: float = 0.001
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    atr_multiplier: float = 2.0
    position_size: float = 0.4
    trailing_stop: bool = True
    trend_filter: bool = True


class _AdvancedTrendFollowingStrategy(Strategy):
    def __init__(self, config: TrendFollowingConfig):
        super().__init__()
        self.cfg = config
        self.data = None  # Will be set by backtester

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        if self.data is None:
            raise ValueError("Data not set for strategy")
        close = self.data["close"]

        # Moving averages
        fast_ma = close.ewm(span=self.cfg.fast_ma, adjust=False).mean()
        slow_ma = close.ewm(span=self.cfg.slow_ma, adjust=False).mean()

        # Trend strength (ADX-like)
        high = self.data["high"]
        low = self.data["low"]
        tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()

        # Trend direction
        trend_direction = (fast_ma > slow_ma).astype(int) * 2 - 1  # 1 for up, -1 for down

        # RSI filter
        rsi_result = rsi(close, period=14)
        if isinstance(rsi_result, pd.DataFrame):
            rsi_values = rsi_result.iloc[:, 0]
        else:
            rsi_values = rsi_result

        # Trend strength indicator
        trend_strength = abs(fast_ma - slow_ma) / close

        # Store indicators directly (avoid IndicatorSeries for now)
        self.fast_ma_values = fast_ma
        self.slow_ma_values = slow_ma
        self.trend_direction_values = trend_direction
        self.trend_strength_values = trend_strength
        self.rsi_values = rsi_values
        self.atr_values = atr

        # Store current index for rule evaluation
        self.current_idx = 0

        # Long entry - simplified rules
        self.add_rule(
            when(lambda strat: strat._check_long_entry())
            .then(lambda strat: strat.buy(size=strat.cfg.position_size))
            .name("trend_long_entry")
        )

        # Short entry - simplified rules
        self.add_rule(
            when(lambda strat: strat._check_short_entry())
            .then(lambda strat: strat.sell(size=strat.cfg.position_size))
            .name("trend_short_entry")
        )

        # Exit rules - simplified
        self.add_rule(
            when(lambda strat: strat._check_long_exit())
            .then(lambda strat: strat.sell(size=strat.cfg.position_size))
            .name("trend_long_exit")
        )

        self.add_rule(
            when(lambda strat: strat._check_short_exit())
            .then(lambda strat: strat.buy(size=strat.cfg.position_size))
            .name("trend_short_exit")
        )

    def _check_long_entry(self) -> bool:
        """Check conditions for long entry."""
        if self.current_idx < 1:
            return False

        try:
            # Check if fast MA crossed above slow MA
            fast_prev = self.fast_ma_values.iloc[self.current_idx - 1]
            fast_curr = self.fast_ma_values.iloc[self.current_idx]
            slow_prev = self.slow_ma_values.iloc[self.current_idx - 1]
            slow_curr = self.slow_ma_values.iloc[self.current_idx]

            crossover = (fast_prev <= slow_prev) and (fast_curr > slow_curr)

            # Check trend strength and RSI
            trend_strength = self.trend_strength_values.iloc[self.current_idx]
            rsi_val = self.rsi_values.iloc[self.current_idx]

            return (crossover and
                   trend_strength > self.cfg.trend_strength_threshold and
                   rsi_val > self.cfg.rsi_oversold)
        except (IndexError, KeyError):
            return False

    def _check_short_entry(self) -> bool:
        """Check conditions for short entry."""
        if self.current_idx < 1:
            return False

        try:
            # Check if fast MA crossed below slow MA
            fast_prev = self.fast_ma_values.iloc[self.current_idx - 1]
            fast_curr = self.fast_ma_values.iloc[self.current_idx]
            slow_prev = self.slow_ma_values.iloc[self.current_idx - 1]
            slow_curr = self.slow_ma_values.iloc[self.current_idx]

            crossunder = (fast_prev >= slow_prev) and (fast_curr < slow_curr)

            # Check trend strength and RSI
            trend_strength = self.trend_strength_values.iloc[self.current_idx]
            rsi_val = self.rsi_values.iloc[self.current_idx]

            return (crossunder and
                   trend_strength > self.cfg.trend_strength_threshold and
                   rsi_val < self.cfg.rsi_overbought)
        except (IndexError, KeyError):
            return False

    def _check_long_exit(self) -> bool:
        """Check conditions for long exit."""
        if self.current_idx < 1:
            return False

        try:
            # Exit when fast MA crosses below slow MA
            fast_prev = self.fast_ma_values.iloc[self.current_idx - 1]
            fast_curr = self.fast_ma_values.iloc[self.current_idx]
            slow_prev = self.slow_ma_values.iloc[self.current_idx - 1]
            slow_curr = self.slow_ma_values.iloc[self.current_idx]

            crossunder = (fast_prev >= slow_prev) and (fast_curr < slow_curr)
            return crossunder
        except (IndexError, KeyError):
            return False

    def _check_short_exit(self) -> bool:
        """Check conditions for short exit."""
        if self.current_idx < 1:
            return False

        try:
            # Exit when fast MA crosses above slow MA
            fast_prev = self.fast_ma_values.iloc[self.current_idx - 1]
            fast_curr = self.fast_ma_values.iloc[self.current_idx]
            slow_prev = self.slow_ma_values.iloc[self.current_idx - 1]
            slow_curr = self.slow_ma_values.iloc[self.current_idx]

            crossover = (fast_prev <= slow_prev) and (fast_curr > slow_curr)
            return crossover
        except (IndexError, KeyError):
            return False

    def next(self) -> None:
        """Update current index for rule evaluation."""
        self.current_idx = len(self.data) - 1


def run_trend_following_bot(
    data: pd.DataFrame,
    *,
    config: Optional[TrendFollowingConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run an advanced trend following bot."""

    cfg = config or TrendFollowingConfig()
    strategy = _AdvancedTrendFollowingStrategy(cfg)
    strategy.set_data(data)  # Set data for strategy
    engine = EventBacktester(data, symbol="TREND", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class MLBasedConfig:
    model_type: str = "ensemble"  # "ensemble", "neural_network", "reinforcement"
    prediction_horizon: int = 5
    confidence_threshold: float = 0.6
    position_size: float = 0.3
    max_positions: int = 1
    risk_management: bool = True


class _MLBasedStrategy(Strategy):
    def __init__(self, config: MLBasedConfig):
        super().__init__()
        self.cfg = config
        self.signals = None
        self.data = None  # Will be set by backtester

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        if self.data is None:
            raise ValueError("Data not set for strategy")
        # Generate ML signals
        if self.cfg.model_type == "ensemble":
            signals = ensemble_ml_signals(self.data)
        elif self.cfg.model_type == "neural_network":
            signals = neural_network_regime_classifier(self.data)
        elif self.cfg.model_type == "reinforcement":
            signals = reinforcement_learning_signals(self.data)
        else:
            signals = feature_importance_signals(self.data)

        # Extract signal column
        if isinstance(signals, pd.DataFrame):
            signal_col = [col for col in signals.columns if "signal" in col.lower()]
            if signal_col:
                signal_values = signals[signal_col[0]]
            else:
                signal_values = pd.Series(0, index=self.data.index)
        else:
            signal_values = signals

        # Store signals directly
        self.signal_values = signal_values.fillna(0)
        self.current_idx = 0

        # ML-based entry rules - simplified
        self.add_rule(
            when(lambda strat: strat._check_ml_long_entry())
            .then(lambda strat: strat.buy(size=strat.cfg.position_size))
            .name("ml_long_entry")
        )

        self.add_rule(
            when(lambda strat: strat._check_ml_short_entry())
            .then(lambda strat: strat.sell(size=strat.cfg.position_size))
            .name("ml_short_entry")
        )

        # Exit rules - simplified
        self.add_rule(
            when(lambda strat: strat._check_ml_exit())
            .then(lambda strat: strat.close_positions())
            .name("ml_exit_weak_signal")
        )

    def _check_ml_long_entry(self) -> bool:
        """Check ML signal for long entry."""
        try:
            signal_val = self.signal_values.iloc[self.current_idx]
            return signal_val > self.cfg.confidence_threshold
        except (IndexError, KeyError):
            return False

    def _check_ml_short_entry(self) -> bool:
        """Check ML signal for short entry."""
        try:
            signal_val = self.signal_values.iloc[self.current_idx]
            return signal_val < -self.cfg.confidence_threshold
        except (IndexError, KeyError):
            return False

    def _check_ml_exit(self) -> bool:
        """Check ML signal for exit."""
        try:
            signal_val = self.signal_values.iloc[self.current_idx]
            return abs(signal_val) < self.cfg.confidence_threshold * 0.5
        except (IndexError, KeyError):
            return False

    def next(self) -> None:
        """Update current index for rule evaluation."""
        self.current_idx = len(self.data) - 1


def run_ml_based_bot(
    data: pd.DataFrame,
    *,
    config: Optional[MLBasedConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run an ML-based trading bot."""

    cfg = config or MLBasedConfig()
    strategy = _MLBasedStrategy(cfg)
    strategy.set_data(data)  # Set data for strategy
    engine = EventBacktester(data, symbol="ML", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class RiskParityConfig:
    target_volatility: float = 0.15
    rebalancing_period: int = 20
    max_weight: float = 0.3
    min_weight: float = 0.05
    assets: Optional[List[str]] = None


class _RiskParityStrategy(Strategy):
    def __init__(self, config: RiskParityConfig, asset_data: Dict[str, pd.DataFrame]):
        super().__init__()
        self.cfg = config
        self.asset_data = asset_data
        self.last_rebalance = 0
        self.data = list(asset_data.values())[0]  # Primary asset data

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        # Initialize with equal weights
        self.weights = {asset: 1.0 / len(self.asset_data) for asset in self.asset_data.keys()}

        # Risk parity rebalancing
        self.add_rule(
            when(lambda strat: (len(strat.data) - strat.last_rebalance) >= strat.cfg.rebalancing_period)
            .then(lambda strat: strat._rebalance_portfolio())
            .name("risk_parity_rebalance")
        )

    def _rebalance_portfolio(self) -> None:
        """Rebalance portfolio using risk parity."""
        try:
            # Calculate volatilities for each asset
            volatilities = {}
            for asset, data in self.asset_data.items():
                returns = data["close"].pct_change().fillna(0)
                vol = returns.rolling(window=20).std().iloc[-1]
                volatilities[asset] = vol if not np.isnan(vol) else 0.02

            # Risk parity weights (inverse volatility)
            inv_vol = {asset: 1.0 / vol for asset, vol in volatilities.items()}
            total_inv_vol = sum(inv_vol.values())

            if total_inv_vol > 0:
                raw_weights = {asset: inv_vol[asset] / total_inv_vol for asset in inv_vol.keys()}

                # Apply constraints
                constrained_weights = {}
                for asset, weight in raw_weights.items():
                    constrained_weights[asset] = np.clip(weight, self.cfg.min_weight, self.cfg.max_weight)

                # Renormalize
                total_weight = sum(constrained_weights.values())
                if total_weight > 0:
                    self.weights = {asset: weight / total_weight for asset, weight in constrained_weights.items()}

            self.last_rebalance = len(self.data)

        except Exception:
            # Keep current weights on error
            pass

    def next(self) -> None:
        pass


def run_risk_parity_bot(
    asset_data: Dict[str, pd.DataFrame],
    *,
    config: Optional[RiskParityConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run a risk parity portfolio bot."""

    cfg = config or RiskParityConfig()
    strategy = _RiskParityStrategy(cfg, asset_data)

    # Use first asset as primary
    primary_asset = list(asset_data.keys())[0]
    engine = EventBacktester(
        asset_data[primary_asset],
        symbol="RISK_PARITY",
        strategy=strategy,
        initial_cash=initial_cash
    )
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


@dataclass(slots=True)
class MultiTimeframeConfig:
    primary_timeframe: str = "1H"
    secondary_timeframes: List[str] = None
    alignment_threshold: float = 0.8
    momentum_threshold: float = 0.02
    position_size: float = 0.4

    def __post_init__(self):
        if self.secondary_timeframes is None:
            self.secondary_timeframes = ["4H", "1D"]


class _MultiTimeframeStrategy(Strategy):
    def __init__(self, config: MultiTimeframeConfig):
        super().__init__()
        self.cfg = config
        self.data = None  # Will be set by backtester

    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for the strategy."""
        self.data = data

    def init(self) -> None:
        if self.data is None:
            raise ValueError("Data not set for strategy")
        # Multi-timeframe momentum signals
        mtf_signals = multi_timeframe_momentum_signals(
            self.data,
            timeframes=[self.cfg.primary_timeframe] + self.cfg.secondary_timeframes,
            momentum_periods=[10, 20]
        )

        # Timeframe synchronization
        sync_signals = timeframe_synchronization_signals(
            self.data,
            primary_timeframe=self.cfg.primary_timeframe,
            secondary_timeframes=self.cfg.secondary_timeframes,
            sync_threshold=self.cfg.alignment_threshold
        )

        # Extract signal columns
        momentum_signal_cols = [col for col in mtf_signals.columns if "signal" in col.lower()]
        sync_signal_cols = [col for col in sync_signals.columns if "signal" in col.lower()]

        if momentum_signal_cols:
            momentum_values = mtf_signals[momentum_signal_cols[0]]
        else:
            momentum_values = pd.Series(0, index=self.data.index)

        if sync_signal_cols:
            sync_values = sync_signals[sync_signal_cols[0]]
        else:
            sync_values = pd.Series(0, index=self.data.index)

        # Store signals directly
        self.momentum_values = momentum_values.fillna(0)
        self.sync_values = sync_values.fillna(0)
        self.current_idx = 0

        # Multi-timeframe entry rules - simplified
        self.add_rule(
            when(lambda strat: strat._check_mtf_long_entry())
            .then(lambda strat: strat.buy(size=strat.cfg.position_size))
            .name("mtf_long_entry")
        )

        self.add_rule(
            when(lambda strat: strat._check_mtf_short_entry())
            .then(lambda strat: strat.sell(size=strat.cfg.position_size))
            .name("mtf_short_entry")
        )

        # Exit when signals diverge
        self.add_rule(
            when(lambda strat: strat._check_mtf_exit())
            .then(lambda strat: strat.close_positions())
            .name("mtf_exit_divergence")
        )

    def _check_mtf_long_entry(self) -> bool:
        """Check multi-timeframe signals for long entry."""
        try:
            momentum_val = self.momentum_values.iloc[self.current_idx]
            sync_val = self.sync_values.iloc[self.current_idx]
            return (momentum_val > self.cfg.momentum_threshold and sync_val > 0)
        except (IndexError, KeyError):
            return False

    def _check_mtf_short_entry(self) -> bool:
        """Check multi-timeframe signals for short entry."""
        try:
            momentum_val = self.momentum_values.iloc[self.current_idx]
            sync_val = self.sync_values.iloc[self.current_idx]
            return (momentum_val < -self.cfg.momentum_threshold and sync_val < 0)
        except (IndexError, KeyError):
            return False

    def _check_mtf_exit(self) -> bool:
        """Check for multi-timeframe exit signal."""
        try:
            sync_val = self.sync_values.iloc[self.current_idx]
            return sync_val == 0
        except (IndexError, KeyError):
            return False

    def next(self) -> None:
        """Update current index for rule evaluation."""
        self.current_idx = len(self.data) - 1


def run_multi_timeframe_bot(
    data: pd.DataFrame,
    *,
    config: Optional[MultiTimeframeConfig] = None,
    initial_cash: float = 10_000.0,
) -> BotResult:
    """Run a multi-timeframe analysis bot."""

    cfg = config or MultiTimeframeConfig()
    strategy = _MultiTimeframeStrategy(cfg)
    strategy.set_data(data)  # Set data for strategy
    engine = EventBacktester(data, symbol="MTF", strategy=strategy, initial_cash=initial_cash)
    result = engine.run()
    logs = strategy.logs_dataframe()

    bot_result = BotResult(equity_curve=result.equity_curve, trades=len(result.trades), logs=logs)
    bot_result.calculate_metrics()
    return bot_result


__all__ = [
    # Core classes
    "BotResult",

    # Basic bot configurations and runners
    "MeanReversionConfig",
    "BreakoutConfig",
    "run_mean_reversion_bot",
    "run_breakout_bot",

    # Advanced bot configurations and runners
    "PairsTradingConfig",
    "ArbitrageConfig",
    "TrendFollowingConfig",
    "MLBasedConfig",
    "RiskParityConfig",
    "MultiTimeframeConfig",

    "run_pairs_trading_bot",
    "run_arbitrage_bot",
    "run_trend_following_bot",
    "run_ml_based_bot",
    "run_risk_parity_bot",
    "run_multi_timeframe_bot",
]


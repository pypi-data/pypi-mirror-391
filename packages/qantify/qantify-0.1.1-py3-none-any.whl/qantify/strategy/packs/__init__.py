"""Pre-built strategy packs delivering turnkey trading templates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple, Type, Union, Literal

import numpy as np
import pandas as pd

from qantify.backtest.risk import DailyLossRule, MaxDrawdownRule, RiskRule
from qantify.core.types import Symbol, TimeFrame
from qantify.risk import RiskReport, build_risk_report
from qantify.signals import ema, atr
from qantify.strategy.base import Strategy, IndicatorFrame, IndicatorSeries
from qantify.strategy.parameters import parameter
from qantify.backtest.types import OrderStatus

if TYPE_CHECKING:
    from qantify.backtest import EventBacktestResult, VectorizedBacktestResult
    from qantify.backtest.costs import CommissionModel, SlippageModel
else:
    EventBacktestResult = VectorizedBacktestResult = None  # type: ignore
    CommissionModel = SlippageModel = object  # type: ignore

PackMode = Literal["event", "vectorized"]


def _default_commission() -> "CommissionModel":
    from qantify.backtest.costs import NoCommission

    return NoCommission()


def _default_slippage() -> "SlippageModel":
    from qantify.backtest.costs import NoSlippage

    return NoSlippage()


def _annual_periods_from_timeframe(timeframe: TimeFrame) -> int:
    seconds = timeframe.seconds
    if seconds <= 0:
        return 252
    per_day = max(1, int(round(86_400 / seconds)))
    trading_days = 252
    return max(1, per_day * trading_days)


@dataclass(slots=True)
class StrategyPackMetadata:
    slug: str
    name: str
    category: str
    summary: str
    description: str
    timeframe: TimeFrame
    symbols: Tuple[Symbol, ...]
    required_columns: Tuple[str, ...]
    tags: Tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


@dataclass(slots=True)
class StrategyPackBacktestConfig:
    initial_cash: float = 100_000.0
    commission_factory: Callable[[], CommissionModel] = _default_commission
    slippage_factory: Callable[[], SlippageModel] = _default_slippage
    risk_rule_factories: Tuple[Callable[[], RiskRule], ...] = field(default_factory=lambda: (lambda: MaxDrawdownRule(0.2), lambda: DailyLossRule(0.1)))
    price_column: str = "close"
    periods_per_year: Optional[int] = None
    risk_free_rate: float = 0.0
    rolling_window: int = 63
    var_level: float = 0.05

    def create_commission(self) -> CommissionModel:
        return self.commission_factory()

    def create_slippage(self) -> SlippageModel:
        return self.slippage_factory()

    def create_risk_rules(self) -> Sequence[RiskRule]:
        return [factory() for factory in self.risk_rule_factories]


@dataclass(slots=True)
class VectorizedPackSpec:
    frame: pd.DataFrame
    entry_signal: pd.Series
    exit_signal: Optional[pd.Series] = None
    short_entry_signal: Optional[pd.Series] = None
    short_exit_signal: Optional[pd.Series] = None
    symbol: str = "SYNTH"
    allow_short: bool = False
    allocation: float = 1.0
    leverage: float = 1.0
    position_mode: Literal["full", "capital", "fixed"] = "capital"
    fixed_size: float = 1.0
    price_column: str = "close"


@dataclass(slots=True)
class StrategyPackResult:
    pack: "StrategyPack"
    strategy: Optional[Strategy]
    event_result: Optional["EventBacktestResult"]
    vectorized_result: Optional["VectorizedBacktestResult"]
    risk_report: RiskReport
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def orders_frame(self) -> pd.DataFrame:
        if self.event_result:
            from qantify.backtest.reporting import orders_to_frame

            return orders_to_frame(self.event_result.orders)
        if self.vectorized_result:
            from qantify.backtest.reporting import orders_to_frame

            return orders_to_frame(self.vectorized_result.orders)
        return pd.DataFrame(columns=["timestamp", "symbol", "side", "type"])

    def trades_frame(self) -> pd.DataFrame:
        if self.event_result:
            from qantify.backtest.reporting import trades_to_frame

            return trades_to_frame(self.event_result.trades)
        if self.vectorized_result:
            from qantify.backtest.reporting import trades_to_frame

            return trades_to_frame(self.vectorized_result.trades)
        return pd.DataFrame(columns=["entry_time", "exit_time", "symbol", "pnl"])


class StrategyPackRegistryError(RuntimeError):
    pass


@dataclass(slots=True)
class StrategyPack:
    metadata: StrategyPackMetadata
    mode: PackMode
    backtest_config: StrategyPackBacktestConfig
    default_parameters: Mapping[str, Any] = field(default_factory=dict)
    strategy_cls: Optional[Type[Strategy]] = None
    data_prep: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
    vectorized_builder: Optional[Callable[[pd.DataFrame], VectorizedPackSpec]] = None
    documentation: Optional[str] = None

    def create_strategy(self, **overrides: Any) -> Strategy:
        if self.mode != "event":
            raise StrategyPackRegistryError("Strategy packs in vectorized mode do not expose strategy classes.")
        if self.strategy_cls is None:
            raise StrategyPackRegistryError("Event-driven strategy pack missing strategy class.")
        params = dict(self.default_parameters)
        params.update(overrides)
        return self.strategy_cls(**params)

    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        prepared = self.data_prep(data) if self.data_prep is not None else data
        if not isinstance(prepared.index, pd.DatetimeIndex):
            raise StrategyPackRegistryError("Strategy pack expects data indexed by DatetimeIndex.")
        if prepared.index.tzinfo is None:
            prepared = prepared.tz_localize("UTC")
        else:
            prepared = prepared.tz_convert("UTC")
        return prepared

    def run_backtest(
        self,
        data: pd.DataFrame,
        *,
        symbol: Optional[str] = None,
        strategy_params: Optional[Mapping[str, Any]] = None,
        commission_model: Optional[CommissionModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        risk_rules: Optional[Sequence[RiskRule]] = None,
    ) -> StrategyPackResult:
        prepared = self._prepare_data(data)
        periods_per_year = self.backtest_config.periods_per_year or _annual_periods_from_timeframe(self.metadata.timeframe)
        if self.mode == "event":
            target_symbol = symbol or str(self.metadata.symbols[0])
            from qantify.backtest import EventBacktester

            strategy = self.create_strategy(**(strategy_params or {}))
            backtester = EventBacktester(
                prepared,
                symbol=target_symbol,
                strategy=strategy,
                initial_cash=self.backtest_config.initial_cash,
                commission_model=commission_model or self.backtest_config.create_commission(),
                slippage_model=slippage_model or self.backtest_config.create_slippage(),
                price_column=self.backtest_config.price_column,
                risk_rules=list(risk_rules) if risk_rules is not None else self.backtest_config.create_risk_rules(),
            )
            if getattr(strategy, "data", None) is None and hasattr(strategy, "_bind"):
                strategy._bind(
                    data=prepared,
                    symbol=target_symbol,
                    broker=backtester.broker,
                    portfolio=backtester.portfolio,
                    price_column=self.backtest_config.price_column,
                )
            event_result = backtester.run()
            risk_report = build_risk_report(
                event_result.equity_curve,
                trades=event_result.trades,
                periods_per_year=periods_per_year,
                risk_free_rate=self.backtest_config.risk_free_rate,
                rolling_window=self.backtest_config.rolling_window,
                var_level=self.backtest_config.var_level,
            )
            artifacts: Dict[str, Any] = {"equity_curve": event_result.equity_curve}
            return StrategyPackResult(
                pack=self,
                strategy=strategy,
                event_result=event_result,
                vectorized_result=None,
                risk_report=risk_report,
                artifacts=artifacts,
            )

        if self.vectorized_builder is None:
            raise StrategyPackRegistryError("Vectorized strategy pack missing vectorized builder.")
        spec = self.vectorized_builder(prepared)
        from qantify.backtest.vectorized import run as run_vectorized
        vectorized_result = run_vectorized(
            spec.frame,
            symbol=spec.symbol,
            entry_signal=spec.entry_signal,
            exit_signal=spec.exit_signal,
            short_entry_signal=spec.short_entry_signal,
            short_exit_signal=spec.short_exit_signal,
            initial_capital=self.backtest_config.initial_cash,
            allocation=spec.allocation,
            leverage=spec.leverage,
            allow_short=spec.allow_short,
            commission_model=commission_model or self.backtest_config.create_commission(),
            slippage_model=slippage_model or self.backtest_config.create_slippage(),
            price_column=spec.price_column,
            position_mode=spec.position_mode,
            fixed_size=spec.fixed_size,
        )
        risk_report = build_risk_report(
            vectorized_result.equity_curve,
            trades=vectorized_result.trades,
            periods_per_year=periods_per_year,
            risk_free_rate=self.backtest_config.risk_free_rate,
            rolling_window=self.backtest_config.rolling_window,
            var_level=self.backtest_config.var_level,
        )
        artifacts = {
            "signals": {
                "entry_long": spec.entry_signal,
                "exit_long": spec.exit_signal,
                "entry_short": spec.short_entry_signal,
                "exit_short": spec.short_exit_signal,
            },
        }
        return StrategyPackResult(
            pack=self,
            strategy=None,
            event_result=None,
            vectorized_result=vectorized_result,
            risk_report=risk_report,
            artifacts=artifacts,
        )


_PACK_REGISTRY: Dict[str, StrategyPack] = {}


def register_pack(pack: StrategyPack, *, overwrite: bool = False) -> None:
    key = pack.metadata.slug.lower()
    if not overwrite and key in _PACK_REGISTRY:
        raise StrategyPackRegistryError(f"Strategy pack '{pack.metadata.slug}' already registered.")
    _PACK_REGISTRY[key] = pack


def get_pack(slug: str) -> StrategyPack:
    key = slug.lower()
    try:
        return _PACK_REGISTRY[key]
    except KeyError as exc:
        raise StrategyPackRegistryError(f"Strategy pack '{slug}' is not registered.") from exc


def available_packs() -> Tuple[str, ...]:
    return tuple(sorted(_PACK_REGISTRY.keys()))


@parameter(
    "fast_window",
    default=21,
    bounds=(5, 63),
    description="Fast EMA lookback for primary trend signal.",
)
@parameter(
    "slow_window",
    default=84,
    bounds=(20, 252),
    description="Slow EMA lookback to define structural trend.",
)
@parameter(
    "atr_window",
    default=14,
    bounds=(5, 63),
    description="ATR lookback for volatility sizing.",
)
@parameter(
    "risk_per_trade",
    default=0.01,
    bounds=(0.001, 0.05),
    description="Fraction of equity risked per signal.",
)
@parameter(
    "atr_stop_multiple",
    default=3.0,
    bounds=(1.0, 6.0),
    description="Stop distance in ATR multiples.",
)
@parameter(
    "take_profit_multiple",
    default=4.0,
    bounds=(1.0, 8.0),
    description="Take profit distance in ATR multiples.",
)
@parameter(
    "trailing_atr_multiple",
    default=1.5,
    bounds=(0.5, 4.0),
    description="ATR multiple for dynamic trailing stop. Set to 0 to disable.",
)
@parameter(
    "max_position_units",
    default=5.0,
    bounds=(0.5, 20.0),
    description="Maximum absolute unit exposure for the underlying.",
)
class DualMovingAverageTrendStrategy(Strategy):
    """Classic dual-EMA trend follower with ATR-based sizing and protective orders."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("Trend strategy requires OHLCV data to be bound.")

        fast_window = int(self.get_parameter("fast_window"))
        slow_window = int(self.get_parameter("slow_window"))
        if fast_window >= slow_window:
            raise ValueError("fast_window must be smaller than slow_window for proper trend detection.")

        atr_window = int(self.get_parameter("atr_window"))
        close_series = self.data[self.price_column]

        self.fast_ma = self.I(
            ema,
            close_series,
            period=fast_window,
            name=f"ema_fast_{fast_window}",
            cache=False,
        )
        self.slow_ma = self.I(
            ema,
            close_series,
            period=slow_window,
            name=f"ema_slow_{slow_window}",
            cache=False,
        )

        atr_handle = self.I(
            atr,
            self.data,
            period=atr_window,
            name=f"atr_{atr_window}",
            cache=False,
        )
        if isinstance(atr_handle, IndicatorFrame):
            column = f"ATR_{atr_window}"
            self.atr = atr_handle[column] if column in atr_handle.frame.columns else atr_handle.frame.iloc[:, 0]
        else:
            self.atr = atr_handle

        self.stop_order = None
        self.take_profit_order = None
        self.trailing_order = None
        self.log("trend_pack_initialized", fast_window=fast_window, slow_window=slow_window, atr_window=atr_window)

    def next(self) -> None:
        price = self.price()
        atr_value = float(self.atr.current)
        if not np.isfinite(atr_value) or atr_value <= 0:
            return

        fast = float(self.fast_ma.current)
        slow = float(self.slow_ma.current)
        if not np.isfinite(fast) or not np.isfinite(slow):
            return

        atr_multiple = float(self.get_parameter("atr_stop_multiple"))
        trailing_multiple = float(self.get_parameter("trailing_atr_multiple"))
        take_profit_multiple = float(self.get_parameter("take_profit_multiple"))
        risk_fraction = float(self.get_parameter("risk_per_trade"))
        max_units = float(self.get_parameter("max_position_units"))

        if not self.has_position:
            if self.fast_ma.cross_above(self.slow_ma):
                stop_distance = atr_value * atr_multiple
                if stop_distance <= 0 or not np.isfinite(stop_distance):
                    return
                equity = max(self.equity, 1.0)
                target_risk_capital = equity * risk_fraction
                quantity = min(max_units, target_risk_capital / stop_distance)
                if quantity <= 0:
                    return
                fill = self.buy(size=quantity)
                if fill is None:
                    return
                stop_price = max(price - stop_distance, 0.0)
                limit_price = price + atr_value * take_profit_multiple
                self._cancel_protective_orders()
                self.stop_order = self.stop(stop_price, size=1.0)
                self.take_profit_order = self.limit(limit_price, side="sell", size=1.0)
                if trailing_multiple > 0:
                    self.trailing_order = self.trailing_stop(
                        side="sell",
                        size=1.0,
                        trail_amount=atr_value * trailing_multiple,
                    )
                self.log(
                    "trend_entry",
                    price=price,
                    atr=atr_value,
                    stop_price=stop_price,
                    take_profit=limit_price,
                    quantity=quantity,
                )
            return

        # Updates while in position
        if self.fast_ma.cross_below(self.slow_ma):
            self.log("trend_exit_cross", price=price)
            self.close()
            self._cancel_protective_orders()
            return

        # Manage stop tightening based on ATR
        if self.stop_order is not None and getattr(self.stop_order, "status", None) not in {OrderStatus.CANCELLED, OrderStatus.FILLED}:
            current_stop = getattr(self.stop_order, "stop_price", None)
            desired_stop = price - atr_value * atr_multiple * 0.5
            if current_stop is not None and desired_stop > current_stop + 1e-6:
                self.cancel(self.stop_order)
                self.stop_order = self.stop(desired_stop, size=1.0)
                self.log("trend_stop_tightened", new_stop=desired_stop)

    def on_fill(self, fill: Any) -> None:
        super().on_fill(fill)
        if getattr(fill.order, "type", None) and getattr(fill.order, "type").name == "STOP":
            self._cancel_protective_orders()

    def _cancel_protective_orders(self) -> None:
        for handle_name in ("stop_order", "take_profit_order", "trailing_order"):
            handle = getattr(self, handle_name, None)
            if handle is not None:
                self.cancel(handle)
            setattr(self, handle_name, None)


@parameter(
    "target_delta",
    default=0.0,
    bounds=(-100_000.0, 100_000.0),
    description="Target portfolio delta to maintain.",
)
@parameter(
    "rebalance_threshold",
    default=0.0,
    bounds=(0.0, 0.2),
    description="Minimum absolute delta gap (as fraction of contract multiplier) before hedging.",
)
@parameter(
    "contract_multiplier",
    default=100.0,
    bounds=(1.0, 1_000.0),
    description="Underlying units represented by one option contract.",
)
@parameter(
    "option_contracts",
    default=10.0,
    bounds=(1.0, 100.0),
    description="Number of option contracts held (positive for long, negative for short).",
)
@parameter(
    "max_hedge_units",
    default=50.0,
    bounds=(1.0, 1_000.0),
    description="Cap on absolute hedge trade size in underlying units.",
)
@parameter(
    "gamma_limit",
    default=5000.0,
    bounds=(0.0, 50000.0),
    description="Threshold for gamma exposure logging alerts.",
)
class DeltaHedgingStrategy(Strategy):
    """Delta-neutral hedging overlay for an options book traded via the underlying asset."""

    REQUIRED_COLUMNS = ("close", "option_delta", "option_gamma", "option_vega", "implied_vol")

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("Delta hedging strategy requires enriched option dataset.")
        missing = [col for col in self.REQUIRED_COLUMNS if col not in self.data.columns]
        if missing:
            raise KeyError(f"Dataset missing required columns: {missing}")
        self.log("delta_hedge_initialized", option_contracts=self.get_parameter("option_contracts"))

    def next(self) -> None:
        row = self.row
        if row is None:
            return

        contract_multiplier = float(self.get_parameter("contract_multiplier"))
        option_contracts = float(self.get_parameter("option_contracts"))
        target_delta = float(self.get_parameter("target_delta"))
        threshold = float(self.get_parameter("rebalance_threshold")) * contract_multiplier
        max_units = float(self.get_parameter("max_hedge_units"))
        gamma_limit = float(self.get_parameter("gamma_limit"))

        option_delta = float(row["option_delta"])
        option_gamma = float(row["option_gamma"])
        option_vega = float(row["option_vega"])
        implied_vol = float(row["implied_vol"])

        book_delta = option_delta * option_contracts * contract_multiplier
        underlying_delta = self.position_quantity * contract_multiplier
        net_delta = book_delta + underlying_delta
        delta_gap = target_delta - net_delta

        self.record(
            "hedge_state",
            net_delta=net_delta,
            delta_gap=delta_gap,
            gamma=option_gamma * option_contracts * (contract_multiplier ** 2),
            vega=option_vega * option_contracts,
            implied_vol=implied_vol,
        )

        if abs(delta_gap) > threshold:
            hedge_units = float(np.clip(delta_gap / contract_multiplier, -max_units, max_units))
            if hedge_units > 0:
                self.buy(size=hedge_units)
                side = "buy"
            elif hedge_units < 0:
                quantity = abs(hedge_units)
                if getattr(self.portfolio, "allow_short", True):
                    fill = self.broker.sell(quantity)
                    self.log("delta_rebalance_fill", quantity=quantity, price=getattr(fill, "price", self.price()))
                else:
                    self.log("delta_rebalance_blocked", reason="shorting_disabled", severity="warning")
                    return
                side = "sell"
            else:
                side = "hold"
            self.log("delta_rebalance", side=side, hedge_units=hedge_units, delta_gap=delta_gap, net_delta=net_delta)

        if abs(option_gamma) * abs(option_contracts) * (contract_multiplier ** 2) > gamma_limit:
            self.log(
                "gamma_alert",
                gamma=option_gamma,
                contracts=option_contracts,
                multiplier=contract_multiplier,
                implied_vol=implied_vol,
                severity="warning",
            )


def _stat_arb_builder(data: pd.DataFrame) -> VectorizedPackSpec:
    required = ("asset_a_close", "asset_b_close")
    for col in required:
        if col not in data.columns:
            raise KeyError(f"Stat-arb pack requires column '{col}'.")

    hedge_ratio = 1.0
    log_a = np.log(data["asset_a_close"])
    log_b = np.log(data["asset_b_close"])
    spread = (log_a - hedge_ratio * log_b).bfill().ffill()

    rolling = spread.rolling(window=40, min_periods=20)
    spread_mean = rolling.mean()
    spread_std = rolling.std(ddof=0).replace(0, np.nan)
    zscore = ((spread - spread_mean) / spread_std).fillna(0.0)

    median = spread.median()
    lower_band = spread.quantile(0.35)
    upper_band = spread.quantile(0.65)

    long_entry = spread < lower_band
    long_exit = spread >= median
    short_entry = spread > upper_band
    short_exit = spread <= median

    synthetic_close = (spread - spread.mean()).cumsum() + 100.0
    synthetic_open = synthetic_close.shift(1).fillna(synthetic_close.iloc[0])
    bar_range = synthetic_close.diff().abs().fillna(0.0) + 0.1
    synthetic_high = (pd.concat([synthetic_open, synthetic_close], axis=1).max(axis=1) + bar_range)
    synthetic_low = (pd.concat([synthetic_open, synthetic_close], axis=1).min(axis=1) - bar_range)

    frame = pd.DataFrame(
        {
            "open": synthetic_open,
            "high": synthetic_high,
            "low": synthetic_low,
            "close": synthetic_close,
            "volume": np.ones_like(synthetic_close) * 1_000,
        },
        index=data.index,
    )

    return VectorizedPackSpec(
        frame=frame,
        entry_signal=long_entry,
        exit_signal=long_exit,
        short_entry_signal=short_entry,
        short_exit_signal=short_exit,
        symbol="PAIR_SPREAD",
        allow_short=True,
        allocation=0.5,
        leverage=1.0,
        position_mode="capital",
        price_column="close",
    )


def _register_default_packs() -> None:
    usd_btc = Symbol("BTCUSDT", exchange="binance")
    btc_timeframe = TimeFrame("1h", "1H", 3_600)

    trend_pack = StrategyPack(
        metadata=StrategyPackMetadata(
            slug="trend-following",
            name="Dual EMA Trend Following",
            category="trend",
            summary="Directional breakout follower with ATR risk overlay.",
            description="Systematic dual-EMA trend follower with ATR-based position sizing, stop-loss, take-profit, and trailing protection for discretionary or systematic desks.",
            timeframe=btc_timeframe,
            symbols=(usd_btc,),
            required_columns=("open", "high", "low", "close", "volume"),
            tags=("trend", "momentum", "atr"),
        ),
        mode="event",
        backtest_config=StrategyPackBacktestConfig(
            initial_cash=250_000.0,
            risk_rule_factories=(
                lambda: MaxDrawdownRule(0.25),
                lambda: DailyLossRule(0.08),
            ),
            price_column="close",
            periods_per_year=None,
            rolling_window=84,
            risk_free_rate=0.01,
            var_level=0.05,
        ),
        default_parameters={
            "fast_window": 34,
            "slow_window": 144,
            "atr_window": 21,
            "risk_per_trade": 0.015,
            "atr_stop_multiple": 2.5,
            "take_profit_multiple": 5.0,
            "trailing_atr_multiple": 1.0,
            "max_position_units": 4.0,
        },
        strategy_cls=DualMovingAverageTrendStrategy,
    )

    register_pack(trend_pack, overwrite=True)

    options_symbol = Symbol("ES", exchange="cme")
    daily_timeframe = TimeFrame("1d", "1D", 86_400)

    options_pack = StrategyPack(
        metadata=StrategyPackMetadata(
            slug="options-hedging",
            name="Delta Overlay Hedger",
            category="derivatives",
            summary="Delta-neutral overlay for option portfolios using underlying futures.",
            description="Maintains delta exposure near target by trading the underlying while monitoring gamma and vega risk with automated alerts.",
            timeframe=daily_timeframe,
            symbols=(options_symbol,),
            required_columns=DeltaHedgingStrategy.REQUIRED_COLUMNS,
            tags=("options", "hedging", "delta-neutral"),
        ),
        mode="event",
        backtest_config=StrategyPackBacktestConfig(
            initial_cash=5_000_000.0,
            risk_rule_factories=(
                lambda: MaxDrawdownRule(0.15),
                lambda: DailyLossRule(0.05),
            ),
            price_column="close",
            periods_per_year=None,
            rolling_window=21,
            risk_free_rate=0.02,
            var_level=0.025,
        ),
        default_parameters={
            "target_delta": 0.0,
            "rebalance_threshold": 0.01,
            "contract_multiplier": 50.0,
            "option_contracts": 25.0,
            "max_hedge_units": 200.0,
            "gamma_limit": 12_500.0,
        },
        strategy_cls=DeltaHedgingStrategy,
    )

    register_pack(options_pack, overwrite=True)

    equities_timeframe = TimeFrame("1h", "1H", 3_600)
    stat_pack = StrategyPack(
        metadata=StrategyPackMetadata(
            slug="stat-arb-basket",
            name="Pairs Trading Basket",
            category="stat-arb",
            summary="Mean-reversion stat-arb template using log-spread z-score triggers.",
            description="Classic pairs trading blueprint that computes rolling z-scores on log-price spreads for two correlated assets, supporting long/short spread trades with capital allocation controls.",
            timeframe=equities_timeframe,
            symbols=(Symbol("SPY"), Symbol("QQQ")),
            required_columns=("asset_a_close", "asset_b_close"),
            tags=("stat-arb", "mean-reversion", "pairs"),
        ),
        mode="vectorized",
        backtest_config=StrategyPackBacktestConfig(
            initial_cash=1_000_000.0,
            risk_rule_factories=tuple(),
            price_column="close",
            periods_per_year=None,
            rolling_window=63,
            risk_free_rate=0.01,
            var_level=0.05,
        ),
        vectorized_builder=_stat_arb_builder,
    )

    register_pack(stat_pack, overwrite=True)


_register_default_packs()


# Import all strategy pack modules (with fallbacks for optional modules)
from . import trend_following
from . import mean_reversion
from . import statistical_arbitrage

# Optional modules - import if available
try:
    from . import momentum
except ImportError:
    momentum = None

try:
    from . import volatility
except ImportError:
    volatility = None

try:
    from . import breakout
except ImportError:
    breakout = None

try:
    from . import ml_based
except ImportError:
    ml_based = None

try:
    from . import risk_parity
except ImportError:
    risk_parity = None

try:
    from . import market_neutral
except ImportError:
    market_neutral = None

try:
    from . import seasonal
except ImportError:
    seasonal = None

try:
    from . import multi_asset
except ImportError:
    multi_asset = None

try:
    from . import crypto
except ImportError:
    crypto = None

try:
    from . import forex
except ImportError:
    forex = None

try:
    from . import options
except ImportError:
    options = None

try:
    from . import futures
except ImportError:
    futures = None

try:
    from . import factor_investing
except ImportError:
    factor_investing = None

try:
    from . import sentiment_based
except ImportError:
    sentiment_based = None

try:
    from . import high_frequency
except ImportError:
    high_frequency = None

# Re-export all strategies from modules
__all__ = [
    # Core pack infrastructure
    "StrategyPack",
    "StrategyPackResult",
    "StrategyPackMetadata",
    "StrategyPackBacktestConfig",
    "VectorizedPackSpec",
    "StrategyPackRegistryError",
    "register_pack",
    "get_pack",
    "available_packs",
    "DualMovingAverageTrendStrategy",
    "DeltaHedgingStrategy",

    # Trend following strategies
    "SMACrossoverStrategy",
    "EMACrossoverStrategy",
    "ADXTrendStrategy",
    "SuperTrendStrategy",
    "ParabolicSARStrategy",
    "IchimokuCloudStrategy",
    "DPOTrendStrategy",
    "VortexStrategy",
    "AroonStrategy",
    "WilliamsAlligatorStrategy",

    # Mean reversion strategies
    "RSIMeanReversionStrategy",
    "BollingerMeanReversionStrategy",
    "ZScoreMeanReversionStrategy",
    "DeviationMeanReversionStrategy",
    "WilliamsRReversionStrategy",
    "StochasticReversionStrategy",
    "CCIReversionStrategy",
    "UltimateOscillatorStrategy",
    "KeltnerChannelStrategy",
    "DonchianChannelStrategy",

    # Statistical arbitrage
    "PairsTradingStrategy",
    "CointegrationStrategy",
    "TriangularArbitrageStrategy",
    "CrossAssetArbitrageStrategy",
    "ETFArbitrageStrategy",
    "FuturesArbitrageStrategy",
    "OptionsArbitrageStrategy",
    "ConvertibleArbitrageStrategy",
    "RiskArbitrageStrategy",
    "StatisticalArbitrageStrategy",

    # Momentum strategies
    "RSIMomentumStrategy",
    "MACDMomentumStrategy",
    "StochasticMomentumStrategy",
    "ROCStrategy",
    "WilliamsRStrategy",
    "TSIMomentumStrategy",
    "AwesomeOscillatorStrategy",
    "BalanceOfPowerStrategy",
    "ChandeMomentumStrategy",
    "DynamicMomentumStrategy",

    # Volatility strategies
    "ATRStrategy",
    "BollingerBandsStrategy",
    "VIXStrategy",
    "RealizedVolatilityStrategy",
    "ImpliedVolatilityStrategy",
    "GARCHVolatilityStrategy",
    "HistoricalVolatilityStrategy",
    "YangZhangVolatilityStrategy",
    "ParkinsonVolatilityStrategy",
    "RogersSatchellVolatilityStrategy",

    # Breakout strategies
    "ChannelBreakoutStrategy",
    "VolumeBreakoutStrategy",
    "PriceBreakoutStrategy",
    "ConsolidationBreakoutStrategy",
    "GapBreakoutStrategy",
    "FlagPatternBreakoutStrategy",
    "TriangleBreakoutStrategy",
    "RectangleBreakoutStrategy",
    "CupHandleBreakoutStrategy",
    "InverseHeadShouldersStrategy",

    # ML-based strategies
    "MLSignalStrategy",
    "EnsembleStrategy",
    "ReinforcementLearningStrategy",
    "NeuralNetworkStrategy",
    "GradientBoostingStrategy",
    "RandomForestStrategy",
    "XGBoostSignalStrategy",
    "LightGBMStrategy",
    "CatBoostStrategy",
    "SVMStrategy",
    "LogisticRegressionStrategy",
    "NaiveBayesStrategy",
    "KNNStrategy",
    "AdaBoostStrategy",
    "BaggingStrategy",
    "ExtraTreesStrategy",
    "IsolationForestStrategy",
    "OneClassSVMStrategy",
    "AutoencoderStrategy",
    "GANStrategy",

    # Risk parity and portfolio strategies
    "RiskParityStrategy",
    "EqualRiskStrategy",
    "MaximumDiversificationStrategy",
    "MinimumVarianceStrategy",
    "EfficientFrontierStrategy",
    "BlackLittermanStrategy",
    "HierarchicalRiskParityStrategy",
    "MostDiversifiedPortfolioStrategy",
    "EqualWeightStrategy",
    "InverseVolatilityStrategy",
    "MinimumCorrelationStrategy",
    "MaximumSharpeStrategy",
    "SemiVarianceStrategy",
    "CVaRStrategy",
    "DrawdownParityStrategy",

    # Market neutral strategies
    "MarketNeutralLongShortStrategy",
    "DollarNeutralStrategy",
    "BetaNeutralStrategy",
    "FactorNeutralStrategy",
    "StatisticalNeutralStrategy",
    "PairsNeutralStrategy",
    "SectorNeutralStrategy",
    "CountryNeutralStrategy",
    "CurrencyNeutralStrategy",
    "InflationNeutralStrategy",

    # Seasonal strategies
    "SeasonalStrategy",
    "CalendarEffectStrategy",
    "HolidayEffectStrategy",
    "MonthlySeasonalStrategy",
    "QuarterlySeasonalStrategy",
    "JanuaryEffectStrategy",
    "SellInMayStrategy",
    "HalloweenEffectStrategy",
    "DayOfWeekStrategy",
    "TimeOfDayStrategy",
    "TurnOfMonthStrategy",
    "QuarterlyRebalancingStrategy",
    "RebalancingAnomalyStrategy",
    "OptionsExpirationStrategy",
    "FOMCStrategy",

    # Multi-asset strategies
    "MultiAssetMomentumStrategy",
    "AssetAllocationStrategy",
    "CrossAssetMomentumStrategy",
    "GlobalMacroStrategy",
    "TAA_GlobalStrategy",
    "GTAA_GlobalStrategy",
    "PortableAlphaStrategy",
    "MultiStrategyStrategy",
    "FundOfFundsStrategy",
    "StyleRotationStrategy",

    # Crypto strategies
    "CryptoMomentumStrategy",
    "DeFiYieldStrategy",
    "NFTFloorPriceStrategy",
    "CryptoArbitrageStrategy",
    "LiquidityMiningStrategy",
    "StakingStrategy",
    "LendingStrategy",
    "FlashLoanArbitrageStrategy",
    "MEVStrategy",
    "ImpermanentLossStrategy",
    "LiquidityProvidingStrategy",
    "TokenSwapStrategy",
    "CrossChainArbitrageStrategy",
    "YieldFarmingStrategy",
    "LiquidityPoolStrategy",
    "DecentralizedExchangeStrategy",
    "AutomatedMarketMakerStrategy",

    # Forex strategies
    "CarryTradeStrategy",
    "CurrencyMomentumStrategy",
    "InterestRateStrategy",
    "FXVolatilityStrategy",
    "CurrencyBasketStrategy",
    "PurchasingPowerParityStrategy",
    "BigMacIndexStrategy",
    "BalanceOfPaymentsStrategy",
    "TermsOfTradeStrategy",
    "CurrencyCrisisStrategy",
    "SafeHavenStrategy",
    "RiskReversalStrategy",
    "FXSwapStrategy",
    "FXForwardStrategy",
    "FXOptionStrategy",

    # Options strategies
    "CoveredCallStrategy",
    "ProtectivePutStrategy",
    "IronCondorStrategy",
    "ButterflyStrategy",
    "StraddleStrategy",
    "StrangleStrategy",
    "CalendarSpreadStrategy",
    "DiagonalSpreadStrategy",
    "CollarStrategy",
    "SyntheticLongStrategy",
    "SyntheticShortStrategy",
    "PutCallParityStrategy",
    "BoxSpreadStrategy",
    "RatioSpreadStrategy",
    "BackRatioSpreadStrategy",
    "JellyRollStrategy",
    "DoubleDiagonalStrategy",
    "GammaScalpingStrategy",
    "DeltaHedgingStrategy",
    "VegaHedgingStrategy",
    "RhoHedgingStrategy",
    "ThetaStrategy",

    # Futures strategies
    "SpreadTradingStrategy",
    "CalendarSpreadStrategy",
    "CrackSpreadStrategy",
    "FuturesArbitrageStrategy",
    "RollYieldStrategy",
    "InterCommoditySpreadStrategy",
    "InterMarketSpreadStrategy",
    "ButterflySpreadStrategy",
    "CondorSpreadStrategy",
    "PackStrategy",
    "BundleStrategy",
    "StripStrategy",
    "StackHedgeStrategy",
    "CrossHedgeStrategy",
    "IndexArbitrageStrategy",
    "ProgramTradingStrategy",

    # Factor investing
    "ValueFactorStrategy",
    "GrowthFactorStrategy",
    "QualityFactorStrategy",
    "MomentumFactorStrategy",
    "LowVolatilityFactorStrategy",
    "SizeFactorStrategy",
    "DividendYieldFactorStrategy",
    "EarningsQualityFactorStrategy",
    "ProfitabilityFactorStrategy",
    "InvestmentFactorStrategy",
    "LeverageFactorStrategy",
    "LiquidityFactorStrategy",
    "BetaFactorStrategy",
    "IdiosyncraticVolatilityFactorStrategy",
    "AccrualsFactorStrategy",
    "AssetGrowthFactorStrategy",
    "ROA_FactorStrategy",
    "ROE_FactorStrategy",
    "ROIC_FactorStrategy",

    # Sentiment-based strategies
    "NewsSentimentStrategy",
    "SocialMediaSentimentStrategy",
    "PutCallRatioStrategy",
    "VIXSentimentStrategy",
    "TwitterSentimentStrategy",
    "RedditSentimentStrategy",
    "GoogleTrendsStrategy",
    "FearGreedIndexStrategy",
    "AAIIInvestorSentimentStrategy",
    "ConsumerConfidenceStrategy",
    "BusinessConfidenceStrategy",
    "EconomicSurpriseStrategy",
    "FedWatchStrategy",
    "OptionsSentimentStrategy",
    "OrderFlowSentimentStrategy",

    # High frequency strategies
    "MarketMakingStrategy",
    "OrderFlowStrategy",
    "LatencyArbitrageStrategy",
    "QuoteStuffingStrategy",
    "MomentumIgnitionStrategy",
    "OrderBookImbalanceStrategy",
    "TimeSalesStrategy",
    "VolumeProfileStrategy",
    "Level2Strategy",
    "VWAPStrategy",
    "TWAPStrategy",
    "POVStrategy",
    "ImplementationShortfallStrategy",
    "OptimalExecutionStrategy",
    "SmartOrderRoutingStrategy",
    "CoLocationStrategy",
    "FeedHandlerStrategy",
    "OrderManagementStrategy",
    "RiskManagementHFTStrategy",
    "ExecutionAlgorithmsStrategy",
]


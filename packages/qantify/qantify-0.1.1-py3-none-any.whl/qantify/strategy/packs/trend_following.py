"""Trend Following Strategy Packs.

This module contains various trend following strategies including:
- Moving average crossovers
- ADX-based trend strategies
- SuperTrend strategies
- Parabolic SAR strategies
- Ichimoku Cloud strategies
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
import pandas as pd

from qantify.strategy.base import Strategy
from qantify.strategy.parameters import parameter

# Import signals with fallbacks for optional indicators
from qantify.signals import ema, sma, adx, supertrend
try:
    from qantify.signals import psar
except ImportError:
    psar = None

try:
    from qantify.signals import ichimoku
except ImportError:
    ichimoku = None

if TYPE_CHECKING:
    from qantify.backtest import EventBacktestResult


@parameter(
    "fast_period",
    default=9,
    bounds=(5, 50),
    description="Fast moving average period",
)
@parameter(
    "slow_period",
    default=21,
    bounds=(10, 100),
    description="Slow moving average period",
)
@parameter(
    "risk_per_trade",
    default=0.02,
    bounds=(0.005, 0.05),
    description="Risk per trade as fraction of capital",
)
class SMACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("SMA Crossover strategy requires OHLCV data")

        fast_period = int(self.get_parameter("fast_period"))
        slow_period = int(self.get_parameter("slow_period"))

        self.fast_ma = self.I(
            sma,
            self.data[self.price_column],
            period=fast_period,
            name=f"sma_fast_{fast_period}"
        )

        self.slow_ma = self.I(
            sma,
            self.data[self.price_column],
            period=slow_period,
            name=f"sma_slow_{slow_period}"
        )

        self.log("sma_crossover_initialized",
                fast_period=fast_period,
                slow_period=slow_period)

    def next(self) -> None:
        if self.fast_ma.cross_above(self.slow_ma):
            risk_amount = self.equity * self.get_parameter("risk_per_trade")
            price = self.price()
            stop_loss = price * 0.95  # 5% stop loss
            quantity = risk_amount / (price - stop_loss)

            if quantity > 0:
                self.buy(size=quantity)
                self.log("sma_buy_signal",
                        price=price,
                        quantity=quantity,
                        stop_loss=stop_loss)

        elif self.fast_ma.cross_below(self.slow_ma):
            if self.has_position:
                self.sell(size=self.position_quantity)
                self.log("sma_sell_signal", price=self.price())


@parameter(
    "fast_period",
    default=12,
    bounds=(5, 50),
    description="Fast EMA period",
)
@parameter(
    "slow_period",
    default=26,
    bounds=(10, 100),
    description="Slow EMA period",
)
@parameter(
    "signal_period",
    default=9,
    bounds=(5, 20),
    description="MACD signal line period",
)
class EMACrossoverStrategy(Strategy):
    """Exponential Moving Average Crossover Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("EMA Crossover strategy requires OHLCV data")

        fast_period = int(self.get_parameter("fast_period"))
        slow_period = int(self.get_parameter("slow_period"))
        signal_period = int(self.get_parameter("signal_period"))

        fast_ema = self.I(ema, self.data[self.price_column], period=fast_period)
        slow_ema = self.I(ema, self.data[self.price_column], period=slow_period)

        self.macd = fast_ema - slow_ema
        self.signal = self.I(ema, self.macd, period=signal_period, name="macd_signal")

        self.log("ema_crossover_initialized",
                fast_period=fast_period,
                slow_period=slow_period,
                signal_period=signal_period)

    def next(self) -> None:
        if self.macd.cross_above(self.signal):
            if not self.has_position:
                self.buy(size=1.0)
                self.log("ema_buy_signal", price=self.price())

        elif self.macd.cross_below(self.signal):
            if self.has_position:
                self.sell(size=self.position_quantity)
                self.log("ema_sell_signal", price=self.price())


@parameter(
    "adx_period",
    default=14,
    bounds=(5, 50),
    description="ADX period",
)
@parameter(
    "adx_threshold",
    default=25,
    bounds=(10, 40),
    description="ADX trend strength threshold",
)
@parameter(
    "di_period",
    default=14,
    bounds=(5, 50),
    description="DI period",
)
class ADXTrendStrategy(Strategy):
    """ADX-based Trend Following Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("ADX strategy requires OHLCV data")

        adx_period = int(self.get_parameter("adx_period"))
        di_period = int(self.get_parameter("di_period"))

        adx_result = self.I(adx, self.data, period=adx_period)
        if hasattr(adx_result, 'ADX'):
            self.adx = adx_result.ADX
            self.plus_di = adx_result.DIP
            self.minus_di = adx_result.DIM
        else:
            # Fallback if structure is different
            self.adx = adx_result
            self.plus_di = self.I(lambda x: x['high'].diff().where(x['high'].diff() > 0, 0).rolling(di_period).mean(), self.data)
            self.minus_di = self.I(lambda x: x['low'].diff().where(x['low'].diff() < 0, 0).abs().rolling(di_period).mean(), self.data)

        self.log("adx_trend_initialized",
                adx_period=adx_period,
                adx_threshold=self.get_parameter("adx_threshold"))

    def next(self) -> None:
        adx_value = float(self.adx.current)
        plus_di = float(self.plus_di.current)
        minus_di = float(self.minus_di.current)
        threshold = self.get_parameter("adx_threshold")

        if adx_value > threshold:
            if plus_di > minus_di and not self.has_position:
                self.buy(size=1.0)
                self.log("adx_buy_signal",
                        adx=adx_value,
                        plus_di=plus_di,
                        minus_di=minus_di)
            elif minus_di > plus_di and self.has_position:
                self.sell(size=self.position_quantity)
                self.log("adx_sell_signal",
                        adx=adx_value,
                        plus_di=plus_di,
                        minus_di=minus_di)


@parameter(
    "factor",
    default=3,
    bounds=(1, 5),
    description="SuperTrend factor",
)
@parameter(
    "atr_period",
    default=10,
    bounds=(5, 20),
    description="ATR period for SuperTrend",
)
class SuperTrendStrategy(Strategy):
    """SuperTrend Trend Following Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("SuperTrend strategy requires OHLCV data")

        factor = self.get_parameter("factor")
        atr_period = int(self.get_parameter("atr_period"))

        supertrend_result = self.I(
            supertrend,
            self.data,
            factor=factor,
            atr_period=atr_period
        )

        if hasattr(supertrend_result, 'trend'):
            self.supertrend = supertrend_result.trend
        else:
            self.supertrend = supertrend_result

        self.log("supertrend_initialized",
                factor=factor,
                atr_period=atr_period)

    def next(self) -> None:
        trend = float(self.supertrend.current)

        if trend == 1.0 and not self.has_position:
            self.buy(size=1.0)
            self.log("supertrend_buy_signal", price=self.price())
        elif trend == -1.0 and self.has_position:
            self.sell(size=self.position_quantity)
            self.log("supertrend_sell_signal", price=self.price())


@parameter(
    "acceleration",
    default=0.02,
    bounds=(0.01, 0.1),
    description="Parabolic SAR acceleration factor",
)
@parameter(
    "max_acceleration",
    default=0.2,
    bounds=(0.1, 0.5),
    description="Maximum acceleration factor",
)
class ParabolicSARStrategy(Strategy):
    """Parabolic SAR Trend Following Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("Parabolic SAR strategy requires OHLCV data")

        acceleration = self.get_parameter("acceleration")
        max_acceleration = self.get_parameter("max_acceleration")

        self.psar = self.I(
            psar,
            self.data,
            acceleration=acceleration,
            max_acceleration=max_acceleration
        )

        self.log("psar_initialized",
                acceleration=acceleration,
                max_acceleration=max_acceleration)

    def next(self) -> None:
        price = self.price()
        psar_value = float(self.psar.current)

        # Buy when price crosses above PSAR
        if price > psar_value and not self.has_position:
            self.buy(size=1.0)
            self.log("psar_buy_signal", price=price, psar=psar_value)

        # Sell when price crosses below PSAR
        elif price < psar_value and self.has_position:
            self.sell(size=self.position_quantity)
            self.log("psar_sell_signal", price=price, psar=psar_value)


class IchimokuCloudStrategy(Strategy):
    """Ichimoku Cloud Trend Following Strategy."""

    def init(self) -> None:
        if self.data is None:
            raise RuntimeError("Ichimoku strategy requires OHLCV data")

        ichimoku_result = self.I(ichimoku, self.data)

        if hasattr(ichimoku_result, 'tenkan_sen'):
            self.tenkan_sen = ichimoku_result.tenkan_sen
            self.kijun_sen = ichimoku_result.kijun_sen
            self.senkou_span_a = ichimoku_result.senkou_span_a
            self.senkou_span_b = ichimoku_result.senkou_span_b
            self.chikou_span = ichimoku_result.chikou_span
        else:
            # Fallback implementation
            high_9 = self.data['high'].rolling(9).max()
            low_9 = self.data['low'].rolling(9).min()
            self.tenkan_sen = (high_9 + low_9) / 2

            high_26 = self.data['high'].rolling(26).max()
            low_26 = self.data['low'].rolling(26).min()
            self.kijun_sen = (high_26 + low_26) / 2

            self.senkou_span_a = ((self.tenkan_sen + self.kijun_sen) / 2).shift(26)
            self.senkou_span_b = ((high_52 + low_52) / 2).shift(26) if 'high_52' in locals() else self.senkou_span_a
            self.chikou_span = self.data[self.price_column].shift(-26)

        self.log("ichimoku_initialized")

    def next(self) -> None:
        price = self.price()
        tenkan = float(self.tenkan_sen.current)
        kijun = float(self.kijun_sen.current)
        senkou_a = float(self.senkou_span_a.current) if hasattr(self.senkou_span_a, 'current') else price
        senkou_b = float(self.senkou_span_b.current) if hasattr(self.senkou_span_b, 'current') else price

        # Bullish signals
        if (price > senkou_a and price > senkou_b and
            tenkan > kijun and not self.has_position):
            self.buy(size=1.0)
            self.log("ichimoku_buy_signal",
                    price=price,
                    tenkan=tenkan,
                    kijun=kijun)

        # Bearish signals
        elif (price < senkou_a and price < senkou_b and
              tenkan < kijun and self.has_position):
            self.sell(size=self.position_quantity)
            self.log("ichimoku_sell_signal",
                    price=price,
                    tenkan=tenkan,
                    kijun=kijun)


# Additional trend following strategies would be implemented here
# Each following the same pattern with proper parameter decorators

class DPOTrendStrategy(Strategy):
    """Detrended Price Oscillator Trend Strategy."""
    pass

class VortexStrategy(Strategy):
    """Vortex Indicator Trend Strategy."""
    pass

class AroonStrategy(Strategy):
    """Aroon Indicator Trend Strategy."""
    pass

class WilliamsAlligatorStrategy(Strategy):
    """Williams Alligator Trend Strategy."""
    pass


__all__ = [
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
]

"""Mean Reversion Strategy Packs.

This module contains various mean reversion strategies including:
- RSI-based strategies
- Bollinger Band strategies
- Z-Score strategies
- Statistical mean reversion
"""

from __future__ import annotations

from qantify.strategy.base import Strategy
from qantify.strategy.parameters import parameter
from qantify.signals import rsi, bollinger_bands, zscore


@parameter("rsi_period", default=14, bounds=(5, 30))
@parameter("oversold", default=30, bounds=(20, 40))
@parameter("overbought", default=70, bounds=(60, 80))
class RSIMeanReversionStrategy(Strategy):
    """RSI-based Mean Reversion Strategy."""

    def init(self):
        self.rsi = self.I(rsi, self.data['close'], period=int(self.get_parameter("rsi_period")))

    def next(self):
        rsi_val = self.rsi.current
        if rsi_val < self.get_parameter("oversold") and not self.has_position:
            self.buy(size=1.0)
        elif rsi_val > self.get_parameter("overbought") and self.has_position:
            self.sell(size=self.position_quantity)


@parameter("period", default=20, bounds=(10, 50))
@parameter("deviations", default=2.0, bounds=(1.5, 3.0))
class BollingerMeanReversionStrategy(Strategy):
    """Bollinger Bands Mean Reversion Strategy."""

    def init(self):
        bb = self.I(bollinger_bands, self.data['close'], period=int(self.get_parameter("period")))
        self.lower = bb.lower
        self.upper = bb.upper
        self.middle = bb.middle

    def next(self):
        price = self.price()
        lower = self.lower.current
        upper = self.upper.current

        if price < lower and not self.has_position:
            self.buy(size=1.0)
        elif price > upper and self.has_position:
            self.sell(size=self.position_quantity)


# Additional mean reversion strategies
class ZScoreMeanReversionStrategy(Strategy):
    """Z-Score Mean Reversion Strategy."""
    pass

class DeviationMeanReversionStrategy(Strategy):
    """Deviation-based Mean Reversion Strategy."""
    pass

class WilliamsRReversionStrategy(Strategy):
    """Williams %R Reversion Strategy."""
    pass

class StochasticReversionStrategy(Strategy):
    """Stochastic Oscillator Reversion Strategy."""
    pass

class CCIReversionStrategy(Strategy):
    """CCI Mean Reversion Strategy."""
    pass

class UltimateOscillatorStrategy(Strategy):
    """Ultimate Oscillator Strategy."""
    pass

class KeltnerChannelStrategy(Strategy):
    """Keltner Channel Strategy."""
    pass

class DonchianChannelStrategy(Strategy):
    """Donchian Channel Strategy."""
    pass


__all__ = [
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
]

"""Statistical Arbitrage Strategy Packs.

This module contains statistical arbitrage strategies.
"""

from __future__ import annotations

from qantify.strategy.base import Strategy
from qantify.strategy.parameters import parameter

class PairsTradingStrategy(Strategy):
    """Classic Pairs Trading Strategy."""
    pass

class CointegrationStrategy(Strategy):
    """Cointegration-based Statistical Arbitrage."""
    pass

__all__ = [
    "PairsTradingStrategy",
    "CointegrationStrategy",
    "TriangularArbitrageStrategy",
    "CrossAssetArbitrageStrategy",
]

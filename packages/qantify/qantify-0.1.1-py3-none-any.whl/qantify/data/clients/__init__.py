"""Built-in exchange client implementations."""

from .binance import BinanceClient
from .binance_futures import BinanceFuturesClient, BinanceOptionsClient
from .dukascopy import DukascopyClient
from .polygon import PolygonClient
from .onchain import OnChainMetricsClient
from .sentiment import SentimentClient
from .footfall import FootfallClient

__all__ = [
    "BinanceClient",
    "BinanceFuturesClient",
    "BinanceOptionsClient",
    "DukascopyClient",
    "PolygonClient",
    "OnChainMetricsClient",
    "SentimentClient",
    "FootfallClient",
]

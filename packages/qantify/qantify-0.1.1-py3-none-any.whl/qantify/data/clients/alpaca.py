"""Advanced Alpaca data client with trading capabilities."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import aiohttp

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime
from qantify.live.adapters import RestExchangeAdapter, ExecutionReport

from ..base import BaseClient
from ..errors import DataClientError, DataNormalizationError


# Alpaca timeframe mappings
_ALPACA_TIMEFRAMES: Dict[str, TimeFrame] = {
    "1Min": TimeFrame("1m", "1T", 60),
    "5Min": TimeFrame("5m", "5T", 300),
    "15Min": TimeFrame("15m", "15T", 900),
    "1H": TimeFrame("1h", "1H", 3600),
    "1D": TimeFrame("1d", "1D", 86400),
}


class AlpacaClient(BaseClient):
    """Advanced asynchronous client for Alpaca API with trading capabilities."""

    name = "alpaca"
    rest_endpoint = "https://api.alpaca.markets"
    data_endpoint = "https://data.alpaca.markets"
    paper_endpoint = "https://paper-api.alpaca.markets"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        paper: bool = True,
        session: Optional[aiohttp.ClientSession] = None,
        **kwargs
    ):
        BaseClient.__init__(self, session=session, **kwargs)

        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.data_url = "https://data.alpaca.markets"
        self._account_cache: Optional[Dict[str, Any]] = None
        self._positions_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 30  # 30 seconds for Alpaca (more real-time)

    def resolve_endpoint(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def resolve_data_endpoint(self, path: str) -> str:
        return f"{self.data_url}{path}"

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _ALPACA_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported Alpaca timeframe '{value}'.") from exc

    # Authentication headers
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get Alpaca authentication headers."""
        return {
            'APCA-API-KEY-ID': self.api_key or '',
            'APCA-API-SECRET-KEY': self.api_secret or ''
        }

    # Account methods
    async def get_account(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get account information."""
        if use_cache and self._account_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._account_cache

        await self._ensure_session()
        url = self.resolve_endpoint("/v2/account")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            account = await response.json()

        self._account_cache = account
        self._cache_timestamp = datetime.utcnow()
        return account

    async def get_positions(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get current positions."""
        if use_cache and self._positions_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._positions_cache

        await self._ensure_session()
        url = self.resolve_endpoint("/v2/positions")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            positions = await response.json()

        self._positions_cache = positions
        self._cache_timestamp = datetime.utcnow()
        return positions

    async def get_portfolio_value(self) -> float:
        """Get current portfolio value."""
        account = await self.get_account()
        return float(account.get('portfolio_value', 0))

    async def get_buying_power(self) -> float:
        """Get available buying power."""
        account = await self.get_account()
        return float(account.get('buying_power', 0))

    # Trading methods
    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[int] = None,
        notional: Optional[float] = None,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        limit_price: Optional[float] = None,
        time_in_force: str = "day",
        extended_hours: bool = False,
        **kwargs
    ) -> ExecutionReport:
        """Submit an order to Alpaca."""
        await self._ensure_session()

        order_data = {
            'symbol': symbol.upper(),
            'side': side.lower(),
            'type': order_type.lower(),
            'time_in_force': time_in_force.lower(),
            'extended_hours': extended_hours,
            **kwargs
        }

        if quantity is not None:
            order_data['qty'] = quantity
        if notional is not None:
            order_data['notional'] = notional
        if price is not None and order_type.lower() == 'limit':
            order_data['limit_price'] = price
        if stop_price is not None:
            order_data['stop_price'] = stop_price
        if limit_price is not None and 'stop' in order_type.lower():
            order_data['limit_price'] = limit_price

        url = self.resolve_endpoint("/v2/orders")
        headers = self._get_auth_headers()

        async with await self._request_context("post", url, json=order_data, headers=headers) as response:
            if response.status not in [200, 201]:
                error_text = await response.text()
                raise DataClientError(f"Order submission failed: {error_text}")

            order_response = await response.json()

        return ExecutionReport(
            order_id=order_response['id'],
            status=order_response['status'],
            filled_qty=float(order_response.get('filled_qty', 0)),
            price=float(order_response.get('limit_price') or order_response.get('stop_price', 0)),
            raw=order_response
        )

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        await self._ensure_session()
        url = self.resolve_endpoint(f"/v2/orders/{order_id}")
        headers = self._get_auth_headers()

        async with await self._request_context("delete", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details."""
        await self._ensure_session()
        url = self.resolve_endpoint(f"/v2/orders/{order_id}")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_orders(self, status: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
        """Get orders."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/orders")

        params = {'limit': min(limit, 500)}
        if status:
            params['status'] = status

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_activities(self, activity_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get account activities."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/account/activities")

        params = {'limit': min(limit, 100)}
        if activity_type:
            params['activity_type'] = activity_type

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    # Market data methods
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get latest quote for a symbol."""
        await self._ensure_session()
        url = self.resolve_data_endpoint(f"/v2/stocks/{symbol.upper()}/quotes/latest")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('quote', {})

    async def get_last_trade(self, symbol: str) -> Dict[str, Any]:
        """Get latest trade for a symbol."""
        await self._ensure_session()
        url = self.resolve_data_endpoint(f"/v2/stocks/{symbol.upper()}/trades/latest")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('trade', {})

    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get historical bars."""
        await self._ensure_session()
        url = self.resolve_data_endpoint(f"/v2/stocks/{symbol.upper()}/bars")

        params = {
            'timeframe': timeframe,
            'limit': min(limit, 10000)
        }

        if start:
            params['start'] = start.isoformat()
        if end:
            params['end'] = end.isoformat()

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('bars', [])

    # Advanced trading methods
    async def place_market_order(self, symbol: str, side: str, quantity: int) -> ExecutionReport:
        """Place a market order."""
        return await self.submit_order(symbol, side, "market", quantity=quantity)

    async def place_limit_order(self, symbol: str, side: str, quantity: int, price: float) -> ExecutionReport:
        """Place a limit order."""
        return await self.submit_order(symbol, side, "limit", quantity=quantity, price=price)

    async def place_stop_order(self, symbol: str, side: str, quantity: int, stop_price: float) -> ExecutionReport:
        """Place a stop order."""
        return await self.submit_order(symbol, side, "stop", quantity=quantity, stop_price=stop_price)

    async def place_stop_limit_order(self, symbol: str, side: str, quantity: int,
                                   stop_price: float, limit_price: float) -> ExecutionReport:
        """Place a stop-limit order."""
        return await self.submit_order(symbol, side, "stop_limit", quantity=quantity,
                                     stop_price=stop_price, limit_price=limit_price)

    async def place_bracket_order(self, symbol: str, side: str, quantity: int,
                                take_profit_price: float, stop_loss_price: float) -> List[ExecutionReport]:
        """Place a bracket order (main order + take profit + stop loss)."""
        # Alpaca doesn't have native bracket orders, so we place separate orders
        main_order = await self.place_market_order(symbol, side, quantity)

        # Take profit order
        tp_side = "sell" if side == "buy" else "buy"
        tp_order = await self.place_limit_order(symbol, tp_side, quantity, take_profit_price)

        # Stop loss order
        sl_order = await self.place_stop_order(symbol, tp_side, quantity, stop_loss_price)

        return [main_order, tp_order, sl_order]

    async def place_trailing_stop_order(self, symbol: str, side: str, quantity: int,
                                      trail_percent: Optional[float] = None,
                                      trail_amount: Optional[float] = None) -> ExecutionReport:
        """Place a trailing stop order."""
        order_data = {
            'trail_percent': trail_percent,
            'trail_price': trail_amount
        }

        return await self.submit_order(symbol, side, "trailing_stop", quantity=quantity, **order_data)

    # Portfolio and risk management
    async def get_portfolio_history(self, period: str = "1M", timeframe: str = "1D") -> Dict[str, Any]:
        """Get portfolio history."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/account/portfolio/history")

        params = {
            'period': period,
            'timeframe': timeframe
        }

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_watchlist(self, watchlist_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get watchlists."""
        await self._ensure_session()

        if watchlist_id:
            url = self.resolve_endpoint(f"/v2/watchlists/{watchlist_id}")
        else:
            url = self.resolve_endpoint("/v2/watchlists")

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    # Market data - historical candles
    async def fetch_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        await self._ensure_session()

        # Convert timeframe to Alpaca format
        alpaca_timeframe = self._timeframe_to_alpaca(timeframe)

        bars = await self.get_bars(
            symbol.value,
            timeframe=alpaca_timeframe,
            start=start,
            end=end,
            limit=limit or 1000
        )

        # Normalize to standard format
        for bar in bars:
            yield {
                "timestamp": ensure_datetime(bar['t']),
                "open": float(bar['o']),
                "high": float(bar['h']),
                "low": float(bar['l']),
                "close": float(bar['c']),
                "volume": float(bar['v']),
            }

    def _timeframe_to_alpaca(self, timeframe: TimeFrame) -> str:
        """Convert TimeFrame to Alpaca format."""
        # Alpaca uses different format
        name = timeframe.name
        if name == "1m":
            return "1Min"
        elif name == "5m":
            return "5Min"
        elif name == "15m":
            return "15Min"
        elif name == "1h":
            return "1H"
        elif name == "1d":
            return "1D"
        else:
            return "1D"  # Default

    def _normalize_batch(
        self,
        payload: List[dict[str, Any]],
        symbol: Symbol,
        timeframe: TimeFrame,
    ) -> List[dict[str, Any]]:
        """Normalize Alpaca bars to standard format."""
        normalized = []
        for bar in payload:
            normalized.append({
                "timestamp": ensure_datetime(bar['t']),
                "open": float(bar['o']),
                "high": float(bar['h']),
                "low": float(bar['l']),
                "close": float(bar['c']),
                "volume": float(bar['v']),
            })
        return normalized

    # Asset information
    async def get_assets(self, status: str = "active", asset_class: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available assets."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/assets")

        params = {'status': status}
        if asset_class:
            params['asset_class'] = asset_class

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_asset(self, symbol: str) -> Dict[str, Any]:
        """Get asset information."""
        await self._ensure_session()
        url = self.resolve_endpoint(f"/v2/assets/{symbol.upper()}")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    # Calendar and market hours
    async def get_calendar(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get market calendar."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/calendar")

        params = {}
        if start:
            params['start'] = start.date().isoformat()
        if end:
            params['end'] = end.date().isoformat()

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_clock(self) -> Dict[str, Any]:
        """Get market clock."""
        await self._ensure_session()
        url = self.resolve_endpoint("/v2/clock")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    # News and fundamentals
    async def get_news(self, symbols: Optional[List[str]] = None, start: Optional[datetime] = None,
                      end: Optional[datetime] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get news articles."""
        await self._ensure_session()
        url = self.resolve_data_endpoint("/v1beta1/news")

        params = {'limit': min(limit, 50)}
        if symbols:
            params['symbols'] = ','.join(symbols)
        if start:
            params['start'] = start.isoformat()
        if end:
            params['end'] = end.isoformat()

        headers = self._get_auth_headers()

        async with await self._request_context("get", url, params=params, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('news', [])

    # Utility methods
    async def get_market_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market snapshot for multiple symbols."""
        await self._ensure_session()
        url = self.resolve_data_endpoint(f"/v2/stocks/snapshots?symbols={','.join(symbols)}")
        headers = self._get_auth_headers()

        async with await self._request_context("get", url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def validate_order(self, symbol: str, quantity: int, side: str, order_type: str) -> bool:
        """Validate order parameters."""
        try:
            # Get asset info
            asset = await self.get_asset(symbol)

            # Check if tradable
            if not asset.get('tradable', False):
                return False

            # Check market hours for live orders
            if not self.paper:
                clock = await self.get_clock()
                if not clock.get('is_open', False):
                    return False

            # Basic quantity validation
            if quantity <= 0:
                return False

            return True

        except Exception:
            return False

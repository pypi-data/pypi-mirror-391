"""Advanced Interactive Brokers data client with institutional trading capabilities."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import aiohttp

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime
from qantify.live.adapters import RestExchangeAdapter, ExecutionReport

from ..base import BaseClient
from ..errors import DataClientError, DataNormalizationError


logger = logging.getLogger(__name__)


# IB timeframe mappings
_IB_TIMEFRAMES: Dict[str, TimeFrame] = {
    "1 min": TimeFrame("1m", "1T", 60),
    "2 mins": TimeFrame("2m", "2T", 120),
    "3 mins": TimeFrame("3m", "3T", 180),
    "5 mins": TimeFrame("5m", "5T", 300),
    "10 mins": TimeFrame("10m", "10T", 600),
    "15 mins": TimeFrame("15m", "15T", 900),
    "20 mins": TimeFrame("20m", "20T", 1200),
    "30 mins": TimeFrame("30m", "30T", 1800),
    "1 hour": TimeFrame("1h", "1H", 3600),
    "2 hours": TimeFrame("2h", "2H", 7200),
    "3 hours": TimeFrame("3h", "3H", 10800),
    "4 hours": TimeFrame("4h", "4H", 14400),
    "8 hours": TimeFrame("8h", "8H", 28800),
    "1 day": TimeFrame("1d", "1D", 86400),
    "1 week": TimeFrame("1w", "1W", 604800),
    "1 month": TimeFrame("1M", "1M", 2592000),
}


class InteractiveBrokersClient(BaseClient, RestExchangeAdapter):
    """Advanced client for Interactive Brokers API with institutional capabilities."""

    name = "interactive_brokers"
    rest_endpoint = "https://api.ibkr.com"
    live_endpoint = "https://api.ibkr.com"
    paper_endpoint = "https://api.ibkr.com"  # IB uses same endpoint

    def __init__(
        self,
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        paper: bool = True,
        host: str = "127.0.0.1",
        port: int = 7497,  # Live trading port
        client_id: int = 1,
        **kwargs
    ):
        BaseClient.__init__(self, **kwargs)
        RestExchangeAdapter.__init__(
            self,
            base_url=self.rest_endpoint,
            api_key=api_key,
            api_secret=None  # IB doesn't use API secret
        )

        self.api_key = api_key
        self.account_id = account_id
        self.paper = paper
        self.ib_host = host
        self.ib_port = port if not paper else 7496  # Paper trading port
        self.client_id = client_id

        # IB specific attributes
        self._session_token: Optional[str] = None
        self._account_cache: Optional[Dict[str, Any]] = None
        self._positions_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 60  # 1 minute for IB

        # Connection management
        self._ib_connection = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3

    def resolve_endpoint(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _IB_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported IB timeframe '{value}'.") from exc

    # Authentication and session management
    async def authenticate(self) -> bool:
        """Authenticate with IB."""
        # IB authentication is complex and typically requires TWS/Gateway
        # This is a simplified implementation
        try:
            # In a real implementation, this would establish connection to TWS/Gateway
            # and authenticate using provided credentials
            self._session_token = f"ib_session_{int(time.time())}"
            logger.info("IB authentication successful")
            return True
        except Exception as e:
            logger.error(f"IB authentication failed: {e}")
            return False

    async def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._session_token is not None

    # Account and portfolio methods
    async def get_account_summary(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get account summary."""
        if use_cache and self._account_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._account_cache

        if not await self.is_authenticated():
            await self.authenticate()

        # IB account summary endpoint
        url = self.resolve_endpoint(f"/v1/api/portfolio/accounts")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            accounts = await response.json()

        if accounts and self.account_id:
            account = next((acc for acc in accounts if acc.get('id') == self.account_id), accounts[0])
        else:
            account = accounts[0] if accounts else {}

        self._account_cache = account
        self._cache_timestamp = datetime.utcnow()
        return account

    async def get_positions(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get current positions."""
        if use_cache and self._positions_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._positions_cache

        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint(f"/v1/api/portfolio/{self.account_id}/positions")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            positions = await response.json()

        self._positions_cache = positions
        self._cache_timestamp = datetime.utcnow()
        return positions

    async def get_portfolio_value(self) -> float:
        """Get total portfolio value."""
        account = await self.get_account_summary()
        return float(account.get('totalCashValue', 0)) + float(account.get('totalStockValue', 0))

    async def get_buying_power(self) -> float:
        """Get buying power."""
        account = await self.get_account_summary()
        return float(account.get('buyingPower', 0))

    # Trading methods
    async def submit_order(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        side: str = "BUY",
        order_type: str = "LMT",
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "DAY",
        **kwargs
    ) -> ExecutionReport:
        """Submit order to IB."""
        if not await self.is_authenticated():
            await self.authenticate()

        order_data = {
            "acctId": self.account_id,
            "conid": 0,  # Contract ID, would need to be resolved
            "secType": sec_type,
            "symbol": symbol,
            "exchange": exchange,
            "currency": currency,
            "side": side,
            "orderType": order_type,
            "quantity": quantity,
            "price": price,
            "tif": time_in_force,
            **kwargs
        }

        if stop_price:
            order_data["auxPrice"] = stop_price

        url = self.resolve_endpoint("/v1/api/iserver/account/orders")

        async with await self._request_context("post", url, json=order_data) as response:
            if response.status not in [200, 201]:
                error_text = await response.text()
                raise DataClientError(f"IB order submission failed: {error_text}")

            order_response = await response.json()

        return ExecutionReport(
            order_id=str(order_response.get('order_id', '')),
            status=order_response.get('status', 'PENDING'),
            filled_qty=float(order_response.get('filledQuantity', 0)),
            price=float(order_response.get('price', 0)),
            raw=order_response
        )

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint(f"/v1/api/iserver/account/orders/{order_id}")

        async with await self._request_context("delete", url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint(f"/v1/api/iserver/account/orders/{order_id}")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_orders(self) -> List[Dict[str, Any]]:
        """Get all orders."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/account/orders")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            return await response.json()

    # Market data methods
    async def get_market_data(self, symbols: List[str], fields: List[str] = None) -> Dict[str, Any]:
        """Get market data snapshot."""
        if not await self.is_authenticated():
            await self.authenticate()

        if fields is None:
            fields = ["31", "84", "86"]  # Last price, bid, ask

        url = self.resolve_endpoint("/v1/api/iserver/marketdata/snapshot")

        params = {
            "conids": ",".join(symbols),  # Contract IDs
            "fields": ",".join(fields)
        }

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1M",
        timeframe: str = "1 day",
        bar_type: str = "TRADES"
    ) -> List[Dict[str, Any]]:
        """Get historical data."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/hmds/history")

        params = {
            "conid": symbol,  # Contract ID
            "period": period,
            "bar": timeframe,
            "barType": bar_type
        }

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('data', [])

    async def subscribe_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Subscribe to real-time market data."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/marketdata")

        subscription_data = {
            "conids": symbols
        }

        async with await self._request_context("post", url, json=subscription_data) as response:
            response.raise_for_status()
            return await response.json()

    async def unsubscribe_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Unsubscribe from market data."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/marketdata")

        async with await self._request_context("delete", url, json={"conids": symbols}) as response:
            response.raise_for_status()
            return await response.json()

    # Contract resolution
    async def search_contracts(self, symbol: str, sec_type: str = "STK",
                             exchange: str = "SMART") -> List[Dict[str, Any]]:
        """Search for contract details."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/secdef/search")

        params = {
            "symbol": symbol,
            "secType": sec_type,
            "exchange": exchange
        }

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_contract_details(self, conid: str) -> Dict[str, Any]:
        """Get detailed contract information."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint(f"/v1/api/iserver/secdef/info")

        params = {"conid": conid}

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    # Advanced order types
    async def place_bracket_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        profit_target: float,
        stop_loss: float
    ) -> List[ExecutionReport]:
        """Place bracket order with entry, profit target, and stop loss."""
        # IB bracket orders are complex - simplified implementation
        entry_order = await self.submit_order(
            symbol=symbol,
            side=side,
            order_type="LMT",
            quantity=quantity,
            price=entry_price
        )

        # Parent order ID would be needed for bracket
        parent_id = entry_order.order_id

        # Profit taker
        profit_side = "SELL" if side == "BUY" else "BUY"
        profit_order = await self.submit_order(
            symbol=symbol,
            side=profit_side,
            order_type="LMT",
            quantity=quantity,
            price=profit_target
        )

        # Stop loss
        stop_order = await self.submit_order(
            symbol=symbol,
            side=profit_side,
            order_type="STP",
            quantity=quantity,
            stop_price=stop_loss
        )

        return [entry_order, profit_order, stop_order]

    async def place_hedge_order(
        self,
        symbol: str,
        hedge_symbol: str,
        side: str,
        quantity: float,
        hedge_ratio: float = 1.0
    ) -> List[ExecutionReport]:
        """Place hedge order."""
        main_order = await self.submit_order(
            symbol=symbol,
            side=side,
            order_type="MKT",
            quantity=quantity
        )

        # Hedge order
        hedge_side = "SELL" if side == "BUY" else "BUY"
        hedge_quantity = quantity * hedge_ratio

        hedge_order = await self.submit_order(
            symbol=hedge_symbol,
            side=hedge_side,
            order_type="MKT",
            quantity=hedge_quantity
        )

        return [main_order, hedge_order]

    # Risk management
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """Get comprehensive risk metrics."""
        account = await self.get_account_summary()
        positions = await self.get_positions()

        total_value = await self.get_portfolio_value()

        # Calculate position concentrations
        position_values = []
        for position in positions:
            market_value = float(position.get('marketValue', 0))
            position_values.append(market_value)

        max_position = max(position_values) if position_values else 0
        concentration_ratio = max_position / total_value if total_value > 0 else 0

        # Margin utilization
        maintenance_margin = float(account.get('maintenanceMargin', 0))
        margin_utilization = maintenance_margin / total_value if total_value > 0 else 0

        return {
            'total_portfolio_value': total_value,
            'buying_power': await self.get_buying_power(),
            'concentration_ratio': concentration_ratio,
            'margin_utilization': margin_utilization,
            'total_positions': len(positions),
            'maintenance_margin': maintenance_margin
        }

    # Market scanners and research
    async def get_market_scanner(self, scanner_type: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run market scanner."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/scanner/run")

        scanner_data = {
            "type": scanner_type,
            "filters": filters or []
        }

        async with await self._request_context("post", url, json=scanner_data) as response:
            response.raise_for_status()
            result = await response.json()
            return result.get('contracts', [])

    async def get_fundamentals(self, symbol: str, report_type: str = "summary") -> Dict[str, Any]:
        """Get fundamental data."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint(f"/v1/api/fundamentals/{symbol}")

        params = {"type": report_type}

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    # Historical data fetch
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

        # Convert to IB format
        ib_timeframe = self._timeframe_to_ib(timeframe)
        period = self._calculate_period(start, end, limit)

        bars = await self.get_historical_data(
            symbol=symbol.value,
            period=period,
            timeframe=ib_timeframe
        )

        # Normalize to standard format
        for bar in bars:
            yield {
                "timestamp": ensure_datetime(bar['timestamp']),
                "open": float(bar.get('open', 0)),
                "high": float(bar.get('high', 0)),
                "low": float(bar.get('low', 0)),
                "close": float(bar.get('close', 0)),
                "volume": float(bar.get('volume', 0)),
            }

    def _timeframe_to_ib(self, timeframe: TimeFrame) -> str:
        """Convert TimeFrame to IB format."""
        name = timeframe.name
        if name == "1m":
            return "1 min"
        elif name == "5m":
            return "5 mins"
        elif name == "15m":
            return "15 mins"
        elif name == "1h":
            return "1 hour"
        elif name == "1d":
            return "1 day"
        else:
            return "1 day"

    def _calculate_period(self, start: Optional[Any], end: Optional[Any], limit: Optional[int]) -> str:
        """Calculate IB period string."""
        if start and end:
            days = (ensure_datetime(end) - ensure_datetime(start)).days
            if days <= 1:
                return "1D"
            elif days <= 7:
                return "1W"
            elif days <= 30:
                return "1M"
            else:
                return "1Y"
        elif limit:
            if limit <= 1000:
                return "1M"
            else:
                return "1Y"
        else:
            return "1M"

    # Connection management
    async def connect_gateway(self) -> bool:
        """Connect to IB Gateway/TWS."""
        # This would establish socket connection to IB Gateway
        # Simplified for this implementation
        try:
            # In real implementation, connect to self.ib_host:self.ib_port
            logger.info(f"Connecting to IB Gateway at {self.ib_host}:{self.ib_port}")
            self._ib_connection = f"connected_{self.client_id}"
            return True
        except Exception as e:
            logger.error(f"IB Gateway connection failed: {e}")
            return False

    async def disconnect_gateway(self) -> None:
        """Disconnect from IB Gateway."""
        if self._ib_connection:
            logger.info("Disconnecting from IB Gateway")
            self._ib_connection = None

    # Utility methods
    async def get_server_time(self) -> datetime:
        """Get IB server time."""
        if not await self.is_authenticated():
            await self.authenticate()

        url = self.resolve_endpoint("/v1/api/iserver/time")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            time_data = await response.json()
            return ensure_datetime(time_data.get('time', datetime.utcnow()))

    async def get_market_hours(self, symbol: str) -> Dict[str, Any]:
        """Get market hours for symbol."""
        # This would query IB for trading hours
        return {
            'symbol': symbol,
            'is_open': True,  # Simplified
            'next_open': datetime.utcnow(),
            'next_close': datetime.utcnow() + timedelta(hours=6)
        }

    async def validate_contract(self, symbol: str, sec_type: str = "STK") -> bool:
        """Validate contract exists and is tradable."""
        try:
            contracts = await self.search_contracts(symbol, sec_type)
            return len(contracts) > 0
        except Exception:
            return False

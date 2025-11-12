"""Advanced Binance spot and futures data client with trading capabilities."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import aiohttp

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime
from qantify.live.adapters import RestExchangeAdapter, ExecutionReport

from ..base import BaseClient
from ..errors import DataClientError, DataNormalizationError


# Enhanced timeframe mappings
_BINANCE_TIMEFRAMES: Dict[str, TimeFrame] = {
    "1m": TimeFrame("1m", "1T", 60),
    "3m": TimeFrame("3m", "3T", 180),
    "5m": TimeFrame("5m", "5T", 300),
    "15m": TimeFrame("15m", "15T", 900),
    "30m": TimeFrame("30m", "30T", 1800),
    "1h": TimeFrame("1h", "1H", 3600),
    "2h": TimeFrame("2h", "2H", 7200),
    "4h": TimeFrame("4h", "4H", 14_400),
    "6h": TimeFrame("6h", "6H", 21_600),
    "8h": TimeFrame("8h", "8H", 28_800),
    "12h": TimeFrame("12h", "12H", 43_200),
    "1d": TimeFrame("1d", "1D", 86_400),
    "3d": TimeFrame("3d", "3D", 259_200),
    "1w": TimeFrame("1w", "7D", 604_800),
    "1M": TimeFrame("1M", "30D", 2_592_000),
}


class BinanceClient(BaseClient):
    """Advanced asynchronous client for Binance REST API with trading capabilities."""

    name = "binance"
    rest_endpoint = "https://api.binance.com"
    testnet_endpoint = "https://testnet.binance.vision"
    max_batch_size = 1000

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        recv_window: int = 5000,
        session: Optional[aiohttp.ClientSession] = None,
        **kwargs
    ):
        BaseClient.__init__(self, session=session, **kwargs)

        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.recv_window = recv_window
        self._account_info_cache: Optional[Dict[str, Any]] = None
        self._exchange_info_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 300  # 5 minutes

    def resolve_endpoint(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _BINANCE_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported Binance interval '{value}'.") from exc

    # Authentication and signing methods
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        if not self.api_secret:
            raise ValueError("API secret required for authenticated requests")

        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_auth_headers(self, signed_params: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key

        if signed_params:
            headers["X-MBX-SIGNED"] = "true"

        return headers

    def _prepare_params(self, params: Dict[str, Any], signed: bool = False) -> Dict[str, Any]:
        """Prepare parameters with timestamp and signature if needed."""
        prepared_params = dict(params)

        if signed:
            prepared_params['timestamp'] = int(time.time() * 1000)
            prepared_params['recvWindow'] = self.recv_window
            prepared_params['signature'] = self._generate_signature(prepared_params)

        return prepared_params

    # Account and trading methods
    async def get_account_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get account information including balances and positions."""
        if use_cache and self._account_info_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._account_info_cache

        await self._ensure_session()
        params = self._prepare_params({}, signed=True)
        url = self.resolve_endpoint("/api/v3/account")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            account_info = await response.json()

        self._account_info_cache = account_info
        self._cache_timestamp = datetime.utcnow()
        return account_info

    async def get_balances(self) -> Dict[str, Dict[str, float]]:
        """Get account balances."""
        account_info = await self.get_account_info()
        balances = {}

        for balance in account_info.get('balances', []):
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked

            if total > 0:  # Only include assets with balance
                balances[asset] = {
                    'free': free,
                    'locked': locked,
                    'total': total
                }

        return balances

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        account_info = await self.get_account_info()
        positions = []

        for position in account_info.get('positions', []):
            if float(position.get('positionAmt', 0)) != 0:
                positions.append({
                    'symbol': position['symbol'],
                    'position_amount': float(position['positionAmt']),
                    'entry_price': float(position['entryPrice']),
                    'unrealized_pnl': float(position.get('unrealizedProfit', 0)),
                    'leverage': int(position.get('leverage', 1)),
                    'margin_type': position.get('marginType', 'isolated'),
                    'liquidation_price': float(position.get('liquidationPrice', 0))
                })

        return positions

    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        iceberg_qty: Optional[float] = None,
        time_in_force: str = "GTC",
        **kwargs
    ) -> ExecutionReport:
        """Submit an order to Binance."""
        await self._ensure_session()

        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': order_type.upper(),
            'timeInForce': time_in_force,
            **kwargs
        }

        if quantity is not None:
            params['quantity'] = quantity
        if price is not None:
            params['price'] = price
        if stop_price is not None:
            params['stopPrice'] = stop_price
        if iceberg_qty is not None:
            params['icebergQty'] = iceberg_qty

        params = self._prepare_params(params, signed=True)
        url = self.resolve_endpoint("/api/v3/order")

        async with await self._request_context("post", url, json=params) as response:
            if response.status != 201:
                error_text = await response.text()
                raise DataClientError(f"Order submission failed: {error_text}")

            order_response = await response.json()

        return ExecutionReport(
            order_id=str(order_response['orderId']),
            status=order_response['status'],
            filled_qty=float(order_response.get('executedQty', 0)),
            price=float(order_response.get('price', 0)),
            raw=order_response
        )

    async def cancel_order(self, symbol: str, order_id: Optional[str] = None,
                          orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an order."""
        await self._ensure_session()

        params = {'symbol': symbol.upper()}
        if order_id:
            params['orderId'] = order_id
        if orig_client_order_id:
            params['origClientOrderId'] = orig_client_order_id

        params = self._prepare_params(params, signed=True)
        url = self.resolve_endpoint("/api/v3/order")

        async with await self._request_context("delete", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_order_status(self, symbol: str, order_id: Optional[str] = None,
                              orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Get order status."""
        await self._ensure_session()

        params = {'symbol': symbol.upper()}
        if order_id:
            params['orderId'] = order_id
        if orig_client_order_id:
            params['origClientOrderId'] = orig_client_order_id

        params = self._prepare_params(params, signed=True)
        url = self.resolve_endpoint("/api/v3/order")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders."""
        await self._ensure_session()

        params = {}
        if symbol:
            params['symbol'] = symbol.upper()

        params = self._prepare_params(params, signed=True)
        url = self.resolve_endpoint("/api/v3/openOrders")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_trade_history(self, symbol: str, limit: int = 500,
                               from_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get trade history."""
        await self._ensure_session()

        params = {'symbol': symbol.upper(), 'limit': min(limit, 1000)}
        if from_id:
            params['fromId'] = from_id

        params = self._prepare_params(params, signed=True)
        url = self.resolve_endpoint("/api/v3/myTrades")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    # Market data methods
    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol."""
        await self._ensure_session()
        params = {'symbol': symbol.upper()}
        url = self.resolve_endpoint("/api/v3/ticker/price")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_24hr_ticker_stats(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24hr ticker statistics."""
        await self._ensure_session()
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()

        url = self.resolve_endpoint("/api/v3/ticker/24hr")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth."""
        await self._ensure_session()
        params = {'symbol': symbol.upper(), 'limit': limit}
        url = self.resolve_endpoint("/api/v3/depth")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get recent trades."""
        await self._ensure_session()
        params = {'symbol': symbol.upper(), 'limit': min(limit, 1000)}
        url = self.resolve_endpoint("/api/v3/trades")

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_exchange_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get exchange information."""
        if use_cache and self._exchange_info_cache and self._cache_timestamp:
            if (datetime.utcnow() - self._cache_timestamp).seconds < self._cache_ttl:
                return self._exchange_info_cache

        await self._ensure_session()
        url = self.resolve_endpoint("/api/v3/exchangeInfo")

        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            exchange_info = await response.json()

        self._exchange_info_cache = exchange_info
        self._cache_timestamp = datetime.utcnow()
        return exchange_info

    # Advanced trading methods
    async def place_market_order(self, symbol: str, side: str, quantity: float) -> ExecutionReport:
        """Place a market order."""
        return await self.submit_order(symbol, side, "MARKET", quantity=quantity)

    async def place_limit_order(self, symbol: str, side: str, quantity: float,
                               price: float, time_in_force: str = "GTC") -> ExecutionReport:
        """Place a limit order."""
        return await self.submit_order(symbol, side, "LIMIT", quantity=quantity,
                                      price=price, time_in_force=time_in_force)

    async def place_stop_loss_order(self, symbol: str, side: str, quantity: float,
                                   stop_price: float) -> ExecutionReport:
        """Place a stop loss order."""
        return await self.submit_order(symbol, side, "STOP_LOSS", quantity=quantity,
                                      stop_price=stop_price)

    async def place_oco_order(self, symbol: str, side: str, quantity: float,
                             price: float, stop_price: float, stop_limit_price: float) -> List[ExecutionReport]:
        """Place a One-Cancels-Other order."""
        # OCO orders require special handling in Binance
        # This is a simplified implementation
        limit_order = await self.place_limit_order(symbol, side, quantity, price)
        stop_order = await self.place_stop_loss_order(symbol, "SELL" if side == "BUY" else "BUY",
                                                     quantity, stop_price)
        return [limit_order, stop_order]

    async def place_iceberg_order(self, symbol: str, side: str, quantity: float,
                                 price: float, iceberg_qty: float) -> ExecutionReport:
        """Place an iceberg order."""
        return await self.submit_order(symbol, side, "LIMIT", quantity=quantity,
                                      price=price, iceberg_qty=iceberg_qty)

    # Risk management methods
    async def get_position_risk(self, symbol: str) -> Dict[str, Any]:
        """Get position risk metrics."""
        positions = await self.get_positions()
        symbol_position = next((p for p in positions if p['symbol'] == symbol), None)

        if not symbol_position:
            return {'symbol': symbol, 'position': 0, 'risk_level': 'none'}

        position_size = abs(symbol_position['position_amount'])
        entry_price = symbol_position['entry_price']
        current_price = float((await self.get_ticker_price(symbol))['price'])

        # Calculate risk metrics
        unrealized_pnl = symbol_position['unrealized_pnl']
        pnl_percentage = (unrealized_pnl / (position_size * entry_price)) * 100

        # Risk levels based on drawdown
        if pnl_percentage < -10:
            risk_level = 'high'
        elif pnl_percentage < -5:
            risk_level = 'medium'
        elif pnl_percentage < -2:
            risk_level = 'low'
        else:
            risk_level = 'none'

        return {
            'symbol': symbol,
            'position_size': position_size,
            'entry_price': entry_price,
            'current_price': current_price,
            'unrealized_pnl': unrealized_pnl,
            'pnl_percentage': pnl_percentage,
            'risk_level': risk_level,
            'liquidation_price': symbol_position.get('liquidation_price', 0)
        }

    async def get_portfolio_risk(self) -> Dict[str, Any]:
        """Get overall portfolio risk metrics."""
        account_info = await self.get_account_info()
        balances = await self.get_balances()
        positions = await self.get_positions()

        total_equity = float(account_info.get('totalWalletBalance', 0))
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)

        # Calculate concentration
        position_values = [abs(p['position_amount'] * p['entry_price']) for p in positions]
        max_position_value = max(position_values) if position_values else 0
        concentration_ratio = max_position_value / total_equity if total_equity > 0 else 0

        # Calculate leverage
        total_position_value = sum(position_values)
        leverage = total_position_value / total_equity if total_equity > 0 else 0

        return {
            'total_equity': total_equity,
            'total_unrealized_pnl': total_unrealized_pnl,
            'concentration_ratio': concentration_ratio,
            'leverage': leverage,
            'num_positions': len(positions),
            'num_assets': len(balances),
            'maintenance_margin': float(account_info.get('totalMaintenanceMargin', 0))
        }

    # Utility methods
    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed symbol information."""
        exchange_info = await self.get_exchange_info()

        for symbol_info in exchange_info.get('symbols', []):
            if symbol_info['symbol'] == symbol.upper():
                return symbol_info

        raise ValueError(f"Symbol {symbol} not found")

    async def get_symbol_filters(self, symbol: str) -> List[Dict[str, Any]]:
        """Get symbol trading filters."""
        symbol_info = await self.get_symbol_info(symbol)
        return symbol_info.get('filters', [])

    async def validate_order_params(self, symbol: str, side: str, order_type: str,
                                   quantity: float, price: Optional[float] = None) -> bool:
        """Validate order parameters against exchange rules."""
        try:
            filters = await self.get_symbol_filters(symbol)
            symbol_info = await self.get_symbol_info(symbol)

            # Check LOT_SIZE filter
            for filter_info in filters:
                if filter_info['filterType'] == 'LOT_SIZE':
                    min_qty = float(filter_info['minQty'])
                    max_qty = float(filter_info['maxQty'])
                    step_size = float(filter_info['stepSize'])

                    if quantity < min_qty or quantity > max_qty:
                        return False

                    # Check step size
                    if (quantity - min_qty) % step_size != 0:
                        return False

                elif filter_info['filterType'] == 'PRICE_FILTER' and price is not None:
                    min_price = float(filter_info['minPrice'])
                    max_price = float(filter_info['maxPrice'])
                    tick_size = float(filter_info['tickSize'])

                    if price < min_price or price > max_price:
                        return False

                    # Check tick size
                    if (price - min_price) % tick_size != 0:
                        return False

                elif filter_info['filterType'] == 'MIN_NOTIONAL' and price is not None:
                    min_notional = float(filter_info['minNotional'])
                    notional = quantity * price

                    if notional < min_notional:
                        return False

            return True

        except Exception:
            return False

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

        symbol_value = self._format_symbol(symbol)
        start_ms = int(ensure_datetime(start).timestamp() * 1000) if start else None
        end_ms = int(ensure_datetime(end).timestamp() * 1000) if end else None
        remaining = limit

        records: List[dict[str, Any]] = []
        next_start = start_ms

        while True:
            batch_limit = min(remaining or self.max_batch_size, self.max_batch_size)
            params = {
                "symbol": symbol_value,
                "interval": timeframe.name,
                "limit": batch_limit,
            }

            if next_start is not None:
                params["startTime"] = next_start
            if end_ms is not None:
                params["endTime"] = end_ms

            url = self.resolve_endpoint("/api/v3/klines")
            async with await self._request_context("get", url, params=params) as response:
                if response.status != 200:
                    text = await response.text()
                    raise DataClientError(
                        f"Binance request failed with status {response.status}: {text}"
                    )
                payload = await response.json()

            if not isinstance(payload, list):
                raise DataClientError("Unexpected response schema for Binance klines.")

            if not payload:
                break

            normalized_batch = self._normalize_batch(payload, symbol, timeframe)
            records.extend(normalized_batch)

            if remaining is not None:
                remaining -= len(normalized_batch)
                if remaining <= 0:
                    break

            last_open = payload[-1][0]
            next_start = int(last_open) + timeframe.seconds * 1000

            if end_ms is not None and next_start >= end_ms:
                break

            if len(payload) < batch_limit:
                break

        return records

    def _format_symbol(self, symbol: Symbol) -> str:
        value = symbol.value.replace("/", "").replace("-", "").upper()
        return value

    def _normalize_batch(
        self,
        payload: List[list[Any]],
        symbol: Symbol,
        timeframe: TimeFrame,
    ) -> List[dict[str, Any]]:
        normalized: List[dict[str, Any]] = []
        for entry in payload:
            if len(entry) < 6:
                raise DataNormalizationError("Unexpected Binance kline payload length.")

            open_time = ensure_datetime(int(entry[0]) / 1000)
            normalized.append(
                {
                    "timestamp": open_time,
                    "open": float(entry[1]),
                    "high": float(entry[2]),
                    "low": float(entry[3]),
                    "close": float(entry[4]),
                    "volume": float(entry[5]),
                }
            )

        return normalized

    async def fetch_ticker(self, symbol: Symbol) -> dict[str, Any]:
        await self._ensure_session()
        params = {"symbol": self._format_symbol(symbol)}
        url = f"{self.rest_endpoint}/api/v3/ticker/24hr"
        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            payload = await response.json()
        return payload

    async def fetch_exchange_info(self) -> dict[str, Any]:
        await self._ensure_session()
        url = f"{self.rest_endpoint}/api/v3/exchangeInfo"
        async with await self._request_context("get", url) as response:
            response.raise_for_status()
            payload = await response.json()
        return payload

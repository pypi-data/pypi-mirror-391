"""Live trading exchange adapters."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

import aiohttp


@dataclass(slots=True)
class ExecutionReport:
    order_id: str
    status: str
    filled_qty: float
    price: float
    raw: Dict[str, Any]


class RestExchangeAdapter:
    base_url: str

    def __init__(self, base_url: str, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "RestExchangeAdapter":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        assert self.session is not None
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.get(url, params=params, headers=self._headers()) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        assert self.session is not None
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.post(url, json=payload, headers=self._headers()) as response:
            response.raise_for_status()
            return await response.json()

    async def submit_order(self, payload: Dict[str, Any]) -> ExecutionReport:
        response = await self.post("/orders", payload)
        return ExecutionReport(
            order_id=response.get("id", ""),
            status=response.get("status", ""),
            filled_qty=float(response.get("filled", 0.0)),
            price=float(response.get("price", 0.0)),
            raw=response,
        )

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        path = f"/orders/{order_id}"
        assert self.session is not None
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.delete(url, headers=self._headers()) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_order(self, order_id: str) -> Dict[str, Any]:
        path = f"/orders/{order_id}"
        return await self.get(path)

    async def list_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {"symbol": symbol} if symbol else None
        return await self.get("/orders/open", params=params)

    def _headers(self) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers


class WebsocketExchangeAdapter:
    def __init__(self, url: str, *, reconnect: bool = True, heartbeat_interval: int = 20) -> None:
        self.url = url
        self.reconnect = reconnect
        self.heartbeat_interval = heartbeat_interval
        self.session: Optional[aiohttp.ClientSession] = None
        self.connection: Optional[aiohttp.ClientWebSocketResponse] = None
        self._subscriptions: list[Dict[str, Any]] = []
        self._listen_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def __aenter__(self) -> "WebsocketExchangeAdapter":
        self.session = aiohttp.ClientSession()
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._listen_task:
            self._listen_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.connection:
            await self.connection.close()
            self.connection = None
        if self.session:
            await self.session.close()
            self.session = None

    async def subscribe(self, payload: Dict[str, Any]) -> None:
        self._subscriptions.append(payload)
        if self.connection is not None:
            await self.connection.send_json(payload)

    async def unsubscribe(self, payload: Dict[str, Any]) -> None:
        self._subscriptions = [sub for sub in self._subscriptions if sub != payload]
        if self.connection is not None:
            await self.connection.send_json({**payload, "op": "UNSUB"})

    async def listen(self):  # pragma: no cover - streaming for live trading
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._listen_task = asyncio.create_task(self._reader(queue))
        self._heartbeat_task = asyncio.create_task(self._heartbeat())
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event

    async def _connect(self) -> None:
        assert self.session is not None
        self.connection = await self.session.ws_connect(self.url)
        for payload in self._subscriptions:
            await self.connection.send_json(payload)

    async def _reader(self, queue: asyncio.Queue) -> None:
        assert self.connection is not None
        async for message in self.connection:
            if message.type == aiohttp.WSMsgType.TEXT:
                await queue.put(message.json())
            elif message.type == aiohttp.WSMsgType.BINARY:
                await queue.put({"binary": message.data})
            elif message.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR}:
                await queue.put({"event": "disconnect"})
                if self.reconnect:
                    await self._connect()
                else:
                    break
        await queue.put(None)

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            if self.connection is not None:
                try:
                    await self.connection.ping()
                except Exception:  # pragma: no cover - network failure
                    if self.reconnect:
                        await self._connect()
                    else:
                        break


__all__ = ["RestExchangeAdapter", "WebsocketExchangeAdapter", "ExecutionReport"]

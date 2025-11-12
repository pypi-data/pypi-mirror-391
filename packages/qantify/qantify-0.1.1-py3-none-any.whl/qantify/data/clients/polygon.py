"""Polygon.io market data client."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Dict

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime

from ..base import BaseClient
from ..errors import DataClientError, DataNormalizationError


_POLYGON_TIMEFRAMES = {
    "1m": TimeFrame("1m", "1T", 60),
    "5m": TimeFrame("5m", "5T", 300),
    "15m": TimeFrame("15m", "15T", 900),
    "1h": TimeFrame("1h", "1H", 3600),
    "1d": TimeFrame("1d", "1D", 86_400),
}


class PolygonClient(BaseClient):
    name = "polygon"
    rest_endpoint = "https://api.polygon.io"
    klines_path = "/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start}/{end}"
    api_key: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.api_key = api_key

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _POLYGON_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported Polygon interval '{value}'.") from exc

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

        if start is None or end is None:
            raise ValueError("Polygon client requires explicit start/end dates.")

        start_dt = ensure_datetime(start)
        end_dt = ensure_datetime(end)

        timespan = timeframe.name
        multiplier = 1

        path = self.klines_path.format(
            symbol=symbol.value.replace("/", "-"),
            multiplier=multiplier,
            timespan=timespan,
            start=start_dt.date().isoformat(),
            end=end_dt.date().isoformat(),
        )
        url = f"{self.rest_endpoint}{path}"

        params = {"adjusted": "true"}
        if limit:
            params["limit"] = limit
        if self.api_key:
            params["apiKey"] = self.api_key

        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            payload = await response.json()

        results = payload.get("results")
        if not isinstance(results, list):
            raise DataNormalizationError("Unexpected Polygon response structure.")

        records = []
        for item in results:
            try:
                records.append(
                    {
                        "timestamp": ensure_datetime(item["t"] / 1000),
                        "open": float(item["o"]),
                        "high": float(item["h"]),
                        "low": float(item["l"]),
                        "close": float(item["c"]),
                        "volume": float(item.get("v", 0.0)),
                    }
                )
            except (KeyError, ValueError, TypeError) as exc:
                raise DataNormalizationError("Invalid Polygon candle payload.") from exc

        return records

    async def fetch_trades(
        self,
        symbol: Symbol,
        *,
        timestamp: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        await self._ensure_session()
        path = f"/v3/trades/{symbol.value}"
        params: Dict[str, Any] = {}
        if timestamp:
            params["timestamp"] = int(ensure_datetime(timestamp).timestamp() * 1e9)
        if limit:
            params["limit"] = limit
        if self.api_key:
            params["apiKey"] = self.api_key

        url = f"{self.rest_endpoint}{path}"
        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            payload = await response.json()

        results = payload.get("results")
        if not isinstance(results, list):
            raise DataNormalizationError("Unexpected Polygon trades payload.")

        return [
            {
                "timestamp": ensure_datetime(item["t"] / 1e9),
                "price": float(item["p"]),
                "size": float(item.get("s", 0.0)),
                "conditions": item.get("c", []),
            }
            for item in results
        ]

    async def fetch_quote(self, symbol: Symbol) -> dict[str, Any]:
        await self._ensure_session()
        path = f"/v2/last/nbbo/{symbol.value}"
        params = {"apiKey": self.api_key} if self.api_key else {}
        url = f"{self.rest_endpoint}{path}"
        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            payload = await response.json()
        return payload

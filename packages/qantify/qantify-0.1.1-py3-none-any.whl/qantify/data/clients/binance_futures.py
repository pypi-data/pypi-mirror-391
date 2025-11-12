"""Binance derivatives data clients."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable, Optional

from qantify.core import Symbol, TimeFrame
from qantify.core.utils import ensure_datetime

from ..base import BaseClient
from ..clients.binance import _BINANCE_TIMEFRAMES
from ..errors import DataClientError, DataNormalizationError


class _BinanceDerivativesMixin(BaseClient):
    rest_endpoint: str = ""
    klines_path: str = ""
    contract_type: str = "perpetual"
    funding_path: str = ""

    def resolve_timeframe(self, value: str) -> TimeFrame:
        try:
            return _BINANCE_TIMEFRAMES[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported Binance interval '{value}'.") from exc

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
        start_ms = int(self._normalize_ts(start) * 1000) if start else None
        end_ms = int(self._normalize_ts(end) * 1000) if end else None

        records: list[dict[str, Any]] = []
        remaining = limit
        next_start = start_ms

        while True:
            batch_limit = min(remaining or self.max_batch_size, self.max_batch_size)
            params = {
                "symbol": symbol_value,
                "interval": timeframe.name,
                "limit": batch_limit,
            }
            if start_ms is not None:
                params["startTime"] = next_start or start_ms
            if end_ms is not None:
                params["endTime"] = end_ms
            if self.contract_type:
                params["contractType"] = self.contract_type

            url = f"{self.rest_endpoint}{self.klines_path}"
            async with await self._request_context("get", url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()

            if not isinstance(payload, list) or not payload:
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

    def _normalize_ts(self, value: Any) -> float:
        return ensure_datetime(value).timestamp()

    def _format_symbol(self, symbol: Symbol) -> str:
        value = symbol.value.replace("/", "").replace("-", "").upper()
        return value

    def _normalize_batch(self, payload: list[list[Any]], symbol: Symbol, timeframe: TimeFrame) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for entry in payload:
            if len(entry) < 6:
                raise DataNormalizationError("Unexpected Binance derivatives kline payload length.")
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


class BinanceFuturesClient(_BinanceDerivativesMixin):
    name = "binance_futures"
    rest_endpoint = "https://fapi.binance.com"
    klines_path = "/fapi/v1/klines"
    funding_path = "/fapi/v1/fundingRate"
    max_batch_size = 1500

    def _format_symbol(self, symbol: Symbol) -> str:
        return super()._format_symbol(symbol) + ""

    async def fetch_funding_rates(
        self,
        symbol: Symbol,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        await self._ensure_session()

        params = {"symbol": self._format_symbol(symbol)}
        if start:
            params["startTime"] = int(ensure_datetime(start).timestamp() * 1000)
        if end:
            params["endTime"] = int(ensure_datetime(end).timestamp() * 1000)
        if limit:
            params["limit"] = limit

        url = f"{self.rest_endpoint}{self.funding_path}"
        async with await self._request_context("get", url, params=params) as response:
            response.raise_for_status()
            payload = await response.json()

        if not isinstance(payload, list):
            raise DataClientError("Unexpected Binance funding rate payload.")

        return [
            {
                "timestamp": ensure_datetime(item["fundingTime"] / 1000),
                "rate": float(item["fundingRate"]),
            }
            for item in payload
        ]


class BinanceOptionsClient(_BinanceDerivativesMixin):
    name = "binance_options"
    rest_endpoint = "https://eapi.binance.com"
    klines_path = "/eapi/v1/klines"
    max_batch_size = 1000

    def _format_symbol(self, symbol: Symbol) -> str:
        return symbol.value.replace("-", "")

    def _normalize_batch(self, payload: list[list[Any]], symbol: Symbol, timeframe: TimeFrame) -> list[dict[str, Any]]:
        normalized = super()._normalize_batch(payload, symbol, timeframe)
        for row in normalized:
            row["volume"] = float(row["volume"])
        return normalized

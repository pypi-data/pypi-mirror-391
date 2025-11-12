"""Abstract base definitions for exchange data clients."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
import inspect
from typing import Any, Iterable, Optional

import aiohttp

from qantify.core import Symbol, TimeFrame


class BaseClient(AbstractAsyncContextManager, ABC):
    """Base class for asynchronous market data clients."""

    name: str = "base"
    user_agent: str = "qantify/0.1"
    timeout_seconds: float = 30

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self._session = session
        self._owns_session = session is None
        self._session_lock = asyncio.Lock()

    async def __aenter__(self) -> "BaseClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP session if this client created it."""

        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def _ensure_session(self) -> None:
        if self._session is not None:
            return

        async with self._session_lock:
            if self._session is not None:
                return

            timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
            headers = {"User-Agent": self.user_agent}
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("HTTP session not initialized. Use the client as an async context manager.")
        return self._session

    async def _request_context(self, method: str, url: str, **kwargs: Any) -> Any:
        await self._ensure_session()
        session = self.session
        handler = getattr(session, method)
        context = handler(url, **kwargs)
        if not hasattr(context, "__aenter__") and inspect.isawaitable(context):
            context = await context
        return context

    @abstractmethod
    def resolve_timeframe(self, value: str) -> TimeFrame:
        """Resolve a user-specified interval string into a ``TimeFrame``."""

    @abstractmethod
    async def fetch_candles(
        self,
        symbol: Symbol,
        timeframe: TimeFrame,
        *,
        start: Optional[Any] = None,
        end: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Iterable[dict[str, Any]]:
        """Fetch OHLCV candles for a symbol/timeframe pair."""

    def canonicalize_symbol(self, value: Symbol | str) -> Symbol:
        """Return a ``Symbol`` instance ensuring exchange information is set."""

        if isinstance(value, Symbol):
            return value
        return Symbol(value=value)

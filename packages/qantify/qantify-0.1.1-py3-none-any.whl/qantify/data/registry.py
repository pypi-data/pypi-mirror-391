"""Client registry and factory helpers."""

from __future__ import annotations

from typing import Dict, Iterable, Type

from .base import BaseClient
from .errors import ClientNotRegisteredError


_REGISTRY: Dict[str, Type[BaseClient]] = {}


def register_client(exchange: str, client_cls: Type[BaseClient], *, overwrite: bool = False) -> None:
    """Register a client class for the given exchange identifier."""

    key = exchange.lower()
    if not overwrite and key in _REGISTRY and _REGISTRY[key] is not client_cls:
        raise ValueError(f"Client already registered for exchange '{exchange}'.")

    _REGISTRY[key] = client_cls


def create_client(exchange: str, **kwargs) -> BaseClient:
    """Instantiate a registered client for the exchange."""

    key = exchange.lower()
    try:
        client_cls = _REGISTRY[key]
    except KeyError as exc:
        raise ClientNotRegisteredError(f"No client registered for exchange '{exchange}'.") from exc

    return client_cls(**kwargs)


def list_clients() -> Iterable[str]:
    """Return identifiers for all registered clients."""

    return tuple(sorted(_REGISTRY))

"""qantify: High-performance, flexible quantitative trading toolkit."""

from importlib import import_module
from typing import Any

__all__ = [
    "lazy_import",
]


def lazy_import(path: str) -> Any:
    """Lazy-import a module or attribute by dotted path.

    This helper lets heavy dependencies stay optional until they're needed.

    Args:
        path: Dotted path to import, e.g. ``"qantify.data"`` or
            ``"qantify.signals.rsi"``.

    Returns:
        The imported module or attribute resolved from the dotted path.
    """

    module_path, dot, attr = path.rpartition(".")

    if not dot:
        return import_module(path)

    module = import_module(module_path)
    return getattr(module, attr)

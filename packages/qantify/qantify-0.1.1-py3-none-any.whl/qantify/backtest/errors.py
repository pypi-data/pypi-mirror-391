"""Custom exceptions for backtesting engines."""


class BacktestError(RuntimeError):
    """Base error for backtest-related failures."""


class ConfigurationError(BacktestError):
    """Raised when strategy or engine configuration is invalid."""


class ExecutionError(BacktestError):
    """Raised when an order cannot be executed under the given market conditions."""

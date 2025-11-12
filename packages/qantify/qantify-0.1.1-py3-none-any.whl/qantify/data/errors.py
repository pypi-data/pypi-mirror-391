"""Custom exception types for the qantify.data module."""


class DataError(RuntimeError):
    """Base error raised by the data module."""


class DataClientError(DataError):
    """Raised when a client fails to fetch data from its source."""


class DataNormalizationError(DataError):
    """Raised when raw payloads cannot be normalized into the expected schema."""


class ClientNotRegisteredError(DataError):
    """Raised when attempting to use an exchange that is not registered."""

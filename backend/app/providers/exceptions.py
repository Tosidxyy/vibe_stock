"""Stable exceptions for data-source failures."""


class DataSourceError(Exception):
    """A provider request or response could not produce valid market data."""


class ProviderTimeoutError(DataSourceError):
    """All available endpoints timed out."""


class InvalidSymbolError(ValueError):
    """The supplied security code is not a supported A-share symbol."""

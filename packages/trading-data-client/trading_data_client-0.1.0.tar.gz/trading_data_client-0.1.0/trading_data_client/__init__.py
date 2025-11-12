"""
Trading Data Client Library

A Python client library for the Trading Data Server.
Provides simple interface for historical data and real-time streaming.
"""

import logging

__version__ = "0.1.0"

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Import main components
from .client import TradingDataClient
from .models import Bar, Subscription
from .exceptions import (
    TradingDataClientError,
    ConnectionError,
    ClientError,
    ServerError,
    ValidationError
)

__all__ = [
    # Main client
    "TradingDataClient",
    # Models
    "Bar",
    "Subscription",
    # Exceptions
    "TradingDataClientError",
    "ConnectionError",
    "ClientError",
    "ServerError",
    "ValidationError",
    # Version
    "__version__",
]

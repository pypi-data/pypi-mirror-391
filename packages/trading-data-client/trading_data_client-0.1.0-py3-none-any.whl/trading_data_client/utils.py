"""
Utility functions for trading-data-client.

Provides validation and helper functions.
"""

import uuid
from datetime import datetime
from typing import List


VALID_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo']


def validate_symbol(symbol: str) -> None:
    """
    Validate ticker symbol.
    
    Args:
        symbol: Ticker symbol to validate
        
    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol:
        raise ValueError("symbol cannot be empty")
    if len(symbol) > 10:
        raise ValueError("symbol must be 10 characters or less")
    if not symbol.replace('.', '').replace('-', '').isalnum():
        raise ValueError("symbol must contain only alphanumeric characters, dots, and hyphens")


def validate_timeframe(timeframe: str) -> None:
    """
    Validate timeframe.
    
    Args:
        timeframe: Timeframe to validate
        
    Raises:
        ValueError: If timeframe is invalid
    """
    if timeframe not in VALID_TIMEFRAMES:
        raise ValueError(f"timeframe must be one of {VALID_TIMEFRAMES}")


def validate_datetime_range(start: datetime, end: datetime) -> None:
    """
    Validate datetime range.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Raises:
        ValueError: If range is invalid
    """
    if start >= end:
        raise ValueError("start must be before end")


def generate_subscription_id() -> str:
    """
    Generate unique subscription ID.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_valid_timeframes() -> List[str]:
    """
    Get list of valid timeframes.
    
    Returns:
        List of valid timeframe strings
    """
    return VALID_TIMEFRAMES.copy()

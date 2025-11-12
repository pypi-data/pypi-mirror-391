"""
Exception classes for trading-data-client.

Defines custom exception hierarchy for clear error handling.
"""

from typing import Optional, Dict, Any


class TradingDataClientError(Exception):
    """
    Base exception for all client errors.
    
    All exceptions raised by the client inherit from this class.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConnectionError(TradingDataClientError):
    """
    Raised when connection to server fails.
    
    Indicates network or connectivity issue. May be transient.
    """
    
    def __init__(self, message: str, url: Optional[str] = None):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            url: URL that failed to connect
        """
        super().__init__(message, {"url": url})
        self.url = url


class ClientError(TradingDataClientError):
    """
    Raised when server returns 4xx error.
    
    Indicates client-side error (bad request). Retry will not succeed
    without fixing the request.
    """
    
    def __init__(self, status_code: int, message: str, response: Optional[Dict[str, Any]] = None):
        """
        Initialize client error.
        
        Args:
            status_code: HTTP status code (400-499)
            message: Error message
            response: Server response body
        """
        super().__init__(
            f"Client error {status_code}: {message}",
            {"status_code": status_code, "response": response}
        )
        self.status_code = status_code
        self.response = response


class ServerError(TradingDataClientError):
    """
    Raised when server returns 5xx error.
    
    Indicates server-side error. May be transient.
    """
    
    def __init__(self, status_code: int, message: str, response: Optional[Dict[str, Any]] = None):
        """
        Initialize server error.
        
        Args:
            status_code: HTTP status code (500-599)
            message: Error message
            response: Server response body
        """
        super().__init__(
            f"Server error {status_code}: {message}",
            {"status_code": status_code, "response": response}
        )
        self.status_code = status_code
        self.response = response


class ValidationError(TradingDataClientError):
    """
    Raised when data validation fails.
    
    Indicates invalid data from server or user.
    """
    
    def __init__(self, field: str, message: str):
        """
        Initialize validation error.
        
        Args:
            field: Field that failed validation
            message: Error message
        """
        super().__init__(
            f"Validation error on field '{field}': {message}",
            {"field": field}
        )
        self.field = field

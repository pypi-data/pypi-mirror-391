"""
Configuration management for trading-data-client.

Supports loading configuration from environment variables.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """
    Client configuration.
    
    Can be loaded from environment variables or provided programmatically.
    """
    
    server_url: str = Field(
        default="http://localhost:8000",
        description="Trading Data Server REST API URL"
    )
    zmq_address: str = Field(
        default="tcp://localhost:5555",
        description="ZeroMQ publisher address"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="HTTP request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    @classmethod
    def from_env(cls) -> "ClientConfig":
        """
        Load configuration from environment variables.
        
        Environment variables:
        - TRADING_SERVER_URL: Server URL
        - TRADING_ZMQ_ADDRESS: ZeroMQ address
        - TRADING_CLIENT_TIMEOUT: Request timeout
        - TRADING_CLIENT_MAX_RETRIES: Max retries
        - TRADING_CLIENT_LOG_LEVEL: Log level
        
        Returns:
            ClientConfig instance with values from environment
        """
        return cls(
            server_url=os.getenv("TRADING_SERVER_URL", "http://localhost:8000"),
            zmq_address=os.getenv("TRADING_ZMQ_ADDRESS", "tcp://localhost:5555"),
            timeout=int(os.getenv("TRADING_CLIENT_TIMEOUT", "30")),
            max_retries=int(os.getenv("TRADING_CLIENT_MAX_RETRIES", "3")),
            log_level=os.getenv("TRADING_CLIENT_LOG_LEVEL", "INFO"),
        )

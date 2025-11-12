"""
Data models for trading-data-client.

Defines Pydantic models for type-safe data handling.
"""

from datetime import datetime
from typing import Callable
from pydantic import BaseModel, Field, field_validator
import uuid


class Bar(BaseModel):
    """
    OHLCV bar data.
    
    Represents a single bar of market data with Open, High, Low, Close, and Volume.
    Includes validation to ensure price consistency.
    """
    
    symbol: str = Field(..., description="Ticker symbol", min_length=1, max_length=10)
    timestamp: datetime = Field(..., description="Bar timestamp (UTC)")
    open: float = Field(..., gt=0, description="Opening price")
    high: float = Field(..., gt=0, description="Highest price")
    low: float = Field(..., gt=0, description="Lowest price")
    close: float = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")
    timeframe: str = Field(..., description="Bar interval")
    
    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v: float, info) -> float:
        """Validate high >= open, close, low."""
        values = info.data
        if 'open' in values and v < values['open']:
            raise ValueError('high must be >= open')
        if 'close' in values and v < values['close']:
            raise ValueError('high must be >= close')
        if 'low' in values and v < values['low']:
            raise ValueError('high must be >= low')
        return v
    
    @field_validator('low')
    @classmethod
    def low_must_be_lowest(cls, v: float, info) -> float:
        """Validate low <= open, close, high."""
        values = info.data
        if 'open' in values and v > values['open']:
            raise ValueError('low must be <= open')
        if 'close' in values and v > values['close']:
            raise ValueError('low must be <= close')
        return v
    
    @field_validator('timeframe')
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Validate timeframe format."""
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo']
        if v not in valid_timeframes:
            raise ValueError(f'timeframe must be one of {valid_timeframes}')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Subscription(BaseModel):
    """
    Internal subscription tracking.
    
    Tracks active subscriptions for real-time streaming.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique subscription ID")
    symbol: str = Field(..., description="Ticker symbol")
    timeframe: str = Field(..., description="Bar interval")
    callback: Callable[[Bar], None] = Field(..., description="Callback function")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    
    class Config:
        arbitrary_types_allowed = True  # Allow Callable type

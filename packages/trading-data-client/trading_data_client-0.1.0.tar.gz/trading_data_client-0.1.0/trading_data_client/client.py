"""
Main client facade for Trading Data Server.

Provides unified interface for historical data and real-time streaming.
"""

import logging
import signal
import time
from typing import List, Callable
from datetime import datetime

from .historical import HistoricalClient
from .stream import StreamClient
from .models import Bar
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class TradingDataClient:
    """
    Main client for Trading Data Server.
    
    Provides unified interface for historical data and real-time streaming.
    
    Thread Safety: Safe for concurrent historical requests.
                   Streaming callbacks invoked from background thread.
    
    Resource Management: Must call close() or use context manager.
    """
    
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        zmq_address: str = "tcp://localhost:5555",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize client.
        
        Args:
            server_url: Base URL of Trading Data Server REST API
            zmq_address: ZeroMQ publisher address
            timeout: HTTP request timeout in seconds (1-300)
            max_retries: Maximum number of retry attempts (0-10)
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if timeout < 1 or timeout > 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
        if max_retries < 0 or max_retries > 10:
            raise ValueError("max_retries must be between 0 and 10")
        
        self.server_url = server_url
        self.zmq_address = zmq_address
        
        # Create sub-clients
        self.historical_client = HistoricalClient(server_url, timeout, max_retries)
        self.stream_client = StreamClient(zmq_address)
        
        # Track if closed
        self._closed = False
        
        logger.info(f"TradingDataClient initialized: server={server_url}, zmq={zmq_address}")
    
    def get_historical_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> List[Bar]:
        """
        Fetch historical OHLCV bars.
        
        Args:
            symbol: Ticker symbol (1-10 chars, uppercase recommended)
            start: Start datetime (UTC, inclusive)
            end: End datetime (UTC, inclusive)
            timeframe: Bar interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo)
            
        Returns:
            List of Bar objects sorted by timestamp
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If server is unreachable
            ClientError: If server returns 4xx error
            ServerError: If server returns 5xx error
        """
        # Validate parameters
        if not symbol or len(symbol) > 10:
            raise ValueError("symbol must be 1-10 characters")
        if start >= end:
            raise ValueError("start must be before end")
        
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo']
        if timeframe not in valid_timeframes:
            raise ValueError(f"timeframe must be one of {valid_timeframes}")
        
        # Delegate to historical client
        return self.historical_client.get_bars(symbol, start, end, timeframe)
    
    def subscribe(
        self,
        symbol: str,
        timeframe: str,
        callback: Callable[[Bar], None],
        poll_interval: int = 60
    ) -> str:
        """
        Subscribe to real-time data stream.
        
        Args:
            symbol: Ticker symbol
            timeframe: Bar interval
            callback: Function called when new bar arrives
                     Signature: callback(bar: Bar) -> None
            poll_interval: Server polling interval in seconds (default: 60)
            
        Returns:
            Subscription ID (UUID string)
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If ZeroMQ connection fails
        """
        # Validate parameters
        if not symbol or len(symbol) > 10:
            raise ValueError("symbol must be 1-10 characters")
        
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo']
        if timeframe not in valid_timeframes:
            raise ValueError(f"timeframe must be one of {valid_timeframes}")
        
        if not callable(callback):
            raise ValueError("callback must be callable")
        
        # Delegate to stream client
        return self.stream_client.subscribe(symbol, timeframe, callback)
    
    def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from stream.
        
        Args:
            subscription_id: ID returned from subscribe()
        """
        self.stream_client.unsubscribe(subscription_id)
    
    def playback(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str,
        speed: float,
        callback: Callable[[Bar], None]
    ) -> str:
        """
        Start historical playback.
        
        Args:
            symbol: Ticker symbol
            start: Start datetime (UTC)
            end: End datetime (UTC)
            timeframe: Bar interval
            speed: Playback speed multiplier (0 = unlimited, >0 = multiplier)
            callback: Function called for each bar
                     Signature: callback(bar: Bar) -> None
            
        Returns:
            Playback ID (UUID string)
            
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If ZeroMQ connection fails
        """
        # Validate parameters
        if not symbol or len(symbol) > 10:
            raise ValueError("symbol must be 1-10 characters")
        if start >= end:
            raise ValueError("start must be before end")
        if speed < 0:
            raise ValueError("speed must be >= 0")
        
        # For playback, we use a special topic format
        # The server should handle playback requests
        # For now, we'll subscribe with a playback prefix
        playback_symbol = f"{symbol}_playback"
        
        return self.stream_client.subscribe(playback_symbol, timeframe, callback)
    
    def stop_playback(self, playback_id: str) -> None:
        """
        Stop historical playback.
        
        Args:
            playback_id: ID returned from playback()
        """
        self.stream_client.unsubscribe(playback_id)
    
    def run(self) -> None:
        """
        Run event loop (blocking).
        
        Blocks until interrupted (Ctrl+C).
        Keeps client running to receive streaming data.
        Call from main thread.
        
        Raises:
            KeyboardInterrupt: When Ctrl+C pressed
        """
        logger.info("Running event loop (press Ctrl+C to stop)")
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info("Interrupt received, stopping...")
            raise KeyboardInterrupt()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Event loop stopped")
            raise
    
    def close(self) -> None:
        """
        Close client and cleanup resources.
        
        - Unsubscribes from all streams
        - Closes ZeroMQ sockets
        - Closes HTTP session
        - Stops background threads (with 5 second timeout)
        - Idempotent (safe to call multiple times)
        - Blocks until cleanup complete
        """
        if self._closed:
            return
        
        logger.info("Closing TradingDataClient")
        
        # Close stream client (stops threads, closes sockets)
        self.stream_client.close()
        
        # Close historical client (closes HTTP session)
        self.historical_client.close()
        
        self._closed = True
        logger.info("TradingDataClient closed")
    
    def __enter__(self) -> "TradingDataClient":
        """
        Context manager entry.
        
        Returns:
            self
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit.
        
        Calls close() automatically.
        Does not suppress exceptions.
        """
        self.close()

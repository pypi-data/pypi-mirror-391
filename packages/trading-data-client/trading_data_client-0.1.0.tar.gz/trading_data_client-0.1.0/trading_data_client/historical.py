"""
Historical data client for REST API.

Handles fetching historical OHLCV data from Trading Data Server.
"""

import logging
from typing import List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import Bar
from .exceptions import ConnectionError, ClientError, ServerError, ValidationError

logger = logging.getLogger(__name__)


class HistoricalClient:
    """
    Client for fetching historical data via REST API.
    
    Thread-safe for concurrent requests (uses connection pooling).
    """
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize historical client.
        
        Args:
            base_url: Base URL of REST API
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"HistoricalClient initialized: {base_url}")
    
    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> List[Bar]:
        """
        Fetch historical bars.
        
        Args:
            symbol: Ticker symbol
            start: Start datetime (UTC)
            end: End datetime (UTC)
            timeframe: Bar interval
            
        Returns:
            List of Bar objects sorted by timestamp
            
        Raises:
            ConnectionError: If request fails
            ClientError: If server returns 4xx
            ServerError: If server returns 5xx
            ValidationError: If response data is invalid
        """
        # Build URL
        url = f"{self.base_url}/api/v1/bars/historical"
        
        # Build query parameters
        params = {
            "symbol": symbol,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "timeframe": timeframe
        }
        
        logger.debug(f"Fetching bars: {symbol} {timeframe} from {start} to {end}")
        
        try:
            # Make request
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Check status code
            if response.status_code >= 400 and response.status_code < 500:
                error_msg = response.json().get("detail", response.text) if response.text else "Client error"
                logger.error(f"Client error {response.status_code}: {error_msg}")
                raise ClientError(response.status_code, error_msg, response.json() if response.text else None)
            
            if response.status_code >= 500:
                error_msg = response.json().get("detail", response.text) if response.text else "Server error"
                logger.error(f"Server error {response.status_code}: {error_msg}")
                raise ServerError(response.status_code, error_msg, response.json() if response.text else None)
            
            # Parse response
            response.raise_for_status()
            data = response.json()
            
            # Extract bars array from response
            bars_data = data.get('bars', []) if isinstance(data, dict) else data
            
            # Convert to Bar objects
            bars = []
            for bar_data in bars_data:
                try:
                    # Parse timestamp if it's a string
                    if isinstance(bar_data.get('timestamp'), str):
                        from dateutil import parser
                        bar_data['timestamp'] = parser.isoparse(bar_data['timestamp'])
                    
                    # Add timeframe if not present
                    if 'timeframe' not in bar_data:
                        bar_data['timeframe'] = timeframe
                    
                    # Convert volume to int if it's float
                    if 'volume' in bar_data and isinstance(bar_data['volume'], float):
                        bar_data['volume'] = int(bar_data['volume'])
                    
                    bar = Bar(**bar_data)
                    bars.append(bar)
                except Exception as e:
                    logger.warning(f"Failed to parse bar: {e}")
                    raise ValidationError("bar_data", str(e))
            
            logger.info(f"Fetched {len(bars)} bars for {symbol}")
            return bars
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Cannot connect to server: {e}", url)
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise ConnectionError(f"Request timeout: {e}", url)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise ConnectionError(f"Request failed: {e}", url)
    
    def health_check(self) -> dict:
        """
        Check server health.
        
        Returns:
            Health status dictionary
            
        Raises:
            ConnectionError: If request fails
        """
        url = f"{self.base_url}/api/v1/health"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise ConnectionError(f"Health check failed: {e}", url)
    
    def close(self) -> None:
        """Close HTTP session."""
        self.session.close()
        logger.info("HistoricalClient closed")

"""
Stream client for ZeroMQ subscriptions.

Handles real-time data streaming via ZeroMQ.
"""

import logging
import threading
import json
from typing import Dict, Callable
import zmq
from datetime import datetime
from dateutil import parser

from .models import Bar, Subscription
from .exceptions import ConnectionError as ClientConnectionError

logger = logging.getLogger(__name__)


class StreamClient:
    """
    Client for subscribing to real-time ZeroMQ streams.
    
    Thread-safe subscription management.
    Callbacks invoked from background thread.
    """
    
    def __init__(self, zmq_address: str):
        """
        Initialize stream client.
        
        Args:
            zmq_address: ZeroMQ publisher address (e.g., "tcp://localhost:5555")
        """
        self.zmq_address = zmq_address
        self.context = zmq.Context()
        self.socket = None
        self.subscriptions: Dict[str, Subscription] = {}
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        logger.info(f"StreamClient initialized: {zmq_address}")
    
    def subscribe(
        self,
        symbol: str,
        timeframe: str,
        callback: Callable[[Bar], None]
    ) -> str:
        """
        Subscribe to stream.
        
        Args:
            symbol: Ticker symbol
            timeframe: Bar interval
            callback: Function to call on new bar
            
        Returns:
            Subscription ID
            
        Raises:
            ConnectionError: If ZeroMQ connection fails
        """
        with self.lock:
            # Create subscription
            subscription = Subscription(
                symbol=symbol,
                timeframe=timeframe,
                callback=callback
            )
            
            # Add to subscriptions
            self.subscriptions[subscription.id] = subscription
            
            logger.info(f"Subscribed: {symbol} {timeframe} (id={subscription.id})")
            
            # Connect if not connected
            if self.socket is None:
                self._connect()
            
            # Subscribe to topic
            topic = symbol.encode('utf-8')
            self.socket.setsockopt(zmq.SUBSCRIBE, topic)
            
            # Start thread if not running
            if not self.running:
                self._start_thread()
            
            return subscription.id
    
    def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from stream.
        
        Args:
            subscription_id: ID from subscribe()
        """
        with self.lock:
            if subscription_id in self.subscriptions:
                subscription = self.subscriptions[subscription_id]
                
                # Remove subscription
                del self.subscriptions[subscription_id]
                
                logger.info(f"Unsubscribed: {subscription.symbol} {subscription.timeframe} (id={subscription_id})")
                
                # If no more subscriptions, stop thread and close socket
                if not self.subscriptions:
                    self._stop_thread()
    
    def _connect(self) -> None:
        """Connect to ZeroMQ publisher."""
        try:
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect(self.zmq_address)
            # Set receive timeout to allow checking running flag
            self.socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
            logger.info(f"Connected to ZeroMQ: {self.zmq_address}")
        except Exception as e:
            logger.error(f"Failed to connect to ZeroMQ: {e}")
            raise ClientConnectionError(f"Failed to connect to ZeroMQ: {e}", self.zmq_address)
    
    def _start_thread(self) -> None:
        """Start background thread for receiving messages."""
        self.running = True
        self.thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.thread.start()
        logger.info("Background thread started")
    
    def _stop_thread(self) -> None:
        """Stop background thread."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            logger.info("Background thread stopped")
        
        # Close socket
        if self.socket:
            self.socket.close()
            self.socket = None
            logger.info("ZeroMQ socket closed")
    
    def _receive_loop(self) -> None:
        """
        Background thread loop.
        
        Receives messages from ZeroMQ and dispatches to callbacks.
        """
        logger.info("Receive loop started")
        
        while self.running:
            try:
                # Receive message (with timeout)
                try:
                    message = self.socket.recv_multipart()
                except zmq.Again:
                    # Timeout, check if still running
                    continue
                
                if len(message) < 2:
                    logger.warning(f"Invalid message format: {message}")
                    continue
                
                # Parse topic and data
                topic = message[0].decode('utf-8')
                data_json = message[1].decode('utf-8')
                
                logger.debug(f"Received message: topic={topic}")
                
                # Parse JSON
                try:
                    data = json.loads(data_json)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    continue
                
                # Dispatch to callbacks
                self._dispatch_message(topic, data)
                
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                # Continue running unless explicitly stopped
        
        logger.info("Receive loop stopped")
    
    def _dispatch_message(self, topic: str, message: dict) -> None:
        """
        Dispatch message to appropriate callback.
        
        Args:
            topic: ZeroMQ topic (symbol)
            message: Parsed JSON message
        """
        # Convert message to Bar
        try:
            # Parse timestamp if it's a string
            if isinstance(message.get('timestamp'), str):
                message['timestamp'] = parser.isoparse(message['timestamp'])
            
            bar = Bar(**message)
        except Exception as e:
            logger.error(f"Failed to create Bar from message: {e}")
            return
        
        # Find matching subscriptions
        with self.lock:
            matching_subs = [
                sub for sub in self.subscriptions.values()
                if sub.symbol == bar.symbol and sub.timeframe == bar.timeframe
            ]
        
        # Invoke callbacks
        for subscription in matching_subs:
            try:
                subscription.callback(bar)
            except Exception as e:
                logger.error(f"Callback error for subscription {subscription.id}: {e}")
    
    def close(self) -> None:
        """
        Close ZeroMQ socket and stop thread.
        """
        logger.info("Closing StreamClient")
        
        with self.lock:
            # Clear all subscriptions
            self.subscriptions.clear()
        
        # Stop thread
        self._stop_thread()
        
        # Destroy context
        self.context.term()
        
        logger.info("StreamClient closed")

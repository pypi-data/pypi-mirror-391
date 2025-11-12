#!/usr/bin/env python3
"""
Example: Real-Time Streaming

Demonstrates how to subscribe to real-time market data streams.
"""

from trading_data_client import TradingDataClient, Bar
from datetime import datetime


def on_bar(bar: Bar):
    """
    Callback function invoked when new bar arrives.
    
    Args:
        bar: New bar data
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"{bar.symbol} @ {bar.timestamp.strftime('%H:%M:%S')}: "
          f"O={bar.open:.2f} H={bar.high:.2f} L={bar.low:.2f} C={bar.close:.2f} V={bar.volume:,}")


def main():
    """Subscribe to real-time data stream."""
    
    print("=" * 80)
    print("Real-Time Streaming Example")
    print("=" * 80)
    print("\nThis example subscribes to real-time AAPL 1-minute bars.")
    print("Press Ctrl+C to stop.\n")
    
    # Create client
    client = TradingDataClient(
        server_url="http://localhost:8000",
        zmq_address="tcp://localhost:5555"
    )
    
    try:
        # Subscribe to AAPL 1-minute bars
        print("Subscribing to AAPL 1m stream...")
        subscription_id = client.subscribe(
            symbol="AAPL",
            timeframe="1m",
            callback=on_bar,
            poll_interval=60  # Server polls every 60 seconds
        )
        
        print(f"Subscribed! (subscription_id={subscription_id})")
        print("\nWaiting for data...\n")
        
        # Run event loop (blocks until Ctrl+C)
        client.run()
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
        
        # Unsubscribe
        print("Unsubscribing...")
        client.unsubscribe(subscription_id)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        print("Closing client...")
        client.close()
        print("Done!")


if __name__ == "__main__":
    main()

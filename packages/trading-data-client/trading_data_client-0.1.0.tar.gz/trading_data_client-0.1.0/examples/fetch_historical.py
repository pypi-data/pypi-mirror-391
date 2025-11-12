#!/usr/bin/env python3
"""
Example: Fetch Historical Data

Demonstrates how to fetch historical OHLCV data using the Trading Data Client.
"""

from trading_data_client import TradingDataClient, ConnectionError, ClientError, ServerError
from datetime import datetime, timedelta


def main():
    """Fetch and display historical bars."""
    
    # Create client
    print("Creating Trading Data Client...")
    client = TradingDataClient(
        server_url="http://localhost:8000",
        timeout=30,
        max_retries=3
    )
    
    try:
        # Define date range (last 30 days)
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        
        print(f"\nFetching AAPL daily bars from {start.date()} to {end.date()}...")
        
        # Fetch historical bars
        bars = client.get_historical_bars(
            symbol="AAPL",
            start=start,
            end=end,
            timeframe="1d"
        )
        
        print(f"\nFetched {len(bars)} bars:\n")
        
        # Display bars
        print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
        print("-" * 70)
        
        for bar in bars[:10]:  # Show first 10 bars
            print(
                f"{bar.timestamp.date()!s:<12} "
                f"{bar.open:>10.2f} "
                f"{bar.high:>10.2f} "
                f"{bar.low:>10.2f} "
                f"{bar.close:>10.2f} "
                f"{bar.volume:>12,}"
            )
        
        if len(bars) > 10:
            print(f"... and {len(bars) - 10} more bars")
        
        # Calculate some statistics
        if bars:
            closes = [bar.close for bar in bars]
            avg_close = sum(closes) / len(closes)
            min_close = min(closes)
            max_close = max(closes)
            
            print(f"\nStatistics:")
            print(f"  Average Close: ${avg_close:.2f}")
            print(f"  Min Close: ${min_close:.2f}")
            print(f"  Max Close: ${max_close:.2f}")
            print(f"  Price Range: ${max_close - min_close:.2f} ({((max_close - min_close) / min_close * 100):.1f}%)")
        
    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Make sure the Trading Data Server is running at http://localhost:8000")
    
    except ClientError as e:
        print(f"\n❌ Client Error ({e.status_code}): {e}")
        print("Check your request parameters (symbol, dates, timeframe)")
    
    except ServerError as e:
        print(f"\n❌ Server Error ({e.status_code}): {e}")
        print("The server encountered an error. Try again later.")
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
    
    finally:
        # Clean up
        print("\nClosing client...")
        client.close()
        print("Done!")


if __name__ == "__main__":
    main()

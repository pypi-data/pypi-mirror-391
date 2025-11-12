# Trading Data Client

A Python client library for accessing historical and real-time market data from the Trading Data Server.

## Features

- 📊 **Historical Data**: Fetch OHLCV bars for any symbol and timeframe
- 🔴 **Real-time Streaming**: Subscribe to live market data via ZeroMQ
- 🔄 **Automatic Retry**: Built-in retry logic with exponential backoff
- 🎯 **Type Safe**: Full type hints and Pydantic models
- 🧵 **Thread Safe**: Safe for concurrent use
- 🎨 **Simple API**: Clean, intuitive interface

## Installation

```bash
pip install trading-data-client
```

## Quick Start

### Historical Data

```python
from trading_data_client import TradingDataClient
from datetime import datetime, timedelta

# Create client
client = TradingDataClient(
    server_url="http://localhost:8000",
    zmq_address="tcp://localhost:5555"
)

# Fetch historical bars
end = datetime.now()
start = end - timedelta(days=30)

bars = client.get_historical_bars(
    symbol="AAPL",
    start=start,
    end=end,
    timeframe="1d"
)

for bar in bars:
    print(f"{bar.timestamp}: O={bar.open} H={bar.high} L={bar.low} C={bar.close} V={bar.volume}")
```

### Real-time Streaming

```python
from trading_data_client import TradingDataClient

def on_bar(bar):
    print(f"New bar: {bar.symbol} @ {bar.timestamp}")
    print(f"  OHLC: {bar.open}/{bar.high}/{bar.low}/{bar.close}")
    print(f"  Volume: {bar.volume}")

# Create client
client = TradingDataClient(
    server_url="http://localhost:8000",
    zmq_address="tcp://localhost:5555"
)

# Subscribe to real-time data
subscription_id = client.subscribe(
    symbol="BTCUSD",
    timeframe="1m",
    callback=on_bar
)

# Keep running
try:
    client.run()  # Blocks until Ctrl+C
except KeyboardInterrupt:
    client.unsubscribe(subscription_id)
    client.close()
```

### Context Manager

```python
from trading_data_client import TradingDataClient
from datetime import datetime, timedelta

# Automatic resource cleanup
with TradingDataClient() as client:
    bars = client.get_historical_bars(
        symbol="TSLA",
        start=datetime.now() - timedelta(days=7),
        end=datetime.now(),
        timeframe="1h"
    )
    print(f"Fetched {len(bars)} bars")
# Client automatically closed
```

## Supported Timeframes

- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day
- `1w` - 1 week
- `1mo` - 1 month

## Configuration

### Environment Variables

```bash
export TRADING_SERVER_URL="http://localhost:8000"
export TRADING_ZMQ_ADDRESS="tcp://localhost:5555"
export TRADING_CLIENT_TIMEOUT="30"
export TRADING_CLIENT_MAX_RETRIES="3"
export TRADING_CLIENT_LOG_LEVEL="INFO"
```

### Programmatic Configuration

```python
from trading_data_client import TradingDataClient

client = TradingDataClient(
    server_url="http://your-server:8000",
    zmq_address="tcp://your-server:5555",
    timeout=60,  # seconds
    max_retries=5
)
```

## Error Handling

```python
from trading_data_client import (
    TradingDataClient,
    ConnectionError,
    ClientError,
    ServerError,
    ValidationError
)

try:
    client = TradingDataClient()
    bars = client.get_historical_bars("AAPL", start, end, "1d")
except ConnectionError as e:
    print(f"Cannot connect to server: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except ClientError as e:
    print(f"Client error (4xx): {e}")
except ServerError as e:
    print(f"Server error (5xx): {e}")
```

## Models

### Bar

```python
from trading_data_client import Bar

bar = Bar(
    symbol="AAPL",
    timestamp=datetime.now(),
    open=150.0,
    high=152.0,
    low=149.0,
    close=151.0,
    volume=1000000,
    timeframe="1d"
)
```

### Subscription

```python
from trading_data_client import Subscription

# Created automatically when subscribing
subscription = client.subscribe(
    symbol="BTCUSD",
    timeframe="1m",
    callback=my_callback
)
print(f"Subscription ID: {subscription}")
```

## Requirements

- Python 3.10+
- Trading Data Server running and accessible

## Dependencies

- `requests` - HTTP client
- `pyzmq` - ZeroMQ bindings
- `pydantic` - Data validation
- `python-dateutil` - Date parsing

## Development

### Install Development Dependencies

```bash
pip install trading-data-client[dev]
```

### Run Tests

```bash
pytest tests/
```

### Type Checking

```bash
mypy trading_data_client/
```

### Code Formatting

```bash
black trading_data_client/
```

## License

MIT License - see LICENSE file for details

## Links

- **GitHub**: https://github.com/benjamincham/moonbase_Datahub
- **Issues**: https://github.com/benjamincham/moonbase_Datahub/issues
- **PyPI**: https://pypi.org/project/trading-data-client/

## Support

For issues, questions, or contributions, please visit the GitHub repository.

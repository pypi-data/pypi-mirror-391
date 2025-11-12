# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.2.0
- Complete server-side streaming integration
- Enhanced error recovery
- Connection pooling
- Async/await support
- Additional examples

## [0.1.0] - 2024-11-11

### Added
- Initial alpha release of trading-data-client
- Historical data fetching via REST API
- Real-time streaming client (ZeroMQ)
- Pydantic models for type safety (Bar, Subscription)
- Context manager support for automatic cleanup
- Thread-safe operations
- Comprehensive error handling with custom exceptions
- Full type hints with py.typed marker
- Automatic retry logic with exponential backoff
- Configuration via environment variables
- Example scripts for common use cases
- Complete documentation and README

### Client Features
- `TradingDataClient` - Main facade class
- `get_historical_bars()` - Fetch historical OHLCV data
- `subscribe()` - Subscribe to real-time streams
- `unsubscribe()` - Unsubscribe from streams
- `run()` - Run event loop for streaming
- `close()` - Clean up resources

### Supported Timeframes
- 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo

### Dependencies
- requests >= 2.28.0
- pyzmq >= 25.0.0
- pydantic >= 2.0.0
- python-dateutil >= 2.8.0

### Known Limitations
- Streaming requires Trading Data Server with streaming enabled
- No async support yet (planned for v0.2)
- Limited connection pooling

### Notes
- This is an alpha release - API may change in future versions
- Requires Python 3.10 or higher
- Requires Trading Data Server to be running
- `close()` - Cleanup resources
- Context manager protocol (`with` statement)

### Models
- `Bar` - OHLCV bar data with validation
- `Subscription` - Internal subscription tracking
- Custom exception hierarchy

### Dependencies
- requests >= 2.28.0
- pyzmq >= 2.5.0
- pydantic >= 2.0.0
- python-dateutil >= 2.8.0

### Documentation
- README with quick start guide
- API reference documentation
- Example scripts
- Type hints for IDE support

[1.0.0]: https://github.com/example/trading-data-client/releases/tag/v1.0.0

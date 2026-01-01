# FastAPI Trading Strategy API

A comprehensive trading system built with FastAPI, PostgreSQL, and Docker that implements a Moving Average Crossover trading strategy.

## Features

- **PostgreSQL Database**: Stores OHLCV (Open, High, Low, Close, Volume) ticker data
- **FastAPI REST API**: Provides endpoints for data management and strategy analysis
- **Moving Average Crossover Strategy**: Implements buy/sell signals based on MA crossovers
- **Input Validation**: Comprehensive data validation using Pydantic models
- **Unit Testing**: 80%+ test coverage with pytest
- **Docker Support**: Fully containerized application
- **Performance Metrics**: Calculate returns, win rate, drawdown, and Sharpe ratio

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Start

```bash
# Clone the repository
git clone <your-repo-url>
cd fastapi-trading-system

# Start the application with Docker Compose
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- FastAPI application on port 8000

### 2. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 3. Load Sample Data

```bash
# Install Python dependencies (if running locally)
pip install requests

# Run the sample data loader
python sample_data.py
```

## API Endpoints

### Data Management

- `GET /data` - Fetch all ticker records
- `POST /data` - Add a single ticker record
- `POST /data/bulk` - Add multiple ticker records
- `GET /data/count` - Get total record count
- `DELETE /data/all` - Delete all records (testing only)

### Trading Strategy

- `GET /strategy/performance` - Get strategy performance metrics
  - Query parameters: `short_window` (default: 5), `long_window` (default: 20)

### System

- `GET /` - API information
- `GET /health` - Health check

## Data Schema

Each ticker record contains:

```json
{
  "datetime": "2023-01-01T09:30:00",
  "open": 100.0,
  "high": 105.0,
  "low": 99.0,
  "close": 103.0,
  "volume": 1000000
}
```

### Validation Rules

- All prices must be positive
- High ≥ Open, Close, Low
- Low ≤ Open, Close, High
- Volume must be non-negative integer

## Trading Strategy

### Moving Average Crossover

The system implements a simple but effective trading strategy:

1. **Calculate Moving Averages**: Short-term (default: 5 periods) and long-term (default: 20 periods)
2. **Generate Signals**:
   - **BUY**: When short MA crosses above long MA
   - **SELL**: When short MA crosses below long MA
   - **HOLD**: No crossover detected

3. **Performance Metrics**:
   - Total Returns (%)
   - Total Trades
   - Win Rate (%)
   - Maximum Drawdown (%)
   - Sharpe Ratio

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://trading_user:trading_password@localhost:5432/trading_db"

# Start PostgreSQL (using Docker)
docker run --name postgres-trading \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=trading_user \
  -e POSTGRES_PASSWORD=trading_password \
  -p 5432:5432 -d postgres:15

# Run the application
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_validation.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite covers:

- ✅ Input validation for all data fields
- ✅ Price relationship validation (high/low/open/close)
- ✅ Moving average calculations
- ✅ Trading signal generation
- ✅ Strategy performance metrics
- ✅ API endpoint functionality
- ✅ Database operations

Current coverage: **85%+**

## Database Schema

```sql
CREATE TABLE ticker_data (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    open NUMERIC(10,4) NOT NULL,
    high NUMERIC(10,4) NOT NULL,
    low NUMERIC(10,4) NOT NULL,
    close NUMERIC(10,4) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ticker_datetime ON ticker_data(datetime);
```

## Example Usage

### Add Data

```bash
curl -X POST "http://localhost:8000/data" \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "2023-01-01T09:30:00",
    "open": 100.0,
    "high": 105.0,
    "low": 99.0,
    "close": 103.0,
    "volume": 1000000
  }'
```

### Get Strategy Performance

```bash
curl "http://localhost:8000/strategy/performance?short_window=5&long_window=20"
```

### Response Example

```json
{
  "total_returns": 15.75,
  "total_trades": 8,
  "win_rate": 62.5,
  "max_drawdown": 5.2,
  "sharpe_ratio": 1.23,
  "signals": [
    {
      "datetime": "2023-01-01T09:30:00",
      "price": 103.0,
      "short_ma": 101.5,
      "long_ma": 100.8,
      "signal": "BUY"
    }
  ]
}
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │   Trading       │
│                 │    │   Database      │    │   Strategy      │
│ • REST API      │◄──►│                 │    │                 │
│ • Validation    │    │ • OHLCV Data    │    │ • Moving Avg    │
│ • Error Handling│    │ • Indexing      │    │ • Signals       │
└─────────────────┘    └─────────────────┘    │ • Performance   │
                                              └─────────────────┘
```

## Production Considerations

1. **Security**: Add authentication, rate limiting, and input sanitization
2. **Monitoring**: Implement logging, metrics, and health checks
3. **Scaling**: Use connection pooling, caching, and horizontal scaling
4. **Data**: Add data backup, archiving, and real-time data feeds
5. **Testing**: Expand test coverage and add integration tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
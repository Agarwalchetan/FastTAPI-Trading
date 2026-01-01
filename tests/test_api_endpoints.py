import pytest
from datetime import datetime
from fastapi.testclient import TestClient

class TestAPIEndpoints:
    
    def test_root_endpoint(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_data_empty_database(self, client: TestClient):
        response = client.get("/data")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_valid_ticker_data(self, client: TestClient):
        ticker_data = {
            "datetime": "2026-01-01T09:30:00",
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000
        }
        
        response = client.post("/data", json=ticker_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["open"] == 100.0
        assert data["high"] == 105.0
        assert data["low"] == 99.0
        assert data["close"] == 103.0
        assert data["volume"] == 1000000
        assert "id" in data
        assert "created_at" in data
    
    def test_create_invalid_ticker_data(self, client: TestClient):
        invalid_data = {
            "datetime": "2026-01-01T09:30:00",
            "open": -100.0,  # Invalid negative price
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000
        }
        
        response = client.post("/data", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_bulk_data(self, client: TestClient):
        bulk_data = [
            {
                "datetime": "2026-01-01T09:30:00",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000
            },
            {
                "datetime": "2026-01-02T09:30:00",
                "open": 103.0,
                "high": 108.0,
                "low": 102.0,
                "close": 106.0,
                "volume": 1200000
            }
        ]
        
        response = client.post("/data/bulk", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert all("id" in item for item in data)
    
    def test_get_data_after_creation(self, client: TestClient):
        # First create some data
        ticker_data = {
            "datetime": "2026-01-01T09:30:00",
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000
        }
        
        create_response = client.post("/data", json=ticker_data)
        assert create_response.status_code == 200
        
        # Then get all data
        get_response = client.get("/data")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert len(data) >= 1
        assert data[0]["open"] == 100.0
    
    def test_get_data_count(self, client: TestClient):
        response = client.get("/data/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
    
    def test_strategy_performance_no_data(self, client: TestClient):
        response = client.get("/strategy/performance")
        assert response.status_code == 404  # No data found
    
    def test_strategy_performance_with_data(self, client: TestClient):
        # Create sufficient test data
        base_date = datetime(2023, 1, 1, 9, 30)
        bulk_data = []
        
        for i in range(25):  # Create 25 days of data
            price = 100 + i * 0.5  # Gradually increasing price
            ticker_data = {
                "datetime": (base_date.replace(day=1+i)).isoformat(),
                "open": price,
                "high": price + 2,
                "low": price - 1,
                "close": price + 1,
                "volume": 1000000 + i * 10000
            }
            bulk_data.append(ticker_data)
        
        # Create the data
        create_response = client.post("/data/bulk", json=bulk_data)
        assert create_response.status_code == 200
        
        # Test strategy performance
        response = client.get("/strategy/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_returns" in data
        assert "total_trades" in data
        assert "win_rate" in data
        assert "max_drawdown" in data
        assert "sharpe_ratio" in data
        assert "signals" in data
        
        # Verify data types
        assert isinstance(data["total_returns"], (int, float))
        assert isinstance(data["total_trades"], int)
        assert isinstance(data["win_rate"], (int, float))
        assert isinstance(data["max_drawdown"], (int, float))
        assert isinstance(data["sharpe_ratio"], (int, float))
        assert isinstance(data["signals"], list)
    
    def test_strategy_performance_custom_parameters(self, client: TestClient):
        # First create some data (reuse from previous test setup)
        base_date = datetime(2023, 1, 1, 9, 30)
        bulk_data = []
        
        for i in range(25):
            price = 100 + i * 0.5
            ticker_data = {
                "datetime": (base_date.replace(day=1+i)).isoformat(),
                "open": price,
                "high": price + 2,
                "low": price - 1,
                "close": price + 1,
                "volume": 1000000 + i * 10000
            }
            bulk_data.append(ticker_data)
        
        create_response = client.post("/data/bulk", json=bulk_data)
        assert create_response.status_code == 200
        
        # Test with custom parameters
        response = client.get("/strategy/performance?short_window=3&long_window=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "signals" in data
        assert len(data["signals"]) > 0
    
    def test_delete_all_data(self, client: TestClient):
        """Test deleting all data"""
        # First create some data
        ticker_data = {
            "datetime": "2026-01-01T09:30:00",
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000
        }
        
        create_response = client.post("/data", json=ticker_data)
        assert create_response.status_code == 200
        
        # Delete all data
        delete_response = client.delete("/data/all")
        assert delete_response.status_code == 200
        
        data = delete_response.json()
        assert "message" in data
        assert "Deleted" in data["message"]
        
        # Verify data is deleted
        get_response = client.get("/data")
        assert get_response.status_code == 200
        assert get_response.json() == []
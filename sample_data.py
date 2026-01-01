#!/usr/bin/env python3


import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def create_sample_data():
    """Create sample ticker data"""
    
    # Sample data based on typical stock price movements
    base_date = datetime(2023, 1, 1, 9, 30)
    sample_data = []
    
    # Generate 50 days of sample data with realistic price movements
    base_price = 100.0
    
    for i in range(50):
        # Simulate price movement with some randomness
        price_change = (i % 5 - 2) * 0.5  # Simple oscillation
        current_price = base_price + price_change + (i * 0.1)  # Slight upward trend
        
        # Create OHLCV data
        open_price = current_price
        high_price = current_price + abs(price_change) + 1
        low_price = current_price - abs(price_change) - 0.5
        close_price = current_price + (price_change * 0.5)
        volume = 1000000 + (i * 50000)  # Increasing volume
        
        ticker_data = {
            "datetime": (base_date + timedelta(days=i)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        }
        sample_data.append(ticker_data)
    
    return sample_data

def populate_database():
    """Populate database with sample data"""
    
    print("Creating sample data...")
    sample_data = create_sample_data()
    
    print(f"Uploading {len(sample_data)} records to database...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/data/bulk",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Sample data uploaded successfully!")
            print(f"Created {len(sample_data)} ticker records")
        else:
            print(f"❌ Error uploading data: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_strategy_performance():
    """Test the strategy performance endpoint"""
    
    print("\nTesting strategy performance...")
    
    try:
        response = requests.get(f"{BASE_URL}/strategy/performance")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Strategy performance calculated successfully!")
            print(f"Total Returns: {data['total_returns']:.2f}%")
            print(f"Total Trades: {data['total_trades']}")
            print(f"Win Rate: {data['win_rate']:.2f}%")
            print(f"Max Drawdown: {data['max_drawdown']:.2f}%")
            print(f"Sharpe Ratio: {data['sharpe_ratio']:.4f}")
            print(f"Signals Generated: {len(data['signals'])}")
        else:
            print(f"❌ Error getting strategy performance: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 FastAPI Trading System - Sample Data Loader")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API health check failed")
            exit(1)
    except:
        print("❌ API is not running. Please start it first with: docker-compose up")
        exit(1)
    
    # Populate database
    populate_database()
    
    # Test strategy
    test_strategy_performance()
    
    print("\n🎉 Done! You can now:")
    print("- View API docs at: http://localhost:8000/docs")
    print("- Get all data: http://localhost:8000/data")
    print("- Get strategy performance: http://localhost:8000/strategy/performance")
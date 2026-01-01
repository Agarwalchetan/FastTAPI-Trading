#!/usr/bin/env python3

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8000"

def load_data_from_excel():
    """Read HINDALCO stock data from Excel file and prepare it for upload"""
    data_file = Path(__file__).parent / "data" / "HINDALCO_1D.xlsx"
    
    if not data_file.exists():
        raise FileNotFoundError(f"Couldn't locate {data_file.name} - please check the path")
    
    df = pd.read_excel(data_file, engine='openpyxl')
    
    # Transform each row into our API's expected format
    records = []
    for _, row in df.iterrows():
        # Excel files might use different column naming conventions
        timestamp = row.get('datetime') or row.get('date') or row.get('Datetime') or row.get('Date')
        
        if not timestamp or pd.isna(timestamp):
            continue  # skip any rows with missing dates
        
        # Normalize the timestamp format
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            timestamp = pd.to_datetime(timestamp)
        
        # Build the record with proper type conversions
        record = {
            "datetime": timestamp.isoformat(),
            "open": float(row.get('open', row.get('Open', 0))),
            "high": float(row.get('high', row.get('High', 0))),
            "low": float(row.get('low', row.get('Low', 0))),
            "close": float(row.get('close', row.get('Close', 0))),
            "volume": int(row.get('volume', row.get('Volume', 0)))
        }
        records.append(record)
    
    return records

def populate_database():
    """Load HINDALCO data from Excel and upload it to the database"""
    
    print("Loading data from Excel file...")
    data = load_data_from_excel()
    
    print(f"Found {len(data)} records. Uploading to database...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/data/bulk",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("Data uploaded successfully!")
            print(f"Created {len(data)} ticker records")
        else:
            print(f"Error uploading data: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to API")
    except Exception as e:
        print(f"Error: {e}")

def test_strategy_performance():
    """Test the strategy performance endpoint"""
    
    print("\nTesting strategy performance...")
    
    try:
        response = requests.get(f"{BASE_URL}/strategy/performance")
        
        if response.status_code == 200:
            data = response.json()
            print("Strategy performance calculated successfully!")
            print(f"Total Returns: {data['total_returns']:.2f}%")
            print(f"Total Trades: {data['total_trades']}")
            print(f"Win Rate: {data['win_rate']:.2f}%")
            print(f"Max Drawdown: {data['max_drawdown']:.2f}%")
            print(f"Sharpe Ratio: {data['sharpe_ratio']:.4f}")
            print(f"Signals Generated: {len(data['signals'])}")
        else:
            print(f"Error getting strategy performance: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to API")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("FastAPI Trading System - HINDALCO Data Loader")
    print("=" * 50)
    
    # Quick health check before we start
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("API is up and running")
        else:
            print("API responded but health check failed")
            exit(1)
    except:
        print("Couldn't reach the API")
        exit(1)
    
    populate_database()
    test_strategy_performance()
    
    print("- API docs: http://localhost:8000/docs")
    print("- All data: http://localhost:8000/data")
    print("- Strategy Performance: http://localhost:8000/strategy/performance")
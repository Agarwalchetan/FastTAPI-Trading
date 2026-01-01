import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import TickerDataCreate

class TestInputValidation:
    """Test input validation for ticker data"""
    
    def test_valid_ticker_data(self):
        """Test valid ticker data creation"""
        valid_data = {
            "datetime": datetime(2023, 1, 1, 9, 30),
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000
        }
        ticker = TickerDataCreate(**valid_data)
        assert ticker.open == 100.0
        assert ticker.high == 105.0
        assert ticker.low == 99.0
        assert ticker.close == 103.0
        assert ticker.volume == 1000000
    
    def test_negative_prices_validation(self):
        """Test that negative prices are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=-100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                volume=1000000
            )
        assert "must be positive" in str(exc_info.value)
    
    def test_negative_volume_validation(self):
        """Test that negative volume is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                volume=-1000
            )
        assert "must be non-negative" in str(exc_info.value)
    
    def test_high_less_than_low_validation(self):
        """Test that high < low is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=95.0,  # High less than low
                low=99.0,
                close=103.0,
                volume=1000000
            )
        assert "High price cannot be less than low price" in str(exc_info.value)
    
    def test_high_less_than_open_validation(self):
        """Test that high < open is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=95.0,  # High less than open
                low=90.0,
                close=93.0,
                volume=1000000
            )
        assert "High price cannot be less than open price" in str(exc_info.value)
    
    def test_high_less_than_close_validation(self):
        """Test that high < close is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=95.0,  # High less than close
                low=90.0,
                close=98.0,
                volume=1000000
            )
        assert "High price cannot be less than close price" in str(exc_info.value)
    
    def test_low_greater_than_open_validation(self):
        """Test that low > open is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=105.0,
                low=102.0,  # Low greater than open
                close=103.0,
                volume=1000000
            )
        assert "Low price cannot be greater than open price" in str(exc_info.value)
    
    def test_low_greater_than_close_validation(self):
        """Test that low > close is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=105.0,
                low=104.0,  # Low greater than close
                close=103.0,
                volume=1000000
            )
        assert "Low price cannot be greater than close price" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            TickerDataCreate(
                datetime=datetime(2023, 1, 1, 9, 30),
                open=100.0,
                high=105.0,
                # Missing low, close, volume
            )
        assert "field required" in str(exc_info.value)
    
    def test_zero_values_allowed(self):
        """Test that zero values are allowed where appropriate"""
        # Zero volume should be allowed
        ticker = TickerDataCreate(
            datetime=datetime(2023, 1, 1, 9, 30),
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            volume=0  # Zero volume allowed
        )
        assert ticker.volume == 0
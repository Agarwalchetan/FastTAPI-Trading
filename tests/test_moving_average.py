import pytest
from datetime import datetime, timedelta
from app.trading_strategy import MovingAverageCrossoverStrategy
from app.models import TickerData

class TestMovingAverageCalculations:
    
    def setup_method(self):
        self.strategy = MovingAverageCrossoverStrategy(short_window=3, long_window=5)
        
        # Create test ticker data
        base_date = datetime(2023, 1, 1, 9, 30)
        self.test_data = []
        
        # Create 10 days of test data with known price pattern
        prices = [100, 101, 102, 103, 104, 105, 104, 103, 102, 101]
        
        for i, price in enumerate(prices):
            ticker = TickerData(
                id=i+1,
                datetime=base_date + timedelta(days=i),
                open=price,
                high=price + 1,
                low=price - 1,
                close=price,
                volume=1000000,
                created_at=base_date + timedelta(days=i)
            )
            self.test_data.append(ticker)
    
    def test_moving_average_calculation(self):
        prices = [100, 101, 102, 103, 104]
        short_ma, long_ma = self.strategy.calculate_moving_averages(prices)
        
        # First 2 values should be NaN for 3-period MA
        assert str(short_ma[0]) == 'nan'
        assert str(short_ma[1]) == 'nan'
        
        # Third value should be average of first 3 prices
        expected_ma_3 = (100 + 101 + 102) / 3
        assert abs(short_ma[2] - expected_ma_3) < 0.001
        
        # Fourth value should be average of prices 1-3
        expected_ma_4 = (101 + 102 + 103) / 3
        assert abs(short_ma[3] - expected_ma_4) < 0.001
    
    def test_moving_average_with_insufficient_data(self):
        prices = [100, 101]  # Only 2 prices, need 3 for short MA
        short_ma, long_ma = self.strategy.calculate_moving_averages(prices)
        
        # All values should be NaN
        assert all(str(x) == 'nan' for x in short_ma)
        assert all(str(x) == 'nan' for x in long_ma)
    
    def test_signal_generation_insufficient_data(self):
        # Use only first 3 data points (less than long_window=5)
        insufficient_data = self.test_data[:3]
        signals = self.strategy.generate_signals(insufficient_data)
        
        # Should return empty list
        assert signals == []
    
    def test_signal_generation_with_sufficient_data(self):
        signals = self.strategy.generate_signals(self.test_data)
        
        # Should have signals for all data points
        assert len(signals) == len(self.test_data)
        
        # First few signals should be HOLD (until we have valid MAs)
        assert signals[0].signal == "HOLD"
        assert signals[1].signal == "HOLD"
        
        # Check that prices match
        for i, signal in enumerate(signals):
            assert signal.price == self.test_data[i].close
            assert signal.datetime == self.test_data[i].datetime
    
    def test_buy_signal_generation(self):
        # Create data that will generate a buy signal
        base_date = datetime(2023, 1, 1, 9, 30)
        
        # Prices that start low then trend up to create crossover
        prices = [100, 100, 100, 100, 100, 101, 102, 103, 104, 105]
        buy_signal_data = []
        
        for i, price in enumerate(prices):
            ticker = TickerData(
                id=i+1,
                datetime=base_date + timedelta(days=i),
                open=price,
                high=price + 1,
                low=price - 1,
                close=price,
                volume=1000000,
                created_at=base_date + timedelta(days=i)
            )
            buy_signal_data.append(ticker)
        
        signals = self.strategy.generate_signals(buy_signal_data)
        
        # Should have at least one BUY signal
        buy_signals = [s for s in signals if s.signal == "BUY"]
        assert len(buy_signals) > 0
    
    def test_sell_signal_generation(self):
        # Create data that will generate a sell signal
        base_date = datetime(2023, 1, 1, 9, 30)
        
        # Prices that start high then trend down to create crossover
        prices = [105, 105, 105, 105, 105, 104, 103, 102, 101, 100]
        sell_signal_data = []
        
        for i, price in enumerate(prices):
            ticker = TickerData(
                id=i+1,
                datetime=base_date + timedelta(days=i),
                open=price,
                high=price + 1,
                low=price - 1,
                close=price,
                volume=1000000,
                created_at=base_date + timedelta(days=i)
            )
            sell_signal_data.append(ticker)
        
        signals = self.strategy.generate_signals(sell_signal_data)
        
        # Should have at least one SELL signal
        sell_signals = [s for s in signals if s.signal == "SELL"]
        assert len(sell_signals) > 0
    
    def test_performance_calculation_no_signals(self):
        empty_signals = []
        performance = self.strategy.calculate_performance(empty_signals)
        
        assert performance.total_returns == 0.0
        assert performance.total_trades == 0
        assert performance.win_rate == 0.0
        assert performance.max_drawdown == 0.0
        assert performance.sharpe_ratio == 0.0
    
    def test_performance_calculation_with_signals(self):
        signals = self.strategy.generate_signals(self.test_data)
        performance = self.strategy.calculate_performance(signals)
        
        # Performance should be calculated
        assert isinstance(performance.total_returns, float)
        assert isinstance(performance.total_trades, int)
        assert isinstance(performance.win_rate, float)
        assert isinstance(performance.max_drawdown, float)
        assert isinstance(performance.sharpe_ratio, float)
        
        # Win rate should be between 0 and 100
        assert 0 <= performance.win_rate <= 100
        
        # Max drawdown should be non-negative
        assert performance.max_drawdown >= 0
    
    def test_moving_average_edge_cases(self):
        # Test with single price
        single_price = [100]
        short_ma, long_ma = self.strategy.calculate_moving_averages(single_price)
        assert str(short_ma[0]) == 'nan'
        assert str(long_ma[0]) == 'nan'
        
        # Test with identical prices
        identical_prices = [100, 100, 100, 100, 100]
        short_ma, long_ma = self.strategy.calculate_moving_averages(identical_prices)
        
        # MA of identical values should equal the value
        assert short_ma[2] == 100.0  # First valid 3-period MA
        assert long_ma[4] == 100.0   # First valid 5-period MA
import pandas as pd
import numpy as np
from typing import List, Tuple
from app.schemas import MovingAverageSignal, StrategyPerformance
from app.models import TickerData

class MovingAverageCrossoverStrategy:    
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_moving_averages(self, prices: List[float]) -> Tuple[List[float], List[float]]:
        df = pd.DataFrame({'price': prices})
        
        # Calculate moving averages
        df['short_ma'] = df['price'].rolling(window=self.short_window).mean()
        df['long_ma'] = df['price'].rolling(window=self.long_window).mean()
        
        return df['short_ma'].tolist(), df['long_ma'].tolist()
    
    def generate_signals(self, ticker_data: List[TickerData]) -> List[MovingAverageSignal]:
        if len(ticker_data) < self.long_window:
            return []
        
        # Extract prices and dates
        prices = [float(data.close) for data in ticker_data]
        dates = [data.datetime for data in ticker_data]
        
        # Calculate moving averages
        short_ma, long_ma = self.calculate_moving_averages(prices)
        
        signals = []
        for i, (date, price, short, long) in enumerate(zip(dates, prices, short_ma, long_ma)):
            signal_type = "HOLD"
            
            # Generate signals only when we have valid MA values
            if i > 0 and not pd.isna(short) and not pd.isna(long):
                prev_short = short_ma[i-1]
                prev_long = long_ma[i-1]
                
                # Buy signal: short MA crosses above long MA
                if short > long and prev_short <= prev_long:
                    signal_type = "BUY"
                # Sell signal: short MA crosses below long MA
                elif short < long and prev_short >= prev_long:
                    signal_type = "SELL"
            
            signals.append(MovingAverageSignal(
                datetime=date,
                price=price,
                short_ma=short if not pd.isna(short) else None,
                long_ma=long if not pd.isna(long) else None,
                signal=signal_type
            ))
        
        return signals
    
    def calculate_performance(self, signals: List[MovingAverageSignal]) -> StrategyPerformance:
        if not signals:
            return StrategyPerformance(
                total_returns=0.0,
                total_trades=0,
                win_rate=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                signals=[]
            )
        
        position = 0  # 0 = no position, 1 = long
        buy_price = 0.0
        total_returns = 0.0
        trades = 0
        winning_trades = 0
        portfolio_values = [10000.0]  # Starting with $10,000
        
        for signal in signals:
            if signal.signal == "BUY" and position == 0:
                position = 1
                buy_price = signal.price
                trades += 1
            elif signal.signal == "SELL" and position == 1:
                return_pct = (signal.price - buy_price) / buy_price
                total_returns += return_pct
                if return_pct > 0:
                    winning_trades += 1
                position = 0
                
                # Update portfolio value
                new_value = portfolio_values[-1] * (1 + return_pct)
                portfolio_values.append(new_value)
        
        # Calculate metrics
        win_rate = (winning_trades / trades * 100) if trades > 0 else 0.0
        
        # Calculate maximum drawdown
        max_drawdown = 0.0
        peak = portfolio_values[0]
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate Sharpe ratio (simplified)
        if len(portfolio_values) > 1:
            returns = []
            for i in range(1, len(portfolio_values)):
                ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                returns.append(ret)
            
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        return StrategyPerformance(
            total_returns=total_returns * 100,  # Convert to percentage
            total_trades=trades,
            win_rate=win_rate,
            max_drawdown=max_drawdown * 100,  # Convert to percentage
            sharpe_ratio=sharpe_ratio,
            signals=signals
        )
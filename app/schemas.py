from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class TickerDataBase(BaseModel):
    datetime: datetime
    open: float = Field(..., gt=0, description="Opening price must be positive")
    high: float = Field(..., gt=0, description="High price must be positive")
    low: float = Field(..., gt=0, description="Low price must be positive")
    close: float = Field(..., gt=0, description="Closing price must be positive")
    volume: int = Field(..., ge=0, description="Volume must be non-negative")

    @validator('high')
    def high_must_be_highest(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError('High price cannot be less than low price')
        if 'open' in values and v < values['open']:
            raise ValueError('High price cannot be less than open price')
        if 'close' in values and v < values['close']:
            raise ValueError('High price cannot be less than close price')
        return v

    @validator('low')
    def low_must_be_lowest(cls, v, values):
        if 'open' in values and v > values['open']:
            raise ValueError('Low price cannot be greater than open price')
        if 'close' in values and v > values['close']:
            raise ValueError('Low price cannot be greater than close price')
        return v

class TickerDataCreate(TickerDataBase):
    pass

class TickerDataResponse(TickerDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MovingAverageSignal(BaseModel):
    datetime: datetime
    price: float
    short_ma: Optional[float]
    long_ma: Optional[float]
    signal: str  # 'BUY', 'SELL', 'HOLD'

class StrategyPerformance(BaseModel):
    total_returns: float
    total_trades: int
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    signals: List[MovingAverageSignal]

class ValidationErrorDetail(BaseModel):
    field: str
    message: str

class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorDetail]
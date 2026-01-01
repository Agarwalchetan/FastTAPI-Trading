from sqlalchemy import Column, Integer, String, DateTime, Numeric, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class TickerData(Base):
    __tablename__ = "ticker_data"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, nullable=False, index=True)
    open = Column(Numeric(10, 4), nullable=False)
    high = Column(Numeric(10, 4), nullable=False)
    low = Column(Numeric(10, 4), nullable=False)
    close = Column(Numeric(10, 4), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<TickerData(datetime={self.datetime}, close={self.close})>"
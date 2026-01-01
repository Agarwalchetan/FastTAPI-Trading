from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models, schemas
from typing import List, Optional
from datetime import datetime

def get_ticker_data(db: Session, skip: int = 0, limit: int = 1000) -> List[models.TickerData]:
    """Get all ticker data with pagination"""
    return db.query(models.TickerData).order_by(models.TickerData.datetime).offset(skip).limit(limit).all()

def get_ticker_data_by_date_range(
    db: Session, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> List[models.TickerData]:
    query = db.query(models.TickerData)
    
    if start_date:
        query = query.filter(models.TickerData.datetime >= start_date)
    if end_date:
        query = query.filter(models.TickerData.datetime <= end_date)
    
    return query.order_by(models.TickerData.datetime).all()

def create_ticker_data(db: Session, ticker_data: schemas.TickerDataCreate) -> models.TickerData:
    db_ticker = models.TickerData(**ticker_data.dict())
    db.add(db_ticker)
    db.commit()
    db.refresh(db_ticker)
    return db_ticker

def create_multiple_ticker_data(db: Session, ticker_data_list: List[schemas.TickerDataCreate]) -> List[models.TickerData]:
    db_tickers = [models.TickerData(**ticker_data.dict()) for ticker_data in ticker_data_list]
    db.add_all(db_tickers)
    db.commit()
    for db_ticker in db_tickers:
        db.refresh(db_ticker)
    return db_tickers

def get_ticker_count(db: Session) -> int:
    return db.query(models.TickerData).count()

def delete_all_ticker_data(db: Session) -> int:
    count = db.query(models.TickerData).count()
    db.query(models.TickerData).delete()
    db.commit()
    return count
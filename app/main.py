from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app import crud, models, schemas
from app.database import SessionLocal, engine, get_db
from app.trading_strategy import MovingAverageCrossoverStrategy

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Strategy API",
    description="A FastAPI application for managing ticker data and trading strategies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Trading Strategy API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/data", response_model=List[schemas.TickerDataResponse])
async def get_all_data(
    skip: int = 0, 
    limit: int = 1000, 
    db: Session = Depends(get_db)
):
    try:
        ticker_data = crud.get_ticker_data(db, skip=skip, limit=limit)
        return ticker_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}"
        )

@app.post("/data", response_model=schemas.TickerDataResponse)
async def create_data(
    ticker_data: schemas.TickerDataCreate, 
    db: Session = Depends(get_db)
):
    try:
        return crud.create_ticker_data(db=db, ticker_data=ticker_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating data: {str(e)}"
        )

@app.post("/data/bulk", response_model=List[schemas.TickerDataResponse])
async def create_bulk_data(
    ticker_data_list: List[schemas.TickerDataCreate], 
    db: Session = Depends(get_db)
):
    try:
        return crud.create_multiple_ticker_data(db=db, ticker_data_list=ticker_data_list)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating bulk data: {str(e)}"
        )

@app.get("/data/count")
async def get_data_count(db: Session = Depends(get_db)):
    try:
        count = crud.get_ticker_count(db)
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting count: {str(e)}"
        )

@app.get("/strategy/performance", response_model=schemas.StrategyPerformance)
async def get_strategy_performance(
    short_window: int = 5,
    long_window: int = 20,
    db: Session = Depends(get_db)
):
    try:
        # Get all ticker data
        ticker_data = crud.get_ticker_data(db, limit=10000)
        
        if not ticker_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ticker data found in database"
            )
        
        # Initialize strategy
        strategy = MovingAverageCrossoverStrategy(
            short_window=short_window, 
            long_window=long_window
        )
        
        # Generate signals
        signals = strategy.generate_signals(ticker_data)
        
        # Calculate performance
        performance = strategy.calculate_performance(signals)
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating strategy performance: {str(e)}"
        )

@app.delete("/data/all")
async def delete_all_data(db: Session = Depends(get_db)):
    try:
        count = crud.delete_all_ticker_data(db)
        return {"message": f"Deleted {count} records"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting data: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
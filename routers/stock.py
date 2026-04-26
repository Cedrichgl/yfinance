from datetime import date
from fastapi import APIRouter, HTTPException, Depends,Query
from typing import List
from schemas.stock import StockResponse
from database import get_db
from sqlalchemy.orm import Session
from models.stock import Stock

router = APIRouter()
@router.get("/")
async def index():
    return {"message": "Hello World"}



@router.get("/stock", response_model=List[StockResponse])
async def get_all_stocks(skip:int = 0, limit:int = 100, db: Session = Depends(get_db)):
    data = db.query(Stock).offset(skip).limit(limit).all()
    return data

@router.get("/stocks/{ticker}", response_model=list[StockResponse])
def get_stock(ticker: str, db: Session = Depends(get_db)):
    return db.query(Stock).filter(Stock.ticker == ticker).all()

@router.get("/stocks/{ticker}/latest", response_model=StockResponse)
def get_latest(ticker: str, db: Session = Depends(get_db)):
    return (
        db.query(Stock)
        .filter(Stock.ticker == ticker.upper())
        .order_by(Stock.date.desc())
        .first()
    )

@router.get("/stocks/{ticker}/history", response_model=list[StockResponse])
def get_history(ticker: str,start: date = Query(default=None),end: date = Query(default=None),db: Session = Depends(get_db)):
    query = db.query(Stock).filter(Stock.ticker == ticker.upper())
    if start:
        query = query.filter(Stock.date >= start)
    if end:
        query = query.filter(Stock.date <= end)
    return query.order_by(Stock.date.asc()).all()


@router.get("/stocks/{ticker}/stats")
def get_stats(ticker: str, db: Session = Depends(get_db)):
    rows = (db.query(Stock).filter(Stock.ticker == ticker.upper()).order_by(Stock.date.asc()).all())
    closes = [row.close for row in rows]
    volumes = [row.volume for row in rows]
    returns = [
        (closes[i] - closes[i - 1]) / closes[i - 1] * 100
        for i in range(1, len(closes))
    ]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = variance ** 0.5
    return {
        "ticker": ticker.upper(),
        "close_min": round(min(closes), 2),
        "close_max": round(max(closes), 2),
        "close_mean": round(sum(closes) / len(closes), 2),
        "volume_mean": round(sum(volumes) / len(volumes)),
        "volatility": round(volatility, 4),
        "best_day": round(max(returns), 2),
        "worst_day": round(min(returns), 2),
    }

@router.get("/stocks/compare")
def compare_stocks(
    tickers: str = Query(..., description="Ex: AAPL,MSFT,GOOGL"),
    start: date = Query(default=None),
    end: date = Query(default=None),
    db: Session = Depends(get_db)
):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    query = db.query(Stock).filter(Stock.ticker.in_(ticker_list))

    if start:
        query = query.filter(Stock.date >= start)
    if end:
        query = query.filter(Stock.date <= end)

    rows = query.order_by(Stock.ticker, Stock.date.asc()).all()

    result = {}
    for row in rows:
        if row.ticker not in result:
            result[row.ticker] = {"dates": [], "values": [], "base": row.close}

        base = result[row.ticker]["base"]
        normalized = (row.close / base) * 100

        result[row.ticker]["dates"].append(str(row.date))
        result[row.ticker]["values"].append(round(normalized, 2))

    return result
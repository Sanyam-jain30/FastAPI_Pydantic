import uvicorn as uvicorn
from fastapi import FastAPI, Depends, Request
from typing import Optional
from sqlalchemy.orm import Session
import datetime as dt
from sqlalchemy import or_, and_
import schema
from database import SessionLocal, engine
import model
from model import Trade
import random


model.Base.metadata.create_all(bind=engine)
app = FastAPI()

ROWS_PER_PAGE = 5

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Posting trade
@app.post("/trade/")
async def create_trade(trade: schema.Trade, request: Request, db: Session = Depends(get_database_session)):
    trade_id = "TRA" + str(random.randint(1000,9999))
    db_trade = model.Trade(asset_class= trade.asset_class,
                            counterparty = trade.counterparty,
                            instrument_id = trade.instrument_id,
                            instrument_name = trade.instrument_name,
                            trade_date_time = trade.trade_date_time,
                            buySellIndicator = trade.trade_details.buySellIndicator,
                            price = trade.trade_details.price,
                            quantity = trade.trade_details.quantity,
                            trade_id = trade_id,
                            trader = trade.trader)
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

# Listing trade
@app.get("/trades")
async def listing_trades(request: Request, db: Session = Depends(get_database_session), sorting: Optional[str] = None, page: Optional[str] = None):
    item = db.query(Trade).all()
    if sorting is not None:
        if (sorting.lower() == "asc" or sorting.lower() == "ascending"):
            item = db.query(Trade).order_by(Trade.trade_id.asc()).all()
        elif (sorting.lower() == "desc" or sorting.lower() == "descending"):
            item = db.query(Trade).order_by(Trade.trade_id.desc()).all()
    if page is not None and page != 0:
        page = int(page)
        if page == 1:
            item = item[0:ROWS_PER_PAGE]
        else:
            item = item[((page-1)*ROWS_PER_PAGE-1):(min((page*ROWS_PER_PAGE), ROWS_PER_PAGE))]
    return item

# Single trade
@app.get("/trade/{trade_id}")
async def single_trade(trade_id: str, request: Request, db: Session = Depends(get_database_session)):
    item = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    return item

# Searching Trades
@app.get("/trade")
async def searching_trades(search: str, request: Request, db: Session = Depends(get_database_session)):
    item = db.query(Trade).filter(
        or_(
            Trade.counterparty.ilike(f'%{search}%'),
            Trade.instrument_id.ilike(f'%{search}%'),
            Trade.instrument_name.ilike(f'%{search}%'),
            Trade.trader.ilike(f'%{search}%')
        )
    ).all()
    return item

# Advance Filtering
@app.get("/trade-ad")
async def advance_filtering(request: Request, db: Session = Depends(get_database_session), assetClass: Optional[str] = None, end: Optional[dt.date] = None, maxPrice: Optional[float] = None, minPrice: Optional[float] = None, start: Optional[dt.date] = None, tradeType: Optional[str] = None):
    total = db.query(Trade).all()
    if assetClass is not None:
        asset = db.query(Trade).filter(Trade.asset_class.ilike(f'%{assetClass}%')).all()
        total = list(set(total).intersection(asset))
    if start is not None and end is not None:
        dates = db.query(Trade).filter(
            and_(
                Trade.trade_date_time >= start,
                Trade.trade_date_time <= end
            )
        ).all()
    elif start is None:
        dates = db.query(Trade).filter(
            and_(
                Trade.trade_date_time >= end
            )
        ).all()
    elif end is None:
        dates = db.query(Trade).filter(
            and_(
                Trade.trade_date_time >= start
            )
        ).all()
    total = list(set(total).intersection(dates))
    if minPrice is not None and maxPrice is not None:
        price = db.query(Trade).filter(
            and_(
                Trade.price >= minPrice,
                Trade.price <= maxPrice
            )
        ).all()
    elif minPrice is None:
        price = db.query(Trade).filter(
            and_(
                Trade.price >= start
            )
        ).all()
    elif maxPrice is None:
        price = db.query(Trade).filter(
            and_(
                Trade.price >= end
            )
        ).all()
    total = list(set(total).intersection(price))
    if tradeType is not None:
        type = db.query(Trade).filter(Trade.buySellIndicator == tradeType).all()
        total = list(set(total).intersection(type))
    return total

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

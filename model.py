from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Float
from database import Base

class Trade(Base):
    __tablename__ = "Trade"
    asset_class = Column(String(100), nullable=True)
    counterparty = Column(String(50), nullable=True)
    instrument_id = Column(String(50))
    instrument_name = Column(String(50))
    trade_date_time = Column(DateTime())
    buySellIndicator = Column(String(4))
    price = Column(Float)
    quantity = Column(Integer)
    trade_id = Column(String(7), nullable=True, primary_key=True)
    trader = Column(String(50))
from sqlalchemy import Column, Integer, String, Float
from app.database import Base
from datetime import datetime

class Portfolio(Base):
    __tablename__ = "portfolio"
	
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    buy_price = Column(Float)
    quantity = Column(Integer)
    buy_date = Column(String, default=str(datetime.now()))
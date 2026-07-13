from sqlalchemy import Column, Integer, String, Numeric, DateTime

from backend.config.database import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    price = Column(Numeric(18, 6), nullable=False)
    source = Column(String(120), nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

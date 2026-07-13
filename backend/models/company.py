from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from backend.config.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(120))
    sub_sector = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

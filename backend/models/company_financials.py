from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from backend.config.database import Base


class CompanyFinancials(Base):
    __tablename__ = "company_financials"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(20), nullable=False)
    roe = Column(Numeric(10, 4))
    roic = Column(Numeric(10, 4))
    debt = Column(Numeric(18, 2))
    cash = Column(Numeric(18, 2))
    dividend_yield = Column(Numeric(10, 4))
    source = Column(String(120), nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint("company_id", "period"),)

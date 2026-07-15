from sqlalchemy import (
    Boolean,
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
    # Bkz. database/migrations/0002_add_financials_source_tracking.sql —
    # atlas_score güven bandını besler (ai/analyzers/company_analyzer.py).
    source_count = Column(Integer, nullable=False, default=1)
    has_conflicting_data = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("company_id", "period"),)

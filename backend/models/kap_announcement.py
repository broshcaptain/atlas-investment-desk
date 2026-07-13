from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from backend.config.database import Base


class KapAnnouncement(Base):
    __tablename__ = "kap_announcements"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    announced_at = Column(DateTime(timezone=True), nullable=False)
    category = Column(String(120))
    content = Column(Text, nullable=False)
    ai_summary = Column(Text)
    source_url = Column(Text)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

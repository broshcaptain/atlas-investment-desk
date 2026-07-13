from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.company_financials import CompanyFinancials
from backend.models.kap_announcement import KapAnnouncement


def get_company_by_code(db: Session, code: str) -> Company | None:
    return db.query(Company).filter(Company.code == code).first()


def get_latest_financials(db: Session, company_id: int) -> CompanyFinancials | None:
    return (
        db.query(CompanyFinancials)
        .filter(CompanyFinancials.company_id == company_id)
        .order_by(CompanyFinancials.fetched_at.desc())
        .first()
    )


def get_recent_announcements(db: Session, company_id: int, limit: int = 10) -> list[KapAnnouncement]:
    return (
        db.query(KapAnnouncement)
        .filter(KapAnnouncement.company_id == company_id)
        .order_by(KapAnnouncement.announced_at.desc())
        .limit(limit)
        .all()
    )

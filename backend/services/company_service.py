from sqlalchemy.orm import Session

from ai.analyzers.company_analyzer import analyze_company
from backend.models.company_financials import CompanyFinancials
from backend.models.kap_announcement import KapAnnouncement
from backend.repositories.company_repository import (
    get_company_by_code,
    get_latest_financials,
    get_recent_announcements,
)

ANNOUNCEMENTS_LIMIT = 10


def get_company_overview(db: Session, code: str) -> dict | None:
    company = get_company_by_code(db, code)
    if not company:
        return None

    financials = get_latest_financials(db, company.id)
    announcements = get_recent_announcements(db, company.id, limit=ANNOUNCEMENTS_LIMIT)
    serialized_financials = _serialize_financials(financials)

    return {
        "company": {
            "code": company.code,
            "name": company.name,
            "sector": company.sector,
            "sub_sector": company.sub_sector,
        },
        "financials": serialized_financials,
        "atlas_score": analyze_company(
            serialized_financials,
            company_code=company.code,
            source_count=serialized_financials.get("source_count", 1),
            has_conflicting_data=serialized_financials.get("has_conflicting_data", False),
        ),
        "recent_announcements": [_serialize_announcement(a) for a in announcements],
    }


def _serialize_financials(financials: CompanyFinancials | None) -> dict:
    # Zorunlu kural: veri eksikse sahte skor üretme, "yetersiz veri" dön.
    if not financials:
        return {"status": "yetersiz veri"}

    return {
        "period": financials.period,
        "roe": _to_float(financials.roe),
        "roic": _to_float(financials.roic),
        "debt": _to_float(financials.debt),
        "cash": _to_float(financials.cash),
        "dividend_yield": _to_float(financials.dividend_yield),
        "source": financials.source,
        "fetched_at": financials.fetched_at,
        "source_count": financials.source_count,
        "has_conflicting_data": financials.has_conflicting_data,
    }


def _serialize_announcement(announcement: KapAnnouncement) -> dict:
    return {
        "announced_at": announcement.announced_at,
        "category": announcement.category,
        "content": announcement.content,
        "ai_summary": announcement.ai_summary,
        "source_url": announcement.source_url,
        "fetched_at": announcement.fetched_at,
    }


def _to_float(value):
    return float(value) if value is not None else None

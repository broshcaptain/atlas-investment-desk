from sqlalchemy.orm import Session

from ai.summaries.morning_briefing import generate_morning_briefing
from backend.repositories.market_data_repository import get_latest_prices
from backend.services.company_service import get_company_overview

BRIEFING_PILOT_COMPANY_CODE = "TUPRS"


def get_market_summary(db: Session) -> dict:
    rows = get_latest_prices(db)
    items = [
        {
            "symbol": row.symbol,
            "price": float(row.price),
            "source": row.source,
            "fetched_at": row.fetched_at,
        }
        for row in rows
    ]

    market_summary = {"items": items}
    company_overview = get_company_overview(db, BRIEFING_PILOT_COMPANY_CODE)
    briefing = generate_morning_briefing(market_summary, company_overview)

    return {"items": items, "briefing": briefing}

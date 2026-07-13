from sqlalchemy.orm import Session

from backend.repositories.market_data_repository import get_latest_prices


def get_market_summary(db: Session) -> dict:
    rows = get_latest_prices(db)

    return {
        "items": [
            {
                "symbol": row.symbol,
                "price": float(row.price),
                "source": row.source,
                "fetched_at": row.fetched_at,
            }
            for row in rows
        ]
    }

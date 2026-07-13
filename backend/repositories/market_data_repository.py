from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.market_data import MarketData


def get_latest_prices(db: Session) -> list[MarketData]:
    """Her sembol için en son fetched_at'e sahip market_data satırını döner."""
    latest_per_symbol = (
        db.query(
            MarketData.symbol,
            func.max(MarketData.fetched_at).label("max_fetched_at"),
        )
        .group_by(MarketData.symbol)
        .subquery()
    )

    return (
        db.query(MarketData)
        .join(
            latest_per_symbol,
            (MarketData.symbol == latest_per_symbol.c.symbol)
            & (MarketData.fetched_at == latest_per_symbol.c.max_fetched_at),
        )
        .order_by(MarketData.symbol)
        .all()
    )

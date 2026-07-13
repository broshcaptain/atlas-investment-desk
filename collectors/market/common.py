from datetime import datetime, timezone

import yfinance as yf

from backend.config.database import SessionLocal
from backend.models.market_data import MarketData

# 1 troy ons = bu kadar gram (gram altın türetmesinde kullanılır).
GRAM_PER_TROY_OUNCE = 31.1034768


def fetch_price(ticker: str) -> float:
    """yfinance üzerinden son kapanış fiyatını çeker."""
    data = yf.Ticker(ticker).history(period="1d")

    if data.empty:
        raise RuntimeError(f"{ticker} için veri alınamadı (boş sonuç).")

    return float(data["Close"].iloc[-1])


def save_market_data(symbol: str, price: float, source: str) -> MarketData:
    """market_data tablosuna fetched_at damgasıyla bir satır yazar."""
    fetched_at = datetime.now(timezone.utc)

    db = SessionLocal()
    try:
        row = MarketData(
            symbol=symbol,
            price=price,
            source=source,
            fetched_at=fetched_at,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()

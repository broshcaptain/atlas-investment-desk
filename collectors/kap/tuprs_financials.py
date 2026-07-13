from datetime import datetime, timezone

import yfinance as yf

from backend.config.database import SessionLocal
from backend.models.company_financials import CompanyFinancials
from collectors.kap.common import get_or_create_company

TICKER = "TUPRS"
COMPANY_NAME = "TÜPRAŞ-Türkiye Petrol Rafinerileri A.Ş."
YF_TICKER = "TUPRS.IS"


def _latest_period(balance_sheet) -> str:
    latest_date = balance_sheet.columns[0]
    return str(latest_date.date()) if hasattr(latest_date, "date") else str(latest_date)


def collect() -> dict:
    company = get_or_create_company(TICKER, COMPANY_NAME, sector="Enerji")

    ticker = yf.Ticker(YF_TICKER)
    info = ticker.info
    balance_sheet = ticker.balance_sheet
    financials = ticker.financials

    roe = info.get("returnOnEquity")
    debt = info.get("totalDebt")
    cash = info.get("totalCash")
    dividend_yield = info.get("dividendYield")

    source_note = f"yfinance:{YF_TICKER} (.info)"
    roic = None
    try:
        ebit = financials.loc["EBIT"].iloc[0]
        tax_rate = financials.loc["Tax Rate For Calcs"].iloc[0]
        equity = balance_sheet.loc["Stockholders Equity"].iloc[0]
        invested_capital = (debt or 0) + equity - (cash or 0)

        if invested_capital:
            roic = float(ebit * (1 - tax_rate) / invested_capital)
            source_note += " + derived ROIC: EBIT*(1-tax_rate)/(Debt+Equity-Cash)"
    except (KeyError, IndexError, TypeError):
        roic = None  # yetersiz veri — sahte skor üretilmez

    period = _latest_period(balance_sheet)
    fetched_at = datetime.now(timezone.utc)

    db = SessionLocal()
    try:
        existing = (
            db.query(CompanyFinancials)
            .filter(
                CompanyFinancials.company_id == company.id,
                CompanyFinancials.period == period,
            )
            .first()
        )

        if existing:
            existing.roe = roe
            existing.roic = roic
            existing.debt = debt
            existing.cash = cash
            existing.dividend_yield = dividend_yield
            existing.source = source_note
            existing.fetched_at = fetched_at
        else:
            db.add(
                CompanyFinancials(
                    company_id=company.id,
                    period=period,
                    roe=roe,
                    roic=roic,
                    debt=debt,
                    cash=cash,
                    dividend_yield=dividend_yield,
                    source=source_note,
                    fetched_at=fetched_at,
                )
            )
        db.commit()
    finally:
        db.close()

    return {
        "period": period,
        "roe": roe,
        "roic": roic,
        "debt": debt,
        "cash": cash,
        "dividend_yield": dividend_yield,
    }


if __name__ == "__main__":
    result = collect()
    print(f"{TICKER} company_financials güncellendi: {result}")

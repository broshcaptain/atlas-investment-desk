"""TUPRS finansal verisini İş Yatırım'dan (isyatirim.com.tr) çekip, mevcut
yfinance kaynaklı `company_financials` satırıyla çapraz kontrol eder.

Bu collector `collectors/kap/tuprs_financials.py`'den (yfinance, birincil
kaynak) SONRA çalıştırılmalıdır — aynı `company_id + period` satırını arar,
bulamazsa hata verir. `roe/roic/debt/cash` sütunlarına dokunmaz (birincil
kaynağın sayıları görüntülenmeye devam eder); sadece `source_count`'u 2'ye
çıkarır ve iki kaynağın ROE/ROIC/borç/nakit değerleri arasında
`CONFLICT_THRESHOLD`'u aşan bir bağıl fark varsa `has_conflicting_data`'yı
işaretler. Bkz. database/migrations/0002_add_financials_source_tracking.sql.

Endpoint, resmi/dokümante bir İş Yatırım API'si değil — açık kaynak
`isyatirimhisse` (PyPI) paketinden doğrulanmış, kimlik doğrulama gerektirmeyen
genel bir uç nokta. TUPRS için sadece `financialGroup=XI_29` veri döndürüyor
(canlı test edildi) — bu İş Yatırım'ın dahili kategori etiketi, gerçek
muhasebe standardını yansıtmıyor.
"""

from datetime import datetime, timezone
from typing import Optional

import requests

from backend.config.database import SessionLocal
from backend.models.company_financials import CompanyFinancials
from collectors.kap.common import get_or_create_company

TICKER = "TUPRS"
COMPANY_NAME = "TÜPRAŞ-Türkiye Petrol Rafinerileri A.Ş."
IS_YATIRIM_CODE = "TUPRS"

MALI_TABLO_URL = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
FINANCIAL_GROUP = "XI_29"  # TUPRS için veri döndüren tek grup (canlı test edildi)

# Bilanço/gelir tablosu satır kodları (canlı yanıtla doğrulandı).
ITEM_CASH = "1AA"  # Nakit ve Nakit Benzerleri
ITEM_DEBT_SHORT = "2AA"  # Kısa Vadeli Finansal Borçlar
ITEM_DEBT_LONG = "2BA"  # Uzun Vadeli Finansal Borçlar
ITEM_EQUITY = "2N"  # Özkaynaklar (toplam)
ITEM_NET_INCOME = "3L"  # DÖNEM KARI (ZARARI)
ITEM_EBIT = "3DF"  # FAALİYET KARI (ZARARI)
ITEM_PRETAX_INCOME = "3I"  # Sürdürülen Faaliyetler Vergi Öncesi Karı
ITEM_TAX_EXPENSE = "3IA"  # Sürdürülen Faaliyetler Vergi Geliri (Gideri)

CONFLICT_THRESHOLD = 0.15  # bağıl fark bu değeri aşarsa has_conflicting_data=True


def _fetch_mali_tablo(year: int, prior_year: int) -> dict:
    params = {
        "companyCode": IS_YATIRIM_CODE,
        "exchange": "TRY",
        "financialGroup": FINANCIAL_GROUP,
        "year1": year, "period1": 12,
        "year2": prior_year, "period2": 12,
        "year3": prior_year, "period3": 9,
        "year4": prior_year, "period4": 6,
    }
    resp = requests.get(MALI_TABLO_URL, params=params, timeout=15)
    resp.raise_for_status()
    rows = resp.json().get("value") or []
    return {row["itemCode"].strip(): row for row in rows}


def _item_value(items: dict, code: str) -> Optional[float]:
    row = items.get(code)
    if not row or row.get("value1") in (None, ""):
        return None
    return float(row["value1"])


def _compute_financials(items: dict) -> dict:
    cash = _item_value(items, ITEM_CASH)
    debt_short = _item_value(items, ITEM_DEBT_SHORT) or 0.0
    debt_long = _item_value(items, ITEM_DEBT_LONG) or 0.0
    debt = debt_short + debt_long
    equity = _item_value(items, ITEM_EQUITY)
    net_income = _item_value(items, ITEM_NET_INCOME)
    ebit = _item_value(items, ITEM_EBIT)
    pretax_income = _item_value(items, ITEM_PRETAX_INCOME)
    tax_expense = _item_value(items, ITEM_TAX_EXPENSE)

    roe = (net_income / equity) if net_income is not None and equity else None

    roic = None
    if ebit is not None and pretax_income and tax_expense is not None and equity is not None and cash is not None:
        tax_rate = abs(tax_expense) / pretax_income
        invested_capital = debt + equity - cash
        if invested_capital:
            roic = ebit * (1 - tax_rate) / invested_capital

    return {"cash": cash, "debt": debt, "roe": roe, "roic": roic}


def _relative_diff(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or a == 0:
        return None
    return abs(a - b) / abs(a)


def _fmt_pct(value: Optional[float]) -> str:
    return f"%{value * 100:.1f}" if value is not None else "—"


def _fmt_try(value: Optional[float]) -> str:
    return f"{value:,.0f} ₺".replace(",", ".") if value is not None else "—"


FIELD_LABELS = {"roe": "ROE", "roic": "ROIC", "debt": "Borç", "cash": "Nakit"}


def _build_comparison_note(computed: dict, existing: CompanyFinancials, conflicting_fields: list) -> str:
    """`source` alanına eklenen, kullanıcının doğrudan okuyabileceği bir
    karşılaştırma notu üretir — ham float/pseudocode yerine biçimlendirilmiş
    yüzde/TL değerleri, iki kaynağın yan yana gösterimi."""
    existing_roe = float(existing.roe) if existing.roe is not None else None
    existing_roic = float(existing.roic) if existing.roic is not None else None
    existing_debt = float(existing.debt) if existing.debt is not None else None
    existing_cash = float(existing.cash) if existing.cash is not None else None

    note = (
        "çapraz kontrol (isyatirim.com.tr vs yfinance): "
        f"ROE {_fmt_pct(computed['roe'])} vs {_fmt_pct(existing_roe)}, "
        f"ROIC {_fmt_pct(computed['roic'])} vs {_fmt_pct(existing_roic)}, "
        f"Borç {_fmt_try(computed['debt'])} vs {_fmt_try(existing_debt)}, "
        f"Nakit {_fmt_try(computed['cash'])} vs {_fmt_try(existing_cash)}"
    )
    if conflicting_fields:
        labels = ", ".join(FIELD_LABELS[f] for f in conflicting_fields)
        note += f" — {labels} alanlarında >%{int(CONFLICT_THRESHOLD * 100)} fark bulundu"
    else:
        note += " — kaynaklar tutarlı"
    return note


def collect() -> dict:
    company = get_or_create_company(TICKER, COMPANY_NAME, sector="Enerji")

    now = datetime.now(timezone.utc)
    year = now.year - 1  # en son yayınlanmış yıllık rapor (Şubat/Mart'ta yayınlanır)
    items = _fetch_mali_tablo(year=year, prior_year=year - 1)
    computed = _compute_financials(items)
    period = f"{year}-12-31"

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

        if not existing:
            raise RuntimeError(
                f"{TICKER} için {period} döneminde birincil (yfinance) kayıt bulunamadı — "
                "önce collectors/kap/tuprs_financials.py çalıştırılmalı."
            )

        diffs = {
            "cash": _relative_diff(computed["cash"], float(existing.cash) if existing.cash is not None else None),
            "debt": _relative_diff(computed["debt"], float(existing.debt) if existing.debt is not None else None),
            "roe": _relative_diff(computed["roe"], float(existing.roe) if existing.roe is not None else None),
            "roic": _relative_diff(computed["roic"], float(existing.roic) if existing.roic is not None else None),
        }
        conflicting_fields = [k for k, v in diffs.items() if v is not None and v > CONFLICT_THRESHOLD]
        has_conflicting_data = bool(conflicting_fields)

        comparison_note = _build_comparison_note(computed, existing, conflicting_fields)

        existing.source_count = 2
        existing.has_conflicting_data = has_conflicting_data
        existing.source = f"{existing.source} + {comparison_note}"
        db.commit()
    finally:
        db.close()

    return {
        "period": period,
        "isyatirim": computed,
        "diffs": diffs,
        "has_conflicting_data": has_conflicting_data,
    }


if __name__ == "__main__":
    result = collect()
    print(f"{TICKER} çapraz kontrol tamamlandı: {result}")

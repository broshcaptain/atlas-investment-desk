"""Buffett/Lynch/Graham/Dalio TR çerçevelerini `company_financials` verisine
uygulayıp atlas_score üretir.

SINIRLAMA: `company_financials` şeması sadece roe, roic, debt, cash,
dividend_yield alanlarını taşır — fiyat bazlı veri (F/K, PD/DD) ve tarihsel
kazanç/büyüme verisi yok. Bu yüzden her çerçeve klasik tanımının SADECE bu
alanlarla değerlendirilebilen alt kriterlerini kullanır. Değerlendirilemeyen
kriterler `missing_criteria` içinde açıkça listelenir ve eksik veri, uydurma
bir alt-skorla telafi edilmez — sadece o kriter atlanır ve güven bandı buna
göre düşer.

Bu modül al/sat tavsiyesi üretmez; atlas_score sadece mevcut temel verilere
dayalı basitleştirilmiş bir karşılaştırma göstergesidir.
"""

from datetime import datetime, timezone
from typing import Optional

# Eşikler kabaca literatürden uyarlanmıştır (Buffett: ROE>%15, Graham: temkinli
# bilanço, vb.) — bilimsel olarak doğrulanmış kesin sınırlar değildir, atlas_score
# bu eşiklere göre "olabilir" düzeyinde bir gösterge üretir.
ROE_BAD, ROE_GOOD = 0.05, 0.20
ROIC_BAD, ROIC_GOOD = 0.02, 0.15
DIVIDEND_YIELD_BAD, DIVIDEND_YIELD_GOOD = 0.0, 0.05

# Net borç / nakit oranı: 0 = borç yok (ideal), değer arttıkça bilanço zayıflar.
BUFFETT_DEBT_BAD, BUFFETT_DEBT_GOOD = 2.0, 0.0
LYNCH_DEBT_BAD, LYNCH_DEBT_GOOD = 3.0, 0.0
GRAHAM_DEBT_BAD, GRAHAM_DEBT_GOOD = 1.5, 0.0
DALIO_DEBT_BAD, DALIO_DEBT_GOOD = 1.5, 0.0

DATA_AGE_STALE_DAYS = 180  # temel veri çeyreklik güncellendiği için eşik daha gevşek


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _linear_score(value: Optional[float], bad: float, good: float) -> Optional[float]:
    """`bad` değerinde 0, `good` değerinde 100 puan; aradaki değerler lineer
    enterpole edilir. `good < bad` ise ölçek otomatik ters çevrilir (düşük
    değerin iyi olduğu kriterler için)."""
    if value is None:
        return None
    if good == bad:
        return 100.0 if value >= good else 0.0
    fraction = (value - bad) / (good - bad)
    return _clamp(fraction * 100)


def _net_debt_to_cash_ratio(debt: Optional[float], cash: Optional[float]) -> Optional[float]:
    if debt is None or cash is None:
        return None
    debt, cash = float(debt), float(cash)
    if debt <= 0:
        return 0.0
    if cash <= 0:
        return float("inf")
    return debt / cash


def _build_framework(name: str, note: str, components: list[tuple[str, Optional[float]]]) -> dict:
    """`components`: (kriter adı, hesaplanan alt-skor ya da None) listesi.
    Alt-skoru None olan kriterler `missing_criteria`'ya düşer, skora katılmaz."""
    used_criteria, missing_criteria, used_scores = [], [], []
    for label, sub_score in components:
        if sub_score is None:
            missing_criteria.append(label)
        else:
            used_criteria.append(label)
            used_scores.append(sub_score)

    score = round(sum(used_scores) / len(used_scores), 1) if used_scores else None

    return {
        "name": name,
        "score": score,
        "used_criteria": used_criteria,
        "missing_criteria": missing_criteria,
        "note": note,
    }


def _buffett_tr(roe, roic, debt, cash) -> dict:
    debt_ratio = _net_debt_to_cash_ratio(debt, cash)
    components = [
        ("ROE (kârlılık kalitesi)", _linear_score(roe, ROE_BAD, ROE_GOOD)),
        ("ROIC (sermaye verimliliği)", _linear_score(roic, ROIC_BAD, ROIC_GOOD)),
        ("Borç disiplini (net borç/nakit)", _linear_score(debt_ratio, BUFFETT_DEBT_BAD, BUFFETT_DEBT_GOOD)),
    ]
    note = (
        "Buffett TR: kârlılık (ROE/ROIC) ve borç disiplinine dayalı basitleştirilmiş "
        "sürüm. Ekonomik hendek (moat), yönetim kalitesi ve fiyatlama gücü gibi nitel "
        "kriterler bu veriyle otomatik değerlendirilemez, dahil edilmedi."
    )
    return _build_framework("buffett_tr", note, components)


def _lynch_tr(debt, cash) -> dict:
    debt_ratio = _net_debt_to_cash_ratio(debt, cash)
    components = [
        ("PEG oranı (F/K ÷ kazanç büyümesi)", None),  # fiyat/büyüme verisi şemada yok
        ("Borç yönetilebilirliği (net borç/nakit)", _linear_score(debt_ratio, LYNCH_DEBT_BAD, LYNCH_DEBT_GOOD)),
    ]
    note = (
        "Lynch TR: çerçevenin özü olan PEG oranı (F/K ÷ kazanç büyümesi) için gereken "
        "fiyat ve büyüme verisi company_financials şemasında yok — bu skor yalnızca "
        "borç yönetilebilirliğine dayanır, gerçek bir Lynch/PEG değerlendirmesi olarak "
        "okunmamalı."
    )
    return _build_framework("lynch_tr", note, components)


def _graham_tr(debt, cash, dividend_yield) -> dict:
    debt_ratio = _net_debt_to_cash_ratio(debt, cash)
    components = [
        ("Bilanço gücü (net borç/nakit)", _linear_score(debt_ratio, GRAHAM_DEBT_BAD, GRAHAM_DEBT_GOOD)),
        ("Güncel temettü verimi", _linear_score(dividend_yield, DIVIDEND_YIELD_BAD, DIVIDEND_YIELD_GOOD)),
        ("Ölçülü F/K (<15)", None),           # fiyat verisi şemada yok
        ("Ölçülü PD/DD (<1.5)", None),        # fiyat verisi şemada yok
        ("10 yıllık kazanç istikrarı/büyümesi", None),   # tarihsel seri yok
        ("20 yıllık kesintisiz temettü kaydı", None),    # tarihsel seri yok, sadece güncel verim var
    ]
    note = (
        "Graham TR: klasik defansif yatırımcı kriterlerinin çoğu (F/K, PD/DD, "
        "çok yıllı kazanç/temettü kaydı) fiyat ve tarihsel veri gerektirir, şemada "
        "yok. Bu skor yalnızca bilanço gücü ve güncel temettü verimine dayanır."
    )
    return _build_framework("graham_tr", note, components)


def _dalio_tr(roic, debt, cash) -> dict:
    debt_ratio = _net_debt_to_cash_ratio(debt, cash)
    components = [
        ("Bilanço dayanıklılığı (net borç/nakit tamponu)", _linear_score(debt_ratio, DALIO_DEBT_BAD, DALIO_DEBT_GOOD)),
        ("Sermaye verimliliği (ROIC)", _linear_score(roic, ROIC_BAD, ROIC_GOOD)),
        ("Makro rejime/çeşitlendirmeye duyarlılık", None),  # tek şirket, tek dönem — kapsam dışı
    ]
    note = (
        "Dalio TR: orijinal çerçeve makro-ekonomik rejim ve varlık çeşitlendirmesine "
        "dayanır; tek bir şirketin tek dönemlik temel verisiyle bu doğrudan uygulanamaz. "
        "Burada yalnızca bilanço dayanıklılığı (borç/nakit tamponu) ve sermaye "
        "verimliliğine daraltılmış bir uyarlama kullanılıyor."
    )
    return _build_framework("dalio_tr", note, components)


def _confidence(frameworks: dict, source_count: int, has_conflicting_data: bool, data_age_days: Optional[float]) -> dict:
    used_total = sum(len(f["used_criteria"]) for f in frameworks.values())
    missing_total = sum(len(f["missing_criteria"]) for f in frameworks.values())
    total = used_total + missing_total

    raw = (used_total / total * 100) if total else 0.0
    if has_conflicting_data:
        raw *= 0.5
    if data_age_days is not None and data_age_days > DATA_AGE_STALE_DAYS:
        raw *= 0.7
    raw = round(_clamp(raw), 1)

    # Zorunlu kural: tek kaynaklı bilgi düşük güven skoruyla işaretlenir.
    if source_count <= 1:
        band = "Düşük"
    elif raw >= 70:
        band = "Yüksek"
    elif raw >= 40:
        band = "Orta"
    else:
        band = "Düşük"

    return {
        "band": band,
        "raw": raw,
        "source_count": source_count,
        "has_conflicting_data": has_conflicting_data,
        "data_age_days": data_age_days,
    }


def analyze_company(
    financials: Optional[dict],
    *,
    source_count: int = 1,
    has_conflicting_data: bool = False,
    company_code: Optional[str] = None,
    now: Optional[datetime] = None,
) -> dict:
    """`financials`: {"roe", "roic", "debt", "cash", "dividend_yield",
    "period", "fetched_at", ...} şeklinde bir sözlük (bkz.
    backend/services/company_service.py:_serialize_financials). Veri yoksa
    veya `financials` boşsa "yetersiz veri" döner — sahte skor üretilmez.
    """
    if not financials or financials.get("status") == "yetersiz veri":
        return {
            "status": "yetersiz_veri",
            "atlas_score": None,
            "confidence": None,
            "frameworks": None,
            "message": "Temel finansal veri bulunamadı, atlas_score üretilemedi.",
        }

    roe = financials.get("roe")
    roic = financials.get("roic")
    debt = financials.get("debt")
    cash = financials.get("cash")
    dividend_yield = financials.get("dividend_yield")

    frameworks = {
        "buffett_tr": _buffett_tr(roe, roic, debt, cash),
        "lynch_tr": _lynch_tr(debt, cash),
        "graham_tr": _graham_tr(debt, cash, dividend_yield),
        "dalio_tr": _dalio_tr(roic, debt, cash),
    }

    framework_scores = [f["score"] for f in frameworks.values() if f["score"] is not None]
    if not framework_scores:
        return {
            "status": "yetersiz_veri",
            "atlas_score": None,
            "confidence": None,
            "frameworks": frameworks,
            "message": "Hiçbir çerçeve için yeterli veri yok, atlas_score üretilemedi.",
        }

    atlas_score = round(sum(framework_scores) / len(framework_scores), 1)

    fetched_at = financials.get("fetched_at")
    data_age_days = None
    if fetched_at is not None:
        reference_now = now or datetime.now(timezone.utc)
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        data_age_days = (reference_now - fetched_at).total_seconds() / 86400

    confidence = _confidence(frameworks, source_count, has_conflicting_data, data_age_days)

    subject = f"{company_code} için " if company_code else ""
    message = (
        f"{subject}atlas_score {atlas_score:.0f}/100 olarak hesaplandı — bu bir al/sat "
        f"tavsiyesi değildir, mevcut temel verilere dayalı basitleştirilmiş bir "
        f"karşılaştırma göstergesi olabilir. Güven: {confidence['band']} ({confidence['raw']:.0f}/100)."
    )

    return {
        "status": "ok",
        "period": financials.get("period"),
        "atlas_score": atlas_score,
        "confidence": confidence,
        "frameworks": frameworks,
        "message": message,
    }


if __name__ == "__main__":
    from backend.config.database import SessionLocal
    from backend.repositories.company_repository import get_company_by_code, get_latest_financials
    from backend.services.company_service import _serialize_financials

    db = SessionLocal()
    try:
        company = get_company_by_code(db, "TUPRS")
        financials = _serialize_financials(get_latest_financials(db, company.id)) if company else None
    finally:
        db.close()

    result = analyze_company(financials, company_code="TUPRS")
    print(result["message"])
    if result["frameworks"]:
        for key, framework in result["frameworks"].items():
            print(f"  {key}: {framework['score']} (eksik: {framework['missing_criteria']})")

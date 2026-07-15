"""AI Sabah Brifingi için prompt şablonu, girdi hazırlama ve Groq API
entegrasyonu.

`build_morning_briefing_prompt()` CLAUDE.md'nin zorunlu kurallarına uygun,
mevcut piyasa/şirket verisinden üretilmiş nihai prompt metnini döner — canlı
veri toplama veya API anahtarı olmadan, mock veriyle test edilebilir.
`generate_morning_briefing()` bu prompt'u gerçek bir Groq API çağrısıyla
brifing metnine çevirir; veri eksikse veya `GROQ_API_KEY` tanımlı değilse
sahte metin üretmez, durumu açıkça döner.

[Düzeltme 1] Piyasa verisi `MARKET_DATA_STALE_HOURS` saatten eskiyse
"veri bayat" olarak işaretlenir — sessizce eski veriyle brifing üretilmez.
"""

import os
from datetime import datetime, timezone
from typing import Optional

import groq
from groq import Groq

from ai.summaries.language_guard import find_non_turkish_script

MARKET_DATA_STALE_HOURS = 24
ANNOUNCEMENT_CONTENT_PREVIEW_CHARS = 200
MAX_ANNOUNCEMENTS_IN_BRIEFING = 5
BRIEFING_MODEL = "llama-3.3-70b-versatile"
BRIEFING_MAX_OUTPUT_TOKENS = 4096
# Model (llama-3.3-70b-versatile) gözlemsel olarak Türkçe metne rastgele
# Çince/İngilizce kelimeler karıştırabiliyor (CLAUDE.md — Dil kuralını ihlal
# eder); temperature=0.3'te bile tekrar görüldü. Daha da düşük bir değer bu
# riski azaltır ama garanti etmez — asıl güvence sistem promptundaki DİL
# kuralı (bkz. BRIEFING_SYSTEM_PROMPT).
BRIEFING_TEMPERATURE = 0.1

BRIEFING_SYSTEM_PROMPT = """
Sen Atlas uygulamasının sabah brifing yazarısın. Tek kullanıcı için, o günün
piyasa ve şirket verisini özetleyen kısa bir Türkçe brifing yazacaksın.

Zorunlu kurallar:
1. DİL: Yanıtının tamamı, başından sonuna kadar SADECE Türkçe olacak. Başka
   hiçbir dilden (İngilizce, Çince, Arapça vb.) tek kelime, tek karakter
   veya tek ifade bile karıştırma. Emin olamadığın bir terim varsa onu da
   Türkçeleştir, olduğu gibi başka dilde bırakma.
2. Al/sat tavsiyesi verme, kesinlik iddia etme ("kesin yükselecek" gibi ifadeler yasak).
3. Veri ve yorumu ayır — yorum cümlelerinde "olabilir" dili kullan.
4. Aşağıda verilmeyen hiçbir veriyi uydurma; bir bölüm için veri yoksa veya
   "yetersiz veri" olarak işaretlenmişse bunu açıkça söyle, tahmin üretme.
5. "VERİ BAYAT" notu taşıyan piyasa verilerini kullanırken bunu kullanıcıya
   açıkça belirt, güncelmiş gibi sunma.
6. Güven skorlarını olduğu gibi (bant + parantez içi ham sayı) aktar, tek
   başına ham sayı olarak gösterme.
7. KAP duyuru içeriği bazen ham XBRL taksonomi etiketleri içerebilir, düzyazı
   gibi sunma; anlamlı bir özet çıkaramıyorsan bunu belirt.
""".strip()


def _to_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _age_hours(fetched_at: Optional[datetime], now: datetime) -> Optional[float]:
    if fetched_at is None:
        return None
    return (now - _to_aware_utc(fetched_at)).total_seconds() / 3600


def _prepare_market_rows(market_summary: Optional[dict], now: datetime) -> list[dict]:
    items = (market_summary or {}).get("items", [])
    rows = []
    for item in items:
        age_hours = _age_hours(item.get("fetched_at"), now)
        rows.append(
            {
                "symbol": item.get("symbol"),
                "price": item.get("price"),
                "source": item.get("source"),
                "fetched_at": item.get("fetched_at"),
                "age_hours": round(age_hours, 1) if age_hours is not None else None,
                "stale": age_hours is not None and age_hours > MARKET_DATA_STALE_HOURS,
            }
        )
    return rows


def _prepare_company_block(company_overview: Optional[dict]) -> Optional[dict]:
    if not company_overview:
        return None
    return {
        "code": company_overview.get("company", {}).get("code"),
        "name": company_overview.get("company", {}).get("name"),
        "financials": company_overview.get("financials"),
        "atlas_score": company_overview.get("atlas_score"),
        "recent_announcements": (company_overview.get("recent_announcements") or [])[
            :MAX_ANNOUNCEMENTS_IN_BRIEFING
        ],
    }


def build_briefing_context(
    market_summary: Optional[dict],
    company_overview: Optional[dict] = None,
    now: Optional[datetime] = None,
) -> dict:
    """Ham piyasa/şirket verisini, brifing prompt'unu üretmeye hazır bir
    context'e dönüştürür (veri yaşı hesabı, bayat veri işaretleme dahil).
    İkisi de boşsa "yetersiz veri" döner — sahte brifing üretilmez.
    """
    now = now or datetime.now(timezone.utc)
    market_rows = _prepare_market_rows(market_summary, now)
    company_block = _prepare_company_block(company_overview)

    if not market_rows and not company_block:
        return {
            "status": "yetersiz_veri",
            "message": "Piyasa ya da şirket verisi bulunamadı, brifing için yeterli veri yok.",
        }

    return {
        "status": "ok",
        "generated_at": now,
        "market": market_rows,
        "company": company_block,
    }


def _format_market_lines(market_rows: list[dict]) -> str:
    if not market_rows:
        return "(piyasa verisi yok)"

    lines = []
    for row in market_rows:
        age = f"{row['age_hours']} saat önce" if row["age_hours"] is not None else "veri yaşı bilinmiyor"
        stale_note = " [VERİ BAYAT]" if row["stale"] else ""
        lines.append(f"- {row['symbol']}: {row['price']} (kaynak: {row['source']}, {age}{stale_note})")
    return "\n".join(lines)


def _format_financials_line(financials: Optional[dict]) -> str:
    if not financials or financials.get("status") == "yetersiz veri":
        return "  Temel finansal veri: yetersiz veri"
    return (
        f"  Temel veri ({financials.get('period')}, kaynak: {financials.get('source')}): "
        f"ROE={financials.get('roe')}, ROIC={financials.get('roic')}, "
        f"Borç={financials.get('debt')}, Nakit={financials.get('cash')}, "
        f"Temettü verimi={financials.get('dividend_yield')}"
    )


def _format_atlas_score_line(atlas_score: Optional[dict]) -> str:
    if not atlas_score or atlas_score.get("status") != "ok":
        return "  atlas_score: yetersiz veri"
    confidence = atlas_score["confidence"]
    return (
        f"  atlas_score: {atlas_score['atlas_score']}/100 — "
        f"Güven: {confidence['band']} ({confidence['raw']}/100)"
    )


def _format_announcements(announcements: list[dict]) -> list[str]:
    if not announcements:
        return ["  Son KAP duyurusu yok."]

    lines = ["  Son KAP duyuruları:"]
    for a in announcements:
        text = (a.get("ai_summary") or a.get("content") or "")[:ANNOUNCEMENT_CONTENT_PREVIEW_CHARS]
        lines.append(f"    - {a.get('announced_at')}: {a.get('category')} — {text}")
    return lines


def _format_company_block(company: Optional[dict]) -> str:
    if not company:
        return "(şirket verisi yok)"

    lines = [f"{company['code']} — {company['name']}"]
    lines.append(_format_financials_line(company.get("financials")))
    lines.append(_format_atlas_score_line(company.get("atlas_score")))
    lines.extend(_format_announcements(company.get("recent_announcements") or []))
    return "\n".join(lines)


def _build_data_section(context: dict) -> str:
    return (
        f"Brifing zamanı: {context['generated_at'].isoformat()}\n\n"
        + "PİYASA VERİSİ:\n"
        + _format_market_lines(context["market"])
        + "\n\nŞİRKET VERİSİ:\n"
        + _format_company_block(context["company"])
    )


def build_morning_briefing_prompt(
    market_summary: Optional[dict],
    company_overview: Optional[dict] = None,
    now: Optional[datetime] = None,
) -> dict:
    """Piyasa özeti (bkz. backend/services/dashboard_service.py:get_market_summary)
    ve şirket genel görünümü (bkz. backend/services/company_service.py:get_company_overview)
    verilerinden bir LLM'e gönderilmeye hazır brifing prompt'u üretir.

    Veri yoksa {"status": "yetersiz_veri", ...} döner, sahte brifing üretilmez.
    """
    context = build_briefing_context(market_summary, company_overview, now)
    if context["status"] != "ok":
        return context

    prompt = BRIEFING_SYSTEM_PROMPT + "\n\n---\n\n" + _build_data_section(context)

    return {"status": "ok", "prompt": prompt, "context": context}


def generate_morning_briefing(
    market_summary: Optional[dict],
    company_overview: Optional[dict] = None,
    now: Optional[datetime] = None,
) -> dict:
    """`build_morning_briefing_prompt()`'un ürettiği veriyi gerçek bir Groq
    API çağrısıyla brifing metnine çevirir.

    Piyasa/şirket verisi yetersizse `{"status": "yetersiz_veri", ...}`,
    `GROQ_API_KEY` tanımlı değilse `{"status": "anahtar_eksik", ...}`,
    API çağrısı başarısız olursa veya yanıt Türkçe dışı bir alfabeden
    karakter içeriyorsa `{"status": "hata", ...}` döner — hiçbir durumda
    sahte veya dil kuralını ihlal eden brifing metni üretilmez.
    """
    context = build_briefing_context(market_summary, company_overview, now)
    if context["status"] != "ok":
        return context

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "status": "anahtar_eksik",
            "message": "GROQ_API_KEY tanımlı değil, brifing üretilemedi.",
        }

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=BRIEFING_MODEL,
            messages=[
                {"role": "system", "content": BRIEFING_SYSTEM_PROMPT},
                {"role": "user", "content": _build_data_section(context)},
            ],
            max_tokens=BRIEFING_MAX_OUTPUT_TOKENS,
            temperature=BRIEFING_TEMPERATURE,
        )
        text = response.choices[0].message.content
    except groq.APIError as e:
        return {
            "status": "hata",
            "message": f"Brifing üretilirken API hatası oluştu: {e}",
        }

    leaked_char = find_non_turkish_script(text)
    if leaked_char:
        return {
            "status": "hata",
            "message": (
                f"Model yanıtında Türkçe dışı bir alfabeden karakter tespit edildi "
                f"('{leaked_char}', U+{ord(leaked_char):04X}) — sonuç gösterilmiyor."
            ),
        }

    return {
        "status": "ok",
        "text": text,
        "generated_at": context["generated_at"],
    }


if __name__ == "__main__":
    from datetime import timedelta

    now = datetime(2026, 7, 13, 8, 0, tzinfo=timezone.utc)

    mock_market_summary = {
        "items": [
            {"symbol": "USDTRY", "price": 34.21, "source": "yfinance", "fetched_at": now - timedelta(hours=1)},
            {"symbol": "EURTRY", "price": 37.05, "source": "yfinance", "fetched_at": now - timedelta(hours=1)},
            {"symbol": "ONS_ALTIN", "price": 2385.4, "source": "yfinance", "fetched_at": now - timedelta(hours=30)},
            {"symbol": "BRENT", "price": 82.3, "source": "yfinance", "fetched_at": now - timedelta(hours=2)},
            {"symbol": "BIST100", "price": 9850.1, "source": "yfinance", "fetched_at": now - timedelta(hours=1)},
        ]
    }

    mock_company_overview = {
        "company": {
            "code": "TUPRS",
            "name": "TÜPRAŞ-Türkiye Petrol Rafinerileri A.Ş.",
            "sector": "Enerji",
            "sub_sector": None,
        },
        "financials": {
            "period": "2025-12-31",
            "roe": 0.1037,
            "roic": 0.1421,
            "debt": 55735943168.0,
            "cash": 130056552448.0,
            "dividend_yield": 0.0511,
            "source": "yfinance:TUPRS.IS (.info)",
            "fetched_at": now - timedelta(days=10),
        },
        "atlas_score": {
            "status": "ok",
            "atlas_score": 80.9,
            "confidence": {"band": "Düşük", "raw": 57.1, "source_count": 1, "has_conflicting_data": False, "data_age_days": 10},
            "frameworks": {},
            "message": "TUPRS için atlas_score 81/100 olarak hesaplandı — bu bir al/sat tavsiyesi değildir.",
        },
        "recent_announcements": [
            {
                "announced_at": now - timedelta(days=2),
                "category": "Finansal Rapor",
                "content": "TÜPRAŞ 2025 yılı 4. çeyrek finansal sonuçlarını açıkladı.",
                "ai_summary": None,
                "source_url": None,
                "fetched_at": now - timedelta(days=2),
            }
        ],
    }

    result = build_morning_briefing_prompt(mock_market_summary, mock_company_overview, now=now)
    print(f"status: {result['status']}\n")
    print(result["prompt"])

    print("\n\n--- Veri yoksa kontrolü ---")
    empty_result = build_morning_briefing_prompt(None, None, now=now)
    print(empty_result)

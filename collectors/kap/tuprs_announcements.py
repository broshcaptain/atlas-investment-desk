import time
from datetime import datetime, timedelta, timezone

from backend.config.database import SessionLocal
from backend.models.kap_announcement import KapAnnouncement
from collectors.kap.common import (
    fetch_disclosure_list,
    fetch_disclosure_text,
    get_member_oid,
    get_or_create_company,
)

TICKER = "TUPRS"
COMPANY_NAME = "TÜPRAŞ-Türkiye Petrol Rafinerileri A.Ş."
LOOKBACK_DAYS = 30  # düşük hacimli, tek şirket sorgusu — MVP'de sadece TUPRS
REQUEST_DELAY_SECONDS = 0.5  # KAP'a karşı nazik olmak için detay istekleri arasında bekleme


def _parse_kap_datetime(value: str) -> datetime:
    # KAP formatı: "10.07.2026 18:16:03"
    return datetime.strptime(value, "%d.%m.%Y %H:%M:%S").replace(tzinfo=timezone.utc)


def collect() -> int:
    company = get_or_create_company(TICKER, COMPANY_NAME, sector="Enerji")
    member_oid = get_member_oid(TICKER)

    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=LOOKBACK_DAYS)

    disclosures = fetch_disclosure_list(member_oid, from_date.isoformat(), to_date.isoformat())

    db = SessionLocal()
    saved = 0
    try:
        existing_urls = {
            row.source_url
            for row in db.query(KapAnnouncement.source_url).filter(
                KapAnnouncement.company_id == company.id
            )
        }

        for item in disclosures:
            disclosure_index = item["disclosureIndex"]
            source_url = f"https://www.kap.org.tr/tr/Bildirim/{disclosure_index}"

            if source_url in existing_urls:
                continue

            content = fetch_disclosure_text(disclosure_index)
            time.sleep(REQUEST_DELAY_SECONDS)

            row = KapAnnouncement(
                company_id=company.id,
                announced_at=_parse_kap_datetime(item["publishDate"]),
                category=item.get("subject") or item.get("disclosureCategory"),
                content=content or item.get("summary", ""),
                ai_summary=None,
                source_url=source_url,
                fetched_at=datetime.now(timezone.utc),
            )
            db.add(row)
            db.commit()
            saved += 1
    finally:
        db.close()

    return saved


if __name__ == "__main__":
    count = collect()
    print(f"{TICKER}: {count} yeni KAP duyurusu kaydedildi.")

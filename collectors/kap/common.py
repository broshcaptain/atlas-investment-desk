import re

import requests
from bs4 import BeautifulSoup

from backend.config.database import SessionLocal
from backend.models.company import Company

# Resmi/dokümante KAP REST API'si (Borsa İstanbul ile veri dağıtım sözleşmesi + API key
# gerektiriyor) bu proje kapsamında kullanılmıyor. Bunun yerine kap.org.tr'nin kendi
# web sitesinin de kullandığı, kimlik doğrulama gerektirmeyen genel uç noktaları
# düşük hacimde (tek şirket, günlük) çağırıyoruz. Kaynak şeffaflığı için her satırda
# bu not `source`/`source_url` alanlarına yansıtılır.
KAP_BASE_URL = "https://www.kap.org.tr/tr/api"
KAP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AtlasResearchBot/1.0; personal, low-volume use)",
    "Referer": "https://www.kap.org.tr/tr/bist-sirketler",
}


def get_or_create_company(code: str, name: str, sector: str = None, sub_sector: str = None) -> Company:
    db = SessionLocal()
    try:
        company = db.query(Company).filter(Company.code == code).first()
        if company:
            return company

        company = Company(code=code, name=name, sector=sector, sub_sector=sub_sector)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    finally:
        db.close()


def get_member_oid(ticker: str) -> str:
    resp = requests.get(f"{KAP_BASE_URL}/member/filter/{ticker}", headers=KAP_HEADERS, timeout=15)
    resp.raise_for_status()
    results = resp.json()

    if not results:
        raise RuntimeError(f"KAP'ta {ticker} için şirket bulunamadı.")

    return results[0]["mkkMemberOid"]


def fetch_disclosure_list(member_oid: str, from_date: str, to_date: str) -> list:
    payload = {
        "fromDate": from_date,
        "toDate": to_date,
        "mkkMemberOidList": [member_oid],
        "subjectList": [],
    }
    resp = requests.post(
        f"{KAP_BASE_URL}/disclosure/members/byCriteria",
        json=payload,
        headers=KAP_HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_disclosure_text(disclosure_index: int) -> str:
    resp = requests.get(
        f"{KAP_BASE_URL}/notification/attachment-detail/{disclosure_index}",
        headers=KAP_HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if not data:
        return ""

    body_parts = data[0].get("disclosureBody") or []
    html = "\n".join(body_parts) if isinstance(body_parts, list) else str(body_parts)

    soup = BeautifulSoup(html, "html.parser")
    # KAP'ın yapılandırılmış (XBRL tabanlı) duyuru şablonları, dil değiştirme için
    # gizli (display:none) İngilizce/Türkçe kopya hücreler içeriyor — bunlar
    # temizlenmezse metin iki dilde tekrar eder.
    for hidden in soup.find_all(style=lambda s: s and "display:none" in s.replace(" ", "")):
        hidden.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()

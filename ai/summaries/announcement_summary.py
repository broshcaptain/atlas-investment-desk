"""Tek bir KAP duyurusunun temizlenmiş metnini özetleyen Groq API entegrasyonu.

Girdi olarak `collectors/kap/common.py:fetch_disclosure_text()`'in ürettiği
temiz metni bekler — bu modül HTML/XBRL temizliği yapmaz, sadece özetler.
"""

import os
from typing import Optional

import groq
from groq import Groq

from ai.summaries.language_guard import find_non_turkish_script

SUMMARY_MODEL = "llama-3.3-70b-versatile"
SUMMARY_MAX_OUTPUT_TOKENS = 1024
# Model (llama-3.3-70b-versatile) gözlemsel olarak Türkçe metne rastgele
# Çince/İngilizce kelimeler karıştırabiliyor (CLAUDE.md — Dil kuralını ihlal
# eder); temperature=0.3'te bile tekrar görüldü. Daha da düşük bir değer bu
# riski azaltır ama garanti etmez — asıl güvence sistem promptundaki DİL
# kuralı (bkz. ANNOUNCEMENT_SUMMARY_SYSTEM_PROMPT).
SUMMARY_TEMPERATURE = 0.1

ANNOUNCEMENT_SUMMARY_SYSTEM_PROMPT = """
Sen Atlas uygulamasının KAP duyuru özetleyicisisin. Sana verilen tek bir KAP
(Kamuyu Aydınlatma Platformu) duyurusunun metnini, 1-3 cümlelik tarafsız bir
Türkçe özete çevireceksin.

Zorunlu kurallar:
1. DİL: Yanıtının tamamı, başından sonuna kadar SADECE Türkçe olacak. Başka
   hiçbir dilden (İngilizce, Çince, Arapça vb.) tek kelime, tek karakter
   veya tek ifade bile karıştırma. Emin olamadığın bir terim varsa onu da
   Türkçeleştir, olduğu gibi başka dilde bırakma.
2. Sadece verilen metinde yer alan bilgiyi özetle, yeni bilgi/sayı/tarih uydurma.
3. Al/sat tavsiyesi verme, kesinlik iddia etme.
4. Yorum ekleme — sadece duyurunun ne söylediğini özetle.
5. Duyuru içeriği önemli bir bilgi taşımıyorsa (ör. rutin/prosedürel bir
   bildirim), bunu olduğu gibi söyle, önemli bir şey varmış gibi gösterme.
""".strip()


def generate_announcement_summary(content: str, category: Optional[str] = None) -> dict:
    """Bir KAP duyurusunun temiz metnini Groq API ile özetler.

    İçerik boşsa `{"status": "yetersiz_veri", ...}`, `GROQ_API_KEY`
    tanımlı değilse `{"status": "anahtar_eksik", ...}`, API çağrısı
    başarısız olursa veya yanıt Türkçe dışı bir alfabeden karakter
    içeriyorsa `{"status": "hata", ...}` döner — hiçbir durumda sahte
    veya dil kuralını ihlal eden özet üretilmez.
    """
    if not content or not content.strip():
        return {
            "status": "yetersiz_veri",
            "message": "Duyuru içeriği boş, özet üretilemedi.",
        }

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "status": "anahtar_eksik",
            "message": "GROQ_API_KEY tanımlı değil, özet üretilemedi.",
        }

    data_section = (f"Kategori: {category}\n\n" if category else "") + f"Duyuru metni:\n{content}"

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": ANNOUNCEMENT_SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": data_section},
            ],
            max_tokens=SUMMARY_MAX_OUTPUT_TOKENS,
            temperature=SUMMARY_TEMPERATURE,
        )
        text = response.choices[0].message.content
    except groq.APIError as e:
        return {
            "status": "hata",
            "message": f"Özet üretilirken API hatası oluştu: {e}",
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

    return {"status": "ok", "text": text.strip()}


if __name__ == "__main__":
    mock_content = (
        "Açıklama\n"
        "Şirketimizin 01.01.2026 – 30.06.2026 hesap dönemine ilişkin finansal "
        "raporlarının 04 Ağustos 2026 tarihinde kamuya açıklanması "
        "planlanmaktadır. Kurumsal politikalarımız gereği, finansal tabloların "
        "açıklanmasından önceki iki hafta süresince \"sessiz dönem\" uygulaması "
        "yürütülecektir."
    )
    result = generate_announcement_summary(mock_content, category="Finansal Takvim")
    print(result)

    print("\n--- İçerik boşsa kontrolü ---")
    print(generate_announcement_summary("", category="Finansal Takvim"))

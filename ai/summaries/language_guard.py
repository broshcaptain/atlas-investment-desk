"""LLM ciktisina Turkce disi bir alfabeden (Cince, Kiril, Arapca vb.) sizan
karakterleri tespit eden basit bir korunma katmani.

Kod noktasi (codepoint) araligina dayali bir kontrol oldugu icin sadece
betik (script) degisimini yakalar - Latin alfabesiyle yazilmis Ingilizce
bir kelimeyi yakalamaz. Gozlemlenen gercek sizinti ornekleri (Cince
karakterler) bu sekilde tespit edilebiliyor; sistem promptundaki DIL
kurali ve dusuk `temperature` bu sizintiyi buyuk olcude onlese de garanti
etmedigi icin, ikinci bir savunma hatti olarak kullanilir.
"""

from typing import Optional

# (baslangic, bitis) kod noktasi araliklari - Turkce metinde hicbir zaman
# gorulmemesi gereken betikler.
_NON_TURKISH_SCRIPT_RANGES = [
    (0x4E00, 0x9FFF, "CJK (Cince/Japonca kanji)"),
    (0x3400, 0x4DBF, "CJK Extension A"),
    (0x3040, 0x30FF, "Hiragana/Katakana"),
    (0xAC00, 0xD7A3, "Hangul (Korece)"),
    (0x0600, 0x06FF, "Arapca"),
    (0x0400, 0x04FF, "Kiril"),
    (0x0E00, 0x0E7F, "Tayca"),
    (0x0900, 0x097F, "Devanagari"),
]


def find_non_turkish_script(text: str) -> Optional[str]:
    """Metinde Turkce disi bir betikten karakter varsa o karakteri, yoksa None doner."""
    for ch in text or "":
        codepoint = ord(ch)
        for start, end, _label in _NON_TURKISH_SCRIPT_RANGES:
            if start <= codepoint <= end:
                return ch
    return None

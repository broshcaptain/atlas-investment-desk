# Atlas — Ürün Tanımı

> Kaynak: `docs/ATLAS_MASTER_PROMPT_v1.1.md` (v1.1 MVP) — Ürün Tanımı, MVP Kapsamı, Kapsam dışı bölümleri.

Atlas, tek kullanıcı için tasarlanmış profesyonel bir yatırım araştırma masaüstü
uygulamasıdır. Amaç hisse önermek değil, kullanıcının kendi yatırım kararlarının
kalitesini artırmaktır.

**Sistem şunu asla yapmaz:** al/sat tavsiyesi, kesinlik iddiası ("kesin yükselecek"),
kaynaksız iddia.
**Sistem şunu yapar:** veriyi gösterir, olası yorumu ("olabilir" dili ile) sunar,
kaynağı belirtir.

---

## MVP Kapsamı — Sadece Bunlar

```
Dashboard
  ↓
Piyasa özeti: USDTRY, EURTRY, Gram Altın, Ons Altın, Brent, BIST100
  ↓
TUPRS şirket sayfası (tek şirket, pilot)
  ↓
Buffett/Lynch/Graham/Dalio TR skoru (atlas_score) — temel finansal verilerle
  ↓
KAP özetleri (TUPRS için)
  ↓
AI Sabah Brifingi
```

Bu akışın geliştirme sırası ve güncel durumu için bkz. `docs/roadmap.md`.

---

## Kapsam dışı — dokunma (Faz 2+)

Etki Analizi, Senaryo Motoru, Yatırım Mahkemesi, Tez Takibi, diğer 6 şirket
(sadece TUPRS pilot), Ekonomi Akademisi, kişiselleştirme, `causal_relationships`
tablosu.

Claude Code bu sınırın dışına çıkmamalı. Bu modüllerden birine dokunman
gerekecek gibi görünürse, kod yazmadan önce dur ve sor. "Madem buradayım,
şunu da ekleyeyim" davranışı yasak.

# Atlas — Mimari

> Kaynak: `docs/ATLAS_MASTER_PROMPT_v1.1.md` (v1.1 MVP) — Teknoloji Yığını, Klasör
> Yapısı, Veritabanı bölümleri; `CLAUDE.md` — Ortam Değişkenleri.

## Teknoloji Yığını

- Backend: Python, FastAPI
- Frontend: Next.js 16 (App Router, Turbopack), TypeScript, Tailwind CSS
- Database: PostgreSQL (yerelde `.env` ile override edilebilir — bkz. "Ortam
  Değişkenleri")
- Paket yönetimi: backend için `uv`/`poetry`, frontend için `npm`

## Klasör Yapısı

```
frontend/     Next.js/TypeScript — app/components/lib/types, `npm run dev` ile localhost:3000
backend/      FastAPI — routes/services/models/repositories/jobs/config
database/     migrations/seeds/schema + database/atlas.db (eski SQLite, referans)
collectors/   kap/tcmb/market/news/company_reports — veri toplama betikleri
ai/           prompts/analyzers/validators/summaries
docs/         product.md/architecture.md/investment_rules.md/roadmap.md + ATLAS_MASTER_PROMPT_v1.1.md (orijinal kaynak)
scripts/      legacy_portfolio_tracker/ — eski Streamlit portföy takipçisi (referans, kullanılmıyor)
```

## Veritabanı — İlk Sürüm Tabloları

```
companies              # kod, sektör, alt sektör
market_data            # fiyat/endeks anlık veri
macro_data             # TCMB, enflasyon, faiz, CDS vb. — tarih, değer, kaynak
kap_announcements      # şirket, tarih, kategori, içerik, ai_summary
news                    # başlık, kaynak, tarih, içerik, ai_summary (ham ve özet ayrı tutulur)
investment_thesis       # şirket, neden aldım, riskler, satış koşulu
events                   # ne oldu, neden oldu, neyi etkiler, kaynak
analysis                # AI çıktıları — güven skoru, kaynak sayısı dahil
sources                 # her iddianın referans aldığı kaynak kaydı
company_financials       # şirket, dönem, roe, roic, borç, nakit, temettü verimi, kaynak (frameworks skorunu besler)
```

Gerçek şema: `database/migrations/0001_initial_schema.sql` (bu 10 tablo,
`causal_relationships` hariç — gerçek PostgreSQL parser'ı (pglast) ve SQLite'ta
çalıştırılarak test edildi).

**Not:** `causal_relationships` (sebep-sonuç veritabanı) bilinçli olarak v1
kapsamı dışında bırakıldı — Etki Analizi modülü (Faz 2) ile birlikte eklenecek.
Şimdiden isim rezerve edildi, `analysis` tablosuyla karıştırılmayacak.

**[Düzeltme 1 — veri bayatlığı]** Her veri tablosunda (`market_data`,
`macro_data`, `kap_announcements`, `news`, `company_financials`) `fetched_at`
alanı zorunlu. Frontend her kartta "X dakika/saat önce güncellendi" gösterir.
Toplayıcı başarısız olursa veya veri N saatten eskiyse, kart açıkça "veri bayat"
uyarısı taşır — sessizce eski veriyle brifing üretilmez. (Kural detayı için
bkz. `docs/investment_rules.md`.)

**[Düzeltme 3 — döngüsel doğrulama, Faz 2 için şimdiden hazırlık]**
`causal_relationships` eklendiğinde `status` alanı taşıyacak: `proposed` (AI
önerdi) / `approved` (kullanıcı onayladı). Sadece `approved` satırlar
`impact_analyzer.py` tarafından kanıt olarak kullanılabilir. AI kendi
önerisini kendi analizinde referans gösteremez.

## Ortam Değişkenleri

`.env.example`'ı `.env` olarak kopyalayın. `DATABASE_URL` ayarlanmazsa
`backend/config/database.py` placeholder bir Postgres DSN'e düşer — prod'da
mutlaka `.env` ile override edin. Yerel geliştirmede
`DATABASE_URL=sqlite:///./atlas_dev.db` kullanılıyor.

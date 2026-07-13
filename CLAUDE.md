# Atlas

Tek kullanıcı için profesyonel yatırım araştırma masaüstü uygulaması. Amaç hisse
önermek değil, kullanıcının kendi yatırım kararlarının kalitesini artırmak.
Tam ürün/mimari tanımı: `docs/ATLAS_MASTER_PROMPT_v1.1.md`.

**Sistem şunu asla yapmaz:** al/sat tavsiyesi, kesinlik iddiası, kaynaksız iddia.
**Sistem şunu yapar:** veriyi gösterir, olası yorumu ("olabilir" dili ile) sunar, kaynağı belirtir.

## Teknoloji Yığını

- Backend: Python, FastAPI
- Frontend: Next.js, TypeScript (henüz kurulmadı)
- Database: PostgreSQL (yerelde `.env` ile override edilebilir)

## Klasör Yapısı

```
frontend/     Next.js/TypeScript (henüz iskelet yok)
backend/      FastAPI — routes/services/models/repositories/jobs/config
database/     migrations/seeds/schema + database/atlas.db (eski SQLite, referans)
collectors/   kap/tcmb/market/news/company_reports — veri toplama betikleri
ai/           prompts/analyzers/validators/summaries
docs/         product.md/architecture.md/investment_rules.md/roadmap.md (henüz bölünmedi)
scripts/      legacy_portfolio_tracker/ — eski Streamlit portföy takipçisi (referans, kullanılmıyor)
```

## Ortam Değişkenleri

`.env.example`'ı `.env` olarak kopyalayın. `DATABASE_URL` ayarlanmazsa
`backend/config/database.py` placeholder bir Postgres DSN'e düşer — prod'da
mutlaka `.env` ile override edin.

## Durum

**Tamamlanan:**
- Repo, master prompt'taki klasör yapısına göre yeniden düzenlendi (`frontend/backend/database/collectors/ai/docs/scripts`).
- Eski portföy takipçisi kodu (`app/`) dokunulmadan `scripts/legacy_portfolio_tracker/`'a taşındı — importları hâlâ eski `app.*` yoluna işaret ediyor, bağlı değil.
- `database/migrations/0001_initial_schema.sql`: MVP'nin 10 tablosu (`causal_relationships` bilinçli olarak Faz 2'ye bırakıldı, isim rezerve). Gerçek PostgreSQL parser'ı (pglast) ve SQLite'ta çalıştırılarak test edildi.
- `collectors/market/`: USDTRY, EURTRY, Ons Altın, Brent, BIST100 (yfinance) + türetilmiş Gram Altın — `market_data`'ya `fetched_at` ile yazıyor.
- `collectors/kap/`: TUPRS için KAP duyuruları (KAP'ın gayri-resmi ama canlı doğrulanmış iç API'si, düşük hacimli) ve `company_financials` (yfinance — ROE/borç/nakit/temettü verimi + türetilmiş ROIC).
- `.env` desteği: `python-dotenv` entegre edildi, `.env.example` eklendi, `.env` `.gitignore`'da.

**Sırada (master prompt'un 9 adımlık geliştirme sırasına göre):**
- Adım 5: `backend/` üzerinde minimal FastAPI iskeleti (`/dashboard`, `/companies/tuprs`)
- Adım 6: `ai/analyzers/company_analyzer.py` — atlas_score (Buffett/Lynch/Graham/Dalio TR)
- Adım 7: `ai/summaries/` — AI sabah brifingi
- Adım 8-9: `frontend/app/dashboard/`, `frontend/app/companies/tuprs/`
- `docs/` içeriğinin `product.md`/`architecture.md`/`investment_rules.md`/`roadmap.md` olarak bölünmesi henüz yapılmadı.

**Bilinen açık noktalar:**
- `scripts/legacy_portfolio_tracker/` içindeki importlar kırık (kasıtlı olarak dokunulmadı).
- KAP içerik metni yapılandırılmış duyurularda ham XBRL taksonomi etiketleri içeriyor (temiz düzyazı değil).

## Kapsam dışı — dokunma

Etki Analizi, Senaryo Motoru, Yatırım Mahkemesi, Tez Takibi, diğer 6 şirket (sadece
TUPRS pilot), Ekonomi Akademisi, kişiselleştirme, `causal_relationships` tablosu.
Bu modüllerden birine dokunman gerekecek gibi görünürse, kod yazmadan önce dur ve sor.

## Zorunlu kurallar

- Her veri satırında `fetched_at` zorunlu.
- Güven skoru kullanıcıya ham sayı olarak gösterilmez — bant (Düşük/Orta/Yüksek) + parantez içinde sayı.
- Veri eksikse sahte skor/sonuç üretme, "yetersiz veri" dön.

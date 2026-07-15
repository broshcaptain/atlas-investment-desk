# Atlas

## Dil
Tüm yanıtlar, sorular ve açıklamalar Türkçe olacak. Kod ve teknik terimler
(değişken adları, fonksiyon isimleri) İngilizce kalabilir, ama açıklama metni
her zaman Türkçe.

Tek kullanıcı için profesyonel yatırım araştırma masaüstü uygulaması. Amaç hisse
önermek değil, kullanıcının kendi yatırım kararlarının kalitesini artırmak.
Ürün tanımı: `docs/product.md`, mimari: `docs/architecture.md`, yatırım/AI
kuralları: `docs/investment_rules.md`, yol haritası ve durum:
`docs/roadmap.md` (orijinal kaynak: `docs/ATLAS_MASTER_PROMPT_v1.1.md`).

**Sistem şunu asla yapmaz:** al/sat tavsiyesi, kesinlik iddiası, kaynaksız iddia.
**Sistem şunu yapar:** veriyi gösterir, olası yorumu ("olabilir" dili ile) sunar, kaynağı belirtir.

## Teknoloji Yığını

- Backend: Python, FastAPI
- Frontend: Next.js 16 (App Router, Turbopack), TypeScript, Tailwind CSS
- Database: PostgreSQL (yerelde `.env` ile override edilebilir)

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
- Adım 5: `backend/` üzerinde minimal FastAPI iskeleti (`/dashboard`, `/companies/tuprs`) — yerelde `uvicorn backend.main:app --reload` ile ayağa kaldırılıp canlı doğrulandı. `.env`'de `DATABASE_URL=sqlite:///./atlas_dev.db` ile çalıştırıldı, `collectors/market/run_all.py` (`python -m` ile) gerçek market verisini yazdı, `/dashboard` bu veriyi 200 OK ile döndü.
- Adım 6: `ai/analyzers/company_analyzer.py` — `buffett_tr`/`lynch_tr`/`graham_tr`/`dalio_tr` çerçeveleri `company_financials`'taki mevcut alanlarla (roe/roic/debt/cash/dividend_yield) çalışır; şemada olmayan klasik kriterler (F/K, PD/DD, PEG, çok yıllı geçmiş) `missing_criteria` olarak işaretlenir, sahte skorla doldurulmaz. Tek kaynaklı veri güven bandını otomatik "Düşük"e sabitler. `backend/services/company_service.py` üzerinden `/companies/tuprs` yanıtına `atlas_score` alanı olarak entegre edildi, canlı doğrulandı. Yan düzeltme: `collectors/kap/tuprs_financials.py`'de `dividend_yield` birim hatası giderildi (yfinance yüzde-puan döndürüyordu, roe/roic ile tutarlı kesir birimine çevrildi).
- Adım 7: `ai/summaries/morning_briefing.py` — `build_morning_briefing_prompt()` piyasa özeti ve şirket genel görünümü (atlas_score dahil) verisinden LLM'e gönderilmeye hazır bir prompt metni üretir; henüz gerçek bir LLM çağrısı yok (ayrı bir entegrasyon adımı). Veri bayatlığı (piyasa verisi 24 saatten eskiyse `[VERİ BAYAT]`) ve `yetersiz_veri` kontrolleri mock veriyle test edildi.
- Adım 8: `frontend/` sıfırdan kuruldu (`create-next-app`, App Router, TypeScript, Tailwind). `frontend/app/dashboard/page.tsx` bir Server Component olarak `backend`'in `/dashboard` endpoint'ini (`API_BASE_URL`, varsayılan `http://localhost:8000`) sunucu tarafında çağırıp piyasa özetini kart olarak gösteriyor — her kart kaynağı ve "X saat/dakika önce güncellendi" bilgisini taşıyor, 24 saatten eski veri "Veri bayat" rozetiyle işaretleniyor (Düzeltme 1). Sabah brifingi kartı, LLM entegrasyonu henüz bağlı olmadığından açık bir "henüz aktif değil" durum mesajı gösteriyor — sahte/mock brifing metni yok. Kök `/` sayfası `/dashboard`'a yönlendiriyor. `npm run dev` + gerçek backend verisiyle tarayıcıda canlı doğrulandı (tüm 6 sembol, tr-TR sayı biçimi, kaynak/veri yaşı doğru render edildi).
- Adım 9: `frontend/app/companies/tuprs/page.tsx` — `backend`'in `/companies/tuprs` endpoint'ini sunucu tarafında çağırıp şirket adı/sektör, `atlas_score` (skor, güven bandı + parantez içinde ham sayı, 4 çerçevenin (buffett/lynch/graham/dalio_tr) alt skorları ve `missing_criteria`), temel finansal veriler (ROE/ROIC/borç/nakit/temettü verimi, veri bayatlığı rozetiyle) ve son KAP duyurularını gösteriyor. Backend 404 döndüğünde (`getCompanyOverview`, `frontend/lib/api.ts`) veya duyuru listesi boşsa sahte veri üretmeden "yetersiz veri" mesajı gösteriliyor. Gerçek TUPRS verisiyle (atlas_score 81/100, Güven: Düşük) SSR HTML çıktısı üzerinden canlı doğrulandı.
- `docs/` içeriği `product.md`/`architecture.md`/`investment_rules.md`/`roadmap.md` olarak bölündü — kaynak `ATLAS_MASTER_PROMPT_v1.1.md` ve bu dosya. Detaylı "Durum" takibi artık `docs/roadmap.md`'de de tutuluyor (bu bölümle birlikte güncel tutulmalı).
- Sabah brifingi için gerçek LLM entegrasyonu: `ai/summaries/morning_briefing.py:generate_morning_briefing()` LLM API'ye bağlandı (`backend/services/dashboard_service.py`, TUPRS `company_overview`'ini de çekip `/dashboard` yanıtına `briefing` alanı olarak ekliyor; `frontend/components/BriefingCard.tsx` gerçek brifing metnini/durum mesajını gösteriyor). API anahtarı tanımlı değilse `anahtar_eksik`, API hatası olursa `hata` döner — hiçbir durumda sahte metin üretilmez.
- KAP duyuru içeriği temizliği: `collectors/kap/common.py:fetch_disclosure_text()` artık ham XBRL taksonomi etiketlerini (`taxonomy-field-name-cell` — ör. `oda_ExplanationTextBlock|`) kaldırıyor ve tablo yapısını taksonomiye özgü sınıf adlarına bağlı kalmadan (genel `<table>`/`<tr>`/`<td>` gezinmesiyle) "Etiket: değer" biçiminde satır satır okunabilir metne çeviriyor; tablo bulunamazsa düz metne geri dönüyor. Gerçek TUPRS duyurularıyla (Finansal Takvim, Özel Durum Açıklaması) canlı doğrulandı. Yeni `ai/summaries/announcement_summary.py:generate_announcement_summary()` bu temiz metni LLM ile 1-3 cümlelik tarafsız özete çeviriyor (aynı `anahtar_eksik`/`hata`/sahte özet üretmeme kalıbı); `collectors/kap/tuprs_announcements.py` her yeni duyuru için bunu çağırıp `ai_summary`'yi dolduruyor, başarısız olursa `ai_summary` `NULL` kalıyor (frontend bu durumda temiz `content`'e düşüyor). Gerçek anahtarla iki gerçek TUPRS duyurusu üzerinde uçtan uca canlı doğrulandı — özetler doğru ve kaynak metne sadık.
- LLM sağlayıcısı Gemini'den Groq'a taşındı: `ai/summaries/morning_briefing.py` ve `ai/summaries/announcement_summary.py` artık `groq` SDK'sı (`Groq` client, OpenAI-uyumlu `chat.completions.create`) ile `GROQ_API_KEY` kullanıyor, model `llama-3.3-70b-versatile`. `GEMINI_API_KEY`/`google-generativeai` tamamen kaldırıldı (`.env`, `.env.example`, `requirements.txt`).
- Dil sızıntısı düzeltmesi: model (`llama-3.3-70b-versatile`) `temperature=0.3`'te bile Türkçe metne ara sıra Çince/İngilizce kelime karıştırmaya devam etti (canlı kullanımda gözlemlendi, ör. "注意 edin"). İki sistem promptuna da en üste açık bir "DİL" kuralı eklendi (sadece Türkçe, başka dilden tek kelime/karakter bile yasak) ve `temperature` 0.3'ten 0.1'e düşürüldü. Gerçek anahtarla 5+5 (brifing + duyuru özeti) ardışık canlı çağrıda hiçbirinde yabancı dil karışması görülmedi. Ayrıca `ai/summaries/language_guard.py:find_non_turkish_script()` eklendi — CJK/Hiragana-Katakana/Hangul/Arapça/Kiril/Tayca/Devanagari kod noktası aralıklarını tarayan, dış bağımlılık gerektirmeyen bir runtime koruma katmanı. `generate_morning_briefing()` ve `generate_announcement_summary()` model yanıtını döndürmeden önce bu taramadan geçiriyor; sızıntı tespit edilirse sonuç kullanıcıya gösterilmez, `hata` durumu döner. Not: sadece betik (script) değişimini yakalar, Latin alfabesiyle yazılmış İngilizce bir kelimeyi yakalamaz — canlı testle (mock kirli yanıt enjekte edilerek) tetiklendiği doğrulandı.

- TUPRS finansal verisine gerçek ikinci kaynak: kullanıcı, tek kaynaklı veriye (`source_count<=1`) otomatik "Düşük" güven bandı verilmesine itiraz etti ("yfinance kesin veri çekiyor"). Buna karşı İş Yatırım'ın (isyatirim.com.tr) kamuya açık, kimlik doğrulama gerektirmeyen finansal tablo endpoint'i (`.../Common/Data.aspx/MaliTablo`, `isyatirimhisse` PyPI paketinden doğrulandı) araştırılıp entegre edildi. Yeni `collectors/kap/tuprs_financials_isyatirim.py`, yfinance'ten (birincil kaynak, `collectors/kap/tuprs_financials.py`) SONRA çalışıp aynı `company_financials` satırını İş Yatırım'ın ham bilanço/gelir tablosu kalemleriyle (nakit/borç/özkaynak/net kâr/FAVÖK/vergi — itemCode bazlı) çapraz kontrol ediyor; `roe/roic/debt/cash` sütunlarına dokunmuyor (görüntülenen sayılar hâlâ yfinance'in), sadece yeni `source_count`/`has_conflicting_data` kolonlarını (bkz. `database/migrations/0002_add_financials_source_tracking.sql`, `backend/models/company_financials.py`) dolduruyor — >%15 bağıl fark varsa çelişki işaretleniyor. `backend/services/company_service.py` artık bu gerçek değerleri `analyze_company()`'e geçiriyor (önceden hep varsayılan `1`/`False`'du). Canlı TUPRS verisiyle uçtan uca doğrulandı: ROE/ROIC'te gerçek ve anlamlı bir sapma bulundu (ROE %8.1 vs %10.4, ROIC %9.1 vs %14.2 — borç/nakit ise %1-10 aralığında tutarlı), `has_conflicting_data=True` çıktı, güven ham skoru 57.1'den 28.6'ya düştü (`raw *= 0.5` çelişki cezası) — band hâlâ "Düşük" ama artık "tek kaynak" yerine "kaynaklar çelişiyor" gerekçesiyle, bu bilgi `source` alanında görünür. Frontend değişmedi (`AtlasScoreCard`/`CompanyFinancialsCard` zaten var olan alanları gösteriyor). Temettü verimi kapsam dışı bırakıldı — İş Yatırım'ın bu endpoint'inde yok, hâlâ yfinance-only.

**Sırada:**
- Master prompt'un 9 adımı, sabah brifingi LLM entegrasyonu, KAP metin temizliği + duyuru özeti, Gemini→Groq geçişi ve TUPRS finansal verisine ikinci kaynak eklenmesi tamamlandı; şu an için belirlenmiş yeni bir adım yok.

**Bilinen açık noktalar:**
- `scripts/legacy_portfolio_tracker/` içindeki importlar kırık (kasıtlı olarak dokunulmadı).
- İş Yatırım'ın `MaliTablo` endpoint'i resmi/dokümante değil (açık kaynak bir pakette doğrulanmış, kimlik doğrulama gerektirmeyen genel bir uç nokta) — KAP entegrasyonundaki gibi düşük hacimli/nazik kullanım gerekiyor, ayrıca URL/parametre şekli habersiz değişebilir.

## Kapsam dışı — dokunma

Etki Analizi, Senaryo Motoru, Yatırım Mahkemesi, Tez Takibi, diğer 6 şirket (sadece
TUPRS pilot), Ekonomi Akademisi, kişiselleştirme, `causal_relationships` tablosu.
Bu modüllerden birine dokunman gerekecek gibi görünürse, kod yazmadan önce dur ve sor.

## Zorunlu kurallar

- Her veri satırında `fetched_at` zorunlu.
- Güven skoru kullanıcıya ham sayı olarak gösterilmez — bant (Düşük/Orta/Yüksek) + parantez içinde sayı.
- Veri eksikse sahte skor/sonuç üretme, "yetersiz veri" dön.

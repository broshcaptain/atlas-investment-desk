# Atlas — Yol Haritası ve Durum

> Kaynak: `docs/ATLAS_MASTER_PROMPT_v1.1.md` (v1.1 MVP) — İlk Geliştirme Görevi;
> `CLAUDE.md` — Durum. Bu dosya, `CLAUDE.md`'deki "Durum" bölümüyle birlikte
> güncel tutulmalı.

## İlk Geliştirme Görevi (9 adım)

1. Proje iskeletini klasör yapısına göre kur (bkz. `docs/architecture.md`).
2. PostgreSQL şemasını `database/migrations/` altında oluştur (yukarıdaki 10
   tablo, bkz. `docs/architecture.md`).
3. `collectors/market/` için temel fiyat verisi çekme betiklerini yaz
   (USDTRY, EURTRY, altın, Brent, BIST100).
4. `collectors/kap/` için TUPRS'e özel KAP çekme betiğini yaz — hem duyuru
   metni hem temel finansal veriyi (`company_financials`) doldursun.
5. `backend/` üzerinde minimal FastAPI iskeleti kur — `/dashboard`,
   `/companies/tuprs` endpoint'leri.
6. `ai/analyzers/company_analyzer.py` içinde buffett_tr/lynch_tr/graham_tr/
   dalio_tr çerçevelerini `company_financials`'a uygulayıp `atlas_score`
   üret. Veri eksikse skor yerine "yetersiz veri" döner — sahte skor
   üretilmez.
7. `ai/summaries/` içinde sabah brifingi üretecek basit bir prompt +
   fonksiyon yaz (henüz canlı veri toplama tamamlanmadan mock veriyle test
   edilebilir).
8. `frontend/app/dashboard/` üzerinde piyasa özeti ve brifing kartını
   gösteren minimal arayüz kur.
9. `frontend/app/companies/tuprs` üzerinde atlas_score ve KAP özetlerini
   gösteren şirket sayfasını kur.

Her adımdan sonra dur, ne yapıldığını özetle, bir sonrakine geçmeden onay al.

---

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
- `docs/` içeriği `product.md`/`architecture.md`/`investment_rules.md`/`roadmap.md` olarak bölündü (bu dosyalar) — kaynak: `ATLAS_MASTER_PROMPT_v1.1.md` ve `CLAUDE.md`.

**Sırada:**
- Sabah brifingi için gerçek LLM entegrasyonu (Claude API — SDK/`.env` anahtarı) henüz yapılmadı, şu an sadece prompt üretiliyor; frontend'de de bu yüzden placeholder durumda.

**Bilinen açık noktalar:**
- `scripts/legacy_portfolio_tracker/` içindeki importlar kırık (kasıtlı olarak dokunulmadı).
- KAP içerik metni yapılandırılmış duyurularda ham XBRL taksonomi etiketleri içeriyor (temiz düzyazı değil).

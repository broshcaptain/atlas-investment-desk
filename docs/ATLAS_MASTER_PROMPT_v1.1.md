# Atlas — Claude Code Master Prompt (v1.1 MVP)

Bu doküman Claude Code'a verilecek ilk proje talimatıdır. Aşağıdaki her bölüm, projenin `docs/` klasörüne de ayrı ayrı konulmalıdır (`product.md`, `architecture.md`, `investment_rules.md`, `roadmap.md`).

v1.1'de eklenen 5 düzeltme, sistemin kendi tasarım risklerine karşı önlem: yanıltıcı kesinlik, sahte bağımsız denetim, döngüsel doğrulama, kapsam kayması, veri bayatlığı. Her biri aşağıda ilgili bölümde işaretli.

---

## Ürün Tanımı

Atlas, tek kullanıcı için tasarlanmış profesyonel bir yatırım araştırma masaüstü uygulamasıdır. Amaç hisse önermek değil, kullanıcının kendi yatırım kararlarının kalitesini artırmaktır.

**Sistem şunu asla yapmaz:** al/sat tavsiyesi, kesinlik iddiası ("kesin yükselecek"), kaynaksız iddia.
**Sistem şunu yapar:** veriyi gösterir, olası yorumu ("olabilir" dili ile) sunar, kaynağı belirtir.

---

## Teknoloji Yığını

- **Backend:** Python, FastAPI
- **Frontend:** Next.js, TypeScript
- **Database:** PostgreSQL
- **Paket yönetimi:** backend için `uv` veya `poetry`, frontend için `npm`

---

## Klasör Yapısı

```text
atlas/
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── macro/
│   │   ├── companies/
│   │   ├── thesis/
│   │   └── settings/
│   ├── components/
│   ├── services/
│   └── types/
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── jobs/
│   └── config/
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   └── schema/
│
├── collectors/
│   ├── kap/
│   ├── tcmb/
│   ├── market/
│   ├── news/
│   └── company_reports/
│
├── ai/
│   ├── prompts/
│   ├── analyzers/
│   ├── validators/
│   └── summaries/
│
├── docs/
│   ├── product.md
│   ├── architecture.md
│   ├── investment_rules.md
│   └── roadmap.md
│
└── scripts/
```

---

## Veritabanı — İlk Sürüm Tabloları

```text
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

**Not:** `causal_relationships` (sebep-sonuç veritabanı) bilinçli olarak v1 kapsamı dışında bırakıldı — Etki Analizi modülü (Faz 2) ile birlikte eklenecek. Şimdiden isim rezerve edildi, `analysis` tablosuyla karıştırılmayacak.

**[Düzeltme 1 — veri bayatlığı]** Her veri tablosunda (`market_data`, `macro_data`, `kap_announcements`, `news`) `fetched_at` alanı zorunlu. Frontend her kartta "X dakika/saat önce güncellendi" gösterir. Toplayıcı başarısız olursa veya veri N saatten eskiyse, kart açıkça "veri bayat" uyarısı taşır — sessizce eski veriyle brifing üretilmez.

**[Düzeltme 3 — döngüsel doğrulama, Faz 2 için şimdiden hazırlık]** `causal_relationships` eklendiğinde `status` alanı taşıyacak: `proposed` (AI önerdi) / `approved` (kullanıcı onayladı). Sadece `approved` satırlar `impact_analyzer.py` tarafından kanıt olarak kullanılabilir. AI kendi önerisini kendi analizinde referans gösteremez.

---

## MVP Kapsamı — Sadece Bunlar

```text
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

**Kapsam dışı (Faz 2+):** Etki Analizi, Senaryo Motoru, Yatırım Mahkemesi, Tez Takibi, diğer 6 şirket, Ekonomi Akademisi, kişiselleştirme.

Claude Code bu sınırın dışına çıkmamalı. Kapsam genişletme isteği gelirse önce kullanıcıya sorulmalı.

---

## Kanıt Gösteren AI — Zorunlu Kurallar

`ai/validators/` bu kuralları uygular, her AI çıktısı bunlardan geçer:

1. Her iddianın kaynağı olacak (`sources` tablosuna referans).
2. Veri ve yorum ayrılacak — yorum cümleleri "olabilir" dili kullanır, kesinlik iddia etmez.
3. Her analizin güven skoru olacak, gerekçesiyle birlikte.
4. Tek kaynaklı bilgi düşük güven skoruyla işaretlenir.
5. Yeterli veri yoksa sistem "bilmiyorum" diyebilmeli — uydurma cevap üretmemeli.

**[Düzeltme 2 — yanıltıcı kesinlik]** Güven skoru tek başına sayı olarak gösterilmez. Her skorun yanında zorunlu üç bileşen görünür: kaynak sayısı, çelişkili veri var mı, veri yaşı. UI'da sayı yerine bant kullanılır: Düşük / Orta / Yüksek + parantez içinde ham sayı (`Orta (58/100)`). Amaç: kullanıcının sayıyı ölçülmüş bir olasılık sanmasını önlemek.

**[Düzeltme — kapsam disiplini]** Claude Code, MVP dışı bir modülün (Yatırım Mahkemesi, Etki Analizi, causal_relationships vb.) koduna dokunmadan önce durur ve kullanıcıya sorar. "Madem buradayım, şunu da ekleyeyim" davranışı yasak.

---

## İlk Geliştirme Görevi (Claude Code için)

1. Proje iskeletini yukarıdaki klasör yapısına göre kur.
2. PostgreSQL şemasını `database/migrations/` altında oluştur (yukarıdaki 10 tablo).
3. `collectors/market/` için temel fiyat verisi çekme betiklerini yaz (USDTRY, EURTRY, altın, Brent, BIST100).
4. `collectors/kap/` için TUPRS'e özel KAP çekme betiğini yaz — hem duyuru metni hem temel finansal veriyi (`company_financials`) doldursun.
5. `backend/` üzerinde minimal FastAPI iskeleti kur — `/dashboard`, `/companies/tuprs` endpoint'leri.
6. `ai/analyzers/company_analyzer.py` içinde buffett_tr/lynch_tr/graham_tr/dalio_tr çerçevelerini `company_financials`'a uygulayıp `atlas_score` üret. Veri eksikse skor yerine "yetersiz veri" döner — sahte skor üretilmez.
7. `ai/summaries/` içinde sabah brifingi üretecek basit bir prompt + fonksiyon yaz (henüz canlı veri toplama tamamlanmadan mock veriyle test edilebilir).
8. `frontend/app/dashboard/` üzerinde piyasa özeti ve brifing kartını gösteren minimal arayüz kur.
9. `frontend/app/companies/tuprs` üzerinde atlas_score ve KAP özetlerini gösteren şirket sayfasını kur.

Her adımdan sonra dur, ne yapıldığını özetle, bir sonrakine geçmeden onay al.

---

## Bilinen Riskler — Faz 2 Öncesi Not

**Yatırım Mahkemesi'nin bağımsızlığı sınırlı.** Boğa/ayı/hakem aynı temel modelden çalışırsa, bu gerçek bağımsız denetim değil, tek modelin kendi kendine itirazıdır — aynı kör noktaları paylaşabilirler. Faz 2'de bu modül eklenirken arayüzde "üç bağımsız görüş" değil, "AI'ın kendi çapraz sorgulaması" olarak adlandırılmalı; kullanıcı yanlış bir bağımsızlık algısına kapılmamalı.

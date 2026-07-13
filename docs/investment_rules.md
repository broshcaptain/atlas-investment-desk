# Atlas — Yatırım / AI Kuralları

> Kaynak: `docs/ATLAS_MASTER_PROMPT_v1.1.md` (v1.1 MVP) — Kanıt Gösteren AI,
> Bilinen Riskler bölümleri; `CLAUDE.md` — Zorunlu kurallar.

## Kanıt Gösteren AI — Zorunlu Kurallar

`ai/validators/` bu kuralları uygular, her AI çıktısı bunlardan geçer:

1. Her iddianın kaynağı olacak (`sources` tablosuna referans).
2. Veri ve yorum ayrılacak — yorum cümleleri "olabilir" dili kullanır, kesinlik
   iddia etmez.
3. Her analizin güven skoru olacak, gerekçesiyle birlikte.
4. Tek kaynaklı bilgi düşük güven skoruyla işaretlenir.
5. Yeterli veri yoksa sistem "bilmiyorum" diyebilmeli — uydurma cevap
   üretmemeli.

## Zorunlu kurallar (uygulama genelinde)

- Her veri satırında `fetched_at` zorunlu.
- Güven skoru kullanıcıya ham sayı olarak gösterilmez — bant
  (Düşük/Orta/Yüksek) + parantez içinde sayı.
- Veri eksikse sahte skor/sonuç üretme, "yetersiz veri" dön.

**[Düzeltme 2 — yanıltıcı kesinlik]** Güven skoru tek başına sayı olarak
gösterilmez. Her skorun yanında zorunlu üç bileşen görünür: kaynak sayısı,
çelişkili veri var mı, veri yaşı. UI'da sayı yerine bant kullanılır:
Düşük / Orta / Yüksek + parantez içinde ham sayı (`Orta (58/100)`). Amaç:
kullanıcının sayıyı ölçülmüş bir olasılık sanmasını önlemek.

Uygulama: `ai/analyzers/company_analyzer.py` → `atlas_score`/`confidence`
(`band`/`raw`/`source_count`/`has_conflicting_data`/`data_age_days`),
`frontend/components/AtlasScoreCard.tsx` bandı + parantez içi ham sayıyı
render eder.

**[Düzeltme — kapsam disiplini]** Claude Code, MVP dışı bir modülün (Yatırım
Mahkemesi, Etki Analizi, `causal_relationships` vb.) koduna dokunmadan önce
durur ve kullanıcıya sorar. "Madem buradayım, şunu da ekleyeyim" davranışı
yasak. (Kapsam sınırları için bkz. `docs/product.md` — Kapsam dışı.)

## Bilinen Riskler — Faz 2 Öncesi Not

**Yatırım Mahkemesi'nin bağımsızlığı sınırlı.** Boğa/ayı/hakem aynı temel
modelden çalışırsa, bu gerçek bağımsız denetim değil, tek modelin kendi
kendine itirazıdır — aynı kör noktaları paylaşabilirler. Faz 2'de bu modül
eklenirken arayüzde "üç bağımsız görüş" değil, "AI'ın kendi çapraz
sorgulaması" olarak adlandırılmalı; kullanıcı yanlış bir bağımsızlık algısına
kapılmamalı.

-- Atlas — Initial schema (MVP, v1.1 master prompt)
-- Kapsam: docs/product.md / architecture.md / investment_rules.md'de tanımlanan 10 tablo.
-- NOT: causal_relationships bilinçli olarak burada YOK — Faz 2 (Etki Analizi) kapsamında eklenecek.
--      İsim şimdiden rezerve edilmiştir, `analysis` tablosuyla karıştırılmamalıdır.

-- ---------------------------------------------------------------------------
-- companies — kod, sektör, alt sektör
-- ---------------------------------------------------------------------------
CREATE TABLE companies (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) NOT NULL UNIQUE,   -- örn: TUPRS
    name        VARCHAR(255) NOT NULL,
    sector      VARCHAR(120),
    sub_sector  VARCHAR(120),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- market_data — fiyat/endeks anlık veri
-- [Düzeltme 1] fetched_at zorunlu — veri bayatlığı UI'da bu alandan hesaplanır.
-- ---------------------------------------------------------------------------
CREATE TABLE market_data (
    id          SERIAL PRIMARY KEY,
    symbol      VARCHAR(20) NOT NULL,          -- örn: USDTRY, BIST100, TUPRS.IS
    price       NUMERIC(18, 6) NOT NULL,
    source      VARCHAR(120) NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_market_data_symbol_fetched_at ON market_data (symbol, fetched_at DESC);

-- ---------------------------------------------------------------------------
-- macro_data — TCMB, enflasyon, faiz, CDS vb. — tarih, değer, kaynak
-- [Düzeltme 1] fetched_at zorunlu.
-- ---------------------------------------------------------------------------
CREATE TABLE macro_data (
    id          SERIAL PRIMARY KEY,
    indicator   VARCHAR(120) NOT NULL,         -- örn: enflasyon, politika_faizi, cds
    value       NUMERIC(18, 6) NOT NULL,
    as_of_date  DATE NOT NULL,                 -- verinin ait olduğu tarih
    source      VARCHAR(120) NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_macro_data_indicator_as_of ON macro_data (indicator, as_of_date DESC);

-- ---------------------------------------------------------------------------
-- kap_announcements — şirket, tarih, kategori, içerik, ai_summary
-- [Düzeltme 1] fetched_at zorunlu. Ham içerik ve AI özeti ayrı kolonlarda tutulur.
-- ---------------------------------------------------------------------------
CREATE TABLE kap_announcements (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER NOT NULL REFERENCES companies(id),
    announced_at    TIMESTAMPTZ NOT NULL,
    category        VARCHAR(120),
    content         TEXT NOT NULL,             -- ham duyuru metni
    ai_summary      TEXT,                      -- AI özeti (henüz üretilmemişse NULL)
    source_url      TEXT,
    fetched_at      TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_kap_announcements_company ON kap_announcements (company_id, announced_at DESC);

-- ---------------------------------------------------------------------------
-- news — başlık, kaynak, tarih, içerik, ai_summary (ham ve özet ayrı tutulur)
-- [Düzeltme 1] fetched_at zorunlu.
-- ---------------------------------------------------------------------------
CREATE TABLE news (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(500) NOT NULL,
    source          VARCHAR(120) NOT NULL,
    published_at    TIMESTAMPTZ NOT NULL,
    content         TEXT NOT NULL,             -- ham haber metni
    ai_summary      TEXT,                      -- AI özeti (henüz üretilmemişse NULL)
    fetched_at      TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_news_published_at ON news (published_at DESC);

-- ---------------------------------------------------------------------------
-- investment_thesis — şirket, neden aldım, riskler, satış koşulu
-- ---------------------------------------------------------------------------
CREATE TABLE investment_thesis (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER NOT NULL REFERENCES companies(id),
    reason          TEXT NOT NULL,             -- neden aldım
    risks           TEXT,
    sell_condition  TEXT,                      -- satış koşulu
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- events — ne oldu, neden oldu, neyi etkiler, kaynak
-- ---------------------------------------------------------------------------
CREATE TABLE events (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(500) NOT NULL,
    what_happened   TEXT NOT NULL,             -- ne oldu
    why_happened    TEXT,                      -- neden oldu
    impact          TEXT,                      -- neyi etkiler
    source          VARCHAR(255),
    occurred_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- sources — her iddianın referans aldığı kaynak kaydı
-- ---------------------------------------------------------------------------
CREATE TABLE sources (
    id              SERIAL PRIMARY KEY,
    url             TEXT,
    title           VARCHAR(500),
    published_at    TIMESTAMPTZ,
    retrieved_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    reliability_note TEXT
);

-- ---------------------------------------------------------------------------
-- analysis — AI çıktıları — güven skoru, kaynak sayısı dahil
-- [Düzeltme 2] Güven skoru tek başına gösterilmez; kaynak sayısı, çelişkili veri
-- olup olmadığı ve veri yaşı burada birlikte tutulur — UI bu üç bileşeni bant
-- olarak gösterir (Düşük/Orta/Yüksek + ham sayı).
-- ---------------------------------------------------------------------------
CREATE TABLE analysis (
    id                      SERIAL PRIMARY KEY,
    company_id              INTEGER REFERENCES companies(id),
    analysis_type           VARCHAR(60) NOT NULL,   -- örn: atlas_score, morning_briefing
    output                  TEXT NOT NULL,
    confidence_score        NUMERIC(5, 2),          -- 0-100, NULL = yetersiz veri
    source_count            INTEGER NOT NULL DEFAULT 0,
    has_conflicting_data    BOOLEAN NOT NULL DEFAULT false,
    data_age_hours          NUMERIC(10, 2),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- analysis <-> sources (çoktan çoğa: bir analiz birden çok kaynağa dayanır)
CREATE TABLE analysis_sources (
    analysis_id     INTEGER NOT NULL REFERENCES analysis(id),
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    PRIMARY KEY (analysis_id, source_id)
);

-- ---------------------------------------------------------------------------
-- company_financials — şirket, dönem, roe, roic, borç, nakit, temettü verimi, kaynak
-- (Buffett/Lynch/Graham/Dalio TR skorunu besler)
-- [Düzeltme 1] fetched_at zorunlu.
-- ---------------------------------------------------------------------------
CREATE TABLE company_financials (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER NOT NULL REFERENCES companies(id),
    period          VARCHAR(20) NOT NULL,      -- örn: 2025-Q4
    roe             NUMERIC(10, 4),
    roic            NUMERIC(10, 4),
    debt            NUMERIC(18, 2),
    cash            NUMERIC(18, 2),
    dividend_yield  NUMERIC(10, 4),
    source          VARCHAR(120) NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (company_id, period)
);

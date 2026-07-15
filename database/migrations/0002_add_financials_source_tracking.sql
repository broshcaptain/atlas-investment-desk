-- Atlas — company_financials'a çoklu-kaynak takibi ekle
-- Bağlam: atlas_score'un güven bandı, source_count<=1 olduğunda otomatik
-- "Düşük"e sabitleniyor (ai/analyzers/company_analyzer.py). TUPRS finansal
-- verisi tek kaynaklıydı (yfinance); bu iki kolon, ikinci bağımsız bir
-- kaynakla (İş Yatırım) çapraz kontrol yapıldığında gerçek kaynak sayısını
-- ve kaynaklar arasında anlamlı bir sapma bulunup bulunmadığını taşır.
-- Görüntülenen roe/roic/debt/cash değerleri değişmiyor — bu kolonlar sadece
-- güven skoru hesabını besler, sessizce bir "harmanlanmış" sayı üretmez.

ALTER TABLE company_financials ADD COLUMN source_count INTEGER NOT NULL DEFAULT 1;
ALTER TABLE company_financials ADD COLUMN has_conflicting_data BOOLEAN NOT NULL DEFAULT false;

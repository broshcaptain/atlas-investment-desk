export type MarketMeta = {
  label: string;
  unit: string;
};

const MARKET_META: Record<string, MarketMeta> = {
  USDTRY: { label: "USD/TRY", unit: "₺" },
  EURTRY: { label: "EUR/TRY", unit: "₺" },
  XAUUSD: { label: "Ons Altın", unit: "$" },
  GRAMALTIN: { label: "Gram Altın", unit: "₺" },
  BRENT: { label: "Brent Petrol", unit: "$" },
  BIST100: { label: "BIST 100", unit: "" },
};

// Dashboard'da gösterilecek sabit sıra — master prompt'taki piyasa özeti sırasıyla eşleşir.
export const MARKET_DISPLAY_ORDER = [
  "USDTRY",
  "EURTRY",
  "GRAMALTIN",
  "XAUUSD",
  "BRENT",
  "BIST100",
];

export function getMarketMeta(symbol: string): MarketMeta {
  return MARKET_META[symbol] ?? { label: symbol, unit: "" };
}

export type MarketItem = {
  symbol: string;
  price: number;
  source: string;
  fetched_at: string;
};

export type Briefing =
  | { status: "ok"; text: string; generated_at: string }
  | { status: "yetersiz_veri" | "anahtar_eksik" | "hata"; message: string };

export type DashboardResponse = {
  items: MarketItem[];
  briefing: Briefing;
};

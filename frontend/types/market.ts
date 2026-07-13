export type MarketItem = {
  symbol: string;
  price: number;
  source: string;
  fetched_at: string;
};

export type DashboardResponse = {
  items: MarketItem[];
};

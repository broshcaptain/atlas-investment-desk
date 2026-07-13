import type { DashboardResponse } from "@/types/market";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function getMarketSummary(): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE_URL}/dashboard`, { cache: "no-store" });

  if (!res.ok) {
    throw new Error(`/dashboard isteği başarısız oldu: ${res.status}`);
  }

  return res.json();
}

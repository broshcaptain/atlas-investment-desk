import type { CompanyOverview } from "@/types/company";
import type { DashboardResponse } from "@/types/market";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function getMarketSummary(): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE_URL}/dashboard`, { cache: "no-store" });

  if (!res.ok) {
    throw new Error(`/dashboard isteği başarısız oldu: ${res.status}`);
  }

  return res.json();
}

// 404 -> null (yetersiz veri): backend, şirket kaydı yoksa bu koda düşer.
// Diğer hata kodları gerçek bir arıza olduğundan fırlatılır.
export async function getCompanyOverview(code: string): Promise<CompanyOverview | null> {
  const res = await fetch(`${API_BASE_URL}/companies/${code}`, { cache: "no-store" });

  if (res.status === 404) {
    return null;
  }

  if (!res.ok) {
    throw new Error(`/companies/${code} isteği başarısız oldu: ${res.status}`);
  }

  return res.json();
}

import { BriefingCard } from "@/components/BriefingCard";
import { MarketTile } from "@/components/MarketTile";
import { getMarketSummary } from "@/lib/api";
import { MARKET_DISPLAY_ORDER } from "@/lib/market-meta";
import type { MarketItem } from "@/types/market";

function sortByDisplayOrder(items: MarketItem[]): MarketItem[] {
  return [...items].sort(
    (a, b) => MARKET_DISPLAY_ORDER.indexOf(a.symbol) - MARKET_DISPLAY_ORDER.indexOf(b.symbol),
  );
}

export default async function DashboardPage() {
  let items: MarketItem[] = [];
  let error: string | null = null;

  try {
    const dashboard = await getMarketSummary();
    items = sortByDisplayOrder(dashboard.items);
  } catch (e) {
    error = e instanceof Error ? e.message : "Bilinmeyen hata";
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-6 py-10">
      <header>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Atlas — Dashboard</h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">Piyasa özeti ve sabah brifingi.</p>
      </header>

      <section aria-labelledby="market-heading" className="flex flex-col gap-3">
        <h2 id="market-heading" className="text-sm font-medium text-[var(--text-secondary)]">
          Piyasa Özeti
        </h2>

        {error && (
          <div className="rounded-lg border border-[var(--status-critical)] bg-[var(--surface-1)] p-4 text-sm text-[var(--text-primary)]">
            Piyasa verisi alınamadı: {error}
          </div>
        )}

        {!error && items.length === 0 && (
          <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4 text-sm text-[var(--text-secondary)]">
            Yetersiz veri — henüz piyasa verisi toplanmamış.
          </div>
        )}

        {items.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <MarketTile key={item.symbol} item={item} />
            ))}
          </div>
        )}
      </section>

      <section aria-labelledby="briefing-heading" className="flex flex-col gap-3">
        <h2 id="briefing-heading" className="text-sm font-medium text-[var(--text-secondary)]">
          Sabah Brifingi
        </h2>
        <BriefingCard />
      </section>
    </main>
  );
}

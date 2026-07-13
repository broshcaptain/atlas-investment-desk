import { getFreshness } from "@/lib/freshness";
import { getMarketMeta } from "@/lib/market-meta";
import type { MarketItem } from "@/types/market";

const priceFormatter = new Intl.NumberFormat("tr-TR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function MarketTile({ item }: { item: MarketItem }) {
  const meta = getMarketMeta(item.symbol);
  const freshness = getFreshness(item.fetched_at);

  return (
    <div className="flex flex-col gap-1 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
      <span className="text-sm text-[var(--text-secondary)]">{meta.label}</span>
      <span className="text-2xl font-semibold text-[var(--text-primary)]">
        {priceFormatter.format(item.price)}
        {meta.unit && (
          <span className="ml-1 text-base font-normal text-[var(--text-secondary)]">
            {meta.unit}
          </span>
        )}
      </span>
      <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
        <span>{freshness.label}</span>
        <span aria-hidden="true">·</span>
        <span>{item.source}</span>
      </div>
      {freshness.stale && (
        <div className="mt-1 flex w-fit items-center gap-1.5 text-xs font-medium text-[var(--text-secondary)]">
          <span className="h-2 w-2 rounded-full bg-[var(--status-warning)]" aria-hidden="true" />
          <span>Veri bayat</span>
        </div>
      )}
    </div>
  );
}

import { getFreshness } from "@/lib/freshness";
import type { Financials } from "@/types/company";

const percentFormatter = new Intl.NumberFormat("tr-TR", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const currencyFormatter = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 });

function formatPercent(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : percentFormatter.format(value);
}

function formatCurrency(value: number | null | undefined): string {
  return value === null || value === undefined ? "—" : `${currencyFormatter.format(value)} ₺`;
}

export function CompanyFinancialsCard({ financials }: { financials: Financials }) {
  if (financials.status === "yetersiz veri" || !financials.fetched_at) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface-1)] p-5">
        <span className="text-sm text-[var(--text-secondary)]">Temel Finansal Veriler</span>
        <p className="text-base text-[var(--text-primary)]">Yetersiz veri.</p>
      </div>
    );
  }

  const freshness = getFreshness(financials.fetched_at);
  const rows: { label: string; value: string }[] = [
    { label: "ROE", value: formatPercent(financials.roe) },
    { label: "ROIC", value: formatPercent(financials.roic) },
    { label: "Borç", value: formatCurrency(financials.debt) },
    { label: "Nakit", value: formatCurrency(financials.cash) },
    { label: "Temettü Verimi", value: formatPercent(financials.dividend_yield) },
  ];

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm text-[var(--text-secondary)]">
          Temel Finansal Veriler{financials.period ? ` — ${financials.period}` : ""}
        </span>
        {freshness.stale && (
          <div className="flex items-center gap-1.5 text-xs font-medium text-[var(--text-secondary)]">
            <span className="h-2 w-2 rounded-full bg-[var(--status-warning)]" aria-hidden="true" />
            <span>Veri bayat</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {rows.map((row) => (
          <div key={row.label} className="flex flex-col gap-0.5">
            <span className="text-xs text-[var(--text-muted)]">{row.label}</span>
            <span className="text-base font-medium text-[var(--text-primary)]">{row.value}</span>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
        <span>{freshness.label}</span>
        {financials.source && (
          <>
            <span aria-hidden="true">·</span>
            <span>{financials.source}</span>
          </>
        )}
      </div>
    </div>
  );
}

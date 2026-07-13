import { AnnouncementCard } from "@/components/AnnouncementCard";
import { AtlasScoreCard } from "@/components/AtlasScoreCard";
import { CompanyFinancialsCard } from "@/components/CompanyFinancialsCard";
import { getCompanyOverview } from "@/lib/api";
import type { CompanyOverview } from "@/types/company";

export default async function TuprsPage() {
  let overview: CompanyOverview | null = null;
  let error: string | null = null;

  try {
    overview = await getCompanyOverview("tuprs");
  } catch (e) {
    error = e instanceof Error ? e.message : "Bilinmeyen hata";
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-6 py-10">
      <header className="flex flex-col gap-1">
        <a
          href="/dashboard"
          className="text-sm text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
        >
          ← Dashboard
        </a>
        {overview ? (
          <>
            <h1 className="text-2xl font-semibold text-[var(--text-primary)]">
              {overview.company.name}{" "}
              <span className="text-[var(--text-muted)]">({overview.company.code})</span>
            </h1>
            <p className="text-sm text-[var(--text-secondary)]">
              {[overview.company.sector, overview.company.sub_sector].filter(Boolean).join(" · ") ||
                "Sektör bilgisi yok"}
            </p>
          </>
        ) : (
          <h1 className="text-2xl font-semibold text-[var(--text-primary)]">TUPRS</h1>
        )}
      </header>

      {error && (
        <div className="rounded-lg border border-[var(--status-critical)] bg-[var(--surface-1)] p-4 text-sm text-[var(--text-primary)]">
          Şirket verisi alınamadı: {error}
        </div>
      )}

      {!error && !overview && (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4 text-sm text-[var(--text-secondary)]">
          Yetersiz veri — TUPRS için şirket verisi bulunamadı.
        </div>
      )}

      {overview && (
        <>
          <section aria-labelledby="atlas-score-heading" className="flex flex-col gap-3">
            <h2 id="atlas-score-heading" className="text-sm font-medium text-[var(--text-secondary)]">
              Atlas Score
            </h2>
            <AtlasScoreCard atlasScore={overview.atlas_score} />
          </section>

          <section aria-labelledby="financials-heading" className="flex flex-col gap-3">
            <h2 id="financials-heading" className="text-sm font-medium text-[var(--text-secondary)]">
              Temel Finansal Veriler
            </h2>
            <CompanyFinancialsCard financials={overview.financials} />
          </section>

          <section aria-labelledby="announcements-heading" className="flex flex-col gap-3">
            <h2 id="announcements-heading" className="text-sm font-medium text-[var(--text-secondary)]">
              Son KAP Duyuruları
            </h2>
            {overview.recent_announcements.length === 0 ? (
              <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4 text-sm text-[var(--text-secondary)]">
                Yetersiz veri — henüz KAP duyurusu toplanmamış.
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {overview.recent_announcements.map((announcement, index) => (
                  <AnnouncementCard
                    key={`${announcement.announced_at}-${index}`}
                    announcement={announcement}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}

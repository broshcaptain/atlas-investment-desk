import type { AtlasScore } from "@/types/company";

const CONFIDENCE_DOT: Record<string, string> = {
  Yüksek: "bg-[var(--status-good)]",
  Orta: "bg-[var(--status-warning)]",
  Düşük: "bg-[var(--status-serious)]",
};

export function AtlasScoreCard({ atlasScore }: { atlasScore: AtlasScore }) {
  if (atlasScore.status !== "ok" || atlasScore.atlas_score === null) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface-1)] p-5">
        <span className="text-sm text-[var(--text-secondary)]">Atlas Score</span>
        <p className="text-base text-[var(--text-primary)]">Yetersiz veri.</p>
        <p className="text-sm text-[var(--text-muted)]">{atlasScore.message}</p>
      </div>
    );
  }

  const { confidence, frameworks } = atlasScore;

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div className="flex flex-col gap-1">
          <span className="text-sm text-[var(--text-secondary)]">Atlas Score</span>
          <span className="text-3xl font-semibold text-[var(--text-primary)]">
            {atlasScore.atlas_score.toFixed(0)}
            <span className="ml-1 text-base font-normal text-[var(--text-secondary)]">/100</span>
          </span>
        </div>
        {confidence && (
          <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
            <span
              className={`h-2 w-2 rounded-full ${CONFIDENCE_DOT[confidence.band] ?? "bg-[var(--text-muted)]"}`}
              aria-hidden="true"
            />
            <span>
              Güven: {confidence.band} ({confidence.raw.toFixed(0)}/100)
            </span>
          </div>
        )}
      </div>

      <p className="text-sm text-[var(--text-secondary)]">{atlasScore.message}</p>

      {frameworks && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Object.values(frameworks).map((framework) => (
            <div
              key={framework.name}
              className="flex flex-col gap-1.5 rounded-md border border-[var(--border)] p-3"
            >
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-sm font-medium text-[var(--text-primary)]">{framework.name}</span>
                <span className="text-sm text-[var(--text-secondary)]">
                  {framework.score !== null ? `${framework.score.toFixed(0)}/100` : "—"}
                </span>
              </div>
              {framework.missing_criteria.length > 0 && (
                <p className="text-xs text-[var(--text-muted)]">
                  Değerlendirilemeyen: {framework.missing_criteria.join(", ")}
                </p>
              )}
              <p className="text-xs text-[var(--text-muted)]">{framework.note}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { getFreshness } from "@/lib/freshness";
import type { Briefing } from "@/types/market";

const STATUS_MESSAGE: Record<Exclude<Briefing["status"], "ok">, string> = {
  yetersiz_veri: "Yetersiz veri — brifing için piyasa ya da şirket verisi bulunamadı.",
  anahtar_eksik: "Brifing üretilemedi — ANTHROPIC_API_KEY tanımlı değil.",
  hata: "Brifing üretilemedi — bir API hatası oluştu.",
};

export function BriefingCard({ briefing }: { briefing: Briefing }) {
  if (briefing.status !== "ok") {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface-1)] p-5">
        <span className="text-sm text-[var(--text-secondary)]">AI Sabah Brifingi</span>
        <p className="text-base text-[var(--text-primary)]">{STATUS_MESSAGE[briefing.status]}</p>
        <p className="text-sm text-[var(--text-muted)]">{briefing.message}</p>
      </div>
    );
  }

  const freshness = getFreshness(briefing.generated_at);

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[var(--text-secondary)]">AI Sabah Brifingi</span>
        <span className="text-xs text-[var(--text-muted)]">{freshness.label}</span>
      </div>
      <p className="whitespace-pre-line text-sm text-[var(--text-primary)]">{briefing.text}</p>
    </div>
  );
}

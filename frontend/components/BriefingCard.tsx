export function BriefingCard() {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface-1)] p-5">
      <span className="text-sm text-[var(--text-secondary)]">AI Sabah Brifingi</span>
      <p className="text-base text-[var(--text-primary)]">Sabah brifingi henüz aktif değil.</p>
      <p className="text-sm text-[var(--text-muted)]">
        Brifing metni üretimi için LLM entegrasyonu bekleniyor. Prompt ve veri toplama mantığı
        hazır (<code className="font-mono">ai/summaries/morning_briefing.py</code>), ancak henüz
        canlı bir modele bağlı değil.
      </p>
    </div>
  );
}

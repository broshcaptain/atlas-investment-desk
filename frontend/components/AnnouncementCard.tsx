import { getFreshness } from "@/lib/freshness";
import type { Announcement } from "@/types/company";

const dateFormatter = new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" });

export function AnnouncementCard({ announcement }: { announcement: Announcement }) {
  const freshness = getFreshness(announcement.fetched_at);

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-[var(--text-muted)]">
          {dateFormatter.format(new Date(announcement.announced_at))}
        </span>
        {announcement.category && (
          <span className="rounded-full border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--text-secondary)]">
            {announcement.category}
          </span>
        )}
      </div>

      {announcement.ai_summary ? (
        <p className="text-sm text-[var(--text-primary)]">{announcement.ai_summary}</p>
      ) : (
        // ai_summary yoksa ham içerik gösterilir — bilinen sınırlama: yapılandırılmış
        // duyurularda bu ham XBRL taksonomi etiketleri içerebilir, temiz düzyazı değil.
        <p className="line-clamp-4 text-sm text-[var(--text-secondary)]">{announcement.content}</p>
      )}

      <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
        <span>{freshness.label}</span>
        {announcement.source_url && (
          <>
            <span aria-hidden="true">·</span>
            <a
              href={announcement.source_url}
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-[var(--text-secondary)]"
            >
              Kaynak
            </a>
          </>
        )}
      </div>
    </div>
  );
}

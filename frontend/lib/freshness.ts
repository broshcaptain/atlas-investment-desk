const STALE_THRESHOLD_HOURS = 24;

export type Freshness = {
  label: string;
  stale: boolean;
};

// [Düzeltme 1] Veri N saatten eskiyse "veri bayat" olarak işaretlenir —
// sessizce eski veriyle kart gösterilmez. Eşik ai/summaries/morning_briefing.py
// (MARKET_DATA_STALE_HOURS) ile tutarlıdır.
export function getFreshness(fetchedAt: string, now: Date = new Date()): Freshness {
  const diffMs = now.getTime() - new Date(fetchedAt).getTime();
  const diffMinutes = diffMs / 60000;
  const diffHours = diffMinutes / 60;
  const stale = diffHours > STALE_THRESHOLD_HOURS;

  let label: string;
  if (diffMinutes < 1) {
    label = "az önce güncellendi";
  } else if (diffMinutes < 60) {
    label = `${Math.round(diffMinutes)} dakika önce güncellendi`;
  } else if (diffHours < 24) {
    label = `${Math.round(diffHours)} saat önce güncellendi`;
  } else {
    label = `${Math.round(diffHours / 24)} gün önce güncellendi`;
  }

  return { label, stale };
}

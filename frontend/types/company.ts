export type Company = {
  code: string;
  name: string;
  sector: string | null;
  sub_sector: string | null;
};

export type Financials = {
  status?: "yetersiz veri";
  period?: string;
  roe?: number | null;
  roic?: number | null;
  debt?: number | null;
  cash?: number | null;
  dividend_yield?: number | null;
  source?: string;
  fetched_at?: string;
};

export type Confidence = {
  band: string;
  raw: number;
  source_count: number;
  has_conflicting_data: boolean;
  data_age_days: number | null;
  reason: string;
};

export type Framework = {
  name: string;
  score: number | null;
  used_criteria: string[];
  missing_criteria: string[];
  note: string;
};

export type AtlasScore = {
  status: "ok" | "yetersiz_veri";
  atlas_score: number | null;
  confidence: Confidence | null;
  frameworks: Record<string, Framework> | null;
  message: string;
  period?: string;
};

export type Announcement = {
  announced_at: string;
  category: string | null;
  content: string;
  ai_summary: string | null;
  source_url: string | null;
  fetched_at: string;
};

export type CompanyOverview = {
  company: Company;
  financials: Financials;
  atlas_score: AtlasScore;
  recent_announcements: Announcement[];
};

export interface AnalyticsOverview {
  total_applications: number;
  open_positions: number;
  in_pipeline: number;
  hires: number;
  average_time_to_hire_days: number | null;
  offer_acceptance_rate: number | null;
  trends: Record<string, number | null>;
  series: AnalyticsSeriesPoint[];
}

export interface AnalyticsSeriesPoint {
  date: string;
  applications: number;
  hires: number;
}

export interface FunnelStage {
  stage: string;
  count: number;
  conversion_from_prior: number | null;
}

export interface FunnelResponse {
  total: number;
  stages: FunnelStage[];
}

export interface TimeToHireSummary {
  count: number;
  average_days: number | null;
  median_days: number | null;
}

export interface TimeToHireJob extends TimeToHireSummary {
  job_id: string;
  job_title: string;
}

export interface TimeToHireResponse {
  overall: TimeToHireSummary;
  by_job: TimeToHireJob[];
}

export interface SourceEffectivenessRow {
  source: string;
  source_label: string;
  applications: number;
  offers: number;
  hires: number;
  conversion_rate: number | null;
  cost_per_hire: number | null;
}

export interface SourceEffectivenessResponse {
  sources: SourceEffectivenessRow[];
}

export interface TeamActivityRow {
  recruiter_id: string;
  name: string;
  email: string;
  status_updates: number;
  candidates_processed: number;
  interviews_conducted: number;
  hires: number;
  average_response_hours: number | null;
}

export interface TeamActivityResponse {
  recruiters: TeamActivityRow[];
}

export interface AnalyticsDashboardResponse {
  overview: AnalyticsOverview;
  funnel: FunnelResponse;
  time_to_hire: TimeToHireResponse;
  sources: SourceEffectivenessResponse;
  team_activity: TeamActivityResponse;
}

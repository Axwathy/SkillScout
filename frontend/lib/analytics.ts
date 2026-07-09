import { apiFetch } from "@/lib/api";
import { apiClient } from "@/lib/api/client";
import type {
  AnalyticsDashboardResponse,
  AnalyticsOverview,
  FunnelResponse,
  SourceEffectivenessResponse,
  TeamActivityResponse,
  TimeToHireResponse,
} from "@/types/analytics";

interface RangeParams {
  start?: string;
  end?: string;
  job?: string;
}

function rangeQuery(params: RangeParams): string {
  const search = new URLSearchParams();
  if (params.start) search.set("start", params.start);
  if (params.end) search.set("end", params.end);
  if (params.job) search.set("job", params.job);
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function getAnalyticsOverview(
  params: RangeParams = {},
): Promise<AnalyticsOverview> {
  return apiFetch<AnalyticsOverview>(`/api/v1/analytics/overview/${rangeQuery(params)}`, {
    method: "GET",
  });
}

export async function getAnalyticsFunnel(params: RangeParams = {}): Promise<FunnelResponse> {
  return apiFetch<FunnelResponse>(`/api/v1/analytics/funnel/${rangeQuery(params)}`, {
    method: "GET",
  });
}

export async function getAnalyticsTimeToHire(
  params: RangeParams = {},
): Promise<TimeToHireResponse> {
  return apiFetch<TimeToHireResponse>(`/api/v1/analytics/time-to-hire/${rangeQuery(params)}`, {
    method: "GET",
  });
}

export async function getAnalyticsDashboard(
  params: RangeParams = {},
): Promise<AnalyticsDashboardResponse> {
  return apiFetch<AnalyticsDashboardResponse>(`/api/v1/analytics/dashboard/${rangeQuery(params)}`, {
    method: "GET",
  });
}

export async function getAnalyticsSources(
  params: RangeParams = {},
): Promise<SourceEffectivenessResponse> {
  return apiFetch<SourceEffectivenessResponse>(`/api/v1/analytics/sources/${rangeQuery(params)}`, {
    method: "GET",
  });
}

export async function getAnalyticsTeamActivity(
  params: RangeParams = {},
): Promise<TeamActivityResponse> {
  return apiFetch<TeamActivityResponse>(
    `/api/v1/analytics/team-activity/${rangeQuery(params)}`,
    { method: "GET" },
  );
}

export async function getAnalyticsExport(metric: string, params: RangeParams = {}): Promise<Blob> {
  const query = new URLSearchParams();
  query.set("metric", metric);
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.job) query.set("job", params.job);
  const response = await apiClient.get<Blob>(`/api/v1/analytics/export/?${query.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

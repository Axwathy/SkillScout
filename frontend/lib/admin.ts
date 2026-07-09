import { RecruiterProfile, Organization } from "@/types/auth";
import { apiFetch } from "./api";

export async function getAdminRecruiters(status?: string): Promise<RecruiterProfile[]> {
  const query = status ? `?status=${status}` : "";
  return apiFetch<RecruiterProfile[]>(`/api/v1/admin/recruiters/${query}`, { method: "GET" });
}

export async function approveRecruiter(id: string): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`/api/v1/admin/recruiters/${id}/approve/`, { method: "POST" });
}

export async function rejectRecruiter(id: string): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`/api/v1/admin/recruiters/${id}/reject/`, { method: "POST" });
}

export async function getAdminOrganizations(status?: string): Promise<Organization[]> {
  const query = status ? `?status=${status}` : "";
  return apiFetch<Organization[]>(`/api/v1/admin/organizations/${query}`, { method: "GET" });
}

export async function approveOrganization(id: string): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`/api/v1/admin/organizations/${id}/approve/`, { method: "POST" });
}

export async function rejectOrganization(id: string): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`/api/v1/admin/organizations/${id}/reject/`, { method: "POST" });
}

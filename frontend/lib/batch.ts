import { apiFetch } from "@/lib/api";
import type {
  BatchJob,
  BatchPipelineActionPayload,
  BatchProgress,
  ScheduledBatchOperation,
  ScheduledBatchPayload,
} from "@/types/batch";

export async function getBatchHistory(): Promise<BatchJob[]> {
  return apiFetch<BatchJob[]>("/api/v1/batch/", { method: "GET" });
}

export async function getBatchProgress(id: string): Promise<BatchProgress> {
  return apiFetch<BatchProgress>(`/api/v1/batch/${id}/progress/`, { method: "GET" });
}

export async function uploadBatchResumes(jobId: string, files: File[]): Promise<BatchProgress> {
  const formData = new FormData();
  formData.append("job_id", jobId);
  files.forEach((file) => formData.append("files", file));
  return apiFetch<BatchProgress>("/api/v1/batch/upload/", {
    method: "POST",
    body: formData,
  });
}

export async function createBatchScore(jobId: string): Promise<BatchProgress> {
  return apiFetch<BatchProgress>(`/api/v1/batch/score/${jobId}/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function createBatchPipelineAction(
  payload: BatchPipelineActionPayload,
): Promise<BatchProgress> {
  return apiFetch<BatchProgress>("/api/v1/batch/pipeline-action/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function retryBatchItem(batchId: string, itemId: string): Promise<BatchProgress> {
  return apiFetch<BatchProgress>(`/api/v1/batch/${batchId}/items/${itemId}/retry/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function cancelBatch(batchId: string): Promise<BatchProgress> {
  return apiFetch<BatchProgress>(`/api/v1/batch/${batchId}/cancel/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function getScheduledBatches(): Promise<ScheduledBatchOperation[]> {
  return apiFetch<ScheduledBatchOperation[]>("/api/v1/batch/schedules/", { method: "GET" });
}

export async function createScheduledBatch(
  payload: ScheduledBatchPayload,
): Promise<ScheduledBatchOperation> {
  return apiFetch<ScheduledBatchOperation>("/api/v1/batch/schedules/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function disableScheduledBatch(id: string): Promise<void> {
  await apiFetch<void>(`/api/v1/batch/schedules/${id}/`, { method: "DELETE" });
}

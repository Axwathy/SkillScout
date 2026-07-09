export type BatchJobType = "upload" | "score" | "pipeline_action";
export type BatchStatus =
  | "pending"
  | "running"
  | "cancel_requested"
  | "canceled"
  | "completed"
  | "completed_with_errors"
  | "failed";
export type BatchItemStatus = "pending" | "running" | "completed" | "failed";
export type BatchPipelineAction = "move" | "reject" | "archive";

export interface BatchItem {
  id: string;
  label: string;
  status: BatchItemStatus;
  error: string;
  application_id: string | null;
  candidate_id: string | null;
  metadata: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BatchJob {
  id: string;
  job_type: BatchJobType;
  status: BatchStatus;
  total_count: number;
  processed_count: number;
  failed_count: number;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
  initiated_by_email: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface BatchProgress extends BatchJob {
  items: BatchItem[];
}

export interface BatchPipelineActionPayload {
  action: BatchPipelineAction;
  application_ids: string[];
  target_status?: string;
  target_stage_id?: string;
}

export type ScheduledBatchFrequency = "once" | "daily" | "weekly";

export interface ScheduledBatchOperation {
  id: string;
  job_type: BatchJobType;
  params: Record<string, unknown>;
  frequency: ScheduledBatchFrequency;
  is_active: boolean;
  next_run_at: string;
  last_run_at: string | null;
  last_batch_id: string | null;
  created_by_email: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduledBatchPayload {
  job_type: BatchJobType;
  params: Record<string, unknown>;
  frequency: ScheduledBatchFrequency;
  next_run_at: string;
}

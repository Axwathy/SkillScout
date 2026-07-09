---
type: analysis
title: "Sprint 15 Bulk Operations Implementation"
analysis_type: framework
date_created: 2026-06-14
date_updated: 2026-06-15
source_count: 1
tags: [product/feature, product/architecture, recruitment/screening, batch-processing, websocket, sprint/implemented]
---

# Sprint 15 Bulk Operations Implementation

## Methodology

Implemented [[sprint-15-bulk-operations|Sprint 15 Bulk Operations & Batch Processing]] by reusing existing resume parsing, scoring, pipeline transition, cookie auth, and recruiter organization scoping. The implementation adds Django Channels for live batch progress while preserving REST polling fallback for reliability.

## What Shipped

**Backend - `apps.batch`:**
- `BatchJob` tracks organization, initiator, job type, status, counters, params/result payloads, and lifecycle timestamps.
- `BatchItem` tracks per-file/per-application status, errors, related candidate/application IDs, metadata, and retry state.
- REST API under `/api/v1/batch/`:
  - `GET /api/v1/batch/` history list.
  - `POST /api/v1/batch/upload/` multipart bulk upload to a selected job.
  - `POST /api/v1/batch/score/<job_id>/` batch scoring.
  - `POST /api/v1/batch/pipeline-action/` bulk move/reject/archive.
  - `GET /api/v1/batch/<id>/progress/` polling fallback.
  - `POST /api/v1/batch/<id>/items/<item_id>/retry/` failed-item retry.
- WebSocket progress at `ws/batch/<uuid>/`, authenticated via the existing `access` cookie and organization-scoped before joining the batch group.
- Channels/Redis/Daphne wiring in ASGI and settings.
- Bulk upload extracts resume text, parses once, resolves candidate identity by parsed email, falls back to placeholder email when missing, creates/reuses applications, stores the uploaded resume, persists parsed data, and scores the application.
- Batch scoring and pipeline actions update per-item status and finish with `completed` or `completed_with_errors`.
- 15B hardening adds cooperative cancel, per-organization active batch limits, scheduled score/pipeline batches, and a non-eager Celery chord fan-in path for per-item processing.

**Frontend:**
- `/dashboard/batch` history list.
- `/dashboard/batch/upload` job selector, multi-file upload list, and live progress panel.
- `/dashboard/batch/[id]` progress/error report with failed-item retry.
- `useBatchProgress()` opens WebSocket progress and falls back to polling on disconnect.
- Applications page now supports selecting multiple applications, choosing a bulk action, and opening the resulting batch progress page.
- Dashboard navigation includes Batch.
- Batch progress panels support cancellation for pending/running jobs.
- Batch history includes scheduled score refresh controls.

## Verification

- Backend Ruff passed for batch/config during implementation.
- Django system check passed after Channels wiring.
- Batch focused tests passed: lifecycle/counters, progress endpoint, pipeline reject, upload identity resolution with placeholder fallback, partial-failure handling, org scoping, cancel, active batch limits, and schedule create/disable.
- Frontend type-check and lint passed after adding the batch pages and hook.

## Deferred / Out of Scope

- Hard cancellation of an item already inside a long parser/LLM call. Cancellation is cooperative and stops between items.
- Deployment-level Celery beat scheduling. The scheduled-operation model and due-schedule task exist, but production must run the task periodically.
- Per-organization rate limiting beyond the active-batch concurrency cap.
- Rich source mapping for bulk uploads beyond direct source.
- Production ASGI deployment wiring beyond documenting that Daphne/Uvicorn is required.

## Source References

- [[sprint-15-bulk-operations|Sprint 15 Plan]]
- [[Sprint 8 Candidate Ranking Implementation]]
- [[Sprint 9 Hiring Pipeline Implementation]]
- [[Sprint 14 Analytics Implementation]]

## Open Questions

- Should placeholder candidates created from resumes without email be surfaced in a recruiter review queue?
- Should bulk upload enforce a maximum file count per batch before production launch?
- Should failed upload items retain staged bytes for retry indefinitely, or expire them after a short retention window?

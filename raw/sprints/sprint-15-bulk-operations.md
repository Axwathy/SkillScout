---
title: "Sprint 15 — Bulk Operations & Batch Processing"
sprint_number: 15
status: planned
start_date: 2026-12-15
end_date: 2026-12-24
story_points_planned: 38
story_points_completed: 0
tags:
  - sprint
  - bulk
  - batch
  - celery
---

# Sprint 15 — Bulk Operations & Batch Processing

## 🎯 Sprint Goal

> **Primary Objective:** Enable bulk resume uploads, batch candidate scoring, and bulk pipeline actions so recruiters can efficiently process large volumes of candidates without manual one-by-one operations.
>
> **Success Criteria:** Recruiters can upload 50+ resumes in a single batch, trigger batch scoring for all applications on a job, and perform bulk stage moves. Progress is tracked in real-time with a centralized progress dashboard.

---

## 📋 Planned Features

- [ ] Bulk resume upload with parallel processing
- [ ] Batch scoring across all applications for a given job
- [ ] Bulk pipeline actions: move, reject, archive multiple candidates
- [ ] Real-time progress tracking dashboard

---

## ⚙️ Backend Tasks

- [ ] Create `BatchJob` model: type (upload/score/action), status, total_items, processed_items, failed_items, started_at, completed_at, initiated_by
- [ ] Implement `POST /api/v1/batch/upload/` accepting multiple files with per-file status tracking
- [ ] Build Celery chord workflow: fan-out individual file processing → fan-in completion callback
- [ ] Implement `POST /api/v1/batch/score/{job_id}/` triggering parallel scoring tasks for all applications on that job
- [ ] Build `POST /api/v1/batch/pipeline-action/` for bulk stage moves, rejections, and archiving
- [ ] Create `GET /api/v1/batch/{id}/progress/` returning real-time progress data
- [ ] Add WebSocket channel for push-based progress updates during batch processing
- [ ] Implement retry logic for individual failures within a batch (max 3 retries per item)
- [ ] Add rate limiting on batch operations: max concurrent batch jobs per org
- [ ] Write tests: batch job lifecycle, partial failure handling, progress accuracy, concurrent batches

---

## 🖥️ Frontend Tasks

- [ ] Build Bulk Upload page: large dropzone for multiple files, file list with individual status indicators
- [ ] Create Progress Dashboard: overall progress bar, per-item status table, ETA calculation
- [ ] Implement batch action controls: select candidates → choose action → confirm → track progress
- [ ] Build batch history page showing past operations with results summary
- [ ] Add cancel batch button with graceful shutdown (finish current, skip remaining)
- [ ] Create error report view: list failed items with error details and retry button
- [ ] Implement real-time progress updates via WebSocket with smooth animations

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Celery worker memory with large batches | High | Chunk processing (10 items per task), monitor memory | 🔴 Open |
| local embedding service rate limits during batch scoring | High | Implement backoff strategy, queue with rate limiter | 🟡 In Progress |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No batch operation scheduling — all operations are immediate
- [ ] Progress tracking polling fallback if WebSocket disconnects

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-05-resume-upload]], [[sprint-08-candidate-ranking]] — individual operations must work before batching
- **References:** [[system-overview|System Overview]], [[ai-pipeline|AI Pipeline]]
- **Next Sprint:** [[sprint-16-security-hardening]] — Security Hardening

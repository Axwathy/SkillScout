---
title: "Sprint 9 — Hiring Pipeline"
sprint_number: 9
status: planned
start_date: 2026-09-22
end_date: 2026-10-02
story_points_planned: 42
story_points_completed: 0
tags:
  - sprint
  - pipeline
  - kanban
  - workflow
---

# Sprint 9 — Hiring Pipeline

## 🎯 Sprint Goal

> **Primary Objective:** Build a Kanban-style hiring pipeline with drag-and-drop stage management, configurable stages, and full transition history tracking for audit and analytics.
>
> **Success Criteria:** Recruiters can view candidates in a Kanban board, drag them between stages, configure custom pipeline stages per job, and see complete stage transition history.

---

## 📋 Planned Features

- [ ] Configurable pipeline stages per job (default: Applied → Screening → Interview → Offer → Hired/Rejected)
- [ ] Drag-and-drop Kanban board interface
- [ ] Stage transition history with timestamps and actor tracking
- [ ] Pipeline templates for common hiring workflows

---

## ⚙️ Backend Tasks

- [ ] Create `PipelineStage` model: job, name, order, color, is_terminal, auto_actions
- [ ] Use `candidate_applications.current_stage_id` for current stage state
- [ ] Create `CandidateStageHistory` model: application, from_stage, to_stage, moved_by, moved_at, notes
- [ ] Implement `POST /api/v1/pipeline/move/` for moving applications between stages
- [ ] Build stage ordering API: `PATCH /api/v1/pipeline/stages/reorder/`
- [ ] Add validation: prevent invalid transitions, enforce stage prerequisites
- [ ] Create default pipeline template seeded on job creation (5 standard stages)
- [ ] Implement `GET /api/v1/pipeline/board/{job_id}/` returning applications grouped by stage
- [ ] Add WebSocket channel for real-time board updates when others move candidates
- [ ] Write tests: stage transitions, ordering, permission checks, concurrent move handling

See also: [[pipeline-schema|Pipeline Schema]], [[pipeline-api|Pipeline API]]

---

## 🖥️ Frontend Tasks

- [ ] Build Kanban board using `@dnd-kit/core` for accessible drag-and-drop
- [ ] Create stage column components with candidate cards showing name, score, time-in-stage
- [ ] Implement drag preview with visual feedback (shadow, color highlight)
- [ ] Add stage configuration panel: rename, reorder, add/remove stages, set colors
- [ ] Build transition confirmation dialog with optional notes field
- [ ] Display transition history timeline on candidate detail view
- [ ] Add real-time updates via WebSocket — show other users' moves live
- [ ] Implement stage count badges and progress indicators per pipeline

See also: [[pipeline-board|Pipeline Board]]

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Drag-and-drop accessibility compliance | Medium | Use `@dnd-kit` which has built-in a11y | 🟢 Planned |
| Concurrent stage moves by multiple recruiters | High | Optimistic locking with version check on backend | 🟡 In Progress |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No pipeline analytics yet — funnel metrics come in [[sprint-14-analytics]]
- [ ] Stage auto-actions (e.g., send email on stage enter) are placeholder — not implemented

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-08-candidate-ranking]] — scored candidates populate the pipeline
- **References:** [[pipeline-board|Pipeline Board]], [[pipeline-schema|Pipeline Schema]], [[pipeline-api|Pipeline API]]
- **Next Sprint:** [[sprint-10-candidate-dashboard]] — Candidate Dashboard

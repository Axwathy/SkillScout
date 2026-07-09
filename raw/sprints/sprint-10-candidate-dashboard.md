---
title: "Sprint 10 — Candidate Dashboard"
sprint_number: 10
status: planned
start_date: 2026-10-06
end_date: 2026-10-16
story_points_planned: 40
story_points_completed: 0
tags:
  - sprint
  - candidate
  - dashboard
  - frontend
---

# Sprint 10 — Candidate Dashboard

## 🎯 Sprint Goal

> **Primary Objective:** Build a comprehensive candidate profile view that aggregates scores, parsed resume data, AI insights, pipeline status, and interaction history into a single, actionable dashboard.
>
> **Success Criteria:** Recruiters can view a candidate's full profile with match scores, parsed skills/experience, AI-generated summary, pipeline position, and action buttons — all on one page.

---

## 📋 Planned Features

- [ ] Unified candidate profile page with tabbed sections
- [ ] Score visualization with radar charts and sub-score breakdowns
- [ ] Parsed resume display with structured data and original document access
- [ ] AI-generated candidate summary and fit assessment

---

## 🖥️ Frontend Tasks

- [ ] Build Candidate Profile page with header: name, photo, current stage badge, overall score
- [ ] Create Score Visualization component using Recharts: radar chart for sub-scores, trend line if multiple scores
- [ ] Build Skills Grid component: parsed skills with proficiency bars and category grouping
- [ ] Create Experience Timeline component: chronological list with role, company, duration, highlights
- [ ] Build Education Section component: degree, institution, graduation year, GPA
- [ ] Implement AI Summary Card: 3–5 sentence AI-generated assessment of candidate fit
- [ ] Create Activity Feed: stage transitions, notes added, interviews scheduled — reverse chronological
- [ ] Build Quick Actions bar: move stage, add note, schedule interview, download resume, reject
- [ ] Add tab navigation: Overview | Resume | Scores | Activity | Notes
- [ ] Implement candidate comparison mode: side-by-side view of two candidates

---

## ⚙️ Backend Tasks

- [ ] Create `GET /api/v1/candidates/{id}/profile/` aggregated endpoint combining: parsed resume, scores, pipeline stage, activity log
- [ ] Implement AI summary generation endpoint: `POST /api/v1/candidates/{id}/generate-summary/`
- [ ] Build candidate notes CRUD: `POST/GET /api/v1/candidates/{id}/notes/`
- [ ] Add candidate activity log query with pagination and filtering
- [ ] Implement candidate comparison endpoint: `GET /api/v1/candidates/compare/?ids=1,2`
- [ ] Write tests: aggregated response shape, permission scoping, performance benchmarks

See also: [[candidate-dashboard|Candidate Dashboard]], [[candidate-api|Candidate API]]

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Aggregated endpoint query performance | Medium | Use `select_related` and `prefetch_related`, add DB indexes | 🟡 In Progress |
| AI summary generation latency | Low | Generate async, show loading state, cache result | 🟢 Planned |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Candidate photo is placeholder — no photo upload feature yet
- [ ] Comparison mode limited to 2 candidates — expand to N in future

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-09-pipeline]] — pipeline stage data must exist
- **References:** [[candidate-dashboard|Candidate Dashboard]], [[candidate-api|Candidate API]], [[ai-pipeline|AI Pipeline]]
- **Next Sprint:** [[sprint-11-semantic-search]] — Semantic Search

---
type: analysis
title: "Sprint 10 Candidate Dashboard Plan"
analysis_type: framework
date_created: 2026-06-10
date_updated: 2026-06-10
source_count: 5
tags: [product/feature, product/ux, product/architecture, recruitment/screening, candidate-dashboard, sprint/implemented]
---

# Sprint 10 Candidate Dashboard Plan

## Methodology

Compared the human-managed [[sprint-10-candidate-dashboard|Sprint 10 plan]] against the current product state from [[Sprint 6 Resume Parsing Implementation]], [[Sprint 8 Candidate Ranking Implementation]], [[Sprint 9 Hiring Pipeline Implementation]], and the [[Candidate Dashboard]] concept. The goal is to plan the next implementation sprint without reopening completed ranking or pipeline architecture.

## Current Readiness

Sprint 10 is implemented for the core recruiter dashboard slice. The required data now exists:

- Parsed resume data from Sprint 6: candidate identity, skills, experience, education, projects, confidence, parser model, and source resume access.
- Ranking data from Sprint 8: overall score, semantic score, skill score, experience score, score version, and score timestamp.
- Pipeline data from Sprint 9: canonical status plus configurable per-job `current_stage`, stage history, and application status history.
- Recruiter candidate profile UI now aggregates those ingredients into a unified candidate workspace.

## Implementation Status

Implemented in the application:

- Aggregated recruiter candidate profile API under `/api/v1/applications/candidates/{id}/profile/`.
- Candidate notes model, migration, list/create/update/delete endpoints, and audit logging.
- Recruiter candidate list at `/dashboard/candidates`.
- Candidate profile page at `/dashboard/candidates/[id]` with Overview, Resume, Scores, Activity, and Notes tabs.
- Links from the recruiter application list and application detail page to the candidate profile.
- Tenant-scoped backend tests for aggregate profile data, cross-organization isolation, missing parsed resumes, multiple applications, and notes lifecycle.

Deferred from this sprint:

- AI-generated candidate summary endpoint and cache.
- Candidate comparison endpoint.
- Real-time updates, interview scheduling, photo upload, and analytics.

## Recommended Sprint Goal

Build a recruiter-facing candidate dashboard that aggregates the candidate, their applications, parsed resume profile, match scores, current pipeline stage, and activity history into one focused profile page.

Primary route recommendation:

- `GET /api/v1/candidates/{id}/profile/`
- Frontend: `/dashboard/candidates/[id]`

This avoids overloading the current application detail page and supports candidates with multiple applications over time.

## Scope For Sprint 10

### Must Ship

1. **Aggregated candidate profile API**
   - Candidate identity and contact fields.
   - Applications list with job, status, current stage, applied date, score fields, and latest resume.
   - Latest parsed resume summary: skills, experience, education, projects, confidence, parser model.
   - Unified activity feed combining application history, pipeline stage history, and resume parse events.
   - Tenant-scoped recruiter permissions.

2. **Candidate dashboard page**
   - Header with name, contact, current/most recent application, stage badge, and overall score.
   - Tabs: Overview, Resume, Scores, Activity, Notes.
   - Parsed profile display reused from the existing resume panel patterns.
   - Score cards for all applications, with semantic / skill / experience breakdown.
   - Activity timeline with stage moves and application status changes.
   - Quick links/actions: open application, download resume, move stage via existing pipeline flow.

3. **Candidate notes**
   - `GET/POST /api/v1/candidates/{id}/notes/`.
   - Simple note model: candidate, organization, author, body, created_at, updated_at.
   - Notes tab in the dashboard.

4. **Tests**
   - Aggregated response shape.
   - Organization isolation.
   - Notes CRUD permissions.
   - Candidate with no parsed resume.
   - Candidate with multiple applications.

### Should Ship If Time Allows

1. **Candidate comparison endpoint**
   - `GET /api/v1/candidates/compare/?ids=<id1>,<id2>`.
   - Limit to two candidates for this sprint.
   - Return identity, latest score breakdown, skills overlap, missing skills, and latest stage.

2. **Score visualization**
   - Lightweight bar/radar-style visualization using existing CSS first.
   - Avoid adding a chart dependency unless the current UI cannot express the breakdown cleanly.

### Defer

- Real-time dashboard updates.
- Interview scheduling.
- Candidate photo upload.
- Analytics/funnel metrics.
- Any AI output that changes scores, rank, or stage.

## AI Summary Plan

The raw Sprint 10 plan includes an AI-generated candidate summary. Implement it as recruiter assistance only:

- Endpoint: `POST /api/v1/candidates/{id}/generate-summary/`.
- Store/cached field rather than regenerating on every page load.
- Inputs: parsed resume, selected job/application, deterministic scores, matched/missing skills, and stage history.
- Output: 3-5 sentence summary plus evidence bullets.
- Guardrail: summary must never return `hire`, `reject`, or a final recommendation. It explains evidence; the math remains authoritative.

If model reliability or latency is not stable, ship the dashboard first and keep the summary card behind an explicit "Generate summary" action.

## Data Contract Sketch

```json
{
  "candidate": {},
  "applications": [
    {
      "id": "uuid",
      "job": {},
      "status": "shortlisted",
      "current_stage": {},
      "scores": {},
      "latest_resume": {},
      "parsed_resume": {}
    }
  ],
  "activity": [],
  "notes": []
}
```

## Execution Sequence

1. Backend aggregate serializer and profile endpoint.
2. Notes model, migration, serializer, and endpoint.
3. Frontend candidate dashboard route with tabs and existing score/resume components.
4. Wire candidate links from application cards and candidate lists.
5. Add tests and run full backend/frontend validation.
6. Optional: AI summary endpoint after the dashboard is stable.

## Acceptance Criteria

- Recruiter can open one candidate profile and understand identity, resume, applications, scores, current stage, and activity without switching pages.
- Candidate profile is tenant-scoped and cannot leak candidates across organizations.
- Existing application detail, pipeline, scoring, and candidate portal behavior remain unchanged.
- Page works when resume parsing is missing, failed, or still processing.
- Full validation passes: backend tests, Ruff, frontend type-check, lint, and production build.

## Source References

- [[sprint-10-candidate-dashboard|Sprint 10 Plan]]
- [[Sprint 6 Resume Parsing Implementation]]
- [[Sprint 8 Candidate Ranking Implementation]]
- [[Sprint 9 Hiring Pipeline Implementation]]
- [[Candidate Dashboard]]

## Open Questions

- Should the first dashboard route be candidate-centric (`/dashboard/candidates/[id]`) only, or should application detail embed it as a tab?
- Should notes be candidate-level only, or support application-scoped notes from the beginning?
- Should the AI summary be generated per candidate overall, or per candidate-job application?

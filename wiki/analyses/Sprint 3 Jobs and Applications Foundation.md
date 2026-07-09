---
type: analysis
title: "Sprint 3 Jobs and Applications Foundation"
analysis_type: framework
date_created: 2026-05-30
date_updated: 2026-05-30
source_count: 5
tags: [product/strategy, product/architecture, recruitment/jobs, recruitment/screening, security/tenancy]
---

# Sprint 3 Jobs and Applications Foundation

## Methodology

This plan reconciles the current product state with the human-approved Sprint 3 scope and the existing vault references: `raw/sprints/sprint-03-job-management.md`, `raw/apis/jobs-api.md`, `raw/apis/candidate-api.md`, `raw/database/job-schema.md`, and `raw/database/candidate-schema.md`.

## Status Baseline

- Sprint 1 is complete: foundation, backend, frontend, Docker, CI, and developer workflow are in place via [[Sprint 1 Foundation Implementation]].
- Sprint 2 is complete: recruiter/admin authentication, organization approval, and RBAC are in place.
- Sprint 2.1 is complete: confirm password, silent refresh, scoped auth rate limits, and auth tests are in place via [[Sprint 2.1 Auth Hardening Plan]].
- Candidate authentication is intentionally out of scope. The candidate side starts as a public application flow, not a candidate portal.

## Sprint 3 Scope

Sprint 3 should create the first real recruitment workflow:

- Recruiters can create, edit, publish, unpublish, archive, list, and inspect jobs.
- Public candidates can browse published jobs and apply without an account.
- Recruiters can list and view applications scoped to their organization.
- Candidate profiles are created as domain records only; no candidate login, register, or dashboard.
- Every recruiter-facing query must enforce tenant isolation through the current user's organization.

## Architecture Notes

The implementation should use organization-scoped Jobs, Candidates, and Applications. Although the human-facing Sprint 3 field list keeps Candidate minimal, the vault's [[candidate-schema|Candidate Schema]] requires `organization_id` for tenant isolation, so candidate records should include organization ownership internally.

Application status should start with only:

- `applied`
- `under_review`
- `rejected`
- `shortlisted`

Full pipeline stages, resume upload, parsing, embeddings, scoring, analytics, and AI summaries remain out of scope.

## Source References

- `raw/sprints/sprint-03-job-management.md`
- `raw/apis/jobs-api.md`
- `raw/apis/candidate-api.md`
- `raw/database/job-schema.md`
- `raw/database/candidate-schema.md`
- [[Multi-Tenant Architecture]]
- [[Authentication Strategy]]

## Open Questions

- Should public job URLs use globally unique slugs, organization-prefixed slugs, or UUID-backed URLs long term?
- Should duplicate applications by the same email to the same job be blocked or treated as idempotent updates?
- Should Sprint 4 introduce a recruiter-managed candidate profile page before or after the pipeline board?

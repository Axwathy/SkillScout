---
type: database
title: "Entity Relationships"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [database/schema, database/relationships, database/erd]
---

# Entity Relationships

## Overview

The schema follows a **multi-tenant architecture** where `organizations` is the root entity. Candidate identity is separated from job-specific applications:

```text
Organizations → Users/Memberships
Organizations → Jobs → Job Skills
Organizations → Candidates → Candidate Applications → Scores
Candidate Applications → Stage History → Interview Feedback
```

This model supports one candidate applying to multiple jobs while keeping resume/profile data reusable.

---

## ER Diagram

```text
organizations
├── memberships ── users
├── jobs
│   ├── job_skills
│   └── candidate_applications
│       ├── candidate_scores
│       ├── candidate_stage_history
│       └── interview_feedback
├── candidates
│   └── candidate_applications
└── pipeline_stages
    ├── candidate_applications.current_stage_id
    ├── candidate_stage_history.from_stage_id / to_stage_id
    └── interview_feedback.stage_id
```

---

## Core Relations with Cardinality

| Parent Entity | Relationship | Child Entity | Cardinality | Description |
|---|---|---|---|---|
| `organizations` | has many | `memberships` | 1:N | An org has multiple members |
| `organizations` | has many | `jobs` | 1:N | An org posts multiple jobs |
| `organizations` | has many | `candidates` | 1:N | Candidate profiles are org-scoped |
| `organizations` | has many | `candidate_applications` | 1:N | Applications are org-scoped for fast filtering |
| `organizations` | has many | `pipeline_stages` | 1:N | Each org defines its own pipeline |
| `users` | has many | `memberships` | 1:N | A user can belong to multiple orgs |
| `users` | has many | `jobs` (created_by) | 1:N | A user creates job postings |
| `users` | has many | `candidate_stage_history` (moved_by) | 1:N | A user moves applications through stages |
| `users` | has many | `interview_feedback` | 1:N | A user provides interview feedback |
| `jobs` | has many | `job_skills` | 1:N | A job has skill requirements |
| `jobs` | has many | `candidate_applications` | 1:N | A job receives applications |
| `candidates` | has many | `candidate_applications` | 1:N | A candidate can apply to multiple jobs |
| `candidate_applications` | has many | `candidate_scores` | 1:N | Scores are versioned per application |
| `candidate_applications` | has many | `candidate_stage_history` | 1:N | Stage transition audit trail |
| `candidate_applications` | has many | `interview_feedback` | 1:N | Feedback belongs to an application |
| `candidate_applications` | belongs to | `pipeline_stages` | N:1 | Current pipeline position |
| `pipeline_stages` | has many | `candidate_stage_history` | 1:N | Transitions into/out of stages |
| `pipeline_stages` | has many | `interview_feedback` | 1:N | Feedback at a stage |

---

## Foreign Key Constraints & Cascade Behaviors

| FK Column | References | ON DELETE | ON UPDATE | Rationale |
|---|---|---|---|---|
| `memberships.organization_id` | `organizations.id` | CASCADE | CASCADE | Deleting an org removes memberships |
| `memberships.user_id` | `users.id` | CASCADE | CASCADE | Deleting a user removes memberships |
| `jobs.organization_id` | `organizations.id` | CASCADE | CASCADE | Org deletion removes jobs |
| `jobs.created_by` | `users.id` | SET NULL | CASCADE | Preserve job if creator is deleted |
| `job_skills.job_id` | `jobs.id` | CASCADE | CASCADE | Skills are part of the job definition |
| `candidates.organization_id` | `organizations.id` | CASCADE | CASCADE | Org deletion removes candidate profiles |
| `candidate_applications.organization_id` | `organizations.id` | CASCADE | CASCADE | Org deletion removes applications |
| `candidate_applications.candidate_id` | `candidates.id` | CASCADE | CASCADE | Applications are owned by candidate profiles |
| `candidate_applications.job_id` | `jobs.id` | CASCADE | CASCADE | Job deletion removes associated applications |
| `candidate_applications.current_stage_id` | `pipeline_stages.id` | SET NULL | CASCADE | Stage deletion should not delete an application |
| `candidate_scores.application_id` | `candidate_applications.id` | CASCADE | CASCADE | Scores are owned by applications |
| `candidate_scores.candidate_id` | `candidates.id` | CASCADE | CASCADE | Denormalized lookup follows candidate lifecycle |
| `candidate_scores.job_id` | `jobs.id` | CASCADE | CASCADE | Denormalized lookup follows job lifecycle |
| `candidate_stage_history.application_id` | `candidate_applications.id` | CASCADE | CASCADE | History is part of the application record |
| `candidate_stage_history.from_stage_id` | `pipeline_stages.id` | SET NULL | CASCADE | Preserve history if stage is removed |
| `candidate_stage_history.to_stage_id` | `pipeline_stages.id` | SET NULL | CASCADE | Preserve history if stage is removed |
| `candidate_stage_history.moved_by` | `users.id` | SET NULL | CASCADE | Preserve audit trail if user leaves |
| `interview_feedback.application_id` | `candidate_applications.id` | CASCADE | CASCADE | Feedback belongs to an application |
| `interview_feedback.stage_id` | `pipeline_stages.id` | SET NULL | CASCADE | Preserve feedback if stage changes |
| `interview_feedback.interviewer_id` | `users.id` | SET NULL | CASCADE | Preserve feedback if interviewer leaves |

### Cascade Behavior Principles

1. **CASCADE on ownership** — When a parent owns the child, deletion cascades.
2. **SET NULL on contextual references** — Context references are nullified to preserve history.
3. **Audit trail preservation** — Stage history and feedback survive user/stage deletions where possible.

---

## Multi-Tenant Scoping

Every application query is scoped by `organization_id`. This is enforced at multiple levels:

1. **Django ORM** — `OrgScopedMixin` filters querysets by `request.user.org_id`.
2. **Database session context** — Middleware sets `SET LOCAL app.current_org_id = '<org_uuid>'` for request-scoped database work.
3. **PostgreSQL RLS** — Policies compare row `organization_id` against `current_setting('app.current_org_id', true)`.

```sql
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY candidates_org_isolation ON candidates
USING (
  organization_id = NULLIF(current_setting('app.current_org_id', true), '')::uuid
);
```

Because product auth is handled by Django JWTs rather than Supabase Auth, application tables should not rely on `auth.jwt()` for tenant scoping.

---

## Related Documents

- [[candidate-schema|Candidate Schema]] — Candidate, application, and scoring tables.
- [[job-schema|Job Schema]] — Job posting and skill requirements.
- [[pipeline-schema|Pipeline Schema]] — Stage history and feedback tables.
- [[pgvector-notes|pgvector Notes]] — Vector column configuration.
- [[backend-architecture|Backend Architecture]] — Django ORM patterns and query optimization.

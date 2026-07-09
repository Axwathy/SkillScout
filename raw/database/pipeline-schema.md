---
type: database
title: "Pipeline Schema"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [database/schema, domain/pipeline, domain/hiring]
---

# Pipeline Schema

## Overview

The pipeline schema supports the **Kanban-style hiring pipeline** — the core workflow tool for recruiters. It tracks customizable interview stages, candidate progression through those stages, and structured interview feedback. Organizations can define their own stage names and ordering while the system provides sensible defaults.

These tables power the [[pipeline-board|Pipeline Board]] UI and provide audit trails for compliance and analytics.

---

## `pipeline_stages` Table

Defines the customizable stages in an organization's hiring pipeline.

```sql
CREATE TABLE pipeline_stages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    stage_order     INTEGER NOT NULL,
    color           VARCHAR(7) DEFAULT '#6366F1',
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    is_terminal     BOOLEAN NOT NULL DEFAULT FALSE,
    auto_action     VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `organization_id` | UUID | FK to `organizations`. Each org has its own pipeline stages |
| `name` | VARCHAR(100) | Stage name (e.g., "Applied", "Phone Screen", "Technical Interview") |
| `description` | TEXT | Optional description of what happens at this stage |
| `stage_order` | INTEGER | Display order in the pipeline (ascending). Determines left-to-right Kanban layout |
| `color` | VARCHAR(7) | Hex color code for the stage column in the UI |
| `is_default` | BOOLEAN | If `true`, new candidates are automatically placed in this stage |
| `is_terminal` | BOOLEAN | If `true`, this is a final stage (e.g., "Hired", "Rejected") |
| `auto_action` | VARCHAR(50) | Optional automated action triggered when a candidate enters this stage |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last modification timestamp |

### Default Stages (Created on Organization Setup)

| Order | Name | Default | Terminal | Color | Auto Action |
|-------|------|---------|----------|-------|-------------|
| 1 | Applied | ✅ | ❌ | `#6366F1` | — |
| 2 | Screening | ❌ | ❌ | `#8B5CF6` | — |
| 3 | Phone Interview | ❌ | ❌ | `#A78BFA` | `send_interview_invite` |
| 4 | Technical Assessment | ❌ | ❌ | `#F59E0B` | — |
| 5 | On-site Interview | ❌ | ❌ | `#F97316` | `send_interview_invite` |
| 6 | Offer | ❌ | ❌ | `#10B981` | `send_offer_email` |
| 7 | Hired | ❌ | ✅ | `#059669` | `send_welcome_email` |
| 8 | Rejected | ❌ | ✅ | `#EF4444` | `send_rejection_email` |

### Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| `pk_pipeline_stages` | PRIMARY KEY | `id` |
| `fk_stages_org` | FOREIGN KEY | `organization_id → organizations(id) ON DELETE CASCADE` |
| `uq_stage_order` | UNIQUE | `(organization_id, stage_order)` — no duplicate ordering within an org |
| `uq_stage_name` | UNIQUE | `(organization_id, name)` — no duplicate stage names within an org |
| `chk_stage_order` | CHECK | `stage_order > 0` |

### Indexes

```sql
-- Stages for an organization (primary access pattern)
CREATE INDEX idx_stages_org ON pipeline_stages(organization_id, stage_order);

-- Default stage lookup
CREATE INDEX idx_stages_default ON pipeline_stages(organization_id)
WHERE is_default = TRUE;
```

---

## `candidate_stage_history` Table

An append-only audit log tracking every stage transition for every job-specific application. This provides a complete timeline for compliance, analytics, and the candidate detail view.

```sql
CREATE TABLE candidate_stage_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID NOT NULL REFERENCES candidate_applications(id) ON DELETE CASCADE,
    from_stage_id   UUID REFERENCES pipeline_stages(id) ON DELETE SET NULL,
    to_stage_id     UUID REFERENCES pipeline_stages(id) ON DELETE SET NULL,
    moved_by        UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    notes           TEXT,
    reason          VARCHAR(50),
    duration_hours  INTEGER,
    moved_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `application_id` | UUID | FK to `candidate_applications`. The job-specific application being moved |
| `from_stage_id` | UUID | FK to `pipeline_stages`. Previous stage (null for initial placement) |
| `to_stage_id` | UUID | FK to `pipeline_stages`. Destination stage |
| `moved_by` | UUID | FK to `users`. The recruiter who performed the move |
| `notes` | TEXT | Optional notes explaining the stage transition |
| `reason` | VARCHAR(50) | Categorized reason: `advanced`, `skipped`, `rejected`, `reconsidered` |
| `duration_hours` | INTEGER | Computed: hours spent in the previous stage (calculated on insert) |
| `moved_at` | TIMESTAMPTZ | When the transition occurred |

### Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| `pk_stage_history` | PRIMARY KEY | `id` |
| `fk_history_application` | FOREIGN KEY | `application_id → candidate_applications(id) ON DELETE CASCADE` |
| `fk_history_from_stage` | FOREIGN KEY | `from_stage_id → pipeline_stages(id) ON DELETE SET NULL` |
| `fk_history_to_stage` | FOREIGN KEY | `to_stage_id → pipeline_stages(id) ON DELETE SET NULL` |
| `fk_history_user` | FOREIGN KEY | `moved_by → users(id) ON DELETE SET NULL` |

### Indexes

```sql
-- Application timeline (chronological history)
CREATE INDEX idx_history_application ON candidate_stage_history(application_id, moved_at DESC);

-- Stage analytics (how many candidates enter/leave each stage)
CREATE INDEX idx_history_to_stage ON candidate_stage_history(to_stage_id, moved_at);
CREATE INDEX idx_history_from_stage ON candidate_stage_history(from_stage_id, moved_at);

-- User activity tracking
CREATE INDEX idx_history_moved_by ON candidate_stage_history(moved_by, moved_at DESC);
```

---

## `interview_feedback` Table

Stores structured feedback from interviewers for each job-specific application at each pipeline stage. Multiple interviewers can submit feedback for the same application at the same stage.

```sql
CREATE TABLE interview_feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID NOT NULL REFERENCES candidate_applications(id) ON DELETE CASCADE,
    stage_id        UUID REFERENCES pipeline_stages(id) ON DELETE SET NULL,
    interviewer_id  UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    overall_rating  INTEGER NOT NULL,
    technical_rating INTEGER,
    communication_rating INTEGER,
    culture_fit_rating INTEGER,
    strengths       TEXT,
    weaknesses      TEXT,
    notes           TEXT,
    recommendation  VARCHAR(20) NOT NULL DEFAULT 'neutral',
    is_submitted    BOOLEAN NOT NULL DEFAULT FALSE,
    submitted_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `application_id` | UUID | FK to `candidate_applications`. The job-specific application being evaluated |
| `stage_id` | UUID | FK to `pipeline_stages`. The stage at which this feedback was given |
| `interviewer_id` | UUID | FK to `users`. The interviewer providing feedback |
| `overall_rating` | INTEGER | Overall rating (1–5 scale) |
| `technical_rating` | INTEGER | Technical competency rating (1–5, nullable for non-technical stages) |
| `communication_rating` | INTEGER | Communication skills rating (1–5) |
| `culture_fit_rating` | INTEGER | Culture fit assessment (1–5) |
| `strengths` | TEXT | Free-text description of candidate strengths |
| `weaknesses` | TEXT | Free-text description of areas of concern |
| `notes` | TEXT | General interview notes and observations |
| `recommendation` | VARCHAR(20) | `strong_yes`, `yes`, `neutral`, `no`, `strong_no` |
| `is_submitted` | BOOLEAN | Whether the feedback has been finalized (draft until submitted) |
| `submitted_at` | TIMESTAMPTZ | When the feedback was finalized |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last modification timestamp |

### Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| `pk_feedback` | PRIMARY KEY | `id` |
| `fk_feedback_application` | FOREIGN KEY | `application_id → candidate_applications(id) ON DELETE CASCADE` |
| `fk_feedback_stage` | FOREIGN KEY | `stage_id → pipeline_stages(id) ON DELETE SET NULL` |
| `fk_feedback_interviewer` | FOREIGN KEY | `interviewer_id → users(id) ON DELETE SET NULL` |
| `uq_feedback_unique` | UNIQUE | `(application_id, stage_id, interviewer_id)` — one feedback per interviewer per stage |
| `chk_overall_rating` | CHECK | `overall_rating BETWEEN 1 AND 5` |
| `chk_technical_rating` | CHECK | `technical_rating IS NULL OR technical_rating BETWEEN 1 AND 5` |
| `chk_communication_rating` | CHECK | `communication_rating IS NULL OR communication_rating BETWEEN 1 AND 5` |
| `chk_culture_rating` | CHECK | `culture_fit_rating IS NULL OR culture_fit_rating BETWEEN 1 AND 5` |
| `chk_recommendation` | CHECK | `recommendation IN ('strong_yes','yes','neutral','no','strong_no')` |

### Indexes

```sql
-- Feedback for a specific application (detail view)
CREATE INDEX idx_feedback_application ON interview_feedback(application_id, stage_id);

-- Interviewer's feedback history
CREATE INDEX idx_feedback_interviewer ON interview_feedback(interviewer_id, created_at DESC);

-- Pending feedback (drafts needing submission)
CREATE INDEX idx_feedback_pending ON interview_feedback(interviewer_id)
WHERE is_submitted = FALSE;
```

---

## Related Documents

- [[relationships|Entity Relationships]] — Full ER diagram showing how pipeline tables connect to candidates and jobs.
- [[pipeline-board|Pipeline Board]] — Frontend Kanban UI that consumes this data.
- [[candidate-schema|Candidate Schema]] — Candidate/application data model and the `current_stage_id` foreign key.
- [[analytics-dashboard|Analytics Dashboard]] — Pipeline velocity and stage duration metrics derived from `candidate_stage_history`.

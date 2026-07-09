---
type: database
title: "Candidate Schema"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [database/schema, database/pgvector, domain/candidates]
---

# Candidate Schema

## Overview

The candidate schema separates **candidate profiles** from **job applications**:

- `candidates` stores reusable person-level profile data, resume text, parsed resume data, and embeddings.
- `candidate_applications` stores the candidate's application to a specific job, including pipeline state and source.
- `candidate_scores` stores deterministic scoring results for an application/job pair.

This avoids the earlier job-centric model where `candidates.job_id` made a candidate belong to only one job.

All candidate and application data is **organization-scoped** via `organization_id`.

---

## `candidates` Table

The central table for storing candidate profile data independent of any single job application.

```sql
CREATE TABLE candidates (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name             VARCHAR(255) NOT NULL,
    email            VARCHAR(255) NOT NULL,
    phone            VARCHAR(50),
    resume_url       TEXT,
    raw_text         TEXT,
    parsed_data      JSONB DEFAULT '{}',
    embedding        vector(384),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key, auto-generated UUIDv4 |
| `organization_id` | UUID | FK to `organizations`; enforces tenant isolation |
| `name` | VARCHAR(255) | Candidate's full name |
| `email` | VARCHAR(255) | Candidate's email address; unique within an organization |
| `phone` | VARCHAR(50) | Optional phone number |
| `resume_url` | TEXT | Backend-managed Supabase Storage path or signed URL reference |
| `raw_text` | TEXT | Extracted resume text used for search fallback and parsing |
| `parsed_data` | JSONB | Structured data extracted by Ollama |
| `embedding` | vector(384) | BAAI `bge-small-en-v1.5` vector representation |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last modification timestamp |

### `parsed_data` JSONB Structure

```json
{
  "skills": [
    { "name": "Python", "proficiency": "advanced", "years": 5 },
    { "name": "Django", "proficiency": "advanced", "years": 4 }
  ],
  "experience": [
    {
      "title": "Senior Backend Developer",
      "company": "Acme Corp",
      "start_date": "2020-01",
      "end_date": "2024-06",
      "description": "Led backend architecture..."
    }
  ],
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "MIT",
      "graduation_year": 2018
    }
  ],
  "total_experience_years": 6,
  "location": "San Francisco, CA",
  "summary": "Experienced backend developer..."
}
```

### Constraints

| Constraint | Type | Details |
|---|---|---|
| `pk_candidates` | PRIMARY KEY | `id` |
| `fk_candidates_org` | FOREIGN KEY | `organization_id → organizations(id) ON DELETE CASCADE` |
| `uq_candidate_email_org` | UNIQUE | `(organization_id, email)` |

### Indexes

```sql
CREATE INDEX idx_candidates_org ON candidates(organization_id);
CREATE INDEX idx_candidates_email ON candidates(organization_id, email);

CREATE INDEX idx_candidates_embedding ON candidates
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_candidates_raw_text ON candidates
USING gin (to_tsvector('english', raw_text));

CREATE INDEX idx_candidates_parsed_skills ON candidates
USING gin ((parsed_data -> 'skills'));
```

---

## `candidate_applications` Table

Stores a candidate's application to a specific job. Pipeline state belongs here because the same candidate may be in different stages for different jobs.

```sql
CREATE TABLE candidate_applications (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    candidate_id      UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id            UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status            VARCHAR(20) NOT NULL DEFAULT 'new',
    current_stage_id  UUID REFERENCES pipeline_stages(id) ON DELETE SET NULL,
    source            VARCHAR(50) DEFAULT 'direct',
    applied_at        TIMESTAMPTZ DEFAULT NOW(),
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|---|---|---|
| `organization_id` | UUID | Duplicated for tenant scoping and query efficiency |
| `candidate_id` | UUID | Candidate profile being submitted |
| `job_id` | UUID | Job this application targets |
| `status` | VARCHAR(20) | `new`, `screening`, `interviewing`, `offered`, `hired`, `rejected` |
| `current_stage_id` | UUID | Current pipeline stage for this application |
| `source` | VARCHAR(50) | `direct`, `upload`, `linkedin`, `referral`, `api`, etc. |
| `applied_at` | TIMESTAMPTZ | When the application was created |

### Constraints

| Constraint | Type | Details |
|---|---|---|
| `pk_candidate_applications` | PRIMARY KEY | `id` |
| `fk_applications_org` | FOREIGN KEY | `organization_id → organizations(id) ON DELETE CASCADE` |
| `fk_applications_candidate` | FOREIGN KEY | `candidate_id → candidates(id) ON DELETE CASCADE` |
| `fk_applications_job` | FOREIGN KEY | `job_id → jobs(id) ON DELETE CASCADE` |
| `fk_applications_stage` | FOREIGN KEY | `current_stage_id → pipeline_stages(id) ON DELETE SET NULL` |
| `uq_application_candidate_job` | UNIQUE | `(candidate_id, job_id)` |
| `chk_application_status` | CHECK | `status IN ('new','screening','interviewing','offered','hired','rejected')` |

### Indexes

```sql
CREATE INDEX idx_applications_org_job ON candidate_applications(organization_id, job_id);
CREATE INDEX idx_applications_candidate ON candidate_applications(candidate_id);
CREATE INDEX idx_applications_org_status ON candidate_applications(organization_id, status);
CREATE INDEX idx_applications_stage ON candidate_applications(current_stage_id);
CREATE INDEX idx_applications_applied_at ON candidate_applications(applied_at DESC);
```

---

## `candidate_scores` Table

Stores computed scoring results for a specific application. Scores are generated by the [[ai-pipeline|AI Pipeline]] after embeddings exist.

```sql
CREATE TABLE candidate_scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID NOT NULL REFERENCES candidate_applications(id) ON DELETE CASCADE,
    candidate_id        UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    semantic_score      DECIMAL(5,4) NOT NULL DEFAULT 0.0,
    skill_score         DECIMAL(5,4) NOT NULL DEFAULT 0.0,
    experience_score    DECIMAL(5,4) NOT NULL DEFAULT 0.0,
    overall_score       DECIMAL(5,4) NOT NULL DEFAULT 0.0,
    llm_summary         TEXT,
    llm_strengths       TEXT[],
    llm_gaps            TEXT[],
    interview_questions TEXT[],
    scoring_version     INTEGER NOT NULL DEFAULT 1,
    scored_at           TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|---|---|---|
| `application_id` | UUID | Job-specific candidate application |
| `candidate_id` | UUID | Denormalized candidate reference for fast lookup |
| `job_id` | UUID | Denormalized job reference for job-level ranking |
| `semantic_score` | DECIMAL(5,4) | Cosine similarity between candidate and job embeddings |
| `skill_score` | DECIMAL(5,4) | Required/preferred skill match score |
| `experience_score` | DECIMAL(5,4) | Experience match score |
| `overall_score` | DECIMAL(5,4) | Weighted hybrid score: `0.45×semantic + 0.30×skill + 0.25×experience` |
| `llm_summary` | TEXT | Ollama-generated narrative explanation; not used for scoring |
| `scoring_version` | INTEGER | Algorithm version for reproducibility |

### Constraints

| Constraint | Type | Details |
|---|---|---|
| `pk_candidate_scores` | PRIMARY KEY | `id` |
| `fk_scores_application` | FOREIGN KEY | `application_id → candidate_applications(id) ON DELETE CASCADE` |
| `fk_scores_candidate` | FOREIGN KEY | `candidate_id → candidates(id) ON DELETE CASCADE` |
| `fk_scores_job` | FOREIGN KEY | `job_id → jobs(id) ON DELETE CASCADE` |
| `uq_score_application_version` | UNIQUE | `(application_id, scoring_version)` |
| `chk_semantic_range` | CHECK | `semantic_score BETWEEN 0 AND 1` |
| `chk_skill_range` | CHECK | `skill_score BETWEEN 0 AND 1` |
| `chk_experience_range` | CHECK | `experience_score BETWEEN 0 AND 1` |
| `chk_overall_range` | CHECK | `overall_score BETWEEN 0 AND 1` |

### Indexes

```sql
CREATE INDEX idx_scores_application ON candidate_scores(application_id);
CREATE INDEX idx_scores_candidate ON candidate_scores(candidate_id);
CREATE INDEX idx_scores_job_overall ON candidate_scores(job_id, overall_score DESC);
CREATE INDEX idx_scores_version ON candidate_scores(scoring_version);
```

---

## Related Documents

- [[job-schema|Job Schema]] — Job posting and skills schema definitions.
- [[relationships|Entity Relationships]] — Full ER diagram and foreign key relationships.
- [[pgvector-notes|pgvector Notes]] — Vector column configuration and indexing strategies.
- [[ai-pipeline|AI Pipeline]] — How scores and embeddings are generated.
- [[semantic-matching|Semantic Matching]] — Cosine similarity and hybrid ranking formula.

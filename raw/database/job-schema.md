---
type: database
title: "Job Schema"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [database/schema, domain/jobs]
---

# Job Schema

## Overview

The job schema defines the structure for job postings and their associated skill requirements. Jobs are the anchor point for candidate matching — each job generates an embedding vector that is compared against candidate embeddings via [[semantic-matching|Semantic Matching]]. The `job_skills` table provides structured skill requirements that feed into the hybrid scoring formula.

All job data is **organization-scoped** via the `organization_id` foreign key.

---

## `jobs` Table

The primary table for storing job posting details, structured requirements, and the job embedding vector.

```sql
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    requirements    JSONB DEFAULT '{}',
    department      VARCHAR(100),
    location        VARCHAR(255),
    location_type   VARCHAR(20) DEFAULT 'onsite',
    salary_min      INTEGER,
    salary_max      INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    employment_type VARCHAR(20) DEFAULT 'full_time',
    experience_min  INTEGER DEFAULT 0,
    experience_max  INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    embedding       vector(384),
    published_at    TIMESTAMPTZ,
    closes_at       TIMESTAMPTZ,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key, auto-generated UUIDv4 |
| `organization_id` | UUID | FK to `organizations`. Enforces tenant isolation |
| `title` | VARCHAR(255) | Job title (e.g., "Senior Backend Developer") |
| `description` | TEXT | Full job description in markdown or plain text |
| `requirements` | JSONB | Structured requirements beyond skills (see structure below) |
| `department` | VARCHAR(100) | Department name (e.g., "Engineering", "Marketing") |
| `location` | VARCHAR(255) | Primary work location (e.g., "San Francisco, CA") |
| `location_type` | VARCHAR(20) | `onsite`, `remote`, `hybrid` |
| `salary_min` | INTEGER | Minimum annual salary (in smallest currency unit or whole number) |
| `salary_max` | INTEGER | Maximum annual salary |
| `salary_currency` | VARCHAR(3) | ISO 4217 currency code (default: `USD`) |
| `employment_type` | VARCHAR(20) | `full_time`, `part_time`, `contract`, `internship` |
| `experience_min` | INTEGER | Minimum years of experience required |
| `experience_max` | INTEGER | Maximum years (null = no upper limit) |
| `status` | VARCHAR(20) | Job status: `draft`, `published`, `paused`, `closed`, `archived` |
| `embedding` | vector(384) | BAAI `bge-small-en-v1.5` vector of the job description + requirements |
| `published_at` | TIMESTAMPTZ | When the job was first published (null if draft) |
| `closes_at` | TIMESTAMPTZ | Application deadline (null = open-ended) |
| `created_by` | UUID | FK to `users`. The recruiter who created the posting |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last modification timestamp |

### `requirements` JSONB Structure

```json
{
  "must_have": [
    "5+ years backend development experience",
    "Strong Python proficiency",
    "Experience with REST API design"
  ],
  "nice_to_have": [
    "Experience with Django or FastAPI",
    "Knowledge of machine learning concepts",
    "Open source contributions"
  ],
  "responsibilities": [
    "Design and implement scalable backend services",
    "Mentor junior developers",
    "Participate in architecture decisions"
  ],
  "benefits": [
    "Competitive salary + equity",
    "Remote-first culture",
    "Learning & development budget"
  ]
}
```

### Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| `pk_jobs` | PRIMARY KEY | `id` |
| `fk_jobs_org` | FOREIGN KEY | `organization_id → organizations(id) ON DELETE CASCADE` |
| `fk_jobs_creator` | FOREIGN KEY | `created_by → users(id) ON DELETE SET NULL` |
| `chk_jobs_status` | CHECK | `status IN ('draft','published','paused','closed','archived')` |
| `chk_jobs_location_type` | CHECK | `location_type IN ('onsite','remote','hybrid')` |
| `chk_jobs_employment_type` | CHECK | `employment_type IN ('full_time','part_time','contract','internship')` |
| `chk_jobs_salary` | CHECK | `salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max` |
| `chk_jobs_experience` | CHECK | `experience_min >= 0` |

### Indexes

```sql
-- Organization-scoped queries (primary access pattern)
CREATE INDEX idx_jobs_org ON jobs(organization_id);

-- Status filtering within an org
CREATE INDEX idx_jobs_org_status ON jobs(organization_id, status);

-- Department filtering
CREATE INDEX idx_jobs_org_department ON jobs(organization_id, department);

-- Vector similarity search
CREATE INDEX idx_jobs_embedding ON jobs
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);

-- Full-text search on title and description
CREATE INDEX idx_jobs_title_search ON jobs
USING gin (to_tsvector('english', title || ' ' || description));

-- Requirements JSONB queries
CREATE INDEX idx_jobs_requirements ON jobs USING gin (requirements);

-- Date-based queries
CREATE INDEX idx_jobs_published_at ON jobs(published_at DESC)
WHERE status = 'published';

CREATE INDEX idx_jobs_closes_at ON jobs(closes_at)
WHERE closes_at IS NOT NULL AND status = 'published';
```

---

## `job_skills` Table

Stores the individual skill requirements for each job. This table enables the **skill match scoring** component of the [[semantic-matching|Semantic Matching]] hybrid formula.

```sql
CREATE TABLE job_skills (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id      UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_name  VARCHAR(100) NOT NULL,
    category    VARCHAR(50),
    importance  VARCHAR(20) NOT NULL DEFAULT 'required',
    min_years   INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `job_id` | UUID | FK to `jobs`. The parent job posting |
| `skill_name` | VARCHAR(100) | Skill name (e.g., "Python", "React", "Machine Learning") |
| `category` | VARCHAR(50) | Skill category: `language`, `framework`, `tool`, `methodology`, `soft_skill` |
| `importance` | VARCHAR(20) | `required` (must-have) or `preferred` (nice-to-have) |
| `min_years` | INTEGER | Minimum years of experience with this skill (0 = any) |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |

### Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| `pk_job_skills` | PRIMARY KEY | `id` |
| `fk_job_skills_job` | FOREIGN KEY | `job_id → jobs(id) ON DELETE CASCADE` |
| `uq_job_skill_name` | UNIQUE | `(job_id, skill_name)` — prevents duplicate skill entries per job |
| `chk_job_skill_importance` | CHECK | `importance IN ('required', 'preferred')` |
| `chk_job_skill_years` | CHECK | `min_years >= 0` |

### Indexes

```sql
-- Skills for a specific job
CREATE INDEX idx_job_skills_job ON job_skills(job_id);

-- Skill name lookup (for cross-job skill analysis)
CREATE INDEX idx_job_skills_name ON job_skills(skill_name);

-- Required skills only (common filter for scoring)
CREATE INDEX idx_job_skills_required ON job_skills(job_id)
WHERE importance = 'required';
```

---

## Embedding Generation Trigger

When a job is created or its description/requirements are updated, an embedding regeneration is triggered:

```python
# apps/jobs/signals.py
@receiver(post_save, sender=Job)
def trigger_embedding_generation(sender, instance, created, **kwargs):
    if created or instance.tracker.has_changed('description') or instance.tracker.has_changed('requirements'):
        generate_job_embedding.delay(str(instance.id))
```

The embedding input is a concatenation of:
- Job title
- Job description
- Required skills (from `job_skills` where `importance = 'required'`)
- Must-have requirements (from `requirements.must_have`)

---

## Common Query Patterns

```sql
-- List published jobs for an organization with candidate counts
SELECT j.*, COUNT(a.id) AS application_count
FROM jobs j
LEFT JOIN candidate_applications a ON a.job_id = j.id
WHERE j.organization_id = :org_id AND j.status = 'published'
GROUP BY j.id
ORDER BY j.published_at DESC;

-- Find jobs matching a skill set
SELECT j.*
FROM jobs j
JOIN job_skills js ON js.job_id = j.id
WHERE j.organization_id = :org_id
  AND j.status = 'published'
  AND js.skill_name = ANY(:skills)
GROUP BY j.id
HAVING COUNT(DISTINCT js.skill_name) >= :min_match_count;
```

---

## Related Documents

- [[candidate-schema|Candidate Schema]] — Candidate data and scoring tables.
- [[relationships|Entity Relationships]] — Full ER diagram and foreign key relationships.
- [[ai-pipeline|AI Pipeline]] — How job embeddings are generated and used.
- [[semantic-matching|Semantic Matching]] — Vector similarity search and ranking formula.

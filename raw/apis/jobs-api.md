---
type: api
title: "Jobs API"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, recruitment/jobs]
---

# Jobs API

## Overview

The Jobs API manages the full lifecycle of job postings — creation, editing, publishing, and retrieval. It supports pagination, filtering, search, and provides aggregated statistics for each job. All endpoints require authentication and are scoped to the user's organization.

See [[job-schema|Job Schema]] for the database model and [[sprint-03-job-management|Sprint 3 — Job Management]] for implementation details.

## Base URL

```
/api/v1/jobs/
```

## Authentication

All endpoints require a valid `access_token` cookie. See [[auth-api|Authentication API]] for authentication details.

## Permissions

| Role | List | Create | Read | Update | Delete | Publish |
|------|------|--------|------|--------|--------|---------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Recruiter | ✅ | ✅ | ✅ | Own only | Own only | Own only |
| Viewer | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |

## Endpoint Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/jobs/` | List all jobs | Required |
| `POST` | `/api/v1/jobs/` | Create a new job | Required |
| `GET` | `/api/v1/jobs/{id}/` | Get job detail | Required |
| `PUT` | `/api/v1/jobs/{id}/` | Update job | Required |
| `DELETE` | `/api/v1/jobs/{id}/` | Soft delete job | Required |
| `POST` | `/api/v1/jobs/{id}/publish/` | Publish a draft job | Required |
| `GET` | `/api/v1/jobs/{id}/candidates/` | List candidates for job | Required |

---

## `GET /api/v1/jobs/`

List all jobs for the current organization with pagination and filtering.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page (max 100) |
| `status` | string | — | Filter: `draft`, `published`, `closed`, `archived` |
| `search` | string | — | Full-text search on title and description |
| `ordering` | string | `-created_at` | Sort field: `title`, `created_at`, `candidate_count` |

### Response — `200 OK`

```json
{
  "count": 45,
  "next": "/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440010",
      "title": "Senior Backend Engineer",
      "department": "Engineering",
      "location": "San Francisco, CA (Hybrid)",
      "employment_type": "full_time",
      "status": "published",
      "candidate_count": 28,
      "avg_score": 72.5,
      "created_at": "2025-05-10T09:00:00Z",
      "published_at": "2025-05-12T14:30:00Z"
    }
  ]
}
```

---

## `POST /api/v1/jobs/`

Create a new job posting (defaults to `draft` status).

### Request Body

```json
{
  "title": "Senior Backend Engineer",
  "department": "Engineering",
  "description": "We are looking for a senior backend engineer to lead...",
  "requirements": "- 5+ years Python experience\n- Django/FastAPI expertise\n- PostgreSQL proficiency\n- System design experience",
  "responsibilities": "- Design and implement APIs\n- Mentor junior engineers\n- Own service reliability",
  "location": "San Francisco, CA (Hybrid)",
  "employment_type": "full_time",
  "salary_range": {
    "min": 150000,
    "max": 200000,
    "currency": "USD"
  },
  "experience_level": "senior",
  "skills_required": ["Python", "Django", "PostgreSQL", "REST APIs", "Docker"]
}
```

### Validation Rules

| Field | Rules |
|-------|-------|
| `title` | Required, 5–200 characters |
| `description` | Required, 50–10000 characters |
| `requirements` | Required, 20–5000 characters |
| `location` | Required, 2–200 characters |
| `employment_type` | Enum: `full_time`, `part_time`, `contract`, `internship` |
| `salary_range` | Optional; if provided, `min` < `max` |
| `experience_level` | Enum: `entry`, `mid`, `senior`, `lead`, `executive` |

### Response — `201 Created`

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440010",
  "title": "Senior Backend Engineer",
  "status": "draft",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-05-22T10:00:00Z"
}
```

---

## `GET /api/v1/jobs/{id}/`

Get detailed information about a specific job, including aggregated statistics.

### Response — `200 OK`

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440010",
  "title": "Senior Backend Engineer",
  "department": "Engineering",
  "description": "We are looking for a senior backend engineer to lead...",
  "requirements": "- 5+ years Python experience\n...",
  "responsibilities": "- Design and implement APIs\n...",
  "location": "San Francisco, CA (Hybrid)",
  "employment_type": "full_time",
  "salary_range": { "min": 150000, "max": 200000, "currency": "USD" },
  "experience_level": "senior",
  "skills_required": ["Python", "Django", "PostgreSQL", "REST APIs", "Docker"],
  "status": "published",
  "stats": {
    "candidate_count": 28,
    "avg_score": 72.5,
    "top_score": 94.2,
    "stage_breakdown": {
      "Applied": 8,
      "Screening": 10,
      "Phone Interview": 5,
      "Technical Interview": 3,
      "Offer": 1,
      "Rejected": 1
    }
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-05-10T09:00:00Z",
  "published_at": "2025-05-12T14:30:00Z",
  "updated_at": "2025-05-20T16:45:00Z"
}
```

---

## `PUT /api/v1/jobs/{id}/`

Update an existing job posting. Partial updates are supported (PATCH semantics via PUT).

### Request Body

```json
{
  "title": "Senior Backend Engineer (Remote)",
  "salary_range": { "min": 160000, "max": 210000, "currency": "USD" }
}
```

### Response — `200 OK`

Returns the full updated job object (same schema as GET detail).

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `403` | `PERMISSION_DENIED` | User is not the owner or admin |
| `404` | `NOT_FOUND` | Job does not exist or is not in user's org |

---

## `DELETE /api/v1/jobs/{id}/`

Soft delete a job posting. Sets `status` to `archived` and `deleted_at` timestamp. Candidates are preserved but the job no longer appears in active listings.

### Response — `204 No Content`

---

## `POST /api/v1/jobs/{id}/publish/`

Transition a job from `draft` to `published` status. Validates that all required fields are populated before publishing.

### Response — `200 OK`

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440010",
  "status": "published",
  "published_at": "2025-05-22T14:30:00Z"
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `400` | `INCOMPLETE_JOB` | Missing required fields for publishing |
| `409` | `ALREADY_PUBLISHED` | Job is already in published status |

---

## `GET /api/v1/jobs/{id}/candidates/`

List all candidate applications associated with a job, including profile data, AI scores, and current pipeline stage.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page |
| `stage` | string | — | Filter by pipeline stage name |
| `min_score` | float | — | Minimum AI score |
| `ordering` | string | `-score` | Sort: `score`, `-score`, `applied_at`, `name` |

### Response — `200 OK`

```json
{
  "count": 28,
  "results": [
    {
      "candidate_id": "880e8400-e29b-41d4-a716-446655440020",
      "application_id": "990e8400-e29b-41d4-a716-446655440030",
      "full_name": "Alex Johnson",
      "email": "alex@example.com",
      "current_title": "Backend Developer",
      "overall_score": 87.3,
      "stage": "Technical Interview",
      "applied_at": "2025-05-15T08:30:00Z",
      "time_in_stage": "3 days"
    }
  ]
}
```

## Related Pages

- [[job-schema|Job Schema]] — Database model and migration details
- [[sprint-03-job-management|Sprint 3 — Job Management]] — Sprint implementation plan
- [[candidate-api|Candidate API]] — Candidate endpoints linked to jobs
- [[pipeline-board|Pipeline Board]] — Visual board filtered by job
- [[auth-api|Authentication API]] — Authentication requirements

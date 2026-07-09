---
type: api
title: "Candidate API"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, recruitment/candidates]
---

# Candidate API

## Overview

The Candidate API manages the full lifecycle of candidate profiles and job applications — from creation and resume upload to AI scoring retrieval and semantic search. It integrates with the [[ai-pipeline|AI Pipeline]] for resume parsing and scoring, and with [[semantic-search|Semantic Search]] for natural language candidate discovery.

See [[candidate-schema|Candidate Schema]] for the database model.

## Base URL

```
/api/v1/candidates/
```

## Authentication

All endpoints require a valid `access_token` cookie. Results are scoped to the authenticated user's organization.

## Endpoint Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/candidates/` | List candidates | Required |
| `POST` | `/api/v1/candidates/` | Create candidate | Required |
| `GET` | `/api/v1/candidates/{id}/` | Candidate detail | Required |
| `PUT` | `/api/v1/candidates/{id}/` | Update candidate | Required |
| `POST` | `/api/v1/candidates/{id}/upload-resume/` | Upload resume | Required |
| `GET` | `/api/v1/candidates/{id}/applications/{application_id}/scores/` | Application score breakdown | Required |
| `POST` | `/api/v1/candidates/bulk-upload/` | Bulk resume upload | Required |
| `GET` | `/api/v1/candidates/search/` | Semantic search | Required |

---

## `GET /api/v1/candidates/`

List all candidates for the current organization with pagination and filtering. Job, stage, and score filters operate through `candidate_applications`.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page (max 100) |
| `job_id` | UUID | — | Filter by job posting |
| `stage` | string | — | Filter by current pipeline stage |
| `min_score` | float | — | Minimum overall AI score |
| `max_score` | float | — | Maximum overall AI score |
| `search` | string | — | Keyword search on name, email, skills |
| `has_resume` | bool | — | Filter by resume upload status |
| `ordering` | string | `-created_at` | Sort: `name`, `score`, `created_at`, `stage` |

### Response — `200 OK`

```json
{
  "count": 156,
  "next": "/api/v1/candidates/?page=2",
  "previous": null,
  "results": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440020",
      "application_id": "990e8400-e29b-41d4-a716-446655440030",
      "full_name": "Alex Johnson",
      "email": "alex@example.com",
      "current_title": "Senior Backend Developer",
      "overall_score": 87.3,
      "stage": "Technical Interview",
      "job": {
        "id": "770e8400-e29b-41d4-a716-446655440010",
        "title": "Senior Backend Engineer"
      },
      "has_resume": true,
      "is_parsed": true,
      "created_at": "2025-05-15T08:30:00Z"
    }
  ]
}
```

---

## `POST /api/v1/candidates/`

Create or reuse a candidate profile, then create a job-specific application. Optionally include a resume file as multipart form data.

### Request — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | Yes | Candidate's full name |
| `email` | string | Yes | Unique email address |
| `phone` | string | No | Phone number |
| `job_id` | UUID | Yes | Job posting to associate with |
| `source` | string | No | How they applied: `direct`, `referral`, `linkedin`, `agency` |
| `resume` | file | No | Resume file (PDF or DOCX, max 10 MB) |
| `notes` | string | No | Recruiter notes |

### Response — `201 Created`

```json
{
  "candidate_id": "880e8400-e29b-41d4-a716-446655440020",
  "application_id": "990e8400-e29b-41d4-a716-446655440030",
  "full_name": "Alex Johnson",
  "email": "alex@example.com",
  "job_id": "770e8400-e29b-41d4-a716-446655440010",
  "stage": "Applied",
  "resume_uploaded": true,
  "parsing_status": "queued",
  "created_at": "2025-05-22T10:00:00Z"
}
```

If a resume is included, the [[ai-pipeline|AI Pipeline]] is triggered automatically (parsing → embedding → scoring). Scoring is stored against the application.

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `400` | `VALIDATION_ERROR` | Invalid or missing required fields |
| `409` | `DUPLICATE_APPLICATION` | Candidate already has an application for this job |
| `413` | `FILE_TOO_LARGE` | Resume exceeds 10 MB limit |
| `415` | `UNSUPPORTED_FORMAT` | File is not PDF or DOCX |

---

## `GET /api/v1/candidates/{id}/`

Get comprehensive candidate details. When `application_id` is supplied, the response also includes job-specific scores, current stage, pipeline history, and feedback for that application.

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `include` | string | Comma-separated: `scores`, `parsed_data`, `pipeline_history`, `feedback` |
| `application_id` | UUID | Optional job application context for job-specific fields |

### Response — `200 OK`

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440020",
  "full_name": "Alex Johnson",
  "email": "alex@example.com",
  "phone": "+1-555-0123",
  "current_title": "Senior Backend Developer",
  "application": {
    "id": "990e8400-e29b-41d4-a716-446655440030",
    "job": {
      "id": "770e8400-e29b-41d4-a716-446655440010",
      "title": "Senior Backend Engineer"
    },
    "stage": "Technical Interview",
    "source": "direct"
  },
  "scores": {
    "overall": 87.3,
    "skill_match": 92.0,
    "experience_relevance": 85.0,
    "semantic_similarity": 93.1,
    "explanation": "Strong Python and Django experience aligning with job requirements..."
  },
  "parsed_data": {
    "summary": "Experienced backend developer with 7 years of...",
    "experience": [
      {
        "title": "Senior Backend Developer",
        "company": "TechCorp",
        "start_date": "2021-03",
        "end_date": "Present",
        "achievements": ["Led migration to microservices...", "Reduced API latency by 40%..."]
      }
    ],
    "skills": ["Python", "Django", "PostgreSQL", "Docker", "Kubernetes"],
    "education": [
      { "degree": "B.S. Computer Science", "institution": "UC Berkeley", "graduation_date": "2018-05" }
    ]
  },
  "pipeline_history": [
    { "stage": "Applied", "entered_at": "2025-05-15T08:30:00Z", "moved_by": "System" },
    { "stage": "Screening", "entered_at": "2025-05-16T10:00:00Z", "moved_by": "Jane Recruiter" },
    { "stage": "Technical Interview", "entered_at": "2025-05-19T14:00:00Z", "moved_by": "Jane Recruiter", "notes": "Strong resume, advancing to tech screen" }
  ],
  "resume_url": "/api/v1/candidates/880e8400/resume/download/",
  "created_at": "2025-05-15T08:30:00Z",
  "updated_at": "2025-05-20T16:00:00Z"
}
```

---

## `PUT /api/v1/candidates/{id}/`

Update candidate information. Supports partial updates.

### Request Body

```json
{
  "phone": "+1-555-0456",
  "notes": "Referred by engineering team lead"
}
```

### Response — `200 OK`

Returns the full updated candidate object.

---

## `POST /api/v1/candidates/{id}/upload-resume/`

Upload or replace a candidate's resume. Triggers the full [[ai-pipeline|AI Pipeline]] (parsing → embedding → scoring).

### Request — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume` | file | Yes | PDF or DOCX file, max 10 MB |

### Response — `202 Accepted`

```json
{
  "message": "Resume uploaded successfully. Parsing has been queued.",
  "task_id": "task-abc123-def456",
  "parsing_status": "queued"
}
```

The `202 Accepted` status indicates the upload was received but parsing is async. Use [[ai-api|AI API]] to poll parsing status via the `task_id`.

---

## `GET /api/v1/candidates/{id}/applications/{application_id}/scores/`

Get the full application-level AI score breakdown with LLM-generated explanations.

### Response — `200 OK`

```json
{
  "candidate_id": "880e8400-e29b-41d4-a716-446655440020",
  "application_id": "990e8400-e29b-41d4-a716-446655440030",
  "job_id": "770e8400-e29b-41d4-a716-446655440010",
  "overall_score": 87.3,
  "dimensions": {
    "skill_match": {
      "score": 92.0,
      "explanation": "Candidate demonstrates strong proficiency in 4 of 5 required skills (Python, Django, PostgreSQL, Docker). Kubernetes experience is listed but with limited depth."
    },
    "experience_relevance": {
      "score": 85.0,
      "explanation": "7 years of backend development experience with progressive seniority. Recent role involves system design and team leadership, aligning well with senior-level expectations."
    },
    "semantic_similarity": {
      "score": 93.1,
      "explanation": "Resume content shows very high semantic alignment with the job description, particularly in backend architecture and API design areas."
    }
  },
  "ai_summary": "Alex Johnson is a strong match for the Senior Backend Engineer role. Key strengths include deep Python/Django expertise and relevant system design experience. Recommended focus areas for interview: Kubernetes depth, distributed systems patterns.",
  "scored_at": "2025-05-15T09:15:00Z",
  "model_version": "qwen2.5-coder:7b"
}
```

---

## `POST /api/v1/candidates/bulk-upload/`

Upload multiple resumes at once. Each file creates or reuses a candidate profile, creates a job application, and triggers the parsing pipeline.

### Request — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_id` | UUID | Yes | Job to associate all candidates with |
| `resumes` | file[] | Yes | Multiple PDF/DOCX files (max 20 files, 10 MB each) |
| `source` | string | No | Default source for all candidates |

### Response — `202 Accepted`

```json
{
  "message": "15 resumes uploaded successfully. Parsing has been queued.",
  "candidates_created": 15,
  "applications_created": 15,
  "duplicates_skipped": 2,
  "task_ids": ["task-001", "task-002", "..."]
}
```

---

## `GET /api/v1/candidates/search/?q=`

Semantic search across all candidates using natural language. See [[semantic-search|Semantic Search]] for the full search architecture.

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Natural language query (required) |
| `job_id` | UUID | Scope search to a specific job |
| `limit` | int | Max results (default 20, max 50) |
| `min_relevance` | float | Minimum relevance score (0.0–1.0) |

### Response — `200 OK`

```json
{
  "query": "Python developer with ML experience",
  "results": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440020",
      "application_id": "990e8400-e29b-41d4-a716-446655440030",
      "full_name": "Alex Johnson",
      "relevance_score": 0.89,
      "highlights": ["7 years Python experience", "Built ML pipeline for recommendation engine"],
      "current_title": "Senior Backend Developer",
      "stage": "Technical Interview",
      "job_title": "Senior Backend Engineer"
    }
  ],
  "total_results": 12,
  "search_time_ms": 145
}
```

## Related Pages

- [[candidate-schema|Candidate Schema]] — Database model and JSONB structure
- [[ai-pipeline|AI Pipeline]] — Resume parsing and scoring workflow
- [[semantic-search|Semantic Search]] — Natural language search architecture
- [[resume-parser|Resume Parser]] — Resume parsing feature details
- [[candidate-dashboard|Candidate Dashboard]] — Frontend consuming this API
- [[auth-api|Authentication API]] — Authentication requirements

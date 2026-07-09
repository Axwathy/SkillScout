---
type: api
title: "Pipeline API"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, api, recruitment/pipeline]
---

# Pipeline API

## Overview
API endpoints for managing the Kanban-style hiring pipeline, stage transitions, and application history.

## Endpoints

### 1. List Pipeline Stages
`GET /api/v1/pipeline/stages/`
- **Description:** Get all pipeline stages ordered by their sequential order.
- **Query Params:** `job_id` (optional, for job-specific stages)
- **Response:**
  ```json
  {
    "stages": [
      {
        "id": "uuid",
        "name": "Applied",
        "order": 1,
        "is_default": true
      }
    ]
  }
  ```

### 2. Create Custom Stage
`POST /api/v1/pipeline/stages/`
- **Description:** Add a new custom stage for an organization or specific job.
- **Request Body:**
  ```json
  {
    "name": "Technical Assessment",
    "order": 3,
    "job_id": "uuid (optional)"
  }
  ```
- **Permissions:** Admin or Recruiter only.

### 3. Update Stage
`PUT /api/v1/pipeline/stages/{id}/`
- **Description:** Rename a stage or change its order.
- **Request Body:** `{"name": "string", "order": "integer"}`

### 4. Delete Stage
`DELETE /api/v1/pipeline/stages/{id}/`
- **Description:** Remove a stage. Requires a strategy for reassigning candidates currently in this stage (e.g., move to default fallback stage).
- **Request Body:** `{"fallback_stage_id": "uuid"}`

### 5. Move Application to Stage
`POST /api/v1/pipeline/move/`
- **Description:** Move a job-specific candidate application from its current stage to a new one. Records the transition in history.
- **Request Body:**
  ```json
  {
    "application_id": "uuid",
    "stage_id": "uuid",
    "notes": "Completed initial screening, strong communication skills."
  }
  ```

### 6. Get Pipeline Board
`GET /api/v1/pipeline/board/{job_id}/`
- **Description:** Get the full Kanban board structure for a job, including stages and applications within each stage.
- **Response:** Nested JSON with stages containing arrays of candidate summary objects.

### 7. Get Application Stage History
`GET /api/v1/pipeline/history/{application_id}/`
- **Description:** Retrieve the chronological log of stage transitions for a specific job application.

## Edge Cases & Error Handling
- **Concurrent Moves:** Handle race conditions if multiple recruiters try to move a candidate simultaneously.
- **Invalid Stage ID:** Returns 404.
- **Permissions:** Ensure the user has access to the job and application before allowing moves.

See also: [[pipeline-schema|Pipeline Schema]], [[pipeline-board|Pipeline Board]]

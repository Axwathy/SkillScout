---
type: api
title: "AI API"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, api, ai/llm, ai/ml]
---

# AI API

## Overview
Endpoints for triggering and retrieving results from the AI pipeline, including resume parsing, scoring, search, and interview generation. Most heavy operations are asynchronous and return a task ID.

## Endpoints

### 1. Trigger Resume Parsing
`POST /api/v1/ai/parse-resume/`
- **Description:** Kick off the asynchronous resume parsing and embedding generation pipeline.
- **Request Body:** `{"candidate_id": "uuid"}`
- **Response:**
  ```json
  {
    "task_id": "uuid",
    "status": "processing"
  }
  ```

### 2. Check Parsing Status
`GET /api/v1/ai/parse-resume/{task_id}/`
- **Description:** Poll for the completion status of a parsing task.
- **Response:** `{"status": "completed|failed|processing", "result": {...}}`

### 3. Trigger Candidate Scoring
`POST /api/v1/ai/score/`
- **Description:** Asynchronously calculate the hybrid score and generate the LLM explanation for a candidate application.
- **Request Body:** `{"application_id": "uuid"}`
- **Response:** `{"task_id": "uuid"}`

### 4. Get Score with Explanation
`GET /api/v1/ai/score/{application_id}/`
- **Description:** Retrieve the finalized scores and LLM-generated breakdown.
- **Response:**
  ```json
  {
    "application_id": "uuid",
    "candidate_id": "uuid",
    "job_id": "uuid",
    "overall_score": 85,
    "semantic_score": 88,
    "skill_score": 82,
    "experience_score": 85,
    "explanation": {
      "strengths": ["React", "System Design"],
      "weaknesses": ["Docker deployment"],
      "recommendation_context": "Strong frontend fit, may need infra support."
    }
  }
  ```

### 5. Generate Interview Questions
`POST /api/v1/ai/interview-questions/`
- **Description:** Synchronous endpoint to generate customized interview questions based on the candidate's parsed resume and the job's requirements.
- **Request Body:** `{"application_id": "uuid", "focus_areas": ["system design", "leadership"]}`

### 6. Semantic Search
`POST /api/v1/ai/search/`
- **Description:** Search across candidates using natural language query via vector similarity.
- **Request Body:** `{"query": "senior frontend engineer with web3 experience", "job_id": "uuid (optional filter)"}`

### 7. AI API Usage Stats
`GET /api/v1/ai/usage/`
- **Description:** Internal endpoint to track token usage and API calls for billing purposes across the organization.

## Rate Limiting
- AI endpoints are strictly rate-limited (e.g., 10 requests/minute per user) due to downstream API costs.

See also: [[ai-pipeline|AI Pipeline]], [[candidate-scoring|Candidate Insight Generator]], [[interview-generation|Interview Question Generation]]

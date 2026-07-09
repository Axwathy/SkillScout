---
type: api
title: "API Design"
date_created: 2026-05-22
date_updated: 2026-05-22
tags: [product/architecture, api]
---

# API Design

This document defines cross-cutting API conventions for the recruitment SaaS.

## Base URL

All product API endpoints use the versioned prefix:

```text
/api/v1/
```

Examples:

- `POST /api/v1/auth/login/`
- `GET /api/v1/jobs/`
- `GET /api/v1/candidates/`
- `POST /api/v1/ai/score/`

## Conventions

- Use RESTful resource names with plural nouns.
- Use trailing slashes consistently because Django REST Framework defaults to them.
- Return paginated lists with `count`, `next`, `previous`, and `results`.
- Use `202 Accepted` for asynchronous AI tasks that return a task ID.
- Use consistent error payloads: `code`, `message`, and optional `details`.
- Scope every request by organization from the authenticated user context.

## Error Shape

```json
{
  "code": "validation_error",
  "message": "The submitted data is invalid.",
  "details": {
    "email": ["This field is required."]
  }
}
```

## Related Documents

- [[auth-api|Authentication API]]
- [[jobs-api|Jobs API]]
- [[candidate-api|Candidate API]]
- [[pipeline-api|Pipeline API]]
- [[ai-api|AI API]]

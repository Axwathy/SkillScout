---
type: architecture
title: "Project Structure"
date_created: 2026-05-22
date_updated: 2026-05-22
tags: [product/architecture, engineering/structure]
---

# Project Structure

This document defines the intended monorepo layout for the AI Recruitment SaaS implementation.

## Repository Layout

```text
/
├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── organizations/
│   │   ├── jobs/
│   │   ├── candidates/
│   │   ├── pipeline/
│   │   ├── analytics/
│   │   └── ai_engine/
│   ├── config/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   └── package.json
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx/
└── docs/
```

## Rules

- Keep business logic in backend service modules, not directly in views.
- Keep API contracts mirrored between `backend/apps/*/serializers.py` and frontend `types/`.
- Keep deployment configuration under `infrastructure/` unless a platform requires colocated config.
- Keep AI prompts versioned separately from runtime code so prompt changes can be reviewed and rolled back.

## Related Documents

- [[system-overview|System Overview]]
- [[backend-architecture|Backend Architecture]]
- [[frontend-architecture|Frontend Architecture]]
- [[docker-setup|Docker Setup]]

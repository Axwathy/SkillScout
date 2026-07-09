---
type: architecture
title: "Deployment Architecture"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, devops/deployment, devops/ci-cd]
---

# Deployment Architecture

## Overview

The platform follows a **split deployment model**: the Next.js frontend is deployed to **Vercel** for edge-optimized delivery, while the Django backend runs on **Railway** with Docker containers. The database and file storage are managed by **Supabase**. This architecture balances developer experience, cost efficiency, and production reliability.

---

## Production Architecture

```
┌──────────────┐     HTTPS      ┌────────────────┐
│   Browser    │ ──────────────→│    Vercel       │
│  (Next.js)   │                │   (Frontend)    │
└──────┬───────┘                └────────────────┘
       │                               │
       │ API calls (/api/v1/*)         │ SSR data fetching
       ▼                               ▼
┌──────────────────────────────────────────────┐
│              API Gateway / Nginx              │
│         (Railway — reverse proxy)             │
└──────────────────┬───────────────────────────┘
                   │
       ┌───────────┼───────────────┐
       ▼           ▼               ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│  Django    │ │  Celery    │ │  Celery    │
│  Web (×2)  │ │  Worker(×2)│ │  Beat      │
│  Gunicorn  │ │  AI tasks  │ │  Scheduler │
└─────┬──────┘ └─────┬──────┘ └────────────┘
      │               │
      ▼               ▼
┌──────────────────────────────┐
│          Supabase            │
│  ┌──────────┐ ┌───────────┐ │
│  │PostgreSQL│ │  Storage   │ │
│  │+ pgvector│ │  (Resumes) │ │
│  └──────────┘ └───────────┘ │
└──────────────────────────────┘
      │
      ▼
┌──────────────┐
│    Redis     │
│  (Railway)   │
│ Cache+Broker │
└──────────────┘
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# Triggered on push to main or PR
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    # Run test suite (pytest, type checking, linting)
  build:
    # Build Docker image, push to registry
  deploy-staging:
    # Deploy to staging (on PR merge to main)
  deploy-production:
    # Deploy to production (manual approval gate)
```

### Pipeline Stages

| Stage | Trigger | Actions | Duration |
|-------|---------|---------|----------|
| **Lint & Type Check** | Every push | ESLint, mypy, black, isort | ~1 min |
| **Unit Tests** | Every push | pytest (Django), Jest (Next.js) | ~3 min |
| **Integration Tests** | PR to main | API tests with test DB | ~5 min |
| **Build** | PR approved | Docker image build + push | ~3 min |
| **Deploy Staging** | Merge to main | Auto-deploy to staging | ~2 min |
| **Deploy Production** | Manual approval | Blue-green deploy to Railway | ~2 min |

---

## Environment Management

| Environment | Purpose | Infrastructure | Data |
|-------------|---------|---------------|------|
| **Development** | Local development | Docker Compose (all services) | Seeded test data |
| **Staging** | Pre-production testing | Railway (free tier), Supabase (dev project) | Anonymized production subset |
| **Production** | Live service | Railway (pro), Supabase (pro), Vercel (pro) | Real data |

### Environment Variables

All secrets are managed via Railway's environment variable system and Vercel's project settings. No secrets are committed to the repository.

```bash
# Backend (.env)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
OLLAMA_BASE_URL=https://ollama-internal.example.com
LLM_MODEL=qwen2.5-coder:7b
LLM_FALLBACK_MODELS=mistral,phi3
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
DJANGO_SECRET_KEY=...
ALLOWED_HOSTS=api.myapp.com
CORS_ALLOWED_ORIGINS=https://myapp.com

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.myapp.com
```

---

## Scaling Strategy

### Horizontal Scaling

| Component | Scaling Method | Trigger |
|-----------|---------------|---------|
| **Django Web** | Railway replicas (2→8) | CPU > 70% or response time > 500ms |
| **Celery Workers** | Railway replicas (2→6) | Queue depth > 100 tasks |
| **Frontend** | Vercel auto-scales | Handled by Vercel edge network |
| **Database** | Supabase compute add-ons | Connection count, query latency |
| **Redis** | Railway memory scaling | Memory usage > 80% |

### Database Scaling

1. **Connection Pooling** — Supabase's built-in PgBouncer (transaction mode) handles connection pooling. Django connects via the pooler URL.
2. **Read Replicas** — For analytics-heavy queries, Supabase read replicas can be provisioned to offload reporting workloads.
3. **Partitioning** — Candidate data partitioned by `organization_id` for large tenants (future consideration).

---

## Monitoring & Logging

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Sentry** | Error tracking, performance monitoring | Django + Next.js SDKs |
| **Railway Logs** | Container logs, deploy events | Built-in |
| **Vercel Analytics** | Frontend performance, Web Vitals | Built-in |
| **Flower** | Celery task monitoring dashboard | Self-hosted on Railway |
| **Supabase Dashboard** | Database metrics, query performance | Built-in |
| **Uptime Robot** | Endpoint health checks | External |

### Alerting Rules

| Condition | Severity | Channel |
|-----------|----------|---------|
| API error rate > 5% (5 min window) | Critical | Slack + PagerDuty |
| Response time p95 > 2s | Warning | Slack |
| Celery queue depth > 500 | Warning | Slack |
| Database connections > 80% pool | Critical | Slack + PagerDuty |
| Disk usage > 90% | Critical | PagerDuty |

---

## Docker Configuration

See [[docker-setup|Docker Setup]] for the complete `Dockerfile` and `docker-compose.yml` configuration.

```dockerfile
# Backend Dockerfile (simplified)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## Related Documents

- [[docker-setup|Docker Setup]] — Complete Docker and Docker Compose configuration files.
- [[ci-cd|CI/CD Pipeline]] — Detailed GitHub Actions workflow definitions.
- [[vercel-deployment|Vercel Deployment]] — Frontend deployment configuration and edge functions.
- [[railway-deployment|Railway Deployment]] — Backend deployment, scaling, and service configuration.
- [[nginx-gunicorn|Nginx + Gunicorn Configuration]] — Reverse proxy and WSGI server tuning.
- [[system-overview|System Overview]] — High-level platform architecture.

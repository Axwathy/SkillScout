---
type: deployment
title: "Railway Deployment"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, deployment]
---

# Railway Deployment

This document covers the deployment of the **Django backend** on Railway, including service configuration, database strategy, scaling, and operational procedures.

See also: [[backend-architecture|Backend Architecture]], [[deployment-architecture|Deployment Architecture]]

---

## Why Railway

| Factor             | Benefit                                               |
|--------------------|-------------------------------------------------------|
| Docker-native      | Deploys directly from Dockerfile                      |
| Built-in Postgres  | One-click PostgreSQL addon with automated backups     |
| Redis addon        | Managed Redis instance for caching and Celery broker  |
| Environments       | Separate staging/production with shared config        |
| GitHub integration | Auto-deploy on push to configured branches            |
| Transparent pricing| Pay-per-use with no cold starts                       |

---

## Service Architecture on Railway

```
┌─────────────────────────────────────────────────┐
│                Railway Project                   │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │   Django      │  │  Celery      │             │
│  │   Web Server  │  │  Worker      │             │
│  │   (Gunicorn)  │  │              │             │
│  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                     │
│  ┌──────┴──────────────────┴───────┐             │
│  │       PostgreSQL (pgvector)      │             │
│  └──────────────────────────────────┘             │
│                                                  │
│  ┌──────────────────────────────────┐             │
│  │       Redis (Cache + Broker)      │             │
│  └──────────────────────────────────┘             │
│                                                  │
│  ┌──────────────┐                                │
│  │  Celery Beat  │                                │
│  │  (Scheduler)  │                                │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

---

## Service Configuration

### Django Web Server

| Setting            | Value                                       |
|--------------------|---------------------------------------------|
| Build command       | `docker build -f Dockerfile .`             |
| Start command       | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4` |
| Health check path   | `/api/v1/health/`                          |
| Replicas            | 1 (staging), 2+ (production)               |
| Region              | US East (`us-east-1`)                      |

### Celery Worker

| Setting            | Value                                       |
|--------------------|---------------------------------------------|
| Start command       | `celery -A config worker -l info -c 4`     |
| Health check        | Custom Celery inspect ping                  |
| Replicas            | 1 (staging), 2+ (production)               |

### Celery Beat

| Setting            | Value                                       |
|--------------------|---------------------------------------------|
| Start command       | `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` |
| Replicas            | **Always 1** (exactly-once scheduling)      |

---

## Database Strategy

### Option A: Railway PostgreSQL Addon (Current)

- **Pros**: Zero config, automatic backups, integrated networking, no egress fees
- **Cons**: No pgvector pre-installed (requires manual extension install), limited scaling options
- **Setup**: Add PostgreSQL plugin → Railway auto-injects `DATABASE_URL`

```sql
-- Enable pgvector after provisioning
CREATE EXTENSION IF NOT EXISTS vector;
```

### Option B: Supabase External DB (Planned for Production)

- **Pros**: pgvector pre-installed, connection pooling via Supavisor, Row Level Security, dashboard for data inspection, generous free tier
- **Cons**: External connection adds ~5ms latency, requires managing connection strings
- **Setup**: Use Supabase connection pooler URL in `DATABASE_URL`

| Aspect           | Railway Postgres   | Supabase             |
|------------------|--------------------|----------------------|
| pgvector support | Manual install     | Pre-installed        |
| Backups          | Daily automated    | Point-in-time recovery|
| Connection pooling| Manual (pgbouncer)| Built-in (Supavisor) |
| Dashboard        | None               | Full SQL editor      |
| Cost             | $5/GB/mo           | Free up to 500MB     |
| Latency          | Internal (~1ms)    | External (~5-10ms)   |

**Decision**: Use Railway PostgreSQL for staging, Supabase for production. See [[deployment-architecture|Deployment Architecture]] for rationale.

---

## Redis Addon

- **Purpose**: Django cache backend + Celery message broker
- **Setup**: Add Redis plugin → Railway auto-injects `REDIS_URL`
- **Configuration**: Use separate Redis databases for cache (db 0) and Celery (db 1)

```python
# settings/production.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{os.environ['REDIS_URL']}/0",
    }
}
CELERY_BROKER_URL = f"{os.environ['REDIS_URL']}/1"
```

---

## Environment Variables

| Variable                | Staging                          | Production                      |
|-------------------------|----------------------------------|---------------------------------|
| `DATABASE_URL`          | Railway internal                 | Supabase pooler URL             |
| `REDIS_URL`             | Railway internal                 | Railway internal                |
| `DJANGO_SECRET_KEY`     | Staging secret                   | Production secret               |
| `DJANGO_SETTINGS_MODULE`| `config.settings.staging`       | `config.settings.production`    |
| `ALLOWED_HOSTS`         | `staging-api.example.com`       | `api.example.com`               |
| `CORS_ALLOWED_ORIGINS`  | `https://staging.example.com`   | `https://app.example.com`       |
| `OLLAMA_BASE_URL`       | Staging model endpoint           | Production model endpoint       |
| `LLM_MODEL`             | `qwen2.5-coder:7b`               | `qwen2.5-coder:7b`              |
| `LLM_FALLBACK_MODELS`   | `mistral,phi3`                   | `mistral,phi3`                  |
| `EMBEDDING_MODEL`       | `BAAI/bge-small-en-v1.5`         | `BAAI/bge-small-en-v1.5`        |
| `EMBEDDING_DIMENSIONS`  | `384`                            | `384`                           |
| `SENTRY_DSN`            | Staging DSN                      | Production DSN                  |

---

## Scaling

### Horizontal Scaling

- **Web server**: Increase replicas from 1 → N in Railway dashboard or `railway.json`
- **Celery workers**: Scale independently based on queue depth
- **Load balancing**: Railway automatically distributes traffic across replicas

### Vertical Scaling

| Tier           | vCPU | RAM   | Recommended For        |
|----------------|------|-------|------------------------|
| Starter        | 1    | 512MB | Development/staging    |
| Pro            | 2    | 2GB   | Early production       |
| Pro (scaled)   | 4    | 8GB   | Growth stage           |

### Auto-Scaling Triggers

- CPU usage > 70% sustained for 5 minutes → scale up
- Queue depth > 100 pending tasks → add Celery worker
- Response time P95 > 500ms → investigate and scale

---

## Custom Domains

1. Navigate to Railway service → Settings → Domains
2. Add custom domain: `api.example.com`
3. Configure DNS:
   - **CNAME**: `api.example.com` → `<project>.up.railway.app`
4. Railway auto-provisions SSL via Let's Encrypt
5. Enable "Force HTTPS" redirect

---

## Health Checks

### Django Health Endpoint

```python
# api/v1/health/views.py
from django.http import JsonResponse
from django.db import connection
from django_redis import get_redis_connection

def health_check(request):
    checks = {}

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Redis check
    try:
        redis = get_redis_connection("default")
        redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    status = 200 if all(v == "healthy" for v in checks.values()) else 503
    return JsonResponse({"status": "ok" if status == 200 else "degraded", "checks": checks}, status=status)
```

### Railway Health Check Config

```json
{
  "healthcheckPath": "/api/v1/health/",
  "healthcheckTimeout": 10,
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 5
}
```

---

## Deployment Checklist

- [ ] Run `python manage.py check --deploy` locally
- [ ] Verify all environment variables are set for the target environment
- [ ] Confirm database migrations are backwards-compatible
- [ ] Check Celery task signatures haven't changed in incompatible ways
- [ ] Review Railway build logs for warnings
- [ ] Verify health check endpoint returns 200 after deploy
- [ ] Monitor error rates in Sentry for 15 minutes post-deploy

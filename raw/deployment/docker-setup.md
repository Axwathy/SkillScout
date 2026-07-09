---
type: deployment
title: "Docker Setup"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, deployment]
---

# Docker Setup

This document describes the Docker Compose configuration used for local development of the AI Recruitment SaaS platform. All services are orchestrated via `docker-compose.yml` to ensure a consistent, reproducible development environment across the team.

See also: [[deployment-architecture|Deployment Architecture]], [[backend-architecture|Backend Architecture]]

---

## Services Overview

| Service         | Image / Build       | Port  | Purpose                              |
|-----------------|---------------------|-------|--------------------------------------|
| `django`        | Custom Dockerfile   | 8000  | Django web application (API + Admin) |
| `postgres`      | `pgvector/pgvector:pg16` | 5432  | PostgreSQL with pgvector extension   |
| `redis`         | `redis:7-alpine`    | 6379  | Cache layer + Celery message broker  |
| `ollama`        | `ollama/ollama`     | 11434 | Local LLM inference for development  |
| `celery-worker` | Custom Dockerfile   | —     | Async task processing                |
| `celery-beat`   | Custom Dockerfile   | —     | Periodic task scheduler              |

---

## Sample `docker-compose.yml`

```yaml
version: "3.9"

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: recruitment_db
      POSTGRES_USER: recruit_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U recruit_user -d recruitment_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  django:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - static_files:/app/staticfiles
      - media_files:/app/media
    environment:
      - DATABASE_URL=postgres://recruit_user:${POSTGRES_PASSWORD:-changeme}@postgres:5432/recruitment_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - OLLAMA_BASE_URL=http://ollama:11434
      - LLM_MODEL=qwen2.5-coder:7b
      - LLM_FALLBACK_MODELS=mistral,phi3
      - EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
      - EMBEDDING_DIMENSIONS=384
      - DEBUG=True
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ollama:
        condition: service_started

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A config worker -l info --concurrency=2
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgres://recruit_user:${POSTGRES_PASSWORD:-changeme}@postgres:5432/recruitment_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - OLLAMA_BASE_URL=http://ollama:11434
      - LLM_MODEL=qwen2.5-coder:7b
      - LLM_FALLBACK_MODELS=mistral,phi3
      - EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
      - EMBEDDING_DIMENSIONS=384
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ollama:
        condition: service_started

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgres://recruit_user:${POSTGRES_PASSWORD:-changeme}@postgres:5432/recruitment_db
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
  redis_data:
  static_files:
  media_files:
  ollama_data:
```

---

## Environment Variables

All sensitive configuration is managed through a `.env` file at the project root (never committed to version control).

| Variable                | Description                        | Default          |
|-------------------------|------------------------------------|------------------|
| `POSTGRES_PASSWORD`     | Database password                  | `changeme`       |
| `OLLAMA_BASE_URL`       | Ollama endpoint for local LLM calls | `http://ollama:11434` |
| `LLM_MODEL`             | Primary local LLM for insights      | `qwen2.5-coder:7b` |
| `LLM_FALLBACK_MODELS`   | Comma-separated fallback LLMs       | `mistral,phi3` |
| `EMBEDDING_MODEL`       | Embedding model identifier          | `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSIONS`  | pgvector embedding dimension        | `384` |
| `DJANGO_SECRET_KEY`     | Django secret key                  | auto-generated   |
| `DJANGO_SETTINGS_MODULE`| Settings module path               | `config.settings.development` |
| `CELERY_BROKER_URL`     | Redis URL for Celery broker        | `redis://redis:6379/1` |
| `DEBUG`                 | Enable Django debug mode           | `True`           |

---

## Volume Mounts

- **`./backend:/app`** — Live code reload for Django, Celery worker, and Celery beat. Changes to Python files trigger automatic restart via `runserver` or Celery's `--autoreload` flag.
- **`postgres_data`** — Named volume for PostgreSQL data persistence across container restarts.
- **`redis_data`** — Named volume for Redis persistence (AOF).
- **`static_files`** — Collected static assets for Django admin and DRF browsable API.
- **`media_files`** — User-uploaded files (resumes, profile pictures).

---

## Health Checks

Every stateful service includes a health check to ensure dependent services wait for readiness:

- **PostgreSQL**: `pg_isready` confirms the database accepts connections.
- **Redis**: `redis-cli ping` confirms the cache is responsive.
- **Django**: The `depends_on` with `condition: service_healthy` ensures the app only starts after its dependencies are confirmed healthy.

---

## Development vs Production Dockerfile

### `Dockerfile.dev` (Development)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements/dev.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# No COPY of source — mounted via volume for live reload
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### `Dockerfile` (Production)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements/prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Key differences:**

| Aspect              | Development              | Production                     |
|----------------------|--------------------------|--------------------------------|
| Source code          | Volume-mounted (live reload) | Copied into image (immutable)  |
| Dependencies         | `dev.txt` (includes debug tools) | `prod.txt` (minimal)          |
| Server               | `runserver` (auto-reload) | `gunicorn` (multi-worker)      |
| Static files         | Served by Django          | Pre-collected, served by Nginx |
| Multi-stage build    | No                        | Yes (smaller final image)      |
| Debug mode           | Enabled                   | Disabled                       |

---

## Common Commands

```bash
# Start all services
docker compose up -d

# View logs for a specific service
docker compose logs -f django

# Run Django management commands
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser

# Rebuild after dependency changes
docker compose build --no-cache django

# Stop and remove all containers
docker compose down

# Stop and remove all containers + volumes (reset DB)
docker compose down -v
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5432 already in use | Stop local PostgreSQL: `sudo systemctl stop postgresql` |
| pgvector extension not found | Ensure you're using `pgvector/pgvector:pg16`, not standard postgres image |
| Celery tasks not executing | Check broker URL matches between Django and Celery services |
| Volume permission errors | Run `docker compose exec django chown -R 1000:1000 /app/media` |

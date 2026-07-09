# Infrastructure

Sprint 1 keeps deployable infrastructure minimal:

- `docker-compose.yml` at the repository root runs PostgreSQL with pgvector, Redis, Django, Celery, and Next.js.
- Production Nginx/Gunicorn configuration is documented in `raw/deployment/` and will be added when deployment sprints begin.


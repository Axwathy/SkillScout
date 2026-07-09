---
type: architecture
title: "Environment Variables Reference"
date_created: 2025-05-30
date_updated: 2025-05-30
tags: [product/architecture, deployment]
---

# Environment Variables Reference

All variables are documented here. Three `.env.example` files exist in the repo:
- `.env.example` — root-level (used by docker-compose)
- `backend/.env.example` — Django server
- `frontend/.env.example` — Next.js (NEXT_PUBLIC_* only safe for browser)

---

## Core

| Variable | Default | Used by | Notes |
|----------|---------|---------|-------|
| `APP_ENV` | `development` | Both | `development` or `production` |
| `DEBUG` | `True` | Backend | Set `False` in production |

---

## Django

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `DJANGO_SECRET_KEY` | `unsafe-dev-secret-key` | ✅ prod | 50+ char random string |
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | ✅ | `config.settings.prod` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | ✅ prod | Comma-separated list |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | ✅ prod | Comma-separated origins |

---

## Database

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `DATABASE_URL` | SQLite fallback | ✅ prod | `postgres://user:pass@host:5432/db` |
| `POSTGRES_DB` | `recruitment_db` | Docker | Used by postgres container |
| `POSTGRES_USER` | `recruit_user` | Docker | Used by postgres container |
| `POSTGRES_PASSWORD` | `changeme` | Docker | Change in production |

---

## JWT / Auth *(Sprint 1: configured, Sprint 2: implemented)*

| Variable | Default | Notes |
|----------|---------|-------|
| `DJANGO_SECRET_KEY` | — | Used as JWT signing key (same as Django secret) |

Token lifetimes are configured in `config/settings/base.py`:
- Access token: 15 minutes
- Refresh token: 7 days (rotated on use)

See `raw/architecture/cookie-auth-strategy.md` for the full HTTP-only cookie strategy.

---

## Redis / Celery

| Variable | Default | Notes |
|----------|---------|-------|
| `REDIS_URL` | `redis://localhost:6379/0` | General Redis connection |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Task queue |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/2` | Task result storage |

---

## Frontend (public — browser-safe)

| Variable | Notes |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Django API base URL. No trailing slash. |
| `NEXT_PUBLIC_APP_URL` | Frontend base URL. Used for redirects. |
| `NEXT_PUBLIC_SUPABASE_URL` | Sprint 3+. Public Supabase project URL. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Sprint 3+. Safe public key. |

---

## Supabase *(Sprint 3+)*

| Variable | Notes |
|----------|-------|
| `SUPABASE_URL` | Project URL |
| `SUPABASE_ANON_KEY` | Safe for browser (also in NEXT_PUBLIC_*) |
| `SUPABASE_SERVICE_ROLE_KEY` | **Server-side ONLY. Never expose.** |
| `SUPABASE_STORAGE_BUCKET` | Default: `resumes` |
| `SUPABASE_CLI_VERSION` | Pin the CLI version for consistency |

---

## AI / Ollama *(Sprint 4+)*

| Variable | Default | Notes |
|----------|---------|-------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API |
| `LLM_MODEL` | `qwen2.5-coder:7b` | Primary LLM |
| `LLM_FALLBACK_MODELS` | `mistral,phi3` | Comma-separated fallbacks |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
| `EMBEDDING_DIMENSIONS` | `384` | Must match model output |

---

## Security Notes

1. **Never commit `.env` files.** Only `.env.example` files are committed.
2. `SUPABASE_SERVICE_ROLE_KEY` must only exist in server environment variables.
3. `DJANGO_SECRET_KEY` must be a cryptographically random string in production.
4. Use deployment secrets (GitHub Actions secrets, Fly.io secrets, etc.) for production values.

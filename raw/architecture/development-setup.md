---
type: architecture
title: "Development Setup Guide"
date_created: 2025-05-30
date_updated: 2025-05-30
tags: [product/architecture, deployment]
---

# Development Setup Guide

> Sprint 1 — Foundation

This guide gets a new developer from zero to running local services.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12 | Match Docker and CI |
| Node.js | 20 LTS | Use nvm or fnm |
| Docker Desktop | Latest | For local services |
| Git | Any | Trunk-based dev |
| pre-commit | Latest | `pip install pre-commit` |

---

## 1. Clone and configure

```bash
git clone <repo-url>
cd "AI recruitment SaaS"

# Copy root env file
cp .env.example .env
```

Edit `.env` and fill in `DJANGO_SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`)

---

## 2. Backend — Python environment

```powershell
# Windows PowerShell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Run migrations and start the dev server:

```powershell
# Still inside backend/ with venv active
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Backend health check: http://localhost:8000/api/v1/health/  
Django admin: http://localhost:8000/admin/

---

## 3. Frontend — Node environment

```powershell
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

---

## 4. Docker — full stack

For running all services together (PostgreSQL, Redis, Celery, Ollama):

```bash
# From project root
docker compose up --build

# Apply migrations
docker compose exec django python manage.py migrate
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django admin: http://localhost:8000/admin/
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 5. Pre-commit hooks

```bash
# Install hooks (run once after clone)
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

Hooks configured: `ruff`, `ruff-format`, `prettier`  
Hooks to add: `black`, `isort`, `eslint` (Sprint 2)

---

## 6. Running tests

```powershell
# Backend (inside backend/ with venv)
pytest

# Frontend type check
cd frontend
npm run type-check
npm run lint
```

---

## 7. Environment variable management

- Root `.env.example` — shared variables for docker-compose
- `backend/.env.example` — backend-specific variables
- `frontend/.env.example` — frontend-specific variables

See `raw/architecture/environment-variables.md` for full reference.

---

## Troubleshooting

**`psycopg2` install fails on Windows**  
Use `psycopg2-binary` (already in requirements.txt). If it still fails, install via conda or use WSL2.

**`pre-commit` hooks fail on first run**  
Run `pre-commit run --all-files` once to let hooks auto-fix formatting.

**Port conflicts**  
Default ports: 3000 (frontend), 8000 (Django), 5432 (PG), 6379 (Redis).  
Change in `docker-compose.yml` or `.env` if needed.

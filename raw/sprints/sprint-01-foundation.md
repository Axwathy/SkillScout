---
title: "Sprint 1 — Project Foundation"
sprint_number: 1
status: planned
start_date: 2026-06-02
end_date: 2026-06-13
team_velocity: 0
story_points_planned: 34
story_points_completed: 0
tags:
  - sprint
  - foundation
  - infrastructure
---

# Sprint 1 — Project Foundation

## 🎯 Sprint Goal

> **Primary Objective:** Set up the project infrastructure, monorepo structure, development environment, and CI/CD basics so the team can begin feature development with a solid, reproducible foundation.
>
> **Success Criteria:** All team members can clone the repo, run `docker-compose up`, and access both the Django API health check and the Next.js dev server locally.

---

## 📋 Planned Features

- [ ] Django project initialization with production-ready settings structure
- [ ] Next.js project initialization with TypeScript and TailwindCSS
- [ ] Supabase project provisioning and local development setup
- [ ] Docker Compose orchestration for all services
- [ ] Basic CI pipeline with linting and test scaffolds

---

## ⚙️ Backend Tasks

- [ ] Scaffold Django project with `startproject` and custom folder layout
- [ ] Configure split settings module (`base.py`, `dev.py`, `prod.py`) per [[tech-stack|Tech Stack]]
- [ ] Generate `requirements.txt` with pinned versions (Django, DRF, psycopg2, celery, redis)
- [ ] Create custom User model extending `AbstractBaseUser` for future auth flexibility
- [ ] Implement `/api/v1/health/` endpoint returning service status and DB connectivity
- [ ] Configure Django CORS headers for local Next.js dev server
- [ ] Set up basic Django admin with branding customization
- [ ] Write initial unit test for health check endpoint using `pytest-django`

---

## 🖥️ Frontend Tasks

- [ ] Initialize Next.js 14+ project with App Router and TypeScript (`--typescript`)
- [ ] Install and configure TailwindCSS with custom design tokens (colors, fonts, spacing)
- [ ] Create folder structure: `app/`, `components/`, `lib/`, `hooks/`, `types/`, `styles/`
- [ ] Build root layout with metadata, font loading (Inter via `next/font`), and global styles
- [ ] Create placeholder landing page with navigation skeleton
- [ ] Configure path aliases (`@/components`, `@/lib`) in `tsconfig.json`
- [ ] Set up ESLint + Prettier with shared config for consistent code style

---

## 🚀 DevOps Tasks

- [ ] Write `docker-compose.yml` with services: Django, PostgreSQL 15, Redis 7
- [ ] Create Dockerfiles for Django (multi-stage) and Next.js (dev mode)
- [ ] Set up `.env.example` with all required environment variables documented
- [ ] Create GitHub Actions workflow: lint (ruff + eslint), type-check, test scaffold
- [ ] Configure `pre-commit` hooks for formatting and linting
- [ ] Set up Supabase project and configure local development with `supabase init`
- [ ] Document local setup instructions in `README.md`

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Supabase CLI version compatibility | Medium | Pin CLI version in docs | 🟡 Monitoring |
| Docker resource usage on dev machines | Low | Document min requirements | 🟢 Resolved |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Placeholder test suite — needs real test coverage in subsequent sprints
- [ ] TailwindCSS config may need refinement once design system is finalized

---

## 📝 Sprint Notes

- **Dependencies:** This sprint blocks all subsequent sprints — must be completed cleanly
- **References:** [[system-overview|System Overview]], [[tech-stack|Tech Stack]], [[project-structure|Project Structure]]
- **Next Sprint:** [[sprint-02-auth]] — Authentication System

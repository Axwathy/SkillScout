---
type: deployment
title: "CI/CD Pipeline"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, deployment]
---

# CI/CD Pipeline

This document defines the continuous integration and continuous deployment pipeline for the AI Recruitment SaaS platform, built on **GitHub Actions**.

See also: [[deployment-architecture|Deployment Architecture]]

---

## Pipeline Stages

The pipeline follows a linear progression with stage gates:

```
Lint → Test → Build → Deploy
```

| Stage   | Trigger                        | Duration | Failure Behavior           |
|---------|--------------------------------|----------|----------------------------|
| Lint    | Every push, every PR           | ~1 min   | Blocks all downstream      |
| Test    | After lint passes              | ~3-5 min | Blocks build + deploy      |
| Build   | After tests pass on `main`/`develop` | ~2 min | Blocks deploy              |
| Deploy  | Auto (staging), Manual (prod)  | ~3 min   | Rollback on failure        |

---

## Branch Strategy

| Branch           | Environment | Deploy Mode | Protection Rules                     |
|------------------|-------------|-------------|--------------------------------------|
| `main`           | Production  | Manual approval | Require PR, 1+ review, passing CI |
| `develop`        | Staging     | Auto on merge   | Require PR, passing CI             |
| `feature/*`      | Preview     | PR preview only  | No direct push to `develop`/`main` |
| `hotfix/*`       | Production  | Manual approval  | Can PR directly to `main`          |

### Workflow

1. Developer creates `feature/xyz` branch from `develop`
2. Opens PR → triggers lint + test
3. After review + merge to `develop` → auto-deploy to staging
4. After validation, PR from `develop` to `main` → manual deploy to production

---

## GitHub Actions Workflow

**GitHub repo** -> https://github.com/Paaarthiv/AI-recruitment-SaaS.git

### `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Python linters
        run: pip install ruff

      - name: Run Ruff (Python)
        run: ruff check backend/ --output-format=github

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install frontend dependencies
        run: cd frontend && npm ci

      - name: Run ESLint (JavaScript/TypeScript)
        run: cd frontend && npx eslint . --max-warnings=0

      - name: Run TypeScript type check
        run: cd frontend && npx tsc --noEmit

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test_user"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements/test.txt

      - name: Run pytest
        env:
          DATABASE_URL: postgres://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest --cov=. --cov-report=xml --cov-fail-under=80

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install frontend dependencies
        run: cd frontend && npm ci

      - name: Run Jest tests
        run: cd frontend && npm test -- --coverage --watchAll=false

  build:
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Railway (Staging)
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN_STAGING }}
          service: backend-staging

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com
    steps:
      - name: Deploy to Railway (Production)
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN_PRODUCTION }}
          service: backend-production
```

---

## Secrets Management

All secrets are stored in **GitHub Repository Secrets** and scoped by environment.

| Secret                     | Environment | Description                       |
|----------------------------|-------------|-----------------------------------|
| `RAILWAY_TOKEN_STAGING`    | Staging     | Railway deploy token for staging  |
| `RAILWAY_TOKEN_PRODUCTION` | Production  | Railway deploy token for prod     |
| `DATABASE_URL`             | Both        | Production/staging DB connection  |
| `DJANGO_SECRET_KEY`        | Both        | Django secret key                 |
| `SUPABASE_SERVICE_KEY`     | Both        | Server-side Supabase service key  |
| `VERCEL_TOKEN`             | Both        | Vercel deploy token for frontend  |
| `CODECOV_TOKEN`            | CI          | Code coverage reporting           |

### Environment-Specific Configs

- **Staging** (`develop`): Relaxed rate limits, staging model endpoint, seeded demo data
- **Production** (`main`): Strict rate limits, production model endpoint, manual deploy gate with required approval from at least one maintainer

---

## PR Preview Deployments

For every pull request:
- **Frontend**: Vercel automatically creates a preview deployment (see [[vercel-deployment|Vercel Deployment]])
- **Backend**: A temporary Railway environment can be spun up using Railway's PR environment feature

---

## Quality Gates

| Gate                  | Threshold     | Enforced By        |
|-----------------------|---------------|--------------------|
| Python lint (Ruff)    | 0 errors      | CI lint stage      |
| TypeScript lint       | 0 warnings    | CI lint stage      |
| TypeScript types      | 0 errors      | CI lint stage      |
| Backend test coverage | ≥ 80%         | pytest-cov         |
| Frontend tests        | All passing   | Jest               |
| PR review             | 1+ approval   | Branch protection  |

---

## Monitoring & Notifications

- **GitHub Actions** dashboard for pipeline status
- **Slack integration** via GitHub App for build failure notifications
- **Codecov** bot comments on PRs with coverage diff
- **Vercel** bot comments on PRs with preview URL

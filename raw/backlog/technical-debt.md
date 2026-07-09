---
type: backlog
title: "Technical Debt Tracker"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, engineering]
---

# Technical Debt Tracker

This document tracks known technical debt in the AI Recruitment SaaS platform. Items are categorized by type, assessed for impact and remediation effort, and assigned to sprints for resolution. The goal is to keep technical debt visible and manageable — not to eliminate it entirely (some debt is strategic).

See also: [[sprint-01-foundation|Sprint 1 — Project Foundation]], [[sprint-03-job-management|Sprint 3 — Job Management]], [[mvp-features|MVP Feature List]]

---

## Debt Categories

| Category           | Description                                                      |
|--------------------|------------------------------------------------------------------|
| **Architecture**   | Structural decisions that limit scalability or maintainability    |
| **Code Quality**   | Code that works but is hard to read, test, or maintain           |
| **Testing**        | Gaps in test coverage or test infrastructure                     |
| **Documentation**  | Missing or outdated documentation                                |
| **Infrastructure** | DevOps, deployment, or tooling gaps                              |
| **Security**       | Known security improvements that need addressing                 |

---

## Active Debt Items

### Architecture Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| AD-001 | **SQLite in local development** — Initial Django project uses SQLite for local dev. This hides PostgreSQL-specific issues (pgvector queries, JSON fields, full-text search) until staging. Developers may write code that works locally but fails in production. | High | S | [[sprint-01-foundation|Sprint 1 — Project Foundation]] | 🟡 Planned |
| AD-002 | **Monolithic Django app structure** — All features currently live in a single Django app (`core`). As the codebase grows, this will make it harder to reason about boundaries, run targeted tests, and eventually extract microservices. | Medium | M | Sprint 3 | 🔴 Open |
| AD-003 | **API versioning drift** — Earlier docs mixed unversioned API routes with `/api/v1/...`. Documentation has been normalized to `/api/v1/`; implementation should enforce the same prefix. | Medium | S | [[api-design|API Design]] | ✅ Resolved in docs |
| AD-004 | **Synchronous AI calls in request cycle** — Resume parsing and scoring are currently called synchronously during the HTTP request. For large resumes or slow API responses, this causes timeouts. Must be moved to Celery tasks. | High | M | [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]] | 🟡 Planned |

### Code Quality Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| CQ-001 | **No consistent error handling** — API views use ad-hoc try/except blocks with inconsistent error response formats. Need a centralized exception handler with standardized error responses (RFC 7807 Problem Details). | Medium | S | Sprint 4 | 🔴 Open |
| CQ-002 | **Magic numbers in scoring logic** — Candidate scoring weights and thresholds are hardcoded in the scoring service. Should be moved to configuration (database or environment variables) for easy tuning. | Medium | S | Sprint 3 | 🔴 Open |
| CQ-003 | **Frontend components not extracted into design system** — UI components (buttons, cards, modals, form inputs) are defined inline in page components. Need a shared component library with consistent styling and props. | Medium | M | Sprint 4 | 🔴 Open |
| CQ-004 | **No type safety on API responses** — Frontend fetches API data without TypeScript type validation. Should use Zod schemas or generated types from OpenAPI spec to catch contract mismatches at compile time. | Medium | M | Sprint 5 | 🔴 Open |

### Testing Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| TD-001 | **No test coverage baseline** — pytest is installed but no tests exist yet. Need initial test setup with fixtures, factories (factory_boy), and CI enforcement of coverage thresholds. | High | M | [[sprint-03-job-management|Sprint 3 — Job Management]] | 🟡 Planned |
| TD-002 | **No integration tests for AI pipeline** — Local model calls are not mocked or tested. Need fixtures with sample model responses and integration tests that validate the full parsing/scoring flow. | High | M | [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]] | 🔴 Open |
| TD-003 | **No frontend testing** — No Jest/React Testing Library setup. Need unit tests for utility functions and component tests for critical UI flows (login, pipeline board, candidate detail). | High | M | Sprint 5 | 🔴 Open |
| TD-004 | **No end-to-end tests** — No Playwright or Cypress setup. Need E2E tests for critical user journeys: sign up → create job → upload resume → view scored candidate → move through pipeline. | Medium | L | Sprint 6 | 🔴 Open |

### Documentation Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| DD-001 | **No API documentation** — REST API has no OpenAPI/Swagger spec. Need drf-spectacular or similar to auto-generate interactive API docs. | Medium | S | Sprint 4 | 🔴 Open |
| DD-002 | **No onboarding guide** — New developers have no setup guide beyond "read the README." Need a comprehensive onboarding document covering local setup, architecture overview, coding conventions, and PR process. | Medium | S | Sprint 2 | 🔴 Open |
| DD-003 | **No architecture decision records** — Past decisions lack documentation. Need ADR template and retrospective ADRs for decisions already made (database choice, framework selection, AI provider). | Low | S | Ongoing | 🟡 In Progress |

### Infrastructure Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| ID-001 | **No staging environment** — All testing happens in local development. Need a staging environment that mirrors production for QA and stakeholder demos. | High | M | Sprint 2 | 🔴 Open |
| ID-002 | **No database migration strategy** — No process for handling breaking schema changes in production. Need a migration checklist: backward-compatible migrations, deploy-then-migrate, data backfill scripts. | High | S | Sprint 3 | 🔴 Open |
| ID-003 | **No log aggregation** — Application logs go to stdout only. Need structured logging (JSON format) with aggregation via Railway logs, or a service like Datadog/Sentry for searchability and alerting. | Medium | M | Sprint 5 | 🔴 Open |
| ID-004 | **No secrets rotation** — API keys and database passwords have no rotation schedule. Need a process for periodic rotation and audit trail. | Medium | S | Sprint 6 | 🔴 Open |

### Security Debt

| ID   | Description | Impact | Effort | Sprint | Status |
|------|-------------|--------|--------|--------|--------|
| SD-001 | **No rate limiting** — API endpoints have no rate limiting. Vulnerable to brute-force attacks on auth endpoints and abuse of AI-powered features (which have per-call cost). | High | S | Sprint 3 | 🔴 Open |
| SD-002 | **No CORS configuration** — Django CORS headers are set to allow all origins in development. Must be restricted to specific frontend domains before staging/production deployment. | High | S | Sprint 2 | 🟡 Planned |
| SD-003 | **No Content Security Policy** — Frontend pages have no CSP headers. Need CSP configuration to prevent XSS attacks and unauthorized script injection. | Medium | S | Sprint 5 | 🔴 Open |

---

## Debt Management Process

### Adding New Debt

When you incur intentional technical debt (to meet a deadline, simplify an approach, etc.):

1. Add an entry to this document with a unique ID
2. Set the impact and effort level
3. Assign a target sprint for remediation
4. Leave a `# TODO(debt): TD-XXX` comment in the code

### Reviewing Debt

- **Sprint planning**: Review this document at the start of each sprint
- **Debt budget**: Allocate 20% of each sprint to debt remediation
- **Escalation**: Any "High" impact item open for more than 2 sprints requires a team discussion

### Debt Metrics

| Metric                        | Current | Target |
|-------------------------------|---------|--------|
| Total open items              | 19      | < 10   |
| High-impact open items        | 8       | 0      |
| Average age of open items     | 0 sprints | < 2 sprints |
| Items resolved per sprint     | 0       | 3-5    |

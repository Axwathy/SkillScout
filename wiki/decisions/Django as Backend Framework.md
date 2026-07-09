---
type: decision
title: "Django as Backend Framework"
status: decided
date_created: 2026-05-22
date_decided: 2025-05-22
superseded_by: ""
tags: [product/architecture, backend/django]
---

# Django as Backend Framework

## Context

The product needs a backend that can support multi-tenant recruiting workflows, complex relational models, secure authentication, background AI processing, and a REST API for a Next.js frontend.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| Django + DRF | Mature ORM, admin, security defaults, strong ecosystem | Less async-native than FastAPI |
| FastAPI | Async-first, strong API ergonomics | Less batteries-included for admin, auth, and large app structure |
| Node.js / Express | Same language as frontend, async I/O | Less opinionated, no built-in admin or ORM |
| Go | Performance, simple deployment | Slower CRUD-heavy development |

## Decision

Use Django 5.x with Django REST Framework as the primary backend framework.

## Implications

- Product development can move quickly with Django ORM, admin, DRF serializers, and established security defaults.
- Background AI workloads should run outside request handlers via Celery.
- App boundaries need to stay clear to avoid an unstructured monolith.

## Review Triggers

- API latency becomes dominated by Python application overhead rather than database or AI calls.
- AI services need independent scaling that Django/Celery cannot satisfy cleanly.
- Enterprise integration requirements demand a separate service boundary.

## Source References

- `raw/decisions/ADR-001-django.md`

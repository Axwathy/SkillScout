---
type: decision
title: "ADR-001 — Django as Backend Framework"
status: decided
date_created: 2025-05-22
date_decided: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, product/strategy]
---

## Context

We are building a multi-tenant recruitment SaaS platform with the following technical requirements:

- Complex relational data models (candidates, jobs, organizations, pipelines, evaluations)
- AI/ML integrations for resume parsing, candidate scoring, and interview generation
- Real-time features (notifications, pipeline updates)
- Background task processing (bulk resume parsing, AI inference, email dispatch)
- Role-based access control with multi-tenancy isolation
- RESTful API consumed by a modern frontend SPA

The backend framework must support rapid iteration during early-stage development while providing a clear path to production scale.

## Decision

**Django 5.x with Django REST Framework (DRF)** as the primary backend framework.

## Rationale

| Criterion | Django | FastAPI | Node.js/Express | Go (Gin) |
|---|---|---|---|---|
| ORM maturity | ★★★★★ | ★★★ (SQLAlchemy) | ★★★ (Prisma/Sequelize) | ★★ (GORM) |
| Ecosystem breadth | ★★★★★ | ★★★ | ★★★★ | ★★★ |
| Admin interface | Built-in | None | None | None |
| Security defaults | ★★★★★ | ★★★★ | ★★★ | ★★★ |
| Talent pool | ★★★★★ | ★★★ | ★★★★★ | ★★★ |
| Dev velocity | ★★★★★ | ★★★★ | ★★★ | ★★ |
| Async support | ★★★ (ASGI) | ★★★★★ | ★★★★★ | ★★★★★ |

### Key reasons for choosing Django:

1. **Mature ORM** — Django's ORM handles complex queries (multi-table joins, aggregations, subqueries) that are central to recruitment workflows. Candidate search, pipeline analytics, and reporting all depend on sophisticated query generation.
2. **Ecosystem depth** — Celery for task queues, Django Channels for WebSockets, django-filter for query filtering, drf-spectacular for OpenAPI docs. These are battle-tested and well-documented.
3. **Built-in admin panel** — Immediate operational tooling for customer support, data inspection, and internal debugging without building custom admin UIs.
4. **Security by default** — CSRF protection, SQL injection prevention, XSS escaping, clickjacking protection, and password hashing are all enabled out of the box.
5. **Battle-tested at scale** — Instagram, Pinterest, Disqus, and Mozilla all run Django at massive scale, validating our architecture choices.

## Alternatives Considered

### FastAPI
- **Pros**: Native async, automatic OpenAPI docs, Pydantic validation, excellent performance.
- **Cons**: SQLAlchemy is powerful but less opinionated than Django ORM. Smaller ecosystem for auth, admin, and background tasks. Less mature for large monolithic applications.
- **Verdict**: Better for microservices or API-only projects; Django's batteries-included approach better suits our full-stack needs.

### Node.js / Express
- **Pros**: JavaScript everywhere (frontend + backend), massive npm ecosystem, excellent async I/O.
- **Cons**: Callback/promise complexity for heavy business logic, no built-in ORM or admin, TypeScript adds build complexity, less opinionated structure leads to inconsistency.
- **Verdict**: Good for real-time apps but adds cognitive overhead for complex domain logic.

### Go (Gin/Echo)
- **Pros**: Exceptional performance, compiled binary deployment, goroutines for concurrency.
- **Cons**: Verbose code, immature ORMs, no admin panel, slower development velocity for CRUD-heavy applications. Static typing adds boilerplate for rapid prototyping.
- **Verdict**: Better suited for performance-critical microservices, not full application development at our stage.

## Consequences

### Positive
- Rapid development with Django's conventions and DRF serializers
- Powerful ORM for complex recruitment data queries
- Built-in admin panel for operations and debugging
- Strong security posture out of the box
- Large community and extensive documentation

### Negative
- **GIL limitation** — Python's Global Interpreter Lock limits true CPU-bound parallelism. Mitigated by offloading AI inference to Celery workers and using async views for I/O-bound operations.
- **Async maturity** — Django's async support (ASGI) is less mature than FastAPI or Node.js. Mitigated by using Django Channels for WebSocket features and sync views for most endpoints.
- **Monolith tendency** — Django encourages monolithic architecture. Mitigated by strict app separation and potential future extraction of AI services into standalone microservices.

## Implementation Notes

```python
# Core dependencies
django>=5.0,<6.0
djangorestframework>=3.15
django-cors-headers>=4.3
django-filter>=24.0
celery>=5.3
django-channels>=4.0
drf-spectacular>=0.27
```

## Related Documents

- [[ADR-002-postgresql|ADR-002 — PostgreSQL with pgvector]]
- [[ADR-004-supabase|ADR-004 — Supabase as Data Platform]]
- [[backend-architecture|Backend Architecture]]
- [[authentication-flow|Authentication Flow]]

---
type: decision
title: "Supabase as Data Platform"
status: decided
date_created: 2026-05-22
date_decided: 2025-05-22
superseded_by: ""
tags: [product/architecture, database/postgresql, storage/supabase]
---

# Supabase as Data Platform

## Context

The platform needs managed PostgreSQL with pgvector, object storage for resumes, database-level tenant isolation, and a path to realtime updates without heavy infrastructure work.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| Supabase | Managed Postgres, pgvector, storage, realtime | Vendor-specific storage and realtime APIs |
| AWS RDS + S3 | Mature and flexible | More operational overhead |
| Neon | Serverless Postgres and branching | No built-in object storage |
| Self-hosted Postgres | Maximum control | Too much ops burden for current stage |

## Decision

Use Supabase for managed PostgreSQL, pgvector, and private object storage while keeping application auth and business logic in Django.

## Implications

- Django remains the policy enforcement layer for custom JWT auth.
- Database RLS must use explicit org context from Django rather than assuming Supabase Auth sessions.
- Resume storage access should flow through backend-validated signed URLs.

## Review Triggers

- Supabase connection limits or storage policies constrain growth.
- Enterprise buyers require alternative hosting.
- Realtime or RLS integration becomes too coupled to Supabase APIs.

## Source References

- `raw/decisions/ADR-004-supabase.md`

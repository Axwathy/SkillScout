---
type: decision
title: "Multi-Tenant Architecture"
status: decided
date_created: 2026-05-30
date_decided: 2026-05-30
superseded_by: ""
tags: [product/architecture, product/strategy, market/segment, security/tenancy]
---

# Multi-Tenant Architecture

## Context

The AI Recruitment SaaS platform must support multiple hiring organizations in one product while preventing cross-company data access. This becomes a core architecture concern as [[Authentication Strategy]] and recruiter verification introduce organization-scoped users.

## Options Considered

### Schema-Based Tenancy

**Pros:** Strong database-level isolation and clearer tenant boundaries.

**Cons:** More complex migrations, more operational overhead, and a poor fit for the current MVP stage.

### Row-Based Tenancy With Organization Foreign Keys

**Pros:** Simple migrations, works naturally with Django ORM and DRF, aligns with [[Supabase as Data Platform]], and can later be reinforced with PostgreSQL Row Level Security.

**Cons:** Requires disciplined query scoping. Missing organization filters can create data leakage risk.

## Decision

Use row-based tenancy with `Organization` as the tenant boundary.

Every tenant-owned model from Sprint 3 onward should carry an `organization` foreign key. API serializers should derive organization ownership from the authenticated user rather than accepting tenant identifiers from request payloads.

## Implications

- Tenant-owned querysets need organization scoping by default.
- Admin-only endpoints may intentionally bypass tenant scoping, but that bypass must be explicit.
- Tests should cover cross-tenant isolation once tenant-owned models exist.
- Supabase/PostgreSQL Row Level Security remains available later as defense in depth.

## Review Triggers

- A tenant grows large enough that shared-table performance becomes a concern.
- Regulatory or customer requirements demand stronger physical or schema-level isolation.
- Repeated bugs show that application-level tenant filtering is not reliable enough.


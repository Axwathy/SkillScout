---
type: decision
title: "ADR-006 — Multi-Tenant Architecture via Organization-Based Tenancy"
status: decided
date_created: 2026-05-30
date_decided: 2026-05-30
tags: [product/architecture, product/strategy, market/segment]
---

# ADR-006 — Multi-Tenant Architecture via Organization-Based Tenancy

## Context

The AI Recruitment SaaS platform serves multiple hiring companies simultaneously. From Sprint 2 onwards, data isolation between companies is a hard requirement. A recruiter at Company A must never access, see, or accidentally interact with data belonging to Company B.

Two common multi-tenant approaches:
- **Schema-based tenancy**: Separate PostgreSQL schema per tenant. Strong isolation, complex migrations.
- **Row-based tenancy**: Single schema, every row carries a tenant FK. Simpler, requires discipline.

## Options Considered

### Option A — Schema-based tenancy (Supabase Row Level Security policies per schema)
**Pros:** Strongest isolation, database-enforced boundaries, no risk of cross-tenant data leaks in queries.  
**Cons:** Complex migrations across all tenants, complicates Supabase usage, over-engineered for our scale in 2025.

### Option B — Row-based tenancy with `organization` FK (chosen)
**Pros:** Simple migrations, works with standard Django ORM and DRF querysets, Supabase Row Level Security can still be added later, proven approach at scale (GitHub, Linear, Notion all use this pattern).  
**Cons:** Requires developer discipline — every queryset on tenant-owned models MUST filter by `organization`. Bugs in queryset logic could theoretically leak cross-tenant data.

**Mitigation:** Custom queryset mixin (`OrganizationScopedQuerySet`) that automatically filters by the requesting user's organization. Applied to every tenant-owned model manager from Sprint 3+.

## Decision

Use **row-based tenancy** with `Organization` as the tenant boundary.

- Every data model from Sprint 3+ carries `organization = ForeignKey(Organization, on_delete=PROTECT)`
- Serializers enforce tenant scope by injecting `organization` from `request.user`
- Views use `OrganizationScopedQuerySet` mixin — never raw `.all()` on tenant models
- Admin endpoints (staff-only) may bypass tenant filter with explicit intent

## Implications

1. **Sprint 3+ models** (Job, Application, Pipeline) MUST include `organization` FK — no exceptions
2. **Serializer layer** — `organization` is always set from `request.user.recruiter_profile.organization`, never from request payload (prevents tenant spoofing)
3. **Test discipline** — every model test must assert cross-tenant queries return 0 results
4. **Future Supabase RLS** — Row Level Security policies can be added later as a defense-in-depth layer without schema changes

## Review Triggers

- If a single organization consistently exceeds 10,000 active jobs or candidates, re-evaluate schema-based tenancy
- If regulatory requirements (GDPR data isolation) demand stronger guarantees, escalate to schema-based

---
type: decision
title: "ADR-004 — Supabase as Data Platform"
status: decided
date_created: 2025-05-22
date_decided: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, product/strategy]
---

## Context

The recruitment SaaS requires managed infrastructure for:

- **PostgreSQL hosting** with pgvector support (see [[ADR-002-postgresql|ADR-002 — PostgreSQL with pgvector]])
- **File storage** for resume uploads (PDF, DOCX) with per-organization isolation
- **Authentication** primitives (though we implement our own JWT strategy — see [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]])
- **Realtime** capabilities for live pipeline updates and notifications
- **Row-Level Security** for database-level multi-tenancy enforcement

Self-hosting these services requires significant DevOps investment. We need a managed platform that bundles these capabilities with minimal operational overhead.

## Decision

**Supabase** as the managed data platform layer, providing PostgreSQL hosting, object storage, and realtime subscriptions.

## Rationale

### Service Comparison

| Capability | Supabase | AWS RDS + S3 | PlanetScale | Neon | Self-Hosted |
|---|---|---|---|---|---|
| Managed PostgreSQL | ✅ | ✅ | ✗ (MySQL) | ✅ | Manual |
| pgvector support | ✅ | ✅ | ✗ | ✅ | Manual |
| Object storage | ✅ (built-in) | ✅ (S3) | ✗ | ✗ | Manual |
| Row-Level Security | ✅ (first-class) | ✅ | ✗ | ✅ | Manual |
| Realtime subscriptions | ✅ (built-in) | ✗ (need AppSync) | ✗ | ✗ | Manual |
| Free tier | ✅ (generous) | ✅ (limited) | ✅ | ✅ | N/A |
| Operational burden | Low | High | Low | Low | Very High |
| Vendor lock-in risk | Medium | Low | High | Medium | None |

### Key Advantages

1. **Integrated PostgreSQL + pgvector** — Supabase runs PostgreSQL 15+ with pgvector pre-installed. No extension management or custom builds needed.

2. **Built-in object storage** — Resume files are stored in a private Supabase Storage bucket. Django validates the requesting user's organization and generates short-lived signed URLs. Because product authentication uses Django JWTs rather than Supabase Auth, direct browser access to storage objects should not rely on `auth.jwt()`.

   ```sql
   -- Bucket remains private. Django uses the service role key server-side
   -- after validating organization membership in application code.
   -- Do not expose the service role key to the browser.
   ```

3. **Row-Level Security** — Database-level tenant isolation that's enforced even if application logic has bugs:

   ```sql
   -- RLS policy: Users can only see candidates in their organization
   ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "tenant_isolation" ON candidates
   FOR ALL USING (
     organization_id = NULLIF(current_setting('app.current_org_id', true), '')::uuid
   );
   ```

4. **Realtime subscriptions** — PostgreSQL changes broadcast via WebSockets for live pipeline updates:

   ```javascript
   // Frontend: Listen for candidate status changes
   supabase
     .channel('pipeline-updates')
     .on('postgres_changes', {
       event: 'UPDATE',
       schema: 'public',
       table: 'applications',
       filter: `organization_id=eq.${orgId}`
     }, handlePipelineUpdate)
     .subscribe();
   ```

5. **Developer experience** — Dashboard for database inspection, SQL editor, storage browser, and log viewer. Reduces need for custom admin tooling during development.

## Alternatives Considered

### AWS RDS + S3
- **Pros**: Maximum flexibility, no vendor lock-in, mature ecosystem, fine-grained IAM.
- **Cons**: Significant operational burden (VPC setup, security groups, backup config, monitoring). S3 requires separate SDK integration. No built-in realtime. Higher cost for small-to-medium scale.
- **Verdict**: Overkill for our stage. Consider for future migration if Supabase limitations emerge.

### PlanetScale
- **Pros**: Excellent DX, branching workflows, zero-downtime schema changes.
- **Cons**: MySQL only — no pgvector support, no RLS, different ORM patterns. Eliminates our vector search strategy.
- **Verdict**: Incompatible with our pgvector requirement.

### Neon
- **Pros**: Serverless PostgreSQL, branching, scale-to-zero, pgvector support.
- **Cons**: Newer platform with less ecosystem maturity. No built-in object storage or realtime. Fewer integrations and community resources.
- **Verdict**: Promising but less feature-complete than Supabase for our needs.

### Self-Hosted PostgreSQL
- **Pros**: Full control, no vendor lock-in, no usage-based pricing.
- **Cons**: Requires DevOps expertise for backups, monitoring, security patches, scaling, and HA configuration. Significant time investment away from product development.
- **Verdict**: Not viable at our current team size and stage.

## Consequences

### Positive
- **Reduced operational burden** — No server management, automatic backups, managed upgrades
- **Integrated services** — Storage, realtime, and database in one platform
- **RLS for multi-tenancy** — Database-level security independent of application code
- **Fast development** — Dashboard, SQL editor, and client libraries accelerate development
- **Cost-effective** — Free tier supports development; Pro tier ($25/mo) covers early production

### Negative
- **Vendor lock-in** — Supabase-specific RLS patterns and storage APIs. Mitigated by keeping business logic in Django (not Supabase Edge Functions) and using standard PostgreSQL SQL where possible.
- **Connection limits** — Free tier has connection limits. Mitigated by connection pooling (PgBouncer, built into Supabase) and Django's `CONN_MAX_AGE` setting.
- **Migration path** — Moving off Supabase requires migrating storage buckets, RLS policies, and realtime subscriptions. Mitigated by documenting Supabase-specific patterns and abstracting storage behind a service layer.

## Related Documents

- [[ADR-002-postgresql|ADR-002 — PostgreSQL with pgvector]]
- [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]]
- [[backend-architecture|Backend Architecture]]
- [[upload-security|File Upload Security]]

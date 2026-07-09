---
type: decision
title: "Authentication Strategy"
status: decided
date_created: 2026-05-22
date_decided: 2025-05-22
superseded_by: ""
tags: [product/architecture, security/auth, security/jwt]
---

# Authentication Strategy

## Context

The product handles sensitive candidate data in a browser-based SaaS app. Authentication must support multi-tenancy, role-based permissions, horizontal backend scaling, and protection against common browser token risks.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| JWT in HttpOnly cookies | XSS-resistant token storage, stateless verification | Requires CSRF protection and careful cookie config |
| Server sessions | Simple revocation | Shared session store required |
| localStorage JWT | Simple API calls | Token theft risk under XSS |
| Supabase Auth | Managed auth | Less control over custom Django RBAC |
| Auth0 / Clerk | Enterprise auth features | Cost and external dependency |

## Decision

Use JWT access and refresh tokens in HttpOnly cookies with CSRF protection via a readable CSRF token and matching request header.

## Implications

- Frontend requests must include credentials and CSRF headers.
- Refresh token rotation and blacklist handling must be implemented.
- Cookie domain and SameSite settings need environment-specific testing.

## Review Triggers

- Enterprise SSO becomes a sales requirement.
- Token revocation requirements outgrow the current blacklist approach.
- Cross-domain deployment introduces cookie complexity that hurts reliability.

## Source References

- `raw/decisions/ADR-005-auth-strategy.md`

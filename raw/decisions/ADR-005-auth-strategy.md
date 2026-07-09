---
type: decision
title: "ADR-005 — Authentication Strategy"
status: decided
date_created: 2025-05-22
date_decided: 2025-05-22
date_updated: 2026-05-22
tags: [security, product/architecture]
---

## Context

The recruitment SaaS requires secure authentication for a multi-tenant platform with the following requirements:

- **Multi-tenancy** — Users belong to organizations; data must be isolated per-tenant
- **Role-based access** — Roles include Admin, Hiring Manager, Recruiter, and Viewer with distinct permission sets
- **SPA frontend** — React/Next.js frontend communicating via REST API
- **Stateless scaling** — Backend must scale horizontally without shared session state
- **Security posture** — Enterprise-grade security for handling sensitive candidate PII (resumes, contact information, evaluation notes)

## Decision

**JWT tokens stored in HttpOnly cookies** with **CSRF protection** via the double-submit cookie pattern.

## Authentication Flow

```
┌─────────┐     POST /api/v1/auth/login     ┌─────────────┐
│         │ ──────────────────────────► │             │
│         │     (email, password)        │             │
│         │                              │   Django    │
│ Browser │ ◄────────────────────────── │   Backend   │
│  (SPA)  │   Set-Cookie: access_token   │             │
│         │   Set-Cookie: refresh_token  │             │
│         │   Set-Cookie: csrf_token     │             │
│         │                              │             │
│         │     GET /api/v1/candidates       │             │
│         │ ──────────────────────────► │             │
│         │   Cookie: access_token       │             │
│         │   X-CSRFToken: <token>       │             │
└─────────┘                              └─────────────┘
```

## Token Architecture

| Property | Access Token | Refresh Token | CSRF Token |
|---|---|---|---|
| Lifetime | 15 minutes | 7 days | Matches access token |
| Storage | HttpOnly cookie | HttpOnly cookie | Regular cookie (JS-readable) |
| Purpose | API authentication | Access token renewal | CSRF protection |
| Rotation | On refresh | On every use (rotate) | On refresh |
| Revocation | Blacklist on logout | Blacklist on logout | N/A |

### JWT Payload Structure

```json
{
  "sub": "usr_a1b2c3d4",
  "org_id": "org_x7y8z9",
  "role": "hiring_manager",
  "permissions": ["candidates:read", "candidates:write", "jobs:read", "jobs:write"],
  "iat": 1716422400,
  "exp": 1716423300,
  "jti": "tok_unique_id"
}
```

## Rationale

### Why HttpOnly Cookies?

1. **XSS protection** — JavaScript cannot access HttpOnly cookies, preventing token theft via cross-site scripting attacks. This is critical for a platform handling candidate PII.
2. **Automatic transmission** — Browser automatically includes cookies in requests, simplifying frontend code compared to manual `Authorization` header management.
3. **Refresh token security** — Refresh tokens (long-lived) are especially dangerous if exposed. HttpOnly cookies are the most secure browser-side storage mechanism.

### Why CSRF Protection?

Cookie-based authentication is vulnerable to cross-site request forgery. The double-submit cookie pattern mitigates this:

1. Server sets a CSRF token in a **readable** cookie (not HttpOnly)
2. Frontend reads the CSRF cookie and includes it in a custom header (`X-CSRFToken`)
3. Server validates that the header value matches the cookie value
4. Attackers cannot read cross-origin cookies, so they cannot forge the header

### Why JWT (not sessions)?

1. **Stateless verification** — JWT can be verified without a database lookup, enabling horizontal scaling
2. **Embedded claims** — User role and org_id in the token reduce per-request database queries
3. **Cross-service compatibility** — JWT is a standard that works across Django, Celery, and future microservices

## Alternatives Considered

### Session-Based Authentication
- **Pros**: Simpler implementation, easy revocation, smaller cookie size.
- **Cons**: Requires server-side session store (Redis/DB), harder to scale horizontally, session fixation risks.
- **Verdict**: Viable but adds infrastructure dependency and scaling complexity.

### localStorage JWT (Authorization Header)
- **Pros**: Simple CORS, no CSRF concerns, straightforward implementation.
- **Cons**: **Critically vulnerable to XSS** — any script injection can steal tokens. Unacceptable for a platform handling sensitive PII.
- **Verdict**: Rejected due to security risk.

### Supabase Auth
- **Pros**: Built-in, managed, handles OAuth providers.
- **Cons**: Less control over token claims, harder to integrate with Django's permission system, Supabase-specific patterns.
- **Verdict**: Less suitable for custom RBAC requirements.

### Auth0 / Clerk
- **Pros**: Enterprise features (MFA, SSO), managed service, social login.
- **Cons**: Cost ($23+/mo per 1K users), external dependency, latency for token verification, less control over flows.
- **Verdict**: Consider for future enterprise features (SSO). Overkill for MVP.

## Cookie Configuration

```python
# Django settings for cookie-based JWT auth
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True          # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'       # CSRF mitigation
CSRF_COOKIE_HTTPONLY = False           # Must be readable by JS for double-submit
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'

CORS_ALLOWED_ORIGINS = [
    'https://app.yourdomain.com',
]
CORS_ALLOW_CREDENTIALS = True         # Required for cookie transmission
```

## Consequences

### Positive
- **Strong security** — HttpOnly cookies + CSRF protection is the most secure browser-based auth pattern
- **Stateless scaling** — JWT verification without server-side state
- **Full control** — Custom RBAC, token claims, and auth flows tailored to our multi-tenancy model
- **Audit trail** — Token JTI enables request-level audit logging

### Negative
- **Cookie complexity** — CORS, SameSite, Secure flags require careful configuration per environment
- **CSRF overhead** — Double-submit pattern adds complexity to frontend requests
- **Token size** — JWT with claims is larger than a session ID cookie. Mitigated by keeping claims minimal.

## Related Documents

- [[authentication-flow|Authentication Flow]]
- [[jwt-strategy|JWT Token Strategy]]
- [[http-only-cookies|HTTP-Only Cookie Configuration]]
- [[csrf-protection|CSRF Protection Strategy]]
- [[rate-limiting|API Rate Limiting]]
- [[ADR-004-supabase|ADR-004 — Supabase as Data Platform]]

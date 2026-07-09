---
type: analysis
title: "Sprint 2.1 Auth Hardening Plan"
analysis_type: framework
date_created: 2026-05-30
date_updated: 2026-05-30
source_count: 0
tags: [product/strategy, product/architecture, security/auth, backend/django, frontend/nextjs]
---

# Sprint 2.1 Auth Hardening Plan

## Methodology

This plan synthesizes the current implementation state after Sprint 1 and the partial Sprint 2 authentication work. It compares the implemented recruiter/admin authentication system against the intended authentication architecture, while preserving the product roadmap principle that candidate accounts should wait until the candidate-facing product surface exists.

## Current Position

Sprint 1 is effectively complete enough to support feature work. Sprint 2 is partially complete: recruiter/admin registration, login, organization approval, RBAC, cookie JWT handling, and protected dashboard routing exist, but authentication is not yet hardened enough to treat as complete.

The current system is a recruiter/admin system, not a candidate system. That is acceptable. Candidate login, candidate registration, and candidate dashboard work should remain out of Sprint 2.1.

## Implementation Status

Implemented on 2026-05-30.

Completed:

- Added `confirm_password` validation to recruiter registration.
- Added frontend confirm-password input and client-side mismatch handling.
- Added scoped DRF throttling for register, login, and refresh endpoints.
- Added Axios-backed silent refresh and single-flight retry behavior while preserving the existing `apiFetch` interface.
- Added session-expiration event handling in the frontend auth provider.
- Added backend auth tests for registration, duplicate email, password mismatch, pending recruiter login, approved login cookies, logout cookie clearing, refresh cookies, protected endpoint access, admin-only access, and login throttling.

Validation:

- Backend Ruff passes.
- Django system check passes.
- Migration check reports no changes.
- Backend test suite passes with 11 tests.
- Frontend ESLint and TypeScript checks pass.
- Frontend production dependency audit reports 0 vulnerabilities.

## Recommended Sprint 2.1 Scope

### 1. Confirm Password

Registration should require both `password` and `confirm_password`.

Acceptance criteria:

- Frontend register form includes confirm password.
- Backend serializer validates password equality.
- Mismatch returns a clear validation error.
- Existing password validation still runs.

Priority: high.

### 2. Silent Token Refresh

The frontend should recover from expired access tokens without forcing an immediate logout.

Acceptance criteria:

- API client detects `401` responses.
- Client calls the refresh endpoint using the HttpOnly refresh cookie.
- Original request is retried once after refresh succeeds.
- Failed refresh clears auth state and sends the user to login.
- Concurrent `401` responses do not trigger uncontrolled refresh storms.

Priority: high.

### 3. Rate Limiting

Authentication endpoints need basic abuse protection before more product workflows depend on them.

Minimum endpoints:

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/refresh/`

Acceptance criteria:

- Login and registration are limited per IP.
- Refresh is limited enough to prevent loops or abuse.
- Rate-limited responses return a clear error and proper HTTP status.
- Development configuration works without external infrastructure.

Priority: high.

### 4. Auth Tests

Authentication currently has insufficient backend coverage.

Minimum tests:

- Registration creates user, organization, and recruiter profile.
- Duplicate email registration fails.
- Password confirmation mismatch fails.
- Pending recruiter cannot log in.
- Approved recruiter can log in and receives cookies.
- Logout clears cookies and blacklists refresh token where possible.
- Refresh rotates/renews access cookies.
- Protected endpoints reject unauthenticated requests.
- Admin-only endpoints reject non-admin users.

Priority: high.

### 5. Password Reset Architecture

Password reset can be designed now without blocking Sprint 3 implementation.

Acceptance criteria:

- Document endpoint shape, token lifetime, email transport, and frontend routes.
- Decide whether implementation is in Sprint 2.1 or deferred.
- If deferred, create clear acceptance criteria for the future implementation.

Priority: medium.

## Explicit Non-Goals

Do not include these in Sprint 2.1:

- Candidate login.
- Candidate registration.
- Candidate dashboard.
- Resume upload.
- Resume parsing.
- AI summaries or scoring.
- Embeddings.
- Pipeline board.

## Roadmap Adjustment

Recommended sequence:

1. Sprint 1: foundation.
2. Sprint 2: authentication, organizations, RBAC.
3. Sprint 2.1: auth hardening.
4. Sprint 3: jobs module and application foundations.
5. Sprint 4: candidate portal and application tracking.
6. Sprint 5: resume upload and storage.
7. Sprint 6: resume parsing.
8. Sprint 7: pipeline board.
9. Sprint 8: hybrid scoring.
10. Sprint 9: embeddings.
11. Sprint 10: AI insights.

## Source References

- [[Sprint 1 Foundation Implementation]]
- [[Authentication Strategy]]
- [[Multi-Tenant Architecture]]
- [[Lumina Nexus UI UX Foundation]]

## Open Questions

- Should Sprint 2.1 implement password reset now, or only document it and defer implementation?
- Should rate limiting be implemented with Django cache first, then Redis-backed throttling later?
- Should the refresh endpoint stay `/api/v1/auth/refresh/` or be renamed to match the original sprint wording of `/api/v1/auth/token/refresh/`?

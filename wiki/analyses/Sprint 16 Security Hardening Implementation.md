---
type: analysis
title: "Sprint 16 Security Hardening Implementation"
analysis_type: framework
date_created: 2026-06-15
date_updated: 2026-06-15
source_count: 0
tags: [product/security, backend/django, frontend/nextjs, sprint/implemented]
---

# Sprint 16 Security Hardening Implementation

## Methodology

Reviewed the existing authentication, cookie JWT, upload, search, public job application, settings, frontend API, and dependency surfaces. Implemented focused hardening that preserves existing product flows while closing high-risk gaps.

## Implemented Scope

- Added cache-backed DRF global and scoped throttles for anonymous, authenticated, auth, upload, and search traffic.
- Added login-failure tracking and temporary account lockout using Django cache.
- Added CSRF token endpoint and optional cookie-JWT CSRF enforcement for unsafe browser-cookie requests.
- Added frontend automatic `X-CSRFToken` handling for unsafe API requests.
- Added Django and Next.js security headers.
- Added shared resume upload validation for size, extension, MIME type, and file signature checks.
- Added HTML-stripping sanitization for recruiter/candidate-controlled text inputs.
- Upgraded vulnerable direct backend dependencies: Django, SimpleJWT, PyJWT, pdfplumber/pdfminer, and pytest.
- Ran frontend and backend dependency/secret checks.

## Validation

- Backend Ruff passed.
- Django system check passed.
- Migration drift check passed.
- Full backend test suite passed: 113 tests.
- Frontend lint, type-check, production build, and npm audit passed.
- Secret-pattern scan found no matching leaked tokens in tracked/scanned project files.

## Known Residual Risk

`pip-audit` still reports `CVE-2025-3000` for `torch`, which is pulled by `sentence-transformers`. PyPI currently exposes no fixed torch version in the audit data; `torch==2.12.0` is pinned for deterministic installs until an upstream fixed release is available.

## Source References

- [[Authentication Strategy]]
- [[Multi-Tenant Architecture]]
- [[Sprint 15 Bulk Operations Implementation]]
- [[overview|Overview]]

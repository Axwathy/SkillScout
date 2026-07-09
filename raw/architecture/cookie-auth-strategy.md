---
type: architecture
title: "HTTP-only Cookie + JWT Authentication Strategy"
date_created: 2025-05-30
date_updated: 2025-05-30
tags: [product/architecture, security]
related_adr: "[[ADR-005-auth-strategy]]"
sprint_implemented: 2
---

# HTTP-only Cookie + JWT Authentication Strategy

> **Sprint 1:** Package installed, settings configured. **Implementation → Sprint 2.**
> This document defines the complete strategy so Sprint 2 has a clear contract to implement.

---

## Overview

Lumina Nexus uses JWT (JSON Web Tokens) delivered via HTTP-only cookies. This approach combines the statelessness of JWT with the XSS protection of HTTP-only cookies.

```
Browser                          Django API
  │                                   │
  │──── POST /api/v1/auth/login ─────►│
  │     { email, password }           │
  │                                   │ Validate credentials
  │                                   │ Issue access + refresh tokens
  │◄─── 200 OK ──────────────────────│
  │     Set-Cookie: access=...        │ HTTP-only, Secure, SameSite=Lax
  │     Set-Cookie: refresh=...       │ HTTP-only, Secure, SameSite=Lax
  │                                   │
  │──── GET /api/v1/me ──────────────►│
  │     Cookie: access=...            │ Auto-sent by browser
  │                                   │ Validate access token from cookie
  │◄─── 200 OK ──────────────────────│
  │     { user data }                 │
```

---

## Token Configuration *(Set in `base.py` Sprint 1)*

| Property | Value | Notes |
|----------|-------|-------|
| Access token lifetime | 15 minutes | Short-lived to limit blast radius |
| Refresh token lifetime | 7 days | Rotated on every use |
| Algorithm | HS256 | Standard, sufficient for this scale |
| Rotation | ✅ Enabled | New refresh token issued on each refresh |
| Blacklist | ✅ Enabled | Consumed tokens blacklisted immediately |

---

## Cookie Settings *(To implement in Sprint 2)*

```python
# Sprint 2 implementation target
AUTH_COOKIE_ACCESS = "access"         # Cookie name for access token
AUTH_COOKIE_REFRESH = "refresh"       # Cookie name for refresh token
AUTH_COOKIE_HTTP_ONLY = True          # No JavaScript access
AUTH_COOKIE_SECURE = True             # HTTPS only (False in dev)
AUTH_COOKIE_SAMESITE = "Lax"         # CSRF protection without breaking OAuth
AUTH_COOKIE_PATH = "/"
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days (refresh token lifetime)
```

---

## Token Refresh Flow *(Sprint 2)*

```
Browser                          Django API
  │                                   │
  │ [access token expired]            │
  │──── POST /api/v1/auth/refresh ───►│
  │     Cookie: refresh=...           │
  │                                   │ Validate refresh token
  │                                   │ Blacklist old refresh token
  │                                   │ Issue new access + refresh tokens
  │◄─── 200 OK ──────────────────────│
  │     Set-Cookie: access=...        │ New access token
  │     Set-Cookie: refresh=...       │ New refresh token (rotated)
```

---

## Logout Flow *(Sprint 2)*

```python
# Sprint 2: logout endpoint clears both cookies and blacklists refresh token
response.delete_cookie("access")
response.delete_cookie("refresh")
# Blacklist the refresh token via SimpleJWT's token_blacklist app
```

---

## Custom Authentication Class *(Sprint 2)*

A custom DRF authentication class will read the access token from the cookie instead of the `Authorization` header:

```python
# apps/accounts/authentication.py — Sprint 2
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access")
        if raw_token is None:
            return None
        # Validate and return (user, token)
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
```

Register in `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]` during Sprint 2.

---

## CSRF Considerations

- HTTP-only cookies prevent XSS token theft.
- `SameSite=Lax` prevents CSRF for the majority of attack vectors.
- Django's CSRF middleware remains active.
- The frontend must send the CSRF token in the `X-CSRFToken` header for state-mutating requests (POST, PUT, DELETE, PATCH).

---

## API Endpoints *(Sprint 2 targets)*

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/auth/login/` | Issue tokens, set cookies |
| `POST` | `/api/v1/auth/logout/` | Clear cookies, blacklist refresh |
| `POST` | `/api/v1/auth/refresh/` | Rotate tokens |
| `GET` | `/api/v1/auth/me/` | Return authenticated user profile |
| `POST` | `/api/v1/auth/register/` | Create user + organization |

---

## Related

- [[ADR-005-auth-strategy]] — Architectural decision record
- `backend/config/settings/base.py` — `SIMPLE_JWT` configuration block
- `backend/apps/accounts/` — Auth models and (Sprint 2) views

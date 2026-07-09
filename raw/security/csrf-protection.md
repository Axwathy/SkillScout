---
type: security
title: "CSRF Protection Strategy"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [security, product/architecture]
---

## Overview

Since the recruitment SaaS uses [[http-only-cookies|HTTP-Only Cookie Configuration]] for JWT transport, the application is inherently vulnerable to Cross-Site Request Forgery (CSRF) attacks. This document defines the CSRF protection strategy using Django's built-in middleware combined with the **double-submit cookie pattern** adapted for SPA (Single Page Application) frontends.

## CSRF Attack Model

```
┌─────────────┐       1. User visits          ┌──────────────┐
│             │       malicious site           │              │
│   Attacker  │ ◄──────────────────────────── │   Browser    │
│   Website   │                                │  (logged in  │
│             │       2. Malicious form         │   to SaaS)   │
│             │       auto-submits to           │              │
│             │       api.yourdomain.com        │              │
│             │ ────────────────────────────►  │              │
│             │       3. Browser includes       │              │
│             │       auth cookies              │              │
│             │       automatically!            │              │
└─────────────┘                                └──────────────┘
```

Without CSRF protection, any website can submit requests to our API, and the browser will automatically include the user's authentication cookies, effectively impersonating the authenticated user.

## Protection Strategy: Double-Submit Cookie Pattern

### How It Works

1. On login, the server sets a **readable** CSRF cookie (not HttpOnly) alongside the HttpOnly auth cookies
2. The frontend JavaScript reads the CSRF cookie value
3. For every state-changing request (POST, PUT, PATCH, DELETE), the frontend includes the CSRF token in a custom header (`X-CSRFToken`)
4. The Django middleware validates that the header value matches the cookie value
5. An attacker's site **cannot read** cookies from another domain (Same-Origin Policy), so they cannot forge the header

### Why This Works

| Attacker Capability | Can They? | Why? |
|---|---|---|
| Trigger requests to our API | ✅ Yes | Forms/fetch can target any URL |
| Include auth cookies | ✅ Yes | Browser sends cookies automatically |
| Read our CSRF cookie | ✗ No | Same-Origin Policy prevents cross-domain cookie reading |
| Set the X-CSRFToken header | ✗ No | They don't know the value |

## Django Configuration

### Middleware Setup

```python
# settings.py

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # CORS first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',      # CSRF middleware
    # ... remaining middleware
]

# CSRF Configuration
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_HTTPONLY = False          # Must be readable by JavaScript
CSRF_COOKIE_SECURE = True            # HTTPS only
CSRF_COOKIE_SAMESITE = 'Lax'         # Additional CSRF mitigation layer
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'  # Custom header name
CSRF_TRUSTED_ORIGINS = [
    'https://app.yourdomain.com',
    'https://admin.yourdomain.com',
]
```

### Exempt Endpoints

Some endpoints must be exempt from CSRF protection:

```python
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Login endpoint — no existing CSRF cookie yet
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Login is CSRF-exempt because:
    1. The user has no CSRF cookie before authentication
    2. The endpoint is protected by rate limiting instead
    3. Credentials (email/password) serve as the authentication proof
    """
    throttle_classes = [LoginRateThrottle]  # 5 attempts/min

    def post(self, request):
        # ... authenticate and set cookies (including CSRF cookie) ...
        pass


# Webhook endpoints (authenticated via signature, not cookies)
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Verified via Stripe signature header, not user cookies."""
    pass
```

| Endpoint | CSRF Exempt? | Alternative Protection |
|---|---|---|
| `POST /api/v1/auth/login` | ✅ Yes | Rate limiting (5/min) |
| `POST /api/v1/auth/register` | ✅ Yes | Rate limiting (3/min) + email verification |
| `POST /api/v1/auth/refresh` | ✗ No | CSRF required (uses existing cookies) |
| `POST /api/v1/auth/logout` | ✗ No | CSRF required |
| `POST /api/v1/webhooks/*` | ✅ Yes | Signature verification |
| All other state-changing APIs | ✗ No | CSRF required |

## Frontend Implementation

### Axios Configuration (React/Next.js)

```javascript
// lib/api.js — Axios instance with CSRF support

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // Include cookies in cross-origin requests
});

// Read CSRF token from cookie and attach to every request
api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

export default api;
```

### Fetch API Alternative

```javascript
// Using native fetch with CSRF
async function apiRequest(url, options = {}) {
  const csrfToken = getCookie('csrftoken');

  return fetch(`${API_BASE_URL}${url}`, {
    ...options,
    credentials: 'include',  // Include cookies
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      ...options.headers,
    },
  });
}
```

## CORS + CSRF Interaction

CORS and CSRF work together but must be configured carefully:

| CORS Setting | Value | CSRF Impact |
|---|---|---|
| `CORS_ALLOW_CREDENTIALS` | `true` | Required for cookies to be sent |
| `CORS_ALLOWED_ORIGINS` | Explicit list | Must match `CSRF_TRUSTED_ORIGINS` |
| `CORS_ALLOW_ALL_ORIGINS` | `false` | Must be false with credentials |
| `CORS_ALLOW_HEADERS` | Include `X-CSRFToken` | Required for custom header |

```python
# Ensure CORS allows the CSRF header
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',        # Must be explicitly allowed
    'x-requested-with',
]
```

## Testing CSRF Protection

```python
# tests/test_csrf.py

class CSRFProtectionTests(APITestCase):
    def test_post_without_csrf_token_rejected(self):
        """State-changing requests without CSRF token should be rejected."""
        self.client.force_login(self.user)
        response = self.client.post('/api/v1/candidates/', data={...})
        self.assertEqual(response.status_code, 403)

    def test_post_with_valid_csrf_token_accepted(self):
        """Requests with valid CSRF token should succeed."""
        self.client.force_login(self.user)
        csrf_token = self.client.cookies['csrftoken'].value
        response = self.client.post(
            '/api/v1/candidates/',
            data={...},
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(response.status_code, 201)

    def test_login_exempt_from_csrf(self):
        """Login endpoint should work without CSRF token."""
        response = self.client.post('/api/v1/auth/login/', data={
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertIn(response.status_code, [200, 401])
```

## Related Documents

- [[http-only-cookies|HTTP-Only Cookie Configuration]]
- [[authentication-flow|Authentication Flow]]
- [[jwt-strategy|JWT Token Strategy]]
- [[rate-limiting|API Rate Limiting]]
- [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]]

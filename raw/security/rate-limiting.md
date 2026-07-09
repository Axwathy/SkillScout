---
type: security
title: "API Rate Limiting"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [security, product/architecture]
---

## Overview

Rate limiting protects the recruitment SaaS from abuse, brute-force attacks, and excessive resource consumption. This document defines the rate limiting strategy using `django-ratelimit` with a Redis backend for distributed enforcement across multiple application servers.

## Rate Limit Tiers

### By Endpoint Category

| Category | Rate Limit | Scope | Rationale |
|---|---|---|---|
| **Authentication** | 5 requests/min | Per IP | Prevent brute-force login attacks |
| **Registration** | 3 requests/min | Per IP | Prevent mass account creation |
| **Password Reset** | 3 requests/min | Per IP | Prevent email bombing |
| **Standard API** | 60 requests/min | Per user | Normal operational throughput |
| **Search/Filter** | 30 requests/min | Per user | Database-intensive queries |
| **AI Endpoints** | 10 requests/min | Per user | LLM inference is expensive ($0.01-0.05/call) |
| **File Upload** | 5 requests/min | Per user | Storage and processing cost |
| **Bulk Operations** | 2 requests/min | Per user | Heavy processing (bulk resume upload) |
| **Webhook Inbound** | 100 requests/min | Per IP | External service delivery |

### By User Role

| Role | Multiplier | Effective Standard API Limit |
|---|---|---|
| `admin` | 2.0× | 120 requests/min |
| `hiring_manager` | 1.5× | 90 requests/min |
| `recruiter` | 1.0× | 60 requests/min |
| `viewer` | 0.5× | 30 requests/min |

## Implementation

### Django-Ratelimit Setup

```python
# requirements.txt
django-ratelimit>=4.1
redis>=5.0

# settings.py
RATELIMIT_USE_CACHE = 'ratelimit'
RATELIMIT_FAIL_OPEN = False  # Deny requests if Redis is unavailable

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    },
    'ratelimit': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',  # Dedicated DB for rate limits
    },
}
```

### Decorator Usage

```python
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

# ── Authentication endpoints ──
class LoginView(APIView):
    @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request):
        # ... login logic ...
        pass

# ── Standard API endpoints ──
class CandidateListView(APIView):
    @ratelimit(key='user', rate='60/m', method=['GET', 'POST'], block=True)
    def get(self, request):
        # ... list candidates ...
        pass

# ── AI endpoints (expensive) ──
class CandidateScoringView(APIView):
    @ratelimit(key='user', rate='10/m', method='POST', block=True)
    def post(self, request):
        # ... invoke AI scoring pipeline ...
        pass

# ── File upload ──
class ResumeUploadView(APIView):
    @ratelimit(key='user', rate='5/m', method='POST', block=True)
    def post(self, request):
        # ... handle resume upload ...
        pass
```

### Custom Rate Limit Key Functions

```python
# utils/ratelimit.py

def get_user_or_ip(group, request):
    """Use authenticated user ID if available, fall back to IP."""
    if request.user.is_authenticated:
        return str(request.user.id)
    return get_client_ip(request)

def get_org_rate(group, request):
    """Rate limit by organization to prevent single-tenant abuse."""
    if hasattr(request.user, 'organization_id'):
        return str(request.user.organization_id)
    return get_client_ip(request)

def get_client_ip(request):
    """Extract real client IP, accounting for reverse proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
```

## Response Headers

All API responses include rate limit headers so clients can self-throttle:

```python
# middleware/ratelimit_headers.py

class RateLimitHeadersMiddleware:
    """Add rate limit information to response headers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add rate limit headers from django-ratelimit
        if hasattr(request, 'limited'):
            response['X-RateLimit-Limit'] = getattr(request, 'ratelimit_limit', '')
            response['X-RateLimit-Remaining'] = getattr(request, 'ratelimit_remaining', '')
            response['X-RateLimit-Reset'] = getattr(request, 'ratelimit_reset', '')

        return response
```

### Response Header Reference

| Header | Example Value | Description |
|---|---|---|
| `X-RateLimit-Limit` | `60` | Maximum requests allowed in window |
| `X-RateLimit-Remaining` | `45` | Requests remaining in current window |
| `X-RateLimit-Reset` | `1716423360` | Unix timestamp when the window resets |
| `Retry-After` | `30` | Seconds to wait before retrying (429 responses only) |

## Rate Limit Exceeded Response

```python
# handlers/ratelimit.py

from django.http import JsonResponse

def ratelimit_handler(request, exception):
    """Custom handler for 429 Too Many Requests."""
    return JsonResponse({
        'error': 'rate_limit_exceeded',
        'message': 'Too many requests. Please wait before trying again.',
        'retry_after': getattr(request, 'ratelimit_reset', 60),
    }, status=429, headers={
        'Retry-After': str(getattr(request, 'ratelimit_reset', 60)),
    })

# settings.py
RATELIMIT_VIEW = 'handlers.ratelimit.ratelimit_handler'
```

## Redis Backend for Distributed Rate Limiting

Using Redis ensures rate limits are enforced consistently across multiple Django instances behind a load balancer:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Django 1  │     │ Django 2  │     │ Django 3  │
└────┬──────┘     └────┬──────┘     └────┬──────┘
     │                 │                 │
     └────────┬────────┴────────┬────────┘
              │                 │
         ┌────▼─────────────────▼────┐
         │         Redis             │
         │   (Shared rate counters)  │
         └───────────────────────────┘
```

### Redis Key Structure

```
ratelimit:<group>:<key>:<window> = <count>
ratelimit:login:192.168.1.1:1716422400 = 3    # 3 login attempts from this IP
ratelimit:api:usr_a1b2c3:1716422400 = 45      # 45 API calls from this user
```

Keys auto-expire with the rate window TTL, preventing unbounded memory growth.

## Monitoring & Alerting

| Metric | Alert Threshold | Action |
|---|---|---|
| 429 response rate | > 5% of requests | Investigate potential abuse or misconfigured client |
| Single IP 429 count | > 50/hour | Auto-block IP, notify security team |
| Single user 429 count | > 20/hour | Flag account for review |
| Redis latency | > 10ms p99 | Scale Redis or investigate network issues |

## Related Documents

- [[backend-architecture|Backend Architecture]]
- [[auth-api|Authentication API]]
- [[jwt-strategy|JWT Token Strategy]]
- [[csrf-protection|CSRF Protection Strategy]]
- [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]]

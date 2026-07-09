---
type: security
title: "JWT Token Strategy"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [security, product/architecture]
---

## Overview

This document defines the JWT token architecture for the recruitment SaaS platform. Tokens are the primary mechanism for stateless API authentication, carrying user identity and authorization claims across requests.

For the broader authentication design, see [[authentication-flow|Authentication Flow]] and [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]].

## Token Architecture

### Token Types

| Property | Access Token | Refresh Token |
|---|---|---|
| **Purpose** | API request authentication | Access token renewal |
| **Lifetime** | 15 minutes | 7 days |
| **Storage** | HttpOnly cookie | HttpOnly cookie |
| **Rotation** | Issued on refresh | Rotated on every use |
| **Revocation** | Blacklisted on logout | Blacklisted on logout |
| **Size (approx.)** | ~500 bytes | ~200 bytes |

### Why 15-Minute Access Tokens?

Short-lived access tokens minimize the window of exploitation if a token is compromised:

- **15 minutes** balances security (limited exposure) with UX (infrequent refresh interruptions)
- Tokens shorter than 5 minutes cause excessive refresh traffic
- Tokens longer than 30 minutes increase the risk window for stolen tokens
- The refresh mechanism is transparent to the user via automatic renewal

### Refresh Token Rotation

```
┌──────────┐                           ┌──────────────┐
│          │  POST /api/v1/auth/refresh    │              │
│          │  Cookie: refresh_token_v1  │              │
│  Browser │ ────────────────────────►  │    Django     │
│          │                            │    Backend    │
│          │  Set-Cookie: access_v2     │              │
│          │  Set-Cookie: refresh_v2    │              │
│          │ ◄────────────────────────  │  Blacklist   │
│          │                            │  refresh_v1  │
└──────────┘                            └──────────────┘
```

**One-time use**: Each refresh token can only be used once. Upon use, a new refresh token is issued and the old one is blacklisted. If a blacklisted refresh token is presented, **all tokens for that user are revoked** (indicates potential token theft).

## JWT Payload Structure

### Access Token Claims

```json
{
  "sub": "usr_a1b2c3d4e5f6",
  "org_id": "org_x7y8z9w0",
  "role": "hiring_manager",
  "permissions": [
    "candidates:read",
    "candidates:write",
    "jobs:read",
    "jobs:write",
    "evaluations:read",
    "evaluations:write"
  ],
  "iat": 1716422400,
  "exp": 1716423300,
  "jti": "tok_9f8e7d6c5b4a",
  "token_type": "access"
}
```

### Claim Definitions

| Claim | Type | Description |
|---|---|---|
| `sub` | string | User ID (prefixed with `usr_`) |
| `org_id` | string | Organization ID for multi-tenancy (prefixed with `org_`) |
| `role` | string | User role: `admin`, `hiring_manager`, `recruiter`, `viewer` |
| `permissions` | array | Granular permission list derived from role |
| `iat` | integer | Issued-at timestamp (Unix epoch) |
| `exp` | integer | Expiration timestamp (Unix epoch) |
| `jti` | string | Unique token identifier for revocation tracking |
| `token_type` | string | `access` or `refresh` |

### Refresh Token Claims (Minimal)

```json
{
  "sub": "usr_a1b2c3d4e5f6",
  "jti": "rtk_1a2b3c4d5e6f",
  "iat": 1716422400,
  "exp": 1717027200,
  "token_type": "refresh",
  "family": "fam_abc123"
}
```

The `family` claim groups refresh token chains. If a token from a revoked family is used, all tokens in the family are invalidated.

## Signing Algorithm

### RS256 vs HS256

| Criterion | RS256 (RSA-SHA256) | HS256 (HMAC-SHA256) |
|---|---|---|
| Key type | Asymmetric (public/private) | Symmetric (shared secret) |
| Verification | Public key (distributable) | Same secret (must be shared) |
| Performance | Slower signing, fast verification | Fast signing and verification |
| Key rotation | Rotate private key; distribute new public key | Rotate secret across all services |
| Microservice fit | ✅ Excellent (verify with public key) | ⚠️ Requires secret sharing |
| Security | Higher (private key never leaves auth service) | Lower (secret must be on every verifier) |

**Decision**: **RS256** for production. The asymmetric model allows future microservices (e.g., AI pipeline workers) to verify tokens with only the public key, without access to the signing secret.

```python
# Django settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': open('/run/secrets/jwt_private_key.pem').read(),
    'VERIFYING_KEY': open('/run/secrets/jwt_public_key.pem').read(),
    'AUTH_HEADER_TYPES': (),  # We use cookies, not headers
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'sub',
    'TOKEN_OBTAIN_SERIALIZER': 'auth.serializers.CookieTokenObtainSerializer',
}
```

## Token Blacklisting

Blacklisted tokens are stored in Redis for fast lookup with automatic expiration:

```python
# Token blacklisting on logout
def blacklist_token(jti: str, exp: int) -> None:
    """Add token JTI to blacklist. Entry auto-expires when token would have expired."""
    ttl = exp - int(time.time())
    if ttl > 0:
        redis_client.setex(f"blacklist:{jti}", ttl, "1")

def is_blacklisted(jti: str) -> bool:
    """Check if a token has been revoked."""
    return redis_client.exists(f"blacklist:{jti}") > 0
```

## Role-Permission Mapping

| Role | Permissions |
|---|---|
| `admin` | Full CRUD on all resources, user management, org settings, billing |
| `hiring_manager` | CRUD on jobs, candidates, evaluations, pipeline management |
| `recruiter` | CRUD on candidates, read jobs, create evaluations |
| `viewer` | Read-only access to candidates, jobs, and evaluations |

## Related Documents

- [[authentication-flow|Authentication Flow]]
- [[http-only-cookies|HTTP-Only Cookie Configuration]]
- [[auth-api|Authentication API]]
- [[csrf-protection|CSRF Protection Strategy]]
- [[ADR-005-auth-strategy|ADR-005 — Authentication Strategy]]

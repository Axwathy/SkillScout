---
type: architecture
title: "Authentication Flow"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, security/auth, security/jwt]
---

# Authentication Flow

## Overview

The platform uses a **JWT-based authentication strategy** with tokens stored in **HttpOnly cookies**. This approach combines the statelessness of JWTs with the XSS protection of HttpOnly cookie storage, avoiding the common vulnerability of storing tokens in `localStorage` or `sessionStorage`.

All authentication endpoints are served under `/api/v1/auth/` and are rate-limited to prevent brute-force attacks.

---

## JWT Token Strategy

| Token | Lifetime | Storage | Purpose |
|-------|----------|---------|---------|
| **Access Token** | 15 minutes | HttpOnly cookie (`access_token`) | Authenticates API requests |
| **Refresh Token** | 7 days | HttpOnly cookie (`refresh_token`) | Obtains new access tokens |

### Token Payload (Access Token)

```json
{
  "user_id": "uuid",
  "org_id": "uuid",
  "role": "admin|recruiter|viewer",
  "exp": 1700000000,
  "iat": 1699999100,
  "jti": "unique-token-id"
}
```

The `org_id` is embedded in the token to enforce multi-tenant data scoping at the middleware level. Every API request is automatically filtered to the user's organization context.

See [[jwt-strategy|JWT Token Strategy]] for detailed token design decisions and rotation policies.

---

## Authentication Flows

### Login Flow

```
1. POST /api/v1/auth/login/ { email, password }
2. Server validates credentials against hashed password (bcrypt)
3. Server generates access + refresh token pair
4. Tokens set as HttpOnly, Secure, SameSite=Lax cookies
5. Response: { user: { id, name, email, role, org } }
```

### Registration Flow

```
1. POST /api/v1/auth/register/ { name, email, password, org_name? }
2. Server validates input, checks for duplicate email
3. If org_name provided → create new Organization, assign user as Admin
4. If invite_code provided → join existing Organization with invited role
5. Verification email sent (optional, configurable per org)
6. Tokens set, user redirected to onboarding
```

### Token Refresh Flow

```
1. Access token expires (401 Unauthorized)
2. Frontend interceptor detects 401
3. POST /api/v1/auth/refresh/ (refresh_token cookie sent automatically)
4. Server validates refresh token, checks blacklist
5. New access + refresh token pair issued
6. Original request retried with new access token
```

The frontend uses an Axios interceptor with a token refresh queue to prevent multiple simultaneous refresh requests.

### Logout Flow

```
1. POST /api/v1/auth/logout/
2. Server blacklists the current refresh token (stored in Redis, TTL = token remaining lifetime)
3. Access and refresh cookies cleared (Set-Cookie with Max-Age=0)
4. Response: 204 No Content
```

### Password Reset Flow

```
1. POST /api/v1/auth/password-reset/ { email }
2. Server generates a time-limited reset token (1 hour expiry)
3. Reset link sent via email: {FRONTEND_URL}/reset-password?token={token}
4. User clicks link → frontend renders reset form
5. POST /api/v1/auth/password-reset/confirm/ { token, new_password }
6. Server validates token, updates password hash, invalidates all existing sessions
```

---

## Role-Based Access Control (RBAC)

| Role | Permissions |
|------|------------|
| **Admin** | Full access: manage org settings, users, billing, all CRUD operations |
| **Recruiter** | Manage jobs, candidates, pipeline. Cannot manage org settings or users |
| **Viewer** | Read-only access to jobs, candidates, pipeline, analytics |

Permissions are enforced at three levels:

1. **Middleware** — Validates JWT, extracts `org_id` and `role`, attaches to `request.user`.
2. **DRF Permission Classes** — Custom permission classes (`IsOrgAdmin`, `IsOrgRecruiter`, `IsOrgMember`) check role against required permission for each view.
3. **Queryset Filtering** — All querysets are scoped by `organization_id` from the JWT payload, preventing cross-tenant data access.

```python
class IsOrgRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'recruiter']
```

---

## CSRF Protection Strategy

Since tokens are stored in cookies (not headers), CSRF protection is critical:

- **Django's CSRF middleware** is enabled for all non-safe methods (POST, PUT, DELETE).
- The frontend obtains a CSRF token via `GET /api/v1/auth/csrf/` on page load.
- The CSRF token is sent in the `X-CSRFToken` header with every mutating request.
- `SameSite=Lax` cookie attribute provides additional CSRF mitigation.

See [[csrf-protection|CSRF Protection Strategy]] for implementation details and edge cases.

---

## Cookie Configuration

```python
# settings.py
JWT_COOKIE_SECURE = True          # HTTPS only in production
JWT_COOKIE_HTTPONLY = True         # Not accessible via JavaScript
JWT_COOKIE_SAMESITE = 'Lax'       # Sent with top-level navigations
JWT_COOKIE_DOMAIN = '.myapp.com'  # Shared across subdomains
JWT_COOKIE_PATH = '/'             # Available to all paths
```

See [[http-only-cookies|HTTP-Only Cookie Configuration]] for browser compatibility notes and testing strategies.

---

## Security Considerations

- **Rate Limiting** — Login attempts limited to 5/minute per IP, password reset to 3/hour per email.
- **Token Blacklisting** — Refresh tokens are blacklisted on logout in Redis for fast lookups.
- **Password Hashing** — bcrypt with 12 rounds (Django's default `BCryptSHA256PasswordHasher`).
- **Input Validation** — All auth inputs validated and sanitized at the serializer level.
- **Audit Logging** — Login, logout, password change, and role change events are logged for security auditing.

---

## Related Documents

- [[jwt-strategy|JWT Token Strategy]] — Detailed token design, rotation, and blacklisting policies.
- [[http-only-cookies|HTTP-Only Cookie Configuration]] — Cookie security configuration and browser behavior.
- [[csrf-protection|CSRF Protection Strategy]] — Cross-site request forgery mitigation implementation.
- [[auth-api|Authentication API]] — API endpoint reference for all authentication routes.
- [[system-overview|System Overview]] — Platform architecture context.

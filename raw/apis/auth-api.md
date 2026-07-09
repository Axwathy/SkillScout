---
type: api
title: "Authentication API"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, security]
---

# Authentication API

## Overview

The Authentication API handles user registration, login, session management, and password recovery. It uses JWT tokens delivered via HttpOnly cookies for secure, stateless authentication. All endpoints are rate-limited and follow OWASP security best practices.

See [[authentication-flow|Authentication Flow]] for the complete auth architecture and [[jwt-strategy|JWT Token Strategy]] for token configuration details.

## Base URL

```
/api/v1/auth/
```

## Endpoint Summary

| Method | Endpoint                   | Description         | Auth Required        | Rate Limit |
| ------ | -------------------------- | ------------------- | -------------------- | ---------- |
| `POST` | `/register/`               | Create new account  | No                   | 5/hour     |
| `POST` | `/login/`                  | Authenticate user   | No                   | 10/min     |
| `POST` | `/logout/`                 | End session         | Yes                  | 30/min     |
| `POST` | `/refresh/`                | Rotate access token | Yes (refresh cookie) | 30/min     |
| `POST` | `/password-reset/`         | Request reset email | No                   | 3/hour     |
| `POST` | `/password-reset/confirm/` | Set new password    | No (token)           | 5/hour     |
| `GET`  | `/me/`                     | Get current user    | Yes                  | 60/min     |

---

## `POST /api/v1/auth/register/`

Create a new user account and organization.

### Request Body

```json
{
  "email": "recruiter@company.com",
  "password": "SecureP@ss123!",
  "password_confirm": "SecureP@ss123!",
  "full_name": "Jane Recruiter",
  "org_name": "Acme Hiring Inc."
}
```

### Validation Rules

| Field | Rules |
|-------|-------|
| `email` | Valid email format, unique across system |
| `password` | Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char |
| `password_confirm` | Must match `password` |
| `full_name` | 2–100 characters |
| `org_name` | 2–200 characters, creates new organization |

### Response — `201 Created`

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "recruiter@company.com",
    "full_name": "Jane Recruiter",
    "role": "admin",
    "organization": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Acme Hiring Inc."
    }
  }
}
```

Sets HttpOnly cookies: `access_token` (15 min TTL) and `refresh_token` (7 day TTL).

### Error Responses

| Status | Code               | Description                               |
| ------ | ------------------ | ----------------------------------------- |
| `400`  | `VALIDATION_ERROR` | Invalid fields (details in response body) |
| `409`  | `EMAIL_EXISTS`     | Email already registered                  |
| `429`  | `RATE_LIMITED`     | Too many registration attempts            |

---

## `POST /api/v1/auth/login/`

Authenticate an existing user with email and password.

### Request Body

```json
{
  "email": "recruiter@company.com",
  "password": "SecureP@ss123!"
}
```

### Response — `200 OK`

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "recruiter@company.com",
    "full_name": "Jane Recruiter",
    "role": "admin",
    "organization": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Acme Hiring Inc."
    },
    "last_login": "2025-05-22T10:30:00Z"
  }
}
```

Sets HttpOnly cookies: `access_token` (15 min) and `refresh_token` (7 days).

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `401` | `INVALID_CREDENTIALS` | Email or password incorrect |
| `403` | `ACCOUNT_DISABLED` | Account has been deactivated |
| `429` | `RATE_LIMITED` | Too many login attempts (locked for 15 min) |

---

## `POST /api/v1/auth/logout/`

End the current session by blacklisting the refresh token and clearing cookies.

### Request

No body required. Authentication via `access_token` cookie.

### Response — `200 OK`

```json
{
  "message": "Successfully logged out."
}
```

Clears both `access_token` and `refresh_token` cookies.

---

## `POST /api/v1/auth/refresh/`

Rotate the refresh token and issue a new access token. Uses token rotation to detect token theft.

### Request

No body required. Authentication via `refresh_token` cookie.

### Response — `200 OK`

```json
{
  "message": "Token refreshed successfully."
}
```

Sets new HttpOnly cookies: `access_token` (15 min) and `refresh_token` (7 days). Previous refresh token is blacklisted.

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `401` | `TOKEN_EXPIRED` | Refresh token has expired |
| `401` | `TOKEN_BLACKLISTED` | Token was already used (possible theft) |

---

## `POST /api/v1/auth/password-reset/`

Send a password reset email with a time-limited token.

### Request Body

```json
{
  "email": "recruiter@company.com"
}
```

### Response — `200 OK`

```json
{
  "message": "If an account with that email exists, a reset link has been sent."
}
```

> **Note:** Always returns 200 regardless of whether the email exists to prevent user enumeration.

---

## `POST /api/v1/auth/password-reset/confirm/`

Set a new password using the token received via email.

### Request Body

```json
{
  "token": "abc123-reset-token-xyz",
  "password": "NewSecureP@ss456!",
  "password_confirm": "NewSecureP@ss456!"
}
```

### Response — `200 OK`

```json
{
  "message": "Password has been reset successfully."
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| `400` | `INVALID_TOKEN` | Token is invalid or expired (24h TTL) |
| `400` | `VALIDATION_ERROR` | Password doesn't meet requirements |

---

## `GET /api/v1/auth/me/`

Retrieve the currently authenticated user's profile.

### Response — `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "recruiter@company.com",
  "full_name": "Jane Recruiter",
  "role": "admin",
  "organization": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Acme Hiring Inc.",
    "plan": "professional",
    "member_count": 5
  },
  "created_at": "2025-01-15T08:00:00Z",
  "last_login": "2025-05-22T10:30:00Z"
}
```

## Security Notes

- All cookies use `HttpOnly`, `Secure`, `SameSite=Strict` flags
- Passwords are hashed with Argon2id (Django's recommended hasher)
- Failed login attempts are tracked per IP and per account
- After 5 failed attempts, account is locked for 15 minutes
- All auth endpoints are behind Nginx rate limiting as an additional layer

## Related Pages

- [[authentication-flow|Authentication Flow]] — Visual flow diagrams for all auth scenarios
- [[jwt-strategy|JWT Token Strategy]] — Token configuration, rotation policy, and blacklisting
- [[jobs-api|Jobs API]] — Protected endpoints requiring authentication
- [[candidate-api|Candidate API]] — Protected endpoints requiring authentication

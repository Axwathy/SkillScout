---
title: "Sprint 2 — Authentication System"
sprint_number: 2
status: planned
start_date: 2026-06-16
end_date: 2026-06-27
story_points_planned: 42
story_points_completed: 0
tags:
  - sprint
  - authentication
  - security
---

# Sprint 2 — Authentication System

## 🎯 Sprint Goal

> **Primary Objective:** Implement a complete JWT authentication system with HttpOnly cookie transport, covering registration, login, email verification, and password reset flows.
>
> **Success Criteria:** Users can register, verify email, log in, and reset passwords. Authenticated routes are protected on both frontend and backend. Tokens refresh silently without user intervention.

---

## 📋 Planned Features

- [ ] JWT-based authentication with HttpOnly secure cookies — see [[jwt-strategy|JWT Token Strategy]]
- [ ] User registration with email verification flow
- [ ] Login/logout with automatic token refresh
- [ ] Password reset via email link
- [ ] Protected route middleware on frontend

---

## ⚙️ Backend Tasks

- [ ] Extend custom User model with `email_verified`, `last_login_ip` fields
- [ ] Implement `POST /api/v1/auth/register/` with input validation and duplicate checks
- [ ] Implement `POST /api/v1/auth/login/` returning JWT access + refresh tokens in HttpOnly cookies
- [ ] Implement `POST /api/v1/auth/logout/` clearing cookies and blacklisting refresh token
- [ ] Implement `POST /api/v1/auth/token/refresh/` for silent token rotation
- [ ] Build email verification flow: generate token → send email → `GET /api/v1/auth/verify-email/`
- [ ] Build password reset flow: request → email link → `POST /api/v1/auth/reset-password/`
- [ ] Configure `djangorestframework-simplejwt` with custom claims and cookie transport
- [ ] Add rate limiting to auth endpoints (5 attempts/minute) per [[rate-limiting|API Rate Limiting]]
- [ ] Write comprehensive tests: registration, login, token refresh, edge cases

See also: [[authentication-flow|Authentication Flow]], [[auth-api|Authentication API]]

---

## 🖥️ Frontend Tasks

- [ ] Build Login page with email/password form, validation, and error states
- [ ] Build Register page with name, email, password, confirm password fields
- [ ] Create `AuthContext` provider with `user`, `isAuthenticated`, `login()`, `logout()` state
- [ ] Implement `useAuth()` hook for consuming auth state across components
- [ ] Build `ProtectedRoute` wrapper component redirecting unauthenticated users
- [ ] Implement silent token refresh using Axios interceptors on 401 responses
- [ ] Create "Forgot Password" and "Reset Password" pages
- [ ] Build email verification confirmation page
- [ ] Add loading skeletons during auth state resolution

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Email service provider selection | Medium | Use console backend for dev, decide provider by mid-sprint | 🟡 In Progress |
| HttpOnly cookie SameSite policy across dev domains | Medium | Configure `localhost` CORS properly | 🔴 Open |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Email templates are plain-text — need HTML templates in a future sprint
- [ ] Rate limiting is basic — should integrate with Redis for distributed rate limiting later

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-01-foundation]] must be completed
- **References:** [[authentication-flow|Authentication Flow]], [[jwt-strategy|JWT Token Strategy]], [[auth-api|Authentication API]]
- **Next Sprint:** [[sprint-03-job-management]] — Job Management

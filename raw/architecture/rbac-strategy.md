---
type: architecture
title: "RBAC Strategy"
date_created: 2026-05-30
date_updated: 2026-05-30
sprint_implemented: 2
tags: [product/architecture, security]
---

# Role-Based Access Control (RBAC) Strategy

## Roles

| Role | Value | Description |
|------|-------|-------------|
| `admin` | `User.Role.ADMIN` | Platform superuser. Manages orgs, recruiters, settings. |
| `recruiter` | `User.Role.RECRUITER` | Core user. Creates jobs, reviews candidates, manages pipeline. |
| `hiring_manager` | `User.Role.HIRING_MANAGER` | Reviews shortlists, provides feedback, makes decisions. |
| `interviewer` | `User.Role.INTERVIEWER` | Conducts interviews, submits scorecards. |

> Roles are stored on `User.role` (CharField). A user has exactly one role.

## Verification Requirement

Recruiters (and hiring managers, interviewers) must pass **organization approval** AND **recruiter verification** before gaining full access. Until then, they are authenticated but unauthorized for most endpoints.

| Condition | Access |
|-----------|--------|
| `org.approval_status == pending` | Login blocked (403) |
| `org.approval_status == approved` + `recruiter.verification_status == pending` | Login blocked (403) |
| Both approved | Full login, tokens issued |
| `verification_status == rejected` | Login blocked (403) |
| `verification_status == suspended` | Login blocked (403) |

## DRF Permission Classes

Defined in `backend/apps/accounts/permissions.py`:

```python
IsAdmin                # user.role == "admin"
IsRecruiter            # user.role == "recruiter"
IsHiringManager        # user.role == "hiring_manager"
IsInterviewer          # user.role == "interviewer"  (Sprint 3+)
IsVerifiedRecruiter    # recruiter profile exists AND verification_status == "approved"
IsAdminOrReadOnly      # safe methods for all, write methods for admin only
```

## Enforcement Points

1. **Login** — `LoginView` checks org + recruiter status before issuing tokens
2. **DRF views** — `permission_classes` on each view
3. **Querysets** — `OrganizationScopedQuerySet` on tenant models (Sprint 3+)
4. **Frontend** — middleware for basic route gating; real enforcement always from `/auth/me` + backend

## Permission Matrix (Sprint 2)

| Endpoint | Admin | Recruiter (approved) | Recruiter (pending) | Unauthenticated |
|----------|-------|---------------------|--------------------|----|
| POST /auth/register | ✅ | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ❌ 403 | ❌ 401 |
| GET /auth/me | ✅ | ✅ | ❌ | ❌ |
| POST /auth/logout | ✅ | ✅ | — | ❌ |
| GET /admin/recruiters | ✅ | ❌ 403 | ❌ | ❌ |
| GET /admin/organizations | ✅ | ❌ 403 | ❌ | ❌ |

## Never Trust Frontend

Frontend route guards are UX conveniences, NOT security. Every state-mutating action must be authorized by the backend. The frontend role check (`user.role`) should only be used to show/hide UI elements — never to unlock data access.

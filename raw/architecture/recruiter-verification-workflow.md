---
type: architecture
title: "Recruiter Registration and Verification Workflow"
date_created: 2026-05-30
date_updated: 2026-05-30
sprint_implemented: 2
tags: [product/architecture, recruitment/onboarding, security]
---

# Recruiter Registration and Verification Workflow

## Overview

Registration is a **multi-step approval process**, not instant access. An unverified recruiter cannot log in and receive tokens.

## Full Flow

```
[1] Recruiter fills registration form
    Fields: first_name, last_name, email, password,
            company_name, company_website

[2] POST /api/v1/auth/register/
    Creates:
      - User (role=recruiter, is_active=True, is_email_verified=False)
      - Organization (approval_status=pending)
      - Recruiter (verification_status=pending, organization=FK)
    Returns: 201 NO COOKIES

[3] Frontend → /pending-verification (static page)
    "Your account has been created. Awaiting admin approval."

[4] Admin reviews pending organizations
    GET /api/v1/admin/organizations/?status=pending
    POST /api/v1/admin/organizations/<id>/approve/
    → Organization.approval_status = "approved"
    → AuditLog written

[5] Admin reviews pending recruiters
    GET /api/v1/admin/recruiters/?status=pending
    POST /api/v1/admin/recruiters/<id>/approve/
    → Recruiter.verification_status = "approved"
    → Recruiter.is_verified = True
    → AuditLog written

[6] Recruiter can now login
    POST /api/v1/auth/login/
    → Validates credentials
    → Checks org.approval_status == "approved"
    → Checks recruiter.verification_status == "approved"
    → Issues access + refresh tokens as HttpOnly cookies
    → Returns 200
```

## Status Values

### Organization `approval_status`
| Value | Meaning |
|-------|---------|
| `pending` | Just registered, awaiting admin review |
| `approved` | Admin approved — recruiters of this org can login |
| `rejected` | Admin rejected — recruiters cannot login |
| `suspended` | Suspended — existing sessions revoked on next refresh |

### Recruiter `verification_status`
| Value | Meaning |
|-------|---------|
| `pending` | Awaiting admin review |
| `approved` | Approved — can login (if org also approved) |
| `rejected` | Rejected — cannot login |
| `suspended` | Suspended — cannot login |

## Login Rejection Messages

| Condition | HTTP | Message |
|-----------|------|---------|
| Bad credentials | 401 | "Invalid email or password." |
| Org pending | 403 | "Your organization is pending approval." |
| Org rejected | 403 | "Your organization access has been denied." |
| Org suspended | 403 | "Your organization has been suspended." |
| Recruiter pending | 403 | "Your account is pending approval." |
| Recruiter rejected | 403 | "Your account access has been denied." |
| Recruiter suspended | 403 | "Your account has been suspended." |

## Future Enhancements (Not Sprint 2)

- Email verification link (Resend/SendGrid)
- Auto-approval for certain email domains (e.g., @enterprise.com)
- Multi-recruiter organization (2nd recruiter at same org auto-approved if org already approved)
- Recruiter invites from within an organization

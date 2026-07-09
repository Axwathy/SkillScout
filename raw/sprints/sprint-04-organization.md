---
title: "Sprint 4 — Organization & Multi-Tenancy"
sprint_number: 4
status: planned
start_date: 2026-07-14
end_date: 2026-07-25
story_points_planned: 40
story_points_completed: 0
tags:
  - sprint
  - organization
  - multi-tenancy
  - rbac
---

# Sprint 4 — Organization & Multi-Tenancy

## 🎯 Sprint Goal

> **Primary Objective:** Implement organization management with member invitations and role-based access control, ensuring all data is properly scoped to organizations for multi-tenant isolation.
>
> **Success Criteria:** Users can create organizations, invite members via email, assign roles (Owner, Admin, Recruiter, Viewer), and all API queries automatically scope data to the user's active organization.

---

## 📋 Planned Features

- [ ] Organization CRUD with branding (name, logo, domain)
- [ ] Member invitation system with email-based onboarding
- [ ] Role-based access control with four permission tiers
- [ ] Automatic data scoping — all queries filtered by organization context

---

## ⚙️ Backend Tasks

- [ ] Create `Organization` model with fields: name, slug, logo, domain, plan_tier, created_by
- [ ] Create `Membership` model linking User ↔ Organization with role enum (Owner, Admin, Recruiter, Viewer)
- [ ] Create `Invitation` model with email, role, token, expiry, status (pending/accepted/expired)
- [ ] Implement `OrganizationViewSet` for CRUD operations (create, update, delete for owners only)
- [ ] Build invitation flow: `POST /api/v1/orgs/{id}/invite/` → email sent → `POST /api/v1/invitations/accept/`
- [ ] Create `OrganizationScopedMixin` for automatic queryset filtering by active org
- [ ] Add middleware to resolve active organization from request headers or user preference
- [ ] Implement role-based permission classes: `IsOrgOwner`, `IsOrgAdmin`, `IsOrgRecruiter`, `IsOrgMember`
- [ ] Retrofit Job model with `organization` ForeignKey and update all queries
- [ ] Write tests: invitation flow, role permissions, data isolation between orgs

---

## 🖥️ Frontend Tasks

- [ ] Build Organization Settings page with name, logo upload, and domain configuration
- [ ] Create Member Management page with role badges and action dropdowns (change role, remove)
- [ ] Build Invitation Flow: invite form → pending invitations list → resend/revoke actions
- [ ] Implement organization switcher dropdown in the top navigation bar
- [ ] Create "Accept Invitation" page for email link recipients
- [ ] Add role-based UI rendering — hide admin controls for non-admin users
- [ ] Build "Create Organization" onboarding wizard for new users

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Retrofitting existing Job model with org scope | Medium | Migration plan drafted, data backfill script ready | 🟡 In Progress |
| Email delivery reliability for invitations | Low | Use verified sender domain, fallback to invitation link display | 🟢 Planned |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Organization logo upload uses basic file storage — should use Supabase Storage (see [[sprint-05-resume-upload]])
- [ ] No audit log for membership changes — track who invited/removed whom

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-03-job-management]] — Job model must exist for org scoping retrofit
- **References:** [[system-overview|System Overview]], [[auth-api|Authentication API]]
- **Next Sprint:** [[sprint-05-resume-upload]] — Resume Upload & Storage

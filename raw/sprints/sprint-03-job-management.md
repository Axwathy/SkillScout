---
title: "Sprint 3 — Job Management"
sprint_number: 3
status: planned
start_date: 2026-06-30
end_date: 2026-07-11
story_points_planned: 38
story_points_completed: 0
tags:
  - sprint
  - jobs
  - crud
---

# Sprint 3 — Job Management

## 🎯 Sprint Goal

> **Primary Objective:** Build complete CRUD operations for job postings including a workflow for creating, editing, publishing, and archiving jobs with a structured requirements builder.
>
> **Success Criteria:** Recruiters can create jobs with structured requirements, publish/unpublish them, search and filter the job list, and view detailed job pages. All operations are organization-scoped.

---

## 📋 Planned Features

- [ ] Full CRUD API for job postings with permission enforcement
- [ ] Job posting lifecycle: Draft → Published → Closed → Archived
- [ ] Interactive requirements builder with skills, experience, and education sections
- [ ] Search and filter capabilities across job listings

---

## ⚙️ Backend Tasks

- [ ] Create `Job` model with fields: title, description, requirements (JSONField), status, salary range, location, remote_policy, department
- [ ] Build `JobSerializer` with nested requirements validation and computed fields
- [ ] Implement `JobViewSet` with full CRUD operations and custom actions (`publish`, `close`, `archive`)
- [ ] Add permission class: only org admins/recruiters can create/edit; candidates can view published jobs
- [ ] Implement search with `django-filter`: by title, department, location, salary range, status
- [ ] Add full-text search using PostgreSQL `SearchVector` for job description queries
- [ ] Create `JobRequirement` structured schema with skill name, proficiency level, required/preferred flag
- [ ] Add pagination (cursor-based) for job listings per [[jobs-api|Jobs API]]
- [ ] Write tests: CRUD operations, permission checks, search accuracy, edge cases

See also: [[jobs-api|Jobs API]], [[job-schema|Job Schema]]

---

## 🖥️ Frontend Tasks

- [ ] Build Job List page with card layout, search bar, and filter sidebar
- [ ] Create Job Detail page displaying all job information with apply CTA
- [ ] Build Create/Edit Job form with multi-step wizard (basics → requirements → review)
- [ ] Implement interactive Requirements Builder UI with add/remove/reorder capabilities
- [ ] Add skill autocomplete using a predefined skills taxonomy
- [ ] Build job status badge component with color-coded lifecycle states
- [ ] Implement optimistic UI updates for status changes
- [ ] Add empty states and loading skeletons for job list

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Skills taxonomy source | Medium | Start with curated list, expand iteratively | 🟡 In Progress |
| Requirements JSONField validation complexity | Low | Use Pydantic models for validation | 🟢 Planned |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Skills taxonomy is hardcoded — should be a dynamic, searchable database table
- [ ] Job search is basic — will be enhanced with semantic search in [[sprint-11-semantic-search]]

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-02-auth]] — requires authenticated users
- **References:** [[jobs-api|Jobs API]], [[job-schema|Job Schema]], [[system-overview|System Overview]]
- **Next Sprint:** [[sprint-04-organization]] — Organization & Multi-Tenancy

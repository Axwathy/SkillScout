---
type: backlog
title: "MVP Feature List"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, product/strategy]
---

# MVP Feature List

This document defines the minimum viable product scope for the AI Recruitment SaaS platform. Features are categorized by priority level with complexity estimates and sprint assignments.

See also: [[future-features|Future Features]], [[sprint-01-foundation|Sprint 1 — Project Foundation]], [[sprint-02-auth|Sprint 2 — Authentication System]], [[sprint-03-job-management|Sprint 3 — Job Management]]

---

## Priority Definitions

| Priority | Label       | Definition                                          |
|----------|-------------|-----------------------------------------------------|
| **P0**   | Must-Have   | MVP cannot launch without these features            |
| **P1**   | Should-Have | Significantly improves the product; include if time allows |
| **P2**   | Nice-to-Have| Desirable but can be deferred to post-MVP           |

## Complexity Scale

| Size | Estimate      | Description                          |
|------|---------------|--------------------------------------|
| S    | 1-2 days      | Simple, well-understood, minimal risk |
| M    | 3-5 days      | Moderate complexity, some unknowns   |
| L    | 1-2 weeks     | High complexity, requires research or iteration |

---

## P0 — Must-Have Features

These features constitute the absolute minimum for a functional product launch.

| Feature                   | Description                                                                 | Size | Sprint |
|---------------------------|-----------------------------------------------------------------------------|------|--------|
| **User Authentication**   | Email/password registration and login with JWT tokens. Password reset flow. Role-based access (admin, recruiter, viewer). | M | [[sprint-02-auth|Sprint 2 — Authentication System]] |
| **Job CRUD**              | Create, read, update, delete job postings. Fields: title, description, requirements, location, salary range, employment type. Status management (draft, active, closed). | M | [[sprint-03-job-management|Sprint 3 — Job Management]] |
| **Resume Upload + Parsing** | Upload resumes in PDF/DOCX format. AI-powered parsing extracts structured data: name, email, phone, skills, experience, education. Store raw file + parsed JSON. | L | [[sprint-05-resume-upload|Sprint 5 — Resume Upload & Storage]] / [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]] |
| **Basic Candidate Scoring** | AI-generated match score (0-100) for each candidate against a specific job. Score based on skill match, experience relevance, and education fit. Display score with brief explanation. | L | [[sprint-08-candidate-ranking|Sprint 8 — Candidate Ranking Engine]] |
| **Pipeline Board**        | Kanban-style board showing candidates across hiring stages. Default stages: Applied → Screening → Interview → Offer → Hired/Rejected. Drag-and-drop to move candidates between stages. | M | [[sprint-09-pipeline|Sprint 9 — Hiring Pipeline]] |
| **Candidate Dashboard**   | Searchable, sortable list of all candidates. Filter by job, stage, score range, skills. Candidate detail view with parsed resume data, score breakdown, and stage history. | M | [[sprint-10-candidate-dashboard|Sprint 10 — Candidate Dashboard]] |

---

## P1 — Should-Have Features

These features add significant value and should be included if the sprint schedule allows.

| Feature                      | Description                                                               | Size | Sprint |
|------------------------------|---------------------------------------------------------------------------|------|--------|
| **Semantic Search**          | Natural language search across candidates. "Find me a senior Python developer with AWS experience." Powered by pgvector embeddings and cosine similarity. | L | [[sprint-11-semantic-search|Sprint 11 — Semantic Search]] |
| **AI Interview Questions**   | Auto-generate tailored interview questions based on the job description and the candidate's resume. Categorized by competency area (technical, behavioral, situational). | M | [[sprint-12-interview-ai|Sprint 12 — AI Interview Assistance]] |
| **Email Notifications**      | Automated emails for key pipeline events: new application received, candidate moved to next stage, offer extended. Templated emails using Django templates or a service like SendGrid. | M | [[sprint-13-notifications|Sprint 13 — Notification System]] |
| **Basic Analytics**          | Dashboard showing: total candidates per job, pipeline conversion rates (applied → hired), average time-in-stage, top candidate sources. Charts using a frontend library (Chart.js or Recharts). | M | [[sprint-14-analytics|Sprint 14 — Analytics Dashboard]] |

---

## P2 — Nice-to-Have Features

These features enhance the product but can be safely deferred to post-MVP releases.

| Feature                       | Description                                                              | Size | Sprint |
|-------------------------------|--------------------------------------------------------------------------|------|--------|
| **Bulk Operations**           | Upload multiple resumes at once (ZIP or batch file picker). Bulk move candidates across stages. Bulk reject with templated reason. | M | Post-MVP |
| **Advanced Analytics**        | Diversity metrics, time-to-fill trends, source effectiveness, recruiter performance. Exportable reports (CSV, PDF). | L | Post-MVP |
| **Custom Pipeline Stages**    | Allow recruiters to define custom hiring stages per job (e.g., "Technical Screen," "Culture Fit Interview"). Default stages serve as a template. | S | Post-MVP |
| **Team Collaboration**        | Multiple recruiters on the same job. Candidate notes and comments. Activity feed showing who did what and when. @mention notifications. | L | Post-MVP |

---

## Feature Dependencies

```
User Auth ──────────────────────────────────────────────┐
    │                                                    │
    ▼                                                    ▼
Job CRUD ──────────► Resume Upload ──────► Candidate     Pipeline
    │                     │                Scoring        Board
    │                     │                   │             │
    │                     ▼                   ▼             │
    │              Semantic Search ◄──── AI Interview      │
    │                                    Questions         │
    ▼                                                      │
Basic Analytics ◄──────────────────────────────────────────┘
```

---

## MVP Success Criteria

The MVP is considered successful when a recruiter can:

1. **Post a job** with a full description and requirements
2. **Receive applications** by uploading candidate resumes
3. **Get AI-powered scoring** that ranks candidates by relevance
4. **Manage the pipeline** by moving candidates through hiring stages
5. **Find candidates** by searching and filtering across all applications
6. **Make a hire** by tracking a candidate from application to offer

### Target Metrics (First 30 Days)

| Metric                    | Target      |
|---------------------------|-------------|
| Active recruiters         | 5-10        |
| Jobs posted               | 20+         |
| Resumes processed         | 200+        |
| Average scoring accuracy  | > 70% alignment with human judgment |
| Pipeline completion rate  | > 50% of jobs reach "offer" stage   |

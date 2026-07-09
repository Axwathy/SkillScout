---
type: architecture
title: "System Overview"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/llm]
---

# AI Recruitment SaaS — System Overview

## Core Purpose

AI-assisted recruitment SaaS platform designed to streamline and augment the hiring process for modern teams. The platform covers the full recruitment lifecycle:

- **Job Management** — Create, publish, and manage job postings with structured requirements and skill taxonomies.
- **Resume Parsing & AI Analysis** — Automatically extract structured data from uploaded resumes using NLP pipelines.
- **Candidate Ranking via Hybrid Scoring** — Combine semantic similarity, keyword matching, and experience scoring to rank applicants objectively.
- **Hiring Pipeline Management** — Kanban-style boards to track candidates through customizable interview stages.
- **AI Interview Assistance** — Generate tailored interview questions, score rubrics, and post-interview summaries powered by LLMs.

The system is built around a fundamental principle: **AI assists, humans decide**. Every AI-generated score, summary, or recommendation is presented as advisory context — never as an automated gate or decision.

---

## Main Stack

| Layer           | Technology                              | Notes                                              |
|-----------------|------------------------------------------|----------------------------------------------------|
| **Frontend**    | Next.js, TypeScript, TailwindCSS         | App Router, server components, responsive UI       |
| **Backend**     | Django, Django REST Framework            | Modular app structure, class-based views            |
| **Database**    | PostgreSQL (Supabase), pgvector          | Relational + vector storage for embeddings          |
| **Storage**     | Supabase Storage                         | Resume files, profile images, attachments           |
| **AI**          | Qwen2.5-Coder:7B via Ollama, BAAI/bge-small-en-v1.5 | Free, local, privacy-first AI |
| **Async**       | Celery, Redis                            | Background task processing for AI workloads         |
| **Auth**        | JWT (HttpOnly cookies)                   | Secure, stateless authentication                    |
| **Deployment**  | Docker, Nginx, Gunicorn, Django | Replaced PM2 with Nginx+Gunicorn |

---

## Core Modules

The platform is organized into the following functional modules:

- [[authentication-flow|Authentication Flow]] — JWT-based auth with HttpOnly cookies, CSRF protection, and role-based access control.
- **Organizations** — Multi-tenant organization management with data isolation. Each organization operates in a fully scoped context.
- **Jobs** — Job posting creation, requirements management, skill tagging, and embedding generation for semantic search.
- **Candidates** — Candidate profiles, application tracking, resume storage, and parsed data management.
- [[ai-pipeline|AI Pipeline]] — The core intelligence layer: resume parsing → embedding generation → scoring → LLM insights.
- [[semantic-matching|Semantic Matching]] — pgvector-powered vector similarity search for matching candidates to job requirements.
- **Hiring Pipeline** — Customizable Kanban-style stage management with drag-and-drop, notes, and feedback capture.
- [[analytics-dashboard|Analytics Dashboard]] — Recruitment metrics: time-to-hire, pipeline velocity, source effectiveness, diversity analytics.
- [[notification-system|Notification System]] — Email notifications (transactional via SendGrid) and in-app notification center.

---

## Architecture Principles

1. **Math decides, AI explains** — Deterministic scoring computes candidate rank and score. The LLM generates summaries, explanations, recruiter insights, and interview questions only. Humans make the hiring decisions. No candidate is ever automatically rejected by AI.

2. **Privacy-first** — Minimal data retention policies, GDPR-compliant data handling, candidate data deletion on request, and encrypted storage for sensitive information. Resume text is processed but raw files can be purged per retention policies.

3. **Multi-tenant** — All data is organization-scoped. Database queries are filtered by `organization_id` at the ORM level. Row-level security policies in Supabase provide an additional isolation layer.

4. **Event-driven** — Heavy AI workloads (resume parsing, embedding generation, scoring) are processed asynchronously via Celery tasks. The API returns immediately with a task ID; the frontend polls or subscribes for completion.

5. **API-first** — A clean REST API layer separates frontend and backend concerns entirely. The API is versioned (`/api/v1/`), documented with OpenAPI/Swagger, and designed for potential third-party integrations.

6. **Progressive Enhancement** — The UI is functional without AI features. If the AI pipeline is unavailable, recruiters can still manage jobs, review resumes manually, and progress candidates through the pipeline.

---


## Engineering Methodology

**Final Development Lifecycle**
1. Agile Planning
2. AI-Assisted Development
3. Git + Trunk-Based Development
4. CI/CD Automation
5. Testing & Code Quality
6. Security (DevSecOps)
7. Monitoring & Observability
8. Optimization & Scaling
9. Experimentation & Feedback
10. Continuous Improvement

## High-Level Data Flow

```
User → Next.js Frontend → REST API (DRF) → PostgreSQL
                                         ↘ Celery Worker → Ollama (Qwen2.5-Coder:7B)
                                                         → BAAI/bge-small-en-v1.5 (embeddings)
                                                         → pgvector (embeddings)
                                                         → Redis (cache/broker)
```

1. Recruiter creates a job posting → Job data stored, job embedding generated asynchronously.
2. Candidate applies or resume is uploaded → Resume stored in Supabase Storage.
3. Celery worker picks up parsing task → Extracts text, parses structured data, generates embedding.
4. Scoring engine runs → Computes hybrid score (semantic + skill + experience), stores results.
5. LLM generates summary → Explains the score, highlights strengths/gaps, suggests interview questions.
6. Recruiter reviews ranked candidates → Moves candidates through pipeline stages.

---

## Related Documents

- [[backend-architecture|Backend Architecture]] — Django project structure, app organization, DRF patterns.
- [[frontend-architecture|Frontend Architecture]] — Next.js App Router, component hierarchy, state management.
- [[deployment-architecture|Deployment Architecture]] — Production infrastructure, CI/CD, scaling strategy.
- [[async-task-flow|Async Task Flow]] — Celery + Redis configuration, task types, retry policies.
- [[semantic-matching|Semantic Matching]] — Vector similarity search, ranking formula, indexing strategy.
- [[ai-pipeline|AI Pipeline]] — Full AI processing pipeline from upload to insight generation.
- [[ai-responsibilities|AI Responsibilities]] — Production responsibility split for embeddings, scoring, and LLMs.

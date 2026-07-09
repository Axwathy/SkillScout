---
type: analysis
title: "Sprint 12 AI Interview Assistance Implementation"
analysis_type: framework
date_created: 2026-06-11
date_updated: 2026-06-11
source_count: 5
tags: [product/feature, product/architecture, ai/llm, recruitment/interview, recruitment/assessment, sprint/implemented]
---

# Sprint 12 AI Interview Assistance Implementation

## Methodology

Reviewed `raw/sprints/sprint-12-interview-ai.md` against the implemented Sprint 8-11 foundation: deterministic ranking, candidate profiles, parsed resumes, candidate notes, pipeline stages, and semantic search. This plan keeps interview assistance as recruiter preparation only; it must not affect ranking, pipeline movement, or hiring recommendations.

## Sprint Goal

Build AI-assisted interview preparation for each candidate-job application. Recruiters should be able to generate structured interview questions, review the rationale/evaluation criteria, add notes, and reuse banked questions.

## Implemented Scope

Sprint 12 core is implemented:

- Interview question data model for application-scoped question sets.
- AI generation service with schema validation and provider fallback.
- Static/question-bank fallback when LLM generation fails.
- Recruiter-scoped APIs to generate and retrieve question sets.
- Recruiter-scoped APIs to update questions and add per-question notes.
- Question bank list/create API for reusable prompts.
- Application detail Interview Prep panel with generate/regenerate, grouped question cards, rationale, evaluation criteria, model/fallback indicator, and note entry.
- Tests for LLM generation, fallback, tenant isolation, note creation, and question-bank visibility.

## Product Rules

- [[Hybrid Ranking System|Math decides. AI explains.]]
- Interview questions are assistance, not scoring or hiring recommendations.
- Generated content must be auditable and editable by recruiters.
- Questions must avoid protected-class inference, medical/family status, age, religion, nationality, disability, or other discriminatory prompts.
- The first release should prioritize saved question sets and notes over automated scheduling or analytics.

## Backend Scope

1. Add interview data models:
   - `InterviewQuestionSet`: application, organization, generated_by, source_context_hash, generation_status, model, created_at.
   - `InterviewQuestion`: question set, category, question_text, rationale, evaluation_criteria, source, order, is_pinned.
   - `InterviewQuestionNote`: question, author, note body, timestamps.
   - `QuestionBankItem`: organization nullable for global seeds, role_family, category, question_text, evaluation_criteria, active flag.
2. Add APIs:
   - `POST /api/v1/interviews/applications/{application_id}/generate/`
   - `GET /api/v1/interviews/applications/{application_id}/questions/`
   - `PATCH /api/v1/interviews/questions/{question_id}/`
   - `POST /api/v1/interviews/questions/{question_id}/notes/`
   - `GET /api/v1/question-bank/`
3. Add service layer:
   - Build candidate-job context from parsed resume, job requirements, ranking breakdown, missing skills, and notes where appropriate.
   - Generate categorized JSON through the current LLM provider with schema validation.
   - Fall back to role-specific question bank items when LLM generation fails.
   - Cache/regenerate based on context hash.
4. Add tests:
   - Tenant isolation.
   - Permission checks.
   - LLM success/failure fallback.
   - Category validation.
   - Bias guardrails.
   - Note CRUD and question reordering.

## Frontend Scope

1. Add an Interview Prep panel to recruiter application detail.
2. Show candidate/job header context with current match breakdown.
3. Add a "Generate questions" action with loading/error states.
4. Render question cards grouped by Technical, Behavioral, Situational, Culture Fit, and Gap Analysis.
5. Add expandable rationale and evaluation criteria.
6. Add inline notes per question.
7. Defer pin/reorder UI to a follow-up.
8. Defer question bank picker to a follow-up.

## Suggested Phasing

### Phase 12A: Core Generated Questions

Implemented models, generation endpoint, retrieval endpoint, prompt/schema validation, fallback bank logic, and frontend question list.

### Phase 12B: Recruiter Workflow

Partially implemented: per-question notes are complete. Pinning, reordering, manual add/edit/delete UI, and question bank picker remain deferred.

### Phase 12C: Hardening

Add bias checklist tests, export/print view, regenerate controls, and better prompt evaluation fixtures.

## Acceptance Criteria

- Recruiters can generate interview questions for an application.
- Questions are grouped by category and include rationale plus evaluation criteria.
- A failed LLM call still returns useful banked questions.
- Generated questions are stored and can be reloaded.
- Notes can be saved per question.
- The feature does not modify application score, rank, status, or pipeline stage.
- Backend and frontend validation pass.

## Deferred

- Interview scheduling integrations.
- Automated candidate evaluation from interview answers.
- Hiring recommendations.
- Analytics dashboards.
- Learning from recruiter feedback.
- Pin/reorder frontend controls.
- Question bank picker modal.
- Print/export view.
- Bias evaluation fixture suite beyond blocked-topic filtering.

## Source References

- [[Sprint 8 Candidate Ranking Implementation]]
- [[Sprint 10 Candidate Dashboard Plan]]
- [[Sprint 11 Semantic Search Implementation]]
- [[LLM Provider Architecture]]
- [[AI Hiring Regulations]]

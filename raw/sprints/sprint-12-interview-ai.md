---
title: "Sprint 12 — AI Interview Assistance"
sprint_number: 12
status: planned
start_date: 2026-11-03
end_date: 2026-11-13
story_points_planned: 36
story_points_completed: 0
tags:
  - sprint
  - ai
  - interview
  - questions
---

# Sprint 12 — AI Interview Assistance

## 🎯 Sprint Goal

> **Primary Objective:** Generate AI-tailored interview questions based on the candidate's profile, resume gaps, and the specific job requirements, providing recruiters with a structured interview preparation toolkit.
>
> **Success Criteria:** Recruiters can generate role-specific interview questions per candidate, covering technical skills, behavioral competencies, and gap analysis. Questions are categorized and include suggested evaluation criteria.

---

## 📋 Planned Features

- [ ] AI-generated interview question sets tailored per candidate-job pair
- [ ] Question categories: Technical, Behavioral, Situational, Culture Fit, Gap Analysis
- [ ] Role-specific question banks as fallback/supplement
- [ ] Interview prep page with question cards and note-taking

---

## 🤖 AI Tasks

- [ ] Design interview question generation prompt: input (job requirements, candidate profile, resume gaps) → output (categorized questions with rationale)
- [ ] Implement few-shot examples for consistent question quality and format
- [ ] Build question categorization logic: map generated questions to predefined categories
- [ ] Create gap analysis prompt: identify missing skills/experience and generate probing questions
- [ ] Design evaluation criteria prompt: for each question, suggest what to listen for in answers
- [ ] Build role-specific question bank: seed 50+ questions across Engineering, Design, Product, Sales, Marketing
- [ ] Test question relevance and bias across diverse candidate profiles

See also: [[interview-generation|Interview Question Generation]]

---

## ⚙️ Backend Tasks

- [ ] Create `InterviewQuestion` model: application, question_text, category, rationale, evaluation_criteria, source (AI/bank), order
- [ ] Implement `POST /api/v1/interviews/{application_id}/generate/` to trigger AI question generation
- [ ] Build `GET /api/v1/interviews/{application_id}/questions/` to retrieve generated questions
- [ ] Create question bank CRUD: `GET/POST /api/v1/question-bank/` for managing reusable questions
- [ ] Implement question pinning and reordering within a set
- [ ] Add interview notes endpoint: `POST /api/v1/interviews/{id}/notes/` for per-question notes
- [ ] Write tests: question generation, category distribution, question bank CRUD

---

## 🖥️ Frontend Tasks

- [ ] Build Interview Prep page: candidate header, job context, question cards list
- [ ] Create Question Card component: question text, category badge, rationale tooltip, evaluation criteria expandable
- [ ] Implement "Generate Questions" button with loading state and result animation
- [ ] Build inline note-taking per question with auto-save
- [ ] Add question reordering via drag-and-drop
- [ ] Create "Add from Question Bank" modal with search and category filter
- [ ] Build print/export view for offline interview use

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Question quality consistency across roles | Medium | Role-specific prompt tuning, human review of outputs | 🟡 In Progress |
| Bias in AI-generated questions | High | Bias review checklist, diverse test profiles, content guidelines | 🔴 Open |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Question bank is static — should learn from recruiter feedback over time
- [ ] No interview scheduling integration — just question preparation

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-08-candidate-ranking]] — scored candidate data needed for context
- **References:** [[interview-generation|Interview Question Generation]], [[ai-pipeline|AI Pipeline]]
- **Next Sprint:** [[sprint-13-notifications]] — Notification System

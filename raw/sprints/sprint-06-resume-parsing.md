---
title: "Sprint 6 — AI Resume Parsing"
sprint_number: 6
status: planned
start_date: 2026-08-11
end_date: 2026-08-21
story_points_planned: 44
story_points_completed: 0
tags:
  - sprint
  - ai
  - resume-parsing
  - llm
---

# Sprint 6 — AI Resume Parsing

## 🎯 Sprint Goal

> **Primary Objective:** Build an AI-powered resume parsing pipeline that extracts structured data (skills, experience, education, certifications) from raw resume text using LLM, producing a standardized candidate profile.
>
> **Success Criteria:** Resumes are automatically parsed into structured JSON with 90%+ field extraction accuracy. Parsed data is stored and viewable in the candidate profile.

---

## 📋 Planned Features

- [ ] LLM-based resume parsing with structured output
- [ ] Async parsing pipeline via Celery with retry logic
- [ ] Parsed data storage with versioning
- [ ] Output schema validation and confidence scoring

---

## ⚙️ Backend Tasks

- [ ] Create `ParsedResume` model with structured fields: skills[], experience[], education[], certifications[], contact_info, summary
- [ ] Implement local embedding service integration service with retry logic and rate limiting
- [ ] Build Celery task `parse_resume_with_llm` triggered after text extraction completes
- [ ] Design structured output schema using Pydantic models for validation
- [ ] Implement parsing pipeline: raw text → prompt construction → LLM call → validation → storage
- [ ] Add error handling: malformed responses, API timeouts, token limit exceeded
- [ ] Create `POST /api/v1/resumes/{id}/reparse/` endpoint for manual re-parsing
- [ ] Implement cost tracking: log token usage and estimated cost per parse
- [ ] Write tests with fixture resumes: standard formats, edge cases, non-English content

See also: [[ai-pipeline|AI Pipeline]], [[resume-analysis|Resume Analysis & Data Extraction]]

---

## 🤖 AI Tasks

- [ ] Design resume parsing prompt with clear instructions and output format specification
- [ ] Implement few-shot examples in prompt for improved extraction consistency
- [ ] Define output schema: skill objects with {name, category, proficiency, years_experience}
- [ ] Build validation layer: check required fields, normalize skill names, validate date ranges
- [ ] Benchmark parsing accuracy across 50+ sample resumes of varying formats
- [ ] Implement confidence scoring for each extracted field
- [ ] Test prompt with edge cases: career gaps, multiple roles at same company, non-standard formats

---

## 🖥️ Frontend Tasks

- [ ] Display parsed resume data in structured view on candidate profile
- [ ] Show parsing status indicator (pending, processing, completed, failed)
- [ ] Build "Re-parse" button for triggering manual re-parsing
- [ ] Display confidence badges next to extracted fields

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| local LLM latency at scale | High | Implement caching, use Qwen2.5-Coder:7B via Ollama with Mistral/Phi-3 fallback only when needed | 🔴 Open |
| Inconsistent LLM output format | Medium | Strict Pydantic validation with retry on failure | 🟡 In Progress |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No support for multi-language resumes — English only initially
- [ ] Confidence scoring is heuristic-based — needs ML-based approach later

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-05-resume-upload]] — raw text must be available
- **References:** [[ai-pipeline|AI Pipeline]], [[resume-analysis|Resume Analysis & Data Extraction]], [[tech-stack|Tech Stack]]
- **Next Sprint:** [[sprint-07-embeddings]] — Embedding Generation & Storage

---
title: "Sprint 8 — Candidate Ranking Engine"
sprint_number: 8
status: planned
start_date: 2026-09-08
end_date: 2026-09-18
story_points_planned: 46
story_points_completed: 0
tags:
  - sprint
  - ai
  - ranking
  - scoring
---

# Sprint 8 — Candidate Ranking Engine

## 🎯 Sprint Goal

> **Primary Objective:** Build a hybrid scoring system that combines semantic similarity, skill matching, and experience relevance to rank candidates against job postings, with AI-generated explanations for each score.
>
> **Success Criteria:** Candidates are scored on a 0–100 scale with sub-scores for semantic, skill, and experience dimensions. Recruiters see ranked candidate lists with clear, AI-generated explanations for each match.

---

## 📋 Planned Features

- [ ] Hybrid scoring formula: semantic (45%) + skill match (30%) + experience (25%)
- [ ] Batch scoring via Celery for all applications on a job
- [ ] AI-generated match explanations per candidate
- [ ] Score caching and invalidation logic

---

## ⚙️ Backend Tasks

- [ ] Create `CandidateScore` model with fields: application, job, candidate, overall_score, semantic_score, skill_score, experience_score, explanation, scored_at
- [ ] Implement `ScoringService` with method `score_application(application)` returning composite score
- [ ] Build semantic similarity calculation using pgvector cosine distance from [[sprint-07-embeddings]]
- [ ] Implement skill matching logic: exact match, synonym match, related skill graph
- [ ] Build experience relevance scorer: years in role, seniority progression, industry overlap
- [ ] Create Celery task `batch_score_applications` to score all applications for a new/updated job
- [ ] Implement score caching with Redis — invalidate on job update or candidate profile change
- [ ] Build `GET /api/v1/jobs/{id}/ranked-candidates/` returning sorted candidates with scores
- [ ] Add filtering on ranked results: minimum score threshold, skill requirements met
- [ ] Write tests: scoring accuracy, formula weights, edge cases (no skills, no experience)

See also: [[ai-pipeline|AI Pipeline]], [[ranking-formula-tests|Ranking Formula Tests]]

---

## 🤖 AI Tasks

- [ ] Design match explanation prompt: given job requirements and candidate profile, explain fit
- [ ] Implement LLM call for generating 2–3 sentence explanations per candidate-job pair
- [ ] Build skill synonym mapping: {"React" ↔ "React.js" ↔ "ReactJS"} normalization layer
- [ ] Calibrate scoring formula weights using test dataset of known good/bad matches
- [ ] Implement confidence indicator: flag low-confidence scores for human review
- [ ] Test explanation quality: accuracy, helpfulness, bias detection

See also: [[candidate-scoring|Candidate Insight Generator]]

---

## 🖥️ Frontend Tasks

- [ ] Build ranked candidate list view with score bars and sub-score breakdown
- [ ] Display AI-generated explanation in expandable card for each candidate
- [ ] Add score filter slider to narrow results by minimum match percentage

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Scoring formula calibration requires labeled data | High | Use synthetic test data, iterate with recruiter feedback | 🔴 Open |
| LLM explanation costs at scale (per candidate) | Medium | Generate explanations on-demand, not batch | 🟡 In Progress |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Skill synonym mapping is static — should evolve into a learning system
- [ ] No A/B testing framework for scoring formula variations

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-07-embeddings]] — embeddings must exist for semantic scoring
- **References:** [[ai-pipeline|AI Pipeline]], [[candidate-scoring|Candidate Insight Generator]], [[ranking-formula-tests|Ranking Formula Tests]]
- **Next Sprint:** [[sprint-09-pipeline]] — Hiring Pipeline

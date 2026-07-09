---
title: "Sprint 11 — Semantic Search"
sprint_number: 11
status: planned
start_date: 2026-10-20
end_date: 2026-10-30
story_points_planned: 44
story_points_completed: 0
tags:
  - sprint
  - search
  - semantic
  - pgvector
---

# Sprint 11 — Semantic Search

## 🎯 Sprint Goal

> **Primary Objective:** Implement natural language search across candidates and jobs using vector similarity, combined with traditional keyword search (BM25) for a hybrid search experience.
>
> **Success Criteria:** Recruiters can type natural language queries like "senior React developer with healthcare experience" and receive ranked results combining semantic relevance and keyword matches, with sub-200ms response times.

---

## 📋 Planned Features

- [ ] Natural language search endpoint with hybrid ranking (vector + BM25)
- [ ] Search across candidates, jobs, or both simultaneously
- [ ] Faceted filtering: skills, experience years, location, salary range
- [ ] Relevance score display with match explanation

---

## ⚙️ Backend Tasks

- [ ] Create `SearchService` class with hybrid search method combining pgvector cosine similarity and PostgreSQL full-text search
- [ ] Implement `GET /api/v1/search/candidates/` with query param accepting natural language
- [ ] Implement `GET /api/v1/search/jobs/` for searching job postings semantically
- [ ] Build query embedding generation: convert search text → embedding on-the-fly
- [ ] Implement BM25 ranking using PostgreSQL `ts_rank` with `to_tsvector`/`plainto_tsquery`
- [ ] Create hybrid scoring formula: `final_score = α * semantic_score + (1-α) * bm25_score` with configurable α
- [ ] Add faceted filters: skills (array contains), min/max experience, location radius, remote_policy
- [ ] Implement search result caching with Redis (TTL 60s, keyed by query hash)
- [ ] Add search analytics: log queries, click-through rates, no-result queries
- [ ] Write tests: search relevance benchmarks, filter combinations, performance under load

See also: [[semantic-search|Semantic Search]], [[semantic-matching|Semantic Matching]]

---

## 🖥️ Frontend Tasks

- [ ] Build Search Page with prominent search bar and typeahead suggestions
- [ ] Create search results list with relevance score badges and match highlights
- [ ] Build filter sidebar with checkbox groups, range sliders, and tag inputs
- [ ] Implement search-as-you-type with debounced API calls (300ms delay)
- [ ] Add "No results" state with suggested alternative queries
- [ ] Create saved search feature: bookmark frequently used queries
- [ ] Display search analytics: "Found X results in Yms"
- [ ] Build result card components: candidate card, job card with key info preview

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Embedding generation latency on search queries | Medium | Cache frequently used query embeddings | 🟡 In Progress |
| Hybrid scoring calibration | Medium | A/B test with recruiter feedback on result quality | 🔴 Open |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No query understanding (NLP) — searches are treated as raw text
- [ ] Saved searches lack notification on new matching candidates

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-07-embeddings]] — embeddings must exist for vector search
- **References:** [[semantic-search|Semantic Search]], [[semantic-matching|Semantic Matching]], [[pgvector-notes|pgvector Notes]]
- **Next Sprint:** [[sprint-12-interview-ai]] — AI Interview Assistance

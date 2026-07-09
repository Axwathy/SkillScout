---
type: analysis
title: "Sprint 11 Semantic Search Implementation"
analysis_type: framework
date_created: 2026-06-11
date_updated: 2026-06-11
source_count: 4
tags: [product/feature, product/architecture, ai/embeddings, ai/nlp, recruitment/sourcing, semantic-search, sprint/implemented]
---

# Sprint 11 Semantic Search Implementation

## Methodology

Reviewed the Sprint 11 plan, semantic search feature notes, embedding architecture, and current Sprint 7-10 implementation. The implementation was scoped to reuse existing resume/job embeddings and deterministic scoring helpers instead of introducing a new ranking model.

## Implemented Scope

Sprint 11 core semantic search is implemented across backend and frontend:

- Recruiter-only semantic search APIs under `/api/v1/search/`.
- Search modes for all results, candidates only, and jobs only.
- Hybrid search scoring using 70% semantic similarity and 30% keyword match.
- Filters for skills, experience range, location, remote policy, job status, and result limit.
- Tenant isolation through recruiter organization scoping.
- Candidate results link to [[Candidate Dashboard]] profiles.
- Job results link to the recruiter job detail view.
- Frontend `/dashboard/search` page with query input, search-type tabs, filters, score display, and result cards.
- Candidate search results deduplicate multiple parsed resumes for the same candidate and keep the best matching parsed resume.
- Keyword relevance uses normalized matching so terms like `front-end` and `frontend` match consistently.

## Architecture Notes

The search layer uses [[Semantic Search]] over existing BAAI/bge-small-en-v1.5 embeddings. It does not change the Sprint 8 deterministic ranking formula; search relevance is separate from final candidate-job match scoring. This preserves the product rule from [[Hybrid Ranking System]]: math decides, AI explains.

The backend caches identical search requests for 60 seconds. The implementation keeps Postgres pgvector HNSW indexes for production while making those historical index migration operations skip on SQLite so local tests can build a database schema.

## Deferred

The following Sprint 11 enhancements remain future work:

- Postgres full-text ranking or BM25-style keyword search.
- Saved recruiter searches.
- Search analytics.
- Redis-backed distributed cache.
- Search result highlighting.
- Typeahead suggestions.
- Salary range and location-radius facets.

## Validation

Validation completed:

- Backend Ruff check passes.
- Django system check passes.
- AI engine tests pass.
- Candidate portal regression tests pass.
- Frontend type-check passes.
- Frontend lint passes.
- Frontend production build passes.

## Source References

- [[Semantic Search]]
- [[Sprint 8 Candidate Ranking Implementation]]
- [[Sprint 10 Candidate Dashboard Plan]]
- [[PostgreSQL with pgvector]]

---
title: "Sprint 7 — Embedding Generation & Storage"
sprint_number: 7
status: planned
start_date: 2026-08-25
end_date: 2026-09-04
story_points_planned: 38
story_points_completed: 0
tags:
  - sprint
  - ai
  - embeddings
  - pgvector
---

# Sprint 7 — Embedding Generation & Storage

## 🎯 Sprint Goal

> **Primary Objective:** Generate and store vector embeddings for job postings and candidate profiles using the local embedding service, enabling semantic similarity matching via pgvector in PostgreSQL.
>
> **Success Criteria:** All jobs and parsed candidates have embeddings stored in pgvector columns. Cosine similarity queries return semantically relevant matches in under 200ms.

---

## 📋 Planned Features

- [ ] Embedding generation service for jobs and candidates
- [ ] pgvector extension setup and vector column storage
- [ ] Automatic embedding refresh on content changes
- [ ] Similarity query infrastructure for downstream features

---

## ⚙️ Backend Tasks

- [ ] Enable `pgvector` extension in PostgreSQL via Supabase migration
- [ ] Add `embedding` vector column (384 dimensions) to Job and ParsedResume models
- [ ] Create `EmbeddingService` class with methods: `generate_job_embedding()`, `generate_candidate_embedding()`
- [ ] Implement text preprocessing: combine relevant fields into embedding input string
- [ ] Build Celery task `generate_embedding` triggered on job creation/update and resume parsing completion
- [ ] Create batch embedding endpoint for backfilling existing records
- [ ] Add HNSW index on vector columns for approximate nearest neighbor search performance
- [ ] Implement embedding versioning: track model version used for each embedding
- [ ] Build `GET /api/v1/jobs/{id}/similar-candidates/` endpoint using cosine similarity
- [ ] Write tests: embedding generation, storage, similarity query accuracy

See also: [[semantic-matching|Semantic Matching]], [[pgvector-notes|pgvector Notes]]

---

## 🤖 AI Tasks

- [ ] Select optimal embedding model: `BAAI/bge-small-en-v1.5` vs `text-embedding-3-large` — benchmark cost vs accuracy
- [ ] Design text preprocessing pipeline: field selection, concatenation order, length truncation
- [ ] Build job embedding input: title + description + requirements + skills (weighted)
- [ ] Build candidate embedding input: summary + skills + experience titles + education
- [ ] Test embedding quality with manual similarity assessments across 20+ pairs
- [ ] Document embedding model selection rationale and performance benchmarks

See also: [[embedding-tests|Embedding Model Tests]]

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| pgvector extension availability on Supabase plan | High | Verify plan supports pgvector, fallback to self-hosted PG | 🔴 Open |
| Embedding API costs for large backfills | Medium | Batch requests, implement caching layer | 🟡 Monitoring |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No embedding cache — regenerating on every content change is wasteful
- [ ] Single embedding per entity — may need separate embeddings for different matching contexts

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-06-resume-parsing]] — parsed resume data needed for candidate embeddings
- **References:** [[semantic-matching|Semantic Matching]], [[pgvector-notes|pgvector Notes]], [[embedding-tests|Embedding Model Tests]], [[ai-pipeline|AI Pipeline]]
- **Next Sprint:** [[sprint-08-candidate-ranking]] — Candidate Ranking Engine

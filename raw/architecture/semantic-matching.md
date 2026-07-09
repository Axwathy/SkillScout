---
type: architecture
title: "Semantic Matching"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/embeddings, ai/vector-search, database/pgvector]
---

# Semantic Matching

## Overview

Semantic matching is the mechanism by which candidates are ranked against job postings based on the **meaning** of their qualifications rather than simple keyword overlap. The system uses **pgvector** in PostgreSQL (via Supabase) to store and query high-dimensional embedding vectors, enabling fast cosine similarity search across thousands of candidates.

This approach captures nuanced relationships — for example, a candidate with "React.js" experience would still score highly against a job requiring "frontend JavaScript frameworks," even without an exact keyword match.

---

## How pgvector Stores Embeddings

pgvector extends PostgreSQL with a native `vector` data type and distance operators. Embeddings are stored directly in the relational database alongside other candidate and job data, eliminating the need for a separate vector database.

### Schema Setup

```sql
-- Enable the extension (run once in Supabase SQL editor)
CREATE EXTENSION IF NOT EXISTS vector;

-- Candidate embedding column
ALTER TABLE candidates
ADD COLUMN embedding vector(384);

-- Job embedding column
ALTER TABLE jobs
ADD COLUMN embedding vector(384);
```

The `384` dimension corresponds to the `BAAI/bge-small-en-v1.5` model output. If the embedding model changes, a migration will be required to update the vector dimensions.

---

## Cosine Similarity Calculations

pgvector provides the `<=>` operator for cosine distance. Cosine **similarity** is computed as `1 - cosine_distance`:

```sql
-- Find top 20 candidates for a job, ranked by semantic similarity
SELECT
    c.id,
    c.name,
    1 - (c.embedding <=> j.embedding) AS semantic_score
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
JOIN jobs j ON j.id = a.job_id
WHERE j.id = :job_id
  AND c.embedding IS NOT NULL
ORDER BY c.embedding <=> j.embedding ASC
LIMIT 20;
```

### Distance Operators

| Operator | Distance Metric | Use Case |
|----------|----------------|----------|
| `<=>` | Cosine distance | **Primary** — normalized similarity, scale-invariant |
| `<->` | L2 (Euclidean) distance | Alternative for non-normalized vectors |
| `<#>` | Inner product (negative) | Fast approximation when vectors are normalized |

We use **cosine distance** (`<=>`) as the primary metric because BGE embeddings are normalized before storage, and cosine similarity is the most intuitive measure of semantic relatedness.

---

## Hybrid Ranking Formula

The final candidate ranking uses a **weighted hybrid score** that combines three signals:

```
overall_score = (W_semantic × semantic_score)
              + (W_skill × skill_match_score)
              + (W_experience × experience_score)
```

### Default Weights

| Signal | Weight | Calculation Method |
|--------|--------|--------------------|
| **Semantic Score** | 0.45 | `1 - (candidate.embedding <=> job.embedding)` |
| **Skill Match Score** | 0.30 | `matched_skills / required_skills` with fuzzy matching |
| **Experience Score** | 0.25 | `min(candidate_years / required_years, 1.0)` |

### Skill Matching Details

Skill matching uses a two-pass approach:

1. **Exact Match** — Direct string comparison (case-insensitive) between candidate skills and job required skills.
2. **Fuzzy Match** — For unmatched skills, compute Levenshtein distance and accept matches with similarity > 0.85 (e.g., "PostgreSQL" ↔ "Postgres").

```python
def compute_skill_score(candidate_skills, job_skills):
    matched = 0
    for job_skill in job_skills:
        if exact_match(job_skill, candidate_skills):
            matched += 1
        elif fuzzy_match(job_skill, candidate_skills, threshold=0.85):
            matched += 0.8  # partial credit for fuzzy matches
    return matched / len(job_skills) if job_skills else 0.0
```

### Experience Scoring

Experience is scored as a ratio capped at 1.0. A candidate with 5 years of experience against a 3-year requirement scores `min(5/3, 1.0) = 1.0`. Exceeding requirements is not penalized but provides no additional benefit.

---

## LLM Explanations Without Re-Ranking

After the deterministic hybrid scoring pass, the **top N candidates** (configurable, default 20) are sent to Ollama for contextual explanation:

1. LLM receives the candidate profile, job description, and computed scores.
2. LLM generates a narrative explanation of why the candidate fits (or doesn't).
3. LLM highlights strengths, gaps, and interview follow-up areas.
4. **The LLM cannot override scores, reorder candidates, or suggest rank adjustments.**

This keeps ranking deterministic and auditable while giving recruiters human-readable context.

---

## Indexing Strategy

### IVFFlat vs HNSW

| Feature | IVFFlat | HNSW |
|---------|---------|------|
| **Build Time** | Fast | Slow (2–5× slower) |
| **Query Speed** | Good | Excellent (faster for large datasets) |
| **Recall** | Lower at default settings | Higher |
| **Memory** | Lower | Higher |
| **Update Cost** | Low (append-friendly) | Moderate |
| **Best For** | < 100K vectors, frequent inserts | > 100K vectors, query-heavy workloads |

### Current Strategy

For the initial product phase (< 100K candidates per org), we use **IVFFlat**:

```sql
-- Create IVFFlat index on candidate embeddings
CREATE INDEX idx_candidates_embedding
ON candidates
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create IVFFlat index on job embeddings
CREATE INDEX idx_jobs_embedding
ON jobs
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 20);
```

**Migration Plan:** When any organization exceeds 100K candidates, migrate to HNSW indexing:

```sql
CREATE INDEX idx_candidates_embedding_hnsw
ON candidates
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Query Tuning

```sql
-- Increase probes for higher recall (at cost of speed)
SET ivfflat.probes = 10;  -- default is 1, recommended 5-20
```

---

## Performance Benchmarks (Target)

| Dataset Size | Index Type | Recall@10 | Query Time (p95) |
|-------------|-----------|-----------|-----------------|
| 10K vectors | IVFFlat (lists=50) | 0.95 | < 5ms |
| 50K vectors | IVFFlat (lists=100) | 0.92 | < 15ms |
| 100K vectors | HNSW (m=16) | 0.98 | < 10ms |

---

## Related Documents

- [[ai-pipeline|AI Pipeline]] — Full processing flow from upload to insight generation.
- [[pgvector-notes|pgvector Notes]] — Extension setup, configuration, and operational notes.
- [[ranking-formula-tests|Ranking Formula Tests]] — Test suite validating scoring accuracy and edge cases.
- [[candidate-schema|Candidate Schema]] — Database schema for candidate data and embeddings.
- [[job-schema|Job Schema]] — Database schema for job postings and embeddings.

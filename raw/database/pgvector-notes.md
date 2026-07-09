---
type: database
title: "pgvector Notes"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [database/pgvector, ai/embeddings, database/performance]
---

# pgvector Notes

## Overview

**pgvector** is a PostgreSQL extension that adds support for vector similarity search directly within the relational database. We use it to store and query BGE embedding vectors for both candidates and jobs, enabling [[semantic-matching|Semantic Matching]] without the operational complexity of a separate vector database (Pinecone, Weaviate, etc.).

This document covers setup, configuration, query patterns, and performance tuning for pgvector in the Supabase-hosted PostgreSQL instance.

---

## Extension Setup in Supabase

pgvector is pre-installed in Supabase but must be enabled per project:

```sql
-- Enable pgvector (run once via Supabase SQL Editor or migration)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Version Requirements

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| PostgreSQL | 15+ | Supabase default |
| pgvector | 0.5.0+ | Required for HNSW index support |
| Supabase | Any current plan | pgvector included on all plans |

To check the installed version:

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

---

## Vector Column Types and Dimensions

### Column Definition

```sql
-- Fixed-dimension vector column (384 for BAAI/bge-small-en-v1.5)
ALTER TABLE candidates ADD COLUMN embedding vector(384);
ALTER TABLE jobs ADD COLUMN embedding vector(384);
```

The dimension **must be specified** at column creation and **cannot be changed** without dropping and recreating the column. If you switch embedding models, a migration is required.

### Embedding Model Reference

| Model | Dimensions | Cost Profile | Use Case |
|-------|-----------|--------------|---------|
| `BAAI/bge-small-en-v1.5` | 384 | Local inference | **Current** — free/local MVP default |
| `bge-large-en-v1.5` | 1024 | Local inference with higher CPU/GPU cost | Future quality upgrade candidate |
| `text-embedding-3-small` | 512–1536 | Paid API | Future managed fallback if local inference is insufficient |
| `text-embedding-3-large` | 256–3072 | Paid API | Future highest-quality managed fallback |

### Storing Vectors

```python
# Django ORM with pgvector-python
from pgvector.django import VectorField

class Candidate(models.Model):
    embedding = VectorField(dimensions=384, null=True, blank=True)

# Storing an embedding
candidate.embedding = embedding_service.embed(candidate_text)  # list of 384 floats
candidate.save()
```

```sql
-- Raw SQL insertion
UPDATE candidates
SET embedding = '[0.0023, -0.0091, 0.0142, ...]'::vector
WHERE id = :candidate_id;
```

---

## Index Types

### IVFFlat (Inverted File with Flat Compression)

IVFFlat partitions vectors into lists (clusters) and searches only the nearest lists during query time.

```sql
CREATE INDEX idx_candidates_embedding ON candidates
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

| Parameter | Description | Guideline |
|-----------|------------|-----------|
| `lists` | Number of clusters | `sqrt(num_vectors)` for < 1M rows, `num_vectors / 1000` for > 1M |
| `probes` | Lists to search at query time | Higher = better recall, slower. Default 1, recommend 5–20 |

**Tradeoffs:**
- ✅ Fast build time (minutes for 100K vectors)
- ✅ Low memory overhead
- ✅ Good for datasets with frequent inserts
- ⚠️ Lower recall at default `probes=1`
- ⚠️ Requires table data at index creation time (cannot index empty table)

### HNSW (Hierarchical Navigable Small World)

HNSW builds a multi-layered graph structure for approximate nearest neighbor search.

```sql
CREATE INDEX idx_candidates_embedding_hnsw ON candidates
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

| Parameter | Description | Guideline |
|-----------|------------|-----------|
| `m` | Max connections per node per layer | 16 default. Higher = better recall, more memory |
| `ef_construction` | Search depth during build | 64 default. Higher = better quality index, slower build |
| `ef_search` | Search depth during query | Set via `SET hnsw.ef_search = 100` |

**Tradeoffs:**
- ✅ Excellent recall (> 0.98 with proper tuning)
- ✅ Faster queries than IVFFlat for large datasets
- ✅ Can index empty tables
- ⚠️ Slower build time (2–5× IVFFlat)
- ⚠️ Higher memory usage (2–3× IVFFlat)
- ⚠️ Slower inserts after index exists

### Decision Matrix

| Factor | IVFFlat | HNSW | Our Choice |
|--------|---------|------|------------|
| Dataset < 100K | ✅ Ideal | Overkill | **IVFFlat** |
| Dataset > 100K | Adequate | ✅ Ideal | **HNSW** |
| Frequent inserts | ✅ Better | ⚠️ Slower | IVFFlat |
| Query-heavy | Good | ✅ Better | HNSW |
| Memory constrained | ✅ Lower | ⚠️ Higher | IVFFlat |

**Current Strategy:** Start with IVFFlat. Migrate to HNSW when any organization exceeds 100K candidates.

---

## Query Patterns

### Cosine Distance (Primary)

```sql
-- Top 20 candidates by semantic similarity to a job
SELECT a.id AS application_id,
       c.id AS candidate_id,
       c.full_name,
       1 - (c.embedding <=> j.embedding) AS similarity
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
JOIN jobs j ON j.id = a.job_id
WHERE a.job_id = :job_id
  AND c.embedding IS NOT NULL
ORDER BY c.embedding <=> j.embedding ASC
LIMIT 20;
```

### Inner Product

```sql
-- Faster for normalized vectors (BGE embeddings are normalized before storage)
SELECT a.id AS application_id,
       c.id AS candidate_id,
       c.full_name,
       (c.embedding <#> j.embedding) * -1 AS similarity
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
JOIN jobs j ON j.id = a.job_id
WHERE a.job_id = :job_id
ORDER BY c.embedding <#> j.embedding ASC
LIMIT 20;
```

### L2 (Euclidean) Distance

```sql
-- Alternative distance metric
SELECT a.id AS application_id,
       c.id AS candidate_id,
       c.full_name,
       c.embedding <-> j.embedding AS l2_distance
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
JOIN jobs j ON j.id = a.job_id
WHERE a.job_id = :job_id
ORDER BY c.embedding <-> :job_embedding ASC
LIMIT 20;
```

### Filtering + Vector Search

```sql
-- Combine vector search with metadata filters
SELECT a.id AS application_id,
       c.id AS candidate_id,
       c.full_name,
       1 - (c.embedding <=> :job_embedding) AS similarity
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
WHERE a.organization_id = :org_id
  AND a.job_id = :job_id
  AND a.status NOT IN ('rejected', 'hired')
  AND c.embedding IS NOT NULL
ORDER BY c.embedding <=> :job_embedding ASC
LIMIT 20;
```

> **Note:** pgvector performs the ANN search *after* applying WHERE filters. For best performance, ensure filtered columns have standard B-tree indexes.

---

## Performance Tuning

### IVFFlat Tuning

```sql
-- Increase probes for higher recall (set per session or globally)
SET ivfflat.probes = 10;  -- Default: 1. Recommended: 5–20

-- Rebuild index after large bulk inserts (> 10% of dataset)
REINDEX INDEX idx_candidates_embedding;
```

### HNSW Tuning

```sql
-- Increase search depth for higher recall
SET hnsw.ef_search = 100;  -- Default: 40. Recommended: 50–200
```

### General PostgreSQL Tuning

```sql
-- Increase work memory for vector operations
SET work_mem = '256MB';

-- Increase maintenance work memory for index builds
SET maintenance_work_mem = '512MB';

-- Parallelism for index creation
SET max_parallel_maintenance_workers = 4;
```

### Monitoring Query Performance

```sql
-- Check if index is being used
EXPLAIN ANALYZE
SELECT a.id AS application_id,
       c.id AS candidate_id,
       1 - (c.embedding <=> :job_embedding) AS similarity
FROM candidate_applications a
JOIN candidates c ON c.id = a.candidate_id
WHERE a.job_id = :job_id
ORDER BY c.embedding <=> :job_embedding
LIMIT 20;

-- Expected: "Index Scan using idx_candidates_embedding"
-- If you see "Seq Scan": the index is not being used (check probes, lists config)
```

---

## Operational Notes

- **Index on empty tables:** IVFFlat cannot be created on empty tables (needs data for clustering). HNSW can be created on empty tables.
- **Dimension mismatch:** Inserting a vector with wrong dimensions raises an error. Always validate embedding dimensions before insert.
- **NULL embeddings:** Candidates without embeddings (parsing failed) are excluded from vector search via `WHERE embedding IS NOT NULL`.
- **Backup compatibility:** pgvector data is included in standard `pg_dump` backups. Ensure the target database also has pgvector enabled before restore.

---

## Related Documents

- [[semantic-matching|Semantic Matching]] — How vector similarity is used in the ranking pipeline.
- [[ai-pipeline|AI Pipeline]] — Embedding generation flow and model configuration.
- [[embedding-tests|Embedding Model Tests]] — Test suite for embedding quality and index performance.
- [[candidate-schema|Candidate Schema]] — Candidate table with embedding column definition.
- [[job-schema|Job Schema]] — Job table with embedding column definition.

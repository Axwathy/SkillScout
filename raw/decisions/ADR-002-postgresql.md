---
type: decision
title: "ADR-002 — PostgreSQL with pgvector"
status: decided
date_created: 2025-05-22
date_decided: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, product/strategy]
---

## Context

The recruitment SaaS platform requires a database that can handle two distinct data paradigms simultaneously:

1. **Relational data** — Organizations, users, jobs, candidates, pipeline stages, evaluations, and audit logs with complex relationships and transactional integrity.
2. **Vector embeddings** — Semantic representations of resumes, job descriptions, and skills for AI-powered candidate-job matching via similarity search.

Running separate databases (relational + vector) increases operational complexity, data synchronization challenges, and infrastructure costs. We need a unified solution.

## Decision

**PostgreSQL 15+ with the pgvector extension**, hosted on [[ADR-004-supabase|Supabase]], as the single data store for both relational and vector data.

## Rationale

### Why PostgreSQL?

| Capability | PostgreSQL | MySQL | MongoDB | SQLite |
|---|---|---|---|---|
| ACID compliance | ★★★★★ | ★★★★ | ★★★ | ★★★★ |
| JSON support | ★★★★★ | ★★★ | ★★★★★ | ★★ |
| Full-text search | ★★★★ | ★★★ | ★★★★ | ★★ |
| Vector search (pgvector) | ★★★★ | ✗ | ★★★ (Atlas) | ✗ |
| Row-Level Security | ★★★★★ | ✗ | ✗ | ✗ |
| Django ORM support | ★★★★★ | ★★★★ | ★★ | ★★★★ |
| Extensibility | ★★★★★ | ★★ | ★★★ | ★ |

### Why pgvector?

- **Unified data layer** — Candidate embeddings live alongside candidate profiles in the same database. No cross-database joins or synchronization needed.
- **Production maturity** — pgvector has been used in production by companies like Supabase, Retool, and Notion. It supports IVFFlat and HNSW indexing for performant similarity search.
- **Embedding operations** — Supports L2 distance, inner product, and cosine distance operators natively.
- **Django integration** — Compatible with Django ORM via `pgvector-python` package and custom model fields.

### Vector Search Configuration

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Example: Candidate embedding column (384 dimensions for BAAI/bge-small-en-v1.5)
ALTER TABLE candidates_candidateprofile
ADD COLUMN resume_embedding vector(384);

-- Create HNSW index for approximate nearest neighbor search
CREATE INDEX idx_candidate_embedding_hnsw
ON candidates_candidateprofile
USING hnsw (resume_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Similarity search query
SELECT id, name, 1 - (resume_embedding <=> $1::vector) AS similarity
FROM candidates_candidateprofile
WHERE organization_id = $2
ORDER BY resume_embedding <=> $1::vector
LIMIT 20;
```

## Alternatives Considered

### PostgreSQL + Pinecone
- **Pros**: Pinecone is purpose-built for vector search with excellent performance and managed scaling.
- **Cons**: Additional service to manage, data synchronization between Postgres and Pinecone, extra cost ($70+/mo for production), increased latency for cross-service queries.
- **Verdict**: Unnecessary complexity at our scale. pgvector handles our expected volume (< 1M embeddings) efficiently.

### MongoDB + Atlas Vector Search
- **Pros**: Flexible document model, Atlas Vector Search is well-integrated.
- **Cons**: Document model is suboptimal for highly relational recruitment data (candidates → applications → evaluations → pipeline stages). Lack of RLS for multi-tenancy. Weaker Django ORM support.
- **Verdict**: Not ideal for relational-heavy domain with multi-tenancy requirements.

### Qdrant (Dedicated Vector DB)
- **Pros**: Purpose-built for vector search, excellent filtering, high performance.
- **Cons**: Another service to deploy, manage, and monitor. Data synchronization overhead. No relational data support.
- **Verdict**: Overengineered for our current scale. Consider if we exceed 10M+ embeddings.

## Consequences

### Positive
- **Simplified architecture** — One database for all data, reducing operational burden
- **Transactional consistency** — Vector updates and relational updates in the same transaction
- **Cost efficiency** — Single managed database instance vs. multiple services
- **RLS for multi-tenancy** — PostgreSQL's Row-Level Security provides database-level tenant isolation

### Negative
- **Scale ceiling** — pgvector is less performant than dedicated vector DBs (Pinecone, Qdrant) at extreme scale (10M+ vectors). Mitigation: monitor query latency, plan migration path to dedicated vector DB if needed.
- **Index tuning** — HNSW index parameters (m, ef_construction, ef_search) require tuning based on dataset size and accuracy requirements.
- **Memory overhead** — Vector columns consume storage (384 × 4 bytes = 1.5KB per embedding for the MVP model). Plan for storage scaling if moving to larger models.

## Performance Benchmarks (Expected)

| Dataset Size | HNSW Query Time (p95) | Recall@10 |
|---|---|---|
| 10,000 vectors | < 5ms | > 0.98 |
| 100,000 vectors | < 15ms | > 0.95 |
| 1,000,000 vectors | < 50ms | > 0.92 |

## Related Documents

- [[pgvector-notes|pgvector Notes]]
- [[semantic-matching|Semantic Matching]]
- [[ADR-004-supabase|ADR-004 — Supabase as Data Platform]]
- [[ADR-003-hybrid-ranking|ADR-003 — Hybrid Ranking System]]
- [[backend-architecture|Backend Architecture]]

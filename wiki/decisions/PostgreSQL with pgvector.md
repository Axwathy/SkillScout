---
type: decision
title: "PostgreSQL with pgvector"
status: decided
date_created: 2026-05-22
date_decided: 2025-05-22
superseded_by: ""
tags: [product/architecture, database/pgvector, ai/embeddings]
---

# PostgreSQL with pgvector

## Context

The platform needs relational data integrity for recruiting workflows and vector search for candidate-job matching. Running a separate vector database would add synchronization and operational complexity.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| PostgreSQL + pgvector | One data layer, relational joins, RLS-compatible | Requires index tuning as volume grows |
| PostgreSQL + Pinecone | Purpose-built vector search | Extra service, sync complexity, cost |
| MongoDB Atlas Vector Search | Flexible documents | Weaker fit for relational recruitment data |
| Qdrant | Strong vector DB | Extra infrastructure and synchronization |

## Decision

Use PostgreSQL 15+ with pgvector as the unified relational and vector data store.

## Implications

- Candidate, job, application, and vector data can be queried together.
- Index strategy must be reviewed as the dataset grows.
- Migration to a dedicated vector database remains possible if scale demands it.

## Review Triggers

- Vector count exceeds pgvector performance targets.
- Search latency or recall cannot be tuned adequately.
- Multi-region or high-throughput search needs outgrow Postgres.

## Source References

- `raw/decisions/ADR-002-postgresql.md`

---
type: feature
title: "Semantic Search"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, ai/embeddings, ai/nlp, recruitment/search]
---

# Semantic Search

## Overview

Semantic Search enables recruiters to find candidates using natural language queries instead of exact keyword matches. Powered by vector embeddings and pgvector, it understands the meaning behind queries like "senior backend engineer with distributed systems experience" and returns candidates ranked by semantic relevance.

## Purpose

Traditional keyword search fails when recruiters describe ideal candidates in natural language. A search for "team lead with cloud experience" won't match a resume that says "managed a 5-person squad deploying microservices on AWS." Semantic Search bridges this vocabulary gap by comparing meaning, not words — dramatically improving candidate discovery.

## User Flow

1. **Enter Query** — Recruiter types a natural language description in the search bar (e.g., "Python developer with ML experience and startup background").
2. **Auto-Suggestions** — As the recruiter types, the system suggests recent queries and popular search patterns.
3. **Execute Search** — On submit, the query is embedded and matched against candidate vectors.
4. **View Results** — Results are displayed as a ranked list with relevance scores (0–100%).
5. **Apply Filters** — Narrow results by job, pipeline stage, score range, or date applied.
6. **View Candidate** — Click a result to open the [[candidate-dashboard|Candidate Dashboard]].

## Backend Architecture

### Embedding Pipeline

```
Natural Language Query
        │
        ▼
┌─────────────────┐
│ Query Embedding  │  ← BAAI/bge-small-en-v1.5 (384 dims)
│ Generation       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ pgvector Search  │  ← Cosine similarity with ivfflat index
│ (Vector Match)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Keyword Search   │  ← PostgreSQL full-text search (tsvector)
│ (Text Match)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hybrid Ranking   │  ← RRF (Reciprocal Rank Fusion)
│ & Scoring        │
└────────┬────────┘
         │
         ▼
    Ranked Results
```

### Hybrid Ranking Algorithm

The system combines vector similarity and keyword relevance using Reciprocal Rank Fusion (RRF):

```python
def hybrid_score(vector_rank: int, keyword_rank: int, k: int = 60) -> float:
    """Combine vector and keyword rankings using RRF."""
    vector_score = 1.0 / (k + vector_rank) if vector_rank else 0
    keyword_score = 1.0 / (k + keyword_rank) if keyword_rank else 0
    return vector_score + keyword_score
```

| Component | Weight | Purpose |
|-----------|--------|---------|
| Vector Similarity | Primary | Captures semantic meaning and context |
| Keyword Match | Secondary | Ensures exact term matches are boosted |
| Recency Bias | Tie-breaker | Newer candidates ranked higher on ties |

### Database Query

```sql
-- Vector similarity search with pgvector
SELECT c.id, c.full_name,
       1 - (c.embedding <=> query_embedding) AS similarity_score
FROM candidates c
WHERE c.organization_id = :org_id
  AND c.embedding IS NOT NULL
ORDER BY c.embedding <=> query_embedding
LIMIT 50;
```

The `embedding` column uses a pgvector `vector(384)` type with an IVFFlat index for fast approximate nearest neighbor search. See [[pgvector-notes|pgvector Notes]] for index tuning details.

## Frontend Components

### Search Input

- Full-width search bar with magnifying glass icon
- Placeholder text: "Search candidates by skills, experience, or description..."
- Recent searches dropdown on focus
- Debounced input (300ms) to avoid excessive API calls
- Clear button and keyboard shortcut (`Ctrl+K` / `Cmd+K`)

### Results List

Each result card shows:

- **Relevance Score** — Circular progress indicator (0–100%)
- **Candidate Name** — Linked to [[candidate-dashboard|Candidate Dashboard]]
- **Current Title** — Most recent job title
- **Key Matches** — Highlighted text snippets showing why this candidate matched
- **Skills Tags** — Relevant skills highlighted with match indicators
- **Applied For** — Job title they applied for
- **Pipeline Stage** — Current stage badge

### Filters Panel

| Filter | Type | Options |
|--------|------|---------|
| Job | Dropdown | All open jobs |
| Pipeline Stage | Multi-select | All configured stages |
| Score Range | Range slider | 0–100 |
| Date Applied | Date range | Custom range picker |
| Has Resume | Toggle | Yes/No |

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Empty results | Show helpful message: "No candidates match your search. Try broadening your query." |
| Very broad queries ("engineer") | Return top 50 results; suggest adding specificity |
| Typos in query | Embedding model is typo-tolerant; also suggest corrections |
| Multi-language queries | Embedding model supports multilingual input natively |
| No embedding for candidate | Exclude from vector results; include in keyword-only fallback |
| Query too long (> 500 words) | Truncate to first 500 words with warning |

## Performance

- Embedding generation: ~100ms per query via local embedding service
- pgvector search: ~50ms for 100K candidates with IVFFlat index
- Total round-trip: < 500ms for typical queries
- Results are not cached (queries are unique), but candidate data is pre-joined

## Related Pages

- [[semantic-matching|Semantic Matching]] — Detailed algorithm documentation
- [[pgvector-notes|pgvector Notes]] — PostgreSQL vector extension setup and tuning
- [[sprint-11-semantic-search|Sprint 11 — Semantic Search]] — Implementation sprint
- [[ai-pipeline|AI Pipeline]] — Overall AI architecture
- [[candidate-api|Candidate API]] — Search endpoint documentation

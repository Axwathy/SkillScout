---
type: architecture
title: "AI Responsibilities"
date_created: 2026-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/llm, ai/embeddings, ai/scoring]
---

# [PRODUCTION] AI Responsibilities

## Core Principle

Math decides. AI explains.

The recruitment platform separates semantic retrieval, deterministic scoring, and LLM-generated recruiter context. This keeps ranking stable, auditable, and explainable.

## Embedding Model

| Field | Value |
|---|---|
| Model | `BAAI/bge-small-en-v1.5` |
| Dimensions | 384 |
| Storage | PostgreSQL pgvector |

### Purpose

- Semantic similarity
- Vector search
- Candidate-job matching
- Semantic search

### Restrictions

- Does not produce final scores by itself
- Does not make hiring decisions
- Does not generate recruiter-facing explanations

## Hybrid Scoring Engine

The hybrid scoring engine is deterministic and rule-based.

### Inputs

- `semantic_similarity`
- `skill_match`
- `experience_match`

### Formula

```text
final_score =
  0.45 * semantic_similarity +
  0.30 * skill_match +
  0.25 * experience_match
```

### Responsible For

- Candidate ranking
- Candidate ordering
- Score generation
- Audit-friendly scoring history

### Restrictions

- Must not depend on score values created by an LLM
- Must preserve the scoring algorithm version
- Must expose sub-scores for recruiter review

## LLM

| Field | Value |
|---|---|
| Primary model | `Qwen2.5-Coder:7B` via Ollama |
| Fallback models | Mistral, Phi-3 |

### Purpose

- Summaries
- Explanations
- Recruiter insights
- Interview question generation
- Resume analysis
- Optional skill extraction assistance

### Restrictions

- Cannot modify scores
- Cannot reorder candidates
- Cannot alter the hybrid score
- Cannot make hiring decisions
- Cannot reject or advance candidates automatically
- Cannot act as the production ranking engine

## Production vs Experimental Labels

Use lifecycle labels in headings or frontmatter where helpful:

| Label | Meaning |
|---|---|
| `[PRODUCTION]` | Current implementation direction or accepted architecture |
| `[EXPERIMENTAL]` | Research, tests, or alternatives that are not current production behavior |
| `[DEPRECATED]` | Rejected or superseded ideas preserved for history |

Experimental formulas and model trials may stay in the vault, but they must be clearly marked so they do not override the production architecture.

## Related Documents

- [[ai-pipeline|AI Pipeline]]
- [[semantic-matching|Semantic Matching]]
- [[ADR-003-hybrid-ranking|ADR-003 - Hybrid Ranking System]]
- [[ranking-formula-tests|Ranking Formula Tests]]
- [[candidate-scoring|Candidate Insight Generator]]

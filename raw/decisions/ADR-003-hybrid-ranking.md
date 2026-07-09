---
type: decision
title: "ADR-003 — Hybrid Ranking System"
status: decided
date_created: 2025-05-22
date_decided: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/ranking]
---

## Context

Candidate ranking is the core value proposition of the recruitment SaaS. The system must:

1. **Accurately rank candidates** against job requirements across diverse roles and industries
2. **Be explainable** — recruiters must understand why a candidate scored high or low
3. **Be fair** — minimize bias, avoid discriminatory signals, maintain auditability
4. **Be deterministic** — the same inputs should produce consistent scores (within tolerance)
5. **Support human oversight** — AI assists but does not make final hiring decisions

No single ranking approach satisfies all these requirements. Pure semantic similarity misses exact skill matches; keyword matching misses semantic relationships; LLM-based evaluation is non-deterministic and expensive.

## Decision

**Hybrid scoring system** combining three weighted components, with **LLM-generated explanations** for recruiter consumption.

### Scoring Formula

```
final_score = (w_semantic × semantic_score) + (w_keyword × keyword_score) + (w_experience × experience_score)
```

| Component | Weight | Method | Score Range |
|---|---|---|---|
| Semantic similarity | 0.45 | Cosine similarity between resume and JD embeddings | 0.0 – 1.0 |
| Keyword matching | 0.30 | TF-IDF weighted skill/requirement overlap | 0.0 – 1.0 |
| Experience scoring | 0.25 | Rule-based years + seniority + recency scoring | 0.0 – 1.0 |

> **Note**: Weights are configurable per organization and tunable via A/B testing. Defaults above are based on initial calibration against recruiter feedback.

### Component Details

#### 1. Semantic Similarity (weight: 0.45)

```python
from pgvector.django import CosineDistance

def compute_semantic_score(candidate_embedding, job_embedding):
    """Cosine similarity between candidate resume and job description embeddings."""
    cosine_distance = CosineDistance(candidate_embedding, job_embedding)
    return 1.0 - cosine_distance  # Convert distance to similarity
```

- Captures conceptual alignment beyond exact keyword matches
- Handles synonyms, related technologies, and transferable skills
- Embeddings generated via BAAI `bge-small-en-v1.5` (384 dimensions)

#### 2. Keyword Matching (weight: 0.30)

```python
def compute_keyword_score(candidate_skills: list, job_requirements: list) -> float:
    """TF-IDF weighted overlap between candidate skills and job requirements."""
    required = set(normalize(r) for r in job_requirements if r.priority == 'required')
    preferred = set(normalize(r) for r in job_requirements if r.priority == 'preferred')
    candidate = set(normalize(s) for s in candidate_skills)

    required_match = len(required & candidate) / max(len(required), 1)
    preferred_match = len(preferred & candidate) / max(len(preferred), 1)

    return (0.7 * required_match) + (0.3 * preferred_match)
```

- Ensures exact required skills are weighted heavily
- Distinguishes required vs. preferred qualifications
- Skill normalization handles variations (e.g., "JS" → "JavaScript")

#### 3. Experience Scoring (weight: 0.25)

| Factor | Weight | Logic |
|---|---|---|
| Years of experience | 0.40 | Score based on proximity to JD requirement |
| Seniority alignment | 0.30 | Match candidate level to role level |
| Recency bonus | 0.20 | Recent relevant experience weighted higher |
| Industry match | 0.10 | Bonus for same-industry experience |

### LLM Explanation Layer

The LLM **does not influence the score** — it only generates a human-readable explanation of the computed score. This separation ensures:

- Deterministic, reproducible scoring
- Non-deterministic, natural-language explanations
- Clear audit trail (score is algorithmic, explanation is supplementary)

See [[candidate-scoring|Candidate Insight Generator]] for the full prompt template.

## Alternatives Considered

### Pure Semantic Ranking
- **Pros**: Simple, captures conceptual fit, handles novel job descriptions.
- **Cons**: Misses exact skill requirements (a Python job might surface Java candidates with similar project descriptions). No way to enforce "must-have" qualifications.
- **Verdict**: Insufficient precision for recruitment where specific skills are non-negotiable.

### LLM-as-Judge
- **Pros**: Nuanced evaluation, handles edge cases, natural language output.
- **Cons**: Non-deterministic (same input → different scores), expensive at scale ($0.01-0.05 per evaluation), bias risks from training data, slow (2-5s per candidate), not auditable.
- **Verdict**: Unacceptable for a system where fairness and consistency are requirements.

### Rule-Based Scoring Only
- **Pros**: Fully deterministic, transparent, fast, no AI costs.
- **Cons**: Brittle (every new role type needs new rules), doesn't generalize across industries, misses semantic relationships, high maintenance burden.
- **Verdict**: Too rigid for a platform serving diverse organizations and roles.

## Consequences

### Positive
- **Balanced accuracy** — Semantic handles conceptual fit; keywords enforce hard requirements; experience validates seniority
- **Explainable** — Each component score is visible; LLM provides natural language summary
- **Auditable** — Algorithmic scoring creates deterministic audit trails for compliance
- **Tunable** — Weights adjustable per organization or role type via admin panel
- **Fair** — No demographic data enters the scoring formula; bias testing via [[ranking-formula-tests|Ranking Formula Tests]]

### Negative
- **Tuning complexity** — Three components with sub-weights require calibration. Mitigated by A/B testing framework and recruiter feedback loops.
- **Weight maintenance** — Default weights may not suit all industries. Mitigated by per-org weight configuration.
- **Explanation cost** — LLM explanation adds local inference cost and latency. Mitigated by generating explanations on-demand (when recruiter views candidate) rather than pre-computing.

## Related Documents

- [[ai-pipeline|AI Pipeline]]
- [[ranking-formula-tests|Ranking Formula Tests]]
- [[candidate-scoring|Candidate Insight Generator]]
- [[semantic-matching|Semantic Matching]]
- [[ADR-002-postgresql|ADR-002 — PostgreSQL with pgvector]]

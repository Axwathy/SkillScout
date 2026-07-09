---
type: architecture
title: "AI Pipeline"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/llm, ai/embeddings, ai/scoring]
---

# [PRODUCTION] AI Pipeline

## Final AI Pipeline

1. Upload resume
2. Extract text
3. Parse structured data
4. Generate embeddings with `BAAI/bge-small-en-v1.5`
5. Store vectors in pgvector
6. Calculate semantic similarity
7. Apply deterministic rule-based scoring
8. Store the hybrid final score
9. Generate LLM insights with Qwen2.5-Coder:7B via Ollama

> **Important principle:** Math decides. AI explains.

## Overview

The AI Pipeline is the core intelligence layer of the recruitment platform. It transforms raw resume uploads into structured, scored, and explained candidate evaluations. The pipeline is fully asynchronous and designed to gracefully degrade: if any AI component fails, the system retains the candidate data and allows manual review.

Scores are computed deterministically from semantic similarity, skill matching, and experience alignment. The LLM's role is to generate human-readable summaries and contextual explanations.

## LLM Responsibilities and Restrictions

**LLM responsibilities:**
- Summaries
- Explanations
- Interview question generation
- Recruiter insights
- Optional skill extraction assistance

**LLM restrictions:**
- Cannot override scores
- Cannot reorder rankings
- Cannot alter the hybrid score
- Cannot make hiring decisions

## Processing Flow

```text
Upload -> Extract Text -> Parse Structured Data -> Generate Embeddings
    -> Store Vectors -> Calculate Similarity -> Apply Hybrid Scoring
    -> Generate LLM Insights -> Return Results
```

## Stage 1: Resume Upload and Text Extraction

| Step | Details |
|---|---|
| Trigger | Candidate uploads resume (PDF, DOCX, or plain text) |
| Storage | Raw file stored in Supabase Storage under `resumes/{org_id}/{candidate_id}/` |
| Extraction | `PyPDF2` for PDFs, `python-docx` for DOCX, plain text passthrough |
| Output | Raw text content stored in `candidates.raw_text` |
| Fallback | If extraction fails, candidate is flagged for manual review |

## Stage 2: Structured Data Parsing

The raw text is sent to Qwen2.5-Coder:7B via Ollama with a structured extraction prompt:

```python
PARSE_PROMPT = """
Extract the following from this resume:
- full_name, email, phone, location
- skills: [{ name, proficiency_level, years }]
- experience: [{ title, company, start_date, end_date, description }]
- education: [{ degree, institution, graduation_year }]
Return as JSON.
"""
```

Parsed data is stored as JSONB in `candidates.parsed_data`, enabling flexible querying without schema migration.

## Stage 3: Embedding Generation

- **Model:** `BAAI/bge-small-en-v1.5`
- **Dimensions:** 384
- **Input:** Concatenation of skills, experience summaries, and education
- **Storage:** `candidates.embedding` column (pgvector `vector(384)` type)
- **Batch processing:** Embeddings are generated in batches of up to 100 for bulk imports

## Stage 4: Similarity Calculation

Once both job and candidate embeddings exist, cosine similarity is computed:

```sql
SELECT 1 - (candidate.embedding <=> job.embedding) AS semantic_score
FROM candidate_applications application
JOIN candidates candidate ON candidate.id = application.candidate_id
JOIN jobs job ON job.id = application.job_id
WHERE application.job_id = %s
ORDER BY semantic_score DESC;
```

See [[semantic-matching|Semantic Matching]] for detailed information on indexing and query optimization.

## Stage 5: Hybrid Scoring

The final candidate score is a weighted combination of three components:

| Component | Weight | Source |
|---|---:|---|
| Semantic Score | 0.45 | Cosine similarity between candidate and job embeddings |
| Skill Match Score | 0.30 | Percentage of required skills matched (exact + fuzzy) |
| Experience Score | 0.25 | Years of relevant experience vs. job requirements |

```python
overall_score = (
    0.45 * semantic_score +
    0.30 * skill_match_score +
    0.25 * experience_score
)
```

Weights are configurable per organization and can be tuned based on hiring outcomes.

## Stage 6: LLM Insight Generation

After scoring, Qwen2.5-Coder:7B via Ollama generates a human-readable summary using the [[candidate-scoring|Candidate Insight Generator]]:

- **Strengths:** What makes this candidate a good fit
- **Gaps:** Missing skills or experience relative to the job
- **Interview suggestions:** Targeted questions based on gaps or interesting experience
- **Overall assessment:** 2-3 sentence narrative summary

The LLM receives the score as input context. It does not compute, override, reorder, or adjust the score.

## AI Components Summary

| Component | Model / Method | Purpose |
|---|---|---|
| Text Extraction | PyPDF2, python-docx | Convert resume files to plain text |
| Structured Parsing | Qwen2.5-Coder:7B via Ollama | Extract structured fields from resume text |
| Embeddings | `BAAI/bge-small-en-v1.5` | Generate vector representations for similarity |
| Hybrid Scoring | Deterministic formula | Compute objective candidate-job fit score |
| LLM Insights | Qwen2.5-Coder:7B via Ollama | Generate explanations, summaries, recruiter insights, and interview questions |

## Error Handling and Retry Logic

| Error Type | Strategy | Max Retries | Backoff |
|---|---|---:|---|
| Ollama/BAAI rate limit (429) | Exponential backoff | 5 | 2^n seconds |
| Ollama/BAAI server error (5xx) | Retry with jitter | 3 | 5s base |
| Text extraction failure | Flag for manual review | 1 | none |
| Embedding generation failure | Retry, then skip scoring | 3 | 10s base |
| LLM insight failure | Retry, serve score without summary | 2 | 5s base |

All retries are managed by Celery's built-in retry mechanism with `autoretry_for` and `retry_backoff` settings. Failed tasks after max retries are sent to the dead letter queue for manual inspection.

## Performance Considerations

- **Batch processing:** Bulk resume imports process embeddings in batches of 100 to maximize local inference throughput.
- **Caching:** Job embeddings are cached in Redis (TTL: 24h) since they change infrequently. Candidate embeddings are computed once and stored persistently.
- **Async by default:** All AI operations run in Celery workers, keeping the API responsive. The frontend polls task status via `/api/v1/tasks/{task_id}/`.
- **Cost management:** Token usage and local inference time are tracked per organization for billing and capacity planning. Embeddings are cheaper than LLM inference, so the pipeline is optimized to minimize LLM invocations.
- **Timeout guards:** Each pipeline stage has an independent timeout (extraction: 30s, parsing: 60s, embedding: 30s, scoring: 10s, insights: 90s).

## Related Documents

- [[ai-responsibilities|AI Responsibilities]]
- [[semantic-matching|Semantic Matching]]
- [[candidate-scoring|Candidate Insight Generator]]
- [[embedding-tests|Embedding Model Tests]]
- [[async-task-flow|Async Task Flow]]
- [[system-overview|System Overview]]

## Hybrid Ranking Formula

`final_score = 0.45 * semantic_similarity + 0.30 * skill_match + 0.25 * experience_match`

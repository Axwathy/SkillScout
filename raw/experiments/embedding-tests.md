---
type: experiment
title: "Embedding Model Tests"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/ml, ai/llm, research]
---

# Embedding Model Tests

This document describes the experiment plan for evaluating and comparing embedding models for use in the AI Recruitment SaaS semantic matching pipeline. The chosen model will power candidate-job similarity scoring via [[pgvector-notes|pgvector Notes]] cosine similarity queries.

See also: [[semantic-matching|Semantic Matching]], [[pgvector-notes|pgvector Notes]], [[ai-pipeline|AI Pipeline]]

---

## Objective

Select the embedding model that provides the best trade-off of **relevance accuracy**, **latency**, **cost**, and **dimension efficiency** for matching candidate resumes against job descriptions.

---

## Models Under Evaluation

| Model | Provider | Dimensions | Context Window | Cost (per 1M tokens) | Notes |
|-------|----------|------------|----------------|----------------------|-------|
| `bge-small-en-v1.5` | BAAI (open source) | 384 | 512 tokens | Self-hosted | **Current MVP default** |
| `text-embedding-3-small` | OpenAI | 1536 | 8,191 tokens | $0.02 | Managed fallback candidate |
| `text-embedding-3-large` | OpenAI | 3072 | 8,191 tokens | $0.13 | Higher accuracy, 6.5x cost |
| `text-embedding-3-large` (reduced) | OpenAI | 1024 (via `dimensions` param) | 8,191 tokens | $0.13 | Reduced dimensions, same cost |
| `bge-large-en-v1.5` | BAAI (open source) | 1024 | 512 tokens | Self-hosted | Top open-source model on MTEB |
| `e5-large-v2` | Microsoft (open source) | 1024 | 512 tokens | Self-hosted | Strong performance, MIT license |
| `nomic-embed-text-v1.5` | Nomic AI | 768 | 8,192 tokens | Self-hosted or API | Long context, Matryoshka support |

---

## Test Methodology

### Step 1: Create Golden Test Set

Build a test set of **50 job-candidate pairs** with human relevance labels.

| Component | Details |
|-----------|---------|
| **Jobs** | 10 diverse job descriptions (junior to senior, different domains: engineering, marketing, data science, product, design) |
| **Candidates** | 5 candidates per job with varying relevance levels |
| **Labels** | Human-assigned relevance score (0-4 scale): 0 = irrelevant, 1 = tangentially related, 2 = somewhat relevant, 3 = strong match, 4 = excellent match |
| **Labelers** | 2 independent labelers per pair, with inter-rater reliability check (Cohen's kappa ≥ 0.7) |

### Step 2: Generate Embeddings

For each model:

1. Embed all 10 job descriptions
2. Embed all 50 candidate resumes (parsed text, not raw PDF)
3. Store embeddings with metadata (model name, dimensions, generation timestamp)

**Preprocessing**:
- Truncate to model's context window
- Job text: title + description + requirements (concatenated)
- Candidate text: skills + experience + summary (structured from parsed resume)

### Step 3: Calculate Similarity

```python
# For each (job, candidate) pair:
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

# Score = cosine_similarity(job_embedding, candidate_embedding)
```

### Step 4: Evaluate Against Human Labels

| Metric | Description | Target |
|--------|-------------|--------|
| **Precision@5** | Of the top 5 candidates returned, how many are truly relevant (label ≥ 3)? | ≥ 0.80 |
| **Recall@5** | Of all truly relevant candidates, how many appear in the top 5? | ≥ 0.70 |
| **NDCG@10** | Normalized Discounted Cumulative Gain — measures ranking quality with position weighting | ≥ 0.85 |
| **Spearman's ρ** | Rank correlation between cosine similarity scores and human relevance labels | ≥ 0.70 |
| **Mean Reciprocal Rank (MRR)** | Average reciprocal rank of the first relevant candidate | ≥ 0.80 |

### Step 5: Measure Operational Metrics

| Metric | Measurement Method |
|--------|-------------------|
| **Latency (single embed)** | Average time to embed one document (100 runs, warm cache) |
| **Latency (batch embed)** | Time to embed 50 documents in one API call |
| **Cost per 1K embeddings** | Token count × price per token × 1000 |
| **Storage per embedding** | Dimensions × 4 bytes (float32) |
| **pgvector query time** | Average cosine similarity search against 10K vectors |

---

## Dimension Trade-Off Analysis

OpenAI's `text-embedding-3-large` supports dimension reduction via the `dimensions` parameter. Test the following:

| Dimensions | Storage (per vector) | Expected Accuracy | Query Speed |
|------------|---------------------|-------------------|-------------|
| 3072 (full) | 12,288 bytes | Baseline (100%) | Slowest |
| 1536 | 6,144 bytes | ~98% of full | Moderate |
| 1024 | 4,096 bytes | ~95% of full | Fast |
| 512 | 2,048 bytes | ~90% of full | Fastest |
| 256 | 1,024 bytes | ~80% of full | Very fast |

> **Hypothesis**: 1024 dimensions will provide the best accuracy-efficiency trade-off for our use case, where the semantic distinction between candidates is coarser than in academic benchmarks.

---

## Self-Hosted Model Evaluation

For BGE and E5 models, additional considerations:

| Factor | Assessment |
|--------|-----------|
| **Hosting cost** | GPU instance (T4 minimum): ~$0.50/hr on GCP/AWS |
| **Throughput** | Batch size optimization needed for production latency |
| **Context limitation** | 512 tokens may require chunking long resumes |
| **Maintenance** | Model serving infrastructure (FastAPI + ONNX or HuggingFace Inference) |
| **Privacy** | Data never leaves our infrastructure — advantage for compliance |

### Break-Even Analysis

At what volume does self-hosting become cheaper than OpenAI API?

```
OpenAI cost = (tokens_per_month / 1M) × $0.02
Self-hosted cost = GPU_hours × $0.50 + maintenance_hours × $50

Break-even ≈ 50M tokens/month (~25K resume embeddings)
```

---

## Results

> ⚠️ **Status**: Experiment not yet started. Results will be filled after execution.

### Accuracy Results

| Model | Precision@5 | Recall@5 | NDCG@10 | Spearman's ρ | MRR |
|-------|-------------|----------|---------|--------------|-----|
| `bge-small-en-v1.5` | — | — | — | — | — |
| `text-embedding-3-small` | — | — | — | — | — |
| `text-embedding-3-large` | — | — | — | — | — |
| `text-embedding-3-large` (1024d) | — | — | — | — | — |
| `bge-large-en-v1.5` | — | — | — | — | — |
| `e5-large-v2` | — | — | — | — | — |
| `nomic-embed-text-v1.5` | — | — | — | — | — |

### Operational Results

| Model | Latency (single) | Latency (batch 50) | Cost/1K | Storage/vector |
|-------|-------------------|---------------------|---------|----------------|
| `bge-small-en-v1.5` | — | — | — | — |
| `text-embedding-3-small` | — | — | — | — |
| `text-embedding-3-large` | — | — | — | — |
| `bge-large-en-v1.5` | — | — | — | — |
| `e5-large-v2` | — | — | — | — |
| `nomic-embed-text-v1.5` | — | — | — | — |

### Recommendation

> To be written after experiments are complete. Include: selected model, rationale, configuration parameters, and migration plan.

---

## Next Steps

1. [ ] Recruit 2 labelers and calibrate on 5 practice pairs
2. [ ] Create 10 job descriptions spanning target domains
3. [ ] Source or generate 50 candidate resumes with known quality levels
4. [ ] Run embedding generation scripts for all models
5. [ ] Calculate metrics and populate results tables
6. [ ] Write recommendation and present to team

---
type: sprint
title: "Master Roadmap & MVP Strategy"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/strategy, sprints]
---

# Master Roadmap

## Build Order (MVP Strategy)
We've pivoted to a more realistic phased approach, avoiding an overly AI-heavy initial release.

### Phase 1: ATS Foundation
Basic Applicant Tracking System. Job posting, resume uploads, candidate tracking, pipeline board.

### Phase 2: Rule-Based Scoring
Implement keyword and experience-based scoring before adding semantic matching.

### Phase 3: Embeddings
Introduce `pgvector` and `BAAI/bge-small-en-v1.5` for semantic similarity search.

### Phase 4: LLM Assistance
Integrate Qwen2.5-Coder:7B via Ollama for LLM-powered candidate summaries, score explanations, recruiter insights, and interview generation.
*Rule: Math decides. AI explains. The LLM does not decide scores, reorder rankings, or make hiring decisions.*

---
type: concept
name: "Semantic Search"
aliases: ["Candidate Semantic Search", "Vector Candidate Search"]
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/feature, ai/embeddings, ai/nlp, recruitment/sourcing]
---

# Semantic Search

## Definition

Semantic Search lets recruiters find candidates using natural-language descriptions rather than exact keyword matching. It relies on embeddings and vector search to match meaning across resumes and job requirements.

## Relevance to AI Recruitment

Search is a high-frequency recruiter workflow. It should support natural-language candidate discovery while keeping ranking explainable and compatible with the [[Hybrid Ranking System]].

## Current State

The source feature specification lives at `raw/features/semantic-search.md`. The requested design system places semantic search in the Candidates page and global search workflows.

## Key Players

Internal product feature using the selected embedding architecture.

## Our Position

Use a prominent candidate search input with filters for job, stage, score range, application date, and source. Results should show why a candidate matched without implying that the LLM made a hiring decision.

## Source References

- `raw/features/semantic-search.md`
- [[Lumina Nexus UI UX Foundation]]
- [[Hybrid Ranking System]]

## Open Questions

- Should semantic search results be blended with keyword search in the first MVP release?

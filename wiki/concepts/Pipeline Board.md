---
type: concept
name: "Pipeline Board"
aliases: ["Hiring Pipeline", "Recruitment Kanban"]
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/feature, product/ux, recruitment/screening]
---

# Pipeline Board

## Definition

The Pipeline Board is the recruiter-facing Kanban interface for moving candidate applications through hiring stages such as Applied, Screening, Technical, HR, Offer, Hired, and Rejected.

## Relevance to AI Recruitment

The board is where deterministic ranking, recruiter judgment, and workflow execution meet. Candidate order should remain score-driven by default, while stage changes remain explicit recruiter actions.

## Current State

The source feature specification lives at `raw/features/pipeline-board.md`. The Lumina Nexus layout direction is refined in [[Lumina Nexus UI UX Foundation]].

## Key Players

Internal product feature.

## Our Position

Use desktop-optimized horizontal columns, compact candidate cards, quick actions, stage counts, and explicit confirmation for terminal transitions.

## Source References

- `raw/features/pipeline-board.md`
- [[Lumina Nexus UI UX Foundation]]
- [[Hybrid Ranking System]]

## Open Questions

- Should the MVP support configurable stage names, or use fixed stages until workflow analytics mature?

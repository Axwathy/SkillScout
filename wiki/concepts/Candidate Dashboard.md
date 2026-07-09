---
type: concept
name: "Candidate Dashboard"
aliases: ["Candidate Profile", "Candidate Detail View"]
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/feature, product/ux, recruitment/screening]
---

# Candidate Dashboard

## Definition

The Candidate Dashboard is the recruiter-facing profile view for reviewing a candidate's resume, deterministic score breakdown, AI-generated summary, strengths, gaps, interview recommendations, and pipeline history.

## Relevance to AI Recruitment

This is the main decision-support screen for recruiters. It must make the [[Hybrid Ranking System]] transparent while keeping LLM-generated analysis clearly separated from score calculation and ranking.

## Current State

The source feature specification lives at `raw/features/candidate-dashboard.md`. The layout direction is refined in [[Lumina Nexus UI UX Foundation]].

## Key Players

Internal product feature.

## Our Position

Use a dense desktop layout for recruiters: score and actions on the left, resume evidence in the center, and AI/context panels on the right.

## Source References

- `raw/features/candidate-dashboard.md`
- [[Lumina Nexus UI UX Foundation]]
- [[Hybrid Ranking System]]

## Open Questions

- How much AI-generated feedback should be exposed to candidates, if any?

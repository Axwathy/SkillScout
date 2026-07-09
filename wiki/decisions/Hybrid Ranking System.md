---
type: decision
title: "Hybrid Ranking System"
status: decided
date_created: 2026-05-22
date_decided: 2025-05-22
superseded_by: ""
tags: [product/architecture, ai/ranking, recruitment/matching]
---

# Hybrid Ranking System

## Context

Candidate ranking must balance relevance, explainability, fairness, determinism, and recruiter trust. Pure semantic matching, pure keyword matching, and LLM-as-judge each fail at least one of those requirements.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| Hybrid deterministic scoring | Balanced, explainable, auditable | Needs calibration |
| Pure semantic ranking | Simple and flexible | Misses hard requirements |
| LLM-as-judge | Nuanced explanations | Non-deterministic, harder to audit, higher risk |
| Rule-only scoring | Transparent and cheap | Brittle across roles |

## Decision

Use deterministic hybrid scoring with default weights of 45% semantic similarity, 30% skill matching, and 25% experience scoring. The LLM may explain the result but must not compute, override, or reorder scores.

## Implications

- Recruiters can inspect sub-scores and explanations.
- Score versions must be stored for auditability.
- Calibration experiments should test weights against human recruiter judgments.

## Review Triggers

- Recruiter relevance feedback consistently contradicts rankings.
- Bias audits identify disparate impact in component scores.
- A specific segment requires different default weights.

## Source References

- `raw/decisions/ADR-003-hybrid-ranking.md`
- `raw/experiments/ranking-formula-tests.md`

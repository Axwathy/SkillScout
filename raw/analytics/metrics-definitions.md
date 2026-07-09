---
type: analytics
title: "Analytics Metrics Definitions"
date_created: 2026-05-22
date_updated: 2026-05-22
tags: [recruitment/analytics, product/analytics]
---

# Analytics Metrics Definitions

This document defines the core metrics used by the recruitment analytics dashboard.

## Funnel Metrics

| Metric | Definition |
|---|---|
| Applications | Number of candidate applications created in the selected period |
| Screened | Applications moved out of the initial applied/new stage |
| Interviewed | Applications that reached any interview stage |
| Offers | Applications that reached offer stage |
| Hires | Applications marked hired |
| Conversion Rate | Stage count divided by prior stage count |

## Velocity Metrics

| Metric | Definition |
|---|---|
| Time to Screen | Time from application creation to first screening transition |
| Time to Interview | Time from application creation to first interview stage |
| Time to Offer | Time from application creation to offer stage |
| Time to Hire | Time from application creation to hired status |
| Time in Stage | Duration between entering and leaving a pipeline stage |

## Quality Metrics

| Metric | Definition |
|---|---|
| Score Distribution | Distribution of deterministic hybrid scores for candidates in a job |
| Source Quality | Average score and downstream conversion by candidate source |
| Recruiter Activity | Count of stage moves, notes, interviews, and decisions by user |

## Compliance Notes

- Demographic metrics require explicit legal review and candidate consent.
- Bias auditing should use aggregate analysis and should never expose protected-class information to ordinary recruiter workflows.
- AI score metrics must preserve the scoring algorithm version for auditability.

## Related Documents

- [[analytics-dashboard|Analytics Dashboard]]
- [[AI Hiring Regulations]]
- [[ADR-003-hybrid-ranking|ADR-003 — Hybrid Ranking System]]

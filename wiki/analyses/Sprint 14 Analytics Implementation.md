---
type: analysis
title: "Sprint 14 Analytics Implementation"
analysis_type: framework
date_created: 2026-06-11
date_updated: 2026-06-12
source_count: 3
tags: [product/feature, product/analytics, recruitment/analytics, dashboard, sprint/implemented]
---

# Sprint 14 Analytics Implementation

## Methodology

Implemented Sprint 14 from the [[sprint-14-analytics|Sprint 14 Analytics Dashboard plan]] using the metric formulas in [[metrics-definitions|Analytics Metrics Definitions]]. `raw/` stays immutable; this page records the implemented product state and the phase split used during delivery.

## Phased Delivery

- **14A completed:** Overview KPIs, pipeline funnel, time-to-hire, date range presets, Recharts visualizations, recruiter-scoped analytics APIs, and Analytics navigation.
- **14B completed:** Short-lived API caching, daily analytics snapshots, source effectiveness, team activity leaderboard, KPI sparklines/trends, CSV export, and chart PNG export.

## What Shipped

**Backend - `apps.analytics`:**
- `DailyAnalyticsSnapshot` stores daily computed analytics payloads by organization and date.
- Cached metric helpers wrap overview, funnel, time-to-hire, source effectiveness, and team activity endpoints with a 60-second cache TTL.
- `compute_dashboard()` returns the full dashboard payload in one request for the frontend.
- Source effectiveness groups applications by `Application.source`, counting applications, offers reached, hires, conversion rate, and future-compatible cost-per-hire.
- Team activity groups `ApplicationHistory` by recruiter and reports status updates, distinct candidates processed, interviews conducted, hires, and average first-response hours.
- CSV export supports overview, funnel, time-to-hire, sources, and team activity.
- `precompute_daily_analytics_snapshots` Celery task can create/update daily snapshots for all organizations.

**Application source capture:**
- Added `Application.source` choices: direct, job board, LinkedIn, referral, agency, other.
- Public applications default to direct but can capture source from public job URLs such as `?source=linkedin`.

**Frontend:**
- `/dashboard/analytics` now uses the bundled dashboard endpoint.
- Added KPI trend badges and small sparklines for application and hire series.
- Added source effectiveness chart/table and recruiter team activity table.
- Added CSV export buttons and PNG chart export buttons for chart panels.

## Verification

- Backend Ruff: passed.
- Django system check: passed.
- Migration drift check: passed.
- Analytics + jobs API focused tests: 22 passed.
- Frontend lint: passed.
- Frontend type-check: passed.
- Frontend production build: passed.

## Deferred / Out of Scope

- Materialized SQL views and warehouse-style analytics tables; current snapshots are JSON payload snapshots.
- Scheduled Celery beat configuration; the task exists, but deployment scheduling is not wired here.
- Cost-per-source input management; `cost_per_hire` remains null until source spend data exists.
- Realtime analytics updates; dashboard still uses request/refresh semantics.
- Bulk analytics actions are planned for [[sprint-15-bulk-operations|Sprint 15 Bulk Operations]].

## Source References

- [[sprint-14-analytics|Sprint 14 Plan]]
- [[metrics-definitions|Analytics Metrics Definitions]]
- [[Sprint 9 Hiring Pipeline Implementation]]

## Open Questions

- Should recruiters be able to manually edit application source after intake?
- Should source tracking also read `utm_source` as an alias for `source`?
- Should daily snapshots be retained forever, or rolled up after 12-24 months?

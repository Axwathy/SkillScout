---
type: feature
title: "Analytics Dashboard"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, analytics, recruitment/metrics]
---

# Analytics Dashboard

## Overview

The Analytics Dashboard provides recruitment leaders with data-driven insights into their hiring process. It visualizes key metrics, funnel conversion rates, and hiring velocity across jobs and time periods. This feature transforms raw pipeline data into actionable intelligence for optimizing recruitment strategy.

## Purpose

Without analytics, recruitment teams operate on intuition. The Analytics Dashboard surfaces patterns in the hiring funnel — identifying bottlenecks, measuring source effectiveness, and tracking time-to-hire — enabling data-informed decisions that improve hiring outcomes and reduce costs.

## User Flow

1. **Access Dashboard** — Navigate to Analytics from the main sidebar. Dashboard loads with current month's data.
2. **View KPI Cards** — Top row shows headline metrics: open positions, total candidates, avg time-to-hire, offer acceptance rate.
3. **Explore Funnel** — Interactive funnel chart shows conversion rates between each pipeline stage.
4. **Analyze Trends** — Time-series charts display metrics over customizable date ranges.
5. **Drill Down** — Click any metric to drill into job-specific or source-specific breakdowns.
6. **Export Reports** — Download charts as PNG or raw data as CSV for stakeholder reporting.

## Key Metrics

### KPI Cards (Top Row)

| Metric | Calculation | Update Frequency |
|--------|-------------|-----------------|
| Open Positions | Count of jobs with `status = 'published'` | Real-time |
| Active Candidates | Candidates in non-terminal stages | Real-time |
| Avg Time-to-Hire | Mean days from `Applied` to `Hired` stage | Daily aggregation |
| Offer Acceptance Rate | `(Hired / Offer Extended) × 100` | Daily aggregation |
| Candidates This Month | New candidates created in current month | Real-time |
| AI Score Average | Mean overall AI score across all scored candidates | Daily aggregation |

### Funnel Chart

Visualizes the recruitment funnel as a stepped horizontal bar chart:

```
Applied          ████████████████████████████████████  250
Screening        ██████████████████████████            180  (72%)
Phone Interview  ████████████████████                  120  (67%)
Technical        ████████████████                       95  (79%)
Final Interview  ██████████                             60  (63%)
Offer            ██████                                 35  (58%)
Hired            ████                                   22  (63%)
```

Each bar shows:
- Absolute candidate count
- Conversion rate from previous stage (percentage)
- Click to filter candidate list by stage

### Time-Series Charts

- **Hiring Velocity** — Candidates hired per week/month over time
- **Application Volume** — New applications per day/week with trend line
- **Score Distribution** — Histogram of AI scores across all candidates
- **Time in Stage** — Average days candidates spend in each stage over time

### Source Effectiveness Table

| Source | Candidates | Avg Score | Conversion to Hire | Cost per Hire |
|--------|-----------|-----------|-------------------|---------------|
| Direct Apply | — | — | — | — |
| Referral | — | — | — | — |
| LinkedIn | — | — | — | — |
| Job Board | — | — | — | — |
| Agency | — | — | — | — |

## Component Architecture

### Date Range Selector

- Preset ranges: Today, This Week, This Month, This Quarter, This Year
- Custom date range picker with start/end date selection
- Comparison mode: compare current period vs. previous period

### Chart Components

All charts use a consistent charting library (Recharts for React):

- **Funnel Chart** — Custom SVG funnel with hover tooltips
- **Line Charts** — Time-series with configurable granularity (day/week/month)
- **Bar Charts** — Grouped or stacked for comparative metrics
- **Pie Charts** — Source distribution and stage breakdown
- **Histogram** — Score distribution with configurable bin sizes

### Filter Bar

| Filter | Description |
|--------|-------------|
| Job | Filter metrics by specific job posting |
| Department | Filter by department/team |
| Recruiter | Filter by assigned recruiter |
| Date Range | Custom or preset time periods |
| Source | Filter by candidate source |

## Backend Architecture

### Aggregation Queries

Metrics are computed via PostgreSQL aggregation queries with materialized views for performance:

```sql
-- Funnel conversion rates for a job
SELECT 
    ps.name AS stage_name,
    ps.order AS stage_order,
    COUNT(DISTINCT h.application_id) AS application_count
FROM pipeline_stages ps
LEFT JOIN candidate_stage_history h ON h.to_stage_id = ps.id
WHERE h.moved_at BETWEEN :start_date AND :end_date
GROUP BY ps.name, ps.order
ORDER BY ps.order;
```

### Caching Strategy

| Data Type | Cache TTL | Invalidation |
|-----------|-----------|-------------|
| KPI Cards | 5 minutes | On pipeline transition |
| Funnel Data | 15 minutes | On pipeline transition |
| Time-Series | 1 hour | Time-based expiry |
| Source Table | 1 hour | On new candidate creation |

Cache is implemented via Redis with Django cache framework.

### Export API

- `GET /api/v1/analytics/export/?format=csv&metric=funnel&date_range=...`
- `GET /api/v1/analytics/export/?format=png&chart=hiring_velocity&date_range=...`

## Permissions

- **Admin** — Full access to all analytics, all jobs, all recruiters
- **Recruiter** — Access to analytics for assigned jobs only
- **Viewer** — Read-only access to shared dashboards (future)

## Future Improvements

- **Predictive Analytics** — ML model predicting time-to-fill based on historical data
- **Custom Dashboards** — Drag-and-drop dashboard builder for custom metric views
- **Automated Reports** — Scheduled email reports (weekly hiring summary)
- **Benchmark Comparisons** — Compare metrics against industry benchmarks
- **Diversity Metrics** — Optional demographic tracking for DEI reporting

## Related Pages

- [[sprint-14-analytics|Sprint 14 — Analytics Dashboard]] — Implementation sprint details
- [[pipeline-board|Pipeline Board]] — Source of pipeline transition data
- [[candidate-api|Candidate API]] — Candidate data endpoints
- [[jobs-api|Jobs API]] — Job posting data for per-job analytics

---
title: "Sprint 14 — Analytics Dashboard"
sprint_number: 14
status: planned
start_date: 2026-12-01
end_date: 2026-12-11
story_points_planned: 42
story_points_completed: 0
tags:
  - sprint
  - analytics
  - metrics
  - dashboard
---

# Sprint 14 — Analytics Dashboard

## 🎯 Sprint Goal

> **Primary Objective:** Build a recruitment analytics dashboard with funnel visualization, time-to-hire metrics, source effectiveness tracking, and key performance indicators for data-driven hiring decisions.
>
> **Success Criteria:** Recruiters and hiring managers can view pipeline funnel conversion rates, average time-to-hire, source effectiveness comparison, and team activity metrics. All charts update in real-time and support date range filtering.

---

## 📋 Planned Features

- [ ] Pipeline funnel visualization with conversion rates between stages
- [ ] Time-to-hire metrics: average, median, by department, by job
- [ ] Source effectiveness: applications, hires, and cost-per-hire by referral source
- [ ] Team activity metrics: interviews conducted, candidates processed, response time

---

## ⚙️ Backend Tasks

- [ ] Build analytics aggregation service with optimized SQL queries using Django ORM annotations
- [ ] Create `GET /api/v1/analytics/funnel/{job_id}/` returning stage-by-stage conversion rates
- [ ] Create `GET /api/v1/analytics/time-to-hire/` with filters: date range, department, job
- [ ] Create `GET /api/v1/analytics/sources/` tracking application sources and their conversion rates
- [ ] Create `GET /api/v1/analytics/team-activity/` with per-recruiter metrics
- [ ] Create `GET /api/v1/analytics/overview/` returning KPI summary cards data
- [ ] Implement date range filtering across all analytics endpoints
- [ ] Add materialized view or caching layer for expensive aggregation queries
- [ ] Create periodic Celery task to pre-compute daily analytics snapshots
- [ ] Write tests: aggregation accuracy, date filtering, permission scoping by org

See also: [[analytics-dashboard|Analytics Dashboard]]

---

## 🖥️ Frontend Tasks

- [ ] Build Analytics Dashboard page with responsive grid layout for chart panels
- [ ] Create Funnel Chart component using Recharts: horizontal funnel with conversion percentages
- [ ] Build Time-to-Hire chart: bar chart by department/job with average line overlay
- [ ] Create Source Effectiveness comparison: grouped bar chart (applications vs hires vs cost)
- [ ] Build KPI Metric Cards: total applicants, open positions, average time-to-hire, offer acceptance rate
- [ ] Implement Date Range Picker with presets (last 7 days, 30 days, 90 days, custom)
- [ ] Add export functionality: download charts as PNG, data as CSV
- [ ] Create Team Leaderboard component: recruiter rankings by candidates processed
- [ ] Build trend sparklines on metric cards showing week-over-week changes

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Aggregation query performance on large datasets | High | Materialized views, pre-computed snapshots, DB indexes | 🟡 In Progress |
| Source tracking requires integration with ATS imports | Medium | Manual source field initially, auto-detection later | 🟢 Planned |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] No real-time dashboard updates — requires page refresh for new data
- [ ] Source tracking is manual — needs automated UTM/referrer detection

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-09-pipeline]] — pipeline transition data feeds funnel analytics
- **References:** [[analytics-dashboard|Analytics Dashboard]], [[system-overview|System Overview]]
- **Next Sprint:** [[sprint-15-bulk-operations]] — Bulk Operations & Batch Processing

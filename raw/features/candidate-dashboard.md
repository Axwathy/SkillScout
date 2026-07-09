---
type: feature
title: "Candidate Dashboard"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, recruitment/screening, frontend]
---

# Candidate Dashboard

## Overview

The Candidate Dashboard provides a comprehensive, single-page view of an individual candidate. It aggregates AI-generated scores, parsed resume data, pipeline history, interview feedback, and actionable insights into a unified interface. This is the primary screen recruiters use to evaluate and make decisions about candidates.

## Purpose

Recruiters need a centralized view that eliminates context-switching between multiple tools and tabs. The Candidate Dashboard consolidates every piece of candidate intelligence — from raw resume data to AI-powered scoring breakdowns — into a single, scannable interface that supports rapid decision-making.

## User Flow

1. **Navigate** — Recruiter clicks a candidate name from the [[pipeline-board|Pipeline Board]], search results, or candidate list.
2. **Profile Load** — Dashboard fetches aggregated candidate data in a single API call.
3. **Review Profile** — Recruiter scans the profile header, AI score badge, and summary card.
4. **Explore Details** — Drill into score breakdown chart, parsed resume sections, or pipeline history.
5. **Review Feedback** — Read interview notes and feedback from other team members.
6. **Take Action** — Use action buttons to advance, reject, schedule an interview, or add notes.

## Component Architecture

### Profile Header

The top section displays at-a-glance candidate information:

| Element | Description |
|---------|-------------|
| Avatar | Generated initials avatar or uploaded photo |
| Full Name | Candidate's parsed full name |
| Current Title | Most recent job title from parsed resume |
| Email / Phone | Contact details with click-to-copy |
| Score Badge | Color-coded overall AI score (0–100) |
| Pipeline Stage | Current stage with time-in-stage indicator |
| Applied Job | Link to the job posting for the selected application |

### AI Score Breakdown

A radar or bar chart visualizing the multi-dimensional AI score:

- **Skill Match** (0–100) — How well candidate skills align with job requirements
- **Experience Relevance** (0–100) — Relevance and depth of work experience
- **Semantic Similarity** (0–100) — Vector similarity between resume and job description
- **Overall Score** — Weighted composite: 45% semantic similarity, 30% skill match, 25% experience relevance

Each dimension is clickable, revealing the LLM-generated explanation for that sub-score.

### Parsed Resume Accordion

Collapsible sections displaying structured data extracted by the [[resume-parser|Resume Parser]]:

- **Summary** — Professional summary / objective statement
- **Experience** — Timeline of positions with company, dates, and achievements
- **Education** — Degrees, institutions, and graduation dates
- **Skills** — Categorized skill tags (technical, soft, tools)
- **Certifications** — Professional certifications with dates
- **Languages** — Language proficiencies

### AI Summary Card

A concise, LLM-generated narrative summary of the candidate's fit for the role. Includes:

- Key strengths relevant to the position
- Potential gaps or concerns
- Recommended interview focus areas
- Comparison to the ideal candidate profile

### Pipeline Timeline

A vertical timeline showing the candidate's journey through hiring stages:

- Stage transitions with timestamps
- Notes added at each transition
- Duration at each stage
- Who moved the candidate (recruiter attribution)

### Interview Feedback Section

Aggregated feedback from all interviewers:

- Individual interviewer scores and comments
- Structured feedback forms (communication, technical, culture fit)
- Consensus indicator (agree/disagree visualization)

### Action Buttons

| Action | Description | Trigger |
|--------|-------------|---------|
| Advance | Move to next pipeline stage | Updates stage via [[pipeline-api|Pipeline API]] |
| Reject | Mark candidate as rejected with reason | Sends rejection notification |
| Schedule Interview | Open scheduling modal | Integrates with calendar |
| Add Note | Attach a note to candidate profile | Saved to candidate timeline |
| Download Resume | Download original uploaded file | Serves from private Supabase Storage through a backend-signed URL |

## Backend Integration

The dashboard is powered by a single aggregated endpoint from the [[candidate-api|Candidate API]]:

```
GET /api/v1/candidates/{candidate_id}/?application_id={application_id}&include=scores,parsed_data,pipeline_history,feedback
```

This endpoint joins data from multiple tables to minimize frontend requests:

- `candidates` — Core profile data
- `parsed_resumes` — JSONB parsed data
- `candidate_applications` — Job-specific application and current stage
- `candidate_scores` — Application-level AI scoring results with explanations
- `candidate_stage_history` — Stage history with timestamps
- `interview_feedback` — Feedback entries from interviewers

Response is cached with a 60-second TTL and invalidated on any candidate update.

## Responsive Design

- **Desktop** (1200px+) — Full three-column layout: profile header spans top, left column for scores and actions, center for resume, right for timeline and feedback.
- **Tablet** (768–1199px) — Two-column layout with stacked sections.
- **Mobile** (< 768px) — Single-column with tabbed navigation between sections.

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation for score breakdown and accordion sections
- Screen reader support for AI score explanations
- High-contrast mode for score indicators

## Related Pages

- [[candidate-api|Candidate API]] — Backend API powering the dashboard
- [[pipeline-board|Pipeline Board]] — Kanban view linking to individual dashboards
- [[ai-pipeline|AI Pipeline]] — AI scoring and parsing workflow
- [[resume-parser|Resume Parser]] — Resume data extraction feature
- [[sprint-10-candidate-dashboard|Sprint 10 — Candidate Dashboard]] — Implementation sprint

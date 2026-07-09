---
type: feature
title: "Pipeline Board"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, recruitment/pipeline, frontend]
---

# Pipeline Board

## Overview

The Pipeline Board is a Kanban-style drag-and-drop interface for managing candidates through configurable hiring stages. It provides a visual, interactive view of the entire recruitment funnel for a given job posting, enabling recruiters to move candidates between stages with intuitive gestures.

## Purpose

Visual pipeline management is critical for recruitment workflows. The Pipeline Board transforms the abstract hiring process into a tangible, manipulable interface where recruiters can see at a glance where every candidate stands, identify bottlenecks, and take action — all without navigating away from the board.

## User Flow

1. **Select Job** — Recruiter selects a job posting from the job selector dropdown.
2. **View Board** — Pipeline loads with all stages as columns, candidates as cards within each column.
3. **Scan & Filter** — Use search bar or filters to find specific candidates. Stage headers show candidate counts.
4. **Drag & Drop** — Drag a candidate card from one stage column to another. A confirmation modal appears for critical transitions (e.g., rejection).
5. **Add Notes** — On drop, an optional notes modal allows the recruiter to document the reason for the move.
6. **Real-time Updates** — Other team members see the move reflected instantly via WebSocket.

## Pipeline Stages

Default stages (configurable per organization):

| Order | Stage Name | Type | Description |
|-------|-----------|------|-------------|
| 1 | Applied | `initial` | New applications land here |
| 2 | Screening | `review` | Initial resume review |
| 3 | Phone Interview | `interview` | First-round phone screen |
| 4 | Technical Interview | `interview` | Technical assessment |
| 5 | Final Interview | `interview` | Final-round with hiring manager |
| 6 | Offer | `decision` | Offer extended |
| 7 | Hired | `terminal` | Candidate accepted and hired |
| 8 | Rejected | `terminal` | Candidate rejected at any stage |

Organizations can add, rename, reorder, or remove non-terminal stages through the stage configuration modal.

## Component Architecture

### Stage Columns

- **Header** — Stage name, candidate count badge, average time-in-stage indicator
- **Column Body** — Scrollable list of candidate cards, sorted by AI score (descending) by default
- **Column Footer** — "Load more" pagination for stages with many candidates
- **Drop Zone** — Visual highlight when a card is dragged over a valid target column

### Candidate Cards

Each card displays a compact summary:

- Candidate name and current title
- AI score badge (color-coded: green ≥ 80, yellow ≥ 60, red < 60)
- Time in current stage (e.g., "3 days")
- Source indicator (direct apply, referral, imported)
- Quick-action icons (view profile, schedule, reject)

### Drag-and-Drop Interaction

- Built with `@dnd-kit/core` (React) for accessible, performant drag interactions
- Visual feedback: card lifts with shadow, source column dims, valid targets highlight
- Invalid drops (e.g., moving to the same stage) snap back with animation
- Optimistic UI update with rollback on API failure

### Stage Configuration Modal

Accessible via a gear icon on the board header:

- Add new custom stages with name and type
- Reorder stages via drag-and-drop
- Rename existing stages
- Delete stages with candidate reassignment dialog
- Set stage-specific automation rules (future)

### Bulk Actions

When multiple candidates are selected (via checkboxes):

- Move all selected to a target stage
- Reject all selected with a shared reason
- Export selected candidate data as CSV

## Backend Architecture

### API Endpoints

All endpoints are documented in [[pipeline-api|Pipeline API]]:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/pipeline/board/{job_id}/` | Full board data for a job |
| `POST` | `/api/v1/pipeline/move/` | Move a candidate application between stages |
| `GET` | `/api/v1/pipeline/stages/` | List configured stages |
| `POST` | `/api/v1/pipeline/stages/` | Create custom stage |
| `PUT` | `/api/v1/pipeline/stages/{id}/` | Update stage details |
| `DELETE` | `/api/v1/pipeline/stages/{id}/` | Delete stage |

### Real-Time Sync

WebSocket connection via Django Channels:

- **Channel Group** — One group per job board: `pipeline_{job_id}`
- **Events** — `candidate_moved`, `candidate_added`, `stage_updated`
- **Payload** — Minimal diff data (`application_id`, `candidate_id`, `from_stage`, `to_stage`, `moved_by`)
- **Conflict Resolution** — Server-authoritative; if a move conflicts, the client receives the corrected state

### Data Model

Stage transitions are recorded in the `candidate_stage_history` table (see [[pipeline-schema|Pipeline Schema]]):

```sql
CREATE TABLE candidate_stage_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES candidate_applications(id) ON DELETE CASCADE,
    from_stage_id UUID REFERENCES pipeline_stages(id),
    to_stage_id UUID NOT NULL REFERENCES pipeline_stages(id),
    moved_by UUID REFERENCES users(id),
    notes TEXT,
    moved_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Edge Cases

| Scenario | Resolution |
|----------|-----------|
| Concurrent moves (two users move same application) | Server rejects second move with 409 Conflict; client refreshes state |
| Stage deletion with applications | Force reassignment dialog — applications must be moved before deletion |
| Custom stage ordering | `order` field with gap numbering (10, 20, 30) for easy insertions |
| Large candidate volumes (500+ per stage) | Virtual scrolling within columns; paginated API with cursor |
| Network disconnection during drag | Optimistic update rolls back; reconnection triggers full state refresh |
| Drag to terminal stage (Rejected) | Confirmation modal with required rejection reason |

## Performance Optimization

- Board data is loaded in a single API call with nested serialization
- Candidate cards use virtual scrolling for stages with > 50 candidates
- WebSocket updates are debounced (100ms) to batch rapid changes
- Stage counts are cached server-side and invalidated on transitions

## Related Pages

- [[pipeline-api|Pipeline API]] — REST API documentation for pipeline operations
- [[pipeline-schema|Pipeline Schema]] — Database schema for pipeline tables
- [[candidate-dashboard|Candidate Dashboard]] — Individual candidate view linked from cards
- [[sprint-09-pipeline|Sprint 9 — Hiring Pipeline]] — Implementation sprint details
- [[notification-system|Notification System]] — Notifications triggered by stage transitions

---
type: analysis
title: "Sprint 13 Notifications Implementation"
analysis_type: framework
date_created: 2026-06-11
date_updated: 2026-06-11
source_count: 4
tags: [product/feature, product/architecture, notifications, email, sprint/phase-complete]
---

# Sprint 13 Notifications Implementation

## Methodology

Implemented Phase 13A of the Sprint 13 plan ([[sprint-13-notifications]]) and the [[notification-system|Notification System]] reference. `raw/` is immutable; this records the implemented product state. Sprints 10–12 (candidate dashboard, semantic search, interview AI) were verified working first (full backend suite green, frontend builds, live smoke of search + interview generation) before starting Sprint 13.

## Phased Decision

The sprint calls for in-app + email + **WebSocket real-time** + preferences. WebSockets need new infra (Django Channels + ASGI + Redis channel layer) the project doesn't have. Per decision, Sprint 13 is split:
- **Phase 13A (done):** in-app notifications + email + per-event preferences, with the bell updated by **polling** — no new infra.
- **Phase 13B (deferred):** Django Channels/WebSocket live push + toasts, which also retro-enables the Sprint 9 live pipeline board.

Email uses **Django's SMTP framework** (console in dev, SMTP via env in prod) — provider-agnostic, no SDK; SendGrid/Resend SMTP creds can drop in later.

## What Shipped (Phase 13A)

**Backend — new `apps.notifications`:**
- `Notification` (recipient, organization, `event_type`, title, body, `data` JSON, `read_at`, indexes on recipient+read/created) and `NotificationPreference` (user × event_type → email/in-app toggles; a missing row means both channels on).
- `services.notify(...)`: honors preferences, **skips self-actor** (you aren't notified of your own action), creates the in-app row and dispatches email. `notify_recruiters_for_job(job, ...)` targets `job.created_by`.
- `tasks.send_notification_email`: `@shared_task` sending plain-text mail via Django `EmailMessage` + `DEFAULT_FROM_EMAIL`, with a deep `Open:` link from `FRONTEND_BASE_URL`. Dispatch mirrors `dispatch_resume_parse` — runs inline when Celery is eager (dev/tests), queues to the worker otherwise.
- REST under `/api/v1/notifications/`: list (`?unread=true`, capped 100), `unread-count/`, `{id}/read/`, `mark-all-read/`, `preferences/` (GET/PATCH matrix). Scoped to `request.user`.
- **Triggers** emitted from views that already hold `request.user`: `candidate_moved` (status-update + pipeline move), `new_application` (public apply → job owner).
- Email settings added to `config/settings/base.py` (SMTP via env; dev keeps console).

**Frontend:**
- `NotificationBell` in the dashboard top bar: bell + unread badge, dropdown list (read/unread styling, relative time), per-item mark-read + click-to-navigate (`data.url`), "Mark all read". Unread count **polls every 30s** and on window focus.
- Notification preferences page (`dashboard/settings/notifications`): event × channel toggle matrix with optimistic save.
- `types/notifications.ts`, `lib/notifications.ts` clients.

## Verification

- Migrations: `makemigrations` clean, `notifications/0001` applied.
- Backend: full suite green incl. **8 new notification tests** (create + email, self-actor skip, preference enforcement both channels + email-off-keeps-in-app, list/unread-count/mark-read/mark-all, preferences GET/PATCH, move + new-application triggers).
- Frontend: type-check, lint, production build all pass.
- Live smoke: `notify()` created an in-app row (unread 0→1) and the **console email fired** with the deep link; self-actor returned `None`; `mark_all_read` cleared the badge. Notifications endpoint live (401 unauth).

## Deferred / Out of Scope

- **Phase 13B** — Django Channels/WebSocket real-time + toasts (+ Sprint 9 live board).
- Provider SDK (using SMTP), branded HTML email templates (plain for 13A), mobile push, digest batching, optimistic concurrency.
- Fan-out beyond the job owner (e.g., all org recruiters / assigned reviewers) — `notify_recruiters_for_job` is the seam.

## Source References

- [[sprint-13-notifications|Sprint 13 Plan]]
- [[notification-system|Notification System]]
- [[Sprint 9 Hiring Pipeline Implementation]]
- [[system-overview|System Overview]]

## Open Questions

- Who should receive pipeline events once team assignment exists — owner only, assigned reviewer, or all org recruiters?
- Should candidates receive their own notifications (status changes) via the candidate portal?
- Daily/weekly digest emails to reduce volume before 13B real-time lands?

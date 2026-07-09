---
title: "Sprint 13 — Notification System"
sprint_number: 13
status: planned
start_date: 2026-11-17
end_date: 2026-11-27
story_points_planned: 38
story_points_completed: 0
tags:
  - sprint
  - notifications
  - email
  - websocket
---

# Sprint 13 — Notification System

## 🎯 Sprint Goal

> **Primary Objective:** Implement email and in-app notification infrastructure for pipeline events, team collaboration alerts, and system messages, with real-time delivery via WebSocket.
>
> **Success Criteria:** Users receive real-time in-app notifications for pipeline changes, mentions, and assignments. Email notifications are sent for critical events. Users can configure notification preferences per channel and event type.

---

## 📋 Planned Features

- [ ] In-app notification center with real-time updates
- [ ] Email notifications via SendGrid/Resend for critical events
- [ ] WebSocket-based real-time delivery using Django Channels
- [ ] Per-user notification preferences and channel configuration

---

## ⚙️ Backend Tasks

- [ ] Create `Notification` model: recipient, type, title, body, data (JSONField), read_at, created_at
- [ ] Create `NotificationPreference` model: user, event_type, email_enabled, in_app_enabled
- [ ] Build `NotificationService` class with methods: `send()`, `send_bulk()`, `mark_read()`
- [ ] Define notification event types: `candidate_moved`, `new_application`, `mention`, `interview_scheduled`, `assignment`, `system_alert`
- [ ] Integrate email provider (SendGrid or Resend) with templated transactional emails
- [ ] Set up Django Channels with Redis channel layer for WebSocket notifications
- [ ] Create WebSocket consumer `NotificationConsumer` for real-time delivery
- [ ] Implement `GET /api/v1/notifications/` with pagination, filter by read/unread
- [ ] Implement `PATCH /api/v1/notifications/{id}/read/` and `POST /api/v1/notifications/mark-all-read/`
- [ ] Build notification preference CRUD: `GET/PATCH /api/v1/notifications/preferences/`
- [ ] Write tests: notification creation, delivery, WebSocket connection, preference enforcement

See also: [[notification-system|Notification System]]

---

## 🖥️ Frontend Tasks

- [ ] Build Notification Center dropdown in top navigation: bell icon with unread count badge
- [ ] Create notification list with grouped items (today, yesterday, older)
- [ ] Implement toast notifications for real-time events using a toast library
- [ ] Build notification detail rendering per type: different icons, colors, action buttons
- [ ] Create Notification Preferences page: toggle matrix (event type × channel)
- [ ] Implement WebSocket connection hook `useNotifications()` with auto-reconnect
- [ ] Add "Mark all as read" and individual mark-as-read functionality
- [ ] Build notification click handlers: navigate to relevant page (candidate, job, pipeline)

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| WebSocket scaling with many concurrent users | Medium | Use Redis channel layer, plan for horizontal scaling | 🟡 Monitoring |
| Email deliverability (spam filters) | Medium | SPF/DKIM setup, warm up sender domain, test with Mail Tester | 🔴 Open |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Email templates are basic — need branded HTML templates
- [ ] No push notifications for mobile — web-only initially

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-09-pipeline]] — pipeline events trigger notifications
- **References:** [[notification-system|Notification System]], [[system-overview|System Overview]]
- **Next Sprint:** [[sprint-14-analytics]] — Analytics Dashboard

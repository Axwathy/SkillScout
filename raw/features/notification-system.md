---
type: feature
title: "Notification System"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, notifications, real-time]
---

# Notification System

## Overview

The Notification System keeps recruiters informed about pipeline events, candidate updates, and system activities in real time. It delivers alerts through multiple channels — in-app notifications, email, and browser push (future) — ensuring recruiters never miss critical hiring events.

## Purpose

Recruitment is a time-sensitive, multi-stakeholder process. When a candidate is scored, moves stages, or receives interview feedback, the relevant recruiter needs to know immediately. The Notification System acts as the central nervous system of the platform, routing events to the right people through their preferred channels.

## User Flow

1. **Event Occurs** — A pipeline event triggers a notification (e.g., candidate stage change, new application, scoring complete).
2. **Notification Created** — System creates a notification record linked to the event and recipient.
3. **In-App Delivery** — Notification appears in the notification bell (badge count increments) and is pushed via WebSocket.
4. **Email Delivery** — If the event type is configured for email, a formatted email is sent asynchronously.
5. **User Interaction** — Recruiter clicks notification to navigate to the relevant page (candidate, job, pipeline).
6. **Mark as Read** — Notification is marked as read on click or via "Mark all as read" action.

## Notification Event Types

| Event | Trigger | Default Channel | Priority |
|-------|---------|-----------------|----------|
| New Application | Candidate created for a job | In-app + Email | Normal |
| Resume Parsed | Parsing pipeline completes | In-app | Low |
| Scoring Complete | AI scoring finishes | In-app | Normal |
| Stage Change | Candidate moved to new stage | In-app + Email | Normal |
| Interview Scheduled | Interview event created | In-app + Email | High |
| Interview Feedback Added | Team member submits feedback | In-app | Normal |
| Offer Extended | Candidate moved to Offer stage | In-app + Email | High |
| Candidate Rejected | Candidate moved to Rejected stage | In-app | Normal |
| System Alert | Error in AI pipeline, quota warning | In-app + Email | Critical |

## Component Architecture

### Notification Bell (Header)

- Persistent bell icon in the app header
- Badge showing unread count (red circle with number)
- Badge disappears when all notifications are read
- Click opens the Notification Drawer

### Notification Drawer

A slide-out panel from the right side of the screen:

- **Header** — "Notifications" title with "Mark all as read" link
- **Filter Tabs** — All | Unread | Mentions
- **Notification List** — Scrollable list of notification cards, newest first
- **Empty State** — "You're all caught up!" with illustration

Each notification card shows:
- Event icon (color-coded by type)
- Brief description (e.g., "John Doe was moved to Technical Interview")
- Timestamp (relative: "2 minutes ago")
- Unread indicator (blue dot)
- Click navigates to the relevant entity

### Notification Preferences

Accessible from user settings:

| Event Type | In-App | Email | Browser Push |
|-----------|--------|-------|-------------|
| New Application | ✅ Always | ✅ Default on | 🔮 Future |
| Scoring Complete | ✅ Always | ⬜ Default off | 🔮 Future |
| Stage Change | ✅ Always | ✅ Default on | 🔮 Future |
| Interview Scheduled | ✅ Always | ✅ Default on | 🔮 Future |
| Feedback Added | ✅ Always | ⬜ Default off | 🔮 Future |
| System Alert | ✅ Always | ✅ Always | 🔮 Future |

## Backend Architecture

### Notification Model

```python
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=50, choices=NotificationEventType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    entity_type = models.CharField(max_length=50)  # 'candidate', 'job', 'pipeline'
    entity_id = models.UUIDField()
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, choices=Priority.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
```

### Event-Driven Triggers

Notifications are dispatched via Django signals:

```python
@receiver(post_save, sender=PipelineTransition)
def notify_stage_change(sender, instance, created, **kwargs):
    if created:
        NotificationService.create(
            recipient=instance.candidate.assigned_recruiter,
            event_type=NotificationEventType.STAGE_CHANGE,
            title=f"{instance.candidate.full_name} moved to {instance.to_stage.name}",
            entity_type='candidate',
            entity_id=instance.candidate.id,
        )
```

### Email Service

- **Provider** — SendGrid (primary) or Resend (fallback)
- **Templates** — HTML email templates with inline CSS for client compatibility
- **Queue** — Emails are queued via Celery to avoid blocking the request cycle
- **Rate Limiting** — Max 100 emails per user per day to prevent spam
- **Unsubscribe** — One-click unsubscribe link in every email footer

### WebSocket Real-Time Delivery

Using Django Channels:

- **Consumer** — `NotificationConsumer` handles per-user WebSocket connections
- **Channel Group** — `notifications_{user_id}` for targeted delivery
- **Payload** — Serialized notification object pushed on creation
- **Reconnection** — Client auto-reconnects with exponential backoff; missed notifications fetched via REST on reconnect

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/notifications/` | List notifications (paginated, filterable) |
| `PUT` | `/api/v1/notifications/{id}/read/` | Mark single notification as read |
| `PUT` | `/api/v1/notifications/read-all/` | Mark all notifications as read |
| `GET` | `/api/v1/notifications/unread-count/` | Get unread notification count |
| `PUT` | `/api/v1/notifications/preferences/` | Update notification preferences |

## Performance Considerations

- Notifications table is indexed on `(recipient_id, is_read, created_at)` for fast queries
- Unread count is cached in Redis and updated atomically on read/create events
- Old notifications (> 90 days) are archived to a separate table via a daily cron job
- WebSocket connections are load-balanced across multiple Channels workers

## Related Pages

- [[sprint-13-notifications|Sprint 13 — Notification System]] — Implementation sprint details
- [[pipeline-board|Pipeline Board]] — Source of stage change events
- [[ai-pipeline|AI Pipeline]] — Source of scoring and parsing events
- [[candidate-dashboard|Candidate Dashboard]] — Notification click navigation target

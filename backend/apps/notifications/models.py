import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class EventType(models.TextChoices):
        NEW_APPLICATION = "new_application", "New application"
        CANDIDATE_MOVED = "candidate_moved", "Candidate moved"
        NOTE_ADDED = "note_added", "Note added"
        INTERVIEW_READY = "interview_ready", "Interview questions ready"
        SYSTEM_ALERT = "system_alert", "System alert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read_at"]),
            models.Index(fields=["recipient", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.recipient_id}"

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self) -> None:
        if self.read_at is None:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])


class NotificationPreference(models.Model):
    """Per-user, per-event channel preference. A missing row means both channels
    are on, so users only need rows once they opt out of something."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    event_type = models.CharField(max_length=32, choices=Notification.EventType.choices)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user", "event_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event_type"],
                name="unique_notification_pref_per_user_event",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.event_type}"


import uuid

from django.db import models


class DailyAnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="analytics_snapshots",
    )
    snapshot_date = models.DateField()
    overview = models.JSONField(default=dict, blank=True)
    funnel = models.JSONField(default=dict, blank=True)
    time_to_hire = models.JSONField(default=dict, blank=True)
    sources = models.JSONField(default=dict, blank=True)
    team_activity = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-snapshot_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "snapshot_date"],
                name="unique_daily_analytics_snapshot",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "snapshot_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id} analytics snapshot {self.snapshot_date}"

from django.db import models


class AuditLog(models.Model):
    """
    Immutable audit trail for important system actions.
    Sprint 2: model + architecture only. No UI.

    Examples of action strings:
        "recruiter.approved", "recruiter.rejected", "recruiter.suspended"
        "org.approved", "org.rejected", "org.suspended"
        "auth.login", "auth.logout", "auth.register"
        "role.changed"
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text="The user who performed the action. Null for system actions.",
    )
    action = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Dot-namespaced action identifier, e.g. 'recruiter.approved'",
    )
    entity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model name of the affected entity, e.g. 'Recruiter', 'Organization'",
    )
    entity_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="PK of the affected entity as string (supports UUIDs and BigInts)",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context — old/new values, reason, etc.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the acting user.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self) -> str:
        actor = self.user.email if self.user else "system"
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M}] "
            f"{actor} -> {self.action} ({self.entity_type}:{self.entity_id})"
        )

    @classmethod
    def log(
        cls,
        action: str,
        user=None,
        entity=None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> "AuditLog":
        """Convenience factory for creating log entries."""
        entity_type = ""
        entity_id = ""
        if entity is not None:
            entity_type = type(entity).__name__
            entity_id = str(entity.pk)

        return cls.objects.create(
            action=action,
            user=user,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
            ip_address=ip_address,
        )

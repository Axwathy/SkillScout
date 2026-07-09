import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class BatchJob(models.Model):
    class JobType(models.TextChoices):
        UPLOAD = "upload", "Bulk Upload"
        SCORE = "score", "Batch Score"
        PIPELINE_ACTION = "pipeline_action", "Pipeline Action"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        CANCEL_REQUESTED = "cancel_requested", "Cancel Requested"
        CANCELED = "canceled", "Canceled"
        COMPLETED = "completed", "Completed"
        COMPLETED_WITH_ERRORS = "completed_with_errors", "Completed with Errors"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="batch_jobs",
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_batch_jobs",
    )
    job_type = models.CharField(max_length=30, choices=JobType.choices, db_index=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    total_count = models.PositiveIntegerField(default=0)
    processed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    params = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status", "created_at"]),
            models.Index(fields=["organization", "job_type", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_job_type_display()} batch {self.id}"

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            self.Status.COMPLETED,
            self.Status.COMPLETED_WITH_ERRORS,
            self.Status.FAILED,
            self.Status.CANCELED,
        }


class BatchItem(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(BatchJob, on_delete=models.CASCADE, related_name="items")
    label = models.CharField(max_length=255)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    error = models.TextField(blank=True)
    application = models.ForeignKey(
        "candidates.Application",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batch_items",
    )
    candidate = models.ForeignKey(
        "candidates.Candidate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batch_items",
    )
    metadata = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "label"]
        indexes = [
            models.Index(fields=["batch", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.batch_id}: {self.label}"


def mark_batch_started(batch: BatchJob) -> BatchJob:
    if batch.status == BatchJob.Status.PENDING:
        batch.status = BatchJob.Status.RUNNING
        batch.started_at = timezone.now()
        batch.save(update_fields=["status", "started_at"])
    return batch


class ScheduledBatchOperation(models.Model):
    class Frequency(models.TextChoices):
        ONCE = "once", "Once"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="scheduled_batch_operations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_batch_operations",
    )
    job_type = models.CharField(max_length=30, choices=BatchJob.JobType.choices)
    params = models.JSONField(default=dict, blank=True)
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.ONCE,
    )
    is_active = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(db_index=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_batch = models.ForeignKey(
        BatchJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_sources",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_run_at"]
        indexes = [
            models.Index(fields=["organization", "is_active", "next_run_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_frequency_display()} {self.get_job_type_display()} schedule"

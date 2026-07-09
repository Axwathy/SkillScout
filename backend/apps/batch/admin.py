from django.contrib import admin

from .models import BatchItem, BatchJob, ScheduledBatchOperation


class BatchItemInline(admin.TabularInline):
    model = BatchItem
    extra = 0
    readonly_fields = (
        "label",
        "status",
        "error",
        "application",
        "candidate",
        "started_at",
        "completed_at",
    )
    can_delete = False


@admin.register(BatchJob)
class BatchJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "job_type",
        "status",
        "total_count",
        "processed_count",
        "failed_count",
        "created_at",
    )
    list_filter = ("job_type", "status", "organization")
    search_fields = ("id", "organization__name", "initiated_by__email")
    readonly_fields = ("created_at", "started_at", "completed_at")
    inlines = [BatchItemInline]


@admin.register(BatchItem)
class BatchItemAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "label", "status", "application", "candidate")
    list_filter = ("status", "batch__job_type")
    search_fields = ("label", "error", "application__candidate__email")


@admin.register(ScheduledBatchOperation)
class ScheduledBatchOperationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "job_type",
        "frequency",
        "is_active",
        "next_run_at",
        "last_run_at",
    )
    list_filter = ("job_type", "frequency", "is_active", "organization")
    search_fields = ("id", "organization__name", "created_by__email")


from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organization",
        "department",
        "status",
        "employment_type",
        "remote_policy",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "employment_type", "remote_policy", "organization")
    search_fields = ("title", "description", "requirements", "location", "department")
    readonly_fields = ("id", "slug", "published_at", "created_at", "updated_at")
    ordering = ("-created_at",)

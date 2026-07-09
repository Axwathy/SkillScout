
from django.contrib import admin

from .models import Application, Candidate, CandidateNote


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "organization", "created_at")
    list_filter = ("organization",)
    search_fields = ("email", "first_name", "last_name", "phone")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "organization", "status", "applied_at")
    list_filter = ("status", "organization")
    search_fields = (
        "candidate__email",
        "candidate__first_name",
        "candidate__last_name",
        "job__title",
    )
    readonly_fields = ("id", "applied_at", "updated_at")
    ordering = ("-applied_at",)


@admin.register(CandidateNote)
class CandidateNoteAdmin(admin.ModelAdmin):
    list_display = ("candidate", "organization", "author", "created_at")
    list_filter = ("organization",)
    search_fields = ("candidate__email", "candidate__first_name", "candidate__last_name", "body")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

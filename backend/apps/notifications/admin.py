from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("event_type", "recipient", "title", "read_at", "created_at")
    list_filter = ("event_type", "read_at")
    search_fields = ("title", "recipient__email")
    readonly_fields = ("created_at",)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "email_enabled", "in_app_enabled")
    list_filter = ("event_type", "email_enabled", "in_app_enabled")
    search_fields = ("user__email",)

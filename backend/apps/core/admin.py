from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "get_actor", "action", "entity_type", "entity_id", "ip_address")
    list_filter = ("action", "entity_type")
    search_fields = ("user__email", "action", "entity_type", "entity_id")
    readonly_fields = (
        "id",
        "user",
        "action",
        "entity_type",
        "entity_id",
        "metadata",
        "ip_address",
        "timestamp",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False  # Audit logs are immutable.

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Actor", ordering="user__email")
    def get_actor(self, obj):
        return obj.user.email if obj.user else "system"

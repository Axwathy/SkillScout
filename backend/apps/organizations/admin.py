from django.contrib import admin

from apps.core.models import AuditLog

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "approval_status", "website", "is_active", "created_at")
    list_filter = ("approval_status", "is_active")
    search_fields = ("name", "slug", "website")
    readonly_fields = ("id", "slug", "created_at", "updated_at")
    ordering = ("-created_at",)
    actions = ["approve_organizations", "reject_organizations", "suspend_organizations"]

    @admin.action(description="Approve selected organizations")
    def approve_organizations(self, request, queryset):
        for org in queryset:
            prev_status = org.approval_status
            org.approval_status = Organization.ApprovalStatus.APPROVED
            org.save(update_fields=["approval_status", "updated_at"])
            AuditLog.log(
                action="org.approved",
                user=request.user,
                entity=org,
                metadata={"previous_status": prev_status},
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} organization(s) approved.")

    @admin.action(description="Reject selected organizations")
    def reject_organizations(self, request, queryset):
        for org in queryset:
            prev_status = org.approval_status
            org.approval_status = Organization.ApprovalStatus.REJECTED
            org.save(update_fields=["approval_status", "updated_at"])
            AuditLog.log(
                action="org.rejected",
                user=request.user,
                entity=org,
                metadata={"previous_status": prev_status},
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} organization(s) rejected.")

    @admin.action(description="Suspend selected organizations")
    def suspend_organizations(self, request, queryset):
        for org in queryset:
            prev_status = org.approval_status
            org.approval_status = Organization.ApprovalStatus.SUSPENDED
            org.save(update_fields=["approval_status", "updated_at"])
            AuditLog.log(
                action="org.suspended",
                user=request.user,
                entity=org,
                metadata={"previous_status": prev_status},
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} organization(s) suspended.")

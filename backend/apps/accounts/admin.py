from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.core.models import AuditLog

from .models import Recruiter, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_email_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_email_verified", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "role")}),
        ("Verification", {"fields": ("is_email_verified",)}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = (
        "get_email",
        "full_name",
        "get_organization",
        "verification_status",
        "is_verified",
        "created_at",
    )
    list_filter = ("verification_status", "is_verified")
    search_fields = ("user__email", "first_name", "last_name", "organization__name")
    readonly_fields = ("id", "created_at", "updated_at", "is_verified")
    ordering = ("-created_at",)
    actions = ["approve_recruiters", "reject_recruiters", "suspend_recruiters"]

    @admin.display(description="Email", ordering="user__email")
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description="Organization", ordering="organization__name")
    def get_organization(self, obj):
        return obj.organization.name if obj.organization else "-"

    @admin.action(description="Approve selected recruiters")
    def approve_recruiters(self, request, queryset):
        for recruiter in queryset:
            prev_status = recruiter.verification_status
            recruiter.approve()
            AuditLog.log(
                action="recruiter.approved",
                user=request.user,
                entity=recruiter,
                metadata={
                    "previous_status": prev_status,
                    "recruiter_email": recruiter.user.email,
                },
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} recruiter(s) approved.")

    @admin.action(description="Reject selected recruiters")
    def reject_recruiters(self, request, queryset):
        for recruiter in queryset:
            prev_status = recruiter.verification_status
            recruiter.reject()
            AuditLog.log(
                action="recruiter.rejected",
                user=request.user,
                entity=recruiter,
                metadata={
                    "previous_status": prev_status,
                    "recruiter_email": recruiter.user.email,
                },
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} recruiter(s) rejected.")

    @admin.action(description="Suspend selected recruiters")
    def suspend_recruiters(self, request, queryset):
        for recruiter in queryset:
            prev_status = recruiter.verification_status
            recruiter.suspend()
            AuditLog.log(
                action="recruiter.suspended",
                user=request.user,
                entity=recruiter,
                metadata={
                    "previous_status": prev_status,
                    "recruiter_email": recruiter.user.email,
                },
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        self.message_user(request, f"{queryset.count()} recruiter(s) suspended.")

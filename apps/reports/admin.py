from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Report, Notification, UserNotification, ResourceLink
from .services import create_audit_log_for_user


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Extends Django's default User admin.

    When a new user is created from Django Admin:
    - create an audit log
    - create a notification
    - send notification to Admin + Department Head users
    """

    def save_model(self, request, obj, form, change):
        is_new_user = obj.pk is None

        super().save_model(request, obj, form, change)

        if is_new_user:
            new_user_name = obj.get_full_name() or obj.username

            create_audit_log_for_user(
                actor=request.user,
                entity_name="User",
                action="Create",
                change_summary=f"Created new user '{new_user_name}' with username '{obj.username}'."
            )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "report_id",
        "report_name",
        "report_type",
        "report_format",
        "status",
        "is_scheduled",
        "created_at",
    )
    search_fields = ("report_name", "report_type", "scope", "department")
    list_filter = ("status", "report_format", "is_scheduled")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "notification_id",
        "title",
        "notification_type",
        "created_by",
        "created_at",
    )
    search_fields = ("title", "message", "notification_type")


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "notification",
        "user",
        "delivery_status",
        "date",
        "delivered_at",
        "read_at",
    )
    search_fields = (
        "notification__title",
        "user__username",
        "user__email",
    )
    list_filter = ("delivery_status",)


@admin.register(ResourceLink)
class ResourceLinkAdmin(admin.ModelAdmin):
    list_display = (
        "resource_id",
        "resource_type",
        "team_id",
        "created_at",
    )
    search_fields = ("resource_type", "description", "documentation")
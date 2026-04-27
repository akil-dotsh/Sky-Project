from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from .models import AuditLog, Notification, UserNotification


def get_management_notification_users():
    """
    Return users who should receive all system/audit notifications.

    Admin users are identified by is_superuser=True.
    Department Heads are identified by the 'Department Head' group.
    """

    return (
        User.objects
        .filter(
            Q(is_superuser=True) |
            Q(groups__name="Department Head"),
            is_active=True
        )
        .distinct()
    )


def create_notification_for_users(created_by, title, message, notification_type, link_url, receivers):
    """
    Create one Notification record and one USER_NOTIFICATION record per receiver.

    Notification.created_by = the user who generated/created the notification.
    UserNotification.user = the user who receives the notification.
    """

    if created_by is None:
        return None

    now_text = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    notification = Notification.objects.create(
        created_by=created_by,
        title=title,
        message=message,
        notification_type=notification_type,
        link_url=link_url,
        created_at=now_text,
    )

    for receiver in receivers:
        receiver_time = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        UserNotification.objects.create(
            notification=notification,
            user=receiver,
            date=receiver_time,
            delivered_at=receiver_time,
            delivery_status="Queued",
            read_at=None,
        )

    return notification


def create_audit_log_for_user(actor, entity_name, action, change_summary):
    """
    Create an audit log and send an audit notification to Admin + Department Head.

    This is used when we already have a user object, such as inside admin.py.
    """

    audit_log = AuditLog.objects.create(
        entity_name=entity_name,
        action=action,
        changed_by_name=actor.get_full_name() or actor.username if actor else "System",
        change_summary=change_summary,
        user=actor,
        changed_at=timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )

    if actor:
        management_users = get_management_notification_users()

        create_notification_for_users(
            created_by=actor,
            title=f"Audit event: {action}",
            message=f"{audit_log.changed_by_name} performed {action} on {entity_name}. {change_summary}",
            notification_type="Audit",
            link_url="/report/notifications/",
            receivers=management_users,
        )

    return audit_log


def create_audit_log(request, entity_name, action, change_summary):
    """
    Wrapper for normal views where request is available.
    """

    actor = request.user if request.user.is_authenticated else None

    return create_audit_log_for_user(
        actor=actor,
        entity_name=entity_name,
        action=action,
        change_summary=change_summary,
    )
from .models import UserNotification


def notifications_context(request):
    """
    Makes notification data available globally in templates.

    Used by the topbar notification bell/dropdown.
    """

    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "latest_notifications": [],
        }

    latest_notifications = (
        UserNotification.objects
        .filter(user=request.user)
        .select_related("notification")
        .order_by("-date")[:3]
    )

    unread_count = UserNotification.objects.filter(
        user=request.user,
        read_at__isnull=True
    ).count()

    return {
        "unread_notifications_count": unread_count,
        "latest_notifications": latest_notifications,
    }
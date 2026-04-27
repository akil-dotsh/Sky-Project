from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.dashboard.models import Team


def get_active_team_count():
    """
    Return the number of active teams for dashboard summary cards.
    """
    return Team.objects.filter(status="Active").count()


def management_dashboard(request):
    """
    Display the management dashboard.
    """
    return render(request, "dashboard/management_dashboard.html", {
        "active_team_count": get_active_team_count(),
    })


def staff_dashboard(request):
    """
    Display the staff dashboard.
    """
    user_groups = list(request.user.groups.values_list("name", flat=True))

    context = {
        "user_groups": user_groups,
        "active_team_count": get_active_team_count(),
    }

    return render(request, "dashboard/staff_dashboard.html", context)


def is_admin_or_department_head(user):
    """
    Only Admin/Superuser and Department Head users can access
    the permission management page.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name="Department Head").exists()


@login_required
@user_passes_test(is_admin_or_department_head)
def user_management(request):
    """
    Display the custom user and permission management page.
    """
    search_query = request.GET.get("search", "").strip()
    group_filter = request.GET.get("group", "").strip()
    status_filter = request.GET.get("status", "").strip()

    users = User.objects.all().prefetch_related("groups").order_by("username")
    groups = Group.objects.all().order_by("name")

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if group_filter:
        users = users.filter(groups__id=group_filter)

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)
    elif status_filter == "staff":
        users = users.filter(is_staff=True)
    elif status_filter == "superuser":
        users = users.filter(is_superuser=True)

    context = {
        "users": users.distinct(),
        "groups": groups,
        "search_query": search_query,
        "group_filter": group_filter,
        "status_filter": status_filter,
    }

    return render(request, "dashboard/user_management.html", context)


@login_required
@user_passes_test(is_admin_or_department_head)
@require_POST
def update_user_permissions(request, user_id):
    """
    Update selected user's active/staff/superuser status and group membership.
    """
    target_user = get_object_or_404(User, id=user_id)

    is_active = request.POST.get("is_active") == "on"
    is_staff = request.POST.get("is_staff") == "on"
    is_superuser = request.POST.get("is_superuser") == "on"

    selected_group_ids = request.POST.getlist("groups")
    selected_groups = Group.objects.filter(id__in=selected_group_ids)

    target_user.is_active = is_active
    target_user.is_staff = is_staff
    target_user.is_superuser = is_superuser
    target_user.save()

    target_user.groups.set(selected_groups)

    messages.success(request, f"Permissions updated for {target_user.username}.")

    return redirect("user_management")


@login_required
@user_passes_test(is_admin_or_department_head)
@require_POST
def create_group(request):
    """
    Create a new permission group.
    """
    group_name = request.POST.get("group_name", "").strip()

    if not group_name:
        messages.error(request, "Group name cannot be empty.")
        return redirect("user_management")

    group, created = Group.objects.get_or_create(name=group_name)

    if created:
        messages.success(request, f"Group '{group.name}' created successfully.")
    else:
        messages.warning(request, f"Group '{group.name}' already exists.")

    return redirect("user_management")
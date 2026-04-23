from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.authentication.models import UserProfile


@login_required
def update_info(request):
    user = request.user
    user_groups = list(user.groups.values_list('name', flat=True))

    if request.user.is_superuser or 'Department Head' in user_groups:
        base_template = "core/base_management.html"
    else:
        base_template = "core/base_staff.html"

    profile = UserProfile.objects.filter(user=user).first()

    if request.method == "POST":
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name", "").strip()

        if "last_name" in request.POST:
            user.last_name = request.POST.get("last_name", "").strip()

        if "email" in request.POST:
            user.email = request.POST.get("email", "").strip()

        user.save()

        if not profile:
            profile = UserProfile(
                user=user,
                dob=date(2000, 1, 1),
                phone=""
            )

        if "phone_number" in request.POST:
            profile.phone = request.POST.get("phone_number", "").strip()

        if "office_location" in request.POST:
            profile.office_location = request.POST.get("office_location", "").strip()

        if "availability_status" in request.POST:
            profile.availability_status = request.POST.get("availability_status", "").strip()

        if "bio" in request.POST:
            profile.bio = request.POST.get("bio", "").strip()

        profile.save()

        messages.success(request, "Your information has been updated successfully.")
        return redirect("update_info")

    context = {
        "profile": profile,
        "user_groups": user_groups,
        "base_template": base_template,
    }

    return render(request, "update_info.html", context)
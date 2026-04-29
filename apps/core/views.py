# Author: Akil Hossain
# Student ID: 20270054

import os
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.authentication.models import UserProfile

# Handles the logic for allowing users to update their profile information and save the submitted changes to the database.
@login_required
def update_info(request):
    user = request.user
    user_groups = list(user.groups.values_list("name", flat=True))

    if request.user.is_superuser or "Department Head" in user_groups:
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

        # Handle profile picture upload.
        # The HTML input name must be "profile_picture".
        uploaded_picture = request.FILES.get("profile_picture")

        if uploaded_picture:
            # Delete previous image file if this user already had one.
            if profile.profile_picture:
                old_picture_path = os.path.join(
                    settings.MEDIA_ROOT,
                    profile.profile_picture.replace(settings.MEDIA_URL, "")
                )

                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            # Save new image inside media/profile_pictures/
            profile_picture_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures")
            os.makedirs(profile_picture_dir, exist_ok=True)

            file_extension = uploaded_picture.name.split(".")[-1].lower()
            file_name = f"user_{user.id}_profile.{file_extension}"
            file_path = os.path.join(profile_picture_dir, file_name)

            with open(file_path, "wb+") as destination:
                for chunk in uploaded_picture.chunks():
                    destination.write(chunk)

            # This model field maps to the database column profile_picture_url.
            profile.profile_picture = f"{settings.MEDIA_URL}profile_pictures/{file_name}"

        profile.save()

        messages.success(request, "Your information has been updated successfully.")
        return redirect("update_info")

    context = {
        "profile": profile,
        "user_groups": user_groups,
        "base_template": base_template,
    }

    return render(request, "update_info.html", context)
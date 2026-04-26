import os
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.authentication.models import UserProfile


@login_required
def update_info(request):
    user = request.user
    user_groups = list(user.groups.values_list("name", flat=True))

    # Select correct base layout depending on user role
    if request.user.is_superuser or "Department Head" in user_groups:
        base_template = "core/base_management.html"
    else:
        base_template = "core/base_staff.html"

    profile = UserProfile.objects.filter(user=user).first()

    if request.method == "POST":
        # Update built-in auth_user fields
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name", "").strip()

        if "last_name" in request.POST:
            user.last_name = request.POST.get("last_name", "").strip()

        if "email" in request.POST:
            user.email = request.POST.get("email", "").strip()

        user.save()

        # Create profile if it does not exist
        if not profile:
            profile = UserProfile(
                user=user,
                dob=date(2000, 1, 1),
                phone=""
            )

        # Update UserProfile extra fields
        if "phone_number" in request.POST:
            profile.phone = request.POST.get("phone_number", "").strip()

        if "office_location" in request.POST:
            profile.office_location = request.POST.get("office_location", "").strip()

        if "availability_status" in request.POST:
            profile.availability_status = request.POST.get("availability_status", "").strip()

        if "bio" in request.POST:
            profile.bio = request.POST.get("bio", "").strip()

        # Handle profile picture upload
        uploaded_picture = request.FILES.get("profile_picture")

        if uploaded_picture:
            # Create media/profile_pictures folder if it does not exist
            profile_picture_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures")
            os.makedirs(profile_picture_dir, exist_ok=True)

            # Keep file name unique for each user
            file_extension = uploaded_picture.name.split(".")[-1].lower()
            file_name = f"user_{user.id}_profile.{file_extension}"

            # Save file inside media/profile_pictures/
            file_path = os.path.join(profile_picture_dir, file_name)

            with open(file_path, "wb+") as destination:
                for chunk in uploaded_picture.chunks():
                    destination.write(chunk)

            # Store URL/path in UserProfile table
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
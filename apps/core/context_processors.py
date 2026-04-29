# Author: Akil Hossain
# Student ID: 20270054

from apps.authentication.models import UserProfile

# Provides the logged-in user's profile to all templates, so shared layout
# elements like the sidebar and top-bar can display profile information safely.

def sidebar_profile(request):
    profile = None

    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()

    return {
        "profile": profile
    }
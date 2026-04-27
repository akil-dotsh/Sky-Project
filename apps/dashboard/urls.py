from django.urls import path
from . import views

urlpatterns = [
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("management_dashboard/", views.management_dashboard, name="management_dashboard"),

    path("users/", views.user_management, name="user_management"),
    path("users/<int:user_id>/permissions/", views.update_user_permissions, name="update_user_permissions"),
    path("groups/create/", views.create_group, name="create_group"),
]
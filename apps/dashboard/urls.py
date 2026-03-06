from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("management_dashboard/", views.management_dashboard, name="management_dashboard"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("update-info/", views.update_info, name="update_info"),
]
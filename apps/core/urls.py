# Author: Akil Hossain
# Student ID: 20270054
from django.urls import path
from . import views

urlpatterns = [
    path("update-info/", views.update_info, name="update_info"),
]
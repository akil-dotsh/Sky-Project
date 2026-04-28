"""
File:        apps/schedule/urls.py
Author:      Ryan Thompson (W1789088)
Module:      5COSC021W — Software Development Group Project
Description: URL patterns for the schedule app, namespaced under
             `schedule:` and mounted at /schedule/ from the project
             URLconf.
Co-authors:  None.
"""

from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_home, name='home'),
    path('monthly/', views.monthly_view, name='monthly'),
    path('weekly/', views.weekly_view, name='weekly'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('create/', views.create_meeting, name='create'),
    path('<int:pk>/edit/', views.edit_meeting, name='edit'),
    path('<int:pk>/delete/', views.delete_meeting, name='delete'),
]

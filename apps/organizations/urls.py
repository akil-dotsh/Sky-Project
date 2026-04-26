from django.urls import  path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'organizations'

urlpatterns=[
    path('Organizations/', views.Organizations, name='organizations'),
]
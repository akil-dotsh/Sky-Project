from django.urls import path
from . import views

urlpatterns = [
    path('', views.teams_list, name='teams_list'), # The directory page
    path('<slug:team_slug>/', views.team_detail, name='team_detail'), # The individual team page
]
from django.urls import path
from . import views


urlpatterns = [
    #main landing page, showing all teams
    path('', views.teams_list, name='teams_list'), # The directory page
    path('<int:user_id>/', views.team_detail, name='team_detail'),
]
from django.urls import path
from . import views

app_name = 'messaging' 

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('draft/', views.draft, name='draft'),
    path('messaging/', views.messaging, name='messaging'),
    path("message/<int:pk>/", views.message_detail, name="detail"),
    path("message/<int:pk>/", views.message_detail, name="message_detail"),
    path("autosave/", views.autosave_draft, name="autosave_draft"),
    path("message/<int:pk>/delete/", views.delete_message, name="delete"),
    path("draft/<int:pk>/delete/", views.delete_draft, name="delete_draft")
]

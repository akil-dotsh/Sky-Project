from django.urls import  path
from . import views


urlpatterns=[
    path('admin/', views.admin_login, name='admin_login'),
    path('dev/',views.dev_login, name='dev_login'),
    path('reg/', views.user_register, name='register'),
]
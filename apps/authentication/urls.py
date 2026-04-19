from django.urls import  path
from . import views


urlpatterns=[
    path('admin/', views.admin_dept_login, name='admin_dept_login'),
]
from django.urls import  path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('admin/', views.admin_login, name='admin_login'),
    path('dev/',views.dev_login, name='dev_login'),
    path('reg/', views.user_register, name='register'),
    path('reset/', views.forgot_password, name='forgot_password'),
    path(
        'reset/sent/',
        TemplateView.as_view(template_name='authentication/forgot_password_sent.html'),
        name='forgot_password_sent'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='authentication/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/complete/',
        TemplateView.as_view(template_name='authentication/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
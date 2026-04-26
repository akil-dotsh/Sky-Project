from django.urls import path

from . import views

urlpatterns =[
    path("",views.admin_report,name="admin_report"),
    path("generate/", views.report_generate, name="report_generate"),
    path("share/", views.share_report, name="share_report"),
    path("user-reports/", views.user_reports, name="user_reports")
]
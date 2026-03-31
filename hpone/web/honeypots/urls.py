from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("", views.dashboard, name="dashboard"),
    path("honeypots/<str:honeypot_id>/", views.detail, name="honeypot-detail"),
    path("honeypots/<str:honeypot_id>/start/", views.start_honeypot, name="honeypot-start"),
    path("honeypots/<str:honeypot_id>/stop/", views.stop_honeypot, name="honeypot-stop"),
    path("honeypots/<str:honeypot_id>/enable/", views.enable_honeypot, name="honeypot-enable"),
    path("honeypots/<str:honeypot_id>/disable/", views.disable_honeypot, name="honeypot-disable"),
    path("honeypots/<str:honeypot_id>/logs/", views.logs, name="honeypot-logs"),
    path("honeypots/<str:honeypot_id>/edit/", views.edit_yaml, name="honeypot-edit"),
]

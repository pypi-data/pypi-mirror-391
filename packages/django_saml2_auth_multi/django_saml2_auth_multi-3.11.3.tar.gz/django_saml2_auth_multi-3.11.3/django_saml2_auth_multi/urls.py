"""Django URL mappings"""

from django.urls import path
from django_saml2_auth_multi import views

app_name = "django_saml2_auth_multi"

urlpatterns = [
    path(r"acs/", views.acs, name="acs"),
    path(r"sp/", views.sp_initiated_login, name="sp"),
    path(r"welcome/", views.welcome, name="welcome"),
    path(r"denied/", views.denied, name="denied"),
]

from customauth import forms, views
from django.urls import path
from django.views.generic.base import RedirectView
from django.conf import settings

app_name = "customauth"
urlpatterns = [
    path(
        "signup/", 
        RedirectView.as_view(url=f"http://localhost:4000/auth/signup?r={settings.LOGIN_REDIRECT_URL}", permanent=False),
        name="signup"
    ),
    path(
        "login/",
        RedirectView.as_view(url=f"http://localhost:4000/auth/login?r={settings.LOGIN_REDIRECT_URL}", permanent=False),
        name="login",
    ),
    path(
        "logout/",
        RedirectView.as_view(url=f"http://localhost:4000/auth/logout", permanent=False), 
        name="logout"
    ),
]
from customauth import views
from django.urls import path
from django.views.generic.base import RedirectView

app_name = "customauth"
urlpatterns = [
    path(
        "signup/",
        views.AuthRedirectView.as_view(url="/auth/signup", permanent=False),
        name="signup"
    ),
    path(
        "login/",
        views.AuthRedirectView.as_view(url="/auth/login", permanent=False),
        name="login",
    ),
    path(
        "logout/",
        RedirectView.as_view(url="/auth/logout", permanent=False),
        name="logout"
    ),
]

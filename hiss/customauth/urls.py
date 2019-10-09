from customauth import forms, views
from django.contrib.auth import views as auth_views
from django.urls import path

app_name = "customauth"
urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=forms.LoginForm),
        name="login",
    ),
    path(
        "resend_activation/",
        views.ResendActivationEmailView.as_view(),
        name="resend_activation",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        views.PlaceholderPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PlaceholderPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),
]

"""ouroboros URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth import views as auth_views
from confirm import views as confirm_views
from django.urls import path, include
from django.conf.urls import url
from ouroboros.settings import customization as custom_settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", confirm_views.SignupView.as_view(), name="signup"),
    url(
        r"^accounts/activate/(?P<uidb64>[\w\d_\-]+)/(?P<token>[\w\d]{1,13}-[\w\d]{1,20})/$",
        confirm_views.ActivateView.as_view(),
        name="activate",
    ),
    path("", include("hacker.urls")),
]

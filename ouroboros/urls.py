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
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hacker.urls')),
    path('', core_views.IndexView.as_view(), name="index"),
    path('accounts/login/', core_views.HackerLoginView.as_view(), name="login"),
    path('accounts/logout/', core_views.LogOutView.as_view(), name="logout"),
    path('accounts/register/', core_views.SignupView.as_view(), name="sign_up"),
    path('accounts/apply/',core_views.CreateApplicationView.as_view(), name="apply"),
    path('confirm_email/', core_views.ConfirmEmailView.as_view(), name="confirm_email"),
]

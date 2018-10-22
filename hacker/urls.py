from django.urls import path, include
from . import views
from django.contrib.auth import login, authenticate
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home),
    path('login', views.login),
    path('register', views.register),
    path('status', views.dashboard.status),
    path('application', views.dashboard.application),
    path('team', views.dashboard.team),
    path('information', views.dashboard.information),
    path('logout', views.dashboard.logout)
]

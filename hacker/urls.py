from django.urls import path, include
from hacker import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('status', views.dashboard.status),
    path('application', views.dashboard.application),
    path('team', views.dashboard.team),
    path('information', views.dashboard.information),
]

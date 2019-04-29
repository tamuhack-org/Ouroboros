from django.urls import path, include
from hacker import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('status', views.dashboard.status, name="status"),
    path('application', views.dashboard.application, name="application"),
    path('team', views.dashboard.team, name="team"),
    path('information', views.dashboard.information, name="information"),
]

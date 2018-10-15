from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('login', views.login),
    path('register', views.signup),
    path('status', views.status),
]

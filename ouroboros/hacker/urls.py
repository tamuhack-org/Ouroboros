from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.contrib.auth.decorators import user_passes_test

from hacker import views as hacker_views

urlpatterns = [
    path("application/", hacker_views.ApplicationCreateView.as_view(), name="application_create"),
    path("application/<int:pk>", hacker_views.ApplicationUpdateView.as_view(), name="application_update"),
    path("status/", hacker_views.StatusView.as_view(), name="status"),
    path("rsvp/", hacker_views.RsvpView.as_view(), name="rsvp"),
]

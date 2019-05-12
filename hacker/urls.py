from django.contrib.auth import views as auth_views
from django.urls import include, path

from hacker import views as hacker_views

urlpatterns = [
    path("application/", hacker_views.ApplicationView.as_view(), name="application"),
    path("status/", hacker_views.StatusView.as_view(), name="status"),
    path("rsvp/", hacker_views.RsvpView.as_view(), name="rsvp"),
]

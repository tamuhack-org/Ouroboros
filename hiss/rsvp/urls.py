from django.urls import path

from rsvp import views

app_name = "rsvp"
urlpatterns = [
    path("", views.CreateRsvpView.as_view(), name="create"),
    path("<uuid:pk>", views.UpdateRsvpView.as_view(), name="update"),
    path("decline", views.DeclineRsvpView.as_view(), name="decline"),
]

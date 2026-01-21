from django.urls import path

from status import views

urlpatterns = [
    path("", views.StatusView.as_view(), name="status"),
    path("rsvp/<uuid:pk>/", views.RSVPSubmitView.as_view(), name="rsvp_submit"),
    path("confirmed/", views.ConfirmedCountView.as_view(), name="confirmed_count"),
]

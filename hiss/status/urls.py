from django.urls import path

from status import views
from team.views import TeamPageView

urlpatterns = [
    path("", views.StatusView.as_view(), name="status"),
    path("team/", TeamPageView.as_view(), name="status_team"),
    path("rsvp/<uuid:pk>/", views.RSVPSubmitView.as_view(), name="rsvp_submit"),
]

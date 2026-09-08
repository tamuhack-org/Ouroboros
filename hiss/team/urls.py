from django.urls import path

from team import views

app_name = "team"
urlpatterns = [
    path("join/", views.JoinTeamView.as_view(), name="join-code"),
    path("members/<uuid:pk>/promote", views.PromoteMemberView.as_view(), name="promote"),
    path("", views.MyTeamView.as_view(), name="my-team"),
    path(
        "members/<uuid:pk>/remove",
        views.RemoveMemberView.as_view(),
        name="remove_member",
    ),
    path("<uuid:pk>/delete", views.DeleteTeamView.as_view(), name="delete"),
    path("join/<uuid:pk>", views.JoinTeamView.as_view(), name="join"),
]

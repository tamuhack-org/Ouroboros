from django.urls import path

from team import views

app_name = "team"
urlpatterns = [
    path("", views.CreateTeamView.as_view(), name="create"),
    path(
        "members/<uuid:pk>/remove",
        views.RemoveMemberView.as_view(),
        name="remove_member",
    ),
    path("<uuid:pk>/delete", views.DeleteTeamView.as_view(), name="delete"),
    path("join/<uuid:pk>", views.JoinTeamView.as_view(), name="join")

]

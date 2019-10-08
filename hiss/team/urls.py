from django.urls import path

from team import views

urlpatterns = [
    path("", views.CreateTeamView.as_view(), name="create"),
    path("join", views.JoinTeamView.as_view(), name="join"),
    path("leave", views.LeaveTeamView.as_view(), name="leave"),
    path("<uuid:pk>", views.DetailTeamView.as_view(), name="detail"),
]
app_name = "team"

from django.urls import path

from team import views

app_name = "team"
urlpatterns = [
    path("", views.CreateTeamView.as_view(), name="create"),
    path("<uuid:pk>", views.DetailTeamView.as_view(), name="detail"),
    path("join", views.JoinTeamView.as_view(), name="join"),
]

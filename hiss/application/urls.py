from django.urls import path

from application import views

app_name = "application"
urlpatterns = [
    path("", views.CreateApplicationView.as_view(), name="create"),
    path("<uuid:pk>", views.UpdateApplicationView.as_view(), name="update"),
]

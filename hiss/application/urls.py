from django.urls import path

from application import views

urlpatterns = [
    path("", views.CreateApplicationView.as_view()),
    path("<uuid:pk>", views.UpdateApplicationView.as_view())
]

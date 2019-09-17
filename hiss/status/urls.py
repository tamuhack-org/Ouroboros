from django.urls import path

from status import views

urlpatterns = [path("", views.StatusView.as_view(), name="status")]

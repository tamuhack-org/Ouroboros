from django.urls import path

from volunteer import views

app_name = "volunteer"
urlpatterns = [
    path("login", views.EmailObtainAuthToken.as_view(), name="login"),
    path("checkin", views.CheckinHackerView.as_view(), name="user-checkin"),
]

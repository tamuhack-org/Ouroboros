from django.urls import path

from volunteer import views

# https://register.tamuhack.com/api/volunteer/<urlpath>

app_name = "volunteer"
urlpatterns = [
    path("login", views.EmailObtainAuthToken.as_view(), name="login"),
    path("verify", views.VerifyAuthenticatedView.as_view(), name="verify"),
    path("checkin", views.CheckinHackerView.as_view(), name="user-checkin"),
    path("food", views.CreateFoodEventView.as_view(), name="food"),
    path("workshops", views.CreateWorkshopEventView.as_view(), name="workshops"),
]

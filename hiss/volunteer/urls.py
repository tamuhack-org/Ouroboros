from django.urls import path

from volunteer import views

app_name = "volunteer"
urlpatterns = [
    path("login", views.EmailObtainAuthToken.as_view(), name="login"),
    path("verify", views.VerifyAuthenticated.as_view(), name="verify"),
    path("checkin", views.CheckinHackerView.as_view(), name="user-checkin"),
    path(
        "dietary_restrictions",
        views.ListDietaryRestrictionsView.as_view(),
        name="list-dietary-restrictions",
    ),
    path("food", views.CreateFoodEventView.as_view(), name="food"),
    path("workshops", views.CreateWorkshopEventView.as_view(), name="workshops"),
    path("search", views.SearchView.as_view(), name="search"),
    path("summary", views.UserSummaryView.as_view(), name="summary"),
]

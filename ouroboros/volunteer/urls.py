from django.urls import include, path
from volunteer import views
from volunteer.views import obtain_email_auth_token

urlpatterns = [
    path("", views.VolunteerApplicationView.as_view(), name="volunteer-signup"),
    path("login", obtain_email_auth_token, name="volunteer-login"),
    path("checkin", views.CheckinHackerView.as_view(), name="checkin-hacker"),
    path("food", views.CreateFoodEventView.as_view(), name="create-food-event"),
    path(
        "workshops",
        views.CreateWorkshopEventView.as_view(),
        name="create-workshop-event",
    ),
]

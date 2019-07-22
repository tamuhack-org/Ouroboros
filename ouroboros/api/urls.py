from django.urls import include, path
from api import views
from api.views import obtain_email_auth_token

urlpatterns = [
    path("login", obtain_email_auth_token, name="api-login"),
    path("checkin", views.CheckinHackerView.as_view(), name="checkin-hacker"),
    path("food", views.CreateFoodEventView.as_view(), name="create-food-event"),
    path("workshops", views.CreateWorkshopEventView.as_view(), name="create-workshop-event"),
]

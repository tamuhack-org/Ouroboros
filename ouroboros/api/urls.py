from django.urls import include, path
from api import views
from api.views import obtain_email_auth_token
urlpatterns = [path("login", obtain_email_auth_token, name="api-login")]


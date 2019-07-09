from django.shortcuts import render
from rest_framework.authtoken import views
from api.serializers import EmailAuthTokenSerializer

# Create your views here.
class EmailObtainAuthToken(views.ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

obtain_email_auth_token = EmailObtainAuthToken.as_view()
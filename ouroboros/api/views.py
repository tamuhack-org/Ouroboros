from django import shortcuts
from django.shortcuts import render
from rest_framework import authentication, permissions, status, response
from rest_framework.authtoken import views

from api import models
from api.serializers import EmailAuthTokenSerializer
from hacker import models as hacker_models


# Create your views here.
class EmailObtainAuthToken(views.ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer


obtain_email_auth_token = EmailObtainAuthToken.as_view()


class CreateFoodEvent(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, format=None):
        email = request.data.get("email", None)
        meal = request.data.get("meal", None)
        restrictions = request.data.get("restrictions", None)
        if not (email and meal and restrictions):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        hacker = None
        try:
            hacker = hacker_models.Hacker.objects.get(email=email)
        except hacker_models.Hacker.DoesNotExist:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        models.FoodEvent.objects.create(
            hacker=hacker, meal=meal, restrictions=restrictions
        )
        return response.Response(status=status.HTTP_200_OK)


class CreateWorkshopEvent(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, format=None):
        email = request.data.get("email", None)
        if not email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        hacker = None
        try:
            hacker = hacker_models.Hacker.objects.get(email=email)
        except hacker_models.Hacker.DoesNotExist:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        models.WorkshopEvent.objects.create(hacker=hacker)
        return response.Response(status=status.HTTP_200_OK)

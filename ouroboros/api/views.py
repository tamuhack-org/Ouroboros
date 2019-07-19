import json

from django import shortcuts
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import authentication, permissions, response, status
from rest_framework.authtoken import views

from api import models
from api.permissions import IsVolunteer
from api.serializers import EmailAuthTokenSerializer
from hacker import models as hacker_models

HACKER_NOT_CHECKED_IN_MSG = (
    "This hacker has not been checked in. Please find an organizer immediately."
)

# Create your views here.
class EmailObtainAuthToken(views.ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer


obtain_email_auth_token = EmailObtainAuthToken.as_view()


class CheckinHackerView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, format=None):
        """
        Sets a hacker as having checked into the event.
        """
        email = request.data.get("email", None)
        if not email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        hacker: hacker_models.Hacker = get_object_or_404(
            hacker_models.Hacker, email=email
        )

        hacker.checked_in = True
        hacker.save()
        return response.Response(status=status.HTTP_200_OK)

    def get(self, request, format=None):
        """
        Retrieves whether a hacker has checked in or not.
        """
        # TODO(SaltyQuetzals): Get email from query params of request
        email = request.GET.get("email")
        if not email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        hacker: hacker_models.Hacker = get_object_or_404(
            hacker_models.Hacker, email=email
        )
        return JsonResponse({"checked_in": True if hacker.checked_in else False})


class CreateFoodEventView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, format=None):
        """
        Creates a new entry for food events with hacker data.
        """
        email = request.data.get("email", None)
        meal = request.data.get("meal", None)
        restrictions = request.data.get("restrictions", None)
        if not (email and meal and restrictions):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        hacker = get_object_or_404(hacker_models.Hacker, email=email)

        if not hacker.checked_in:
            # This hacker somehow hasn't checked in!
            return response.Response(status=status.HTTP_412_PRECONDITION_FAILED)
        models.FoodEvent.objects.create(
            hacker=hacker, meal=meal, restrictions=restrictions
        )
        return response.Response(status=status.HTTP_200_OK)


class CreateWorkshopEventView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, format=None):
        email = request.data.get("email", None)
        if not email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        hacker: hacker_models.Hacker = get_object_or_404(
            hacker_models.Hacker, email=email
        )
        if not hacker.checked_in:
            return response.Response(
                data={"error": HACKER_NOT_CHECKED_IN_MSG},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        models.WorkshopEvent.objects.create(hacker=hacker)
        return response.Response(status=status.HTTP_200_OK)

# class SearchView(views.APIView):
#     permission_classes = [
#         permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
#     ]
#     authentication_classes = [authentication.TokenAuthentication]

#     def get(self, request, *args, **kwargs):
#         matches = hacker_models.Hacker.objects.annotate()
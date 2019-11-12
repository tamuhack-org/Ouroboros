from django.contrib.auth import get_user_model
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, response, permissions, authentication
from rest_framework.authtoken import views
from rest_framework.request import Request

from application.models import Application, STATUS_CHECKED_IN
from volunteer.models import (
    FoodEvent,
    WorkshopEvent,
    BREAKFAST,
    LUNCH,
    DINNER,
    MIDNIGHT_SNACK,
    BREAKFAST_2,
    LUNCH_2,
)
from volunteer.permissions import IsVolunteer
from volunteer.serializers import EmailAuthTokenSerializer

USER_NOT_CHECKED_IN_MSG = (
    "This hacker has not been checked in. Please find an organizer immediately."
)


class EmailObtainAuthToken(views.ObtainAuthToken):
    """
    Given a request containing a user's "email" and "password", this view responds with the user's Token (which can
    be used to authenticate consequent requests).

    More information on how `TokenAuthentication` works can be seen at the DRF documentation site:
    https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    """

    serializer_class = EmailAuthTokenSerializer


class CheckinHackerView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request: Request, format: str = None):
        """
        Sets a specific user's Application status as STATUS_CHECKED_IN (indicating that a user has successfully
        checked into the event). If the request is malformed (i.e. missing the user's email), returns a Django Rest
        Framework Response with a 400 status code. if successful, returns a response with status 200.
        """
        user_email = request.data.get("email", None)
        if not user_email:
            # The hacker's email was not provided in the request body, we can't do anything.
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        # Return 404 if no application exists for the provided user.
        application: Application = get_object_or_404(
            Application, user__email=user_email
        )
        application.status = STATUS_CHECKED_IN
        application.save()
        return response.Response(status=status.HTTP_200_OK)


class CreateFoodEventView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request: Request, format: str = None):
        """
        Creates a new FoodEvent (indicating that a user has taken food for this meal). If the request is malformed (
        i.e. missing the user's email, meal type, or restrictions), returns a Django Rest Framework Response with a
        400 status code. if successful, returns a response with status 200.
        """
        user_email = request.data.get("email", None)
        meal = request.data.get("meal", None)
        restrictions = request.data.get("restrictions", None)

        # Ensure that all required parameters are present
        if not (user_email and meal and restrictions):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        application: Application = get_object_or_404(
            Application, user__email=user_email
        )

        # Ensure that user has checked in
        if not application.status == STATUS_CHECKED_IN:
            return response.Response(
                data={"error": USER_NOT_CHECKED_IN_MSG},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        FoodEvent.objects.create(
            user=application.user, meal=meal, restrictions=restrictions
        )
        return response.Response(status=status.HTTP_200_OK)


class CreateWorkshopEventView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request: Request, format: str = None):
        """
        Creates a new WorkshopEvent (indicating that a user has attended a workshop). If the request is malformed (
        i.e. missing the user's email), returns a Django Rest Framework Response with a 400 status code. if
        successful, returns a response with status 200.
        """
        user_email = request.data.get("email", None)

        # Ensure that all required parameters are present
        if not user_email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        application: Application = get_object_or_404(
            Application, user__email=user_email
        )

        # Ensure that user has checked in
        if not application.status == STATUS_CHECKED_IN:
            return response.Response(
                data={"error": USER_NOT_CHECKED_IN_MSG},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        WorkshopEvent.objects.create(user=application.user)
        return response.Response(status=status.HTTP_200_OK)


class SearchView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, *args, **kwargs):
        """
        Performs a simple regex search for a matching application based on the user's first and last name. Creates a
        new temporary column called "full_name" which is just "<FIRST_NAME> <LAST_NAME>", and then regex-searches the
        query against the column, and returns all matches.
        """
        query = request.GET.get("q")
        matches = list(
            Application.objects.annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            )
            .filter(full_name__icontains=query)
            .values("first_name", "last_name", email=F("user__email"))
        )
        return JsonResponse({"results": matches})


class UserSummaryView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, *args, **kwargs):
        """
        Compiles a summary about a specific user, given their email, and returns that summary as JSON. If the request
        is malformed (i.e. missing the user's email), returns a Django Rest Framework Response with a 400 status
        code. if successful, returns a response with status 200.
        """
        user_email = request.GET.get("email")

        user = get_object_or_404(get_user_model(), email=user_email)
        application: Application = get_object_or_404(
            Application, user__email=user_email
        )

        food_events = FoodEvent.objects.filter(user=user)
        workshop_events = WorkshopEvent.objects.filter(user=user)
        checked_in = application.status == STATUS_CHECKED_IN

        return JsonResponse(
            {
                "num_breakfast": food_events.filter(meal=BREAKFAST).count(),
                "num_lunch": food_events.filter(meal=LUNCH).count(),
                "num_dinner": food_events.filter(meal=DINNER).count(),
                "num_midnight_snack": food_events.filter(meal=MIDNIGHT_SNACK).count(),
                "num_breakfast_2": food_events.filter(meal=BREAKFAST_2).count(),
                "num_lunch_2": food_events.filter(meal=LUNCH_2).count(),
                "num_workshops": workshop_events.count(),
                "checked_in": checked_in,
                "restrictions": application.dietary_restrictions,
            }
        )

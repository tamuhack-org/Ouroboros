from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, response, status
from rest_framework.authtoken import views
from rest_framework.request import Request

from application.models import STATUS_CHECKED_IN, Application
from volunteer.models import FoodEvent, WorkshopEvent
from volunteer.serializers import EmailAuthTokenSerializer
from judgesmentors.models import Judge, Mentor, STATUS_CHECKED_IN as JM_STATUS_CHECKED_IN

USER_NOT_CHECKED_IN_MSG = (
    "This hacker has not been checked in. Please find an organizer immediately."
)


class EmailObtainAuthToken(views.ObtainAuthToken):
    """Given a request containing a user's "email" and "password", this view responds with the user's Token (which can
    be used to authenticate consequent requests).

    More information on how `TokenAuthentication` works can be seen at the DRF documentation site:
    https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    """

    serializer_class = EmailAuthTokenSerializer


class VerifyAuthenticatedView(views.APIView):
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, format: str = None):
        """See if a user's token is valid and if they are authorized to use the API.
        This is a certified workaround-because-i-need-auth-but-i-don't-want-to-learn-django moment.
        Love, Naveen <3

        This will return
            200 if the user is logged in and is authorized
            401 if the user is not logged in (i.e. the token is invalid or missing)
            403 if the user is logged in (token is valid) but is not authorized

        BTW these requests expect the "Authorization" header to be set to "Token <token>"
        """
        return response.Response(status=status.HTTP_200_OK)


class CheckinHackerView(views.APIView):
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, format: str = None):
        """Returns the checkin status of a specific user. If the request is malformed (i.e. missing the user's email),
        returns a Django Rest Framework Response with a 400 status code. if successful, returns a response with status
        200.
        """
        user_email = request.GET.get("email", None)
        if not user_email:
            # The hacker's email was not provided in the request body, we can't do anything.
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            application: Application = Application.objects.get(user__email=user_email)
            return JsonResponse(
                {
                    "checkinStatus": application.status,
                    "wares": application.wares if application.wares else "None",
                    "first_name": application.first_name,
                    "last_name": application.last_name,
                }
            )
        except Application.DoesNotExist:
            # If no application found, try judges and mentors
            pass
        
        # Try to find judge
        try:
            judge = Judge.objects.get(user__email=user_email)
            name_parts = judge.name.split()
            first_name = name_parts[0] if name_parts else 'Judge'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            return JsonResponse({
                "checkinStatus": judge.status,
                "first_name": first_name,
                "last_name": last_name,
                "wares": "None",
            })
        except Judge.DoesNotExist:
            pass
            
        # Try to find mentor
        try:
            mentor = Mentor.objects.get(user__email=user_email)
            name_parts = mentor.name.split()
            first_name = name_parts[0] if name_parts else 'Mentor'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            return JsonResponse({
                "checkinStatus": mentor.status,
                "first_name": first_name,
                "last_name": last_name,
                "wares": "None",  # Keep same response format
            })
        except Mentor.DoesNotExist:
            pass
        
        return response.Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request: Request, format: str = None):
        """Sets a specific user's Application status as STATUS_CHECKED_IN (indicating that a user has successfully
        checked into the event). If the request is malformed (i.e. missing the user's email), returns a Django Rest
        Framework Response with a 400 status code. if successful, returns a response with status 200.
        """
        user_email = request.data.get("email", None)
        if not user_email:
            # The hacker's email was not provided in the request body, we can't do anything.
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            application: Application = Application.objects.get(user__email=user_email)
            application.status = STATUS_CHECKED_IN
            application.save()
            return response.Response(status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            # If no application found, try judges and mentors
            pass
        
        try:
            judge = Judge.objects.get(user__email=user_email)
            judge.status = JM_STATUS_CHECKED_IN
            judge.save()
            return response.Response(status=status.HTTP_200_OK)
        except Judge.DoesNotExist:
            pass
            
        try:
            mentor = Mentor.objects.get(user__email=user_email)
            mentor.status = JM_STATUS_CHECKED_IN
            mentor.save()
            return response.Response(status=status.HTTP_200_OK)
        except Mentor.DoesNotExist:
            pass
        
        return response.Response(status=status.HTTP_404_NOT_FOUND)


class CreateFoodEventView(views.APIView):
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, format: str = None):
        """Returns a list of all FoodEvents belonging to a specific user. If the request is malformed (i.e. missing the
        user's email), returns a Django Rest Framework Response with a 400 status code. if successful, returns a response
        with status 200.
        """
        user_email = request.GET.get("email", None)
        if not user_email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(get_user_model(), email=user_email)
        application = get_object_or_404(Application, user__email=user_email)

        food_events = FoodEvent.objects.filter(user=user)
        # Just a list of the "meal" fields for all FoodEvents
        meal_codes = [event.meal for event in food_events]

        return JsonResponse(
            {
                "mealScans": meal_codes,
                "dietaryRestrictions": application.dietary_restrictions,
                "mealGroup": application.meal_group,
            }
        )

    def post(self, request: Request, format: str = None):
        """Creates a new FoodEvent (indicating that a user has taken food for this meal). If the request is malformed (
        i.e. missing the user's email, meal type, or restrictions), returns a Django Rest Framework Response with a
        400 status code. if successful, returns a response with status 200.
        """
        user_email = request.data.get("email", None)
        meal = request.data.get("meal", None)

        # Ensure that all required parameters are present
        if not (user_email and meal):
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

        food_event = FoodEvent.objects.create(user=application.user, meal=meal)
        food_event.save()
        return response.Response(status=status.HTTP_200_OK)


class CreateWorkshopEventView(views.APIView):
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request: Request, format: str = None):
        """Returns the time of most recent workshop event for a specific user. If the request is malformed (i.e. missing
        the user's email), returns a Django Rest Framework Response with a 400 status code. if successful, returns a
        response with status 200.
        """
        user_email = request.GET.get("email", None)
        if not user_email:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(get_user_model(), email=user_email)
        workshop_events = WorkshopEvent.objects.filter(user=user)
        if workshop_events:
            last_workshop_event = workshop_events.latest("timestamp")
            return JsonResponse({"lastWorkshopScan": last_workshop_event.timestamp})
        return JsonResponse({"lastWorkshopScan": None})

    def post(self, request: Request, format: str = None):
        """Creates a new WorkshopEvent (indicating that a user has attended a workshop). If the request is malformed (
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

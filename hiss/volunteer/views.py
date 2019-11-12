from django.shortcuts import get_object_or_404
from rest_framework import status, response
from rest_framework.authtoken import views
from rest_framework.request import Request

from application.models import Application, STATUS_CHECKED_IN
from volunteer.serializers import EmailAuthTokenSerializer


class EmailObtainAuthToken(views.ObtainAuthToken):
    """
    Given a request containing a user's "email" and "password", this view responds with the user's Token (which can
    be used to authenticate consequent requests).

    More information on how `TokenAuthentication` works can be seen at the DRF documentation site:
    https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    """

    serializer_class = EmailAuthTokenSerializer


class CheckinHackerView(views.APIView):
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

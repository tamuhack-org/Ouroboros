import json

from django import shortcuts
from django.conf import settings
from django.contrib.auth import mixins
from django.contrib.auth.models import Group
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import authentication, permissions, response, status
from rest_framework.authtoken import views
from django import http

from hacker import models as hacker_models
from shared.views import CreateUpdateView
from volunteer import models
from volunteer.forms import VolunteerApplicationModelForm
from volunteer.permissions import IsVolunteer
from volunteer.serializers import EmailAuthTokenSerializer

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


class SearchView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated & (IsVolunteer | permissions.IsAdminUser)
    ]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        matches = list(
            hacker_models.Application.objects.annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            )
            .filter(full_name__icontains=query)
            .values("first_name", "last_name", email=F("hacker__email"))
        )
        return http.JsonResponse(data={"results": matches})


class VolunteerApplicationView(mixins.LoginRequiredMixin, CreateUpdateView):
    success_url = reverse_lazy("status")

    form_class = VolunteerApplicationModelForm
    template_name = "volunteer/signup.html"

    def get_object(self):
        if getattr(self.request.user, "volunteer_app", None) is None:
            return None
        return self.request.user.volunteer_app

    def form_valid(self, form: VolunteerApplicationModelForm):
        volunteer_application: models.VolunteerApplication = form.save(commit=False)
        volunteer_application.hacker = self.request.user
        volunteer_application.save()
        volunteer_application.shifts.set(form.cleaned_data["shifts"])
        return super().form_valid(form)

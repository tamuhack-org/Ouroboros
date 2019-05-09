from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, render_to_response
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic as generic_views
from django.views.generic import base as base_views

from hacker import forms as hacker_forms
from hacker import models as hacker_models


def email_confirmation_check(user):
    return user.has_confirmed_email() 

def has_application_check(user):
    return user.has_related_application()

def has_confirmation_check(user):
    return user.has_related_confirmation()

def has_team_check(user):
    return user.has_related_team()


class dashboard(LoginRequiredMixin):
    login_url = reverse_lazy("login")
    redirect_field_name = reverse_lazy("status")
    
    @login_required
    @user_passes_test(email_confirmation_check, reverse_lazy("confirm_email"))
    @user_passes_test(has_application_check, reverse_lazy("apply"))
    def status(request):
        redirect_field_name = reverse_lazy("status")
        return render(request, 'dashboard/status.html')
    
    @login_required
    @user_passes_test(email_confirmation_check, reverse_lazy("confirm_email"))
    @user_passes_test(has_application_check, reverse_lazy("apply"))
    def application(request):
        redirect_field_name = reverse_lazy("application")
        return render(request, 'dashboard/application.html')

    @login_required
    @user_passes_test(email_confirmation_check, reverse_lazy("confirm_email"))
    @user_passes_test(has_application_check, reverse_lazy("apply"))
    #@user_passes_test(has_confirmation_check, settings.CREATE_CONFIRMATION_URL)
    #@user_passes_test(has_team_check, ______)
    def team(request):
        redirect_field_name = reverse_lazy("team")
        return render(request, 'dashboard/team.html')
    
    @login_required
    @user_passes_test(email_confirmation_check, reverse_lazy("confirm_email"))
    @user_passes_test(has_application_check, reverse_lazy("apply"))
    def information(request):
        redirect_field_name = reverse_lazy("information")
        return render(request, 'dashboard/information.html')

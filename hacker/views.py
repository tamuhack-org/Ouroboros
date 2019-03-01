from django.shortcuts import render, redirect, render_to_response
from django.views.generic import base as base_views
from django.views import generic as generic_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from core import forms as core_forms
from hacker import models as hacker_models


def email_confirmation_check(user):
    return user.has_confirmed_email() 

def completed_application(user):
    return user.has_related_application()

class dashboard(LoginRequiredMixin):
    login_url = settings.LOGIN_URL
    redirect_field_name = settings.LOGIN_REDIRECT_URL
    
    @login_required
    @user_passes_test(email_confirmation_check,settings.SIGNUP_REDIRECT_URL)
    @user_passes_test(completed_application, settings.VIEW_APPLICATION_URL)
    def status(request):
        return render(request, 'dashboard/status.html')
    
    @login_required
    @user_passes_test(email_confirmation_check,settings.SIGNUP_REDIRECT_URL)
    def application(request):
        redirect_field_name = '/application'

        return render(request, 'dashboard/application.html')
    
    @login_required
    @user_passes_test(email_confirmation_check,settings.SIGNUP_REDIRECT_URL)
    @user_passes_test(completed_application, settings.VIEW_APPLICATION_URL)
    def team(request):
        redirect_field_name = '/team'
        return render(request, 'dashboard/team.html')
    
    @login_required
    @user_passes_test(email_confirmation_check,settings.SIGNUP_REDIRECT_URL)
    def information(request):
        redirect_field_name = '/information'
        return render(request, 'dashboard/information.html')


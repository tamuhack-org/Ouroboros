import json
import pdb
import urllib.parse as urlparse
#from access_tokens import tokens

from django import http
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic as generic_views
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import RedirectView
from django.views.generic import base as base_views

from hacker import forms as hacker_forms
from hacker import models as hacker_models


class IndexView(base_views.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HackerLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = hacker_forms.HackerLoginForm
    redirect_authenticated_user = True


class HackerLogoutView(LogoutView):
    template_name = 'index.html'
    redirect_authenticated_user = True


class SignupView(generic_views.FormView):
    form_class = hacker_forms.SignupForm
    template_name = 'registration/signup.html'

    def email_exists(self, form):
        return (hacker_models.Hacker.objects.filter(email=form.cleaned_data.get('email')).exists())

    def form_valid(self, form):
        form.full_clean()
        form.save()
        return super(SignupView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})

    def send_confirmation_email(self):
        user = self.request.user
        user.generate_confirm_code()
        content = 'Almost there ' + user.first_name + '! Use the following confirmation code to confirm your email: ' + user.confirm_code
        send_mail('Confirm your email!', content, settings.EMAIL_HOST_USER, [user.email])
        hacker_models.Hacker.objects.filter(email=user.email).update(confirm_code=user.confirm_code)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user_exists = False
        if form.is_valid():
            if (not self.email_exists(form)):
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1') 
                user = authenticate(username=username, password=raw_password)
                auth_login(request, user)
                self.send_confirmation_email()
                return redirect(reverse_lazy("confirm_email"))
            else:
                user_exists = True 
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors, 'user_exists':user_exists})


class ConfirmEmailView(generic_views.FormView, LoginRequiredMixin):
    form_class = hacker_forms.ConfirmEmailForm
    template_name = hacker_forms.ConfirmEmailForm.template_name
    success_url = hacker_forms.ConfirmEmailForm.success_url

    def form_valid(self, form):
        form.full_clean()
        return super(ConfirmEmailView, self).form_valid(form)
    
    def code_invalid(self, form):
        return render(self.request, self.template_name, {'invalid_code': True})

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        invalid_code = False
        if form.is_valid():
            email = form.cleaned_data.get('email')
            code = form.cleaned_data.get('confirm_code')
            hacker = hacker_models.Hacker.objects.get(email=email)
            if hacker.confirm_email(code):
                # given confirm_code is correct
                hacker_models.Hacker.objects.filter(email=email).update(confirm_code=None)
                hacker_models.Hacker.objects.filter(email=email).update(email_confirmed=True)
                return redirect(reverse_lazy("apply"))
            else:
                # given confirm_code is NOT correct
                # ...
                return self.code_invalid(form)
            
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors, 'invalid_code':invalid_code})
        

class CreateApplicationView(generic_views.CreateView, LoginRequiredMixin):
    model = hacker_models.Application
    success_url = reverse_lazy("status")
    template_used = 'hacker/application_form.html'
    fields = [
        "major", "gender", "classification", "grad_year", "dietary_restrictions", "num_hackathons_attended", "previous_attendant", "tamu_student", "interests", "essay1", "notes", "resume"
    ]

    grad_options = [op[0] for op in hacker_models.GRAD_YEARS]
    student_classifications = [op[0] for op in hacker_models.CLASSIFICATIONS]
    gender_options = hacker_models.GENDERS
    
    def get_context_data(self, **kwargs):
        context = super(CreateApplicationView, self).get_context_data(**kwargs)
        context['grad_options'] = self.grad_options
        context['student_classifications'] = self.student_classifications
        context['gender_options'] = self.gender_options
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.hacker = self.request.user
        obj.save()
        return http.HttpResponseRedirect(self.success_url)


class CreateConfirmationView(generic_views.CreateView, LoginRequiredMixin):
    model = hacker_models.Confirmation
    success_url = reverse_lazy("status")
    fields = [
        "shirt_size",
        "notes"
    ]    

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.hacker = self.request.user
        obj.save()
        return http.HttpResponseRedirect(self.get_success_url())
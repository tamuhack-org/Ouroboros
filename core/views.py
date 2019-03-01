from django.contrib.auth import forms as auth_forms
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views import generic as generic_views
from django.views.generic import base as base_views, RedirectView
from core import forms as core_forms
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from hacker import models as hacker_models
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
import pdb

try:
    import urlparse                     # if using python2
except ImportError:
    import urllib.parse as urlparse     # if using python3 

import json


class IndexView(base_views.TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SignupView(generic_views.FormView):

    form_class = core_forms.SignupForm
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

    # 'recipient_hacker' should be the `Hacker` model receiving the email
    def send_confirmation_email(self, recipient_hacker):
        recipient_hacker.generate_confirm_code()
        to_email = getattr(recipient_hacker, 'email', None)
        confirm_code = getattr(recipient_hacker, 'confirm_code', None)
        first_name = getattr(recipient_hacker, 'first_name', None)
        if to_email is not None and confirm_code is not None:
            email_content = 'Almost there ' + first_name + '! Use the following confirmation code to confirm your email: ' + confirm_code
            send_mail('Confirm you email!', email_content, settings.EMAIL_HOST_USER, [to_email])
            hacker_models.Hacker.objects.filter(email=to_email).update(confirm_code=confirm_code)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user_exists = False
        if form.is_valid():
            if (not self.email_exists(form)):
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1') 
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                hacker = hacker_models.Hacker.objects.get(username=username)
                # call the 'send_confirmation_email' function to send a confirmation email
                self.send_confirmation_email(hacker)
                return redirect(settings.SIGNUP_REDIRECT_URL)
            else:
                user_exists = True 
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors, 'user_exists':user_exists})


class SignInView(generic_views.FormView):
    form_class = core_forms.SignInForm
    template_name = 'registration/login.html'
    success_url = core_forms.SignInForm.success_url   #!!!
    redirect_field_name = core_forms.SignInForm.redirect_field_name

    # references: https://gist.github.com/stefanfoulis/1140136 , https://coderwall.com/p/sll1kw/django-auth-class-based-views-login-and-logout
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(SignInView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log them in.
        """
        login(self.request, form.get_user())
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        return render(self.request, self.template_name, {'invalid_form': True})

    def get_success_url(self):      #!!!!!!!!!
        return self.success_url

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):   #!!!!!!!!!
        if (request.user.is_authenticated):
            return redirect(self.get_success_url())
        form = self.form_class(initial=self.initial)
        self.set_test_cookie()
        return super(SignInView, self).get(request, *args, **kwargs)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)

class LogOutView(RedirectView):
    url = "/"

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)


class ConfirmEmailView(generic_views.FormView):

    form_class = core_forms.ConfirmEmailForm
    template_name = core_forms.ConfirmEmailForm.template_name
    success_url = core_forms.ConfirmEmailForm.success_url

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
                return redirect(settings.CONFIRM_EMAIL_REDIRECT_URL)
            else:
                # given confirm_code is NOT correct
                # ...
                return self.code_invalid(form)
            
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors, 'invalid_code':invalid_code})
        

class CreateApplicationView(generic_views.FormView):

    form_class = core_forms.CreateApplicationForm
    template_name = core_forms.CreateApplicationForm.template_name
    success_url = core_forms.CreateApplicationForm.success_url

    yearOptionsList = [op[0] for op in settings.GRAD_YEAR_CHOICES]

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)        # get form data
        return render(request, self.template_name, {'form': form, 'grad_options': self.yearOptionsList, 'student_classifications': settings.STUDENT_CLASSIFICATIONS})

    def form_valid(self, form):
        form.full_clean()
        return super(CreateApplicationView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        post_q_dict = request.POST.copy()       # get form data
        post_dict = post_q_dict.dict()          # convert from 'QueryDict' data type to 'dict' data type
        post_dict.update({'hacker': request.user.id})       # pass 'hacker' field into form data
        form = self.form_class(post_dict)       # instantiate 'CreateApplicationForm' using form data

        if form.is_valid():
            form.save()         # save instance of 'Application' to database
            return redirect(self.success_url) 

        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form': form, 'FormErrors':FormErrors})
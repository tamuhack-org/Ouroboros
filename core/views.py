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

    def form_valid(self, form):
        form.full_clean()
        form.save()
        return super(SignupView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})

    # 'to_email' is the email-address that the email is being sent to
    def send_confirmation_email(self, to_email):
        hacker = hacker_models.Hacker.objects.get(email=to_email)
        hacker.generate_confirm_code()
        confirm_code = getattr(hacker, 'confirm_code', None)
        first_name = getattr(hacker, 'first_name', None)
        hacker_models.Hacker.objects.filter(email=to_email).update(confirm_code=confirm_code)
        if to_email is not None and confirm_code is not None:
            email_content = 'Almost there ' + first_name + '! Use the following confirmation code to confirm your email: ' + confirm_code
            send_mail('Confirm you email!', email_content, settings.EMAIL_HOST_USER, [to_email])

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')            
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            self.send_confirmation_email(email)
            return redirect(settings.SIGNUP_REDIRECT_URL)
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors})


class SignInView(generic_views.FormView):
    form_class = core_forms.SignInForm
    template_name = 'registration/login.html'
    success_url = core_forms.SignInForm.success_url
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

    def get_success_url(self):
        return self.success_url

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
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
    success_url = core_forms.ConfirmEmailForm.template_name

    def form_valid(self, form):
        form.full_clean()
        #form.save()
        return super(ConfirmEmailView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            #form.save()
            email = form.cleaned_data.get('email')
            code = form.cleaned_data.get('confirm_code')
            hacker = hacker_models.Hacker.objects.get(email=email)
            if hacker.confirm_email(code):
                # given confirm_code is correct
                # ...
                return redirect('/status')
            else:
                # given confirm_code is NOT correct
                # ...
                return redirect('/confirm_email')
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors})
        
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

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1') 
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors})


class SignInView(generic_views.FormView):
    form_class = core_forms.SignInForm
    template_name = 'registration/login.html'
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
        if self.success_url:
            print("success url")
            redirect_to = self.success_url
        else:
            print("redirect_field")
            redirect_to = self.request.GET.get(self.redirect_field_name, '')
        
        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        # Security check -- don't allow redirection to a different host.
        elif netloc and netloc != self.request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL
        return redirect_to

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False


    def get(self, request, *args, **kwargs):
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

        '''
        form.is_valid()
        username = request.POST['username']
        raw_password = request.POST['password']
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(request, user)
            return redirect('/status')
        FormErrors = json.loads(form.errors.as_json())
        print(FormErrors)
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors})
        '''

class LogOutView(RedirectView):
    url = "/"

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import authenticate, login
from django.views import generic as generic_views
from django.views.generic import base as base_views
from core import forms as core_forms
from django.shortcuts import render, redirect
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
            return redirect('/application')
        FormErrors = json.loads(form.errors.as_json())
        return render(request, self.template_name, {'form':form, 'FormErrors':FormErrors})

from django.contrib.auth import forms as auth_forms
from django.views import generic as generic_views
from django.views.generic import base as base_views
from core import forms as core_forms

class IndexView(base_views.TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context

class SignupView(generic_views.FormView):

    form_class = core_forms.SignupForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.full_clean()
        form.save()
        return super(SignupView, self).form_valid(form)

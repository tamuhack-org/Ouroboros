from django import forms
from django.contrib.auth import mixins
from django.core import exceptions
from django.shortcuts import redirect
from django.urls import reverse_lazy

from user import models as user_models
from application import forms as application_forms
from shared.views import CreateUpdateView

class ApplicationView(mixins.LoginRequiredMixin, CreateUpdateView):
    template_name = "hacker/application.html"
    form_class = application_forms.ApplicationModelForm
    success_url = reverse_lazy("status")
    queryset = user_models.Application.objects.all()

    def get_object(self):
        if getattr(self.request.user, "application", None) is None:
            return None
        return self.request.user.application

    def form_valid(self, form: forms.Form):
        application: user_models.Application = form.save(commit=False)
        if application.approved:
            form.add_error(
                None,
                "Your application has already been approved, no further changes are allowed.",
            )
            return self.form_invalid(form)
        application.hacker = self.request.user
        application.wave = user_models.Wave.objects.active_wave()
        application.save()
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if not user_models.Wave.objects.active_wave():
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not user_models.Wave.objects.active_wave():
            raise exceptions.PermissionDenied(
                "Applications can only be submitted during a registration wave."
            )
        if request.user.cant_make_it:
            raise exceptions.PermissionDenied(
                "Applications can't be updated after declining admission."
            )
        return super().post(request, *args, **kwargs)

    class Meta:
        model = user_models.Application
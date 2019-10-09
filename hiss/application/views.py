from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from application.forms import ApplicationModelForm
from application.models import Application, Wave


class CreateApplicationView(mixins.LoginRequiredMixin, generic.CreateView):
    """
    Creates a new Application and links it to a User if one doesn't already exist and the User's not already
    applied to be a volunteer.
    """

    form_class = ApplicationModelForm
    template_name = "application/application_form.html"
    success_url = reverse_lazy("status")

    def form_valid(self, form: ApplicationModelForm):
        if Application.objects.filter(user=self.request.user).exists():
            form.add_error(None, "You can only submit one application to this event.")
            return self.form_invalid(form)
        application: Application = form.save(commit=False)
        application.user = self.request.user
        application.wave = Wave.objects.active_wave()
        application.save()
        return redirect(self.success_url)


class UpdateApplicationView(mixins.LoginRequiredMixin, generic.UpdateView):
    """
    Updates a linked Application. Updating an Application does not change the Wave it was originally submitted
    during.
    """

    queryset = Application.objects.all()
    form_class = ApplicationModelForm
    template_name = "application/application_form.html"

    def get_object(self, queryset=None) -> Application:
        """
        Checks to make sure that the user actually owns the application requested.
        """
        app: Application = super().get_object()
        if app.user != self.request.user:
            raise PermissionDenied("You don't have permission to view this application")
        return app

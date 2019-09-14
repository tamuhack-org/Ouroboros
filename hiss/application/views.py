from django.contrib.auth import mixins
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from application.forms import ApplicationModelForm
from application.models import Application, Wave


class CreateApplicationView(mixins.LoginRequiredMixin, generic.CreateView):
    """Creates a new Application and links it to a User if one doesn't already exist and the User's not already
    applied to be a volunteer."""
    form_class = ApplicationModelForm
    template_name = "application/application_form.html"
    success_url = reverse_lazy("status")

    def form_valid(self, form: ApplicationModelForm):
        application: Application = form.save(commit=False)
        application.wave = Wave.objects.active_wave()
        application.user = self.request.user
        application.save()
        return redirect(self.success_url)


class UpdateApplicationView(generic.UpdateView):
    """Updates a linked Application. Updating an Application does not change the Wave it was originally submitted
    during. """
    form_class = ApplicationModelForm
    template_name = "application/application_form.html"

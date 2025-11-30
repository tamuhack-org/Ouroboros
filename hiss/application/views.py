from django import views
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from application.constants import STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_DECLINED
from application.emails import send_confirmation_email, send_creation_email
from application.forms import InitialRegistrationForm
from application.models import (
    Application,
    Wave,
)


class CreateApplicationView(mixins.LoginRequiredMixin, generic.CreateView):
    """Create a new Application and link it to a User.

    Checks if an Application doesn't already exist and the User's not already applied to be a volunteer.
    """

    form_class = InitialRegistrationForm
    template_name = "application/application_form.html"
    success_url = reverse_lazy("status")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_wave"] = Wave.objects.active_wave()
        return context

    def form_valid(self, form: InitialRegistrationForm):
        try:
            if Application.objects.filter(user=self.request.user).exists():
                form.add_error(
                    None, "You can only submit one application to this event."
                )
                return self.form_invalid(form)
            application: Application = form.save(commit=False)
            application.user = self.request.user
            application.wave = Wave.objects.active_wave()
            application.save()
            send_creation_email(application)

        except Exception as e:
            print(f"Exception: {e}", flush=True)
            raise
        return redirect(self.success_url)


class UpdateApplicationView(mixins.LoginRequiredMixin, generic.UpdateView):
    """Update a linked Application.

    Updating an Application does not change the Wave it was originally submittedduring.
    """

    queryset = Application.objects.all()
    form_class = InitialRegistrationForm
    template_name = "application/application_form.html"
    success_url = reverse_lazy("status")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_wave"] = Wave.objects.active_wave()
        return context

    def get_object(self, _queryset: QuerySet = None) -> Application:
        """Check to make sure that the user actually owns the application requested."""
        app: Application = super().get_object()
        if self.request.user.is_superuser:
            return app
        if app.user != self.request.user:
            msg = "You don't have permission to view this application"
            raise PermissionDenied(msg)
        return app


class ConfirmApplicationView(mixins.LoginRequiredMixin, views.View):
    """Change an application's status from STATUS_ADMITTED to STATUS_CONFIRMED."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)
        if app.status == STATUS_CONFIRMED:
            # Do nothing, they already confirmed.
            return redirect(reverse_lazy("status"))
        if app.user != request.user:
            msg = "You don't have permission to view this application."
            raise PermissionDenied(
                msg
            )
        if app.status != STATUS_ADMITTED:
            msg = "You can't confirm your application if it hasn't been approved."
            raise PermissionDenied(
                msg
            )
        app.status = STATUS_CONFIRMED
        app.save()
        send_confirmation_email(app)
        return redirect(reverse_lazy("status"))


class DeclineApplicationView(mixins.LoginRequiredMixin, views.View):
    """Changes an application's status from STATUS_ADMITTED to STATUS_DECLINED."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)
        if app.status == STATUS_DECLINED:
            # Do nothing, they already declined
            return redirect(reverse_lazy("status"))
        if app.user != request.user:
            msg = "You don't have permission to view this application."
            raise PermissionDenied(
                msg
            )
        if app.status not in (STATUS_ADMITTED, STATUS_CONFIRMED):
            msg = "You can't decline your spot if it hasn't been approved."
            raise PermissionDenied(
                msg
            )
        app.status = STATUS_DECLINED
        app.save()
        return redirect(reverse_lazy("status"))

import structlog
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

logger = structlog.get_logger()


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
                logger.info(
                    "User attempted duplicate application", user_pk=self.request.user.pk
                )
                return self.form_invalid(form)
            logger.info("Creating application for user", user_pk=self.request.user.pk)
            application: Application = form.save(commit=False)
            application.user = self.request.user
            application.wave = Wave.objects.active_wave()
            application.save()
            logger.info(
                "Created application for user",
                application_pk=application.pk,
                user_pk=self.request.user.pk,
            )
            send_creation_email(application)

        except Exception:
            logger.exception("Exception while creating application")
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

    def get_object(self, queryset: QuerySet | None = None) -> Application:  # type: ignore[override]
        """Check to make sure that the user actually owns the application requested."""
        app: Application = super().get_object(queryset)
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
            logger.info("Application already confirmed", app_pk=app.pk)
            return redirect(reverse_lazy("status"))
        if app.user != request.user:
            msg = "You don't have permission to view this application."
            logger.warning(
                "User attempted to confirm application they do not own",
                user_pk=request.user.pk,
                app_pk=app.pk,
            )
            raise PermissionDenied(msg)
        if app.status != STATUS_ADMITTED:
            msg = "You can't confirm your application if it hasn't been approved."
            logger.warning(
                "Application status not eligible for confirm",
                app_pk=app.pk,
                status=app.status,
            )
            raise PermissionDenied(msg)
        if app.status == STATUS_ADMITTED and app.is_past_confirmation_deadline:
            msg = (
                "You can't confirm your application after the confirmation deadline. "
                "Since the deadline has passed, you'll be moved to the waitlist. Please keep "
                "an eye on your email for any updates."
            )
            logger.warning("Application attempted confirm after deadline", app_pk=app.pk)
            raise PermissionDenied(msg)

        app.status = STATUS_CONFIRMED
        app.save()
        logger.info("Application confirmed", app_pk=app.pk)
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
            raise PermissionDenied(msg)
        if app.status not in (STATUS_ADMITTED, STATUS_CONFIRMED):
            msg = "You can't decline your spot if it hasn't been approved."
            raise PermissionDenied(msg)
        app.status = STATUS_DECLINED
        app.save()
        return redirect(reverse_lazy("status"))

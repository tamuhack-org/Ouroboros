from django.conf import settings
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

import application.constants
from application.emails import send_confirmation_email
from application.forms import RSVPConfirmationForm
from application.models import Application, Wave
from user.models import User

class StatusView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "status/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organizer_email"] = settings.ORGANIZER_EMAIL
        user: User = self.request.user

        active_wave = Wave.objects.active_wave()
        user_has_app = user.application_set.exists()

        if not active_wave and not user_has_app:
            next_wave = Wave.objects.next_wave()
            if not next_wave:
                context["NO_MORE_WAVES"] = True
            else:
                context["WAIT_UNTIL_NEXT_WAVE"] = True
                context["next_wave_start"] = next_wave.start
            return context

        if active_wave:
            context["active_wave_end"] = active_wave.end

        if not user_has_app:
            context["NOT_APPLIED"] = True
            return context

        app: Application = user.application_set.first()
        context["application"] = app
        status = app.status

        if status == application.constants.STATUS_ADMITTED:
            context["confirmation_deadline"] = app.confirmation_deadline
            context["rsvp_form"] = RSVPConfirmationForm(instance=app)

        status_map = {
            application.constants.STATUS_PENDING: "PENDING",
            application.constants.STATUS_REJECTED: "REJECTED",
            application.constants.STATUS_CONFIRMED: "CONFIRMED",
            application.constants.STATUS_DECLINED: "DECLINED",
            application.constants.STATUS_CHECKED_IN: "CHECKED_IN",
            application.constants.STATUS_EXPIRED: "EXPIRED",
        }

        if status == application.constants.STATUS_ADMITTED:
            if app.confirmation_deadline and app.is_past_confirmation_deadline:
                context["EXPIRED"] = True
            else:
                context["NEEDS_TO_CONFIRM"] = True
                context["rsvp_form"] = RSVPConfirmationForm(instance=app)
            return context

        flag = status_map.get(status)
        if flag:
            context[flag] = True

        return context


class RSVPSubmitView(mixins.LoginRequiredMixin, generic.View):
    """Handle RSVP form submission - saves logistics info and confirms attendance."""

    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)

        if app.user != request.user:
            raise PermissionDenied("You don't have permission to view this application.")

        if app.status == application.constants.STATUS_CONFIRMED:
            return redirect(reverse_lazy("status"))

        if app.status != application.constants.STATUS_ADMITTED:
            raise PermissionDenied("You can't confirm your application if it hasn't been approved.")

        form = RSVPConfirmationForm(request.POST, instance=app)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = application.constants.STATUS_CONFIRMED
            app.save()
            send_confirmation_email(app)
            return redirect(reverse_lazy("status"))

        return redirect(reverse_lazy("status"))

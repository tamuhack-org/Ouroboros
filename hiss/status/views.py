from datetime import timedelta

import structlog
from django.conf import settings
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

import application.constants
from application.emails import send_confirmation_email
from application.forms import RSVPConfirmationForm
from application.models import Application, Wave
from application.qr import qr_png_base64
from user.models import User
from volunteer.models import ScheduleEvent

logger = structlog.get_logger()


class StatusBaseView(mixins.LoginRequiredMixin, generic.TemplateView):
    """Supply shared application context for pages using status_base.html."""

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
            # Show accepted status even if past confirmation deadline (for now).
            context["NEEDS_TO_CONFIRM"] = True
            return context

        status_map = {
            application.constants.STATUS_PENDING: "PENDING",
            application.constants.STATUS_REJECTED: "REJECTED",
            application.constants.STATUS_CONFIRMED: "CONFIRMED",
            application.constants.STATUS_DECLINED: "DECLINED",
            application.constants.STATUS_CHECKED_IN: "CHECKED_IN",
            application.constants.STATUS_EXPIRED: "EXPIRED",
        }

        flag = status_map.get(status)
        if flag:
            context[flag] = True

        return context


DAY_OF_STATUSES = {
    application.constants.STATUS_CONFIRMED,
    application.constants.STATUS_CHECKED_IN,
    application.constants.STATUS_EXPIRED,
}
DEFAULT_EVENT_LENGTH = timedelta(minutes=30)


def build_schedule(now):
    """Group visible schedule events by local day and mark what's on now / next."""
    days = []
    next_marked = False
    for event in ScheduleEvent.objects.filter(is_visible=True):
        event.is_now = event.start <= now < event.start + DEFAULT_EVENT_LENGTH
        event.is_next = not next_marked and event.start > now
        next_marked = next_marked or event.is_next
        day = timezone.localtime(event.start).date()
        if not days or days[-1]["date"] != day:
            days.append({"date": day, "events": []})
        days[-1]["events"].append(event)
    return days


class StatusView(StatusBaseView):
    template_name = "status/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = context.get("application")
        if app and app.status in DAY_OF_STATUSES:
            context["qr_code_b64"] = qr_png_base64(app)
            context["meal_group"] = app.meal_group
            context["schedule_days"] = build_schedule(timezone.now())
        return context


class RSVPSubmitView(mixins.LoginRequiredMixin, generic.View):
    """Handle RSVP form submission - saves logistics info and confirms attendance."""

    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)

        if app.user != request.user:
            msg = "You don't have permission to view this application."
            raise PermissionDenied(msg)

        if app.status == application.constants.STATUS_CONFIRMED:
            return redirect(reverse_lazy("status"))

        if app.status != application.constants.STATUS_ADMITTED:
            msg = "You can't confirm your application if it hasn't been approved."
            raise PermissionDenied(msg)

        form = RSVPConfirmationForm(request.POST, instance=app)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = application.constants.STATUS_CONFIRMED
            app.save()
            send_confirmation_email(app)
            return redirect(reverse_lazy("status"))

        return redirect(reverse_lazy("status"))

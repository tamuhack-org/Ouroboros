import pytz
from django import forms, http, views
from django.contrib.auth import mixins
from django.core import exceptions
from django.shortcuts import redirect, render_to_response
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from hacker import forms as hacker_forms
from hacker import models as hacker_models


class CreateUpdateView(
    SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView
):
    """
    If the instance requested by the user does not exist, the user is
    redirected to a CreateView, otherwise they're redirected to a view
    containing their instance for updating.
    """

    def get_object(self, queryset=None):
        try:
            return super(CreateUpdateView, self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).post(request, *args, **kwargs)


class ApplicationView(mixins.LoginRequiredMixin, CreateUpdateView):
    template_name = "hacker/application.html"
    form_class = hacker_forms.ApplicationModelForm
    success_url = reverse_lazy("status")
    queryset = hacker_models.Application.objects.all()

    def get_object(self):
        if getattr(self.request.user, "application", None) is None:
            return None
        return self.request.user.application

    def form_valid(self, form: forms.Form):
        application: hacker_models.Application = form.save(commit=False)
        application.hacker = self.request.user
        application.wave = hacker_models.Wave.objects.active_wave()
        application.save()
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if not hacker_models.Wave.objects.active_wave():
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not hacker_models.Wave.objects.active_wave():
            raise exceptions.PermissionDenied(
                "Applications can only be submitted during a registration wave."
            )
        return super().post(request, *args, **kwargs)

    class Meta:
        model = hacker_models.Application


class StatusView(mixins.LoginRequiredMixin, generic.TemplateView):
    """
    The default (core) view for authenticated users. Displays what actions
    a user has left to take, and the status of their application to the event.
    """

    template_name = "hacker/status.html"

    def get_context_data(self, **kwargs):
        hacker = self.request.user
        active_wave = hacker_models.Wave.objects.active_wave()
        if not active_wave:
            next_wave = hacker_models.Wave.objects.next_wave()
            if not next_wave:
                kwargs["NO_MORE_WAVES"] = True
            else:
                kwargs["WAIT_UNTIL_NEXT_WAVE"] = True
                kwargs["next_wave_start"] = next_wave.start
        else:
            if getattr(hacker, "application", None) is None:
                kwargs["active_wave_end"] = active_wave.end
                kwargs["NEEDS_TO_APPLY"] = True
            elif hacker.application.approved is None:
                kwargs["application"] = hacker.application
                kwargs["PENDING"] = True
            else:
                # User application has response
                if hacker.application.approved:
                    # User app approved
                    if getattr(hacker, "rsvp", None) is None:
                        # User hasn't RSVPd
                        if hacker.didnt_rsvp_in_time():
                            # User can't RSVP anymore, they ran out of time
                            kwargs["RSVP_DEADLINE_EXPIRED"] = True
                        else:
                            # User can still RSVP
                            kwargs["rsvp_deadline"] = hacker.rsvp_deadline
                            kwargs["NEEDS_TO_RSVP"] = True
                    else:
                        kwargs["COMPLETE"] = True
                else:
                    kwargs["REJECTED"] = True
        return super().get_context_data(**kwargs)


class RsvpView(mixins.UserPassesTestMixin, CreateUpdateView):
    """
    View for creating an `Rsvp` instance for a `Hacker`. `GET` requests will
    display a form that users will fill out, and `POST` requests will submit the form for validation.

    This view WILL RAISE AN ERROR if a user does not have an approved application.
    """

    template_name = "hacker/rsvp.html"
    queryset = hacker_models.Rsvp.objects.all()
    success_url = reverse_lazy("status")
    permission_denied_message = (
        "You need to be both logged-in and have an approved application to RSVP."
    )
    fields = ["shirt_size", "notes"]

    def test_func(self):
        return (
            not self.request.user.is_anonymous
            and getattr(self.request.user, "application", None) is not None
            and self.request.user.application.approved
        )

    def get_object(self):
        if getattr(self.request.user, "rsvp", None) is None:
            return None
        return self.request.user.rsvp

    def form_valid(self, form: forms.Form):
        rsvp: hacker_models.Rsvp = form.save(commit=False)
        rsvp.hacker = self.request.user
        rsvp.save()
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if request.user.didnt_rsvp_in_time():
            return redirect(reverse_lazy("status"))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.didnt_rsvp_in_time():
            raise exceptions.PermissionDenied("Your RSVP deadline has expired.")
        return super().post(request, *args, **kwargs)

    class Meta:
        model = hacker_models.Rsvp

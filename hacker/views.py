from django import forms, views
from django.contrib.auth import mixins
from django.shortcuts import redirect, render_to_response
from django.urls import reverse_lazy
from django.views import generic

from hacker import models as hacker_models


class ApplicationView(mixins.LoginRequiredMixin, generic.CreateView):
    """
    A view for creating an `Application` for a `Hacker`. `GET` requests will
    display a form that users will fill out, and `POST` requests will submit
    that form for validation.
    """

    template_name = "application.html"
    queryset = hacker_models.Application.objects.all()
    success_url = reverse_lazy("status")
    fields = [
        "major",
        "gender",
        "classification",
        "grad_year",
        "dietary_restrictions",
        "travel_reimbursement_required",
        "num_hackathons_attended",
        "previous_attendant",
        "tamu_student",
        "interests",
        "essay1",
        "essay2",
        "essay3",
        "essay4",
        "notes",
        "resume",
    ]

    def get(self, request, *args, **kwargs):
        if getattr(request.user, "application", None) is not None:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: forms.Form):
        application: hacker_models.Application = form.save(commit=False)
        application.hacker = self.request.user
        application.save()
        return redirect(self.success_url)

    class Meta:
        model = hacker_models.Application


class StatusView(mixins.LoginRequiredMixin, generic.TemplateView):
    """
    The default (core) view for authenticated users. Displays what actions
    a user has left to take, and the status of their application to the event.
    """

    template_name = "status.html"

    def get_context_data(self, **kwargs):
        hacker = self.request.user
        if getattr(hacker, "application", None) is None:
            kwargs["NEEDS_TO_APPLY"] = True
        elif hacker.application.approved is None:
            kwargs["PENDING"] = True
        else:
            # User application has response
            if hacker.application.approved:
                # User app approved
                if getattr(hacker, "rsvp", None) is None:
                    kwargs["NEEDS_TO_RSVP"] = True
                else:
                    kwargs["COMPLETE"] = True
            else:
                kwargs["REJECTED"] = True
        return super().get_context_data(**kwargs)


class RsvpView(mixins.UserPassesTestMixin, generic.CreateView):
    """
    View for creating an `Rsvp` instance for a `Hacker`. `GET` requests will
    display a form that users will fill out, and `POST` requests will submit the form for validation.

    This view WILL RAISE AN ERROR if a user does not have an approved application.
    """

    template_name = "rsvp.html"
    queryset = hacker_models.Rsvp.objects.all()
    permission_denied_message = (
        "You need to be both logged-in and have an approved application to RSVP."
    )

    def test_func(self):
        return (
            not self.request.user.is_anonymous
            and getattr(self.request.user, "application", None) is not None
            and self.request.user.application.approved
        )

    def get_login_url(self):
        if self.request.user.is_anonymous:
            return reverse_lazy("login")
        elif getattr(self.request.user, "application", None) is None:
            return reverse_lazy("application")
        elif not self.request.user.application.approved:
            return reverse_lazy("status")

    fields = ["shirt_size", "notes"]

    def form_valid(self, form: forms.Form):
        rsvp: hacker_models.Rsvp = form.save(commit=False)
        rsvp.hacker = self.request.user
        rsvp.save()
        return redirect(self.success_url)

    class Meta:
        model = hacker_models.Rsvp

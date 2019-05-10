from django import forms, views
from django.contrib.auth import mixins
from django.shortcuts import redirect, render_to_response
from django.urls import reverse_lazy
from django.views import generic

from hacker import forms as hacker_forms
from hacker import models as hacker_models


class ApplicationView(generic.CreateView):
    template_name = "dashboard/application.html"
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

    def form_valid(self, form: forms.Form):
        application: hacker_models.Application = form.save(commit=False)
        application.hacker = self.request.user
        application.save()
        return redirect(reverse_lazy("status"))

    class Meta:
        model = hacker_models.Application


class StatusView(generic.TemplateView, mixins.LoginRequiredMixin):
    template_name = "dashboard/status.html"

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
                if hacker.confirmation is None:
                    kwargs["NEEDS_TO_CONFIRM"] = True
                else:
                    kwargs["COMPLETE"] = True
            else:
                kwargs["REJECTED"] = True
        return super().get_context_data(**kwargs)


class RsvpView(generic.FormView, mixins.LoginRequiredMixin):
    pass

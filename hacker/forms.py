from django import forms
from hacker import models as hacker_models


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = hacker_models.Application
        exclude = [
            "approved",
            "queued_for_approval",
            "date_approved",
            "date_queued_for_approval",
            "date_submitted",
            "hacker",
        ]


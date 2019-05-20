from django import forms
from hacker import models as hacker_models


class ApplicationModelForm(forms.ModelForm):
    def is_valid(self):
        if not hacker_models.Wave.objects.active_wave():
            self.add_error(
                None, "Applications may only be submitted during a registration wave."
            )
        return super().is_valid()

    class Meta:
        model = hacker_models.Application
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


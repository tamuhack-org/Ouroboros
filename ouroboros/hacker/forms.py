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
            "adult",
            "first_name",
            "last_name",
            "major",
            "gender",
            "race",
            "classification",
            "grad_year",
            "num_hackathons_attended",
            "previous_attendant",
            "dietary_restrictions",
            "shirt_size",
            "interests",
            "essay1",
            "essay2",
            "essay3",
            "essay4",
            "notes",
            "resume",
        ]


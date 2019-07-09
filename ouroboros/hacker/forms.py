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
        widgets = {'adult': forms.RadioSelect, "previous_attendant": forms.RadioSelect, 'extra_links': forms.TextInput(attrs={'placeholder': 'ex. GitHub, Devpost, personal website, LinkedIn, etc.'})}
        fields = [
            "first_name",
            "last_name",
            "major",
            "gender",
            "race",
            "classification",
            "grad_year",
            "num_hackathons_attended",
            "previous_attendant",
            "programming_joke",
            "unlimited_resource",
            "cool_prize",
            "adult",
            "resume",
            "extra_links",
            "additional_accommodations",
            "notes",
        ]

class RsvpModelForm(forms.ModelForm):
    class Meta:
        model = hacker_models.Rsvp
        widgets = {'shirt_size': forms.RadioSelect}
        fields = [
            "dietary_restrictions",
            "shirt_size",
        ]
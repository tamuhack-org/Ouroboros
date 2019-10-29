from django import forms
from django.utils.safestring import mark_safe

from application import models as application_models, models


class ApplicationModelForm(forms.ModelForm):
    gender_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )
    race_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

        # HACK: Disable the form if there's not an active wave
        if not application_models.Wave.objects.active_wave():
            for field_name in self.fields.keys():
                self.fields[field_name].widget.attrs["disabled"] = "disabled"

    def clean_gender_other(self):
        gender_other = self.cleaned_data["gender_other"]
        gender = self.cleaned_data["gender"]
        if gender == models.GENDER_OTHER and not gender_other:
            raise forms.ValidationError(
                'Please fill out this field or choose "Prefer not to answer".'
            )
        return gender_other

    def clean_race_other(self):
        race_other = self.cleaned_data["race_other"]
        races = self.cleaned_data["race"]
        if models.RACE_OTHER in races and not race_other:
            raise forms.ValidationError(
                "Please fill out this field with the appropriate information."
            )
        return race_other

    def is_valid(self) -> bool:
        """
        Checks to ensure that a wave is currently active.
        """
        if not application_models.Wave.objects.active_wave():
            self.add_error(
                None,
                "Applications may only be submitted during an active registration wave.",
            )
        return super().is_valid()

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "travel_reimbursement": forms.CheckboxInput,
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "school",
            "major",
            "classification",
            "grad_year",
            "gender",
            "gender_other",
            "race",
            "race_other",
            "num_hackathons_attended",
            "shirt_size",
            "dietary_restrictions",
            "transport_needed",
            "travel_reimbursement",
            "resume",
            "extra_links",
            "question1",
            "question2",
            "question3",
            "additional_accommodations",
            "notes",
            "agree_to_coc",
            "is_adult",
        ]

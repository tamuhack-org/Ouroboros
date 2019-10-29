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

    def clean(self):
        gender = self.cleaned_data.get("gender")
        if gender == models.GENDER_OTHER:
            gender_other = self.cleaned_data.get("gender_other")
            if not gender_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Prefer not to answer".'
                )
                self.add_error("gender_other", msg)
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if models.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        return self.cleaned_data

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

from django import forms
from django.utils.safestring import mark_safe

from application import models as application_models


class ApplicationModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

    def is_valid(self) -> bool:
        """
        Checks to ensure that a wave is currently active.
        """
        if not application_models.Wave.objects.active_wave():
            self.add_error(
                None, "Applications may only be submitted during a registration wave."
            )
        return super().is_valid()

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "previous_attendant": forms.RadioSelect,
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
        }
        fields = [
            "first_name",
            "last_name",
            "major",
            "gender",
            "race",
            "classification",
            "grad_term",
            "num_hackathons_attended",
            "previous_attendant",
            "tamu_student",
            "extra_links",
            "question1",
            "question2",
            "question3",
            "agree_to_coc",
            "is_adult",
            "additional_accommodations",
            "resume",
            "transport_needed",
            "notes",
        ]

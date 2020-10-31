from django import forms
from django.utils.safestring import mark_safe

from application import models as application_models, models
from application.models import School


class ApplicationModelForm(forms.ModelForm):
    race_other = forms.CharField(
        label='If you chose "Other", please elaborate.',
        required=False,
    )
    gender_other = forms.CharField(
        label='If you chose "Other", please elaborate.',
        required=False,
    )
    school = forms.ModelChoiceField(
        School.objects.all(),
        label="What school do you go to?",
    )
    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here.',
        required=False,
    )
    where_did_you_hear_other = forms.CharField(
        label='If you chose "Other", please elaborate.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["liability_waiver"].label = mark_safe(
            'I agree to the terms in the <a target="_blank" href="https://2021.hacklahoma.org/release_of_liability.pdf">Liability Waiver</a>.'
        )

        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a target="_blank" href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>.'
        )

        self.fields["photo_release"].label = mark_safe(
            'I agree to the terms in the <a target="_blank" href="https://2021.hacklahoma.org/photo_release.pdf">Photo Release</a>.'
        )

        # Remove the colons
        self.label_suffix=""

        # Set certain fields to not be required
        self.fields['resume'].required = False
        self.fields['interested_in_hacklahoma'].required = False
        self.fields['mlh_authorize'].required = False
        self.fields['shipping_address'].required = False

        # Set the fields that are required to required
        for field in self.Meta.required:
            self.fields[field].required = True
            self.fields[field].label = mark_safe(f"{self.fields[field].label} <b style=\"color: red;\">*</b> ")

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
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if models.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        hear = self.cleaned_data.get("hear_about")
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "interested_in_hacklahoma": forms.CheckboxInput,
            "mlh_authorize": forms.CheckboxInput,
            "liability_waiver": forms.CheckboxInput,
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "photo_release": forms.CheckboxInput,
            "shipping_address": forms.CheckboxInput,
            "social_links": forms.TextInput(
                attrs={
                    "placeholder": "ex: GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "xxxxxxxxxx"
                }
            ),
            "birthday": forms.TextInput(
                attrs={
                    "placeholder": "mm/dd/yyyy or mm-dd-yyyy"
                }
            ),
            "pronouns": forms.TextInput(
                attrs={
                    "placeholder": "ex: He/Him"
                }
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "school",
            "school_other",
            "birthday",
            "gender",
            "gender_other",
            "pronouns",
            "race",
            "race_other",
            "level_of_study",
            "graduation_year",
            "major",
            "shirt_size",
            "resume",
            "social_links",
            "num_hackathons_attended",
            "question1",
            "question2",
            "question3",
            "where_did_you_hear",
            "where_did_you_hear_other",
            "shipping_address",
            "address1",
            "address2",
            "city",
            "state",
            "zip_code",
            "interested_in_hacklahoma",
            "mlh_authorize",
            "liability_waiver",
            "agree_to_coc",
            "photo_release",
            "is_adult",
            "notes"
        ]

        required = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "school",
            "birthday",
            "gender",
            "pronouns",
            "race",
            "level_of_study",
            "graduation_year",
            "major",
            "shirt_size",
            "num_hackathons_attended",
            "question1",
            "question2",
            "question3",
            "where_did_you_hear",
            "liability_waiver",
            "agree_to_coc",
            "photo_release",
            "is_adult"
        ]
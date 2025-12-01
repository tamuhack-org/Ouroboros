import ast

from django import forms
from django.conf import settings
from django.db.models import Case, IntegerField, When
from django.utils.html import format_html

import application.constants
from application import constants
from application import models as application_models
from application.models import School


class InitialRegistrationForm(forms.ModelForm):
    """Initial registration form for required information"""

    required_css_class = "required-form-input"
    form_help_text = "All fields are required unless marked as (optional)."

    gender_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate (optional).',
        required=False,
    )
    race_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate (optional).',
        required=False,
    )
    major_other = forms.CharField(
        label='If you chose "Other", please specify your major (optional).',
        required=False,
    )

    school = forms.ModelChoiceField(
        queryset=School.objects.annotate(
            priority=Case(
                When(pk=1565, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("priority", "id"),
        label="What school do you go to?",
    )

    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here (optional).',
        required=False,
    )
    tamu_email = forms.CharField(
        label="TAMU Email if you are a Texas A&M student (optional)",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        photo_agreement = f"I grant permission for {settings.ORGANIZER_NAME} to use my name, likeness, voice, and any photographs, video recordings, or audio recordings taken during the event '{settings.EVENT_NAME} {settings.EVENT_YEAR}' for promotional and media purposes, including but not limited to publications, websites, social media, and press releases."

        self.fields["agree_to_photos"].label = photo_agreement

        self.fields["agree_to_coc"].label = format_html(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf" target="_blank" rel="noopener noreferrer">MLH Code of Conduct</a>'
        )

        mlh_stuff = (
            f"I authorize {settings.ORGANIZER_NAME} to share my application/registration information for"
            " event administration, ranking, MLH administration, pre- and post-event informational e-mails,"
            'and occasional messages about hackathons in-line with the <a href="https://mlh.io/privacy" target="_blank" rel="noopener noreferrer">MLH'
            ' Privacy Policy</a>. I further agree to the terms of both the <a href="https://github.com/MLH'
            '/mlh-policies/tree/master/contest-terms.md" target="_blank" rel="noopener noreferrer">MLH Contest Terms and Conditions</a>'
            ' and the <a href="https://mlh.io/privacy" target="_blank" rel="noopener noreferrer">MLH Privacy Policy</a>'
        )

        mlh_newsletter = "I authorize MLH to send me occasional emails about relevant events, career opportunities, and community announcements (optional)."

        self.fields["agree_to_mlh_stuff"].label = format_html(mlh_stuff)
        self.fields["signup_to_mlh_newsletter"].label = mlh_newsletter
        self.fields["is_adult"].label = "Please confirm you are 18 or older."

        # Mark other optional fields
        self.fields["extra_links"].label = self.fields["extra_links"].label + " (optional)"
        self.fields["notes"].label = self.fields["notes"].label + " (optional)"
        self.fields["accessibility_requirements"].label = self.fields["accessibility_requirements"].label + " (optional)"

        if not application_models.Wave.objects.active_wave():
            for field_name in self.fields:
                self.fields[field_name].widget.attrs["disabled"] = "disabled"

    def is_valid(self) -> bool:
        """Check to ensure that a wave is currently active."""
        if not application_models.Wave.objects.active_wave():
            self.add_error(
                None,
                "Applications may only be submitted during an active registration wave.",
            )
        return super().is_valid()

    def clean(self):
        gender = self.cleaned_data.get("gender")
        if gender == application.constants.GENDER_OTHER:
            gender_other = self.cleaned_data.get("gender_other")
            if not gender_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Prefer not to answer".'
                )
                self.add_error("gender_other", msg)
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if application.constants.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        major = self.cleaned_data.get("major")
        if major:
            major_other = self.cleaned_data.get("major_other")
            if major == "Other" and not major_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Other".'
                )
                self.add_error("major_other", msg)
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "agree_to_mlh_stuff": forms.CheckboxInput,
            "signup_to_mlh_newsletter": forms.CheckboxInput,
            "agree_to_photos": forms.CheckboxInput,
            "accessibility_requirements": forms.CheckboxInput,
            "tamu_email": forms.EmailInput(attrs={"placeholder": "netid@tamu.edu"}),
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
            "race": forms.CheckboxSelectMultiple,
        }

        fields = [
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "school",
            "school_other",
            "tamu_email",
            "major",
            "major_other",
            "grad_year",
            "level_of_study",
            "country",
            "gender",
            "gender_other",
            "race",
            "race_other",
            "num_hackathons_attended",
            "wares",
            "resume",
            "extra_links",
            "notes",
            "agree_to_photos",
            "accessibility_requirements",
            "agree_to_coc",
            "agree_to_mlh_stuff",
            "signup_to_mlh_newsletter",
            "is_adult",
        ]


class RSVPConfirmationForm(forms.ModelForm):
    """Form for collecting logistics info after acceptance confirmation."""

    required_css_class = "required-form-input"
    form_help_text = "All fields are required unless marked as (optional)."

    dietary_restrictions = forms.MultipleChoiceField(
        label="Do you have any dietary restrictions (optional)?",
        help_text="Select all that apply",
        choices=constants.DIETARY_RESTRICTIONS,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            kwargs["initial"] = {
                "dietary_restrictions": ast.literal_eval(
                    kwargs.get("instance").dietary_restrictions or "[]"
                ),
            }
        super().__init__(*args, **kwargs)

        # Make fields required even though model has blank=True
        self.fields["shirt_size"].required = True
        self.fields["emergency_contact_name"].required = True
        self.fields["emergency_contact_relationship"].required = True
        self.fields["emergency_contact_phone"].required = True
        self.fields["emergency_contact_email"].required = True

        # Mark optional fields
        self.fields["additional_accommodations"].label = self.fields["additional_accommodations"].label + " (optional)"

        # Add accessibility follow-up text for RSVP form
        accessibilities = "Please check this box you would like our team to follow up with you personally to discuss your accessibility accommodations during this event."
        self.fields["accessibility_requirements"].label = accessibilities + " (optional)"

    class Meta:
        model = application_models.Application
        fields = [
            "shirt_size",
            "dietary_restrictions",
            "additional_accommodations",
            "accessibility_requirements",
            "emergency_contact_name",
            "emergency_contact_relationship",
            "emergency_contact_phone",
            "emergency_contact_email",
        ]
        widgets = {
            "accessibility_requirements": forms.CheckboxInput,
        }


# Keep the legacy form for backwards compatibility if needed
class ApplicationModelForm(forms.ModelForm):
    required_css_class = "required-form-input"
    form_help_text = "All fields are required unless marked as (optional)."

    gender_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate (optional).',
        required=False,
    )
    race_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate (optional).',
        required=False,
    )
    major_other = forms.CharField(
        label='If you chose "Other", please specify your major (optional).',
        required=False,
    )

    # 1565 is the ID for Texas A&M University
    school = forms.ModelChoiceField(
        queryset=School.objects.annotate(
            priority=Case(
                When(pk=1565, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("priority", "id"),
        label="What school do you go to?",
    )

    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here (optional).',
        required=False,
    )
    tamu_email = forms.CharField(
        label="TAMU Email if you are a Texas A&M student (optional)",
        required=False,
    )

    dietary_restrictions = forms.MultipleChoiceField(
        label="Do you have any dietary restrictions (optional)?",
        help_text="Select all that apply",
        choices=constants.DIETARY_RESTRICTIONS,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            kwargs["initial"] = {
                "dietary_restrictions": ast.literal_eval(
                    kwargs.get("instance").dietary_restrictions or "[]"
                ),
            }

        super().__init__(*args, **kwargs)

        photo_agreement = f"I grant permission for {settings.ORGANIZER_NAME} to use my name, likeness, voice, and any photographs, video recordings, or audio recordings taken during the event '{settings.EVENT_NAME} {settings.EVENT_YEAR}' for promotional and media purposes, including but not limited to publications, websites, social media, and press releases."
        accessibilities = "Please check this box you would like our team to follow up with you personally to discuss your accessibility accommodations during this event."

        self.fields["agree_to_photos"].label = photo_agreement
        self.fields["accessibility_requirements"].label = accessibilities

        self.fields["agree_to_coc"].label = format_html(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf" target="_blank" rel="noopener noreferrer">MLH Code of Conduct</a>'
        )

        mlh_stuff = (
            f"I authorize {settings.ORGANIZER_NAME} to share my application/registration information for"
            " event administration, ranking, MLH administration, pre- and post-event informational e-mails,"
            'and occasional messages about hackathons in-line with the <a href="https://mlh.io/privacy" target="_blank" rel="noopener noreferrer">MLH'
            ' Privacy Policy</a>. I further agree to the terms of both the <a href="https://github.com/MLH'
            '/mlh-policies/tree/master/contest-terms.md" target="_blank" rel="noopener noreferrer">MLH Contest Terms and Conditions</a>'
            ' and the <a href="https://mlh.io/privacy" target="_blank" rel="noopener noreferrer">MLH Privacy Policy</a>'
        )

        mlh_newsletter = "I authorize MLH to send me occasional emails about relevant events, career opportunities, and community announcements (optional)."

        self.fields["agree_to_mlh_stuff"].label = format_html(mlh_stuff)
        self.fields["signup_to_mlh_newsletter"].label = mlh_newsletter
        self.fields["is_adult"].label = "Please confirm you are 18 or older."

        # Mark other optional fields
        self.fields["extra_links"].label = self.fields["extra_links"].label + " (optional)"
        self.fields["notes"].label = self.fields["notes"].label + " (optional)"
        self.fields["accessibility_requirements"].label = accessibilities + " (optional)"
        self.fields["additional_accommodations"].label = self.fields["additional_accommodations"].label + " (optional)"

        # HACK: Disable the form if there's not an active wave
        if not application_models.Wave.objects.active_wave():
            for field_name in self.fields:
                self.fields[field_name].widget.attrs["disabled"] = "disabled"

    def is_valid(self) -> bool:
        """Check to ensure that a wave is currently active."""
        if not application_models.Wave.objects.active_wave():
            self.add_error(
                None,
                "Applications may only be submitted during an active registration wave.",
            )
        return super().is_valid()

    def clean(self):
        gender = self.cleaned_data.get("gender")
        if gender == application.constants.GENDER_OTHER:
            gender_other = self.cleaned_data.get("gender_other")
            if not gender_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Prefer not to answer".'
                )
                self.add_error("gender_other", msg)
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if application.constants.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        major = self.cleaned_data.get("major")
        if major:
            major_other = self.cleaned_data.get("major_other")
            if major == "Other" and not major_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Other".'
                )
                self.add_error("major_other", msg)
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "agree_to_mlh_stuff": forms.CheckboxInput,
            "signup_to_mlh_newsletter": forms.CheckboxInput,
            "agree_to_photos": forms.CheckboxInput,
            "accessibility_requirements": forms.CheckboxInput,
            "travel_reimbursement": forms.CheckboxInput,
            "tamu_email": forms.EmailInput(attrs={"placeholder": "netid@tamu.edu"}),
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "country",
            "school",
            "school_other",
            "tamu_email",
            "major",
            "major_other",
            "grad_year",
            "level_of_study",
            "gender",
            "gender_other",
            "race",
            "race_other",
            "num_hackathons_attended",
            "wares",
            "dietary_restrictions",
            "shirt_size",
            "resume",
            "extra_links",
            "additional_accommodations",
            "accessibility_requirements",
            "emergency_contact_name",
            "emergency_contact_relationship",
            "emergency_contact_phone",
            "emergency_contact_email",
            "notes",
            "agree_to_photos",
            "agree_to_coc",
            "agree_to_mlh_stuff",
            "signup_to_mlh_newsletter",
            "is_adult",
        ]

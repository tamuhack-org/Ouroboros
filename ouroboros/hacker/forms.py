from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from hacker import models as hacker_models


class ApplicationModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mlh_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

    def is_valid(self):
        if not hacker_models.Wave.objects.active_wave():
            self.add_error(
                None, "Applications may only be submitted during a registration wave."
            )
        return super().is_valid()

    class Meta:
        model = hacker_models.Application
        widgets = {
            "adult": forms.CheckboxInput,
            "mlh_coc": forms.CheckboxInput,
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
            "grad_year",
            "num_hackathons_attended",
            "previous_attendant",
            "programming_joke",
            "unlimited_resource",
            "cool_prize",
            "resume",
            "extra_links",
            "additional_accommodations",
            "notes",
            "adult",
            "mlh_coc",
        ]


class RsvpModelForm(forms.ModelForm):
    class Meta:
        model = hacker_models.Rsvp
        widgets = {"shirt_size": forms.RadioSelect}
        fields = ["dietary_restrictions", "shirt_size"]


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=hacker_models.Hacker.objects.all(),
        required=False,
        # Use the pretty 'filter_horizontal widget'.
        widget=FilteredSelectMultiple("users", False),
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields["users"].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data["users"])

    def save(self, *args, **kwargs):
        # Default save
        instance = super().save()
        # Save many-to-many data
        self.save_m2m()
        return instance

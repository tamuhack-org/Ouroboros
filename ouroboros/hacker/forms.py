from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from hacker import models as hacker_models


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
         widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super().save()
        # Save many-to-many data
        self.save_m2m()
        return instance

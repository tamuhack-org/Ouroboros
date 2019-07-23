from django import forms
from django.forms import widgets
from volunteer.models import VolunteerApplication, Shift
from multiselectfield import MultiSelectFormField
from django.conf import settings
from django.db.models import Count
from django.forms import ValidationError


def validate_shift(shift: Shift):
    if len(shift.volunteers.all()) >= settings.MAX_VOLUNTEERS_PER_SHIFT:
        raise ValidationError("Please select a shift with spots remaining.")


class VolunteerApplicationModelForm(forms.ModelForm):
    shifts = forms.ModelMultipleChoiceField(
        queryset=Shift.objects.annotate(volunteers_len=Count("volunteers"))
        .filter(volunteers_len__lte=settings.MAX_VOLUNTEERS_PER_SHIFT)
        .all(),
        widget=widgets.CheckboxSelectMultiple,
    )

    class Meta:
        model = VolunteerApplication
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "grad_year",
            "shirt_size",
            "engr_honors",
        ]

    def clean(self):
        return super().clean()

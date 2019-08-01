from django import forms
from django.forms import widgets
from volunteer.models import VolunteerApplication, Shift
from multiselectfield import MultiSelectFormField
from django.conf import settings
from django.db.models import Count
from django.forms import ValidationError


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
        ]

    def clean(self):
        cleaned_data = super().clean()
        shifts = cleaned_data.get("shifts")
        if shifts:
            if (
                shifts.annotate(volunteers_len=Count("volunteers"))
                .filter(volunteers_len__gte=settings.MAX_VOLUNTEERS_PER_SHIFT)
                .exists()
            ):
                self.add_error(
                    "shifts", "Please select shifts that still have spots remaining."
                )

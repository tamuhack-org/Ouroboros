from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

SHIRT_SIZES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

GRAD_YEARS = []
for i in range(timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION):
    for j in ["Spring", "Fall"]:
        GRAD_YEARS.append(("%s %i" % (j, i), "%s %i" % (j, i)))
GRAD_YEARS = GRAD_YEARS[1:-1]
GRAD_YEARS.insert(0, (None, "-- Select Option --"))
GRAD_YEARS.append(("Other", "Other"))


class Shift(models.Model):
    """ tbd """
    start = models.DateTimeField()
    end = models.DateTimeField()
    capacity = models.IntegerField()


class VolunteerApplication(models.Model):
    """ Represents a Volunteer's application to this Hackathon """

    shifts = models.ManyToManyField(Shift, null=True)

    datetime_submitted = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    phone_number = PhoneNumberField()
    
    grad_year = models.CharField(
        "What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11
    )
    shirt_size = models.CharField(choices=SHIRT_SIZES, max_length=3)
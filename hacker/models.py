import json
import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from ouroboros.settings import customization as custom_settings

SHIRT_SIZES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

GENDERS = (
    ("M", "Male"),
    ("F", "Female"),
    ("NB", "Non-binary"),
    ("NA", "Prefer not to disclose"),
)

CLASSIFICATIONS = [("U1", "U1"), ("U2", "U2"), ("U3", "U3"), ("U4", "U4"), ("U5", "U5")]

DIETARY_RESTRICTIONS = (
    ("Vegan", "Vegan"),
    ("Vegetarian", "Vegetarian"),
    ("Halal", "Halal"),
    ("Kosher", "Kosher"),
    ("Food Allergies", "Food Allergies"),
)

WAVE_TYPES = (("Approve", "Approve Application"), ("Reject", "Reject Application"))

GRAD_YEARS = [
    (i, i)
    for i in range(
        timezone.now().year,
        timezone.now().year + custom_settings.EMAIL_CONFIRM_CODE_LENGTH,
    )
]


class Hacker(AbstractUser):
    is_active = models.BooleanField(
        ("active"),
        default=False,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    first_name = models.CharField(
        max_length=255, blank=False, verbose_name="first name"
    )
    last_name = models.CharField(max_length=255, blank=False, verbose_name="last name")
    email = models.EmailField(blank=False, null=False)

    checked_in = models.NullBooleanField(blank=True)
    checked_in_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)


class Application(models.Model):
    major = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDERS, max_length=2)
    classification = models.CharField(choices=CLASSIFICATIONS, max_length=2)
    grad_year = models.IntegerField(choices=GRAD_YEARS, verbose_name="graduation year")
    dietary_restrictions = MultiSelectField(
        choices=DIETARY_RESTRICTIONS, verbose_name="dietary restrictions", blank=True
    )
    travel_reimbursement_required = models.BooleanField(default=False)

    num_hackathons_attended = models.PositiveSmallIntegerField(default=0)
    previous_attendant = models.BooleanField(default=False)
    tamu_student = models.BooleanField(default=True)

    interests = models.TextField(max_length=200)
    essay1 = models.TextField(max_length=200)
    essay2 = models.TextField(max_length=200, null=True, blank=True)
    essay3 = models.TextField(max_length=200, null=True, blank=True)
    essay4 = models.TextField(max_length=200, null=True, blank=True)
    notes = models.TextField(
        max_length=300,
        blank=True,
        help_text="Provide any additional notes and/or comments in the text box provide",
    )
    resume = models.FileField(upload_to="hacker_resumes", null=True, blank=True)

    approved = models.NullBooleanField(blank=True)
    queued_for_approval = models.NullBooleanField(blank=True)

    date_approved = models.DateField(null=True, blank=True)
    date_queued_for_approval = models.DateField(null=True, blank=True)
    date_submitted = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Application" % (self.hacker.last_name, self.hacker.first_name)


class Confirmation(models.Model):
    shirt_size = models.CharField(
        max_length=3, choices=SHIRT_SIZES, verbose_name="shirt size"
    )
    notes = models.TextField(
        max_length=300,
        blank=True,
        help_text="Provide any additional notes and/or comments in the text box provide",
    )

    date_confirmed = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "%s, %s - Confirmation" % (self.hacker.last_name, self.hacker.first_name)


class Team(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

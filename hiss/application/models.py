# pylint: disable=C0330
import uuid
from typing import Optional, List, Union, Tuple

from django.conf import settings
from django.core import exceptions
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from multiselectfield import MultiSelectField
from django_s3_storage.storage import S3Storage

s3_storage = S3Storage()


class WaveManager(models.Manager):
    def next_wave(
        self, start_dt: Optional[timezone.datetime] = None
    ) -> Optional["Wave"]:
        """
        Returns the next INACTIVE wave, if one exists. For the CURRENT active wave, use
        `active_wave`.
        """
        if not start_dt:
            start_dt = timezone.now()
        qs = self.get_queryset().filter(start__gt=start_dt).order_by("start")
        return qs.first()

    def active_wave(
        self, start_dt: Optional[timezone.datetime] = None
    ) -> Optional["Wave"]:
        """
        Returns the CURRENTLY active wave, if one exists. For the next INACTIVE wave, use
        `next_wave`.
        """
        if not start_dt:
            start_dt = timezone.now()
        qs = (
            self.get_queryset()
            .filter(start__lte=start_dt, end__gt=start_dt)
            .order_by("start")
        )
        return qs.first()


class Wave(models.Model):
    """
    Representation of a registration period. `Application`s must be created during
    a `Wave`, and are automatically associated with a wave through the `Application`'s `pre_save` handler.
    """

    start = models.DateTimeField()
    end = models.DateTimeField()
    num_days_to_rsvp = models.IntegerField()
    is_walk_in_wave = models.BooleanField(
        default=False, verbose_name="Is this wave for walk-ins?"
    )

    objects = WaveManager()

    def clean(self):
        super().clean()
        if self.start >= self.end:
            raise exceptions.ValidationError(
                {"start": "Start date can't be after end date."}
            )
        for wave in Wave.objects.exclude(pk=self.pk).all():
            has_start_overlap = wave.start < self.start < wave.end
            has_end_overlap = wave.start < self.end < wave.end
            if has_start_overlap or has_end_overlap:
                raise exceptions.ValidationError(
                    "Cannot create wave; another wave with an overlapping time range exists."
                )


class School(models.Model):
    """
    A simple model for representing colleges/universities.
    """

    name = models.CharField("name", max_length=255)

    def __str__(self):
        return self.name


AGREE = ((True, "Agree"),)

TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))

NO_ANSWER = "NA"

MALE = "M"
FEMALE = "F"
NON_BINARY = "NB"
GENDER_OTHER = "X"

GENDERS: List[Tuple[str, str]] = [
    ("", "---------"),
    (NO_ANSWER, "Prefer not to answer"),
    (MALE, "Male"),
    (FEMALE, "Female"),
    (NON_BINARY, "Non-binary"),
    (GENDER_OTHER, "Prefer to self-describe"),
]

AMERICAN_INDIAN = "AI"
ASIAN = "AS"
BLACK = "BL"
HISPANIC = "HI"
NATIVE_HAWAIIAN = "NH"
WHITE = "WH"
RACE_OTHER = "O"

RACES: List[Tuple[str, str]] = [
    (AMERICAN_INDIAN, "American Indian or Alaskan Native"),
    (ASIAN, "Asian"),
    (BLACK, "Black or African-American"),
    (HISPANIC, "Hispanic or Latino"),
    (NATIVE_HAWAIIAN, "Native Hawaiian or other Pacific Islander"),
    (WHITE, "White"),
    (NO_ANSWER, "Prefer not to answer"),
    (RACE_OTHER, "Prefer to self-describe"),
]

FRESHMAN = "Fr"
SOPHOMORE = "So"
JUNIOR = "Jr"
SENIOR = "Sr"
MASTERS = "Ma"
PHD = "PhD"
CLASSIFICATION_OTHER = "O"

CLASSIFICATIONS: List[Tuple[str, str]] = [
    (FRESHMAN, "Freshman"),
    (SOPHOMORE, "Sophomore"),
    (JUNIOR, "Junior"),
    (SENIOR, "Senior"),
    (MASTERS, "Master's Student"),
    (PHD, "PhD Student"),
    (CLASSIFICATION_OTHER, "Other"),
]

NONE = "None"

HACKATHONS_0 = "0"
HACKATHONS_1_TO_3 = "1-3"
HACKATHONS_4_TO_7 = "4-7"
HACKATHONS_8_TO_10 = "8-10"
HACKATHONS_OVER_TEN = "10+"

HACKATHON_TIMES: List[Tuple[str, str]] = [
    (HACKATHONS_0, "This will be my first!"),
    (HACKATHONS_1_TO_3, "1-3"),
    (HACKATHONS_4_TO_7, "4-7"),
    (HACKATHONS_8_TO_10, "8-10"),
    (HACKATHONS_OVER_TEN, "10+"),
]

GRAD_YEARS: List[Tuple[int, int]] = [
    (int(y), int(y))
    for y in range(
        timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION
    )
]

REFERRAL_LOCATIONS: List[Tuple[str, str]] = [
    ("email", "University Email"),
    ("social", "Facebook / Instagram"),
    ("friend", "Friend"),
    ("MLH", "MLH Website / Newsletter"),
    ("MSC", "MSC Open House"),
    ("campus", "Campus Marketing (ex. Flyers, Posters, Whiteboards, etc)"),
    ("website", "TAMU Datathon Website"),
    ("other", "Other"),
]

PRIZE_SUGGESTION_QTEXT = "What prize(s) do you want to see at TD?"
WORKSHOPS_SUGGESTION_QTEXT = "What workshop(s) do you want to see at TD?"
DS_ML_CLASSES_QTEXT = (
    "What data science or machine learning related classes have you taken, if any?"
)
DS_ML_CLUBS_QTEXT = "What data science or machine learning related clubs on campus are you involved in, if any?"
DS_ML_JOBS_QTEXT = "What data science or machine learning related jobs/internships have you had, if any?"
# Question 6 is moved to forms.py

WOMENS_XXS = "WXXS"
WOMENS_XS = "WXS"
WOMENS_S = "WS"
WOMENS_M = "WM"
WOMENS_L = "WL"
WOMENS_XL = "WXL"
WOMENS_XXL = "WXXL"
UNISEX_XXS = "XXS"
UNISEX_XS = "XS"
UNISEX_S = "S"
UNISEX_M = "M"
UNISEX_L = "L"
UNISEX_XL = "XL"
UNISEX_XXL = "XXL"

SHIRT_SIZES = [
    (UNISEX_XXS, "Unisex XXS"),
    (UNISEX_XS, "Unisex XS"),
    (UNISEX_S, "Unisex S"),
    (UNISEX_M, "Unisex M"),
    (UNISEX_L, "Unisex L"),
    (UNISEX_XL, "Unisex XL"),
    (UNISEX_XXL, "Unisex XXL"),
]

STATUS_PENDING = "P"
"""Status given to a submitted (but unreviewed) application.."""

STATUS_REJECTED = "R"
"""Status given to a rejected application."""

STATUS_ADMITTED = "A"
"""Status given to an approved application."""

STATUS_CONFIRMED = "C"
"""Status given to an admitted application where the user has confirmed their attendance."""

STATUS_DECLINED = "X"
"""Status given to an admitted application where the user has declined their admission."""

STATUS_CHECKED_IN = "I"
"""Status given to an application where the user has checked in to the event."""

STATUS_EXPIRED = "E"
"""The user missed the application's confirmation_deadline."""

STATUS_OPTIONS = [
    (STATUS_PENDING, "Under Review"),
    (STATUS_REJECTED, "Waitlisted"),
    (STATUS_ADMITTED, "Admitted"),
    (STATUS_CONFIRMED, "Confirmed"),
    (STATUS_DECLINED, "Declined"),
    (STATUS_CHECKED_IN, "Checked in"),
    (STATUS_EXPIRED, "Expired"),
]


def uuid_generator(_instance, filename: str):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename


class Application(models.Model):
    """
    Represents a `Hacker`'s application to this hackathon.
    """

    # META INFO
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_submitted = models.DateTimeField(auto_now_add=True)
    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=False)
    status = models.CharField(
        choices=STATUS_OPTIONS, max_length=1, default=STATUS_PENDING
    )

    # ABOUT YOU
    first_name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="last name"
    )
    extra_links = models.TextField(
        "Is there anything else you'd like us to look at while considering your application?",
        max_length=500,
        blank=True,
    )
    prize_suggestions = models.TextField(
        PRIZE_SUGGESTION_QTEXT, max_length=500, blank=True
    )
    workshop_suggestions = models.TextField(
        WORKSHOPS_SUGGESTION_QTEXT, max_length=500, blank=True
    )
    ds_ml_classes = models.TextField(DS_ML_CLASSES_QTEXT, max_length=500, blank=True)
    ds_ml_clubs = models.TextField(DS_ML_CLUBS_QTEXT, max_length=500, blank=True)
    ds_ml_jobs = models.TextField(DS_ML_JOBS_QTEXT, max_length=500, blank=True)
    interesting_industries = models.TextField(max_length=500, blank=True)
    industries_other = models.CharField(
        "other-industries", max_length=255, null=True, blank=True
    )

    resume = models.FileField(
        "Upload your resume (PDF only)",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        upload_to=uuid_generator,
        storage=s3_storage,
        null=True,
        blank=True,
    )
    github_link = models.URLField("Your GitHub", max_length=255, blank=True, null=True)
    linkedin_link = models.URLField(
        "Your Linkedin", max_length=255, blank=True, null=True
    )
    personal_website_link = models.URLField(
        "Your Personal Website", max_length=255, blank=True, null=True
    )
    instagram_link = models.URLField(
        "Your Instagram", max_length=255, blank=True, null=True
    )
    devpost_link = models.URLField(
        "Your Devpost", max_length=255, blank=True, null=True
    )

    # DEMOGRAPHIC INFORMATION
    school = models.ForeignKey(
        School,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="What school do you go to?",
    )
    school_other = models.CharField(null=True, blank=True, max_length=255)
    majors = models.TextField(max_length=500, default=None)
    minors = models.TextField(max_length=500, default=None)
    classification = models.CharField(
        "What classification are you?", choices=CLASSIFICATIONS, max_length=3
    )
    gender = models.CharField(
        "What's your gender?", choices=GENDERS, max_length=2, default=NO_ANSWER
    )
    gender_other = models.CharField(
        "Self-describe", max_length=255, null=True, blank=True
    )
    age = models.IntegerField(
        "What's your age?",
        validators=[MinValueValidator(10), MaxValueValidator(100)],
        default=None,
    )
    race = MultiSelectField(
        "What race(s) do you identify with?", choices=RACES, max_length=41
    )
    race_other = models.CharField(
        "Self-describe", max_length=255, null=True, blank=True
    )
    referral = models.CharField(
        "How did you hear about TAMU Datathon?",
        choices=REFERRAL_LOCATIONS,
        max_length=10,
    )
    volunteer = models.BooleanField(
        "Would you be interested in mentoring for part of the event?",
        choices=TRUE_FALSE_CHOICES,
        default=False,
    )
    first_generation = models.BooleanField(
        "I am a first generation college student.", default=False,
    )
    datascience_experience = models.CharField(max_length=2, default=None)
    technology_experience = models.CharField(max_length=150, default=None)

    grad_year = models.IntegerField(
        "What is your anticipated graduation year?", choices=GRAD_YEARS
    )
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES
    )

    # LEGAL INFO
    agree_to_mlh_policies = models.BooleanField(
        choices=AGREE,
        default=None,
        help_text="Being an MLH event, we need participants to be familiar with the MLH Code of Conduct and the MLH Contest Terms and Conditions.",
    )
    agree_to_privacy = models.BooleanField(
        choices=AGREE,
        default=None,
        help_text="We need your authorization to share your application / registration information for event administration, ranking, MLH administration, pre and post-event informational e-mails, and occasional messages about hackathons, in-line with the MLH Privacy Policy.",
    )
    is_adult = models.BooleanField(
        "Please confirm you are 18 or older.",
        choices=AGREE,
        default=None,
        help_text="Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas "
        "A&M.",
    )

    # LOGISTICAL INFO
    physical_location = models.CharField(
        "Where will you be participating from?", max_length=20
    )
    physical_location_other = models.CharField(
        "other-physical-location", max_length=20, null=True, blank=True
    )

    # CONFIRMATION DEADLINE
    confirmation_deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s, %s - Application" % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application:update", args=[self.id])

    def clean(self):
        super().clean()
        if not self.is_adult:
            raise exceptions.ValidationError(
                "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email "
                "us at connect@tamudatathon.com. "
            )
        if not self.first_name.isalpha():
            raise exceptions.ValidationError("First name can only contain letters.")
        if not self.last_name.isalpha():
            raise exceptions.ValidationError("Last name can only contain letters.")

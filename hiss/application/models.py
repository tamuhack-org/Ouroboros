# pylint: disable=C0330
import uuid
from typing import List, Optional, Tuple

from django.conf import settings
from django.core import exceptions
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django_s3_storage.storage import S3Storage
from multiselectfield import MultiSelectField

from application.filesize_validation import FileSizeValidator
from address.models import AddressField

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


class DietaryRestriction(models.Model):
    name = models.CharField(max_length=255)


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

DRIVING = "D"
EVENT_PROVIDED_BUS = "B"
EVENT_PROVIDED_BUS_UT = "BUT"
EVENT_PROVIDED_BUS_UTD = "BUTD"
EVENT_PROVIDED_BUS_UTA = "BUTA"
EVENT_PROVIDED_BUS_UTSA = "BUTSA"
EVENT_PROVIDED_BUS_UTRGV = "BUTRGV"
OTHER_BUS = "OB"
FLYING = "F"
PUBLIC_TRANSPORTATION = "P"
MANUAL_POWER = "M"

TRANSPORT_MODES: List[Tuple[str, str]] = [
    (DRIVING, "Driving"),
    (EVENT_PROVIDED_BUS, f"{settings.EVENT_NAME} Bus"),
    (EVENT_PROVIDED_BUS_UT, f"{settings.EVENT_NAME} Bus - UT Austin"),
    (EVENT_PROVIDED_BUS_UTD, f"{settings.EVENT_NAME} Bus - UT Dallas"),
    (EVENT_PROVIDED_BUS_UTA, f"{settings.EVENT_NAME} Bus - UT Arlington"),
    (EVENT_PROVIDED_BUS_UTSA, f"{settings.EVENT_NAME} Bus - UTSA"),
    (EVENT_PROVIDED_BUS_UTRGV, f"{settings.EVENT_NAME} Bus - UTRGV"),
    (OTHER_BUS, "Other Bus (Greyhound, Megabus, etc.)"),
    (FLYING, "Flying"),
    (PUBLIC_TRANSPORTATION, "Public Transportation"),
    (MANUAL_POWER, "Walking/Biking"),
]

QUESTION1_TEXT = "Tell us your best programming joke."
QUESTION2_TEXT = "What is the one thing you'd build if you had unlimited resources?"
QUESTION3_TEXT = "What's your hidden talent?"

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
    (WOMENS_XXS, "Women's XXS"),
    (WOMENS_XS, "Women's XS"),
    (WOMENS_S, "Women's S"),
    (WOMENS_M, "Women's M"),
    (WOMENS_L, "Women's L"),
    (WOMENS_XL, "Women's XL"),
    (WOMENS_XXL, "Women's XXL"),
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

HAS_TEAM = "HT"
HAS_NO_TEAM = "HNT"

HAS_TEAM_OPTIONS = [
    (HAS_TEAM, "I do have a team"),
    (HAS_NO_TEAM, "I do not have a team"),
]

WANTS_TEAM_OPTIONS = [
    ("Friend", "From a friend"),
    ("Yard sign", "Yard sign"),
    ("Social media", "Social media"),
    ("Student orgs", "Though another student org"),
    ("TAMUhack organizer", "From a TAMUhack organizer"),
    ("Engineering newsletter", "From the TAMU Engineering Newsletter"),
    ("MLH", "Major League Hacking (MLH)"),
    ("Attended before", f"I've attended {settings.EVENT_NAME} before")
]

PURPOSE_WIN = "W"
"""The user wants to win this freaking hackathon"""

PURPOSE_LEARN = "L"
"""The user wants to use this hackathon to learn something"""

PURPOSE_WORKSHOP = "WR"
"""The user wants to use this hackathon for all it's great workshops"""

PURPOSE_RECRUITING = "R"
"""The user wants to use this hackathon to get a job or internship"""

PURPOSE_MESS_AROUND = "M"
"""The user wants to use this hackathon as an excuse to mess around and get some swag"""

PURPOSE_OPTIONS = [
    (PURPOSE_WIN, "I want to win!"),
    (PURPOSE_LEARN, "I want to learn something new!"),
    (PURPOSE_WORKSHOP, "I just want to attend all the workshops"),
    (
        PURPOSE_RECRUITING,
        "I just want to talk to the sponsors and get a job",
    ),
    (PURPOSE_MESS_AROUND, "I want to just mess around on the Minecraft server!"),
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
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    extra_links = models.CharField(
        "Point us to anything you'd like us to look at while considering your application",
        max_length=200,
        blank=True,
    )
    question1 = models.TextField(QUESTION1_TEXT, max_length=500)
    question2 = models.TextField(QUESTION2_TEXT, max_length=500)
    question3 = models.TextField(QUESTION3_TEXT, max_length=500)
    resume = models.FileField(
        "Upload your resume (PDF only)",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            FileSizeValidator(max_filesize=2.5),
        ],
        upload_to=uuid_generator,
        storage=s3_storage,
    )

    # DEMOGRAPHIC INFORMATION
    school = models.ForeignKey(
        School,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="What school do you go to?",
    )
    school_other = models.CharField(null=True, blank=True, max_length=255)
    major = models.CharField("What's your major?", max_length=255)
    classification = models.CharField(
        "What classification are you?", choices=CLASSIFICATIONS, max_length=3
    )
    gender = models.CharField(
        "What's your gender?", choices=GENDERS, max_length=2, default=NO_ANSWER
    )
    gender_other = models.CharField(
        "Self-describe", max_length=255, null=True, blank=True
    )
    race = MultiSelectField(
        "What race(s) do you identify with?", choices=RACES, max_length=41
    )
    race_other = models.CharField(
        "Self-describe", max_length=255, null=True, blank=True
    )
    grad_year = models.IntegerField(
        "What is your anticipated graduation year?", choices=GRAD_YEARS
    )
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES
    )

    # LEGAL INFO
    agree_to_coc = models.BooleanField(choices=AGREE, default=None)
    agree_to_mlh_stuff = models.BooleanField(
        choices=AGREE, null=True, default=None, blank=True
    )
    is_adult = models.BooleanField(
        "Please confirm you are 18 or older.",
        choices=AGREE,
        default=None,
        help_text="Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas "
        "A&M.",
    )

    # LOGISTICAL INFO
    shirt_size = models.CharField(
        "What size shirt do you wear?", choices=SHIRT_SIZES, max_length=4
    )
    address = AddressField(on_delete=models.CASCADE, default=None, null=True)
    additional_accommodations = models.TextField(
        "Do you require any special accommodations at the event? Please list all dietary restrictions here.",
        max_length=500,
        blank=True,
    )

    technology_experience = models.CharField(max_length=450, default=None)

    # TEAM MATCHING INFO
    has_team = models.CharField(
        "Do you have a team yet?",
        choices=HAS_TEAM_OPTIONS,
        max_length=16,
    )
    wants_team = models.CharField(
        f"How did you hear about {settings.EVENT_NAME}?",
        choices=WANTS_TEAM_OPTIONS,
        help_text="",
        max_length=255,
    )

    # CONFIRMATION DEADLINE
    confirmation_deadline = models.DateTimeField(null=True, blank=True)

    # MISCELLANEOUS
    notes = models.TextField(
        "Anything else you would like us to know?", max_length=300, blank=True
    )

    def __str__(self):
        return "%s, %s - Application" % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application:update", args=[self.id])

    def clean(self):
        super().clean()
        if not self.is_adult:
            raise exceptions.ValidationError(
                "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email "
                f"us at {settings.ORGANIZER_EMAIL}. "
            )
        if not self.first_name.isalpha():
            raise exceptions.ValidationError("First name can only contain letters.")
        if not self.last_name.isalpha():
            raise exceptions.ValidationError("Last name can only contain letters.")

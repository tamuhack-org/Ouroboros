from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import (
    override,
)

from django.conf import settings
from django.core import exceptions
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils import timezone
from django_s3_storage.storage import S3Storage
from multiselectfield import MultiSelectField

from application.constants import (
    AGREE,
    AGREE_DISAGREE,
    CLASSIFICATIONS,
    COUNTRIES_TUPLES,
    DISCOVERY_METHOD_OPTIONS,
    GENDERS,
    GRAD_YEARS,
    HACKATHON_TIMES,
    HAS_TEAM_OPTIONS,
    LEVELS_OF_STUDY,
    MAJORS,
    MAX_AGE,
    NO_ANSWER,
    QUESTION1_TEXT,
    RACES,
    SHIRT_SIZES,
    STATUS_CONFIRMED,
    STATUS_OPTIONS,
    STATUS_PENDING,
    WARECHOICE,
)
from application.filesize_validation import FileSizeValidator

s3_storage = S3Storage()
logger = logging.getLogger(__name__)


class WaveManager(models.Manager["Wave"]):
    def next_wave(self, start_dt: datetime | None = None) -> Wave | None:
        """Return the next INACTIVE wave, if one exists."""
        if start_dt is None:
            start_dt = timezone.now()
        qs: QuerySet[Wave] = (
            self.get_queryset().filter(start__gt=start_dt).order_by("start")
        )
        return qs.first()

    def active_wave(self, start_dt: datetime | None = None) -> Wave | None:
        """Return the currently active wave, if one exists."""
        if start_dt is None:
            start_dt = timezone.now()
        qs: QuerySet[Wave] = (
            self.get_queryset()
            .filter(start__lte=start_dt, end__gt=start_dt)
            .order_by("start")
        )
        return qs.first()


class Wave(models.Model):
    """Representation of a registration period."""

    objects = WaveManager()

    class Meta:
        ordering = ["start"]

    @override
    def __str__(self) -> str:
        return f"Wave from {self.start} to {self.end}"

    start: models.DateTimeField[datetime, datetime] = models.DateTimeField()
    end: models.DateTimeField[datetime, datetime] = models.DateTimeField()
    num_days_to_rsvp: models.IntegerField[int, int] = models.IntegerField()
    is_walk_in_wave: models.BooleanField[bool, bool] = models.BooleanField(
        default=False, verbose_name="Is this wave for walk-ins?"
    )

    @override
    def clean(self) -> None:
        super().clean()
        if self.start and self.end and self.start >= self.end:
            raise exceptions.ValidationError(
                {"start": "Start date can't be after end date."}
            )

        if self.pk:
            all_other: QuerySet[Wave] = Wave.objects.exclude(pk=self.pk)
        else:
            all_other: QuerySet[Wave] = Wave.objects.all()

        if not self.start or not self.end:
            return

        for wave in all_other:
            if not wave.start or not wave.end:
                continue
            has_overlap = (self.start < wave.end) and (self.end > wave.start)

            if has_overlap:
                msg = (
                    f"Cannot save wave; it overlaps with another wave (ID: {wave.pk}) "
                    f"which runs from {wave.start} to {wave.end}."
                )
                raise exceptions.ValidationError(msg)


class School(models.Model):
    """A simple model for representing colleges/universities."""

    name = models.CharField("name", max_length=255)

    @override
    def __str__(self):
        return self.name


def filename_generator(_instance, filename: str):
    if filename is None:
        logger.error(f"filename_generator received None filename for instance {_instance}")
        return f"{uuid.uuid4()}.pdf"
    path = Path(filename)
    ext = path.suffix.lower()
    return f"{uuid.uuid4()}{ext}"


class Application(models.Model):
    """Represents a `Hacker`'s application to this hackathon."""

    # ABOUT YOU
    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    age = models.PositiveIntegerField(blank=False, null=True, verbose_name="age")
    phone_number = models.CharField(
        max_length=13, blank=False, null=True, verbose_name="phone number"
    )
    country = models.CharField(
        "What is your country of residence?",
        max_length=100,
        choices=COUNTRIES_TUPLES,
        blank=False,
        null=True,
    )
    extra_links = models.CharField(
        "Point us to anything you'd like us to look at while considering your application",
        max_length=200,
        blank=True,
    )
    question1 = models.TextField(QUESTION1_TEXT, max_length=500)
    resume = models.FileField(
        "Upload your resume (PDF only)",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            FileSizeValidator(max_filesize=2.5),
        ],
        upload_to=filename_generator,
    )

    # DEMOGRAPHIC INFORMATION
    school = models.ForeignKey(
        School,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="What school do you go to?",
    )
    school_other = models.CharField(null=True, blank=True, max_length=255)
    tamu_email = models.EmailField(
        "TAMU Email if you are a Texas A&M student",
        null=True,
        blank=True,
        max_length=75,
    )
    major = models.CharField(
        "What's your major?", default=NO_ANSWER, choices=MAJORS, max_length=100
    )
    major_other = models.CharField("Other", max_length=255, null=True, blank=True)
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
    level_of_study = models.CharField(
        "What is your current level of study?",
        max_length=100,
        choices=LEVELS_OF_STUDY,
        blank=False,
        null=True,
    )
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES
    )
    wares = models.CharField(
        "TAMUhack will be partnering with IEEE to offer a dedicated hardware track and prizes. Participants can choose to compete in this track or in the general software tracks. Would you like to compete in the software or hardware track",
        choices=WARECHOICE,
        max_length=8,
        default=NO_ANSWER,
        blank=False,
        null=True,
    )

    # LEGAL INFO
    agree_to_coc = models.BooleanField(choices=AGREE, default=None)
    agree_to_mlh_stuff = models.BooleanField(
        choices=AGREE, null=True, default=None, blank=True
    )
    signup_to_mlh_newsletter = models.BooleanField(
        choices=AGREE_DISAGREE, null=True, default=None, blank=True
    )
    is_adult = models.BooleanField(
        "Please confirm you are 18 or older.",
        choices=AGREE,
        default=None,
        help_text="Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas "
        "A&M.",
    )
    agree_to_photos = models.BooleanField(choices=AGREE, null=True, default=None)
    accessibility_requirements = models.BooleanField(
        choices=AGREE_DISAGREE, null=True, default=None, blank=True
    )

    # LOGISTICAL INFO
    shirt_size = models.CharField(
        "What size shirt do you wear?", choices=SHIRT_SIZES, max_length=4
    )

    additional_accommodations = models.TextField(
        'Do you require any special accommodations at the event? Please list dietary restrictions here if you selected "food allergy" or "other".',
        max_length=500,
        blank=True,
    )

    # Emergency Contact Info
    emergency_contact_name = models.CharField(
        "Emergency Contact Name", max_length=255, blank=False
    )
    emergency_contact_relationship = models.CharField(
        "Emergency Contact Relationship", max_length=255, blank=False
    )
    emergency_contact_phone = models.CharField(
        "Emergency Contact Phone Number", max_length=255, blank=False
    )
    emergency_contact_email = models.CharField(
        "Emergency Contact Email", max_length=255, blank=False
    )

    dietary_restrictions = models.CharField(
        "Do you have any dietary restrictions?", max_length=255, blank=True, default=""
    )
    meal_group = models.CharField(max_length=255, null=True, blank=True, default=None)

    technology_experience = models.TextField(
        "What technology do you have experience with?", blank=True
    )

    # TEAM MATCHING INFO
    has_team = models.CharField(
        "Do you have a team yet?",
        choices=HAS_TEAM_OPTIONS,
        max_length=16,
    )
    discovery_method = models.CharField(
        f"How did you hear about {settings.EVENT_NAME}?",
        choices=DISCOVERY_METHOD_OPTIONS,
        help_text="",
        max_length=16,
    )

    # CONFIRMATION DEADLINE
    confirmation_deadline = models.DateTimeField(null=True, blank=True)

    # MISCELLANEOUS
    notes = models.TextField(
        "Anything else you would like us to know?", max_length=300, blank=True
    )
    # META INFO
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_submitted = models.DateTimeField(auto_now_add=True)
    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=False)
    status = models.CharField(
        choices=STATUS_OPTIONS, max_length=1, default=STATUS_PENDING
    )

    @override
    def __str__(self):
        return f"{self.last_name}, {self.first_name} - Application"

    @override
    def save(self, *args, **kwargs):
        """Override save to ensure meal group assignment logic is applied."""
        self.assign_meal_group()
        
        # Log resume upload attempts
        if self.resume:
            try:
                logger.info(f"Attempting to save resume for user {self.user.email}: {self.resume.name}")
                super().save(*args, **kwargs)
                logger.info(f"Successfully saved resume for user {self.user.email}")
            except Exception as e:
                logger.error(f"Failed to save resume for user {self.user.email}: {str(e)}")
                # Continue with save without resume
                self.resume = None
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy("application:update", args=[self.id])

    def get_next_meal_group(self):
        """Determine the next meal group.

        Counts all meal group values modulo 4, using a dictionary to assign meal groups.
        """
        meal_group_map = {0: "A", 1: "B", 2: "C", 3: "D"}
        non_null_count = (
            Application.objects.filter(status=STATUS_CONFIRMED)
            .exclude(meal_group__isnull=True)
            .count()
        )
        next_group_num = non_null_count % 4
        return meal_group_map[next_group_num]

    def assign_meal_group(self):
        """Assign a meal group based on the current status."""
        if self.status == STATUS_CONFIRMED:  # Confirmed
            self.meal_group = self.get_next_meal_group()
        elif self.status == "E":  # Waitlisted
            self.meal_group = "E"
        else:
            self.meal_group = None

    def clean(self):
        super().clean()

        def is_valid_name(name):
            pattern = r"^(?=.{1,40}$)[a-zA-Z]+(?:[-' ][a-zA-Z]+)*$"

            match = re.match(pattern, name)

            return bool(match)

        if (not self.is_adult and self.age > MAX_AGE) or (
            self.is_adult and self.age < MAX_AGE
        ):
            msg = (
                "Age and adult status do not match. Please confirm you are 18 or older."
            )
            raise exceptions.ValidationError(msg)
        # Fixes the obos admin panel bug, idk why the checkbox doesn't show up
        if not self.age >= MAX_AGE or not self.is_adult:
            msg = (
                "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email "
                f"us at {settings.ORGANIZER_EMAIL}. "
            )
            raise exceptions.ValidationError(msg)

        if not is_valid_name(self.first_name):
            msg = (
                "First name can only contain letters, spaces, hyphens, and apostrophes."
            )
            raise exceptions.ValidationError(msg)
        if not is_valid_name(self.last_name):
            msg = (
                "Last name can only contain letters, spaces, hyphens, and apostrophes."
            )
            raise exceptions.ValidationError(msg)

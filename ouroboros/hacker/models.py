import datetime
import json
import random
import string

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core import mail, exceptions
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import html, timezone
from multiselectfield import MultiSelectField

TRUE_FALSE_CHOICES = (
    (True, "Yes"),
    (False, "No")
)

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

RACES = (
    ("American Indian", "American Indian or Alaskan Native"),
    ("Asian", "Asian"),
    ("Black", "Black or African-American"),
    ("Hispanic", "Hispanic or Latino White"),
    ("Native Hawaiian", "Native Hawaiian or other Pacific Islander"),
    ("White", "White or Caucasian"),
    ("NA", "Decline to self-identify")
)

CLASSIFICATIONS = [("Fr", "Freshman"), ("So", "Sophomore"), ("Jr", "Junior"), ("Sr", "Senior"), ("Ot", "Other")]

DIETARY_RESTRICTIONS = (
    ("Vegan", "Vegan"),
    ("Vegetarian", "Vegetarian"),
    ("Halal", "Halal"),
    ("Kosher", "Kosher"),
    ("Food Allergies", "Food Allergies"),
)

HACKATHON_TIMES = [("0", "This will be my first!"), ("1-3", "1-3"), ("4-7", "4-7"), ("8-10", "8-10"), ("10+", "10+")]

# GRAD_YEARS = [
#     (i, i)
#     for i in range(
#         timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION
#     )
# ]


GRAD_YEARS = []
for i in range(timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION):
    for j in ['Spring', 'Fall']:
        GRAD_YEARS.append(("%s %i"%(j,i), "%s %i"%(j,i)))
GRAD_YEARS = GRAD_YEARS[1:-1]
GRAD_YEARS.append(("Other", "Other"))

class HackerManager(BaseUserManager):
    """
    Custom manager to deal with emails as unique IDs for auth instead of usernames.
    """

    def _create_user(self, email, password, **kwargs):
        """
        Creates/saves a User with given email and password.
        """
        if not email:
            raise ValueError("Email field in Hacker must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if kwargs.get("is_staff") is None:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get("is_superuser") is None:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **kwargs)


class Hacker(AbstractBaseUser, PermissionsMixin):
    """
    Represents an individual hacker. This model overrides Django's default `User`
    to make some optional fields required. One important piece of behavior to
    note is that `Hacker`s by default are INACTIVE until they confirm their
    email, and cannot authenticate until email verification has occurred.
    
    During testing, simply setting the `is_active` field to `True` will bypass
    email verification.
    """

    objects = HackerManager()

    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )

    is_active = models.BooleanField(
        "active",
        default=False,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
    )
    first_name = models.CharField(
        max_length=255, blank=False, verbose_name="first name"
    )
    last_name = models.CharField(max_length=255, blank=False, verbose_name="last name")

    rsvp_deadline = models.DateTimeField(null=True)
    cant_make_it = models.BooleanField(default=False)

    checked_in = models.NullBooleanField(blank=True)
    checked_in_datetime = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def didnt_rsvp_in_time(self):
        return (
            not getattr(self, "rsvp", None)
            and getattr(self, "rsvp_deadline", None) is not None
            and self.rsvp_deadline < timezone.now()
        )

    def email_hacker(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        mail.send_mail(subject, message, from_email, [self.email], **kwargs)

    def email_html_hacker(self, template_name, context, subject):
        """Send an HTML email to the hacker."""
        html_msg = render_to_string(template_name, context)
        msg = html.strip_tags(html_msg)
        self.email_hacker(subject, msg, html_message=html_msg)


class WaveManager(models.Manager):
    def next_wave(self, dt: datetime.datetime = timezone.now()):
        """
        Returns the next INACTIVE wave, if one exists. For the CURRENT active wave, use
        `active_wave`.
        """
        qs = self.get_queryset().filter(start__gt=dt).order_by("start")
        return qs.first()

    def active_wave(self, dt: datetime.datetime = timezone.now()):
        """
        Returns the CURRENTLY active wave, if one exists. For the next INACTIVE wave, use
        `next_wave`.
        """
        qs = self.get_queryset().filter(start__lte=dt, end__gt=dt).order_by("start")
        return qs.first()


class Wave(models.Model):
    """
    Representation of a registration period. `Application`s must be created during
    a `Wave`, and are automatically associated with a wave through the `Application`'s `pre_save` handler.
    """

    start = models.DateTimeField()
    end = models.DateTimeField()

    objects = WaveManager()

    def clean(self):
        super().clean()
        if self.start >= self.end:
            raise exceptions.ValidationError(
                {"start": "Start date can't be after end date."}
            )


class Application(models.Model):
    """
    Represents a `Hacker`'s application to this hackathon.
    """

    adult = models.BooleanField("Are you at least 18 or older?", choices=TRUE_FALSE_CHOICES, default=False, help_text="NOTE: We are able to admit minors only if they are accompanied by a college student (18+) who is planning on participating in the hackathon. Have additional questions? Email us at highschool@tamuhack.com")
    major = models.CharField("What's your major?", max_length=50)
    gender = models.CharField("What's your gender?", choices=GENDERS, max_length=2)
    race = MultiSelectField("What race do you identify with?", choices=RACES, max_length=41)
    classification = models.CharField("What classification are you?", choices=CLASSIFICATIONS, max_length=2)
    grad_year = models.IntegerField("What is your anticipated graduation date?", choices=GRAD_YEARS)
    dietary_restrictions = MultiSelectField(
        "Do you have any dietary restrictions that we should know about?", choices=DIETARY_RESTRICTIONS, blank=True
    )
    num_hackathons_attended = models.CharField("How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES)
    previous_attendant = models.BooleanField("Have you attended Howdy Hack before?", choices=TRUE_FALSE_CHOICES, default=False)
    tamu_student = models.BooleanField("Are you a Texas A&M student?", choices=TRUE_FALSE_CHOICES, default=True)

    shirt_size = models.CharField("Shirt size?", choices=SHIRT_SIZES, max_length=3)
    extra_links = models.CharField("Point us to anything you'd like us to look at while considering your application", max_length=200, help_text="Links to LinkedIn, GitHub, Devpost, Personal Website, etc.")
    programming_joke = models.TextField("Tell us your best programming joke", max_length=500)
    unlimited_resource = models.TextField("What is the one thing you'd build if you had unlimited resources?", max_length=500)
    cool_prize = models.TextField("What is a cool prize you'd like to win at TAMUhack?", max_length=500)
    notes = models.TextField(
        max_length=300,
        blank=True,
        help_text="Provide any additional notes and/or comments in the text box provided",
    )
    resume = models.FileField("Provide us a copy of your most recent resume so we can get you connected with companies.")

    approved = models.NullBooleanField(blank=True)

    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Application" % (self.hacker.last_name, self.hacker.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application", args=[self.pk])


class Rsvp(models.Model):
    """
    Represents a `Hacker`'s confirmation that they are attending this hackathon.
    """
    notes = models.TextField(
        max_length=300,
        blank=True,
        help_text="Provide any additional notes and/or comments in the text box provided",
    ) 

    date_rsvped = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Rsvp" % (self.hacker.last_name, self.hacker.first_name)


def send_rsvp_creation_email(hacker: Hacker) -> None:
    email_template = "emails/rsvp/created.html"
    subject = f"Your {settings.EVENT_NAME} RSVP has been received!"
    context = {"first_name": hacker.first_name, "event_name": settings.EVENT_NAME}

    hacker.email_html_hacker(email_template, context, subject)


@receiver(signal=post_save, sender=Rsvp)
def on_rsvp_post_save(sender, instance, *args, **kwargs):
    created = kwargs["created"]
    if created:
        send_rsvp_creation_email(instance.hacker)

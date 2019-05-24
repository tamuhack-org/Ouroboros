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
from django.core import mail
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import html, timezone
from multiselectfield import MultiSelectField

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

CLASSIFICATIONS = [
    ("U1", "U1"),
    ("U2", "U2"),
    ("U3", "U3"),
    ("U4", "U4"),
]

DIETARY_RESTRICTIONS = (
    ("Vegan", "Vegan"),
    ("Vegetarian", "Vegetarian"),
    ("Halal", "Halal"),
    ("Kosher", "Kosher"),
    ("Food Allergies", "Food Allergies"),
)


GRAD_YEARS = [
    (i, i)
    for i in range(
        timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION
    )
]


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
        return not getattr(self, "rsvp", None) and self.rsvp_deadline < timezone.now()


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


class Application(models.Model):
    """
    Represents a `Hacker`'s application to this hackathon.
    """

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
        help_text="Provide any additional notes and/or comments in the text box provided",
    )
    resume = models.FileField(upload_to="hacker_resumes", null=True, blank=True)

    approved = models.NullBooleanField(blank=True)

    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Application" % (self.hacker.last_name, self.hacker.first_name)


@receiver(pre_save, sender=Application)
def application_approved(sender, instance: Application, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if not obj.approved and instance.approved:
            deadline = timezone.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            ) + datetime.timedelta(days=settings.DAYS_TO_RSVP)
            instance.hacker.rsvp_deadline = deadline
            instance.hacker.save()
            send_application_approved_email(instance.hacker)


def send_application_approved_email(hacker: Hacker):
    # User has been approved!
    email_template = "emails/application/approved.html"
    subject = f"Your {settings.EVENT_NAME} application has been approved!"

    html_message = render_to_string(
        email_template,
        context={"first_name": hacker.first_name, "event_name": settings.EVENT_NAME},
    )
    msg = html.strip_tags(html_message)
    mail.send_mail(
        subject,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        [hacker.email],
        html_message=html_message,
    )


@receiver(post_save, sender=Application)
def send_application_email(sender, instance: Application, **kwargs):
    if instance.approved:
        # Don't send two emails when a user's application gets approved.
        # It's not like they'll be making edits to their application afterwards anyway
        return
    created: bool = kwargs["created"]

    email_template = "emails/application/updated.html"
    subject = f"Your {settings.EVENT_NAME} application has been updated!"
    if created:
        email_template = "emails/application/created.html"
        subject = f"Your {settings.EVENT_NAME} application has been created!"

    hacker: Hacker = instance.hacker
    html_message = render_to_string(
        email_template,
        context={"first_name": hacker.first_name, "event_name": settings.EVENT_NAME},
    )
    msg = html.strip_tags(html_message)
    mail.send_mail(
        subject,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        [hacker.email],
        html_message=html_message,
    )


class Rsvp(models.Model):
    """
    Represents a `Hacker`'s confirmation that they are attending this hackathon.
    """

    shirt_size = models.CharField(
        max_length=3, choices=SHIRT_SIZES, verbose_name="shirt size"
    )
    notes = models.TextField(
        max_length=300,
        blank=True,
        help_text="Provide any additional notes and/or comments in the text box provided",
    )

    date_rsvped = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Rsvp" % (self.hacker.last_name, self.hacker.first_name)


@receiver(post_save, sender=Rsvp)
def send_rsvp_email(sender, **kwargs):
    rsvp: Rsvp = kwargs["instance"]
    created: bool = kwargs["created"]

    email_template = "emails/rsvp/updated.html"
    subject = f"Your {settings.EVENT_NAME} RSVP has been updated!"
    if created:
        email_template = "emails/rsvp/created.html"
        subject = f"Your {settings.EVENT_NAME} RSVP has been created!"
    hacker: Hacker = rsvp.hacker
    html_message = render_to_string(
        email_template,
        context={"first_name": hacker.first_name, "event_name": settings.EVENT_NAME},
    )
    msg = html.strip_tags(html_message)
    mail.send_mail(
        subject,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        [hacker.email],
        html_message=html_message,
    )

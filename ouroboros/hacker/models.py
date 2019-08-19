import datetime
import json
import random
import string
from io import BytesIO
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import FileExtensionValidator
from django.core import mail, exceptions
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import html, timezone
from multiselectfield import MultiSelectField
import pyqrcode

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


class Rsvp(models.Model):
    """
    Represents a `Hacker`'s confirmation that they are attending this hackathon.
    """

    notes = models.TextField(
        "Anything else you want us to know?",
        max_length=300,
        blank=True,
        help_text="Please let us know if there's anything else we can do to make %s an amazing experience for you!"
        % (settings.EVENT_NAME),
    )

    date_rsvped = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)
    dietary_restrictions = MultiSelectField(
        "Do you have any dietary restrictions that we should know about?",
        choices=DIETARY_RESTRICTIONS,
        blank=True,
    )
    shirt_size = models.CharField(
        "Shirt size?", choices=SHIRT_SIZES, default=None, max_length=3
    )

    def __str__(self):
        return "%s, %s - Rsvp" % (
            self.hacker.application.last_name,
            self.hacker.application.first_name,
        )


def send_rsvp_creation_email(hacker: Hacker) -> None:
    email_template = "emails/rsvp/created.html"
    subject = f"Your {settings.EVENT_NAME} RSVP has been received!"
    context = {
        "first_name": hacker.application.first_name,
        "event_name": settings.EVENT_NAME,
    }

    html_msg = render_to_string(email_template, context)
    msg = html.strip_tags(html_msg)
    email = mail.EmailMultiAlternatives(
        subject, msg, from_email=None, to=[hacker.email]
    )
    email.attach_alternative(html_msg, "text/html")

    qr_content = json.dumps(
        {
            "first_name": hacker.application.first_name,
            "last_name": hacker.application.last_name,
            "email": hacker.email,
            "university": "Texas A&M University",  # TODO: Remove this hard-coding.
        }
    )
    qr_code = pyqrcode.create(qr_content)
    qr_stream = BytesIO()
    qr_code.png(qr_stream, scale=5)
    email.attach("code.png", qr_stream.getvalue(), "text/png")
    email.send()


@receiver(signal=post_save, sender=Rsvp)
def on_rsvp_post_save(sender, instance, *args, **kwargs):
    created = kwargs["created"]
    if created:
        send_rsvp_creation_email(instance.hacker)

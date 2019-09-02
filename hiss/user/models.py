from django.core import mail
from django.template.loader import render_to_string
from django.utils import html, timezone

from django.contrib.auth import models as auth_models
from django.db import models


class EmailUserManager(auth_models.UserManager):
    """
    An implementation of the UserManager that looks up based on email instead of based on username.
    """

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(auth_models.AbstractUser, auth_models.PermissionsMixin):
    """
    A representation of a user within the registration system. Users are uniquely identified by their email,
    and are inactive until they confirm their email.
    """

    objects = EmailUserManager()

    # Set email to the primary lookup field
    email = models.EmailField(unique=True, null=False, blank=False)
    is_active = models.BooleanField(
        "active",
        default=False,
        help_text="Designates whether this user should be treated as active. Unselect "
        "this instead of deleting accounts.",
    )

    # Explicitly delete Django's old fields
    username = None
    first_name = None
    last_name = None

    # Registration system-specific fields

    # Applying
    application = models.ForeignKey("Application", null=True, on_delete=models.SET_NULL)

    # RSVPing
    rsvp = models.ForeignKey("Rsvp", null=True, on_delete=models.SET_NULL, related_name="user")
    rsvp_deadline = models.DateTimeField(null=True, blank=True)
    declined_acceptance = models.BooleanField(default=False)

    # Volunteering
    # volunteer_application = models.ForeignKey("VolunteerApplication", null=True, on_delete=models.SET_NULL)

    # Day-of
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

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


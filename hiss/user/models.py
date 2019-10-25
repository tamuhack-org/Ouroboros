# pylint: disable=C0330
from django.contrib.auth import models as auth_models
from django.db import models
from django.template.loader import render_to_string
from django.utils import html


class EmailUserManager(auth_models.UserManager):
    """
    An implementation of the UserManager that looks up based on email instead of based on username.
    """

    def _create_user(self, email, password, **extra_fields):  # pylint: disable=W0221
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):  # pylint: disable=W0221
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email, password, **extra_fields
    ):  # pylint: disable=W0221
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


class User(auth_models.AbstractUser):
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

    rsvp_deadline = models.DateTimeField(null=True, blank=True)
    declined_acceptance = models.BooleanField(default=False)

    # Day-of
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(
        "team.Team",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="members",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def send_html_email(self, template_name, context, subject):
        """Send an HTML email to the user."""
        html_msg = render_to_string(template_name, context)
        msg = html.strip_tags(html_msg)
        self.email_user(subject, msg, None, html_message=html_msg)

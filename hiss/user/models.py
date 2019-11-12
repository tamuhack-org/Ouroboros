# pylint: disable=C0330
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import html
from rest_framework.authtoken.models import Token


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

    # Day-of
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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(
    sender, instance: User = None, created: bool = False, **kwargs
) -> None:
    """
    Using Django's model signals (https://docs.djangoproject.com/en/2.2/topics/signals/), creates a new Django Rest
    Framework Token for a newly-created user, for later use with Django Rest Framework's TokenAuthentication.
    See https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication for more details.
    :param sender: The class that triggered this receiver (in this case, our User class)
    :param instance: The specific User that triggered this signal.
    :param created: Whether the user was created (or merely updated)
    :param kwargs: Other keyword arguments. See https://docs.djangoproject.com/en/2.2/topics/signals/ for more details.
    :return: None
    """
    if created:
        # This user was just created, they need a new Token!
        Token.objects.create(user=instance)

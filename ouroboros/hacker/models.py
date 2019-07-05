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
    (None, "-- Select Option --"),
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

GENDERS = (
    (None, "-- Select Option --"),
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

CLASSIFICATIONS = [(None, "-- Select Option --"), ("Fr", "Freshman"), ("So", "Sophomore"), ("Jr", "Junior"), ("Sr", "Senior"), ("Ot", "Other")]

DIETARY_RESTRICTIONS = (
    ("Vegan", "Vegan"),
    ("Vegetarian", "Vegetarian"),
    ("Halal", "Halal"),
    ("Kosher", "Kosher"),
    ("Food Allergies", "Food Allergies"),
)

MAJORS = [(None, "-- Select Option --"), ('Accounting', 'Accounting'), ('Actuarial Science', 'Actuarial Science'), ('Advertising', 'Advertising'), ('Agriculture', 'Agriculture'), ('Agricultural and Biological Engineering', 'Agricultural and Biological Engineering'), ('Agricultural Business Management', 'Agricultural Business Management'), ('Agriculture Economics', 'Agriculture Economics'), ('Animal Bioscience', 'Animal Bioscience'), ('Animal Sciences', 'Animal Sciences'), ('Anthropology', 'Anthropology'), ('Applied Mathematics', 'Applied Mathematics'), ('Archaeology', 'Archaeology'), ('Architectural Engineering', 'Architectural Engineering'), ('Architecture', 'Architecture'), ('Art History', 'Art History'), ('Studio Art', 'Studio Art'), ('Art Education', 'Art Education'), ('Biobehavioral Health', 'Biobehavioral Health'), ('Biochemistry', 'Biochemistry'), ('Bioengineering', 'Bioengineering'), ('Biology', 'Biology'), ('Biophysics', 'Biophysics'), ('Biotechnology', 'Biotechnology'), ('Business Administration and Management', 'Business Administration and Management'), ('Business Logistics', 'Business Logistics'), ('Chemical Engineering', 'Chemical Engineering'), ('Chemistry', 'Chemistry'), ('Children', 'Children'), ('Civil Engineering', 'Civil Engineering'), ('Computer Engineering', 'Computer Engineering'), ('Computer Science', 'Computer Science'), ('Crime, Law, and Justice', 'Crime, Law, and Justice'), ('Dance', 'Dance'), ('Earth Sciences', 'Earth Sciences'), ('Economics', 'Economics'), ('Electrical Engineering', 'Electrical Engineering'), ('Elementary and Kindergarten Education', 'Elementary and Kindergarten Education'), ('Engineering Science', 'Engineering Science'), ('English', 'English'), ('Environmental Systems Engineering', 'Environmental Systems Engineering'), ('Environmental Sciences', 'Environmental Sciences'), ('Environmental Resource Management', 'Environmental Resource Management'), ('Film and Video', 'Film and Video'), ('Finance', 'Finance'), ('Food Science', 'Food Science'), ('Forest Science', 'Forest Science'), ('Forest Technology', 'Forest Technology'), ('General Science', 'General Science'), ('Geography', 'Geography'), ('Geosciences', 'Geosciences'), ('Graphic Design and Photography', 'Graphic Design and Photography'), ('Health and Physical Education', 'Health and Physical Education'), ('Health Policy and Administration', 'Health Policy and Administration'), ('History', 'History'), ('Horticulture', 'Horticulture'), ('Hotel, Restaurant, and Institutional Management', 'Hotel, Restaurant, and Institutional Management'), ('Human Development and Family Studies', 'Human Development and Family Studies'), ('Individual and Family Studies', 'Individual and Family Studies'), ('Industrial Engineering', 'Industrial Engineering'), ('Information Sciences and Technology', 'Information Sciences and Technology'), ('Journalism', 'Journalism'), ('Kinesiology', 'Kinesiology'), ('Landscape Architecture', 'Landscape Architecture'), ('Law Enforcement and Correction', 'Law Enforcement and Correction'), ('Marine Biology', 'Marine Biology'), ('Marketing', 'Marketing'), ('Mathematics', 'Mathematics'), ('Mechanical Engineering', 'Mechanical Engineering'), ('Media Studies', 'Media Studies'), ('Meteorology', 'Meteorology'), ('Microbiology', 'Microbiology'), ('Mineral Economics', 'Mineral Economics'), ('Modern Languages', 'Modern Languages'), ('Music Education', 'Music Education'), ('Nuclear Engineering', 'Nuclear Engineering'), ('Nursing', 'Nursing'), ('Nutrition', 'Nutrition'), ('Philosophy', 'Philosophy'), ('Physics', 'Physics'), ('Physiology', 'Physiology'), ('Political Science', 'Political Science'), ('Pre-medicine', 'Pre-medicine'), ('Psychology', 'Psychology'), ('Public Relations', 'Public Relations'), ('Real Estate', 'Real Estate'), ('Recreation and Parks', 'Recreation and Parks'), ('Rehabilitation Services', 'Rehabilitation Services'), ('Religious Studies', 'Religious Studies'), ('Secondary Education', 'Secondary Education'), ('Sociology', 'Sociology'), ('Social Work', 'Social Work'), ('Special Education', 'Special Education'), ('Speech Communication', 'Speech Communication'), ('Speech Pathology and Audiology/Communication Disorder', 'Speech Pathology and Audiology/Communication Disorder'), ('Statistics', 'Statistics'), ('Telecommunications', 'Telecommunications'), ('Theater', 'Theater'), ('Wildlife and Fishery Science', 'Wildlife and Fishery Science'), ('Wildlife Technology', 'Wildlife Technology'), ("Women's Studies", "Women's Studies")]

HACKATHON_TIMES = [(None, "-- Select Option --"), ("0", "This will be my first!"), ("1-3", "1-3"), ("4-7", "4-7"), ("8-10", "8-10"), ("10+", "10+")]

GRAD_YEARS = []
for i in range(timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION):
    for j in ['Spring', 'Fall']:
        GRAD_YEARS.append(("%s %i"%(j,i), "%s %i"%(j,i)))
GRAD_YEARS = GRAD_YEARS[1:-1]
GRAD_YEARS.insert(0, (None, "-- Select Option --"))
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

    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name", 
    )
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name="last name")
    adult = models.BooleanField("Are you at least 18 or older?", choices=TRUE_FALSE_CHOICES, default=None)
    major = models.CharField("What's your major?", choices=MAJORS, max_length=50)
    gender = models.CharField("What's your gender?", choices=GENDERS, max_length=2)
    race = MultiSelectField("What race(s) do you identify with?", choices=RACES, max_length=41)
    classification = models.CharField("What classification are you?", choices=CLASSIFICATIONS, max_length=2)
    grad_year = models.CharField("What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11)
    num_hackathons_attended = models.CharField("How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES)
    previous_attendant = models.BooleanField(f"Have you attended {settings.EVENT_NAME} before?", choices=TRUE_FALSE_CHOICES, default=False)
    tamu_student = models.BooleanField("Are you a Texas A&M student?", choices=TRUE_FALSE_CHOICES, default=True)
    extra_links = models.CharField("Point us to anything you'd like us to look at while considering your application", max_length=200)
    programming_joke = models.TextField("Tell us your best programming joke", max_length=500)
    unlimited_resource = models.TextField("What is the one thing you'd build if you had unlimited resources?", max_length=500)
    cool_prize = models.TextField(f"What is a cool prize you'd like to win at {settings.EVENT_NAME}?", max_length=500)
    notes = models.TextField("Anything else you would like us to know?",
        max_length=300,
        blank=True,
    )
    resume = models.FileField("Upload your resume", help_text="Companies will use this resume to offer interviews for internships and full-time positions.")

    approved = models.NullBooleanField(blank=True)

    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Application" % (self.hacker.last_name, self.hacker.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application", args=[self.pk])
    
    def clean(self):
        super().clean()
        if not self.adult:
            raise exceptions.ValidationError("Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email us at highschool@tamuhack.com.")
        if any(char.isdigit() for char in self.first_name):
            raise exceptions.ValidationError("First name can't contain any numbers")
        if any(char.isdigit() for char in self.last_name):
            raise exceptions.ValidationError("Last name can't contain any numbers")


class Rsvp(models.Model):
    """
    Represents a `Hacker`'s confirmation that they are attending this hackathon.
    """
    notes = models.TextField("Anything else you want us to know?",
        max_length=300,
        blank=True,
        help_text="Please let us know if there's anything else we can do to make %s an amazing experience for you!"%(settings.EVENT_NAME),
    )

    date_rsvped = models.DateField(auto_now_add=True, blank=True)

    hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)
    dietary_restrictions = MultiSelectField(
        "Do you have any dietary restrictions that we should know about?", choices=DIETARY_RESTRICTIONS, blank=True
    )
    shirt_size = models.CharField("Shirt size?", choices=SHIRT_SIZES, max_length=3)

    def __str__(self):
        return "%s, %s - Rsvp" % (self.hacker.application.last_name, self.hacker.application.first_name)


def send_rsvp_creation_email(hacker: Hacker) -> None:
    email_template = "emails/rsvp/created.html"
    subject = f"Your {settings.EVENT_NAME} RSVP has been received!"
    context = {"first_name": hacker.application.first_name, "event_name": settings.EVENT_NAME}

    hacker.email_html_hacker(email_template, context, subject)


@receiver(signal=post_save, sender=Rsvp)
def on_rsvp_post_save(sender, instance, *args, **kwargs):
    created = kwargs["created"]
    if created:
        send_rsvp_creation_email(instance.hacker)

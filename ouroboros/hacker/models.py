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
from django.utils.safestring import mark_safe

AGREE = (("Agree", ""),)

TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))

SHIRT_SIZES = (
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
    ('Other', 'Other'),
    ("NA", "Prefer not to disclose"),
)

RACES = (
    ("American Indian", "American Indian or Alaskan Native"),
    ("Asian", "Asian"),
    ("Black", "Black or African-American"),
    ("Hispanic", "Hispanic or Latino White"),
    ("Native Hawaiian", "Native Hawaiian or other Pacific Islander"),
    ("White", "White or Caucasian"),
    ('Other', 'Other'),
    ("NA", "Decline to self-identify"),
)

CLASSIFICATIONS = [
    (None, "-- Select Option --"),
    ("Fr", "Freshman"),
    ("So", "Sophomore"),
    ("Jr", "Junior"),
    ("Sr", "Senior"),
    ("Ot", "Other"),
]

DIETARY_RESTRICTIONS = (
    ("Vegan", "Vegan"),
    ("Vegetarian", "Vegetarian"),
    ("Halal", "Halal"),
    ("Kosher", "Kosher"),
    ("Food Allergies", "Food Allergies"),
)

MAJORS = [
    (None, "-- Select Option --"),
    ('Accounting', 'Accounting'),
    ('Aerospace Engineering', 'Aerospace Engineering'),
    ('Agribusiness', 'Agribusiness'),
    ('Agricultural Communications & Journalism', 'Agricultural Communications & Journalism'),
    ('Agricultural Economics', 'Agricultural Economics'),
    ('Agricultural Leadership & Development', 'Agricultural Leadership & Development'),
    ('Agricultural Science', 'Agricultural Science'),
    ('Agricultural Systems Management', 'Agricultural Systems Management'),
    ('Animal Science', 'Animal Science'),
    ('Anthropology', 'Anthropology'),
    ('Applied Mathematical Sciences', 'Applied Mathematical Sciences'),
    ('Architectural Engineering', 'Architectural Engineering'),
    ('Biochemistry', 'Biochemistry'),
    ('Bioenvironmental Sciences', 'Bioenvironmental Sciences'),
    ('Biological & Agricultural Engineering', 'Biological & Agricultural Engineering'),
    ('Biology', 'Biology'),
    ('Biomedical Engineering', 'Biomedical Engineering'),
    ('Biomedical Sciences', 'Biomedical Sciences'),
    ('Business Honors', 'Business Honors'),
    ('Chemical Engineering', 'Chemical Engineering'),
    ('Chemistry', 'Chemistry'),
    ('Civil Engineering', 'Civil Engineering'),
    ('Classics', 'Classics'),
    ('Communication', 'Communication'),
    ('Community Health', 'Community Health'),
    ('Computer Engineering', 'Computer Engineering'),
    ('Computer Science', 'Computer Science'),
    ('Computing', 'Computing'),
    ('Construction Science', 'Construction Science'),
    ('Ecological Restoration', 'Ecological Restoration'),
    ('Economics', 'Economics'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Electronic Systems Engineering Technology', 'Electronic Systems Engineering Technology'),
    ('English', 'English'),
    ('Entomology', 'Entomology'),
    ('Environmental Design', 'Environmental Design'),
    ('Environmental Engineering', 'Environmental Engineering'),
    ('Environmental Geosciences', 'Environmental Geosciences'),
    ('Environmental Studies (COALS)', 'Environmental Studies (COALS)'),
    ('Environmental Studies (Geosciences)', 'Environmental Studies (Geosciences)'),
    ('Finance', 'Finance'),
    ('Food Science & Technology', 'Food Science & Technology'),
    ('Food Systems Industry Management', 'Food Systems Industry Management'),
    ('Forensic & Investigative Sciences', 'Forensic & Investigative Sciences'),
    ('Forestry', 'Forestry'),
    ('General Studies', 'General Studies'),
    ('Genetics', 'Genetics'),
    ('Geographic Information Science & Technology', 'Geographic Information Science & Technology'),
    ('Geography', 'Geography'),
    ('Geology', 'Geology'),
    ('Geophysics', 'Geophysics'),
    ('Health', 'Health'),
    ('History', 'History'),
    ('Horticulture', 'Horticulture'),
    ('Human Resource Development', 'Human Resource Development'),
    ('Industrial Distribution', 'Industrial Distribution'),
    ('Industrial Engineering', 'Industrial Engineering'),
    ('Interdisciplinary Engineering', 'Interdisciplinary Engineering'),
    ('Interdisciplinary Studies - Bilingual Education', 'Interdisciplinary Studies - Bilingual Education'),
    ('Interdisciplinary Studies - Language Arts/Social Studies Middle Grades Certification', 'Interdisciplinary Studies - Language Arts/Social Studies Middle Grades Certification'),
    ('Interdisciplinary Studies - Math/Science Middle Grades Certification ', 'Interdisciplinary Studies - Math/Science Middle Grades Certification '),
    ('Interdisciplinary Studies - PreK-6 Generalist Certification', 'Interdisciplinary Studies - PreK-6 Generalist Certification'),
    ('Interdisciplinary Studies - Special Education', 'Interdisciplinary Studies - Special Education'),
    ('International Studies', 'International Studies'),
    ('Kinesiology - Dance Science', 'Kinesiology - Dance Science'),
    ('Kinesiology - Exercise & Sport Science', 'Kinesiology - Exercise & Sport Science'),
    ('Kinesiology - Exercise Science', 'Kinesiology - Exercise Science'),
    ('Kinesiology - Physical Education Teacher Certification', 'Kinesiology - Physical Education Teacher Certification'),
    ('Landscape Architecture', 'Landscape Architecture'),
    ('Management', 'Management'),
    ('Management Information Systems', 'Management Information Systems'),
    ('Manufacturing & Mechanical Engineering Technology', 'Manufacturing & Mechanical Engineering Technology'),
    ('Marine Biology', 'Marine Biology'),
    ('Marine Engineering Technology', 'Marine Engineering Technology'),
    ('Marine Fisheries', 'Marine Fisheries'),
    ('Marine Sciences', 'Marine Sciences'),
    ('Marine Transportation', 'Marine Transportation'),
    ('Maritime Administration', 'Maritime Administration'),
    ('Maritime Studies', 'Maritime Studies'),
    ('Marketing', 'Marketing'),
    ('Materials Science and Engineering', 'Materials Science and Engineering'),
    ('Mathematics', 'Mathematics'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Meteorology', 'Meteorology'),
    ('Microbiology', 'Microbiology'),
    ('Modern Languages (French', 'Modern Languages (French'),
    ('Molecular and Cell Biology', 'Molecular and Cell Biology'),
    ('Multidisciplinary Engineering Technology', 'Multidisciplinary Engineering Technology'),
    ('Nuclear Engineering', 'Nuclear Engineering'),
    ('Nursing', 'Nursing'),
    ('Nutritional Sciences', 'Nutritional Sciences'),
    ('Ocean and Coastal Resources', 'Ocean and Coastal Resources'),
    ('Ocean Engineering', 'Ocean Engineering'),
    ('Oceanography', 'Oceanography'),
    ('Performance Studies', 'Performance Studies'),
    ('Petroleum Engineering', 'Petroleum Engineering'),
    ('Philosophy', 'Philosophy'),
    ('Physics', 'Physics'),
    ('Plant & Environmental Soil Science', 'Plant & Environmental Soil Science'),
    ('Political Science', 'Political Science'),
    ('Poultry Science', 'Poultry Science'),
    ('Psychology', 'Psychology'),
    ('Public Health', 'Public Health'),
    ('Rangeland Ecology & Management', 'Rangeland Ecology & Management'),
    ('Recreation Park & Tourism Sciences', 'Recreation Park & Tourism Sciences'),
    ('Renewable Natural Resources', 'Renewable Natural Resources'),
    ('Sociology', 'Sociology'),
    ('Spanish', 'Spanish'),
    ('Spatial Sciences', 'Spatial Sciences'),
    ('Sport Management', 'Sport Management'),
    ('Statistics', 'Statistics'),
    ('Supply Chain Management', 'Supply Chain Management'),
    ('Technology Management', 'Technology Management'),
    ('Telecommunication Media Studies', 'Telecommunication Media Studies'),
    ('Turfgrass Science', 'Turfgrass Science'),
    ('University Studies - Bioinformatics', 'University Studies - Bioinformatics'),
    ('University Studies - Biomedical Sciences', 'University Studies - Biomedical Sciences'),
    ('University Studies - Business', 'University Studies - Business'),
    ('University Studies - Child Professional Services', 'University Studies - Child Professional Services'),
    ('University Studies - Dance', 'University Studies - Dance'),
    ('University Studies - Environmental Business', 'University Studies - Environmental Business'),
    ('University Studies - Geographic Information Sciences & Technology', 'University Studies - Geographic Information Sciences & Technology'),
    ('University Studies - Geography', 'University Studies - Geography'),
    ('University Studies - Global Arts', 'University Studies - Global Arts'),
    ('University Studies - Health Humanities', 'University Studies - Health Humanities'),
    ('University Studies - Journalism Studies', 'University Studies - Journalism Studies'),
    ('University Studies - Leadership Studies', 'University Studies - Leadership Studies'),
    ('University Studies - Liberal Arts', 'University Studies - Liberal Arts'),
    ('University Studies - Marine Environmental Law & Policy', 'University Studies - Marine Environmental Law & Policy'),
    ('University Studies - Maritime Public Policy & Communication', 'University Studies - Maritime Public Policy & Communication'),
    ('University Studies - Mathematics for Business', 'University Studies - Mathematics for Business'),
    ('University Studies - Mathematics for Pre-Professionals', 'University Studies - Mathematics for Pre-Professionals'),
    ('University Studies - Mathematics for Secondary Teaching', 'University Studies - Mathematics for Secondary Teaching'),
    ('University Studies - Oceans & One Health', 'University Studies - Oceans & One Health'),
    ('University Studies - Race', 'University Studies - Race'),
    ('University Studies - Religious Thought', 'University Studies - Religious Thought'),
    ('University Studies - Science for Secondary Teaching', 'University Studies - Science for Secondary Teaching'),
    ('University Studies - Society', 'University Studies - Society'),
    ('University Studies - Sports Conditioning', 'University Studies - Sports Conditioning'),
    ('University Studies - Tourism & Coastal Community Development', 'University Studies - Tourism & Coastal Community Development'),
    ('Urban & Regional Planning', 'Urban & Regional Planning'),
    ('Visualization', 'Visualization'),
    ('Wildlife & Fisheries Sciences', 'Wildlife & Fisheries Sciences'),
    ("Women's & Gender Studies", "Women's & Gender Studies"),
    ('Zoology', 'Zoology'),
    ('Other', 'Other')
]

HACKATHON_TIMES = [
    (None, "-- Select Option --"),
    ("0", "This will be my first!"),
    ("1-3", "1-3"),
    ("4-7", "4-7"),
    ("8-10", "8-10"),
    ("10+", "10+"),
]

GRAD_YEARS = []
for i in range(timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION):
    for j in ["Spring", "Fall"]:
        GRAD_YEARS.append(("%s %i" % (j, i), "%s %i" % (j, i)))
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
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    adult = MultiSelectField(
        "Please confirm that you are 18+", choices=AGREE, default=None, help_text="Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas A&M."
    )
    major = models.CharField("What's your major?", choices=MAJORS, max_length=50)
    gender = models.CharField("What's your gender?", choices=GENDERS, max_length=8)
    race = MultiSelectField(
        "What race(s) do you identify with?", choices=RACES, max_length=41
    )
    classification = models.CharField(
        "What classification are you?", choices=CLASSIFICATIONS, max_length=2
    )
    grad_year = models.CharField(
        "What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11
    )
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES
    )
    previous_attendant = models.BooleanField(
        f"Have you attended {settings.EVENT_NAME} before?",
        choices=TRUE_FALSE_CHOICES,
        default=False,
    )
    tamu_student = models.BooleanField(
        "Are you a Texas A&M student?", choices=TRUE_FALSE_CHOICES, default=True
    )
    extra_links = models.CharField(
        "Point us to anything you'd like us to look at while considering your application",
        max_length=200,
        blank=True,
    )
    programming_joke = models.TextField(
        "Tell us your best programming joke", max_length=500
    )
    unlimited_resource = models.TextField(
        "What is the one thing you'd build if you had unlimited resources?",
        max_length=500,
    )
    cool_prize = models.TextField(
        f"What is a cool prize you'd like to win at {settings.EVENT_NAME}?",
        max_length=500,
    )
    notes = models.TextField(
        "Anything else you would like us to know?", max_length=300, blank=True,
    )
    resume = models.FileField(
        "Upload your resume",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
    )
    additional_accommodations = models.TextField(
        "Do you require any special accommodations at the event?", max_length=500, blank=True
    )
    mlh_coc = MultiSelectField("I agree to the MLH Code of Conduct", choices=AGREE, help_text=mark_safe('<a href=https://static.mlh.io/docs/mlh-code-of-conduct.pdf target="_blank">MLH Code of Conduct</a>'), max_length=10)

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
            raise exceptions.ValidationError(
                "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email us at highschool@tamuhack.com."
            )
        if any(char.isdigit() for char in self.first_name):
            raise exceptions.ValidationError("First name can't contain any numbers")
        if any(char.isdigit() for char in self.last_name):
            raise exceptions.ValidationError("Last name can't contain any numbers")


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

    hacker.email_html_hacker(email_template, context, subject)


@receiver(signal=post_save, sender=Rsvp)
def on_rsvp_post_save(sender, instance, *args, **kwargs):
    created = kwargs["created"]
    if created:
        send_rsvp_creation_email(instance.hacker)

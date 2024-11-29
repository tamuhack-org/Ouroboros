# pylint: disable=C0330
import uuid
from typing import List, Optional, Tuple
import re

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

from application.countries import COUNTRIES_TUPLES

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
        if not (self.start and self.end):
            raise exceptions.ValidationError(
                {"start": "Start or End fields cannot be empty."}
            )
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
AGREE_DISAGREE = ((True, "Agree"), (False, "Disagree"))

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
ASIAN_INDIAN_SUB = "ASI"
ASIAN_EAST = "ASE"
ASIAN_SOUTHEAST = "ASSE"
ASIAN_OTHER = "AS"
BLACK = "BL"
HISPANIC = "HI"
NATIVE_HAWAIIAN = "NH"
WHITE = "WH"
RACE_OTHER = "O"

RACES: List[Tuple[str, str]] = [
    (AMERICAN_INDIAN, "American Indian or Alaskan Native"),
    (ASIAN_INDIAN_SUB, "Asian (Indian Subcontinent)"),
    (ASIAN_EAST, "Asian (East Asia)"),
    (ASIAN_SOUTHEAST, "Asian (Southeast Asia)"),
    (ASIAN_OTHER, "Asian (Other)"),
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
HACKATHONS_1 = "1"
HACKATHONS_2_TO_3 = "2-3"
HACKATHONS_4_TO_5 = "4-5"
HACKATHONS_6 = "6+"

HACKATHON_TIMES: List[Tuple[str, str]] = [
    (HACKATHONS_0, "This will be my first!"),
    (HACKATHONS_1, "1"),
    (HACKATHONS_2_TO_3, "2-3"),
    (HACKATHONS_4_TO_5, "4-5"),
    (HACKATHONS_6, "6+"),
]

STUDY_LESS_THAN_SECONDARY = "Less than Secondary / High School"
STUDY_SECONDARY = "Secondary / High School"
STUDY_UNDERGRAD_2YEAR = "Undergraduate University (2 year - community college or similar)"
STUDY_UNDERGRAD_3YEAR = "Undergraduate University (3+ year)"
STUDY_GRADUATE = "Graduate University (Masters, Professional, Doctoral, etc)"
STUDY_CODE_SCHOOL = "Code School / Bootcamp"
STUDY_OTHER_VOCATIONAL = "Other Vocational / Trade Program or Apprenticeship"
STUDY_POSTDOC = "Post Doctorate"
STUDY_OTHER = "Other"
STUDY_NOT_STUDENT = "I'm not currently a student"
STUDY_NO_ANSWER = "Prefer not to answer"

LEVELS_OF_STUDY = [
    (STUDY_LESS_THAN_SECONDARY, STUDY_LESS_THAN_SECONDARY),
    (STUDY_SECONDARY, STUDY_SECONDARY),
    (STUDY_UNDERGRAD_2YEAR, STUDY_UNDERGRAD_2YEAR),
    (STUDY_UNDERGRAD_3YEAR, STUDY_UNDERGRAD_3YEAR),
    (STUDY_GRADUATE, STUDY_GRADUATE),
    (STUDY_CODE_SCHOOL, STUDY_CODE_SCHOOL),
    (STUDY_OTHER_VOCATIONAL, STUDY_OTHER_VOCATIONAL),
    (STUDY_POSTDOC, STUDY_POSTDOC),
    (STUDY_OTHER, STUDY_OTHER),
    (STUDY_NOT_STUDENT, STUDY_NOT_STUDENT),
    (STUDY_NO_ANSWER, STUDY_NO_ANSWER),
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
# QUESTION2_TEXT = "What is the one thing you'd build if you had unlimited resources?"
# QUESTION3_TEXT = "What's your hidden talent?"

UNISEX_XXS = "XXS"
UNISEX_XS = "XS"
UNISEX_S = "S"
UNISEX_M = "M"
UNISEX_L = "L"
UNISEX_XL = "XL"
UNISEX_XXL = "XXL"

SHIRT_SIZES = [
    (UNISEX_XXS, "XXS"),
    (UNISEX_XS, "XS"),
    (UNISEX_S, "S"),
    (UNISEX_M, "M"),
    (UNISEX_L, "L"),
    (UNISEX_XL, "XL"),
    (UNISEX_XXL, "XXL"),
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
    (STATUS_REJECTED, "Rejected"),
    (STATUS_ADMITTED, "Admitted"),
    (STATUS_CONFIRMED, "Confirmed"),
    (STATUS_DECLINED, "Declined"),
    (STATUS_CHECKED_IN, "Checked in"),
    (STATUS_EXPIRED, "Waitlisted (Expired, internally)"),
]

HAS_TEAM = "HT"
HAS_NO_TEAM = "HNT"

HAS_TEAM_OPTIONS = [
    (HAS_TEAM, "I do have a team"),
    (HAS_NO_TEAM, "I do not have a team"),
]

CS = "Computer Science"
CE = "Computer Engineering"
COMP = "Computing"
EE = "Electrical Engineering"
MIS = "Management Information Systems"
DS = "Data Science/Engineering"
GENE = "General Engineering"
BMEN = "Biomedical Engineering"
CHEM = "Chemical Engineering"
CIVIL = "Civil Engineering"
INDU = "Industrial Engineering"
MECH = "Mechanical Engineering"
AERO = "Aerospace Engineering"
ESET = "Electronic Systems Engineering Technology (ESET)"
MATH = "Mathematics"
PHYS = "Physics"
STAT = "Statistics"
BIO = "Biology"
CHEMISTRY = "Chemistry"
MAJOR_OTHER = "Other"

MAJORS = [
    (CS, "Computer Science"),
    (CE, "Computer Engineering"),
    (COMP, "Computing"),
    (EE, "Electrical Engineering"),
    (MIS, "Management Information Systems"),
    (DS, "Data Science/Engineering"),
    (GENE, "General Engineering"),
    (BMEN, "Biomedical Engineering"),
    (CHEM, "Chemical Engineering"),
    (CIVIL, "Civil Engineering"),
    (INDU, "Industrial Engineering"),
    (MECH, "Mechanical Engineering"),
    (AERO, "Aerospace Engineering"),
    (ESET, "Electronic Systems Engineering Technology (ESET)"),
    (MATH, "Mathematics"),
    (PHYS, "Physics"),
    (STAT, "Statistics"),
    (BIO, "Biology"),
    (CHEMISTRY, "Chemistry"),    
    (MAJOR_OTHER, "Other"),
]

WANTS_TEAM_OPTIONS = [
    ("Friend", "From a friend"),
    ("Tabling", "Tabling outside Zachry"),
    ("Howdy Week", "From Howdy Week"),
    ("Yard Sign", "Yard sign"),
    ("Social Media", "Social media"),
    ("Student Orgs", "Though another student org"),
    ("TH Organizer", "From a TAMUhack organizer"),
    ("ENGR Newsletter", "From the TAMU Engineering Newsletter"),
    ("MLH", "Major League Hacking (MLH)"),
    ("Attended Before", f"I've attended {settings.EVENT_NAME} before")
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
    (PURPOSE_MESS_AROUND, "I want to have a fun weekend with my friends!"),
]

WARECHOICE = [
    ("SW", "Software"),
    ("HW", "Hardware")
]
"""HW - Hardware, SW - Software"""

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

    def get_next_meal_group(self):
        """
        Determines the next meal group considering frontloading for restricted groups
        using the RESTRICTED_FRONTLOAD_FACTOR.
        """
        RESTRICTED_FRONTLOAD_FACTOR = 1.3

        meal_groups = ['A', 'B', 'C', 'D']
        group_distribution = {group: 0 for group in meal_groups}
        restricted_distribution = {group: 0 for group in meal_groups}
        total_confirmed = Application.objects.filter(status='C').exclude(meal_group__isnull=True)
        
        for group in meal_groups:
            group_distribution[group] = total_confirmed.filter(meal_group=group).count()
            restricted_distribution[group] = total_confirmed.filter(
                meal_group=group,
                dietary_restrictions__icontains="Vegetarian"
            ).count() + total_confirmed.filter(
                meal_group=group,
                dietary_restrictions__icontains="No-Beef"
            ).count() + total_confirmed.filter(
                meal_group=group,
                dietary_restrictions__icontains="No-Pork"
            ).count() + total_confirmed.filter(
                meal_group=group,
                dietary_restrictions__icontains="Food-Allergy"
            ).count()

        total_apps = sum(group_distribution.values())
        total_restricted = sum(restricted_distribution.values())
        if total_apps == 0:  
            return meal_groups[0]

        base_restricted_percent = total_restricted / total_apps if total_apps else 0
        target_restricted_percent = {
            group: base_restricted_percent * (RESTRICTED_FRONTLOAD_FACTOR if i < len(meal_groups) // 2 else 1.0)
            for i, group in enumerate(meal_groups)
        }
        target_restricted_count = {
            group: target_restricted_percent[group] * group_distribution[group] if group_distribution[group] > 0 else 0
            for group in meal_groups
        }

        restricted_gap = {
            group: target_restricted_count[group] - restricted_distribution[group]
            for group in meal_groups
        }
        prioritized_group = max(restricted_gap, key=restricted_gap.get) 

        last_assigned_group = (
            total_confirmed.order_by('-datetime_submitted')
            .values_list('meal_group', flat=True)
            .first()
        )
        if last_assigned_group:
            next_index = (meal_groups.index(last_assigned_group) + 1) % len(meal_groups)
        else:
            next_index = 0  

        # use frontloaded group if it aligns with round-robin or is significantly better
        if prioritized_group == meal_groups[next_index]:
            return meal_groups[next_index]
        elif restricted_gap[prioritized_group] > restricted_gap[meal_groups[next_index]]:
            return prioritized_group
        else:
            return meal_groups[next_index]

    def assign_meal_group(self):
        """
        Assigns a meal group based on the current status and dietary restrictions.
        """
        if self.status == 'C':  # Confirmed
            self.meal_group = self.get_next_meal_group()
        elif self.status == 'E':  # Waitlisted
            self.meal_group = 'E'
        else:
            self.meal_group = None

    def save(self, *args, **kwargs):
        """
        Overrides save to ensure meal group assignment logic is applied.
        """
        self.assign_meal_group()
        super().save(*args, **kwargs)

    # ABOUT YOU
    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    age = models.CharField(
        max_length=5, blank=False, null=True, verbose_name="age"
    )
    phone_number = models.CharField(
        max_length=13, blank=False, null=True, verbose_name="phone number"
    )
    country = models.CharField(
        "What is your country of residence?", max_length=100, choices=COUNTRIES_TUPLES, blank=False, null=True
    )
    extra_links = models.CharField(
        "Point us to anything you'd like us to look at while considering your application",
        max_length=200,
        blank=True,
    )
    question1 = models.TextField(QUESTION1_TEXT, max_length=500)
    # question2 = models.TextField(QUESTION2_TEXT, max_length=500)
    # question3 = models.TextField(QUESTION3_TEXT, max_length=500)
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
    school_other = models.CharField(
        null=True, blank=True, max_length=255
    ) 
    tamu_email = models.EmailField(
        "TAMU Email if you are a Texas A&M student", null=True, blank=True, max_length = 75
    )
    major = models.CharField(
        "What's your major?", default=NO_ANSWER, choices= MAJORS, max_length = 100
    )
    major_other = models.CharField(
        "Other", max_length=255, null=True, blank=True
    )
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
        "What is your current level of study?", max_length=100, choices=LEVELS_OF_STUDY, blank=False, null=True
    )
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES
    )
    wares = models.CharField(
        "TAMUhack will be partnering with IEEE to offer a dedicated hardware track and prizes. Participants can choose to compete in this track or in the general software tracks. Would you like to compete in the software or hardware track", choices=WARECHOICE, max_length=8, default=NO_ANSWER, blank=True
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
    
    agree_to_photos = models.BooleanField(
        choices=AGREE, null=True, default=None
    )
    accessibility_requirements = models.BooleanField(
        choices=AGREE_DISAGREE, null=True, default=None, blank=True
    )

    # LOGISTICAL INFO
    shirt_size = models.CharField(
        "What size shirt do you wear?", choices=SHIRT_SIZES, max_length=4
    )
    # address = AddressField(on_delete=models.CASCADE, default=None, null=True)
    additional_accommodations = models.TextField(
        "Do you require any special accommodations at the event? Please list dietary restrictions here if you selected \"food allergy\" or \"other\".",
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

    dietary_restrictions = models.CharField(max_length=5000, default=None)
    meal_group = models.CharField(max_length=255, null=True, blank=True, default=None)

    technology_experience = models.CharField(max_length=5000, default=None)

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
        max_length=16,
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

        def is_valid_name(name):
            pattern = r"^(?=.{1,40}$)[a-zA-Z]+(?:[-' ][a-zA-Z]+)*$"
            
            match = re.match(pattern, name)
            
            return bool(match)


        if not self.age.isnumeric():
            raise exceptions.ValidationError("Age must be a number.")
        if not self.is_adult and int(self.age) > 18 or self.is_adult and int(self.age) < 18:
            raise exceptions.ValidationError(
                "Age and adult status do not match. Please confirm you are 18 or older."
            )
        #Fixes the obos admin panel bug, idk why the checkbox doesn't show up
        if not int(self.age) >= 18 or not self.is_adult:
            raise exceptions.ValidationError(
                "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email "
                f"us at {settings.ORGANIZER_EMAIL}. "
            )
        if not is_valid_name(self.first_name):
            raise exceptions.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        if not is_valid_name(self.last_name):
            raise exceptions.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")

# pylint: disable=C0330
import uuid
from typing import Optional, List, Tuple

from django.conf import settings
from django.core import exceptions
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from multiselectfield import MultiSelectField
import re


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

# States
OKLAHOMA = "OK"
ALASKA = "AK"
ARIZONA = "AZ"
ARKANSAS = "AR"
CALIFORNIA = "CA"
COLORADO = "CO"
CONNECTICUT = "CT"
DELAWARE = "DE"
FLORIDA = "FL"
GEORGIA = "GA"
HAWAII = "HI"
IDAHO = "ID"
ILLINOIS = "IL"
INDIANA = "IN"
IOWA = "IA"
KANSAS = "KS"
KENTUCKY = "KY"
LOUISIANA = "LA"
MAINE = "ME"
MARYLAND = "MD"
MASSACHUSETTS = "MA"
MICHIGAN = "MI"
MINNESOTA = "MN"
MISSISSIPPI = "MS"
MISSOURI = "MO"
MONTANA = "MT"
NEBRASKA = "NE"
NEVADA = "NV"
NEW_HAMPSHIRE = "NH"
NEW_JERSEY = "NJ"
NEW_MEXICO = "NM"
NEW_YORK = "NY"
NORTH_CAROLINA = "NC"
NORTH_DAKOTA = "ND"
OHIO = "OH"
OREGON = "OR"
PENNSYLVANIA = "PA"
RHODE_ISLAND = "RI"
SOUTH_CAROLINA = "SC"
SOUTH_DAKOTA = "SD"
TENNESSEE = "TN"
TEXAS = "TX"
UTAH = "UT"
VERMONT = "VT"
VIRGINIA = "VA"
WASHINGTON = "WA"
WEST_VIRGINIA = "WV"
WISCONSIN = "WI"
WYOMING = "WY"

STATES: List[Tuple[str, str]] = [
    (OKLAHOMA, "OK"),
    (ALASKA, "AK"),
    (ARIZONA, "AZ"),
    (ARKANSAS, "AR"),
    (CALIFORNIA, "CA"),
    (COLORADO, "CO"),
    (CONNECTICUT, "CT"),
    (DELAWARE, "DE"),
    (FLORIDA, "FL"),
    (GEORGIA, "GA"),
    (HAWAII, "HI"),
    (IDAHO, "ID"),
    (ILLINOIS, "IL"),
    (INDIANA, "IN"),
    (IOWA, "IA"),
    (KANSAS, "KS"),
    (KENTUCKY, "KY"),
    (LOUISIANA, "LA"),
    (MAINE, "ME"),
    (MARYLAND, "MD"),
    (MASSACHUSETTS, "MA"),
    (MICHIGAN, "MI"),
    (MINNESOTA, "MN"),
    (MISSISSIPPI, "MS"),
    (MISSOURI, "MO"),
    (MONTANA, "MT"),
    (NEBRASKA, "NE"),
    (NEVADA, "NV"),
    (NEW_HAMPSHIRE, "NH"),
    (NEW_JERSEY, "NJ"),
    (NEW_MEXICO, "NM"),
    (NEW_YORK, "NY"),
    (NORTH_CAROLINA, "NC"),
    (NORTH_DAKOTA, "ND"),
    (OHIO, "OH"),
    (OREGON, "OR"),
    (PENNSYLVANIA, "PA"),
    (RHODE_ISLAND, "RI"),
    (SOUTH_CAROLINA, "SC"),
    (SOUTH_DAKOTA, "SD"),
    (TENNESSEE, "TN"),
    (TEXAS, "TX"),
    (UTAH, "UT"),
    (VERMONT, "VT"),
    (VIRGINIA, "VA"),
    (WASHINGTON, "WA"),
    (WEST_VIRGINIA, "WV"),
    (WISCONSIN, "WI"),
    (WYOMING, "WY")
]


# Model for CheckBox
AGREE = ((True, "Agree"), (False, "Disagree"))

# Yes No Model
TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))

# Genders Model
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
    (GENDER_OTHER, "Other"),
]

# Level of Study Model
HIGH_SCHOOL = "H"
TECH_SCHOOL = "T"
UNDERGRAD_UNIVERSITY = "U"
GRAD_UNIVERSITY = "G"

LEVEL_OF_STUDY: List[Tuple[str, str]] = [
    (HIGH_SCHOOL, "High school"),
    (TECH_SCHOOL, "Tech school"),
    (UNDERGRAD_UNIVERSITY, "Undergrad university"),
    (GRAD_UNIVERSITY, "Graduate university"),
]

#Race Model
AMERICAN_INDIAN = "AI"
ASIAN = "AS"
BLACK = "BL"
HISPANIC = "HI"
NATIVE_HAWAIIAN = "NH"
WHITE = "WH"
RACE_OTHER = "O"

RACES: List[Tuple[str, str]] = [
    (AMERICAN_INDIAN, "American Indian or Alaskan Native"),
    (ASIAN, "Asian"),
    (BLACK, "Black or African-American"),
    (HISPANIC, "Hispanic or Latino"),
    (NATIVE_HAWAIIAN, "Native Hawaiian or other Pacific Islander"),
    (WHITE, "White"),
    (NO_ANSWER, "Prefer not to answer"),
    (RACE_OTHER, "Other"),
]

# Where did you hear about Hacklahoma model
SOCIAL_MEDIA = "SM"
FRIEND = "FR"
EMAIL = "EM"
FLYER = "FL"
IN_CLASS = "IC"
MLH = "ML"
ABOUT_OTHER = "O"

HEAR_ABOUT: List[Tuple[str, str]] = [
    (SOCIAL_MEDIA, "Social media"),
    (FRIEND, "Friend"),
    (EMAIL, "Email"),
    (FLYER, "Flyer"),
    (IN_CLASS, "In class"),
    (MLH, "Major League Hacking"),
    (ABOUT_OTHER, "Other"),
]

class DietaryRestriction(models.Model):
    name = models.CharField(max_length=255)

GRAD_YEAR_NA = "N"
GRAD_YEAR_1 = "2021"
GRAD_YEAR_2 = "2022"
GRAD_YEAR_3 = "2023"
GRAD_YEAR_4 = "2024"

GRAD_YEARS: List[Tuple[str, str]] = [
    (GRAD_YEAR_NA, "N/A"),
    (GRAD_YEAR_1, "2021"),
    (GRAD_YEAR_2, "2022"),
    (GRAD_YEAR_3, "2023"),
    (GRAD_YEAR_4, "2024"),
]

DRIVING = "D"
BUS = "OB"
FLYING = "F"
PUBLIC_TRANSPORTATION = "P"
MANUAL_POWER = "M"

TRANSPORT_MODES: List[Tuple[str, str]] = [
    (DRIVING, "Driving"),
    (BUS, "Bus (Greyhound, Megabus, etc.)"),
    (FLYING, "Flying"),
    (PUBLIC_TRANSPORTATION, "Public Transportation"),
    (MANUAL_POWER, "Walking/Biking"),
]

QUESTION1_TEXT = "Why is the history of computing so important?"
QUESTION2_TEXT = "What workshops/activities do you want to see at Hacklahoma?"
QUESTION3_TEXT = "What kind of prizes do you want to see at Hacklahoma?"

UNISEX_XXS = "XXS"
UNISEX_XS = "XS"
UNISEX_S = "S"
UNISEX_M = "M"
UNISEX_L = "L"
UNISEX_XL = "XL"
UNISEX_XXL = "XXL"

SHIRT_SIZES = [
    (UNISEX_XXS, "Unisex XXS"),
    (UNISEX_XS, "Unisex XS"),
    (UNISEX_S, "Unisex S"),
    (UNISEX_M, "Unisex M"),
    (UNISEX_L, "Unisex L"),
    (UNISEX_XL, "Unisex XL"),
    (UNISEX_XXL, "Unisex XXL"),
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
    (STATUS_REJECTED, "Waitlisted"),
    (STATUS_ADMITTED, "Admitted"),
    (STATUS_CONFIRMED, "Confirmed"),
    (STATUS_DECLINED, "Declined"),
    (STATUS_CHECKED_IN, "Checked in"),
    (STATUS_EXPIRED, "Expired"),
]

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

    # ABOUT YOU
    # First Name Character Field
    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name"
    )

    # Last Name Character Field
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )

    # Email Character Field
    school_email = models.CharField(
        max_length=255, 
        blank=False, 
        null=True, 
        verbose_name="email address", 
        help_text="Please enter your school address ending in .edu to be considered. Contact us at team@hacklahoma.org for any exceptions.",
        validators=[RegexValidator(regex="^([A-Za-z0-9_\.-]+\@[\da-z\.-]+\.edu)$", message="Enter a valid email address ending in .edu")]
    )

    # Phone Character Field
    phone_number = models.CharField(
        blank=False, null=True, verbose_name="phone number", max_length=15
    )

    # School Selection Box
    school = models.ForeignKey(
        School,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="What school do you go to?",
    )

    school_other = models.CharField(null=True, blank=True, max_length=255)

    # Birthday Character Field
    birthday = models.CharField(
        max_length=255, blank=False, null=True, verbose_name="birthday"
    )

    # Gender Selection Box
    gender = models.CharField(
        "What's your gender?", choices=GENDERS, max_length=2, default=NO_ANSWER
    )

    gender_other = models.CharField(
        "Other", max_length=255, null=True, blank=True
    )

    # Pronouns Model
    pronouns = models.CharField(
        max_length=255, blank=False, null=False, default= "",verbose_name="pronouns"
    )

    # Race Selection Field
    race = MultiSelectField(
        "What race(s) do you identify with?", choices=RACES, max_length=41, null=True
    )

    race_other = models.CharField(
        "Other", max_length=255, null=True, blank=True
    )

    # Level of Study Model
    level_of_study = models.CharField(
        "What is your most current level of study?", choices=LEVEL_OF_STUDY, max_length=2, default=NO_ANSWER
    )

    # Graduation Year Model
    graduation_year = models.CharField(
        "What is your anticipated graduation year?", choices=GRAD_YEARS, null=True, max_length=4
    )

    # Major Character Field
    major = models.CharField("What's your major?", max_length=255, null=True)

    # Shirt Size Selection Box
    shirt_size = models.CharField(
        "What size shirt do you wear?", choices=SHIRT_SIZES, max_length=4, null=True
    )

    # Resume File Input
    resume = models.FileField(
        "Upload your resume (PDF only)",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        upload_to=uuid_generator, 
        null=True,
        blank=True
    )

    # Social Link Character Field
    social_links = models.CharField(
        "Point us to any social links you'd like us to look at while considering your application",
        max_length=200,
        blank=True,
        help_text="Please separate links with a comma."
    )

    # Number of Hackathons Integer Field
    num_hackathons_attended = models.CharField(
        "How many hackathons have you attended?",
        null=True,
        max_length=22
    )

    # Question Text Fields
    question1 = models.TextField(QUESTION1_TEXT, max_length=500, null=True)
    question2 = models.TextField(QUESTION2_TEXT, max_length=500, null=True)
    question3 = models.TextField(QUESTION3_TEXT, max_length=500, null=True) 
    
    # Where did you hear about us selections field
    where_did_you_hear = MultiSelectField(
        "How did you hear about Hacklahoma?", null=True, choices=HEAR_ABOUT, max_length=41
    )
    where_did_you_hear_other = models.CharField(
        "Other", max_length=255, null=True, blank=True
    )

    # Shipping Address "Label"
    shipping_address = models.BooleanField(
        "Would you like to have swag and snacks shipped directly to you?",
        choices=AGREE,
        default=None,
        help_text="Note: US residents only and must submit a project"
    )

     # Mailing Adress Adress Form
    address1 = models.CharField(
        "Address line 1",
        max_length=1024,
        blank=True,
        null=True,
    )

    address2 = models.CharField(
        "Address line 2",
        max_length=1024,
        blank=True,
        null=True,
    )

    city = models.CharField(
        "City",
        max_length=1024,
        blank=True,
        null=True,
    )

    state = models.CharField(
        "State",
        max_length=2,
        choices=STATES,
        blank=True,
        null=True,
    )

    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12,
        blank=True,
        null=True,
    )

    # Interested in Hacklahoma CheckBox
    interested_in_hacklahoma = models.BooleanField(
        "Are you interested in organizing the Hacklahoma 2022 event?",
        choices=AGREE,
        default=None,
        help_text="We'll possibly reach out to you to join the executive team!"
    )

    # Interested in Hacklahoma CheckBox
    mlh_authorize = models.BooleanField("I authorize Major League Hacking to send me occasional messages about hackathons.", choices=AGREE, default=None)

    # Liability Waiver CheckBox
    liability_waiver = models.BooleanField(choices=AGREE, default=None)

    # MLH Code of Conduct CheckBox
    agree_to_coc = models.BooleanField(choices=AGREE, default=None)

    # Photo Release
    photo_release = models.BooleanField(
        "I authorize Hacklahoma to release photos with me in it.",
        choices=AGREE,
        default=None
    )

    # Over 18 CheckBox
    # is_adult = models.BooleanField(
    #     "I confirm I am 18 years or older.",
    #     choices=AGREE,
    #     default=None,
    # )

    # Addtion Notes Text Field
    notes = models.TextField(
        "Anything else you would like us to know?", max_length=300, blank=True
    )
    
    # CONFIRMATION DEADLINE
    confirmation_deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s, %s - Application" % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application:update", args=[self.id])

    # Check the formatting of the birthday
    def checkBirthday(self):
        sb = re.split('/|-', self.birthday)
        if not len(sb) == 3:
            raise exceptions.ValidationError("Birthday is formatted wrong. Must be formatted mm/dd/yyyy or mm-dd-yyyy")
        for item in sb:
            for character in item:
                if not character.isdigit():
                    raise exceptions.ValidationError("Birthday is formatted wrong. Must be formatted mm/dd/yyyy or mm-dd-yyyy")
        if not len(sb[2]) == 4:
            raise exceptions.ValidationError("Birthday is formatted wrong. Must be formatted mm/dd/yyyy or mm-dd-yyyy")    

    def clean(self):
        super().clean()
        
        self.checkBirthday()
        
        if not self.first_name.isalpha():
            raise exceptions.ValidationError("First name can only contain letters.")
        if not self.last_name.isalpha():
            raise exceptions.ValidationError("Last name can only contain letters.")
        # if not self.is_adult:
        #     raise exceptions.ValidationError(
        #         "Unfortunately, we cannot accept hackers under the age of 18. Have additional questions? Email "
        #         "us at team@hacklahoma.org. "
        #     )
        if not self.phone_number.isnumeric():
            raise exceptions.ValidationError("Please format your phone number to contain no spaces, dashes, or parenthesis.")
        if not self.num_hackathons_attended.isnumeric():
            raise exceptions.ValidationError("Please enter a number for the number of hackathons.")

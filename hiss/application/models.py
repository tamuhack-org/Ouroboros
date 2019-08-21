import datetime

from django.conf import settings
from django.core import exceptions
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from multiselectfield import MultiSelectField

AGREE = ((True, "Agree"),)

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
    ("NA", "Prefer not to disclose"),
    ("O", "Other"),
)

RACES = (
    ("American Indian", "American Indian or Alaskan Native"),
    ("Asian", "Asian"),
    ("Black", "Black or African-American"),
    ("Hispanic", "Hispanic or Latino White"),
    ("Native Hawaiian", "Native Hawaiian or other Pacific Islander"),
    ("White", "White or Caucasian"),
    ("NA", "Decline to self-identify"),
    ("Other", "Other"),
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
    ("Accounting", "Accounting"),
    ("Actuarial Science", "Actuarial Science"),
    ("Advertising", "Advertising"),
    ("Agriculture", "Agriculture"),
    (
        "Agricultural and Biological Engineering",
        "Agricultural and Biological Engineering",
    ),
    ("Agricultural Business Management", "Agricultural Business Management"),
    ("Agriculture Economics", "Agriculture Economics"),
    ("Animal Bioscience", "Animal Bioscience"),
    ("Animal Sciences", "Animal Sciences"),
    ("Anthropology", "Anthropology"),
    ("Applied Mathematics", "Applied Mathematics"),
    ("Archaeology", "Archaeology"),
    ("Architectural Engineering", "Architectural Engineering"),
    ("Architecture", "Architecture"),
    ("Art History", "Art History"),
    ("Studio Art", "Studio Art"),
    ("Art Education", "Art Education"),
    ("Biobehavioral Health", "Biobehavioral Health"),
    ("Biochemistry", "Biochemistry"),
    ("Bioengineering", "Bioengineering"),
    ("Biology", "Biology"),
    ("Biophysics", "Biophysics"),
    ("Biotechnology", "Biotechnology"),
    (
        "Business Administration and Management",
        "Business Administration and Management",
    ),
    ("Business Logistics", "Business Logistics"),
    ("Chemical Engineering", "Chemical Engineering"),
    ("Chemistry", "Chemistry"),
    ("Children", "Children"),
    ("Civil Engineering", "Civil Engineering"),
    ("Computer Engineering", "Computer Engineering"),
    ("Computer Science", "Computer Science"),
    ("Crime, Law, and Justice", "Crime, Law, and Justice"),
    ("Dance", "Dance"),
    ("Earth Sciences", "Earth Sciences"),
    ("Economics", "Economics"),
    ("Electrical Engineering", "Electrical Engineering"),
    ("Elementary and Kindergarten Education", "Elementary and Kindergarten Education"),
    ("Engineering Science", "Engineering Science"),
    ("English", "English"),
    ("Environmental Systems Engineering", "Environmental Systems Engineering"),
    ("Environmental Sciences", "Environmental Sciences"),
    ("Environmental Resource Management", "Environmental Resource Management"),
    ("Film and Video", "Film and Video"),
    ("Finance", "Finance"),
    ("Food Science", "Food Science"),
    ("Forest Science", "Forest Science"),
    ("Forest Technology", "Forest Technology"),
    ("General Science", "General Science"),
    ("Geography", "Geography"),
    ("Geosciences", "Geosciences"),
    ("General Engineering", "General Engineering"),
    ("Graphic Design and Photography", "Graphic Design and Photography"),
    ("Health and Physical Education", "Health and Physical Education"),
    ("Health Policy and Administration", "Health Policy and Administration"),
    ("History", "History"),
    ("Horticulture", "Horticulture"),
    (
        "Hotel, Restaurant, and Institutional Management",
        "Hotel, Restaurant, and Institutional Management",
    ),
    ("Human Development and Family Studies", "Human Development and Family Studies"),
    ("Individual and Family Studies", "Individual and Family Studies"),
    ("Industrial Engineering", "Industrial Engineering"),
    ("Information Sciences and Technology", "Information Sciences and Technology"),
    ("Journalism", "Journalism"),
    ("Kinesiology", "Kinesiology"),
    ("Landscape Architecture", "Landscape Architecture"),
    ("Law Enforcement and Correction", "Law Enforcement and Correction"),
    ("Marine Biology", "Marine Biology"),
    ("Marketing", "Marketing"),
    ("Mathematics", "Mathematics"),
    ("Mechanical Engineering", "Mechanical Engineering"),
    ("Media Studies", "Media Studies"),
    ("Meteorology", "Meteorology"),
    ("Microbiology", "Microbiology"),
    ("Mineral Economics", "Mineral Economics"),
    ("Modern Languages", "Modern Languages"),
    ("Music Education", "Music Education"),
    ("Nuclear Engineering", "Nuclear Engineering"),
    ("Nursing", "Nursing"),
    ("Nutrition", "Nutrition"),
    ("Philosophy", "Philosophy"),
    ("Physics", "Physics"),
    ("Physiology", "Physiology"),
    ("Political Science", "Political Science"),
    ("Pre-medicine", "Pre-medicine"),
    ("Psychology", "Psychology"),
    ("Public Relations", "Public Relations"),
    ("Real Estate", "Real Estate"),
    ("Recreation and Parks", "Recreation and Parks"),
    ("Rehabilitation Services", "Rehabilitation Services"),
    ("Religious Studies", "Religious Studies"),
    ("Secondary Education", "Secondary Education"),
    ("Sociology", "Sociology"),
    ("Social Work", "Social Work"),
    ("Special Education", "Special Education"),
    ("Speech Communication", "Speech Communication"),
    (
        "Speech Pathology and Audiology/Communication Disorder",
        "Speech Pathology and Audiology/Communication Disorder",
    ),
    ("Statistics", "Statistics"),
    ("Telecommunications", "Telecommunications"),
    ("Theater", "Theater"),
    ("Wildlife and Fishery Science", "Wildlife and Fishery Science"),
    ("Wildlife Technology", "Wildlife Technology"),
    ("Women's Studies", "Women's Studies"),
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

QUESTION1_TEXT = "Tell us your best programming joke"
QUESTION2_TEXT = "What is the one thing you'd build if you had unlimited resources?"
QUESTION3_TEXT = f"What is a cool prize you'd like to win at {settings.EVENT_NAME}?"


class Application(models.Model):
    """
    Represents a `Hacker`'s application to this hackathon.
    """

    datetime_submitted = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="first name"
    )
    last_name = models.CharField(
        max_length=255, blank=False, null=False, verbose_name="last name"
    )
    major = models.CharField("What's your major?", choices=MAJORS, max_length=255)
    gender = models.CharField("What's your gender?", choices=GENDERS, max_length=2)
    race = MultiSelectField(
        "What race(s) do you identify with?", choices=RACES, max_length=41
    )
    classification = models.CharField(
        "What classification are you?", choices=CLASSIFICATIONS, max_length=2
    )
    grad_term = models.CharField(
        "What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11
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
    question1 = models.TextField(
        QUESTION1_TEXT, max_length=500
    )
    question2 = models.TextField(
        QUESTION2_TEXT,
        max_length=500,
    )
    approved = models.NullBooleanField(blank=True)
    agree_to_coc = models.BooleanField(choices=AGREE, default=None)
    is_adult = models.BooleanField(
        "Please confirm you are 18 or older",
        choices=AGREE,
        default=None,
        help_text="Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas A&M.",
    )
    additional_accommodations = models.TextField(
        "Do you require any special accommodations at the event?",
        max_length=500,
        blank=True,
    )
    resume = models.FileField(
        "Upload your resume",
        help_text="Companies will use this resume to offer interviews for internships and full-time positions.",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )

    notes = models.TextField(
        "Anything else you would like us to know?", max_length=300, blank=True
    )

    question3 = models.TextField(
        QUESTION3_TEXT,
        max_length=500,
    )

    # wave = models.ForeignKey(Wave, on_delete=models.CASCADE)
    #
    # hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Application" % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse_lazy("application", args=[self.pk])

    def clean(self):
        super().clean()
        if not self.is_adult:
            raise exceptions.ValidationError(
                "Unfortunately, we agreecannot accept hackers under the age of 18. Have additional questions? Email us at highschool@tamuhack.com."
            )
        if any(char.isdigit() for char in self.first_name):
            raise exceptions.ValidationError("First name can't contain any numbers")
        if any(char.isdigit() for char in self.last_name):
            raise exceptions.ValidationError("Last name can't contain any numbers")


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
    num_days_to_rsvp = models.IntegerField()

    objects = WaveManager()

    def clean(self):
        super().clean()
        if self.start >= self.end:
            raise exceptions.ValidationError(
                {"start": "Start date can't be after end date."}
            )
        for wave in Wave.objects.all():
            has_start_overlap = wave.start < self.start < wave.end
            has_end_overlap = wave.start < self.end < wave.end
            if has_start_overlap or has_end_overlap:
                raise exceptions.ValidationError(
                    "Cannot create wave; another wave with an overlapping time range exists."
                )
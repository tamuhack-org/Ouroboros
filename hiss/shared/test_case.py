from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

from application import constants
from application import models as application_models
from application.countries import COUNTRIES_TUPLES
from application.models import School, Wave
from user.models import User

TEST_RESUME_DIR = "test_resume_dir"


@override_settings(MEDIA_ROOT=TEST_RESUME_DIR)
class SharedTestCase(test.TestCase):
    """A shared test case that provides utility functions for testing code easily."""

    def setUp(self) -> None:
        self.email = "email@dummy.com"
        self.password = "password"
        self.first_name = "Kennedy"
        self.last_name = "Doe"
        self.wave1 = None

        self.user = User.objects.create_user(
            email=self.email, password=self.password, is_active=True
        )

        self.email2 = "dummy@email.com"
        self.first_name2 = "Kris"
        self.last_name2 = "Doh"
        self.user2 = User.objects.create_user(
            email=self.email2, password=self.password, is_active=True
        )

        self.admin_email = "admin@official.com"
        self.admin_password = "admin_password"
        self.admin = User.objects.create_superuser(
            self.admin_email, self.admin_password, is_active=True
        )

        self.resume_file_name = "resume.pdf"
        self.resume = SimpleUploadedFile(self.resume_file_name, b"dummy")
        self.resume_file_data = {"resume": self.resume}

        self.first_school = School.objects.create(name="first school")
        self.second_school = School.objects.create(name="second school")

        self.application_fields = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "shirt_size": application_models.UNISEX_XXS,
            "major": "Computer Science",
            "school": self.first_school,
            "school_other": "",  # Defaults to empty if no other school is provided
            "gender": application_models.FEMALE,
            "gender_other": "",  # Defaults to empty if no self-description is given
            "classification": application_models.FRESHMAN,
            "grad_year": timezone.now().year + 1,
            "level_of_study": application_models.STUDY_UNDERGRAD_3YEAR,  # Assuming a 4-year undergrad program
            "num_hackathons_attended": application_models.HACKATHONS_0,
            "age": 19,
            "phone_number": "000-000-0000",
            "user": self.user,
            "race": [application_models.NO_ANSWER],
            "race_other": "",  # Defaults to empty if no self-description is given
            "has_team": application_models.HAS_TEAM,
            "wants_team": "Friend",  # Default value for how the user heard about the event
            "extra_links": "A",
            "question1": "B",
            "is_adult": True,
            "agree_to_coc": True,
            "agree_to_mlh_stuff": True,
            "agree_to_photos": True,
            "signup_to_mlh_newsletter": True,
            "accessibility_requirements": False,  # Default assumption: no special requirements
            "additional_accommodations": "E",
            "country": COUNTRIES_TUPLES[0][0],
            "tamu_email": "",  # Default empty unless provided
            "major_other": "",  # Default empty unless provided
            "meal_group": "E",  # Defaults to None unless assigned
            "wares": application_models.WARECHOICE[0][0],  # Default to "Software"
            "notes": "",  # Defaults to empty unless set
            "emergency_contact_name": "John Doe",  # Placeholder
            "emergency_contact_relationship": "Parent",  # Placeholder
            "emergency_contact_phone": "000-000-0000",  # Placeholder
            "emergency_contact_email": "johndoe@example.com",  # Placeholder
            **self.resume_file_data,
        }

    def create_active_wave(self):
        start = timezone.now() - timezone.timedelta(days=1)
        end = start + timezone.timedelta(days=30)

        self.wave1 = Wave(start=start, end=end, num_days_to_rsvp=30)
        self.wave1.save()

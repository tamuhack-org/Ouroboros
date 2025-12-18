from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

import application.constants
from application.constants import COUNTRIES_TUPLES
from application.models import School, Wave
from user.models import User

TEST_RESUME_DIR = "test_resume_dir"


@override_settings(MEDIA_ROOT=TEST_RESUME_DIR)
class SharedTestCase(test.TestCase):
    """A shared test case that provides utility functions for testing code easily."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Only create these once in memory"""
        cls.email = "email@dummy.com"
        cls.password = "password"
        cls.first_name = "Kennedy"
        cls.last_name = "Doe"

        cls.user = User.objects.create_user(
            email=cls.email, password=cls.password, is_active=True
        )

        cls.email2 = "dummy@email.com"
        cls.first_name2 = "Kris"
        cls.last_name2 = "Doh"
        cls.user2 = User.objects.create_user(
            email=cls.email2, password=cls.password, is_active=True
        )

        cls.admin_email = "admin@official.com"
        cls.admin_password = "admin_password"
        cls.admin = User.objects.create_superuser(
            cls.admin_email, cls.admin_password, is_active=True
        )

        cls.first_school = School.objects.create(name="first school")
        cls.second_school = School.objects.create(name="second school")

    def setUp(self) -> None:
        """Modifiable data"""
        self.wave1 = None

        self.resume_file_name = "resume.pdf"
        self.resume = SimpleUploadedFile(self.resume_file_name, b"dummy")
        self.resume_file_data = {"resume": self.resume}

        self.application_fields = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "shirt_size": application.constants.UNISEX_M,
            "major": "Computer Science",
            "school": self.first_school,
            "school_other": "",  # Defaults to empty if no other school is provided
            "gender": application.constants.FEMALE,
            "gender_other": "",  # Defaults to empty if no self-description is given
            "grad_year": timezone.now().year + 1,
            "level_of_study": application.constants.STUDY_UNDERGRAD_3YEAR,  # Assuming a 4-year undergrad program
            "num_hackathons_attended": application.constants.HACKATHONS_0,
            "age": 19,
            "phone_number": "000-000-0000",
            "user": self.user,
            "race": [application.constants.NO_ANSWER],
            "race_other": "",  # Defaults to empty if no self-description is given
            "extra_links": "A",
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
            "wares": application.constants.WARECHOICE[0][0],  # Default to "Software"
            "notes": "",  # Defaults to empty unless set
            "misc_short_answer": "I would be a banana because I like yellow.",  # Required field
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

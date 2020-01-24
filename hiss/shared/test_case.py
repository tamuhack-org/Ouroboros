from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

from application import models as application_models
from application.models import Wave
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

        self.application_fields = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "shirt_size": application_models.WOMENS_XXS,
            "major": "Computer Science",
            "school": "Of hard knocks",
            "transport_needed": application_models.MANUAL_POWER,
            "gender": application_models.FEMALE,
            "dietary_restrictions": application_models.NONE,
            "classification": application_models.FRESHMAN,
            "grad_year": timezone.now().year + 1,
            "num_hackathons_attended": application_models.HACKATHONS_0,
            "user": self.user,
            "race": [application_models.NO_ANSWER],
            "extra_links": "A",
            "question1": "B",
            "question2": "C",
            "question3": "D",
            "is_adult": True,
            "additional_accommodations": "E",
            "agree_to_coc": True,
            **self.resume_file_data,
        }

    def create_active_wave(self):
        start = timezone.now() - timezone.timedelta(days=1)
        end = start + timezone.timedelta(days=30)

        self.wave1 = Wave(start=start, end=end, num_days_to_rsvp=30)
        self.wave1.save()

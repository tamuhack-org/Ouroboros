from django import test
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from user.models import User
from application.models import Wave

TEST_RESUME_DIR = "test_resume_dir"


@override_settings(MEDIA_ROOT=TEST_RESUME_DIR)
class SharedTestCase(test.TestCase):
    """A shared test case that provides utility functions for testing code easily."""

    def setUp(self) -> None:
        self.email = "email@dummy.com"
        self.password = "password"
        self.first_name = "Kennedy"
        self.last_name = "Doe"

        self.user = User.objects.create_user(
            email=self.email, password=self.password, is_active=True
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
            "major": "Computer Science",
            "transport_needed": "drive",
            "gender": "M",
            "classification": "Fr",
            "grad_term": "Other",
            "num_hackathons_attended": 0,
            "tamu_student": True,
            "user": self.user,
            "race": ["NA"],
            "extra_links": "A",
            "question1": "B",
            "question2": "C",
            "question3": "D",
            "is_adult": True,
            "previous_attendant": False,
            "additional_accommodations": "E",
            "agree_to_coc": True,
            **self.resume_file_data,
        }

    def create_active_wave(self):
        start = timezone.now() - timezone.timedelta(days=1)
        end = start + timezone.timedelta(days=30)

        self.wave1 = Wave(start=start, end=end, num_days_to_rsvp=30)
        self.wave1.save()

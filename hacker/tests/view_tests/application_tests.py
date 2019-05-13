from django import test
from django.urls import reverse_lazy
from urllib.parse import urlencode

from hacker import models as hacker_models


class ApplicationViewTestCase(test.TestCase):
    def setUp(self):
        self.username = "test_username"
        self.password = "abcedfg"
        self.email_addr = "kdoe@email.com"

        self.hacker_fields = {
            "username": self.username,
            "password": self.password,
            "email": self.email_addr,
            "first_name": "Kennedy",
            "last_name": "Doe",
            "password1": self.password,
            "password2": self.password,
        }

        self.application_fields = {
            "major": "DUMMY",
            "gender": "M",
            "classification": "U3",
            "grad_year": 2020,
            "dietary_restrictions": "Vegan",
            "travel_reimbursement_required": False,
            "num_hackathons_attended": 0,
            "previous_attendant": False,
            "tamu_student": False,
            "interests": "A",
            "essay1": "A",
        }
        super().setUp()

    def test_redirects_when_not_signed_in(self):
        response = self.client.get(reverse_lazy("application"), follow=True)
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('application')}"
        )

    def test_associates_application_with_hacker(self):
        hacker = hacker_models.Hacker.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email_addr,
            first_name="Kennedy",
            last_name="Doe",
            is_active=True,
        )

        self.client.login(username=self.username, password=self.password)
        data = urlencode(self.application_fields)
        response = self.client.post(
            reverse_lazy("application"),
            data=data,
            follow=True,
            content_type="application/x-www-form-urlencoded",
        )
        self.assertIsNotNone(getattr(hacker, "application", None))

    def test_redirects_on_success_to_status(self):
        hacker = hacker_models.Hacker.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email_addr,
            first_name="Kennedy",
            last_name="Doe",
            is_active=True,
        )

        self.client.login(username=self.username, password=self.password)
        data = urlencode(self.application_fields)
        response = self.client.post(
            reverse_lazy("application"),
            data=data,
            follow=True,
            content_type="application/x-www-form-urlencoded",
        )

        self.assertRedirects(response, reverse_lazy("status"))

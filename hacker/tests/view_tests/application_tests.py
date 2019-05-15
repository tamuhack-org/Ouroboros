from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from hacker import models as hacker_models


class ApplicationViewTestCase(test.TestCase):
    def setUp(self):
        self.email = "dummy@email.com"
        self.password = "abcdefg"
        self.hacker = get_user_model().objects._create_user(
            email=self.email,
            password=self.password,
            first_name="Kennedy",
            last_name="Doe",
            is_active=True,
        )

        self.application_fields = {
            "major": "A",
            "gender": "M",
            "classification": "U1",
            "grad_year": 2020,
            "dietary_restrictions": "Vegan",
            "num_hackathons_attended": 0,
            "interests": "A",
            "essay1": "A",
            "essay2": "B",
            "essay3": "C",
            "essay4": "D",
            "notes": "E",
        }

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("application"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('application')}"
        )

    def test_associates_application_with_user(self):
        self.client.login(email=self.email, password=self.password)

        response = self.client.post(
            reverse_lazy("application"), data=self.application_fields
        )
        app = hacker_models.Application.objects.get(hacker=self.hacker)
        self.assertEqual(app.hacker, self.hacker)

    def test_user_can_edit_application_once_submitted(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(
            reverse_lazy("application"), data=self.application_fields
        )

        app_fields = self.application_fields
        new_major = "ABCDEFG"
        app_fields["major"] = new_major
        response = self.client.post(reverse_lazy("application"), data=app_fields)
        
        updated_application = hacker_models.Application.objects.get(hacker=self.hacker)
        self.assertEqual(updated_application.major, new_major)

from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from hacker import models as hacker_models


class RsvpTestCase(test.TestCase):
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
            "hacker": self.hacker,
        }

        self.rsvp_fields = {"shirt_size": "S", "notes": ""}

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("rsvp"))

        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('rsvp')}"
        )

    def test_denies_access_when_no_application(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_denies_post_request_when_no_application(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse_lazy("rsvp"), data=self.rsvp_fields)
        self.assertEqual(response.status_code, 403)

    def test_denies_access_when_application_unapproved(self):
        application = hacker_models.Application(**self.application_fields)
        application.save()

        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_denies_post_request_when_application_unapproved(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse_lazy("rsvp"), data=self.rsvp_fields)
        self.assertEqual(response.status_code, 403)

    def test_denies_access_when_application_rejected(self):
        application = hacker_models.Application(**self.application_fields)
        application.approved = False
        application.save()

        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_rsvp_can_be_updated(self):
        application = hacker_models.Application(**self.application_fields)
        application.approved = True
        application.save()

        rsvp = hacker_models.Rsvp(**self.rsvp_fields, hacker=self.hacker)
        rsvp.save()

        fields = self.rsvp_fields
        fields["shirt_size"] = "L"
        self.client.login(email=self.email, password=self.password)
        self.client.post(reverse_lazy("rsvp"), data=fields)

        rsvp = hacker_models.Rsvp.objects.get(hacker=self.hacker)
        self.assertEqual(rsvp.shirt_size, "L")

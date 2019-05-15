from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from hacker import models as hacker_models


class StatusViewTestCase(test.TestCase):
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
            "dietary_restrictions": "",
            "num_hackathons_attended": 0,
            "interests": "A",
            "essay1": "A",
            "essay2": "B",
            "essay3": "C",
            "essay4": "D",
            "notes": "E",
            "hacker": self.hacker,
        }

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("status"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('status')}"
        )

    def test_apply_context(self):
        self.client.login(email=self.email, password=self.password)

        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["NEEDS_TO_APPLY"])

    def test_pending_context(self):
        application = hacker_models.Application(**self.application_fields)
        application.full_clean()
        application.save()
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["PENDING"])

    def test_rejected_context(self):
        app_fields = self.application_fields
        app_fields["approved"] = False
        application = hacker_models.Application(**app_fields)
        application.save()

        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["REJECTED"])

    def test_needs_to_rsvp_context(self):
        app_fields = self.application_fields
        app_fields["approved"] = True
        application = hacker_models.Application(**app_fields)
        application.save()

        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["NEEDS_TO_RSVP"])

    def test_complete_context(self):
        app_fields = self.application_fields
        app_fields["approved"] = True
        application = hacker_models.Application(**app_fields)
        application.save()

        self.client.login(email=self.email, password=self.password)

        confirmation = hacker_models.Rsvp(shirt_size="S", notes="", hacker=self.hacker)
        confirmation.save()
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["COMPLETE"])

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

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("status"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('status')}"
        )

    def test_shows_apply_when_not_applied(self):
        self.client.login(email=self.email, password=self.password)

        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["NEEDS_TO_APPLY"])

    def test_shows_pending_when_applied_but_not_viewed(self):
        application = hacker_models.Application(
            major="A",
            gender="M",
            classification="U1",
            grad_year=2020,
            dietary_restrictions="",
            num_hackathons_attended=0,
            interests="A",
            essay1="A",
            essay2="B",
            essay3="C",
            essay4="D",
            notes="E",
            hacker=self.hacker,
        )
        application.full_clean()
        application.save()
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(response.context["PENDING"])
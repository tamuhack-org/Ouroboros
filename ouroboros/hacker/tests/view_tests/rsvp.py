import datetime

from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone

from hacker import models as hacker_models
from shared import test


class RsvpViewTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()

        self.rsvp_fields = { "notes": ""}

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('rsvp')}"
        )

    def test_denies_access_when_no_application(self):
        self.client.force_login(self.hacker)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_denies_access_when_unapproved_application(self):
        self.create_active_wave()
        self.application_fields["wave"] = self.wave1
        self.client.force_login(self.hacker)
        app = hacker_models.Application(**self.application_fields)
        app.save()
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_redirects_gets_when_didnt_rsvp_in_time(self):
        self.create_active_wave()
        self.application_fields["wave"] = self.wave1
        self.client.force_login(self.hacker)
        app = hacker_models.Application(**self.application_fields)
        app.save()
        app.approved = True
        app.save()

        self.hacker.rsvp_deadline = timezone.now() - datetime.timedelta(
            days=settings.DAYS_TO_RSVP * 100
        )
        self.hacker.save()

        response = self.client.get(reverse_lazy("rsvp"))
        self.assertRedirects(response, reverse_lazy("status"))

    def test_denies_access_when_didnt_rsvp_in_time(self):
        self.create_active_wave()
        self.application_fields["wave"] = self.wave1
        self.client.force_login(self.hacker)
        app = hacker_models.Application(**self.application_fields)
        app.save()
        app.approved = True
        app.save()

        self.hacker.rsvp_deadline = timezone.now() - datetime.timedelta(
            days=settings.DAYS_TO_RSVP * 100
        )
        self.hacker.save()

        response = self.client.post(reverse_lazy("rsvp"), self.rsvp_fields)
        self.assertEqual(response.status_code, 403)

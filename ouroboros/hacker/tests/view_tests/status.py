import datetime

from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone

from hacker import models as hacker_models
from shared import test


class StatusViewTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()

        self.rsvp_fields = {"notes": "", "hacker": self.hacker}

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("status"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('status')}"
        )

    def test_cant_make_it_context(self):
        self.create_active_wave()
        app = hacker_models.Application(**self.application_fields, wave=self.wave1)
        app.save()
        self.hacker.cant_make_it = True
        self.hacker.save()
        self.client.force_login(self.hacker)
        response = self.client.get(reverse_lazy("status"))
        self.assertIn("CANT_MAKE_IT", response.context)

    def test_no_wave_context(self):
        self.client.force_login(self.hacker)
        response = self.client.get(reverse_lazy("status"))
        self.assertIn("NO_MORE_WAVES", response.context)

    def test_wait_until_next_wave_context(self):
        next_wave_start = timezone.now() + datetime.timedelta(days=7)
        next_wave_end = timezone.now() + datetime.timedelta(days=10)
        next_wave = hacker_models.Wave(start=next_wave_start, end=next_wave_end)
        next_wave.save()

        self.client.force_login(self.hacker)
        response = self.client.get(reverse_lazy("status"))
        self.assertIn("WAIT_UNTIL_NEXT_WAVE", response.context)
        self.assertEqual(response.context["next_wave_start"], next_wave_start)

    def test_needs_to_apply_context(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        response = self.client.get(reverse_lazy("status"))
        self.assertIn("active_wave_end", response.context)
        self.assertIn("NEEDS_TO_APPLY", response.context)
        self.assertEqual(response.context["active_wave_end"], self.wave1.end)

    def test_pending_context(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        application = hacker_models.Application(**self.application_fields)
        application.wave = self.wave1
        application.save()

        response = self.client.get(reverse_lazy("status"))
        self.assertIn("PENDING", response.context)

    def test_rsvp_deadline_expired(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        application = hacker_models.Application(**self.application_fields)
        application.wave = self.wave1
        application.approved = True
        application.save()

        self.hacker.rsvp_deadline = timezone.now() - datetime.timedelta(
            settings.DAYS_TO_RSVP * 100
        )
        self.hacker.save()

        response = self.client.get(reverse_lazy("status"))
        self.assertIn("RSVP_DEADLINE_EXPIRED", response.context)

    def test_needs_to_rsvp_context(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        application = hacker_models.Application(**self.application_fields)
        application.wave = self.wave1
        application.save()
        application.approved = True
        application.save()

        response = self.client.get(reverse_lazy("status"))
        self.assertIn("NEEDS_TO_RSVP", response.context)
        self.assertEqual(response.context["rsvp_deadline"], self.hacker.rsvp_deadline)

    def test_complete_context(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        application = hacker_models.Application(**self.application_fields)
        application.wave = self.wave1
        application.save()
        application.approved = True
        application.save()

        rsvp = hacker_models.Rsvp(**self.rsvp_fields)
        rsvp.save()

        response = self.client.get(reverse_lazy("status"))
        self.assertIn("COMPLETE", response.context)

    def test_rejected_context(self):
        self.create_active_wave()
        self.client.force_login(self.hacker)
        application = hacker_models.Application(**self.application_fields)
        application.wave = self.wave1
        application.approved = False
        application.save()

        response = self.client.get(reverse_lazy("status"))
        self.assertIn("REJECTED", response.context)

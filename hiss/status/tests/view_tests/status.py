from datetime import timedelta

from django.urls import reverse_lazy
from django.utils import timezone

import application.constants
from application.models import Application, Wave
from shared import test_case


class StatusViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rsvp_fields = {
            "shirt_size": "XS",
            "dietary_restrictions": ["Vg", "V", "H", "FA", "K"],
            "notes": "",
        }

    def test_redirects_when_not_logged_in(self):
        response = self.client.get(reverse_lazy("status"))
        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('status')}",
        )

    def test_no_more_waves_context(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("NO_MORE_WAVES" in response.context)

    def test_wait_until_next_wave_context(self):
        wave_start = timezone.now() + timedelta(days=5)
        wave_end = wave_start + timedelta(days=5)
        Wave.objects.create(start=wave_start, end=wave_end, num_days_to_rsvp=5)
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("WAIT_UNTIL_NEXT_WAVE" in response.context)

    def test_not_applied_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("status"))
        self.assertTrue("NOT_APPLIED" in response.context)

    def test_pending_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(**self.application_fields, wave=self.wave1)

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("PENDING" in response.context)

    def test_pending_context_provides_edit_link_inside_wave(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        application = Application.objects.create(
            **self.application_fields, wave=self.wave1
        )

        response = self.client.get(reverse_lazy("status"))

        self.assertContains(response, application.get_absolute_url())

    def test_pending_context_shows_view_link_outside_wave(self):
        wave = Wave.objects.create(
            start=timezone.now() - timezone.timedelta(days=100),
            end=timezone.now() - timezone.timedelta(days=30),
            num_days_to_rsvp=100,
        )
        self.client.force_login(self.user)
        Application.objects.create(**self.application_fields, wave=wave)

        response = self.client.get(reverse_lazy("status"))

        self.assertContains(response, "View Application")

    def test_confirmation_deadline_expired_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_EXPIRED,
        )
        self.user.confirmation_deadline = timezone.now() - timedelta(days=10000)
        self.user.save()

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("EXPIRED" in response.context)

    def test_needs_to_confirm_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_ADMITTED,
        )
        self.user.confirmation_deadline = timezone.now() + timedelta(days=10000)
        self.user.save()

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("NEEDS_TO_CONFIRM" in response.context)
        self.assertTrue("confirmation_deadline" in response.context)

    def test_confirmed_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_CONFIRMED,
        )
        self.user.confirmation_deadline = timezone.now() + timedelta(days=10000)
        self.user.save()

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("CONFIRMED" in response.context)

    def test_rejected_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_REJECTED,
        )

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("REJECTED" in response.context)

    def test_rejected_rsvp_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_DECLINED,
        )

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("DECLINED" in response.context and response.context["DECLINED"])

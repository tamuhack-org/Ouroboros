from datetime import timedelta

from django.urls import reverse_lazy
from django.utils import timezone

from application.models import Application
from shared import test_case


class DeclineRsvpViewTestCase(case.SharedTestCase):
    def redirects_if_not_logged_in(self):
        response = self.client.get(reverse_lazy("rsvp:decline"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('rsvp:decline')}",
        )

    def permission_denied_if_not_applied(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        # Application.objects.create(**self.application_fields, wave=self.wave1)

        response = self.client.post(reverse_lazy("rsvp:decline"))

        self.assertEqual(response.status_code, 403)

    def permission_denied_if_not_accepted(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)

        response = self.client.post(reverse_lazy("rsvp:decline"))

        self.assertEqual(response.status_code, 403)

    def denied_if_rejected(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=False
        )

        response = self.client.post(reverse_lazy("rsvp:decline"))

        self.assertEqual(response.status_code, 403)

    def permission_denied_if_deadline_exceeded(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() - timedelta(days=100000)
        self.user.save()

        response = self.client.post(reverse_lazy("rsvp:decline"))

        self.assertEqual(response.status_code, 403)

    def redirects_if_successful(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() + timedelta(days=100000)
        self.user.save()

        response = self.client.post(reverse_lazy("rsvp:decline"))

        self.assertRedirects(response, reverse_lazy("status"))

    def assert_sets_declined_acceptance(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() + timedelta(days=100000)
        self.user.save()

        self.client.post(reverse_lazy("rsvp:decline"))
        self.user.refresh_from_db()

        self.assertTrue(self.user.declined_acceptance)

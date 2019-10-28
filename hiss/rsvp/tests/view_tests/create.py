from datetime import timedelta

from django.urls import reverse_lazy
from django.utils import timezone

from application.models import Application
from rsvp.models import Rsvp
from shared import test_case


class CreateRsvpViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rsvp_fields = {
            "shirt_size": "XS",
            "dietary_restrictions": ["Vg", "V", "H", "FA", "K"],
            "transport_type": "bus-tu",
            "notes": "",
        }

    def test_get_redirects_when_not_authenticated(self):
        response = self.client.get(reverse_lazy("rsvp:create"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('rsvp:create')}",
        )

    def test_get_fails_when_not_applied(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("rsvp:create"))

        self.assertEqual(response.status_code, 403)

    def test_get_fails_when_app_not_approved(self):
        self.create_active_wave()
        app = Application(**self.application_fields, wave=self.wave1)
        app.full_clean()
        app.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("rsvp:create"))

        self.assertEqual(response.status_code, 403)

    def test_get_fails_when_app_rejected(self):
        self.create_active_wave()
        app = Application(**self.application_fields, wave=self.wave1)
        app.approved = False
        app.full_clean()
        app.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("rsvp:create"))

        self.assertEqual(response.status_code, 403)

    def test_get_succeeds_when_app_approved(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() + timedelta(days=10000)
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("rsvp:create"))

        self.assertEqual(response.status_code, 200)

    def test_get_redirects_if_declined(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() + timedelta(days=10000)
        self.user.save()
        self.client.force_login(self.user)
        self.client.post(reverse_lazy("rsvp:decline"))

        response = self.client.get(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertRedirects(response, reverse_lazy("status"))

    def test_post_redirects_when_not_authenticated(self):
        response = self.client.post(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('rsvp:create')}",
        )

    def test_post_fails_when_not_applied(self):
        self.create_active_wave()
        self.client.force_login(self.user)

        response = self.client.post(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertEqual(response.status_code, 403)

    def test_post_fails_when_app_not_approved(self):
        self.create_active_wave()
        app = Application(**self.application_fields, wave=self.wave1)
        app.full_clean()
        app.save()
        self.client.force_login(self.user)

        response = self.client.post(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertEqual(response.status_code, 403)

    def test_post_fails_when_app_rejected(self):
        self.create_active_wave()
        app = Application(**self.application_fields, wave=self.wave1)
        app.approved = False
        app.full_clean()
        app.save()
        self.client.force_login(self.user)

        response = self.client.post(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertEqual(response.status_code, 403)

    def test_post_succeeds_when_app_approved(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        self.user.rsvp_deadline = timezone.now() + timedelta(days=10000)
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.post(reverse_lazy("rsvp:create"), self.rsvp_fields)

        self.assertTrue(Rsvp.objects.filter(user=self.user).exists())
        self.assertRedirects(response, reverse_lazy("status"))

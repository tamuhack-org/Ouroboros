from datetime import timedelta
from unittest import mock

from django.urls import reverse_lazy
from django.utils import timezone

import application.constants
from application.models import Application, Wave
from application.qr import qr_payload
from shared import test_case
from volunteer.models import ScheduleEvent


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
        self.assertContains(
            response, "Sorry, we are currently not accepting applications."
        )
        self.assertNotContains(response, "Complete Application")

    def test_wait_until_next_wave_context(self):
        wave_start = timezone.now() + timedelta(days=5)
        wave_end = wave_start + timedelta(days=5)
        Wave.objects.create(start=wave_start, end=wave_end, num_days_to_rsvp=5)
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("status"))

        self.assertTrue("WAIT_UNTIL_NEXT_WAVE" in response.context)
        self.assertContains(
            response, "Sorry, we are currently not accepting applications."
        )
        self.assertNotContains(response, "Complete Application")

    def test_between_waves_shows_applications_closed(self):
        now = timezone.now()
        Wave.objects.create(
            start=now - timedelta(days=10),
            end=now - timedelta(days=1),
            num_days_to_rsvp=5,
        )
        Wave.objects.create(
            start=now + timedelta(days=5),
            end=now + timedelta(days=10),
            num_days_to_rsvp=5,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy("status"))
        self.assertContains(
            response, "Sorry, we are currently not accepting applications."
        )
        self.assertNotContains(response, "Complete Application")

    def test_not_applied_context(self):
        self.create_active_wave()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("status"))
        self.assertTrue("NOT_APPLIED" in response.context)
        self.assertContains(response, "Complete Application")
        self.assertNotContains(response, "currently not accepting applications")

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
        self.assertContains(response, "SUBMITTED")
        self.assertNotContains(response, "currently not accepting applications")

    def test_checked_in_shows_status(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            status=application.constants.STATUS_CHECKED_IN,
        )
        response = self.client.get(reverse_lazy("status"))
        self.assertContains(response, "CHECKED IN")
        self.assertNotContains(response, "I'll be there!")

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


class DayOfDashboardTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_active_wave()
        self.client.force_login(self.user)
        self.now = timezone.now()
        self.past = ScheduleEvent.objects.create(
            name="Opening Ceremony", start=self.now - timedelta(hours=3)
        )
        self.current = ScheduleEvent.objects.create(
            name="Intro to Git",
            start=self.now - timedelta(minutes=10),
            location="MSC 2400",
        )
        self.upcoming = ScheduleEvent.objects.create(
            name="Lunch", start=self.now + timedelta(hours=1)
        )
        self.later = ScheduleEvent.objects.create(
            name="Awards", start=self.now + timedelta(hours=5)
        )
        self.hidden = ScheduleEvent.objects.create(
            name="Secret Event", start=self.now + timedelta(hours=2), is_visible=False
        )

    def create_app(self, status):
        return Application.objects.create(
            **self.application_fields, wave=self.wave1, status=status
        )

    def get_status(self):
        with mock.patch("status.views.timezone.now", return_value=self.now):
            return self.client.get(reverse_lazy("status"))

    def test_day_of_statuses_show_pass(self):
        for status in (
            application.constants.STATUS_CONFIRMED,
            application.constants.STATUS_CHECKED_IN,
            application.constants.STATUS_EXPIRED,
        ):
            with self.subTest(status=status):
                Application.objects.filter(user=self.user).delete()
                app = self.create_app(status)
                response = self.get_status()
                self.assertTrue(response.context["qr_code_b64"])
                self.assertEqual(response.context["meal_group"], app.meal_group)
                self.assertContains(response, "Your check-in QR code")
                self.assertContains(response, "Intro to Git")
                self.assertContains(response, "MSC 2400")

    def test_other_statuses_hide_pass(self):
        for status in (
            application.constants.STATUS_PENDING,
            application.constants.STATUS_REJECTED,
            application.constants.STATUS_DECLINED,
            application.constants.STATUS_ADMITTED,
        ):
            with self.subTest(status=status):
                Application.objects.filter(user=self.user).delete()
                self.create_app(status)
                response = self.get_status()
                self.assertNotIn("qr_code_b64", response.context)
                self.assertNotContains(response, "Intro to Git")

    def test_hidden_events_excluded(self):
        self.create_app(application.constants.STATUS_CONFIRMED)
        response = self.get_status()
        self.assertNotContains(response, "Secret Event")

    def test_now_and_next_highlighted(self):
        self.create_app(application.constants.STATUS_CONFIRMED)
        response = self.get_status()
        events = {
            e.name: e
            for day in response.context["schedule_days"]
            for e in day["events"]
        }
        self.assertTrue(events["Intro to Git"].is_now)
        self.assertFalse(events["Opening Ceremony"].is_now)
        self.assertTrue(events["Lunch"].is_next)
        self.assertFalse(events["Awards"].is_next)
        self.assertContains(response, "Up next")

    def test_qr_encodes_email(self):
        app = self.create_app(application.constants.STATUS_CONFIRMED)
        self.assertIn(self.user.email, qr_payload(app))

from django.contrib import admin
from django.core import mail
from django.urls import reverse_lazy
from django.utils import timezone

from application.admin import (
    create_rsvp_deadline,
    build_approval_email,
    build_rejection_email,
)
from application.models import Application
from shared import test_case


class ApplicationAdminTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()

    def test_build_approval_email_customizes_event_name(self):
        event_name = "BIGGEST HACKATHON EVER"
        with self.settings(EVENT_NAME=event_name):
            subject, _, _, _ = build_approval_email(self.app, timezone.now())
            self.assertIn(event_name, subject)

    def test_build_approval_email_customizes_user_first_name(self):
        _, message, _, _ = build_approval_email(self.app, timezone.now())

        self.assertIn(self.app.first_name, message)

    def test_build_rejection_email_customizes_event_name(self):
        event_name = "BIGGEST HACKATHON EVER"
        with self.settings(EVENT_NAME=event_name):
            subject, _, _, _ = build_rejection_email(self.app)
            self.assertIn(event_name, subject)

    def test_build_rejection_email_customizes_user_first_name(self):
        _, message, _, _ = build_rejection_email(self.app)

        self.assertIn(self.app.first_name, message)

    def test_approval_action_approves_application(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")

        self.client.post(
            change_url,
            {"action": "approve", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )

        self.app.refresh_from_db()
        self.assertTrue(self.app.approved)

    def test_approval_action_sends_approval_email(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")

        self.client.post(
            change_url, {"action": "approve", admin.ACTION_CHECKBOX_NAME: [self.app.pk]}
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_reject_action_sends_rejection_email(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")

        self.client.post(
            change_url,
            {"action": "reject", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_reject_action_rejects_application(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")
        self.client.post(
            change_url,
            {"action": "reject", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )
        self.app.refresh_from_db()
        self.assertFalse(self.app.approved)

    def test_creates_accurate_rsvp_deadline(self):
        deadline = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
        create_rsvp_deadline(self.user, deadline)
        self.assertEquals(self.user.rsvp_deadline, deadline)

    def test_export_application_emails(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")
        response = self.client.post(
            change_url,
            {
                "action": "export_application_emails",
                admin.ACTION_CHECKBOX_NAME: [self.app.pk],
            },
            follow=True,
        )
        self.assertEquals(response.status_code, 200)

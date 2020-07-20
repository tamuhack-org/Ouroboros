from django.contrib import admin
from django.core import mail
from django.urls import reverse_lazy
from django.utils import timezone

from application.admin import build_approval_email, build_rejection_email
from application.models import Application, STATUS_REJECTED, STATUS_ADMITTED
from shared import test_case


class ApplicationAdminTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()

    def test_approval_email_customizes_event_name(self):
        event_name = "BIGGEST HACKATHON EVER"
        with self.settings(EVENT_NAME=event_name):
            subject, *_ = build_approval_email(self.app, timezone.now())
            self.assertIn(event_name, subject)

    def test_approval_email_customizes_user_first_name(self):
        _, message, *_ = build_approval_email(self.app, timezone.now())

        self.assertIn(self.app.first_name, message)

    def test_rejection_email_customizes_event_name(self):
        event_name = "BIGGEST HACKATHON EVER"
        with self.settings(EVENT_NAME=event_name):
            subject, *_ = build_rejection_email(self.app)
            self.assertIn(event_name, subject)

    def test_rejection_email_customizes_first_name(self):
        _, message, *_ = build_rejection_email(self.app)

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
        self.assertEqual(self.app.status, STATUS_ADMITTED)

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
        self.assertEqual(self.app.status, STATUS_REJECTED)

    def test_export_applicant_data(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")
        response = self.client.post(
            change_url,
            {
                "action": "export_applicant_data",
                admin.ACTION_CHECKBOX_NAME: [self.app.pk],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_resend_confirmation_email(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:application_application_changelist")
        response = self.client.post(
            change_url,
            {
                "action": "resend_confirmation",
                admin.ACTION_CHECKBOX_NAME: [self.app.pk],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 1)

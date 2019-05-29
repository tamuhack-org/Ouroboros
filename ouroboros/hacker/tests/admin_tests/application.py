from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.urls import reverse_lazy

from hacker import models as hacker_models
from hacker.admin import approve
from shared import test


class ApplicationAdminTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = hacker_models.Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()

    def test_approval_action_sends_approval_email(self):
        self.client.force_login(self.hacker2)
        change_url = reverse_lazy("admin:hacker_application_changelist")
        response = self.client.post(
            change_url,
            {"action": "approve", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"Your {settings.EVENT_NAME} application has been approved!",
        )

    def test_approval_action_approves_application(self):
        self.client.force_login(self.hacker2)
        change_url = reverse_lazy("admin:hacker_application_changelist")
        response = self.client.post(
            change_url,
            {"action": "approve", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )
        self.app.refresh_from_db()
        self.assertTrue(self.app.approved)

    def test_rejection_action_sends_rejection_email(self):
        self.client.force_login(self.hacker2)
        change_url = reverse_lazy("admin:hacker_application_changelist")
        response = self.client.post(
            change_url,
            {"action": "reject", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, f"Regarding your {settings.EVENT_NAME} application"
        )

    def test_rejection_action_rejects_application(self):
        self.client.force_login(self.hacker2)
        change_url = reverse_lazy("admin:hacker_application_changelist")
        response = self.client.post(
            change_url,
            {"action": "reject", admin.ACTION_CHECKBOX_NAME: [self.app.pk]},
            follow=True,
        )
        self.app.refresh_from_db()
        self.assertFalse(self.app.approved)

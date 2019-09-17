from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.urls import reverse_lazy

from application.models import Application
from shared import test_case


class ApplicationAdminTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()

    def test_approval_action_sends_approval_email(self):
        pass

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

    def test_reject_action_sends_rejection_email(self):
        pass

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


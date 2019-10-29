from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone

from application.models import Application, STATUS_EXPIRED, STATUS_ADMITTED
from shared import test_case


class ExpireManagementCommandTestCase(test_case.SharedTestCase):
    def test_expires_apps_with_old_deadlines(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            confirmation_deadline=timezone.now() - timedelta(days=1),
            status=STATUS_ADMITTED
        )
        new_app_fields = self.application_fields
        new_app_fields["user"] = self.admin
        Application.objects.create(
            **new_app_fields,
            wave=self.wave1,
            confirmation_deadline=timezone.now() + timedelta(days=1),
            status=STATUS_ADMITTED
        )

        call_command("expire")

        self.assertEqual(Application.objects.filter(status=STATUS_EXPIRED).count(), 1)

from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone

from application.models import Application, STATUS_ADMITTED, STATUS_PENDING
from shared import test_case


class ExpireManagementCommandTestCase(test_case.SharedTestCase):
    def test_expires_apps_with_old_deadlines(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields,
            wave=self.wave1,
            confirmation_deadline=timezone.now() - timedelta(days=1),
            status=STATUS_PENDING
        )
        new_app_fields = self.application_fields
        new_app_fields["user"] = self.admin
        Application.objects.create(
            **new_app_fields,
            wave=self.wave1,
            confirmation_deadline=timezone.now() + timedelta(days=1),
            status=STATUS_PENDING
        )

        call_command("randomadmit", ".5")

        self.assertEqual(Application.objects.filter(status=STATUS_ADMITTED).count(), 1)

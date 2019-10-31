from django.core import mail
from django.http import HttpResponse
from django.urls import reverse_lazy

from application.models import (
    Application,
    STATUS_ADMITTED,
    STATUS_PENDING,
    STATUS_CONFIRMED,
)
from shared import test_case


class ConfirmApplicationViewTestCase(test_case.SharedTestCase):
    def test_requires_login(self) -> None:
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()

        response: HttpResponse = self.client.post(
            reverse_lazy("application:update", args=(application.id,))
        )

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('application:update', args=(application.id,))}",
        )

    def test_non_owners_cannot_confirm(self) -> None:
        self.create_active_wave()
        application = Application.objects.create(
            **self.application_fields, status=STATUS_ADMITTED, wave=self.wave1
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse_lazy("application:confirm", args=[application.pk])
        )
        application.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(application.status, STATUS_ADMITTED)

    def test_non_admitted_cannot_confirm(self) -> None:
        self.create_active_wave()
        application = Application.objects.create(
            **self.application_fields, status=STATUS_PENDING, wave=self.wave1
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse_lazy("application:confirm", args=[application.pk])
        )
        application.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(application.status, STATUS_PENDING)

    def test_owner_of_admitted_app_can_confirm(self) -> None:
        self.create_active_wave()
        application = Application.objects.create(
            **self.application_fields, status=STATUS_ADMITTED, wave=self.wave1
        )
        self.client.force_login(self.user)

        self.client.post(reverse_lazy("application:confirm", args=[application.pk]))
        application.refresh_from_db()

        self.assertEqual(application.status, STATUS_CONFIRMED)

    def test_successful_confirmation_redirects_to_status(self) -> None:
        self.create_active_wave()
        application = Application.objects.create(
            **self.application_fields, status=STATUS_ADMITTED, wave=self.wave1
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse_lazy("application:confirm", args=[application.pk])
        )
        application.refresh_from_db()

        self.assertRedirects(response, reverse_lazy("status"))

    def test_successful_confirmation_sends_email(self) -> None:
        self.create_active_wave()
        application = Application.objects.create(
            **self.application_fields, status=STATUS_ADMITTED, wave=self.wave1
        )
        self.client.force_login(self.user)

        self.client.post(reverse_lazy("application:confirm", args=[application.pk]))

        self.assertEqual(len(mail.outbox), 1)

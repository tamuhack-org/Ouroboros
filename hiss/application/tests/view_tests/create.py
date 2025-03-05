from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.urls import reverse_lazy

from application.models import Application
from shared.test_case import SharedTestCase


class CreateApplicationViewTestCase(SharedTestCase):
    def test_requires_login(self) -> None:
        response: HttpResponse = self.client.get(reverse_lazy("application:create"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('application:create')}",
        )

    def test_accessible_after_login(self) -> None:
        self.client.force_login(self.user)

        response: HttpResponse = self.client.get(reverse_lazy("application:create"))

        self.assertEqual(response.status_code, 200)

    def test_fails_without_active_wave(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            reverse_lazy("application:create"), self.application_fields
        )
        form = response.context["form"]

        self.assertFormError(
            form,
            None,
            "Applications may only be submitted during an active registration wave.",
        )

    def test_associates_with_user(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()

        self.application_fields["school"] = self.first_school.pk

        response: HttpResponse = self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )

        self.assertRedirects(response, reverse_lazy("status"))

    def test_fails_with_existing_app(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()
        # POST once to create a brand-new application for the user.
        self.application_fields["school"] = self.first_school.pk
        self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )
        self.application_fields["resume"] = SimpleUploadedFile("resume2.pdf", b"dummy")
        self.application_fields["school"] = self.first_school.pk

        response = self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )
        form = response.context["form"]

        self.assertFormError(
            form,
            None,
            "You can only submit one application to this event.",
        )

    def test_associates_with_active_wave(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()

        self.application_fields["school"] = self.first_school.pk
        self.client.post(
            reverse_lazy("application:create"),
            data={**self.application_fields, "dietary_restrictions": []},
        )
        self.user.refresh_from_db()

        application = Application.objects.get(user=self.user)
        self.assertEqual(application.wave, self.wave1)

    def test_sends_email(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()

        self.application_fields["school"] = self.first_school.pk

        self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )

        self.assertEqual(len(mail.outbox), 1)

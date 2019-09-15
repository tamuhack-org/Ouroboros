from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.urls import reverse_lazy

from shared import test_case


class CreateApplicationViewTestCase(test_case.SharedTestCase):
    def test_create_application_requires_login(self) -> None:
        response: HttpResponse = self.client.get(reverse_lazy("application:create"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('login')}?next={reverse_lazy('application:create')}",
        )

    def test_create_application_accessible_after_login(self) -> None:
        self.client.force_login(self.user)

        response: HttpResponse = self.client.get(reverse_lazy("application:create"))

        self.assertEqual(response.status_code, 200)

    def test_create_application_fails_without_active_wave(self) -> None:
        self.client.force_login(self.user)

        response: HttpResponse = self.client.post(
            reverse_lazy("application:create"), self.application_fields
        )

        self.assertFormError(
            response,
            "form",
            "__all__",
            "Applications may only be submitted during a registration wave.",
        )

    def test_create_application_associates_with_user(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()

        response: HttpResponse = self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )

        self.assertRedirects(response, reverse_lazy("status"))

    def test_create_application_with_existing_app_fails(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()
        # POST once to create a brand-new application for the user.
        self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )
        self.application_fields["resume"] = SimpleUploadedFile("resume2.pdf", b"dummy")

        response: HttpResponse = self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )

        self.assertFormError(
            response,
            "form",
            "__all__",
            "You can only submit one application to this event.",
        )

    def test_create_application_associates_with_active_wave(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()

        self.client.post(
            reverse_lazy("application:create"), data=self.application_fields
        )
        self.user.refresh_from_db()

        self.assertEqual(self.user.application.wave, self.wave1)

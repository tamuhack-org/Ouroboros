from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.urls import reverse_lazy

from application.models import Application
from shared import test_case


class UpdateApplicationViewTestCase(test_case.SharedTestCase):
    def test_requires_login(self) -> None:
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()

        response: HttpResponse = self.client.get(
            reverse_lazy("application:update", args=(application.id,))
        )

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('application:update', args=(application.id,))}",
        )

    def test_accessible_after_login(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()

        response: HttpResponse = self.client.get(
            reverse_lazy("application:update", args=(application.id,))
        )

        self.assertEqual(response.status_code, 200)

    def test_doesnt_change_wave(self) -> None:
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()
        self.application_fields["resume"] = SimpleUploadedFile("resume2.pdf", b"dummy")

        self.client.post(
            reverse_lazy("application:update", args=(application.id,)),
            data=self.application_fields,
        )

        application.refresh_from_db()
        self.assertEqual(application.wave, self.wave1)

    def test_actually_changes_application(self) -> None:
        self.client.force_login(self.user)
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()
        new_first_name = "Mack"
        self.application_fields["first_name"] = new_first_name
        self.application_fields["resume"] = SimpleUploadedFile("resume2.pdf", b"dummy")

        self.client.post(
            reverse_lazy("application:update", args=(application.id,)),
            data=self.application_fields,
        )

        application.refresh_from_db()
        self.assertEqual(application.first_name, new_first_name)

    def test_only_owner_can_view_application(self) -> None:
        self.client.force_login(self.admin)
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.user.application = application
        self.user.save()
        new_first_name = "Mack"
        self.application_fields["first_name"] = new_first_name
        self.application_fields["resume"] = SimpleUploadedFile("resume2.pdf", b"dummy")

        response: HttpResponse = self.client.post(
            reverse_lazy("application:update", args=(application.id,)),
            data=self.application_fields,
        )
        self.assertEqual(response.status_code, 403)
        application.refresh_from_db()
        self.assertNotEqual(application.first_name, new_first_name)

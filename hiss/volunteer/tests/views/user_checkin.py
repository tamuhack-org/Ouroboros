from django.urls import reverse_lazy
from django.utils.http import urlencode

from application.models import Application, STATUS_CHECKED_IN
from volunteer.tests.test_case import TokenAuthTestCase


class CheckinUserViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.data_dict = {"email": self.user.email}

    def test_get_fails_for_regular_user(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        regular_user_token = self.get_token(self.email, self.password)

        response = self.client.get(
            reverse_lazy("volunteer:user-checkin"),
            HTTP_AUTHORIZATION=regular_user_token,
        )

        self.assertEqual(response.status_code, 403)

    def test_get_succeeds_for_volunteer(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        volunteer_token = self.get_volunteer_token()

        response = self.client.get(
            f'{reverse_lazy("volunteer:user-checkin")}?{urlencode(self.data_dict)}',
            HTTP_AUTHORIZATION=volunteer_token,
        )

        self.assertEqual(response.status_code, 200)

    def test_get_succeeds_for_admin(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.get(
            f'{reverse_lazy("volunteer:user-checkin")}?{urlencode(self.data_dict)}',
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 200)

    def test_gets_accurate_status_when_not_checked_in(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.get(
            f'{reverse_lazy("volunteer:user-checkin")}?{urlencode(self.data_dict)}',
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertJSONEqual(response.content, {"checked_in": False})

    def test_gets_accurate_status_when_checked_in(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.get(
            f'{reverse_lazy("volunteer:user-checkin")}?{urlencode(self.data_dict)}',
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertJSONEqual(response.content, {"checked_in": True})

    def test_post_fails_for_regular_user(self):
        regular_user_token = self.get_token(self.email, self.password)
        self.create_active_wave()
        app = Application.objects.create(**self.application_fields, wave=self.wave1)

        response = self.client.post(
            reverse_lazy("volunteer:user-checkin"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=regular_user_token,
        )
        app.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(app.status, STATUS_CHECKED_IN)

    def test_post_succeeds_for_volunteer(self):
        self.create_active_wave()
        app = Application.objects.create(**self.application_fields, wave=self.wave1)
        volunteer_token = self.get_volunteer_token()

        response = self.client.post(
            reverse_lazy("volunteer:user-checkin"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=volunteer_token,
        )
        app.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.status, STATUS_CHECKED_IN)

    def test_post_succeeds_for_admin(self):
        self.create_active_wave()
        app = Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_token(self.admin_email, self.admin_password)
        response = self.client.post(
            reverse_lazy("volunteer:user-checkin"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=admin_token,
        )
        app.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.status, STATUS_CHECKED_IN)
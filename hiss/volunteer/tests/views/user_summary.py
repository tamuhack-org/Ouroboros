from django.urls import reverse_lazy
from django.utils.http import urlencode

from application.models import Application
from volunteer.tests.test_case import TokenAuthTestCase


class UserSummaryViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.data_dict = {"email": self.email}

    def test_get_fails_for_regular_user(self):
        token = self.get_token(self.email, self.password)

        response = self.client.get(
            f"{reverse_lazy('volunteer:summary')}?{urlencode(self.data_dict)}",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 403)

    def test_get_fails_for_unapplied_user(self):
        token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.get(
            f"{reverse_lazy('volunteer:summary')}?{urlencode(self.data_dict)}",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 404)

    def test_get_succeeds_for_volunteer(self):
        self.create_active_wave()
        app = Application.objects.create(**self.application_fields, wave=self.wave1)
        volunteer_token = self.get_volunteer_token()

        response = self.client.get(
            f"{reverse_lazy('volunteer:summary')}?{urlencode(self.data_dict)}",
            HTTP_AUTHORIZATION=volunteer_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "num_breakfast": 0,
                "num_lunch": 0,
                "num_dinner": 0,
                "num_midnight_snack": 0,
                "num_breakfast_2": 0,
                "num_lunch_2": 0,
                "num_workshops": 0,
                "checked_in": False,
                "restrictions": app.dietary_restrictions,
            },
        )

    def test_get_succeeds_for_admin(self):
        self.create_active_wave()
        app = Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_volunteer_token()

        response = self.client.get(
            f"{reverse_lazy('volunteer:summary')}?{urlencode(self.data_dict)}",
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "num_breakfast": 0,
                "num_lunch": 0,
                "num_dinner": 0,
                "num_midnight_snack": 0,
                "num_breakfast_2": 0,
                "num_lunch_2": 0,
                "num_workshops": 0,
                "checked_in": False,
                "restrictions": app.dietary_restrictions,
            },
        )

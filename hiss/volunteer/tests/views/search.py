import json

from django.urls import reverse

from application.models import Application
from volunteer.tests.test_case import TokenAuthTestCase


class UserSearchViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.query = "Doe"

    def create_application(self):
        self.assertIsNotNone(
            self.wave1,
            "A wave must be created before calling create_application",
        )
        Application.objects.create(**self.application_fields, wave=self.wave1)

    def test_cant_access_if_not_volunteer(self):
        self.create_active_wave()
        self.create_application()
        token = self.get_token(self.email, self.password)
        response = self.client.get(
            f"{reverse('volunteer:search')}?q={self.query}", HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 403)

    def test_can_access_if_volunteer(self):
        self.create_active_wave()
        self.create_application()
        token = self.get_volunteer_token()
        response = self.client.get(
            f"{reverse('volunteer:search')}?q={self.query}", HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 200)

    def test_gets_anticipated_results(self):
        self.create_active_wave()
        self.create_application()
        token = self.get_volunteer_token()
        response = self.client.get(
            f"{reverse('volunteer:search')}?q={self.query}", HTTP_AUTHORIZATION=token
        )
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data["results"]), 1)

    def test_is_case_insensitive(self):
        self.create_active_wave()
        self.create_application()
        token = self.get_volunteer_token()
        response = self.client.get(
            f"{reverse('volunteer:search')}?q={self.query.lower()}",
            HTTP_AUTHORIZATION=token,
        )
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data["results"]), 1)

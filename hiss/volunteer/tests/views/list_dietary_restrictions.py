import json

from django.urls import reverse_lazy

from application.models import DietaryRestriction
from volunteer.tests.test_case import TokenAuthTestCase


class ListDietaryRestrictionViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.dietary_restriction = DietaryRestriction.objects.create(name="dummy")

    def test_get_fails_for_regular_user(self):
        regular_user_token = self.get_token(self.email, self.password)

        response = self.client.get(
            reverse_lazy("volunteer:list-dietary-restrictions"),
            HTTP_AUTHORIZATION=regular_user_token,
        )
        self.assertEqual(response.status_code, 403)

    def test_succeeds_for_volunteer_user(self):
        volunteer_user_token = self.get_volunteer_token()

        response = self.client.get(
            reverse_lazy("volunteer:list-dietary-restrictions"),
            HTTP_AUTHORIZATION=volunteer_user_token,
        )

        json_response = json.loads(response.content)

        self.assertIn("dietary_restrictions", json_response)
        self.assertEqual(
            len(json_response["dietary_restrictions"]),
            DietaryRestriction.objects.count(),
        )

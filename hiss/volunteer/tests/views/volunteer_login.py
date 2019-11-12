import json

from django.urls import reverse_lazy
from rest_framework.authtoken.models import Token

from shared import test_case


class EmailObtainAuthTokenViewTestCase(test_case.SharedTestCase):
    def test_returns_user_token(self):
        expected_token = Token.objects.get(user=self.user)

        response = self.client.post(
            reverse_lazy("volunteer:login"),
            data={"email": self.email, "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertEqual(response_body["token"], str(expected_token))

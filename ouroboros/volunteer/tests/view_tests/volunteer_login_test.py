import json

from django.urls import reverse

from volunteer.models import Token

from .token_auth_test import TokenAuthTestCase


class VolunteerLoginViewTestCase(TokenAuthTestCase):
    def test_authentication_actually_gets_token(self):
        self.assertTrue(Token.objects.filter(user=self.volunteer).exists())
        self.assertTrue(self.volunteer.is_active)
        post_body = {"email": self.volunteer_email, "password": self.volunteer_password}
        response = self.client.post(reverse("volunteer-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)

    def test_authentication_requires_email(self):
        post_body = {"password": self.volunteer_password}
        response = self.client.post(reverse("volunteer-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("email", response_body)

from shared import test
from rest_framework.authtoken.models import Token
from django.shortcuts import reverse
from hacker import models as hacker_models
import json


class TokenAuthTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.volunteer_email = "volunteer@email.com"
        self.volunteer_password = "volunteering_is_good"
        self.volunteer = hacker_models.Hacker(
            email=self.volunteer_email, is_active=True
        )
        self.volunteer.set_password(self.volunteer_password)
        self.volunteer.save()

    def get_token(self):
        post_body = {"email": self.volunteer_email, "password": self.volunteer_password}
        response = self.client.post(reverse("api-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)
        return " ".join(["Token", response_body["token"]])


class ApiLoginViewTestCase(TokenAuthTestCase):
    def test_authentication_actually_gets_token(self):
        self.assertTrue(Token.objects.filter(user=self.volunteer).exists())
        self.assertTrue(self.volunteer.is_active)
        post_body = {"email": self.volunteer_email, "password": self.volunteer_password}
        response = self.client.post(reverse("api-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)

    def test_authentication_requires_email(self):
        post_body = {"password": self.volunteer_password}
        response = self.client.post(reverse("api-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("email", response_body)


class CreateFoodEventViewTestCase(TokenAuthTestCase):
    def test_creates_food_event(self):
        token = self.get_token()
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        response = self.client.post(
            reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 200)

    def test_bad_request_when_missing_field(self):
        token = self.get_token()
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        for key, val in post_body.items():
            del post_body[key]
            response = self.client.post(
                reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=token
            )
            self.assertEqual(response.status_code, 400)
            post_body[key] = val

    def test_bad_request_when_hacker_doesnt_exist(self):
        token = self.get_token()
        post_body = {
            "email": "totally_unknown_email@flibbertigibbet.com"
        }
        response = self.client.post(reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, 400)

    def test_denies_access_when_no_auth(self):
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        response = self.client.post(reverse("create-food-event"), post_body)
        self.assertEqual(response.status_code, 401)


class CreateWorkshopEventViewTestCase(TokenAuthTestCase):
    def test_creates_workshop_event(self):
        token = self.get_token()
        post_body = {"email": self.hacker.email}
        response = self.client.post(
            reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 200)

    def test_bad_request_when_missing_field(self):
        token = self.get_token()
        post_body = {"email": self.hacker.email}
        for key, val in post_body.items():
            del post_body[key]
            response = self.client.post(
                reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
            )
            self.assertEqual(response.status_code, 400)
            post_body[key] = val

    def test_bad_request_when_hacker_doesnt_exist(self):
        token = self.get_token()
        post_body = {"email": "totally_unknown_email@flibbertigibbet.com"}
        response = self.client.post(
            reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 400)

    def test_denies_access_when_no_auth(self):
        post_body = {"email": self.hacker.email}
        response = self.client.post(reverse("create-workshop-event"), post_body)
        self.assertEqual(response.status_code, 401)

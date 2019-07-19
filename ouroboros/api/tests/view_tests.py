import datetime
import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import reverse
from django.utils import timezone

from rest_framework.authtoken.models import Token

from hacker import models as hacker_models
from shared import test


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

        self.volunteer_group = Group(name=settings.VOLUNTEER_GROUP_NAME)
        self.volunteer_group.save()
        self.volunteer.groups.add(self.volunteer_group)

    def get_token(self, email, password):
        post_body = {"email": email, "password": password}
        response = self.client.post(reverse("api-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)
        return " ".join(["Token", response_body["token"]])

    def get_volunteer_token(self):
        return self.get_token(self.volunteer_email, self.volunteer_password)

    def check_in(self, hacker: hacker_models.Hacker):
        hacker.checked_in = True
        hacker.checked_in_datetime = timezone.now()
        hacker.save()


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
    def test_cant_access_unless_volunteer(self):
        hacker_token = self.get_token(self.email, self.password)
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        response = self.client.post(
            reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=hacker_token
        )
        self.assertEqual(response.status_code, 403)

    def test_can_access_if_volunteer(self):
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        volunteer_token = self.get_volunteer_token()
        self.check_in(self.hacker)
        response = self.client.post(
            reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=volunteer_token
        )
        self.assertEqual(response.status_code, 200)

    def test_creates_food_event(self):
        self.check_in(self.hacker)
        token = self.get_volunteer_token()
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
        token = self.get_volunteer_token()
        self.check_in(self.hacker)
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

    def test_not_found_when_hacker_doesnt_exist(self):
        token = self.get_volunteer_token()
        post_body = {
            "email": "totally_unknown_email@flibbertigibbet.com",
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        response = self.client.post(
            reverse("create-food-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 404)

    def test_denies_access_when_no_auth(self):
        post_body = {
            "email": self.hacker.email,
            "meal": "Breakfast",
            "restrictions": "Vegan",
        }
        response = self.client.post(reverse("create-food-event"), post_body)
        self.assertEqual(response.status_code, 401)


class CreateWorkshopEventViewTestCase(TokenAuthTestCase):
    def test_cant_access_unless_volunteer(self):
        hacker_token = self.get_token(self.email, self.password)
        post_body = {"email": self.hacker.email}
        response = self.client.post(
            reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=hacker_token
        )
        self.assertEqual(response.status_code, 403)

    def can_access_if_volunteer(self):
        post_body = {"email": self.hacker.email}
        self.check_in(self.hacker)
        volunteer_token = self.get_volunteer_token()
        response = self.client.post(
            reverse("create-workshop-event"),
            post_body,
            HTTP_AUTHORIZATION=volunteer_token,
        )
        self.assertEqual(response.status_code, 200)

    def test_creates_workshop_event(self):
        token = self.get_volunteer_token()
        self.check_in(self.hacker)
        post_body = {"email": self.hacker.email}
        response = self.client.post(
            reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 200)

    def test_bad_request_when_missing_field(self):
        token = self.get_volunteer_token()
        post_body = {"email": self.hacker.email}
        for key, val in post_body.items():
            del post_body[key]
            response = self.client.post(
                reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
            )
            self.assertEqual(response.status_code, 400)
            post_body[key] = val

    def test_not_found_when_hacker_doesnt_exist(self):
        token = self.get_volunteer_token()
        post_body = {"email": "totally_unknown_email@flibbertigibbet.com"}
        response = self.client.post(
            reverse("create-workshop-event"), post_body, HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 404)

    def test_denies_access_when_no_auth(self):
        post_body = {"email": self.hacker.email}
        response = self.client.post(reverse("create-workshop-event"), post_body)
        self.assertEqual(response.status_code, 401)


class CheckinHackerViewTestCase(TokenAuthTestCase):
    def test_cant_access_unless_volunteer(self):
        hacker_token = self.get_token(self.email, self.password)
        post_body = {"email": self.hacker.email}
        response = self.client.post(
            reverse("checkin-hacker"), post_body, HTTP_AUTHORIZATION=hacker_token
        )
        self.assertEqual(response.status_code, 403)

        volunteer_token = self.get_volunteer_token()
        response = self.client.post(
            reverse("checkin-hacker"), post_body, HTTP_AUTHORIZATION=volunteer_token
        )
        self.assertEqual(response.status_code, 200)

    def test_checks_in_hacker(self):
        volunteer_token = self.get_volunteer_token()
        post_body = {"email": self.hacker.email}
        response = self.client.post(
            reverse("checkin-hacker"), post_body, HTTP_AUTHORIZATION=volunteer_token
        )
        self.assertEqual(response.status_code, 200)

        self.hacker.refresh_from_db()
        self.assertTrue(self.hacker.checked_in)

    def test_retrieves_unchecked_hacker_status(self):
        volunteer_token = self.get_volunteer_token()
        response = self.client.get(
            f"{reverse('checkin-hacker')}?email={self.hacker.email}",
            HTTP_AUTHORIZATION=volunteer_token,
        )
        content = json.loads(response.content)
        self.assertFalse(content["checked_in"])

    def test_retrieves_checked_hacker_status(self):
        volunteer_token = self.get_volunteer_token()
        self.check_in(self.hacker)
        response = self.client.get(
            f"{reverse('checkin-hacker')}?email={self.hacker.email}",
            HTTP_AUTHORIZATION=volunteer_token,
        )
        content = json.loads(response.content)
        self.assertTrue(content["checked_in"])
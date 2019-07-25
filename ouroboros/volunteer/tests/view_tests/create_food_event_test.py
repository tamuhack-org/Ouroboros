from .token_auth_test import TokenAuthTestCase
from django.urls import reverse


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

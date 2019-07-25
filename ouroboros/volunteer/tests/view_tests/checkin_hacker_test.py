import json

from django.urls import reverse

from .token_auth_test import TokenAuthTestCase


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

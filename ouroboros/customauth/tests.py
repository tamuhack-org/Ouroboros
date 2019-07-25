import re

from django.core import mail
from django.urls import reverse_lazy

from hacker import models as hacker_models
from shared import test

URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"


class EmailVerificationTestCase(test.SharedTestCase):
    def setUp(self):
        self.email = "hacker@email.com"
        self.first_name = "Kennedy"
        self.last_name = "Doe"
        self.password = "dummypassword"
        self.fields = {
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        }

    def test_signup_creates_hacker(self):
        response = self.client.post(reverse_lazy("signup"), self.fields)
        hacker = hacker_models.Hacker.objects.get(email=self.email)
        self.assertEqual(hacker.email, self.email)

    def test_signup_creates_inactive_hacker(self):
        response = self.client.post(reverse_lazy("signup"), self.fields)
        hacker = hacker_models.Hacker.objects.get(email=self.email)
        self.assertFalse(hacker.is_active)

    def test_signup_sends_email(self):
        response = self.client.post(reverse_lazy("signup"), self.fields)
        self.assertEqual(len(mail.outbox), 1)

    def test_signup_sends_valid_confirmation_link(self):
        response = self.client.post(reverse_lazy("signup"), self.fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]

        response = self.client.get(url)
        hacker = hacker_models.Hacker.objects.get(email=self.email)
        self.assertTrue(hacker.is_active)

from django.test import TestCase
from hacker import models as hacker_models
from django.urls import reverse_lazy
import re
from django.core import mail

URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"

# Create your tests here.
class SignupTestCase(TestCase):
    def setUp(self):
        self.username = "test_username"
        self.email_addr = "test_username@email.com"
        self.hacker_fields = {
            "username": self.username,
            "email": self.email_addr,
            "first_name": "Dummy",
            "last_name": "Dimmy",
            "password1": "asdfasdfasdfasdfasdf",
            "password2": "asdfasdfasdfasdfasdf",
        }
        return super().setUp()

    def test_signup_renders_correct_template(self):
        response = self.client.get(reverse_lazy("signup"))
        self.assertIn("registration/signup.html", response.template_name)

    def test_signup_creates_inactive_user(self):
        response = self.client.post(reverse_lazy("signup"), data=self.hacker_fields)
        hacker = hacker_models.Hacker.objects.get(email=self.email_addr)
        self.assertFalse(hacker.is_active)

    def test_signup_sends_email(self):
        response = self.client.post(reverse_lazy("signup"), data=self.hacker_fields)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Confirm your email address!")

    def test_confirmation_link_is_valid(self):
        response = self.client.post(reverse_lazy("signup"), data=self.hacker_fields)
        hacker = hacker_models.Hacker.objects.get(username=self.username)
        self.assertFalse(hacker.is_active)
        body = mail.outbox[0].body
        url, _, _ = re.findall(URL_REGEX, body)[0]

        response = self.client.get(url)
        hacker = hacker_models.Hacker.objects.get(username=self.username)
        self.assertTrue(hacker.is_active)
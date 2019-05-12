from django.test import TestCase
from hacker import models as hacker_models
from django.urls import reverse_lazy
from django.core import mail

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

    # TODO: Extract confirmation link before sending email, and follow it to ensure that it works
    # Success determined by if, when link followed, hacker.is_active is True
    # def test_confirmation_link_is_valid(self):
    #     pass


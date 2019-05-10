from django.test import TestCase
from hacker import models as hacker_models
from django.urls import reverse_lazy

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
        hacker = hacker_models.Hacker.objects.get(email=self.email)
        self.assertFalse(hacker.is_active)
        self.assertTrue()

    def test_signup_sends_email(self):
        # TODO Offline; can't figure out how to ensure email is sent
        pass

    def test_signup_sends_valid_link(self):
        # TODO Offline; can't figure out how to get email content
        pass

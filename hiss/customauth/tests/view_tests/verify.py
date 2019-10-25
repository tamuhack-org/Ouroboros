import re

from django.core import mail
from django.urls import reverse_lazy

from shared import test_case
from user.models import User

URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"


class EmailVerificationTestCase(test_case.SharedTestCase):
    def setUp(self):
        self.email = "hacker@tamu.edu"
        self.first_name = "Kennedy"
        self.last_name = "Doe"
        self.password = "dummypassword"
        self.fields = {
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        }

    def test_signup_creates_user(self):
        self.client.post(reverse_lazy("customauth:signup"), self.fields)
        user = User.objects.get(email=self.email)
        self.assertEqual(user.email, self.email)

    def test_signup_creates_inactive_user(self):
        self.client.post(reverse_lazy("customauth:signup"), self.fields)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)

    def test_signup_sends_email(self):
        self.client.post(reverse_lazy("customauth:signup"), self.fields)

        self.assertEqual(len(mail.outbox), 1)

    def test_signup_sends_valid_confirmation_link(self):
        self.client.post(reverse_lazy("customauth:signup"), self.fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]

        self.client.get(url)

        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)

    def test_signout_removes_user(self):
        """
        Verify if user is removed during logout.
        """
        request = self.client.post(reverse_lazy("customauth:signup"), self.fields)
        user = User.objects.get(email=self.email)
        request.user = user

        request = self.client.get(reverse_lazy("customauth:logout"))
        self.assertTrue(not hasattr(request, "user"))

import re

from django.core import mail
from django.urls import reverse_lazy

from shared import test_case
from user.models import User

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from customauth.tokens import email_confirmation_generator

URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"


class EmailVerificationTestCase(test_case.SharedTestCase):
    def is_valid_link(self, user: User, url: str)-> bool:
        """
        Generates a UID and Token and verifies if the passed URL matches it. 
        """
        valid_uid =  urlsafe_base64_encode(force_bytes(user.pk))
        valid_token =  email_confirmation_generator.make_token(user)

        url_split = url.split('/')

        return url_split[-2] == valid_token and url_split[-3] == valid_uid

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
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]

        user = User.objects.get(email=self.email)
        self.assertTrue(self.is_valid_link(user, url))


    def test_signup_sends_valid_confirmation_link(self):
        self.client.post(reverse_lazy("customauth:signup"), self.fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]


        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)
        self.assertTrue(self.is_valid_link(user, url))

import re

from django.core import mail
from django.urls import reverse_lazy

from shared import test_case
from user.models import User

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from customauth.tokens import email_confirmation_generator


URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"


class ResendActivationEmailView(test_case.SharedTestCase):
    def is_valid_link(self, user: User, url: str) -> bool:
        """
        Generates a UID and Token and verifies if the passed URL matches it.
        """
        valid_uid = urlsafe_base64_encode(force_bytes(user.pk))
        valid_token = email_confirmation_generator.make_token(user)

        url_split = url.split("/")

        return url_split[-2] == valid_token and url_split[-3] == valid_uid

    def setUp(self):
        self.email = "hacker@tamu.edu"
        self.password = "dummypassword"
        self.inactive_user = User.objects._create_user(
            email=self.email, password=self.password
        )

    def test_submitting_valid_form_sends_email(self):
        fields = {"email": self.email}
        self.client.post(reverse_lazy("customauth:resend_activation"), fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]
        user = User.objects.get(email=self.email)

        self.assertTrue(self.is_valid_link(user, url))

    def test_clicking_sent_email_link_is_valid(self):
        fields = {"email": self.email}
        self.client.post(reverse_lazy("customauth:resend_activation"), fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]
        user = User.objects.get(email=self.email)

        self.assertTrue(user.is_active)
        self.assertTrue(self.is_valid_link(user, url))

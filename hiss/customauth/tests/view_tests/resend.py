import re

from django.core import mail
from django.urls import reverse_lazy

from shared import test_case
from user.models import User


URL_REGEX = r"(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"


class ResendActivationEmailView(test_case.SharedTestCase):
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

    def test_clicking_sent_email_link_is_valid(self):
        fields = {"email": self.email}
        self.client.post(reverse_lazy("customauth:resend_activation"), fields)
        self.assertEqual(len(mail.outbox), 1)
        body, _ = mail.outbox[0].alternatives[0]
        url, _, _ = re.findall(URL_REGEX, body)[0]

        self.client.get(url)

        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)

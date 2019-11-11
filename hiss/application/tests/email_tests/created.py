from email.message import EmailMessage

from django.conf import settings
from django.core import mail

from application.emails import send_creation_email
from application.models import Application
from shared import test_case


class ApplicationCreatedEmailTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = Application.objects.create(
            **self.application_fields, wave=self.wave1
        )

    def test_send_creation_email_sends_email(self):
        send_creation_email(self.app)

        self.assertEqual(len(mail.outbox), 1)

    def test_send_creation_email_customizes_body(self):
        send_creation_email(self.app)

        email: EmailMessage = mail.outbox[0]

        self.assertIn(self.app.first_name, email.body)
        self.assertIn(settings.EVENT_NAME, email.body)

from django.core import mail
from django.core.mail import EmailMultiAlternatives

from application.emails import send_confirmation_email
from application.models import Application
from shared import test_case


class ApplicationConfirmationEmailTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = Application.objects.create(
            **self.application_fields, wave=self.wave1
        )

    def test_send_confirmation_email_sends_email(self):
        send_confirmation_email(self.app)

        self.assertEqual(len(mail.outbox), 1)

    def test_send_confirmation_email_attaches_file(self):
        send_confirmation_email(self.app)

        # Check that the email has the QR and ics attachments
        email: EmailMultiAlternatives = mail.outbox[0]
        self.assertEqual(len(email.attachments), 2)

    """
    Hard-coded email body should be modified to include application name and settings.EVENT_NAME, instead of hard-coded references to TAMUhack.
    """
    # def test_send_confirmation_email_customizes_body(self):
    #     send_confirmation_email(self.app)

    #     email: EmailMultiAlternatives = mail.outbox[0]

    #     self.assertIn(self.app.first_name, email.body)
    #     self.assertIn(settings.EVENT_NAME, email.body)

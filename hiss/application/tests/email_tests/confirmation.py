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

        email: EmailMultiAlternatives = mail.outbox[0]
        self.assertEqual(len(email.attachments), 1)

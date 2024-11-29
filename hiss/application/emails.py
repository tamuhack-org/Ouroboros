import json
from io import BytesIO

import pyqrcode
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html

from application.models import Application
from application.apple_wallet import get_apple_wallet_pass_url

import threading
from django.core.mail import EmailMessage

#create separate threading class for confirmation email since it has a QR code

class EmailQRThread(threading.Thread):
    def __init__(self, subject, msg, html_msg, recipient_email, qr_stream):
        self.subject = subject
        self.msg = msg
        self.html_msg = html_msg
        self.recipient_email = recipient_email
        self.qr_stream = qr_stream
        threading.Thread.__init__(self)

    def run(self):
        qr_code = pyqrcode.create(self.qr_content)
        qr_stream = BytesIO()
        qr_code.png(qr_stream, scale=5)

        email = mail.EmailMultiAlternatives(
            self.subject, self.msg, from_email=None, to=[self.recipient_email]
        )
        email.attach_alternative(self.html_msg, "text/html")
        email.attach("code.png", self.qr_stream.getvalue(), "text/png")

        # if above code is defined directly in function, it will run synchronously
        # therefore need to directly define in threading class to run asynchronously

        email.send()

def send_creation_email(app: Application) -> None:
    """
    Sends an email to the user informing them of their newly-created app.
    :param app: The user's newly-created application
    :return: None
    """
    subject = f"We've received your application for {settings.EVENT_NAME}!"
    template_name = "application/emails/created.html"
    context = {
        "first_name": app.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
    }

    # send_html_email is threaded from the User class
    # see user/models.py

    app.user.send_html_email(template_name, context, subject)
    

def send_confirmation_email(app: Application) -> None:
    """
    Sends a confirmation email to a user, which contains their QR code as well as additional event information.
    :param app: The user's application
    :type app: Application
    :return: None
    """
    subject = f"TAMUhack: Important Day-Of Information"
    email_template = "application/emails/confirmed.html"
    context = {
        "first_name": app.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "apple_wallet_url": get_apple_wallet_pass_url(app.user.email),
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_msg = render_to_string(email_template, context)
    plain_msg = html.strip_tags(html_msg)

    qr_content = json.dumps(
        {
            "first_name": app.first_name,
            "last_name": app.last_name,
            "email": app.user.email,
            "university": app.school.name,
        }
    )

    email_thread = EmailQRThread(subject, plain_msg, html_msg, app.user.email, qr_content)
    email_thread.start()

import json
from io import BytesIO

import pyqrcode
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html

from application.models import Application


def send_confirmation_email(app: Application) -> None:
    """
    Sends a confirmation email to a user, which contains their QR code as well as additional event information.
    :param app: The user's application
    :type app: Application
    :return: None
    """
    subject = f"{settings.EVENT_NAME} Confirmation!"
    email_template = "application/emails/confirmed.html"
    context = {"first_name": app.first_name, "event_name": settings.EVENT_NAME}
    html_msg = render_to_string(email_template, context)
    msg = html.strip_tags(html_msg)
    email = mail.EmailMultiAlternatives(
        subject, msg, from_email=None, to=[app.user.email]
    )
    email.attach_alternative(html_msg, "text/html")

    qr_content = json.dumps(
        {
            "first_name": app.first_name,
            "last_name": app.last_name,
            "email": app.user.email,
            "university": app.school,
        }
    )
    qr_code = pyqrcode.create(qr_content)
    qr_stream = BytesIO()
    qr_code.png(qr_stream, scale=5)
    email.attach("code.png", qr_stream.getvalue(), "text/png")
    email.send()

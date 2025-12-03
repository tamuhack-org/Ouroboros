import json
import os
from io import BytesIO
from pathlib import Path

import pyqrcode
import requests
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html

from application.models import Application


def send_creation_email(app: Application) -> None:
    """Send an email to the user informing them of their newly-created apppplication.

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

    app.user.send_html_email(template_name, context, subject)


def send_confirmation_email(app: Application) -> None:
    """Send a confirmation email to a user, which contains their QR code as well as additional event information.

    :param app: The user's application
    :type app: Application
    :return: None
    """
    subject = f"{settings.EVENT_NAME}: Important Day-of Information!"
    email_template = "application/emails/confirmed.html"

    if app.status == "E":
        subject = f"{settings.EVENT_NAME} Waitlist: Important Day-of Information!"
        email_template = "application/emails/confirmed-waitlist.html"

    # Generate apple wallet
    apple_wallet_pass_url = ""
    try:
        r = requests.post(
            os.environ.get("APPLE_WALLET_GEN_URL"),
            json={"email": app.user.email, "meal_group": app.meal_group},
            headers={"X-API-Key": os.environ.get("APPLE_WALLET_SECRET_KEY")},
            timeout=10,
        )
        apple_wallet_pass_url = r.json().get("s3_path")
        print(r.json())
    except requests.exceptions.RequestException as e:
        print(f"Error generating apple wallet pass: {e}")

    context = {
        "first_name": app.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "apple_wallet_url": apple_wallet_pass_url,
        "meal_group": app.meal_group,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    print("context:", context)
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
            "university": app.school.name,
        }
    )
    qr_code = pyqrcode.create(qr_content)
    qr_stream = BytesIO()
    qr_code.png(qr_stream, scale=5)
    email.attach("code.png", qr_stream.getvalue(), "text/png")
    ics_path = Path(settings.BASE_DIR) / ".." / "static" / "th26invite.ics"
    email.attach_file(str(ics_path), mimetype="text/calendar")
    print(f"sending confirmation email to {app.user.email}")
    email.send()

from celery import shared_task
import json
from io import BytesIO
import pyqrcode
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html
from application.models import Application
from application.apple_wallet import get_apple_wallet_pass_url
from django.conf import settings
#create separate threading class for confirmation email since it has a QR code

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

    app.user.send_html_email.delay(template_name, context, subject)
    
@shared_task
def send_confirmation_email(app_id: int) -> None:
    """
    Sends a confirmation email to a user, which contains their QR code as well as additional event information.
    :param app_id: The ID of the user's application
    :type app_id: int
    :return: None
    """
    try:
        app = Application.objects.get(id=app_id)

        subject = f"HowdyHack: Important Day-of Information!"
        email_template = "application/emails/confirmed.html"

        if app.status == "E":
            subject = f"HowdyHack Waitlist: Important Day-of Information!"
            email_template = "application/emails/confirmed-waitlist.html"

        context = {
            "first_name": app.first_name,
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "apple_wallet_url": get_apple_wallet_pass_url(app.user.email),
            "meal_group": app.meal_group,
        }
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
        print(f"sending confirmation email to {app.user.email}")
        email.send()
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
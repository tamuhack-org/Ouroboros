import structlog
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from application.admin import build_waitlist_expired_email
from application.constants import STATUS_ADMITTED, STATUS_EXPIRED
from application.models import Application
from shared.admin_functions import send_mass_html_mail

logger = structlog.get_logger()


class Command(BaseCommand):
    def handle(self, *_args, **_options):
        now = timezone.now()

        unconfirmed = Application.objects.filter(
            status=STATUS_ADMITTED,
            confirmation_deadline__lt=now,
        )

        count = unconfirmed.count()
        logger.info("Going to expire applications", count=count)

        email_tuples = []

        with transaction.atomic():
            for app in unconfirmed:
                app.status = STATUS_EXPIRED
                app.save()
                email_tuples.append(build_waitlist_expired_email(app))

        if email_tuples:
            send_mass_html_mail(email_tuples)

        logger.info("All applications successfully expired and notified", count=count)

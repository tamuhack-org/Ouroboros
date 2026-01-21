import structlog
from django.conf import settings
from django.tasks import task
from django.template import Context, Template, TemplateSyntaxError
from django.utils.html import strip_tags

from application.constants import STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_PENDING
from application.emails import (
    send_confirmation_email,
    send_hardware_confirmation_email,
    send_reminder_email,
    send_still_reviewing_email,
)
from application.models import AdHocEmailBatch, Application

logger = structlog.get_logger()

# Note! You must make sure the arguments into the task are JSON serializable!
# https://docs.djangoproject.com/en/6.0/ref/tasks/#django.tasks.Task.enqueue


@task()
def bg_dispatch_send_update_emails(application_ids: list[str]):
    for app_id in application_ids:
        bg_send_update_email.enqueue(app_id)


@task()
def bg_send_update_email(application_id: str):
    try:
        application = Application.objects.get(pk=application_id)
        logger.info("Sending update email", application_id=application_id, status=application.status)
        if application.status == STATUS_PENDING:
            send_still_reviewing_email(application)
        elif application.status == STATUS_ADMITTED:
            send_reminder_email(application)
        elif application.status == STATUS_CONFIRMED and application.wares == "HW":
            send_hardware_confirmation_email(application)
        else:
            send_confirmation_email(application)

    except Application.DoesNotExist:
        pass


@task()
def bg_dispatch_ad_hoc_emails(batch_id: str, application_ids: list[str]):
    """Dispatch individual ad hoc email tasks."""
    for app_id in application_ids:
        bg_send_ad_hoc_email.enqueue(batch_id, app_id)


@task()
def bg_send_ad_hoc_email(batch_id: str, application_id: str):
    """Send a single ad hoc email."""
    try:
        batch = AdHocEmailBatch.objects.get(pk=batch_id)
        application = Application.objects.get(pk=application_id)

        context = {
            "first_name": application.first_name,
            "last_name": application.last_name,
            "email": application.user.email,
            "event_name": settings.EVENT_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_name": settings.ORGANIZER_NAME,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
        }

        template = Template(batch.html_template)
        html_message = template.render(Context(context))
        text_message = strip_tags(html_message)

        application.user.email_user(
            batch.subject, text_message, None, html_message=html_message
        )
        logger.info(
            "Sent ad hoc email",
            application_id=application_id,
            batch_id=batch_id,
        )
    except AdHocEmailBatch.DoesNotExist:
        logger.exception("Ad hoc email batch not found", batch_id=batch_id)
    except Application.DoesNotExist:
        logger.exception("Application not found", application_id=application_id)
    except TemplateSyntaxError as e:
        logger.exception(
            "Template syntax error in ad hoc email",
            batch_id=batch_id,
            error=str(e),
        )

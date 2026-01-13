import structlog
from django.tasks import task

from application.constants import STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_PENDING
from application.emails import (
    send_confirmation_email,
    send_hardware_confirmation_email,
    send_reminder_email,
    send_still_reviewing_email,
)
from application.models import Application

logger = structlog.get_logger()

# Note! You must make sure the arguments into the task are JSON serializable!
# https://docs.djangoproject.com/en/6.0/ref/tasks/#django.tasks.Task.enqueue


@task
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

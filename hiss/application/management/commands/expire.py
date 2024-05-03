from django.core.management.base import BaseCommand
from django.utils import timezone

from application.models import STATUS_ADMITTED, STATUS_EXPIRED, Application


class Command(BaseCommand):
    def handle(self, *args, **options):
        unconfirmed = Application.objects.filter(
            status=STATUS_ADMITTED, confirmation_deadline__lt=timezone.now()
        )
        self.stdout.write("Going to expire %s applications" % (unconfirmed.count()))
        expired = unconfirmed.update(status=STATUS_EXPIRED)
        self.stdout.write(
            self.style.SUCCESS("All %s applications successfully approved" % expired)
        )

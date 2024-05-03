from django.core.management.base import BaseCommand
from django.utils import timezone

from application.models import STATUS_ADMITTED, STATUS_EXPIRED, Application


class Command(BaseCommand):
    def handle(self, *args, **options):  # noqa: ARG002
        unconfirmed = Application.objects.filter(
            status=STATUS_ADMITTED, confirmation_deadline__lt=timezone.now()
        )
        self.stdout.write(f"Going to expire {unconfirmed.count()} applications")
        expired = unconfirmed.update(status=STATUS_EXPIRED)
        self.stdout.write(
            self.style.SUCCESS(f"All {expired} applications successfully approved")
        )

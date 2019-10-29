from django.core.management.base import BaseCommand
from django.utils import timezone

from application.models import Application, STATUS_ADMITTED, STATUS_EXPIRED


class Command(BaseCommand):
    def handle(self, *args, **options):
        Application.objects.filter(
            status=STATUS_ADMITTED, confirmation_deadline__lt=timezone.now()
        ).update(status=STATUS_EXPIRED)

from django.core.management.base import BaseCommand, CommandParser

from application.admin import approve
from application.models import STATUS_PENDING, Application


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "pct", type=float, help="Percentage of non-reviewed applications to admit"
        )

    def handle(self, *args, **options):
        unreviewed = Application.objects.filter(status=STATUS_PENDING).order_by("?")
        num_unreviewed = unreviewed.count()
        num_to_approve = round(options["pct"] * num_unreviewed)
        self.stdout.write(
            f"Going to approve {num_to_approve} applications (out of {num_unreviewed})"
        )
        apps_to_approve = unreviewed[:num_to_approve]
        approve(None, None, apps_to_approve)
        self.stdout.write(
            self.style.SUCCESS(
                f"All {num_to_approve} applications successfully approved"
            )
        )

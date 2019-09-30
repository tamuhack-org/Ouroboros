from django.core.management.base import BaseCommand, CommandParser

from application.admin import approve
from application.models import Application


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "pct", type=float, help="Percentage of non-reviewed applications to admit"
        )

    def handle(self, *args, **options):
        unreviewed = Application.objects.filter(approved=None).order_by("?")
        num_unreviewed = unreviewed.count()
        num_to_approve = round(options["pct"] * num_unreviewed)
        self.stdout.write(
            "Going to approve %s applications (out of %s)"
            % (num_to_approve, num_unreviewed)
        )
        apps_to_approve = unreviewed[:num_to_approve]
        approve(None, None, apps_to_approve)
        self.stdout.write(
            self.style.SUCCESS(
                "All %s applications successfully approved" % num_to_approve
            )
        )

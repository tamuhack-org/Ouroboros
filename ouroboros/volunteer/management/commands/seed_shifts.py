import argparse
import calendar

import pytz
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import dateparse, timezone

from volunteer.models import Shift


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "start_datetime",
            type=str,
            help="The datetime at which shifts will begin in ISO8601 format",
        )
        parser.add_argument(
            "end_datetime",
            type=str,
            help="The datetime at which shifts will end in ISO8601 format",
        )
        parser.add_argument(
            "shift_duration", type=float, help="The length of each shift in hours."
        )

    def handle(self, *args, **options):
        start_datetime = dateparse.parse_datetime(options["start_datetime"])
        if not start_datetime:
            raise Exception("start_datetime provided did not satisfy validation.")
        end_datetime = dateparse.parse_datetime(options["end_datetime"])
        if not end_datetime:
            raise Exception("end_datetime provided did not satisfy validation.")

        while start_datetime < end_datetime:

            Shift.objects.create(
                start=start_datetime,
                end=start_datetime
                + timezone.timedelta(hours=options["shift_duration"]),
            )
            start_datetime += timezone.timedelta(hours=options["shift_duration"] - 0.5)

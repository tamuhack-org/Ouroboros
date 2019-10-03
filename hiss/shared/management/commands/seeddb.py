import random
from datetime import timedelta

from django.core.management import base, CommandParser
from django.utils import timezone

from application.models import (
    Application,
    MAJORS,
    RACES,
    CLASSIFICATIONS,
    HACKATHON_TIMES,
    GRAD_YEARS,
    Wave,
    GENDERS,
    TRANSPORT_MODES,
)
from user.models import User

COMMON_NAMES = [
    "Noah",
    "Liam",
    "Mason",
    "Jacob",
    "William",
    "Ethan",
    "Michael",
    "Alexander",
    "James",
    "Daniel",
    "Emma",
    "Olivia",
    "Sophia",
    "Ava",
    "Isabella",
    "Mia",
    "Abigail",
    "Emily",
    "Charlotte",
    "Harper",
]

LAST_NAME = "Seedoe"
PASSWORD = "password"


class Command(base.BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "num_users", type=int, help="The number of total users to create"
        )
        parser.add_argument(
            "num_active",
            type=int,
            help="The number of active users to create. Must be <= num_users",
        )
        parser.add_argument(
            "num_applications",
            type=int,
            help="The number of applications to create. Must be <= num_active",
        )

    def handle(self, *args, **options):
        """
        Function that creates Users and Applications to make testing easier.
        To run use -- python manage.py shell < shared/seed.py
        WARNING - Will delete most of the Users and Applications when run.
        DO not use in production
        """
        self.stdout.write("Starting the seeding process.")
        num_users = options["num_users"]
        num_active = options["num_active"]
        num_apps = options["num_applications"]

        assert num_users >= num_active >= num_apps
        User.objects.filter(is_superuser=False).delete()
        Application.objects.filter(last_name=LAST_NAME).delete()
        Wave.objects.all().delete()

        wave_start = timezone.now()
        wave_end = wave_start + timedelta(days=10)
        wave = Wave(start=wave_start, end=wave_end, num_days_to_rsvp=5)
        wave.full_clean()
        wave.save()

        seeds = []
        for i in range(num_users):
            random_name = random.choice(COMMON_NAMES)
            email = random_name + str(i) + "@seed.com"
            is_active = True if i < num_active else False
            will_apply = True if i < num_apps else False
            user = User.objects.create_user(email, PASSWORD, is_active=is_active)
            seeds.append((user, will_apply, random_name))
        random.shuffle(seeds)

        for user, will_apply, random_name in seeds:
            if will_apply:
                application = Application(
                    first_name=random_name,
                    last_name=LAST_NAME,
                    notes="",
                    major=random.choice(MAJORS[1:])[0],
                    race=[random.choice(RACES[1:])[0]],
                    classification=random.choice(CLASSIFICATIONS[1:])[0],
                    gender=random.choice(GENDERS[1:])[0],
                    transport_needed=random.choice(TRANSPORT_MODES[1:])[0],
                    grad_term=random.choice(GRAD_YEARS[1:])[0],
                    num_hackathons_attended=random.choice(HACKATHON_TIMES[1:])[0],
                    previous_attendant=random.choice([True, False]),
                    tamu_student=random.choice([True, False]),
                    extra_links="a",
                    question1="b",
                    question2="c",
                    question3="d",
                    approved=random.choice([None, True, False]),
                    agree_to_coc=True,
                    is_adult=True,
                    additional_accommodations="",
                    resume="f.pdf",
                    wave_id=wave.pk,
                    user_id=user.pk,
                )
                application.save()

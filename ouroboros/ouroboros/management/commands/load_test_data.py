from django.core.management.base import BaseCommand
from django.core.management import call_command
from factory import Faker, Factory, fuzzy
import datetime
import pytz

# why is this called 'hacker'?
from hacker import models

WAVE_START = datetime.datetime.now(pytz.utc)
WAVE_END = WAVE_START + datetime.timedelta(days=15)

class Command(BaseCommand):
    def handle(self, **options):
        load_test_data()

class HackerFactory(Factory):
    class Meta:
        model = models.Hacker
    email = Faker('email')

class WaveFactory(Factory):
    class Meta:
        model = models.Wave
    start_time = WAVE_START
    end_time = WAVE_END

class ApplicationFactory(Factory):
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    adult = fuzzy.FuzzyChoice(models.TRUE_FALSE_CHOICES)
    # major = models.CharField("What's your major?", choices=MAJORS, max_length=50)
    # gender = models.CharField("What's your gender?", choices=GENDERS, max_length=2)
    # race = MultiSelectField("What race(s) do you identify with?", choices=RACES, max_length=41)
    # classification = models.CharField("What classification are you?", choices=CLASSIFICATIONS, max_length=2)
    # grad_year = models.CharField("What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11)
    # dietary_restrictions = MultiSelectField(
    #     "Do you have any dietary restrictions that we should know about?", choices=DIETARY_RESTRICTIONS, blank=True
    # )
    # num_hackathons_attended = models.CharField("How many hackathons have you attended?", max_length=22, choices=HACKATHON_TIMES)
    # previous_attendant = models.BooleanField(f"Have you attended {settings.EVENT_NAME} before?", choices=TRUE_FALSE_CHOICES, default=False)
    # tamu_student = models.BooleanField("Are you a Texas A&M student?", choices=TRUE_FALSE_CHOICES, default=True)

    # shirt_size = models.CharField("Shirt size?", choices=SHIRT_SIZES, max_length=3)
    # extra_links = models.CharField("Point us to anything you'd like us to look at while considering your application", max_length=200, help_text="Links to LinkedIn, GitHub, Devpost, Personal Website, etc.")
    # programming_joke = models.TextField("Tell us your best programming joke", max_length=500)
    # unlimited_resource = models.TextField("What is the one thing you'd build if you had unlimited resources?", max_length=500)
    # cool_prize = models.TextField(f"What is a cool prize you'd like to win at {settings.EVENT_NAME}?", max_length=500)
    # notes = models.TextField(
    #     max_length=300,
    #     blank=True,
    #     help_text="Provide any additional notes and/or comments in the text box provided",
    # )
    # resume = models.FileField("Provide us a copy of your most recent resume so we can get you connected with companies.")

    # approved = models.NullBooleanField(blank=True)

    # wave = models.ForeignKey(Wave, on_delete=models.CASCADE)

    # hacker = models.OneToOneField(Hacker, on_delete=models.CASCADE)

def load_test_data():
    print("Clearing database...")
    # _clear_database()
    # seeder = Seed.seeder()
    # seeder.add_entity(Wave, 3)
    # seeder.add_entity(Application, 50)
    # seeder.add_entity(Hacker, 50)
    # seeder.add_entity(Rsvp, 30)

    # inserted_pks = seeder.execute()
    # print(inserted_pks)
    # for h in Hacker.objects.all():
    #     print(h)
    # for h in Wave.objects.all():
    #     print(h)
    # for h in Application.objects.all():
    #     print(h)

def _clear_database():
    """clear the database of all contents before repopulating"""
    call_command('flush', interactive=False)


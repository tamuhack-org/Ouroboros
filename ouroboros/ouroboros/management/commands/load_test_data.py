from django.core.management.base import BaseCommand
from django.core.management import call_command
import factory

from django_seed import Seed
# why is this called 'hacker'?
from hacker import models

class Command(BaseCommand):
    def handle(self, **options):
        load_test_data()

class HackerFactory(factory.Factory):
    class Meta:
        model = models.Hacker

    first_name = factory.Faker('first_name')
    last_name = 'Doe'
    admin = False

def load_test_data():
    print("Clearing database...")
    _clear_database()
    seeder = Seed.seeder()
    seeder.add_entity(Wave, 3)
    seeder.add_entity(Application, 50)
    seeder.add_entity(Hacker, 50)
    seeder.add_entity(Rsvp, 30)

    inserted_pks = seeder.execute()
    print(inserted_pks)
    for h in Hacker.objects.all():
        print(h)
    for h in Wave.objects.all():
        print(h)
    for h in Application.objects.all():
        print(h)

def _clear_database():
    """clear the database of all contents before repopulating"""
    call_command('flush', interactive=False)


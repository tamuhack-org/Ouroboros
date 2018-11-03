from django import test
from django.core import exceptions as django_exceptions
from hacker import models as hacker_models
from django.utils import timezone



class HackerModelTestCase(test.TestCase):

    def setUp(self):
        self.hacker_fields = {
            'admitted': None,
            'checked_in': None,
            'admitted_datetime': None,
            'checked_in_datetime': None,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com'
        }

        self.application_fields = {
            # `Hacker` MUST be declared during instantiation of `Application`
            'major': 'Major',
            'gender': 'M',
            'classification': 'U1',
            'grad_year': timezone.now().year,
            'interests': 'Interests',
            'essay': 'Essay',
            'notes': 'Notes',
        }

        self.confirmation_fields = {
            # `Hacker` MUST be declared during instantiation of `Confirmation`
            'shirt_size': 'M',
            'dietary_restrictions': 'Halal',
            'travel_reimbursement_required': False,
            'notes': 'Notes',
        }

        self.team_fields = {
            'name': 'Team',
        }

    def test_first_name_required(self):
        del self.hacker_fields['first_name']

        hacker_without_first = hacker_models.Hacker(**self.hacker_fields)
        with self.assertRaises(django_exceptions.ValidationError):
            # Runs validation on the model before saving it.
            hacker_without_first.full_clean()

    def test_last_name_required(self):
        del self.hacker_fields['last_name']
        hacker_without_last = hacker_models.Hacker(**self.hacker_fields)

        with self.assertRaises(django_exceptions.ValidationError):
            # Runs validation on the model
            hacker_without_last.full_clean()

    def test_email_required(self):
        del self.hacker_fields['email']
        hacker_without_email = hacker_models.Hacker(**self.hacker_fields)

        with self.assertRaises(django_exceptions.ValidationError):
            # Runs validation on the model
            hacker_without_email.full_clean()

    def test_has_related_application(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        self.assertFalse(hacker_to_test.has_related_application())            

        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertTrue(hacker_to_test.has_related_application())  

    def test_has_related_confirmation(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertFalse(hacker_to_test.has_related_confirmation())  

        confirmation_to_test = hacker_models.Confirmation(hacker=hacker_to_test, **self.confirmation_fields)
        self.assertTrue(hacker_to_test.has_related_confirmation())  

    def test_has_related_team(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        team_to_test = hacker_models.Team(**self.team_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        self.confirmation_fields['team'] = team_to_test
        confirmation_to_test = hacker_models.Confirmation(hacker=hacker_to_test, **self.confirmation_fields)
        self.assertTrue(hacker_to_test.has_related_team())
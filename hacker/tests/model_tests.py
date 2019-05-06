from django import test
from django.core import exceptions as django_exceptions
from hacker import models as hacker_models
from django.utils import timezone


class HackerModelTests(test.TestCase):

    def setUp(self):
        self.hacker_fields = {
            'checked_in': None,
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
            'num_hackathons_attended': 2,
            'previous_attendant': True,
            'tamu_student': True,
            'interests': 'Interests',
            'essay1': 'Essay1',
            'notes': 'Notes',
        }

        self.confirmation_fields = {
            # `Hacker` MUST be declared during instantiation of `Confirmation`
            'shirt_size': 'M',
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

    ''' `Hacker` 'has_related' function tests'''
    def test_has_related_application(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        self.assertFalse(hacker_to_test.has_related_application())            

        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)

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

    ''' test the generate_confirm_code() function in `Hacker` '''
    def test_generate_confirm_code(self):
        # create test instance of `Hacker`
        test_hacker = hacker_models.Hacker(**self.hacker_fields)
        
        # generate confirm_code
        test_hacker.generate_confirm_code()
        code = getattr(test_hacker, 'confirm_code', None)

        # check: confirm_code value has been changed from None
        self.assertIsNotNone(code)
        # check: confirm_code is a string
        self.assertIsInstance(code, str)
        
    def test_check_confirm_code(self):
        # create test instance of `Hacker`
        test_hacker = hacker_models.Hacker(**self.hacker_fields)
        
        # Test 1: if `test_hacker.confirm_code` is 'None',
        #         the value returned by `test_hacker.check_confirm_code(input_code)`
        #         should be 'False' regardless the value of 'input_code'
        self.assertFalse(test_hacker.check_confirm_code('xxxxxx'))

        # generate 'confirm_code'
        test_hacker.generate_confirm_code()
        code = getattr(test_hacker, 'confirm_code', None)

        # Test 2: if the value of the string 'input_code' is NOT
        #         equal to the value of `test_hacker.check_confirm_code(input_code)`,
        #         the value returned by the function should be 'False'
        if code == 'xxxxxx':
            self.assertFalse(test_hacker.check_confirm_code('yyyyyy'))
        else:
            self.assertFalse(test_hacker.check_confirm_code('xxxxxx'))

        # Test 3: if the value of the string 'input_code' IS equal to
        #         the value of `test_hacker.check_confirm_code(input_code)`,
        #         the value returned by the function should be 'True'
        self.assertTrue(test_hacker.check_confirm_code(code))

    def test_confirm_email(self):
        # create test instance of `Hacker`
        test_hacker = hacker_models.Hacker(**self.hacker_fields)

        # generate 'confirm_code'
        test_hacker.generate_confirm_code()
        code = getattr(test_hacker, 'confirm_code', None)

        # Test 1
        if code == 'xxxxxx':
            self.assertFalse(test_hacker.confirm_email('yyyyyy'))
        else:
            self.assertFalse(test_hacker.confirm_email('xxxxxx'))

        # Test 2
        self.assertTrue(test_hacker.confirm_email(code))

        # Test 3
        self.assertTrue(getattr(test_hacker, 'email_confirmed', None))
        self.assertIsNone(getattr(test_hacker, 'confirm_code', 'not none'))


class ApplicationModelTests(test.TestCase):

    def setUp(self):
        self.hacker_fields = {
            'checked_in': None,
            'checked_in_datetime': None,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com'
        }
        self.hacker = hacker_models.Hacker(**self.hacker_fields)

        self.application_fields = {
            'hacker': self.hacker,
            'major': 'Major',
            'gender': 'M',
            'classification': 'U1',
            'grad_year': timezone.now().year,
            'num_hackathons_attended': 2,
            'previous_attendant': True,
            'tamu_student': True,
            'interests': 'Interests',
            'essay1': 'Essay1',
            'notes': 'Notes',
        }
        self.application = hacker_models.Application(**self.application_fields)

        self.team_fields = {
            'name': 'Team',
        }
        self.team = hacker_models.Team(**self.team_fields)

        self.confirmation_fields = {
            'hacker': self.hacker,
            'team': self.team,
            'shirt_size': 'M',
            'notes': 'Notes',
        }
        self.confirmation = hacker_models.Confirmation(**self.confirmation_fields)

    def test_get_first_name(self):
        fn = self.application.get_first_name()
        self.assertTrue(fn == 'First')

    def test_get_last_name(self):
        ln = self.application.get_last_name()
        self.assertTrue(ln == 'Last')

    def test_get_email(self):
        email = self.application.get_email()
        self.assertTrue(email == 'some@email.com')

    def test_get_is_active(self):
        active = self.application.get_is_active()
        self.assertTrue(active)
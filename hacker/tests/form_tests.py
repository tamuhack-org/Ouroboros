from django import test
from core import forms as core_forms
from hacker import models as hacker_models
from ouroboros import settings
from django.utils import timezone
import random
import string


class FormTests(test.TestCase):
    def setUp(self):
        self.test_hacker_fields = {
            'admitted': None,
            'checked_in': None,
            'admitted_datetime': None,
            'checked_in_datetime': None,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'User',
            'password': 'COFd32fsf',
        }

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.EMAIL_CONFIRM_CODE_LENGTH))

        # may require automation in future -> to assure test user doesn't exist
        self.signup_form_fields = {     
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'User',
            'password1': 'COFd32fsf',
            'password2': 'COFd32fsf',
        }

        self.signin_form_fields = {
            'username': 'User',
            'password': 'COFd32fsf',
        }

        self.confirm_email_form_fields = {
            'email': 'some@email.com',
            'confirm_code': code,
        }

        self.create_application_fields = {
            # create test instance of `Hacker`
            'major': 'Major',
            'gender': 'M',
            'classification': 'U1',
            'grad_year': timezone.now().year,
            'interests': 'Interests',
            'essay': 'Essay',
            'notes': 'Notes',
        }

    def test_signup_form(self):
        # check for already-existing Hacker w/ ...
            # email = some@email.com
            # username = User
        # and if it exists, delete it *****     
        ''' in the future -> take measures to prevent users from creating  '''
        '''                  instances of models w/ field values equal to  '''
        '''                  to any of those used in any of the test cases '''

        # ... fill in code ...

        form_data = self.signup_form_fields
        form = core_forms.SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

    def test_signin_form(self):
        # create test instance of `Hacker`
        test_hacker = hacker_models.Hacker.objects.create(**self.test_hacker_fields)

        form_data = self.signin_form_fields
        form = core_forms.SignInForm(data=form_data)
        self.assertTrue(form.is_valid())

        # delete test instance of `Hacker`

        # ...

    def test_confirm_email_form(self):
        form_data = self.confirm_email_form_fields
        form = core_forms.ConfirmEmailForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

    def test_create_application_form(self):
        form_data = self.create_application_fields
        form = core_forms.CreateApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
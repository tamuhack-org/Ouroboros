import random
import string

from django import test
from django.utils import timezone

from hacker import forms as hacker_forms
from hacker import models as hacker_models
from ouroboros import settings


class SignupFormTests(test.TestCase):
    def setUp(self):
        self.form_data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'user',
            'password1': 'my_password',
            'password2': 'my_password'
        }

    # Valid Form Data
    def test_signup_form_valid(self):
        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Blank Form Data
    def test_signup_form_blank(self):
        del self.form_data['first_name']

        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_signup_form_invalid(self):
        self.form_data['password1'] = 'p'

        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertFalse(form.is_valid())


class FormTests(test.TestCase):         # Remove In Future
    def setUp(self):
        self.test_hacker_fields = {
            'checked_in': None,
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
            'num_hackathons_attended': 2,
            'previous_attendant': True,
            'tamu_student': True,
            'interests': 'Interests',
            'essay1': 'Essay1',
            'notes': 'Notes',
        }

        

    def test_confirm_email_form(self):
        form_data = self.confirm_email_form_fields
        form = hacker_forms.ConfirmEmailForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

        
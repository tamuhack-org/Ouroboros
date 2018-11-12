from django import test
from core import forms as core_forms
from hacker import models as hacker_models
from ouroboros import settings
import random
import string


class FormTests(test.TestCase):
    def setUp(self):
        # may require automation in future -> to assure test user doesn't exist
        self.signup_form_fields = {     
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'User',
            'password1': 'sEcReT123',
            'password2': 'sEcReT123',
        }

        self.signin_form_fields = {
            'username': 'User',
            'password': 'sEcReT123',
        }

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.EMAIL_CONFIRM_CODE_LENGTH))

        self.confirm_email_form_fields = {
            'email': 'some@email.com',
            'confirm_code': code,
        }

    def test_signup_form(self):
        form_data = self.signup_form_fields
        form = core_forms.SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

    def test_signin_form(self):
        form_data = self.signin_form_fields
        form = core_forms.SignInForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

    def test_confirm_email_form(self):
        form_data = self.confirm_email_form_fields
        form = core_forms.ConfirmEmailForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...
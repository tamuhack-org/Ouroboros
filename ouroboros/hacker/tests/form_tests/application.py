from hacker import forms
from shared import test
from django.test import modify_settings
from django.core.files.uploadedfile import SimpleUploadedFile


class ApplicationModelFormTestCase(test.SharedTestCase):
    def test_isnt_valid_when_no_active_wave(self):
        form = forms.ApplicationModelForm(
            self.application_fields, self.resume_file_data
        )
        self.assertFalse(form.is_valid())

    def test_is_valid_when_active_wave(self):
        self.create_active_wave()
        form = forms.ApplicationModelForm(
            self.application_fields, self.resume_file_data
        )
        self.assertTrue(form.is_valid())
    
    def test_isnt_valid_when_non_pdf(self):
        
        self.application_fields["resume"] = SimpleUploadedFile("resume.txt", b"dummy")
        form = forms.ApplicationModelForm(
            self.application_fields, {"resume": self.application_fields["resume"]}
        )
        self.assertFalse(form.is_valid())

    def test_isnt_valid_when_first_name_has_numbers(self):
        self.create_active_wave()
        hacker_fields = {
            "email": self.email,
            "password": self.password,
            "first_name": "Bobby432B",
            "last_name": self.last_name,
            "is_active": True,
        }
        form = forms.ApplicationModelForm(hacker_fields)
        self.assertFalse(form.is_valid())

    def test_isnt_valid_when_last_name_has_numbers(self):
        self.create_active_wave()
        hacker_fields = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": "Bob321B",
            "is_active": True,
        }
        form = forms.ApplicationModelForm(hacker_fields)
        self.assertFalse(form.is_valid())
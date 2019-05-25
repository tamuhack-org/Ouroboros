from hacker import forms
from shared import test


class ApplicationModelFormTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()

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

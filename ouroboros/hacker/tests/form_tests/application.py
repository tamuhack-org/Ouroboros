from hacker import forms
from shared import test


class ApplicationModelFormTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.fields = {
            "major": "A",
            "gender": "M",
            "classification": "U1",
            "grad_year": 2020,
            "dietary_restrictions": ["Vegan"],
            "num_hackathons_attended": 0,
            "interests": "A",
            "essay1": "A",
            "essay2": "B",
            "essay3": "C",
            "essay4": "D",
            "notes": "E",
        }

    def test_isnt_valid_when_no_active_wave(self):
        form = forms.ApplicationModelForm(self.fields)
        self.assertFalse(form.is_valid())

    def test_is_valid_when_active_wave(self):
        self.create_active_wave()
        form = forms.ApplicationModelForm(self.fields)
        self.assertTrue(form.is_valid())

from application.forms import ApplicationModelForm
from application.models import GENDER_OTHER, RACE_OTHER
from shared import test_case


class ApplicationModelFormTestCase(test_case.SharedTestCase):
    def test_gender_other_required_if_other_selected(self):
        self.application_fields["gender"] = GENDER_OTHER

        form = ApplicationModelForm(self.application_fields)

        self.assertFalse(form.is_valid())
        self.assertListEqual(
            form["gender_other"].errors,
            ['Please fill out this field or choose "Prefer not to answer".'],
        )

    def test_race_other_required_if_other_selected(self):
        self.application_fields["race"] = [RACE_OTHER]

        form = ApplicationModelForm(self.application_fields)

        self.assertFalse(form.is_valid())
        self.assertListEqual(
            form["race_other"].errors,
            ["Please fill out this field with the appropriate information."],
        )

    def test_race_other_doesnt_error_if_no_races_selected(self):
        self.application_fields["race"] = []

        form = ApplicationModelForm(self.application_fields)

        self.assertFalse(form.is_valid())
        self.assertListEqual(form["race_other"].errors, [])
        self.assertEqual(len(form["race"].errors), 1)

from application import constants
from application.models import Application
from shared import test_case


class ApplicationModelTestCase(test_case.SharedTestCase):
    def test_renames_file_to_uuid(self):
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.assertNotEqual(self.resume_file_name, application.resume.name)

    def test_confirmed_meal_group_is_assigned_once(self):
        self.create_active_wave()
        fields = {**self.application_fields, "meal_group": None}
        application = Application(
            **fields, wave=self.wave1, status=constants.STATUS_CONFIRMED
        )
        application.save()
        assigned = application.meal_group
        self.assertIsNotNone(assigned)

        # Another confirmed app shifts the round-robin count; re-saving must not.
        Application.objects.create(
            **{**fields, "user": self.user2},
            wave=self.wave1,
            status=constants.STATUS_CONFIRMED,
        )
        application.save()
        application.refresh_from_db()
        self.assertEqual(application.meal_group, assigned)

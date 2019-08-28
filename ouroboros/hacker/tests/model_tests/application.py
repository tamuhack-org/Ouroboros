from shared import test
from hacker.models import Application


class ApplicationModelTestCase(test.SharedTestCase):
    def test_renames_file_to_uuid(self):
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.assertNotEqual(self.resume_file_name, application.resume.name)

from application.models import Application
from shared import test_case


class ApplicationModelTestCase(test_case.SharedTestCase):
    def test_renames_file_to_uuid(self):
        self.create_active_wave()
        application = Application(**self.application_fields, wave=self.wave1)
        application.save()
        self.assertNotEqual(self.resume_file_name, application.resume.name)

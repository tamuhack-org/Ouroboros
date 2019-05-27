from shared import test
from hacker import models as hacker_models
from hacker.admin import approve


class ApplicationAdminTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = hacker_models.Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()

    def test_approval_action_sends_approval_email(self):
        # TODO(SaltyQuetzals): Need to implement this test
        pass

from shared import test_case


class CreateApplicationViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        pass

    def create_application_requires_login(self) -> None:
        self.fail()

    def create_application_associates_with_user(self) -> None:
        self.fail()

    def create_application_with_existing_app_fails(self) -> None:
        self.fail()

    def create_application_associates_with_active_wave(self) -> None:
        self.fail()
